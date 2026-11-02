"""The character sheet and in-play actions (HP, wounds, XP, money, stances, toggles, effects)."""

from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from catalog.models import KIND_CHOICES, ItemTemplate
from rules.engine import effects as fx
from rules.lang import gettext as _
from rules.engine import tables
from rules.engine.requirements import character_warnings
from rules.registry import get_registry

from ..templatetags.sheet_tags import effect_html

from .. import access, journal, services
from ..models import EffectEntry, InventoryItem

TAB_NAMES = ("page1", "page2", "inventory", "story")
BARREL_LINES = 14
# Silhouette positions (svg units, see page1.html) of the called-shot locations.
BODY_POSITIONS = {1: (65, 12), 2: (65, 31), 3: (82, 22), 4: (65, 55), 5: (65, 105), 6: (65, 165),
                  7: (28, 119), 8: (102, 119), 9: (16, 183), 10: (114, 183), 11: (53, 232), 12: (77, 232)}


def effect_options():
    """Data for the add-effect form (Alpine): status effects and the called-shot chart."""
    called = {}
    labels = fx.location_labels()
    for n in labels:
        called[n] = [{"kind": k, "label": "{}: {}".format(fx.called_label(k), e['name']), "text": e["text"]}
                     for k in fx.CALLED_KINDS for e in [fx.get(fx.called_key(n, k))]]
    return {
        "status": [{"key": f"status:{e['slug']}", "name": e["name"], "text": e["text"]} for e in fx.status_list()],
        "locations": [{"n": n, "label": f"{n} – {label}"} for n, label in labels.items()],
        "called": called,
    }


