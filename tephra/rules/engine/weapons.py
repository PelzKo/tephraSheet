"""Weapon blocks for the sheet (p.74-79): AP, reach/range, Accuracy, Strike, DC per tier."""

from dataclasses import dataclass, field

from rules.lang import gettext as _
from rules.registry import get_registry

from . import tables
from .modifiers import Value, mod_amount
from .state import ItemState


def one_handing(state):
    """One-Handing It: two-handed weapons (except bows) can be wielded in one hand."""
    reg = get_registry()
    return any(reg.specialties.get(s, {}).get("name_en") == "One-Handing It" for s, _l in state.specialties)


WINGS_TRAIT = "ayodin/wings-as-arms"


def extra_hand(state):
    """The extra one-handed slot (slot "wings") from Wings as Arms or a trait with ``extra_hands``
    (Crazak Additional Arm, Ezka Faux Hands …): its label, or None."""
    if WINGS_TRAIT in state.random_traits or WINGS_TRAIT in state.fixed_traits:
        return _("Wings")
    from .stats import active_trait_keys

    reg = get_registry()
    for key in active_trait_keys(state)[0]:
        extra = reg.traits[key].get("extra_hands")
        if extra:
            return _(extra["label"])
    return None


def _footing_heavy(state):
    """Gnodin: heavy items need the Footing stance too."""
    from .stats import active_trait_keys

    reg = get_registry()
    return any(reg.traits[k].get("footing_heavy") for k in active_trait_keys(state)[0])


