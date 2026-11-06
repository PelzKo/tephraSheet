"""Automatons (core Automata rules, recorded like the Automaton Crafting Sheet): the stat block, pure Python.

Base values by type (Playing Guide pp.197–206): steamer 0 HP / 30 wounds / +3 soak / no own AP (the controller
pays), fuse box 8 HP / 12 wounds / 2 AP (Superior +1, Heroic +2 for DIY-built ones), clockwork 0 HP / 20 wounds /
no AP. The book gives no base Accuracy/Evade/Strike/Defense/Priority: they start at 0 and come from augments, fuse
box specialties, a steamer's operator (Steamer Operator: the higher value) and manual Misc. Every number is a
``Value`` with labelled parts for the sheet's breakdown popover.
"""

from dataclasses import dataclass, field

from rules.lang import gettext as _
from rules.registry import get_registry

from . import tables
from .modifiers import Value, mod_amount

TYPES = {
    "steamer": {"label": "Steamer", "hp": 0, "wnd": 30, "soak": 3, "ap": None, "core": "steamer", "core_label": "Boiler"},
    "fusebox": {"label": "Fuse box", "hp": 8, "wnd": 12, "soak": 0, "ap": 2, "core": "fusebox", "core_label": "Brainworks"},
    "clockwork": {"label": "Clockwork", "hp": 0, "wnd": 20, "soak": 0, "ap": None, "core": "clockwork",
                  "core_label": "Analytical engine"},
}
MOVEMENT = {"arms": None, "legs": ("spd", 20), "wheels": ("spd", 30), "propulsion": ("spd", 20),
            "propulsion-water": ("swim", 20)}
FUSEBOX_SPECIALTIES = {1: 1, 2: 2, 3: 3, 4: 5}
STATS = ("hp", "wnd", "soak", "ap", "pri", "spd", "swim", "climb", "fly", "acc", "eva", "stk", "def")
ATTRS = ("Brute", "Cunning", "Dexterity", "Spirit", "Sciences")
ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV"}


@dataclass
class AutomatonState:
    type: str = "steamer"
    marque: int = 1
    advanced: bool = False
    diy: bool = True
    core_augments: list = field(default_factory=list)  # [[slug, marque]]
    limbs: list = field(default_factory=list)  # [{"name", "material", "beta", "augments": [[slug, marque]]}]
    movement: dict = field(default_factory=dict)  # {"torso": "arms|legs|…", "groin": "legs|wheels|…"}
    specialties: list = field(default_factory=list)  # fuse box only
    misc: dict = field(default_factory=dict)
    toggles: list = field(default_factory=list)
    armor: object = None  # ItemState
    weapon: object = None  # ItemState