def sheet_context(request, character):
    sheet = character.compute()
    reg = get_registry()
    hp = character.current_hp if character.current_hp is not None else sheet.max_hp
    wounds = character.wounds_taken
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
    locations = {n: [] for n in fx.LOCATION_LABELS}
    for e in effects:
        if e.location:
            locations[e.location].append(e)
    spec_data = {}
    for row in sheet.specialty_rows:
        sp = row["specialty"]
        spec_data[row["slug"]] = {
            "slug": row["slug"], "name": sp["name"], "skill": sp["skill"] or "General (Sciences)", "cost": sp["cost"],
            "requires": sp["requires_text"], "effect": sp["effect"], "effect_html": effect_html(sp["effect"]), "usage_note": sp.get("usage_note", ""),
            "options": sp.get("options"), "choice": character.specialty_choices.get(row["slug"], ""),
            "bonuses": ", ".join(f"{_(tables.COMBAT_STAT_LABELS[k])} {v:+d}" for k, v in sp["bonuses"].items()),
        }
    # The Gear/Augments/Notes boxes on p.2 are ruled with BARREL_LINES lines; fill the rest with blanks.
    gear_count = sum(1 for i in items if i.slot != "stored")
    aug_count = len(augments) + len(character.body_augments) + (1 if sheet.stats["aug"].total > len(augments) else 0)
    notes_count = bool(character.personality) + len(sheet.notes) + len(character.notes.splitlines())
    return {
        "character": character, "sheet": sheet, "hp": hp, "wounds": wounds,
        "blank_lines": {k: range(max(0, BARREL_LINES - n)) for k, n in
                        (("gear", gear_count), ("augments", aug_count), ("notes", notes_count))},
        "spec_data": spec_data,
        "slot_choices": InventoryItem._meta.get_field("slot").choices,
        "effects": effects,
        "effect_boxes": [("Wound Effects", [e for e in effects if e.kind == "wound"]),
                         ("Fatal Effects", [e for e in effects if e.kind == "fatal"]),
                         ("Status Effects", [e for e in effects if e.kind in ("normal", "status")])],
        "body_locations": [{"n": n, "label": label, "x": BODY_POSITIONS[n][0], "y": BODY_POSITIONS[n][1],
                            "hits": locations[n]} for n, label in fx.location_labels().items()],
        "effect_options": effect_options(),
        "spec_warnings": character_warnings(sheet.state),
        "missing_options": services.missing_options(character),
        "has_wings": services.has_wings(character),
        "battle_theme": battle_theme_state(character),
        "specialty_slots": slots,
        "stat_cols": tables.COMBAT_STATS, "stat_labels": tables.COMBAT_STAT_LABELS,
        "augments": augments, "stories": stories,
        "items": items,
        "item_kinds": [(v, label) for v, label in KIND_CHOICES if any(i.kind == v for i in items)],
        "carried": [i for i in items if i.slot in ("carried", "worn")],
        "stored": [i for i in items if i.slot == "stored"],
        "money_on_hand": tables.format_money(character.money_on_hand),
        "money_in_bank": tables.format_money(character.money_in_bank),
        "journal": journal.sections(character.story_notes),
        "xp_range": range(1, 13),
        "xp_hand": max(1, min(12, character.xp)),
        "admin_mode": access.in_admin_mode(request, character),
        "admin_allowed": access.admin_mode_allowed(request, character),
        "is_gm": access.is_gm(request),
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
    moved = services.normalize_hands(character)
    if moved:
        messages.info(request, _("{items} needs both hands (or the other hand is full) and was put away.", items=", ".join(moved)))
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
    action = action.replace("-", "_")  # URL slugs use hyphens (effect-add → effect_add)
    sheet = character.compute()
    p = request.POST
    hp = character.current_hp if character.current_hp is not None else sheet.max_hp
    wounds = character.wounds_taken  # counts up from 0 (unhurt) to max wounds

    if action == "damage":
        # Damage reduces HP first; the rest goes to wounds (p.10). "direct" skips HP.
        amount = max(0, _int(p.get("amount")))
        if p.get("direct"):
            wounds += amount
        else:
            to_hp = min(hp, amount)
            hp -= to_hp
            wounds += amount - to_hp
        took_wounds = wounds > character.wounds_taken
        was_full = character.wounds_taken >= sheet.max_wounds
        character.current_hp, character.wounds_taken = hp, min(sheet.max_wounds, wounds)
        if took_wounds and was_full:
            messages.warning(request, _("All wounds taken: this hit causes a fatal effect (roll a location)."),
                             extra_tags="popup")
        elif wounds >= sheet.max_wounds:
            messages.warning(request, _("All wounds taken: every further hit causes a fatal effect (roll a location)."))
        elif took_wounds:
            messages.warning(request, _("Wounds damage: roll a called-shot location for the wounded effect."))
    elif action == "heal":
        amount = max(0, _int(p.get("amount")))
        character.current_hp = min(sheet.max_hp, hp + amount)
    elif action == "heal_wounds":
        amount = max(0, _int(p.get("amount"), 1))
        character.wounds_taken = max(0, wounds - amount)
    elif action == "breather":
        character.current_hp = sheet.max_hp
        ended = [k for k, e in fx.EFFECTS.items() if e.get("breather")]
        character.effects.filter(active=True, key__in=ended).update(active=False)
    elif action == "set_hp":
        character.current_hp = max(0, min(sheet.max_hp, _int(p.get("value"), hp)))
    elif action == "set_wounds":
        character.wounds_taken = max(0, min(sheet.max_wounds, _int(p.get("value"), wounds)))
    elif action == "xp":
        character.xp = max(0, min(99, character.xp + _int(p.get("delta"))))
        if "set" in p:
            character.xp = max(0, min(99, _int(p.get("set"))))
        if character.xp >= tables.XP_PER_LEVEL and character.level < tables.MAX_LEVEL:
            messages.success(request, _("Enough experience for a new level!"))
    elif action == "money":
        field = "money_in_bank" if p.get("where") == "bank" else "money_on_hand"
        unit = {"k": tables.DUKES_PER_KING, "pr": tables.DUKES_PER_PRINCE, "d": 1}.get(p.get("unit", "pr"), 1)
        delta = _int(p.get("amount")) * unit * (-1 if p.get("sign") == "-" else 1)
        setattr(character, field, getattr(character, field) + delta)
        if p.get("transfer"):
            other = "money_on_hand" if field == "money_in_bank" else "money_in_bank"
            setattr(character, other, getattr(character, other) - delta)
    elif action == "stance":
        slug = p.get("stance", "")
        stances = {s["slug"]: s for s in sheet.stances}
        if slug in stances and slug != character.stance:
            # Entering a stance costs 1 AP (book p.12); leaving one is free.
            if pay_ap(request, character, STANCE_AP, stances[slug]["label"]):
                character.stance = slug
        else:
            character.stance = ""
    elif action == "toggle":
        key = p.get("key", "")
        toggles = set(character.toggles)
        ongoing = {t["key"]: t for t in sheet.ongoing if t["available"]}
        if key in toggles:
            if key not in ongoing or pay_ap(request, character, ongoing[key]["stop"], ongoing[key]["label"], stop=True):
                toggles.discard(key)
        elif key in ongoing:
            o = ongoing[key]
            if pay_ap(request, character, o["start"], o["label"]):
                toggles.add(key)
                if o["upkeep"]:
                    messages.info(request, _("{label}: {n} AP upkeep at the start of each further turn.",
                                             label=o["label"], n=o["upkeep"]))
        elif key in {t["key"] for t in sheet.toggles}:
            toggles.add(key)
        character.toggles = sorted(toggles)
    elif action.startswith("fight_"):
        fight_action(request, character, sheet, action[6:], p)
    elif action == "effect_add":
        popups = add_effect(character, p)
        if popups:
            messages.warning(request, " ".join(popups), extra_tags="popup")
    elif action == "theme_sundered":
        text = cancel_battle_theme(character, "sunder")
        if text:
            messages.warning(request, text, extra_tags="popup")
    elif action == "spec_option":
        services.set_specialty_option(character, p.get("slug", ""), p.get("value", ""))
    elif action == "effect_remove":
        character.effects.filter(pk=_int(p.get("id"))).update(active=False)
    elif action == "equip":
        item = InventoryItem.objects.filter(character=character, pk=_int(p.get("id"))).first()
        slot = p.get("slot", "carried")
        if item and slot in {s for s, _ in InventoryItem._meta.get_field("slot").choices}:
            try:
                result = services.equip(character, item, slot)
            except services.EquipError as exc:
                messages.error(request, str(exc))
            else:
                if result["moved"]:
                    messages.info(request, _("Put away (now carried): {items}.", items=", ".join(result["moved"])))
                if result["notice"]:
                    messages.warning(request, result["notice"], extra_tags="popup")
    elif action == "quantity":
        item = InventoryItem.objects.filter(character=character, pk=_int(p.get("id"))).first()
        if item:
            q = item.quantity + _int(p.get("delta"))
            if q <= 0:
                item.delete()
            else:
                item.quantity = q
                item.save(update_fields=["quantity"])
    elif action == "add_item":
        name = p.get("name", "").strip()[:120]
        if name:
            template, _created = ItemTemplate.objects.get_or_create(name=name, kind="general",
                                                             defaults={"source": "custom", "material": "organic"})
            item = InventoryItem.from_template(character, template, quantity=max(1, _int(p.get("quantity"), 1)))
            item.notes = p.get("notes", "").strip()[:255]
            item.save()
    elif action == "drop":
        InventoryItem.objects.filter(character=character, pk=_int(p.get("id"))).delete()
    elif action == "story":
        character.story_notes = p.get("story_notes", "")
    elif action == "notes":
        character.notes = p.get("notes", "")
    if action in ("stance", "toggle", "effect_add"):
        end_unavailable(request, character)
    character.save()
    # Clamp current values if max values changed (e.g. armor, fatigue).
    new = character.compute()
    changed = False
    if character.current_hp is not None and character.current_hp > new.max_hp:
        character.current_hp, changed = new.max_hp, True
    if character.wounds_taken > new.max_wounds:
        character.wounds_taken, changed = new.max_wounds, True
    if changed:
        character.save(update_fields=["current_hp", "wounds_taken"])
    return _respond(request, character)


STANCE_AP = 1


def end_unavailable(request, character):
    """Switch off what lost its precondition (leaving Berserker ends Bloodlust and Unquenchable Thirst)."""
    for _round in range(3):  # chains: Unquenchable Thirst needs Bloodlust needs Berserker
        stale = [o for o in character.compute().ongoing if o["active"] and not o["available"]]
        if not stale:
            return
        character.toggles = [k for k in character.toggles if k not in {o["key"] for o in stale}]
        messages.info(request, _("Ended: {items}.", items=", ".join(o["label"] for o in stale)))


def pay_ap(request, character, cost, label, stop=False):
    """Switching something that costs AP. In fight mode the AP are taken from this round's pool
    (refused if too few are left); outside fight mode only an info bar says what it costs."""
    if not cost:
        return True
    f = character.fight
    if f.get("active"):
        if f.get("ap", 0) < cost:
            messages.error(request, _("Not enough AP: {label} needs {n} AP, you have {ap} left.",
                                      label=label, n=cost, ap=f.get("ap", 0)))
            return False
        character.fight = dict(f, ap=f["ap"] - cost)
        messages.info(request, _("{label}: {n} AP spent.", label=label, n=cost))
    else:
        text = _("Stopping {label} costs {n} AP.", label=label, n=cost) if stop else \
            _("{label}: {n} AP to start.", label=label, n=cost)
        messages.info(request, text)
    return True


def pay_upkeep(request, character, items, keep):
    """Pay the upkeep of the ``keep`` keys among ``items`` (ongoing entries) and switch off the rest."""
    f = dict(character.fight)
    paid = [o for o in items if o["key"] in keep]
    dropped = [o for o in items if o["key"] not in keep]
    f["ap"] = f.get("ap", 0) - sum(o["upkeep"] for o in paid)
    f.pop("upkeep_choice", None)
    character.fight = f
    character.toggles = [k for k in character.toggles if k not in {o["key"] for o in dropped}]
    if paid:
        messages.info(request, _("Upkeep: {n} AP for {items}.", n=sum(o["upkeep"] for o in paid),
                                 items=", ".join(o["label"] for o in paid)))
    if dropped:
        messages.warning(request, _("Ended (no AP for the upkeep): {items}.",
                                    items=", ".join(o["label"] for o in dropped)))


def fight_action(request, character, sheet, what, p):
    """Fight mode: AP left this round. Spending (on your turn or reflexively) subtracts right away;
    "my turn" pays the upkeep of ongoing performances; AP refresh at the end of your turn."""
    max_ap = sheet.stats["ap"].total
    f = dict(character.fight)
    if what == "start":
        f = {"active": True, "ap": max_ap, "my_turn": False, "round": 1}
    elif what == "stop":
        f = {}
    elif not f.get("active"):
        return
    elif what == "spend":
        amount = max(0, _int(p.get("amount"), 1))
        if amount > f.get("ap", 0):
            messages.error(request, _("Only {ap} AP left this round.", ap=f.get("ap", 0)))
            return
        f["ap"] -= amount
    elif what == "undo":
        f["ap"] = min(max_ap, f.get("ap", 0) + 1)
    elif what == "turn":
        f["my_turn"] = True
        character.fight = f
        items = [o for o in sheet.ongoing if o["active"] and o["upkeep"]]
        ap = f.get("ap", 0)
        if sum(o["upkeep"] for o in items) <= ap:
            pay_upkeep(request, character, items, {o["key"] for o in items})
        elif len(items) == 1 or ap < min(o["upkeep"] for o in items):
            pay_upkeep(request, character, items, set())
        else:
            # Not enough AP for everything: the player picks what to keep (dialog in sheet_body.html).
            character.fight = dict(f, upkeep_choice=True)
        return
    elif what == "upkeep":
        items = [o for o in sheet.ongoing if o["active"] and o["upkeep"]]
        keep = set(p.getlist("keep")) & {o["key"] for o in items}
        if sum(o["upkeep"] for o in items if o["key"] in keep) > f.get("ap", 0):
            messages.error(request, _("That needs more AP than you have left."))
            return
        pay_upkeep(request, character, items, keep)
        return
    elif what == "end_turn":
        f.update(ap=max_ap, my_turn=False, round=f.get("round", 1) + 1)
    character.fight = f


# Battle Theme is cancelled by a called shot to the neck (singing), or by a disarm (called shot to a
# hand) or a sunder of the instrument ("sunder").
THEME_CANCEL = {"singing": {4}, "instrument": {9, 10, "sunder"}}


def add_effect(character, p):
    """Status effect (``key`` or custom ``text``) or called-shot effect (``location`` + ``which``).
    Returns pop-up texts for consequences (dropped item, cancelled Battle Theme)."""
    popups = []
    if p.get("kind") == "called":
        loc = _int(p.get("location"))
        key = fx.called_key(loc, p.get("which"))
        data = fx.get(key)
        if data:
            EffectEntry.objects.create(character=character, kind=data["kind"], key=key, location=loc,
                                       text=data["name"], lost_wounds=data.get("lost_wounds", 0))
            if data.get("drop"):
                dropped = drop_from_hand(character, loc)
                if dropped:
                    popups.append(_("You dropped {item} (1 AP to pick it up). It is now carried.", item=dropped))
            popups.append(cancel_battle_theme(character, loc))
        return [t for t in popups if t]
    data = fx.get(p.get("key"))
    if data and data["kind"] == "status":
        EffectEntry.objects.create(character=character, kind="status", key=p["key"], text=data["name"])
    elif p.get("text", "").strip():
        EffectEntry.objects.create(character=character, kind="status", text=p["text"].strip()[:255])
    return []


def cancel_battle_theme(character, location):
    spec = get_registry().specialties_by_name.get("Battle Theme")
    key = f"spec:{spec['slug']}" if spec else ""
    if not spec or key not in character.toggles:
        return ""
    mode = character.specialty_choices.get(spec["slug"], "")
    if location not in THEME_CANCEL.get(mode, set()):
        return ""
    character.toggles = [t for t in character.toggles if t != key]
    what = {4: _("a called shot to your neck"), "sunder": _("your instrument being sundered or knocked away")}.get(
        location, _("being disarmed (called shot to your hand)"))
    return _("Your Battle Theme has been cancelled by {what}. Start it again for 2 AP.", what=what)


def drop_from_hand(character, location):
    """Called shot to a hand: the item held in that hand (9 = left, 10 = right) is dropped."""
    layout = character.compute().hands
    if location == 9:
        item = layout["left"]
    else:
        item = layout["right"] or layout["blocked_by"]
    if item is None or item.id is None:
        return ""
    InventoryItem.objects.filter(character=character, pk=item.id).update(slot="carried")
    return item.name


def battle_theme_state(character):
    """(slug, mode, active) of the character's Battle Theme, or None."""
    spec = get_registry().specialties_by_name.get("Battle Theme")
    if not spec or spec["slug"] not in {s for s, _ in character.specialties}:
        return None
    return spec["slug"], character.specialty_choices.get(spec["slug"], ""), f"spec:{spec['slug']}" in character.toggles