def has_wings(state):
    return extra_hand(state) is not None


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
        blocked_by, reason = left, _("{name} needs both hands", name=left.name)
    elif defl is not None and tables.item_hands(defl) >= 1:
        blocked_by, reason = defl, _("holding {name}", name=defl.name)
    if blocked_by is not None:
        right = None
    return {"left": left, "right": right, "wings": wings, "has_wings": has_wings(state), "extra_label": extra_hand(state),
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
        label = src.label + (f" ({_(m['label'])})" if m.get("label") else "")
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

    acc = stats["acc"].inherited(_("Accuracy (character)"))
    uses_acc = kind in tables.ACCURACY_DAMAGE_KINDS
    stk = None if uses_acc else stats["stk"].inherited(_("Strike (character)"))

    dc = Value()
    if item.dc is not None:
        dc.set_base(_("Item DC"), item.dc)
    else:
        dc.set_base(_("{size} {kind}", size=_(tables.SIZE_LABELS[size]), kind=_(kind)), row["dc"])
    for v in item.variants:
        spec = tables.VARIANTS.get(v)
        if not spec:
            continue
        vlabel = _(spec["label"])
        dc.add(vlabel, spec.get("dc", 0))
        acc.add(vlabel, spec.get("acc", 0))
        if stk is not None:
            stk.add(vlabel, spec.get("stk", 0))
    if item.acc_bonus:
        acc.add(_("Item: {name}", name=item.name), item.acc_bonus)
    if item.stk_bonus and stk is not None:
        stk.add(_("Item: {name}", name=item.name), item.stk_bonus)
    if "turret" in item.variants:
        if state.stance != "footing" and not any(s == "armsmith-fast-mounting" for s, _l in state.specialties):
            notes.append(_("Footing stance needed to fire the turret."))
    elif (row.get("footing") or size == "heavy" and _footing_heavy(state)) and state.stance != "footing":
        label = _("Super-heavy without Footing") if row.get("footing") else _("Heavy without Footing")
        acc.add(label, tables.SUPER_HEAVY_NO_FOOTING)
        if stk is not None and kind == "melee":
            stk.add(label, tables.SUPER_HEAVY_NO_FOOTING)
        notes.append(_("Enter the Footing stance to avoid −3."))

    reach_bonus = _apply_scoped(sheet, item, kind, acc, stk, dc, notes)
    if {"aether", "synced"} & set(item.variants):
        notes += _aether_notes(state)
    dc.floor = 0

    ap_use = Value()
    ap_use.set_base(_("Item") if item.ap_use is not None else _("Size table"),
                    item.ap_use if item.ap_use is not None else row["ap"])
    ap_ready = None
    if kind in tables.RANGED_KINDS:
        ap_ready = Value()
        base_ready = item.ap_ready if item.ap_ready is not None else row.get("ready", 0)
        ap_ready.set_base(_("Item") if item.ap_ready is not None else _("Size table"), base_ready)
        if kind == "firearm" and size == "medium" and item.ap_ready is None:
            notes.append(_("Ready 0 AP when held with two hands."))
        for label, amount in sheet.ap_ready_mods:
            ap_ready.add(label, amount)
        for src, m in sheet.scoped:  # e.g. Belt Fed on this turret
            if m["stat"] == "ap_ready" and _scope_applies(m.get("scope"), kind, src, item):
                ap_ready.add(src.label, mod_amount(m, sheet.variables, m.get("marque")))
        ap_ready.floor = 0

    if kind in tables.RANGED_KINDS:
        rng = item.range if item.range is not None else row["range"]
        inc = item.increment if item.increment is not None else row["increment"]
        reach = _("{range} ft (−1/{increment} ft)", range=rng, increment=inc)
    else:
        reach_ft = item.reach if item.reach is not None else 5 + (5 if "polearm" in item.variants else 0)
        reach_ft += reach_bonus
        reach = _("Adjacent") if reach_ft <= 5 else _("{n} ft", n=reach_ft)
        if "throwing" in item.variants:
            reach = _("{reach} / throw {range} ft", reach=reach, range=tables.THROW_RANGE.get(size, 25))
    if tables.needs_firing_position(item):
        notes.append(_("Rotating barrels: fire only from a firing position."))
    elif tables.ROTATING_BARRELS in {a[0] for a in item.augments} and item.hands is None:
        notes.append(_("Rotating barrels: needs one more hand."))
    if "double-barreled" in item.variants:
        notes.append(_("Double-barreled: fire twice before readying."))
    if item.notes:
        notes.append(item.notes)

    variant_labels = [_(tables.VARIANTS[v]["label"]) for v in item.variants if v in tables.VARIANTS]
    type_label = _(kind.capitalize()) + (f" ({', '.join(variant_labels)})" if variant_labels else "")
    return WeaponBlock(item=item, name=item.name, kind=kind, size=_(tables.SIZE_LABELS.get(size, size)),
                       type_label=type_label, reach=reach, ap_use=ap_use, ap_ready=ap_ready, acc=acc,
                       stk=stk, dc=dc, notes=notes)


def unarmed_block(sheet) -> WeaponBlock:
    item = ItemState(name=_("Unarmed"), kind="unarmed", size="unarmed", slot="unarmed")
    acc = sheet.stats["acc"].inherited(_("Accuracy (character)"))
    stk = sheet.stats["stk"].inherited(_("Strike (character)"))
    dc = Value()
    from .stats import body_race

    body = body_race(sheet.state)
    dc.set_base(_("Base ({name})", name=body["name"]), body.get("unarmed_dc", 2))
    _apply_scoped(sheet, item, "unarmed", acc, stk, dc, [])
    dc.floor = 0
    ap_use = Value()
    ap_use.set_base(_("Unarmed"), tables.MELEE["unarmed"]["ap"])
    notes = [_("Can't be augmented by armsmiths.")]
    if any(i.name == "Manipulator Glove" and i.slot == "worn" for i in sheet.state.items):
        notes += _aether_notes(sheet.state)
    return WeaponBlock(item=item, name=_("Unarmed"), kind="unarmed", size=_("Unarmed"), type_label=_("Unarmed"),
                       reach=_("Adjacent"), ap_use=ap_use, ap_ready=None, acc=acc, stk=stk, dc=dc, notes=notes)


def _aether_notes(state):
    """The worn resonators' augments (Aether): they apply to aether-shaped/synced weapons and gloved fists."""
    reg = get_registry()
    out = []
    for r in state.items:
        if r.kind == "resonator" and r.slot not in ("carried", "stored", ""):
            for slug, marque in r.augments:
                a = reg.augments.get(slug)
                if a:
                    out.append(_("Aether: {name} mQ {marque} – {effect}", name=a["name"],
                                 marque="I II III IV".split()[marque - 1], effect=a["marques"][marque - 1]))
    return out
