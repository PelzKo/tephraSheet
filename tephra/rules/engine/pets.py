"""Animals (Pets & Predators extension): a pet's stat block, pure Python.

A pet is built like the book's steps: size × niche template, movement traits, special traits and training
stories (each worth SP), then one derived-stat row per SP (bio-engineered animals: per level instead).
Every number is a ``Value`` with labelled parts, so the sheet's hover/tap popover shows the exact formula
(e.g. HP = 9 template + 6 HP × 8 SP).
"""

from dataclasses import dataclass, field

from rules.lang import gettext as _
from rules.registry import get_registry

from .formula import evaluate
from .modifiers import Value

ATTRS = ("Brute", "Cunning", "Dexterity", "Spirit", "Sciences")
COMBAT = ("acc", "eva", "stk", "def")
MAJOR = {"acc": 2, "eva": 2, "stk": 2, "def": 2, "pri": 4, "spd": 5}  # derived step 2
MINOR = {"acc": 1, "eva": 1, "stk": 1, "def": 1, "pri": 2}  # derived step 3
PRIMARY = {"land": "spd", "water": "swim", "air": "fly"}
SPEEDS = ("spd", "climb", "swim", "fly")


@dataclass
class PetState:
    template: str
    movement: list = field(default_factory=list)  # movement trait slugs
    traits: list = field(default_factory=list)  # [slug, choice] pairs
    stories: list = field(default_factory=list)  # training story slugs
    derived: list = field(default_factory=list)  # [{"attrs": {"Brute": 2, …}, "major": "acc", "minor": "eva"}]
    sp_bonus: int = 0
    origin: str = "tamed"  # tamed | bioengineered | bought | preset
    wild: bool = False
    stance: str = ""  # trait slug of the active stance trait
    levels: int = 0  # bio-engineered: derived rows come from levels, not SP


def sp_marque(sp):
    return 1 if sp <= 3 else 2 if sp <= 8 else 3 if sp <= 13 else 4


