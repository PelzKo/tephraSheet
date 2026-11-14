"""Bulk import of items from CSV files or pasted tables (CSV, TSV, ;-separated, markdown)."""

import csv
import io
import json
import re

from rules.engine import item_requirements
from rules.engine.tables import VARIANTS
from rules.extensions import EXTENSIONS
from rules.lang import gettext as _
from rules.registry import get_registry

from .models import KIND_CHOICES, MATERIAL_CHOICES, SIZE_CHOICES

TEMPLATE_HEADER = ["name", "kind", "size", "variants", "material", "dc", "ap_use", "ap_ready", "reach", "range",
                   "increment", "soak", "eva_penalty", "spd_penalty", "climb_swim_penalty", "deflect_bonus",
                   "deflect_ranged", "deflect_melee", "concealable", "hands", "beta", "augments", "price",
                   "is_starting_gear", "quantity", "description"]
TEMPLATE_ROWS = [
    ["Cavalry Sabre", "melee", "medium", "", "metal", "", "", "", "", "", "", "", "", "", "", "", "", "", "no", "", "no",
     "Accurate I", "7 pr", "no", "1", "A curved officer's blade."],
    ["Boarding Pike", "melee", "heavy", "polearm", "wood", "", "", "", "", "", "", "", "", "", "", "", "", "", "no", "2",
     "no", "", "12 pr", "no", "1", ""],
    ["Pepperbox Pistol", "firearm", "light", "", "metal", "", "", "", "", "", "", "", "", "", "", "", "", "", "yes", "1",
     "no", "", "2 pr", "no", "1", ""],
    ["Brass Cuirass", "armor", "medium", "", "metal", "", "", "", "", "", "", "", "", "", "", "", "", "", "no", "", "no",
     "Damage Soaking I", "15 pr", "no", "1", ""],
]

ALIASES = {
    "item": "name", "weapon": "name", "type": "kind", "category": "kind", "class": "size",
    "damage class": "dc", "damage": "dc", "ap": "ap_use", "ap to use": "ap_use", "ap to ready": "ap_ready",
    "ready": "ap_ready", "soak class": "soak", "evade penalty": "eva_penalty", "speed penalty": "spd_penalty",
    "climb/swim penalty": "climb_swim_penalty", "climb swim penalty": "climb_swim_penalty",
    "evade bonus": "deflect_bonus", "deflect": "deflect_bonus", "vs ranged": "deflect_ranged",
    "vs melee": "deflect_melee", "cost": "price", "price (dukes)": "price_dukes", "notes": "description",
    "effect": "description", "starting gear": "is_starting_gear", "qty": "quantity", "amount": "quantity",
    "augs": "augments", "handed": "hands", "accuracy bonus": "acc_bonus", "acc bonus": "acc_bonus",
    "strike bonus": "stk_bonus", "stk bonus": "stk_bonus",
}
# Export = import format; price as exact dukes, plus the columns the creator knows beyond the template.
EXPORT_HEADER = [h for h in TEMPLATE_HEADER if h not in ("price", "quantity")] + [
    "price_dukes", "acc_bonus", "stk_bonus", "memento", "binding", "house_rule", "extension", "modifiers"]
MAX_ROWS = 2000
NAME_MAX = 120
KIND_ALIASES = {"weapon": "melee", "melee weapon": "melee", "gun": "firearm", "pistol": "firearm", "rifle": "firearm",
                "shield": "deflection", "equipment": "gear", "item": "general", "general item": "general", "loot": "general",
                "ammunition": "ammo"}
INT_FIELDS = ["dc", "ap_use", "ap_ready", "reach", "range", "increment", "soak", "eva_penalty", "spd_penalty",
              "climb_swim_penalty", "deflect_bonus", "acc_bonus", "stk_bonus", "price_dukes", "quantity", "binding"]
NOT_NULL_INTS = {"price_dukes", "quantity", "binding"}  # the others: empty cell = "use the size table"
BOOL_FIELDS = ["deflect_ranged", "deflect_melee", "concealable", "beta", "is_starting_gear", "memento", "house_rule"]
KINDS = {k for k, _ in KIND_CHOICES}
SIZES = {s for s, _ in SIZE_CHOICES}
MATERIALS = {m for m, _ in MATERIAL_CHOICES}
ROMAN = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "1": 1, "2": 2, "3": 3, "4": 4}
AUGMENT_LISTS_BY_KIND = {"melee": {"melee"}, "firearm": {"firearm", "turret"}, "crossbow": {"crossbow"},
                         "bow": {"bow"}, "armor": {"armor"}, "deflection": {"armor", "shield"}, "ammo": {"munition"},
                         "gear": {"explosive", "firebomb", "squib", "trinket"}, "resonator": {"resonator"},
                         # Gaseous Death / Living Potions allow gas, acid and medicine augments on a living liquid
                         "living-liquid": {"living-liquid", "gas", "acid", "medicine"}}


