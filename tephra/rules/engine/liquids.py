"""Released living liquids (Living Liquids extension): the stat block of one liquid, pure Python.

A released liquid is an item (kind ``living-liquid``, slot ``released``). Its augments' modifiers use
``scope: "liquid"`` and never touch the character. Every value is a ``Value`` with labelled parts, so the
sheet's breakdown popover shows where each number comes from.
"""

from rules.lang import gettext as _
from rules.registry import get_registry

from .modifiers import Value, mod_amount

BASE = {"hp": 20, "ap": 2, "spd": 20, "fly": 0, "dc": 2, "soak": 0, "acc": 0, "eva": 0, "def": 0, "stk": 0,
        "evaporation": 5}
IMPROPER = {"hp": 10, "evaporation": 10}  # smashed vial (narrator ruling)
ROLLS = ("Brute", "Dexterity", "Cunning")
ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV"}


def liquid_block(item):
    """{"stats": {key: Value}, "rolls": {attribute: Value}, "notes": [text], "improper": bool}."""
    improper = "improper" in (item.variants or [])
    stats = {}
    for key, base in BASE.items():
        v = Value()
        if improper and key in IMPROPER:
            v.set_base(_("Improper release"), IMPROPER[key])
        else:
            v.set_base(_("Living liquid"), base)
        stats[key] = v
    stats["evaporation"].floor = 0
    stats["hp"].floor = 0
    rolls = {r: Value() for r in ROLLS}
    notes = []
    sources = [(m.get("label") or _("Release"), m, None) for m in item.modifiers or []]
    reg = get_registry()
    for slug, marque in item.augments or []:
        a = reg.augments.get(slug)
        if not a:
            continue
        label = f"{a['name']} mQ {ROMAN.get(marque, marque)}"
        notes.append(f"{label}: {a['marques'][marque - 1]}")
        sources += [(label, m, marque) for m in a.get("modifiers", [])]
    for label, m, marque in sources:
        stat = m["stat"]
        if stat == "note" or m.get("when") == "note":
            continue  # already in the notes as marque text
        amount = mod_amount(m, {}, marque)
        if stat.startswith("roll:") and stat[5:] in rolls:
            rolls[stat[5:]].add(label, amount)
        elif stat in stats:
            if m.get("op") == "base":
                stats[stat].set_base(label, amount)
            else:
                stats[stat].add(label, amount)
    return {"stats": stats, "rolls": rolls, "notes": notes, "improper": improper}
