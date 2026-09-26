"""Weapon blocks for the sheet (p.74-79): AP, reach/range, Accuracy, Strike, DC per tier."""

from dataclasses import dataclass, field

from rules.registry import get_registry

from . import tables
from .modifiers import Value, mod_amount
from .state import ItemState


def one_handing(state):
    """One-Handing It: two-handed weapons (except bows) can be wielded in one hand."""
    reg = get_registry()
    return any(reg.specialties.get(s, {}).get("name") == "One-Handing It" for s, _ in state.specialties)


WINGS_TRAIT = "ayodin/wings-as-arms"


def has_wings(state):
    return WINGS_TRAIT in state.random_traits or WINGS_TRAIT in state.fixed_traits


def hand_layout(state):
    """What the hands hold: weapon1 = left, weapon2 = right, plus the wings slot (Wings as Arms).
    A two-handed item is shown in the left hand and blocks the right one; a shield or parrying
    dagger (deflection item that needs a hand) also blocks the right hand. ``free`` counts the
    empty real hands (wings don't count)."""
    oh = one_handing(state)
    left = next((i for i in state.items if i.slot == "weapon1"), None)
    right = next((i for i in state.items if i.slot == "weapon2"), None)
    wings = next((i for i in state.items if i.slot == "wings"), None) if has_wings(state) else None
    defl = state.deflection
    if left is None and right is not None and tables.item_hands(right, oh) == 2:
        left, right = right, None
    blocked_by, reason = None, ""
    if left is not None and tables.item_hands(left, oh) == 2:
        blocked_by, reason = left, f"{left.name} needs both hands"
    elif defl is not None and tables.item_hands(defl) >= 1:
        blocked_by, reason = defl, f"holding {defl.name}"
    if blocked_by is not None:
        right = None
    return {"left": left, "right": right, "wings": wings, "has_wings": has_wings(state),
            "blocked_by": blocked_by, "blocked_reason": reason, "one_handing": oh,
            "two_handed": blocked_by if blocked_by is left and left is not None else None,
            "free": (left is None) + (right is None and blocked_by is None)}


@dataclass
class WeaponBlock:
    item: ItemState
    name: str
    kind: str
    size: str
    type_label: str
    reach: str
    ap_use: Value
    ap_ready: Value | None
    acc: Value
    stk: Value | None  # None = damage uses the Accuracy roll (firearms, crossbows)
    dc: Value
    notes: list = field(default_factory=list)

    @property
    def damage(self):
        dc = max(0, self.dc.total)
        return [dc * t for t in (1, 2, 3, 4)]

    @property
    def uses_accuracy_for_damage(self):
        return self.stk is None


def _scope_applies(scope, kind, source, item):
    if scope == "weapon":
        return source.item_id is not None and source.item_id == item.id
    if scope == "melee":
        return kind in ("melee", "unarmed")
    if scope == "unarmed":
        return kind == "unarmed"
    if scope == "ranged":
        return kind in tables.RANGED_KINDS
    return False


def _apply_scoped(sheet, item, kind, acc, stk, dc, notes):
    reach_bonus = 0
    for src, m in sheet.scoped:
        if not _scope_applies(m.get("scope", "character"), kind, src, item):
            continue
        amount = mod_amount(m, sheet.variables, m.get("marque"))
        label = src.label + (f" ({m['label']})" if m.get("label") else "")
        stat = m["stat"]
        if stat == "dc":
            if m.get("op") == "base":
                dc.set_base(label, amount)
            else:
                dc.add(label, amount)
        elif stat == "acc":
            acc.add(label, amount)
        elif stat == "stk" and stk is not None:
            stk.add(label, amount)
        elif stat == "reach":
            reach_bonus += amount
    return reach_bonus


