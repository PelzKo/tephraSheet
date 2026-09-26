import json

from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from characters import access
from characters.models import Character, InventoryItem
from rules.engine import tables

from .forms import ItemForm, augment_choices_json
from .importer import parse_rows, template_csv
from .models import KIND_CHOICES, ItemTemplate

IMPORT_SESSION_KEY = "catalog_import_rows"


def _target_character(request):
    """Character given via ?for=<id> (only if unlocked)."""
    pk = request.GET.get("for") or request.POST.get("for")
    if not pk or not str(pk).isdigit():
        return None
    character = Character.objects.filter(pk=pk).first()
    if character and access.can_access(request, character):
        return character
    return None


def catalog_list(request):
    character = _target_character(request)
    qs = ItemTemplate.objects.all()
    q = request.GET.get("q", "").strip()
    kind = request.GET.get("kind", "")
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
    if kind:
        qs = qs.filter(kind=kind)
    template = "catalog/partials/results.html" if request.headers.get("HX-Request") else "catalog/list.html"
    return render(request, template, {
        "items": qs[:300], "q": q, "kind": kind, "kinds": KIND_CHOICES, "character": character,
        "is_gm": access.is_gm(request), "slots": InventoryItem._meta.get_field("slot").choices,
    })


def _creator_context(form, character, item=None, inventory_item=None):
    return {"form": form, "character": character, "item": item, "inventory_item": inventory_item,
            "tables_json": json.dumps({"melee": tables.MELEE, "firearm": tables.FIREARMS, "bow": tables.BOWS,
                                       "crossbow": tables.CROSSBOWS, "armor": tables.ARMOR,
                                       "deflection": tables.DEFLECTION, "slots": tables.MATERIAL_SLOTS,
                                       "variants": tables.VARIANTS}),
            "augments_json": json.dumps(augment_choices_json())}


def item_create(request):
    character = _target_character(request)
    gm = access.is_gm(request)
    initial = {}
    if request.GET.get("kind"):
        initial["kind"] = request.GET["kind"]
    form = ItemForm(request.POST or None, gm=gm, initial=initial)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        to_catalog = request.POST.get("to_catalog") == "on" or not character
        if to_catalog:
            if ItemTemplate.objects.filter(name=obj.name, kind=obj.kind).exists():
                form.add_error("name", "An item with this name and kind already exists in the catalog.")
                return render(request, "catalog/item_form.html", _creator_context(form, character))
            obj.source = "custom"
            obj.save()
        if character:
            slot = request.POST.get("slot", "carried")
            inv = InventoryItem(character=character, template=obj if obj.pk else None, slot=slot,
                                **{f: getattr(obj, f) for f in ItemTemplate.ITEM_FIELDS})
            if slot in ("weapon1", "weapon2", "armor", "deflection"):
                InventoryItem.objects.filter(character=character, slot=slot).update(slot="carried")
            inv.save()
            messages.success(request, f"{obj.name} added to {character}'s inventory.")
            return redirect(request.POST.get("next") or f"{character.get_absolute_url()}?tab=inventory")
        messages.success(request, f"{obj.name} added to the catalog.")
        return redirect("catalog")
    return render(request, "catalog/item_form.html", _creator_context(form, character))


def item_edit(request, pk):
    item = get_object_or_404(ItemTemplate, pk=pk)
    gm = access.is_gm(request)
    if item.source == "book" and not gm:
        messages.error(request, "Only the narrator can change Playing Guide items.")
        return redirect("catalog")
    form = ItemForm(request.POST or None, instance=item, gm=gm)
    if request.method == "POST":
        if request.POST.get("delete") and gm:
            item.delete()
            messages.success(request, "Item deleted from the catalog.")
            return redirect("catalog")
        if form.is_valid():
            form.save()
            messages.success(request, "Catalog item saved.")
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
        inv.notes = request.POST.get("notes", inv.notes)[:255]
        inv.save()
        messages.success(request, f"{inv.name} updated.")
        return redirect(f"{character.get_absolute_url()}?tab=inventory")
    return render(request, "catalog/item_form.html", _creator_context(form, character, inventory_item=inv))


@require_POST
def add_to_inventory(request, pk):
    template = get_object_or_404(ItemTemplate, pk=pk)
    character = _target_character(request)
    if not character:
        messages.error(request, "Unlock a character first.")
        return redirect("catalog")
    slot = request.POST.get("slot", "carried")
    if slot not in dict(InventoryItem._meta.get_field("slot").choices):
        slot = "carried"
    qty = request.POST.get("quantity", "1")
    if slot in ("weapon1", "weapon2", "armor", "deflection"):
        InventoryItem.objects.filter(character=character, slot=slot).update(slot="carried")
    InventoryItem.from_template(character, template, slot=slot,
                                quantity=max(1, int(qty) if qty.isdigit() else 1)).save()
    if request.POST.get("pay"):
        character.money_on_hand -= template.price_dukes * max(1, int(qty) if qty.isdigit() else 1)
        character.save(update_fields=["money_on_hand"])
    messages.success(request, f"{template.name} added to {character}.")
    if request.headers.get("HX-Request"):
        return HttpResponse(f'<span class="added">✓ added</span>')
    return redirect(request.POST.get("next") or f"{character.get_absolute_url()}?tab=inventory")


def import_template(request):
    resp = HttpResponse(template_csv(), content_type="text/csv; charset=utf-8")
    resp["Content-Disposition"] = 'attachment; filename="tephra_items_template.csv"'
    return resp


def import_view(request):
    character = _target_character(request)
    gm = access.is_gm(request)
    rows = None
    if request.method == "POST" and request.POST.get("action") == "preview":
        text = request.POST.get("text", "")
        upload = request.FILES.get("file")
        if upload:
            text = upload.read().decode("utf-8-sig", errors="replace")
        rows = parse_rows(text)
        request.session[IMPORT_SESSION_KEY] = rows
    elif request.method == "POST" and request.POST.get("action") == "commit":
        rows = request.session.pop(IMPORT_SESSION_KEY, [])
        good = [r for r in rows if not r["errors"]]
        target = request.POST.get("target", "catalog")
        created = 0
        for r in good:
            values = dict(r["values"])
            qty = values.pop("quantity", 1)
            starting = values.pop("is_starting_gear", False)
            if target == "catalog" or not character:
                obj, was_created = ItemTemplate.objects.update_or_create(
                    name=values["name"], kind=values["kind"],
                    defaults={**values, "source": "custom", "is_starting_gear": starting and gm})
                created += was_created
            else:
                InventoryItem.objects.create(character=character, quantity=max(1, qty), slot="carried", **values)
                created += 1
        messages.success(request, f"Imported {created} new item(s), skipped {len(rows) - len(good)} with errors.")
        if character and target != "catalog":
            return redirect(f"{character.get_absolute_url()}?tab=inventory")
        return redirect("catalog")
    return render(request, "catalog/import.html", {
        "rows": rows, "character": character, "ok_count": sum(1 for r in rows or [] if not r["errors"])})