def compute_pet(state):
    """{"stats": {key: Value}, "attrs": {attr: Value}, "attacks": [...], "sp", "marque", "rows", "notes", "venom",
    "taming", "price", "traits": [trait dicts]}"""
    animals = get_registry().animals
    tpl = animals["templates"][state.template]
    traits = [(animals["traits"][s], c) for s, c in state.traits if s in animals["traits"]]
    owned = {t["slug"] for t, _c in traits}
    stories = [animals["stories"][s] for s in state.stories if s in animals["stories"]]

    sp = Value()
    sp.set_base(_("Special traits"), sum(t.get("sp", 1) for t, _c in traits))
    for s in stories:
        if s.get("sp", 1):
            sp.add(_("Story: {name}", name=s["name"]), s.get("sp", 1))
    if state.sp_bonus:
        sp.add(_("Bonus SP"), state.sp_bonus)
    marque = sp_marque(sp.total)
    rows = state.levels if state.origin == "bioengineered" else sp.total

    tlabel = _("Template: {name}", name=tpl["name"])
    stats = {k: Value() for k in ("hp", "wnd", "ap", "pri", *SPEEDS, *COMBAT, "soak_class", "dmg_class")}
    stats["hp"].set_base(tlabel, tpl["hp"])
    stats["wnd"].set_base(tlabel, tpl["wnd"])
    stats["ap"].set_base(_("All animals"), 3)
    stats["pri"].set_base(tlabel, 0)
    for k, field_ in (("spd", "land"), ("climb", "climb"), ("swim", "swim"), ("fly", "fly")):
        stats[k].set_base(tlabel, tpl["speed"][field_])
    stats["eva"].set_base(tlabel, tpl["eva"])
    stats["def"].set_base(tlabel, tpl["def"])
    stats["acc"].set_base(tlabel, tpl["attack"]["acc"])
    stats["stk"].set_base(tlabel, tpl["attack"]["stk"])
    stats["soak_class"].set_base(tlabel, tpl["soak_class"])
    stats["dmg_class"].set_base(tlabel, tpl["attack"]["dmg_class"])
    attrs = {a: Value() for a in ATTRS}
    for a in ATTRS:
        attrs[a].set_base(tlabel, tpl["attrs"].get(a, 0))

    primary = PRIMARY[tpl["niche"]]
    movement = list(state.movement) + [c for t, c in traits if t["slug"] == "mobile" and c]
    for slug in movement:
        m = animals["movement"].get(slug)
        if not m:
            continue
        label = _("Movement: {name}", name=m["name"])
        if slug == "swift":
            stats[primary].add(label, 20)
        elif slug == "climbing":
            stats["climb"].add(label, 20)
        elif slug == "amphibious":
            if tpl["niche"] == "water":
                stats["spd"].add(label, 25)
            else:
                stats["swim"].add(label, 30)

    # Derived statistics: one row per SP (per level for bio-engineered animals).
    hp_per = 14 if "extra-hardy" in owned else 10 if "hardy" in owned else 6
    hp_label = _("Extra Hardy") if hp_per == 14 else _("Hardy") if hp_per == 10 else _("Derived")
    if rows:
        stats["hp"].add(_("{label}: {hp} HP × {n}", label=hp_label, hp=hp_per, n=rows), hp_per * rows)
    for i, row in enumerate(state.derived[:rows], 1):
        label = _("Derived #{n}", n=i)
        for a, v in (row.get("attrs") or {}).items():
            if a in attrs and v:
                attrs[a].add(label, v)
        major, minor = row.get("major"), row.get("minor")
        if major in MAJOR:
            stats[primary if major == "spd" else major].add(label, MAJOR[major])
        if minor in MINOR and minor != major:
            stats[minor].add(label, MINOR[minor])
    missing = max(0, rows - len(state.derived))

    notes = []
    variables = {"sp": sp.total, "marque": marque}
    for t, choice in traits:
        label = _("Trait: {name}", name=t["name"])
        if t["slug"] == "adaptive-versatility":
            stats["hp"].add(label, hp_per)
            for stat in (choice or "").split(","):
                if stat.strip() in COMBAT:
                    stats[stat.strip()].add(label, 2)
        if t["slug"] == "tough-body":
            stats["wnd"].add(_("{label}: 2 × {n} SP", label=label, n=sp.total), 2 * sp.total)
        for m in t.get("mods", []):
            stat, when = m["stat"], m.get("when", "always")
            if stat in ("hp_per_sp", "wnd", "taming_tier", "venom_doses") or stat.startswith("<"):
                continue  # handled above / below
            if when == "stance" and state.stance != t["slug"]:
                continue
            amount = evaluate(m["formula"], variables) if "formula" in m else m.get("value", 0)
            if when == "note" or stat not in stats and not stat.startswith("roll:"):
                notes.append((t["name"], f"{_(m['label'])}: {amount:+d}" if m.get("label") else t["text"]))
            elif stat.startswith("roll:"):
                if stat[5:] in attrs:
                    attrs[stat[5:]].add(label, amount)
            elif m.get("op") == "set":
                stats[stat].override = (label, amount)
            else:
                stats[stat].add(label, amount)
    for s in stories:
        for m in s.get("mods", []):
            if m["stat"] == "ap" and m.get("op") == "set":
                stats["ap"].override = (_("Story: {name}", name=s["name"]), m["value"])
    if state.wild and marque >= 2 and not any(s["slug"].startswith("additional-ap") for s in stories):
        stats["ap"].override = (_("Wild animal, SP marque {m}", m=marque), 5 if marque == 4 else 4)

    attacks = [{"name": tpl["attack"]["name"], "ap": 2, "acc": stats["acc"], "stk": stats["stk"],
                "dmg": [stats["dmg_class"].total * t for t in (1, 2, 3, 4)], "dc": stats["dmg_class"]}]
    for t, _c in traits:
        a = t.get("attack")
        if not a:
            continue
        # Natural attacks with a damage class (Prehensile Limbs' 1-AP unarmed) also get Offensive Advantage.
        bonus = stats["dmg_class"].total - tpl["attack"]["dmg_class"]
        dmg = a.get("dmg") or ([(a["dmg_class"] + bonus) * x for x in (1, 2, 3, 4)] if a.get("dmg_class") else None)
        attacks.append({"name": a["name"], "ap": a["ap"], "acc": stats["acc"], "stk": stats["stk"], "dmg": dmg,
                        "note": t.get("cost", "")})

    venoms = [t for t, _c in traits if t.get("is_venom")]
    doses = marque * (2 if "extra-venoms" in owned else 1) if venoms else 0
    social = "social" in owned
    return {
        "stats": stats, "attrs": attrs, "attacks": attacks, "sp": sp, "marque": marque, "rows": rows,
        "missing_rows": missing, "notes": notes, "venoms": venoms, "venom_doses": doses,
        "taming": -(-sp.total // 2) if social else sp.total,
        "price_pr": sp.total * animals["price_per_sp"][marque - 1] + sum(s.get("price_pr", 0) for s in stories),
        "soak": [stats["soak_class"].total * t for t in (1, 2, 3, 4)],
        "traits": [dict(t, choice=c) for t, c in traits], "stories": stories,
        "movement": [animals["movement"][m] for m in movement if m in animals["movement"]],
        "template": tpl,
    }