def template_csv():
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(TEMPLATE_HEADER)
    writer.writerows(TEMPLATE_ROWS)
    return buf.getvalue()


def export_csv(items):
    """Catalog items as CSV in the import format (round-trips through parse_rows)."""
    reg = get_registry()
    roman = {1: "I", 2: "II", 3: "III", 4: "IV"}

    def cell(item, f):
        v = getattr(item, f)
        if f == "variants":
            return "/".join(v or [])
        if f == "modifiers":
            return json.dumps(v) if v else ""
        if f == "augments":
            text = "; ".join(f"{reg.augments[s]['name_en'] if s in reg.augments else s} {roman.get(m, m)}"
                             for s, m in v or [])
            return text + ";" if "," in text else text  # a ";" makes parse_augments keep commas in names
        if isinstance(v, bool):
            return "yes" if v else "no"
        return "" if v is None else v

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(EXPORT_HEADER)
    writer.writerows([cell(item, f) for f in EXPORT_HEADER] for item in items)
    return buf.getvalue()


def read_table(text):
    """Return (header, rows) from pasted/uploaded text."""
    text = text.strip("﻿\n\r ")
    lines = [l for l in text.splitlines() if l.strip()]
    if not lines:
        return [], []
    if lines[0].lstrip().startswith("|"):
        rows = []
        for line in lines:
            if re.match(r"^\s*\|[\s\-:|]+\|\s*$", line):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            rows.append(cells)
        return rows[0], rows[1:]
    sample = "\n".join(lines[:5])
    delimiter = "\t" if "\t" in sample else max([",", ";"], key=sample.count)
    reader = csv.reader(io.StringIO(text), delimiter=delimiter)  # whole text: quoted cells may hold blank lines
    rows = [r for r in reader if r]
    return rows[0], rows[1:]


def normalize_header(h):
    h = h.strip().lower().replace("_", " ")
    h = ALIASES.get(h, h)
    return h.replace(" ", "_")


def parse_bool(v):
    return str(v).strip().lower() in {"1", "yes", "y", "true", "x", "ja", "✓"}


def parse_price(v):
    v = str(v).strip().lower().replace(",", "")
    if not v:
        return 0
    m = re.match(r"^(\d+(?:\.\d+)?)\s*(pr|princes?|p|d|dukes?|k|kings?)?$", v)
    if not m:
        raise ValueError(_("can't read price '{value}' (use e.g. '5 pr' or '3 d')", value=v))
    amount = float(m.group(1))
    unit = m.group(2) or "pr"
    if unit.startswith("p"):
        amount *= 10
    elif unit.startswith("k"):
        amount *= 100
    return int(round(amount))


def parse_augments(text, kind, errors, memento=False, house_rule=False):
    reg = get_registry()
    lists = None if house_rule else AUGMENT_LISTS_BY_KIND.get(kind)
    if lists and memento:
        lists = lists | {"memento"}
    out = []
    # with a ";" the cell is ;-separated, so names like "Win Some, Lose Some" survive
    for part in re.split(r"[;+]" if ";" in (text or "") else r"[;,+]", text or ""):
        part = part.strip()
        if not part:
            continue
        m = re.match(r"^(.*?)\s+(?:mq\s*)?(i{1,3}|iv|[1-4])$", part, re.I)
        name, marque = (m.group(1), ROMAN[m.group(2).lower()]) if m else (part, 1)
        matches = [a for a in reg.augments.values() if name.strip().lower() in (a["name"].lower(), a["name_en"].lower())
                   and (not lists or lists.intersection(a["lists"]))]
        if not matches:
            errors.append(_("unknown augment '{name}' for {kind}", name=name, kind=kind))
            continue
        out.append([matches[0]["slug"], marque])
    return out


MOD_CHOICES = {"op": ("add", {"add", "base", "transfer", "set"}),  # key: (default, allowed), see curated.mod
               "when": ("always", {"always", "stance", "toggle", "note"}),
               "scope": ("character", {"character", "weapon", "melee", "unarmed", "ranged"})}