def weapon_block(sheet, item: ItemState) -> WeaponBlock:
    kind = item.kind if item.kind in tables.WEAPON_TABLES else "melee"
    table = tables.WEAPON_TABLES[kind]
    size = item.size if item.size in table else "medium"
    row = table[size]
    stats = sheet.stats
    state = sheet.state
    notes = []

    acc = stats["acc"].inherited("Accuracy (character)")
    uses_acc = kind in tables.ACCURACY_DAMAGE_KINDS
    stk = None if uses_acc else stats["stk"].inherited("Strike (character)")

    dc = Value()
    if item.dc is not None:
        dc.set_base("Item DC", item.dc)
    else:
        dc.set_base(f"{tables.SIZE_LABELS[size]} {kind}", row["dc"])
    for v in item.variants:
        spec = tables.VARIANTS.get(v)
        if not spec:
            continue
        dc.add(spec["label"], spec.get("dc", 0))
        acc.add(spec["label"], spec.get("acc", 0))
        if stk is not None:
            stk.add(spec["label"], spec.get("stk", 0))
    if row.get("footing") and state.stance != "footing":
        acc.add("Super-heavy without Footing", tables.SUPER_HEAVY_NO_FOOTING)
        if stk is not None and kind == "melee":
            stk.add("Super-heavy without Footing", tables.SUPER_HEAVY_NO_FOOTING)
        notes.append("Enter the Footing stance to avoid −3.")

    reach_bonus = _apply_scoped(sheet, item, kind, acc, stk, dc, notes)
    dc.floor = 0

    ap_use = Value()
    ap_use.set_base("Item" if item.ap_use is not None else "Size table",
                    item.ap_use if item.ap_use is not None else row["ap"])
    ap_ready = None
    if kind in tables.RANGED_KINDS:
        ap_ready = Value()
        base_ready = item.ap_ready if item.ap_ready is not None else row.get("ready", 0)
        ap_ready.set_base("Item" if item.ap_ready is not None else "Size table", base_ready)
        if kind == "firearm" and size == "medium" and item.ap_ready is None:
            notes.append("Ready 0 AP when held with two hands.")
        for label, amount in sheet.ap_ready_mods:
            ap_ready.add(label, amount)
        ap_ready.floor = 0

    if kind in tables.RANGED_KINDS:
        rng = item.range if item.range is not None else row["range"]
        inc = item.increment if item.increment is not None else row["increment"]
        reach = f"{rng} ft (−1/{inc} ft)"
    else:
        reach_ft = item.reach if item.reach is not None else 5 + (5 if "polearm" in item.variants else 0)
        reach_ft += reach_bonus
        reach = "Adjacent" if reach_ft <= 5 else f"{reach_ft} ft"
        if "throwing" in item.variants:
            reach += f" / throw {tables.THROW_RANGE.get(size, 25)} ft"
    if tables.needs_firing_position(item):
        notes.append("Rotating barrels: fire only from a firing position.")
    elif tables.ROTATING_BARRELS in {a[0] for a in item.augments} and item.hands is None:
        notes.append("Rotating barrels: needs one more hand.")
    if "double-barreled" in item.variants:
        notes.append("Double-barreled: fire twice before readying.")
    if item.notes:
        notes.append(item.notes)

    variant_labels = [tables.VARIANTS[v]["label"] for v in item.variants if v in tables.VARIANTS]
    type_label = kind.capitalize() + (f" ({', '.join(variant_labels)})" if variant_labels else "")
    return WeaponBlock(item=item, name=item.name, kind=kind, size=tables.SIZE_LABELS.get(size, size),
                       type_label=type_label, reach=reach, ap_use=ap_use, ap_ready=ap_ready, acc=acc,
                       stk=stk, dc=dc, notes=notes)


def unarmed_block(sheet) -> WeaponBlock:
    item = ItemState(name="Unarmed", kind="unarmed", size="unarmed", slot="unarmed")
    acc = sheet.stats["acc"].inherited("Accuracy (character)")
    stk = sheet.stats["stk"].inherited("Strike (character)")
    dc = Value()
    dc.set_base(f"Base ({sheet.race['name']})", sheet.race.get("unarmed_dc", 2))
    _apply_scoped(sheet, item, "unarmed", acc, stk, dc, [])
    dc.floor = 0
    ap_use = Value()
    ap_use.set_base("Unarmed", tables.MELEE["unarmed"]["ap"])
    return WeaponBlock(item=item, name="Unarmed", kind="unarmed", size="Unarmed", type_label="Unarmed",
                       reach="Adjacent", ap_use=ap_use, ap_ready=None, acc=acc, stk=stk, dc=dc,
                       notes=["Can't be augmented by armsmiths."])
