"""The character sheet and in-play actions (HP, wounds, XP, money, stances, toggles, effects)."""

from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from rules.engine import tables
from rules.registry import get_registry

from .. import access
from ..models import EffectEntry, InventoryItem

TAB_NAMES = ("page1", "page2", "inventory")


def sheet_context(request, character):
    sheet = character.compute()
    reg = get_registry()
    hp = character.current_hp if character.current_hp is not None else sheet.max_hp
    wounds = character.current_wounds if character.current_wounds is not None else sheet.max_wounds
    effects = list(character.effects.filter(active=True))
    rows = list(sheet.specialty_rows)
    # Sheet p.2 has rows L1, L1, L1, L2 … L12.
    slots = []
    remaining = list(rows)
    for lvl in [1, 1, 1] + list(range(2, 13)):
        row = next((r for r in remaining if r["level"] == lvl), None)
        if row:
            remaining.remove(row)
        slots.append({"level": lvl, "row": row})
    for row in remaining:  # extra specialties (admin additions) go at the end
        slots.append({"level": row["level"], "row": row})
    augments = [reg.augments[a] for a in character.augments if a in reg.augments]
    stories = [reg.stories[s] for s in character.stories if s in reg.stories]
    items = list(character.items.all())
    locations = {n: [] for n in range(1, 13)}
    for e in effects:
        if e.location:
            locations[e.location].append(e)
    spec_data = {}
    for row in sheet.specialty_rows:
        sp = row["specialty"]
        spec_data[row["slug"]] = {
            "name": sp["name"], "skill": sp["skill"] or "General (Sciences)", "cost": sp["cost"],
            "requires": sp["requires_text"], "effect": sp["effect"],
            "bonuses": ", ".join(f"{tables.COMBAT_STAT_LABELS[k]} {v:+d}" for k, v in sp["bonuses"].items()),
        }
    return {
        "character": character, "sheet": sheet, "hp": hp, "wounds": wounds,
        "spec_data": spec_data,
        "slot_choices": InventoryItem._meta.get_field("slot").choices,
        "effects": effects,
        "wound_effects": [e for e in effects if e.kind == "wound"],
        "fatal_effects": [e for e in effects if e.kind == "fatal"],
        "status_effects": [e for e in effects if e.kind in ("status", "called")],
        "locations": locations,
        "location_names": tables.LOCATIONS,
        "specialty_slots": slots,
        "stat_cols": tables.COMBAT_STATS, "stat_labels": tables.COMBAT_STAT_LABELS,
        "augments": augments, "stories": stories,
        "items": items,
        "carried": [i for i in items if i.slot in ("carried", "worn")],
        "stored": [i for i in items if i.slot == "stored"],
        "money_on_hand": tables.format_money(character.money_on_hand),
        "money_in_bank": tables.format_money(character.money_in_bank),
        "xp_range": range(1, 13),
        "xp_hand": max(1, min(12, character.xp)),
        "admin_mode": access.in_admin_mode(request, character),
        "admin_allowed": access.admin_mode_allowed(request, character),
        "is_gm": access.is_gm(request),
        "status_effect_names": tables.STATUS_EFFECTS,
        "attr_layout": [(a, tables.SKILLS[a]) for a in tables.ATTRIBUTES],
        "tab": request.GET.get("tab") if request.GET.get("tab") in TAB_NAMES else "page1",
        "xp_to_level": tables.XP_PER_LEVEL,
        "can_level": character.xp >= tables.XP_PER_LEVEL and character.level < tables.MAX_LEVEL,
    }


@access.character_view
def sheet_view(request, character):
    if character.status == "draft":
        return redirect("wizard", pk=character.pk)
    if character.level < character.target_level:
        return redirect("levelup", pk=character.pk)
    return render(request, "characters/sheet.html", sheet_context(request, character))


def _respond(request, character):
    if request.headers.get("HX-Request"):
        ctx = sheet_context(request, character)
        ctx["tab"] = request.POST.get("tab") if request.POST.get("tab") in TAB_NAMES else ctx["tab"]
        return render(request, "characters/partials/sheet_body.html", ctx)
    return redirect(f"{character.get_absolute_url()}?tab={request.POST.get('tab', 'page1')}")


def _int(value, default=0):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