def _valid_modifier(m):
    return (isinstance(m, dict) and isinstance(m.get("stat"), str)
            and all(m.get(k, default) in allowed for k, (default, allowed) in MOD_CHOICES.items())
            and isinstance(m.get("value", 0), int) and isinstance(m.get("formula", ""), str)
            and isinstance(m.get("by_marque", []), list) and all(isinstance(x, int) for x in m.get("by_marque", [])))


def parse_modifiers(text):
    """Modifiers cell (JSON list in the curated.mod schema) -> list; raises ValueError if malformed."""
    if not text:
        return []
    try:
        mods = json.loads(text)
    except ValueError:
        mods = None
    if not (isinstance(mods, list) and all(_valid_modifier(m) for m in mods)):
        raise ValueError(_("modifiers must be a JSON list like {example}", example='[{"stat": "climb", "value": 2}]'))
    return mods


def parse_rows(text):
    header, rows = read_table(text)
    fields = [normalize_header(h) for h in header]
    if "name" not in fields:
        return [{"line": 1, "values": {}, "errors": [_("header row needs a 'name' column")]}]
    if len(rows) > MAX_ROWS:
        return [{"line": 1, "values": {}, "errors": [_("too many rows ({n}); at most {max} per import",
                                                         n=len(rows), max=MAX_ROWS)]}]
    result = []
    for n, row in enumerate(rows, start=2):
        raw = dict(zip(fields, [c.strip() for c in row]))
        if not any(raw.values()):
            continue
        errors = []
        values = {"name": raw.get("name", "")}
        if "description" in raw:
            values["description"] = raw["description"]
        if not values["name"]:
            errors.append(_("name is empty"))
        elif len(values["name"]) > NAME_MAX:
            errors.append(_("name is longer than {max} characters", max=NAME_MAX))
        kind = raw.get("kind", "gear").lower() or "gear"
        kind = KIND_ALIASES.get(kind, kind)
        if kind not in KINDS:
            errors.append(_("unknown kind '{value}'", value=kind))
        values["kind"] = kind
        if "size" in raw:
            size = raw["size"].lower().replace(" ", "-").replace("superheavy", "super-heavy")
            if size not in SIZES:
                errors.append(_("unknown size '{value}'", value=size))
            values["size"] = size
        if "material" in raw:
            material = raw["material"].lower() or "metal"
            if material not in MATERIALS:
                errors.append(_("unknown material '{value}'", value=material))
            values["material"] = material
        if "variants" in raw:
            variants = [v.strip().lower() for v in re.split(r"[/,;+ ]+", raw["variants"]) if v.strip()]
            bad = [v for v in variants if v not in VARIANTS]
            if bad:
                errors.append(_("unknown variants {values}", values=", ".join(bad)))
            values["variants"] = [v for v in variants if v in VARIANTS]
        if "extension" in raw:
            if raw["extension"] and raw["extension"] not in EXTENSIONS:
                errors.append(_("unknown extension '{value}'", value=raw["extension"]))
            values["extension"] = raw["extension"]
        for f in INT_FIELDS:
            if raw.get(f, "") != "":
                try:
                    values[f] = int(raw[f].lstrip("+").replace("−", "-"))
                except ValueError:
                    errors.append(_("{field} must be a number", field=f))
            elif f in raw and f not in NOT_NULL_INTS:
                values[f] = None
        if "price" in raw and "price_dukes" not in values:
            try:
                values["price_dukes"] = parse_price(raw["price"])
            except ValueError as exc:
                errors.append(str(exc))
        for f in BOOL_FIELDS:
            if raw.get(f, "") != "":
                values[f] = parse_bool(raw[f])
        hands = raw.get("hands", "").strip().lower()
        if hands:
            parsed = {"0": 0, "none": 0, "worn": 0, "1": 1, "one": 1, "one-handed": 1, "2": 2, "two": 2,
                      "two-handed": 2}.get(hands)
            if parsed is not None:
                values["hands"] = parsed
            else:
                errors.append(_("hands must be 0, 1 or 2, not '{value}'", value=hands))
        elif "hands" in raw:
            values["hands"] = None
        if "modifiers" in raw:
            try:
                values["modifiers"] = parse_modifiers(raw["modifiers"])
            except ValueError as exc:
                errors.append(str(exc))
        if "augments" in raw:
            values["augments"] = parse_augments(raw["augments"], kind, errors, memento=values.get("memento", False),
                                                 house_rule=values.get("house_rule", False))
            # shortcut: an update row is checked with its own columns only, not merged with the existing item
            errors += item_requirements.problems(values)
        result.append({"line": n, "values": values, "errors": errors})
    return result
