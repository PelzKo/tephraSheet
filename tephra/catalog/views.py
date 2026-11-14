import json

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from characters import access, actionlog, services
from characters.models import Character, InventoryItem
from rules.engine import tables
from rules.extensions import EXTENSIONS, enabled, offer
from rules.lang import gettext as _
from rules.registry import get_registry

from .forms import ItemForm, augment_choices_json
from .importer import export_csv, parse_rows, template_csv
from .models import KIND_CHOICES, ItemTemplate

IMPORT_SESSION_KEY = "catalog_import_rows"
IMPORT_MAX_BYTES = 1_000_000
PAGE_SIZE = 100
SOURCES = [("book", "Playing Guide"), ("modified", "Playing Guide (modified)"), ("custom", "Custom")]


def _int(value, default=None):
    """int() for request values; None/garbage (also digits like "²", which isdigit() accepts) -> default."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _next_url(request, fallback):
    nxt = request.POST.get("next")
    if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()},
                                               require_https=request.is_secure()):
        return nxt
    return fallback


def _target_character(request):
    """Character given via ?for=<id> (only if unlocked)."""
    pk = _int(request.GET.get("for") or request.POST.get("for"))
    character = Character.objects.filter(pk=pk).first() if pk else None
    if character and access.can_access(request, character):
        return character
    return None


def _filtered(request):
    """Catalog items matching the list filters (q, kind, source, ext) and the filter values."""
    gm = access.is_gm(request)
    f = {k: request.GET.get(k, "").strip() for k in ("q", "kind", "source", "ext")}
    if f["source"] == "hidden" and gm:  # book items the narrator deleted
        qs = ItemTemplate.objects.filter(deleted_at__isnull=False)
    else:
        qs = ItemTemplate.offered()
        if f["source"] in ("book", "modified"):
            qs = qs.filter(source="book", modified=f["source"] == "modified")
        elif f["source"] == "custom":
            qs = qs.filter(source="custom")
    if f["q"]:
        qs = qs.filter(Q(name__icontains=f["q"]) | Q(description__icontains=f["q"]))
    if f["kind"]:
        qs = qs.filter(kind=f["kind"])
    if f["ext"]:
        qs = qs.filter(extension="" if f["ext"] == "core" else f["ext"])
    return qs, f


def catalog_list(request):
    character = _target_character(request)
    gm = access.is_gm(request)
    qs, f = _filtered(request)
    page = Paginator(qs, PAGE_SIZE).get_page(request.GET.get("page"))
    template = "catalog/partials/results.html" if request.headers.get("HX-Request") else "catalog/list.html"
    sources = SOURCES + ([("hidden", "Hidden (deleted book items)")] if gm else [])
    return render(request, template, {
        "items": page, "page": page, **f, "kinds": KIND_CHOICES, "character": character, "is_gm": gm,
        "sources": sources, "extensions": [(k, n) for k, n in EXTENSIONS.items() if k in enabled()],
        "extension_names": EXTENSIONS, "slots": InventoryItem._meta.get_field("slot").choices,
    })


def catalog_export(request):
    """The (filtered) catalog as CSV in the import format: edit in a spreadsheet and re-import, or keep as backup."""
    qs, _f = _filtered(request)
    resp = HttpResponse(export_csv(qs), content_type="text/csv; charset=utf-8")
    resp["Content-Disposition"] = 'attachment; filename="tephra_catalog.csv"'
    return resp


def augment_reference(request):
    """All augments with every marque and the book text, grouped like the book."""
    groups = {}
    augments = offer(get_registry().augments.values())
    for a in augments:
        groups.setdefault(f"{a['skill']} – {a['section']}", []).append(a)
    lists = sorted({li for a in augments for li in a["lists"]})
    return render(request, "catalog/augments.html", {"groups": list(groups.items()), "lists": lists,
                                                     "q": request.GET.get("q", "")})


def _creator_context(form, character, item=None, inventory_item=None, copy_of=None):
    return {"form": form, "character": character, "item": item, "inventory_item": inventory_item, "copy_of": copy_of,
            "tables_json": json.dumps({"melee": tables.MELEE, "firearm": tables.FIREARMS, "bow": tables.BOWS,
                                       "crossbow": tables.CROSSBOWS, "armor": tables.ARMOR,
                                       "deflection": tables.DEFLECTION, "slots": tables.MATERIAL_SLOTS,
                                       "variants": tables.VARIANTS}),
            "augments_json": json.dumps(augment_choices_json())}


def _equip(request, character, inv, slot):
    """Save a new inventory item into ``slot``; if the slot rules refuse, it is carried instead."""
    try:
        result = services.equip(character, inv, slot)
    except services.EquipError as exc:
        messages.error(request, _("{error} It was added as carried.", error=exc))
        services.equip(character, inv, "carried")
        return
    if result["moved"]:
        messages.info(request, _("Put away (now carried): {items}.", items=", ".join(result["moved"])))
    if result["notice"]:
        messages.warning(request, result["notice"])


def item_create(request):
    character = _target_character(request)
    gm = access.is_gm(request)
    initial = {}
    if request.GET.get("kind"):
        initial["kind"] = request.GET["kind"]
    copy_of = ItemTemplate.objects.filter(pk=_int(request.GET.get("copy") or request.POST.get("copy"))).first()
    proxy = None
    if copy_of and request.method != "POST":  # "Copy as new item": prefilled, saved as a custom item
        proxy = ItemTemplate(**copy_of.item_values())
        proxy.name = _("{name} (copy)", name=copy_of.name)[:120]
    form = ItemForm(request.POST or None, gm=gm, initial=initial, instance=proxy)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        if copy_of:
            obj.extension, obj.modifiers = copy_of.extension, list(copy_of.modifiers or [])  # not form fields
        # Every created item is shared in the catalog. A name+kind that already exists stays
        # inventory-only for a character (the catalog keeps the original).
        if ItemTemplate.objects.filter(name=obj.name, kind=obj.kind).exists():
            if not character:
                form.add_error("name", _("An item with this name and kind already exists in the catalog."))
                return render(request, "catalog/item_form.html", _creator_context(form, character, copy_of=copy_of))
            messages.info(request, _("The catalog already has a {kind} called {name}; your version was only added to the inventory.",
                                   kind=obj.get_kind_display().lower(), name=obj.name))
        else:
            obj.source = "custom"
            obj.save()
            actionlog.log(request, "catalog:create", obj)
        if character:
            slot = request.POST.get("slot", "carried")
            inv = InventoryItem(character=character, template=obj if obj.pk else None, slot="carried",
                                **{f: getattr(obj, f) for f in ItemTemplate.ITEM_FIELDS})
            _equip(request, character, inv, slot)
            messages.success(request, _("{name} added to {character}'s inventory.", name=obj.name, character=character))
            return redirect(_next_url(request, f"{character.get_absolute_url()}?tab=inventory"))
        messages.success(request, _("{name} added to the catalog.", name=obj.name))
        return redirect("catalog")
    return render(request, "catalog/item_form.html", _creator_context(form, character, copy_of=copy_of))


def item_edit(request, pk):
    item = get_object_or_404(ItemTemplate, pk=pk)
    gm = access.is_gm(request)
    if item.source == "book" and not gm:
        messages.error(request, _("Only the narrator can change Playing Guide items."))
        return redirect("catalog")
    before = item.item_values()
    form = ItemForm(request.POST or None, instance=item, gm=gm)
    if item.source == "book":  # the seed finds book items by name+kind; variants get "Copy as new item"
        form.fields["name"].disabled = form.fields["kind"].disabled = True
    if request.method == "POST":
        if request.POST.get("delete") and gm:
            actionlog.log(request, "catalog:delete", item)
            # Book items stay hidden (so seed_catalog does not bring them back); custom items go to the trash.
            item.deleted_at = timezone.now()
            item.save(update_fields=["deleted_at"])
            if item.source == "book":
                messages.success(request, _("Playing Guide item hidden from the catalog."))
            else:
                messages.success(request, _("Item moved to the trash. The narrator can restore it on the narrator page."))
            return redirect("catalog")
        if request.POST.get("restore") and gm and item.deleted_at:
            item.deleted_at = None
            item.save(update_fields=["deleted_at"])
            actionlog.log(request, "catalog:restore", item)
            messages.success(request, _("{name} is back in the catalog.", name=item.name))
            return redirect("item_edit", pk=item.pk)
        if request.POST.get("reset") and gm and item.source == "book":
            item.refresh_from_db()
            if item.reset_to_book():
                item.save()
                actionlog.log(request, "catalog:reset", item, before, item.item_values())
                messages.success(request, _("{name} reset to the Playing Guide values.", name=item.name))
            else:
                messages.error(request, _("The Playing Guide has no item called {name}.", name=item.name))
            return redirect("item_edit", pk=item.pk)
        if form.is_valid():
            obj = form.save(commit=False)
            if obj.source == "book" and obj.item_values() != before:
                obj.modified = True
            obj.save()
            actionlog.log(request, "catalog:edit", obj, before, obj.item_values())
            messages.success(request, _("Catalog item saved."))
            return redirect("catalog")
    return render(request, "catalog/item_form.html", _creator_context(form, None, item=item))


@access.character_view
def inventory_item_edit(request, character, item_id):
    inv = get_object_or_404(InventoryItem, pk=item_id, character=character)
    proxy = ItemTemplate(**{f: getattr(inv, f) for f in ItemTemplate.ITEM_FIELDS})
    form = ItemForm(request.POST or None, instance=proxy, gm=False)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        for f in ItemTemplate.ITEM_FIELDS:
            setattr(inv, f, getattr(obj, f))
        before = actionlog.values(InventoryItem.objects.get(pk=inv.pk))
        inv.notes = request.POST.get("notes", inv.notes)[:255]
        inv.save()
        actionlog.log(request, "inventory:edit", inv, before, actionlog.values(inv))
        messages.success(request, _("{name} updated.", name=inv.name))
        return redirect(f"{character.get_absolute_url()}?tab=inventory")
    return render(request, "catalog/item_form.html", _creator_context(form, character, inventory_item=inv))


@require_POST
def add_to_inventory(request, pk):
    template = get_object_or_404(ItemTemplate.offered(), pk=pk)
    character = _target_character(request)
    if not character:
        messages.error(request, _("Unlock a character first."))
        return redirect("catalog")
    slot = request.POST.get("slot", "carried")
    if slot not in dict(InventoryItem._meta.get_field("slot").choices):
        slot = "carried"
    qty = min(max(1, _int(request.POST.get("quantity"), 1)), 9999)
    fallback = f"{character.get_absolute_url()}?tab=inventory"
    if request.POST.get("pay"):
        cost = template.price_dukes * qty
        if cost > character.money_on_hand:
            messages.error(request, _("Not enough money: {cost} needed, {money} on hand.", cost=tables.format_money(cost),
                                      money=tables.format_money(character.money_on_hand)))
            if request.headers.get("HX-Request"):
                return HttpResponse(f'<span class="err">{_("Not enough money")}</span>')
            return redirect(_next_url(request, fallback))
        character.money_on_hand -= cost
        character.save(update_fields=["money_on_hand"])
    _equip(request, character, InventoryItem.from_template(character, template, slot="carried", quantity=qty), slot)
    messages.success(request, _("{name} added to {character}.", name=template.name, character=character))
    if request.headers.get("HX-Request"):
        return HttpResponse(f'<span class="added">{_("✓ added")}</span>')
    return redirect(_next_url(request, fallback))


def import_template(request):
    resp = HttpResponse(template_csv(), content_type="text/csv; charset=utf-8")
    resp["Content-Disposition"] = 'attachment; filename="tephra_items_template.csv"'
    return resp


CATALOG_FIELDS = {*ItemTemplate.ITEM_FIELDS, "is_starting_gear"}


def _catalog_values(row, gm):
    """Model values of an import row for the shared catalog (starting gear and modifiers only from the narrator)."""
    return {k: v for k, v in row["values"].items()
            if k in CATALOG_FIELDS and (gm or k not in ("is_starting_gear", "modifiers"))}


def _import_status(values, gm):
    """(status, existing item) of an import row into the catalog: new / update / unchanged / skipped."""
    existing = ItemTemplate.objects.filter(name=values["name"], kind=values["kind"]).first()
    if not existing:
        return "new", None
    if existing.source == "book" and not gm:
        return "skipped", existing  # only the narrator may change Playing Guide items (see item_edit)
    if existing.deleted_at or any(getattr(existing, k) != v for k, v in values.items()):
        return "update", existing
    return "unchanged", existing


def _import_summary(counts):
    return _("{new} new, {update} updated, {unchanged} unchanged, {skipped} skipped (Playing Guide items), {error} with errors",  # noqa: E501
             **counts)


def import_view(request):
    character = _target_character(request)
    gm = access.is_gm(request)
    rows = None
    if request.method == "POST" and request.POST.get("action") == "preview":
        text = request.POST.get("text", "")
        upload = request.FILES.get("file")
        if upload and upload.size > IMPORT_MAX_BYTES:
            messages.error(request, _("The file is too big (at most {n} MB).", n=IMPORT_MAX_BYTES // 1_000_000))
        else:
            if upload:
                text = upload.read().decode("utf-8-sig", errors="replace")
            rows = parse_rows(text)
            request.session[IMPORT_SESSION_KEY] = rows
    elif request.method == "POST" and request.POST.get("action") == "commit":
        rows = request.session.pop(IMPORT_SESSION_KEY, [])
        good = [r for r in rows if not r["errors"]]
        if character and request.POST.get("target", "catalog") != "catalog":
            for r in good:
                values = {k: v for k, v in r["values"].items() if k in ItemTemplate.ITEM_FIELDS}
                InventoryItem.objects.create(character=character, quantity=max(1, r["values"].get("quantity", 1)),
                                             slot="carried", **values)
            actionlog.log(request, "inventory:import", character, label=f"{character}: {len(good)}")
            messages.success(request, _("Imported {created} new item(s), skipped {skipped} with errors.",
                                        created=len(good), skipped=len(rows) - len(good)))
            return redirect(f"{character.get_absolute_url()}?tab=inventory")
        counts = {"new": 0, "update": 0, "unchanged": 0, "skipped": 0, "error": len(rows) - len(good)}
        for r in good:
            values = _catalog_values(r, gm)
            status, existing = _import_status(values, gm)
            counts[status] += 1
            if status == "new":
                ItemTemplate.objects.create(**values, source="custom")
            elif status == "update":
                for k, v in values.items():
                    setattr(existing, k, v)
                existing.deleted_at = None
                existing.modified = existing.source == "book"
                existing.save()
        actionlog.log(request, "catalog:import", label=_import_summary(counts))
        messages.success(request, _("Import into the catalog: {summary}.", summary=_import_summary(counts)))
        return redirect("catalog")
    counts = None
    if rows is not None:
        counts = {"new": 0, "update": 0, "unchanged": 0, "skipped": 0, "error": 0}
        for r in rows:
            r["status"] = "error" if r["errors"] else _import_status(_catalog_values(r, gm), gm)[0]
            counts[r["status"]] += 1
    return render(request, "catalog/import.html", {
        "rows": rows, "character": character, "ok_count": sum(1 for r in rows or [] if not r["errors"]),
        "summary": _import_summary(counts) if counts else ""})