def compute_automaton(auto, owner_specialties=(), owner_stats=None, owner_augments=()):
    """``owner_specialties``: slugs the creator knows; ``owner_stats``: the creator's sheet stats (Steamer
    Operator); ``owner_augments``: augment slugs the creator knows (warning only)."""
    reg = get_registry()
    t = TYPES[auto.type]
    owned = set(owner_specialties)
    stats = {k: Value() for k in STATS}
    base = _("{type} (base)", type=_(t["label"]))
    stats["hp"].set_base(base, t["hp"])
    stats["wnd"].set_base(base, t["wnd"])
    stats["soak"].set_base(base, t["soak"])
    for k in ("pri", "acc", "eva", "stk", "def", "spd", "swim", "climb", "fly"):
        stats[k].set_base(base, 0)
    has_ap = t["ap"] is not None
    if has_ap:
        stats["ap"].set_base(base, t["ap"])
        if auto.diy and "automata-heroic-brainworks" in owned:
            stats["ap"].set_base(_("Heroic Brainworks"), 4)
        elif auto.diy and "automata-superior-brainworks" in owned:
            stats["ap"].set_base(_("Superior Brainworks"), 3)
    attrs = {a: Value() for a in ATTRS}
    for a in ATTRS:
        attrs[a].set_base(base, 0)

    for part in ("torso", "groin"):
        unit = MOVEMENT.get(auto.movement.get(part, ""))
        if unit and unit[1] > stats[unit[0]].total:
            stats[unit[0]].set_base(_("Movement: {unit}", unit=_(auto.movement[part])), unit[1])

    warnings = []
    core_slots = 3 + (2 if auto.advanced else 0)
    sources = []

    def add_augments(augs, where, allowed):
        used = 0
        for slug, marque in augs:
            a = reg.augments.get(slug)
            if not a:
                continue
            used += a.get("slots") or 0
            if not set(a["lists"]) & allowed:
                warnings.append(_("{augment} doesn't belong on the {where}.", augment=a["name"], where=where))
            if owner_augments and slug not in owner_augments:
                warnings.append(_("{augment}: the creator doesn't know this augment.", augment=a["name"]))
            label = f"{a['name']} mQ {ROMAN.get(marque, marque)}"
            sources.extend((f"auto:{slug}", label, m, marque) for m in a.get("modifiers", []))
        return used

    used = add_augments(auto.core_augments, _(t["core_label"]), {t["core"]})
    if used > core_slots:
        warnings.append(_("The {core} uses {used} of {slots} augment slots.", core=_(t["core_label"]), used=used,
                          slots=core_slots))
    for limb in auto.limbs:
        slots = tables.MATERIAL_SLOTS.get(limb.get("material", "metal"), 3) + (2 if limb.get("beta") else 0)
        name = limb.get("name") or _("Limb")
        used = add_augments(limb.get("augments", []), name, {"prosthetic"})
        if used > slots:
            warnings.append(_("{limb} uses {used} of {slots} augment slots.", limb=name, used=used, slots=slots))
        if limb.get("beta") and not auto.advanced:
            warnings.append(_("{limb}: beta limbs need a beta/advanced automaton.", limb=name))

    for key, label, m, marque in sources:
        if m.get("when") == "note":
            continue
        if m.get("when") == "toggle" and key not in auto.toggles:
            continue
        amount = mod_amount(m, {}, marque)
        stat = m["stat"]
        if stat.startswith("roll:") and stat[5:] in attrs:
            attrs[stat[5:]].add(label, amount)
        elif stat in stats:
            if m.get("op") == "base":
                stats[stat].set_base(label, amount)
            else:
                stats[stat].add(label, amount)

    if auto.type == "fusebox":
        limit = FUSEBOX_SPECIALTIES.get(auto.marque, 1)
        if len(auto.specialties) > limit:
            warnings.append(_("A marque {m} fuse box knows {n} specialties.", m=ROMAN.get(auto.marque), n=limit))
        for slug in auto.specialties:
            spec = reg.specialties.get(slug)
            if not spec:
                continue
            for stat, v in spec.get("bonuses", {}).items():
                if stat in stats and v:
                    stats[stat].add(_("Specialty: {name}", name=spec["name"]), v)
            if spec.get("attribute") == "Spirit" and "automata-personality" not in owned:
                warnings.append(_("{name}: Spirit specialties need Personality.", name=spec["name"]))

    armor = None
    if auto.armor is not None:
        size = auto.armor.size if auto.armor.size in tables.ARMOR else "none"
        row = tables.ARMOR[size]
        label = _("Armor: {name}", name=auto.armor.name)
        soak = auto.armor.soak if auto.armor.soak is not None else row["soak"]
        stats["soak"].add(label, soak)
        pen = auto.armor.eva_penalty if auto.armor.eva_penalty is not None else row["eva"]
        if pen:
            stats["eva"].add(label, -pen)
        armor = {"name": auto.armor.name, "size": size, "soak": soak}

    if auto.type == "steamer" and "automata-steamer-operator" in owned and owner_stats:
        for k in ("acc", "eva", "stk", "def"):
            if owner_stats[k].total > stats[k].total:
                stats[k].override = (_("Operator (Steamer Operator)"), owner_stats[k].total)

    for k, v in (auto.misc or {}).items():
        if k in stats and v:
            stats[k].add(_("Manual Misc Change"), v)
    stats["soak"].floor = 0

    weapon = None
    if auto.weapon is not None:
        w = auto.weapon
        kind = w.kind if w.kind in tables.WEAPON_TABLES else "melee"
        table = tables.WEAPON_TABLES[kind]
        row = table.get(w.size) or table["medium"]
        dc = Value()
        dc.set_base(_("Item DC") if w.dc is not None else _("Size table"), w.dc if w.dc is not None else row["dc"])
        acc = stats["acc"].inherited(_("Accuracy (automaton)"))
        if w.acc_bonus:
            acc.add(_("Item: {name}", name=w.name), w.acc_bonus)
        weapon = {"name": w.name, "acc": acc, "stk": stats["stk"], "dc": dc,
                  "dmg": [dc.total * n for n in (1, 2, 3, 4)], "ap": w.ap_use if w.ap_use is not None else row["ap"]}

    toggles = [{"key": key, "label": label, "on": key in auto.toggles}
               for key, label, m, _m in sources if m.get("when") == "toggle"]
    return {"stats": stats, "attrs": attrs, "has_ap": has_ap, "warnings": list(dict.fromkeys(warnings)),
            "core_slots": core_slots, "armor": armor, "weapon": weapon, "toggles": toggles, "type": t,
            "soak_tiers": [stats["soak"].total * n for n in (1, 2, 3, 4)]}