@require_POST
@access.character_view
def play_action(request, character, action):
    sheet = character.compute()
    p = request.POST
    hp = character.current_hp if character.current_hp is not None else sheet.max_hp
    wounds = character.current_wounds if character.current_wounds is not None else sheet.max_wounds

    if action == "damage":
        # Damage reduces HP first; the rest goes to wounds (p.10). "direct" skips HP.
        amount = max(0, _int(p.get("amount")))
        if p.get("direct"):
            wounds -= amount
        else:
            to_hp = min(hp, amount)
            hp -= to_hp
            wounds -= amount - to_hp
        took_wounds = wounds < (character.current_wounds if character.current_wounds is not None
                                else sheet.max_wounds)
        character.current_hp, character.current_wounds = hp, max(0, wounds)
        if wounds <= 0:
            messages.warning(request, "0 wounds: every further hit causes a fatal effect (roll a location).")
        elif took_wounds:
            messages.warning(request, "Wounds damage: roll a called-shot location for the wounded effect.")
    elif action == "heal":
        amount = max(0, _int(p.get("amount")))
        character.current_hp = min(sheet.max_hp, hp + amount)
    elif action == "heal_wounds":
        amount = max(0, _int(p.get("amount"), 1))
        character.current_wounds = min(sheet.max_wounds, wounds + amount)
    elif action == "breather":
        character.current_hp = sheet.max_hp
        character.effects.filter(active=True, kind__in=["called"]).update(active=False)
    elif action == "set_hp":
        character.current_hp = max(0, min(sheet.max_hp, _int(p.get("value"), hp)))
    elif action == "set_wounds":
        character.current_wounds = max(0, min(sheet.max_wounds, _int(p.get("value"), wounds)))
    elif action == "xp":
        character.xp = max(0, min(99, character.xp + _int(p.get("delta"))))
        if "set" in p:
            character.xp = max(0, min(99, _int(p.get("set"))))
        if character.xp >= tables.XP_PER_LEVEL and character.level < tables.MAX_LEVEL:
            messages.success(request, "Enough experience for a new level!")
    elif action == "money":
        field = "money_in_bank" if p.get("where") == "bank" else "money_on_hand"
        unit = tables.DUKES_PER_PRINCE if p.get("unit", "pr") == "pr" else 1
        delta = _int(p.get("amount")) * unit * (-1 if p.get("sign") == "-" else 1)
        setattr(character, field, getattr(character, field) + delta)
        if p.get("transfer"):
            other = "money_on_hand" if field == "money_in_bank" else "money_in_bank"
            setattr(character, other, getattr(character, other) - delta)
    elif action == "stance":
        slug = p.get("stance", "")
        valid = {s["slug"] for s in sheet.stances}
        character.stance = slug if slug in valid and slug != character.stance else ""
    elif action == "toggle":
        key = p.get("key", "")
        toggles = set(character.toggles)
        if key in toggles:
            toggles.discard(key)
        elif key in {t["key"] for t in sheet.toggles}:
            toggles.add(key)
        character.toggles = sorted(toggles)
    elif action == "effect_add":
        text = p.get("text", "").strip()
        kind = p.get("kind", "status")
        if text and kind in dict(EffectEntry.KIND_CHOICES):
            loc = _int(p.get("location"), 0) or None
            EffectEntry.objects.create(character=character, kind=kind, text=text[:255],
                                       location=loc if loc and 1 <= loc <= 12 else None,
                                       lost_wounds=max(0, _int(p.get("lost_wounds"))) if kind == "fatal" else 0)
    elif action == "effect_remove":
        character.effects.filter(pk=_int(p.get("id"))).update(active=False)
    elif action == "equip":
        item = InventoryItem.objects.filter(character=character, pk=_int(p.get("id"))).first()
        slot = p.get("slot", "carried")
        if item and slot in {s for s, _ in InventoryItem._meta.get_field("slot").choices}:
            if slot in ("weapon1", "weapon2", "armor", "deflection"):
                InventoryItem.objects.filter(character=character, slot=slot).exclude(pk=item.pk).update(slot="carried")
            item.slot = slot
            item.save(update_fields=["slot"])
    elif action == "quantity":
        item = InventoryItem.objects.filter(character=character, pk=_int(p.get("id"))).first()
        if item:
            q = item.quantity + _int(p.get("delta"))
            if q <= 0:
                item.delete()
            else:
                item.quantity = q
                item.save(update_fields=["quantity"])
    elif action == "drop":
        InventoryItem.objects.filter(character=character, pk=_int(p.get("id"))).delete()
    elif action == "notes":
        character.notes = p.get("notes", "")
    character.save()
    # Clamp current values if max values changed (e.g. armor, fatigue).
    new = character.compute()
    changed = False
    if character.current_hp is not None and character.current_hp > new.max_hp:
        character.current_hp, changed = new.max_hp, True
    if character.current_wounds is not None and character.current_wounds > new.max_wounds:
        character.current_wounds, changed = new.max_wounds, True
    if changed:
        character.save(update_fields=["current_hp", "current_wounds"])
    return _respond(request, character)
