"""Bulk import of items from CSV files or pasted tables (CSV, TSV, ;-separated, markdown)."""

import csv
import io
import re

from rules.engine.tables import VARIANTS
from rules.registry import get_registry

from .models import KIND_CHOICES, MATERIAL_CHOICES, SIZE_CHOICES

TEMPLATE_HEADER = ["name", "kind", "size", "variants", "material", "dc", "ap_use", "ap_ready", "reach", "range",
                   "increment", "soak", "eva_penalty", "spd_penalty", "climb_swim_penalty", "deflect_bonus",
                   "deflect_ranged", "deflect_melee", "concealable", "beta", "augments", "price",
                   "is_starting_gear", "quantity", "description"]
TEMPLATE_ROWS = [
    ["Cavalry Sabre", "melee", "medium", "", "metal", "", "", "", "", "", "", "", "", "", "", "", "", "", "no", "no",
     "Accurate I", "7 pr", "no", "1", "A curved officer's blade."],
    ["Boarding Pike", "melee", "heavy", "polearm", "wood", "", "", "", "", "", "", "", "", "", "", "", "", "", "no",
     "no", "", "12 pr", "no", "1", ""],
    ["Pepperbox Pistol", "firearm", "light", "", "metal", "", "", "", "", "", "", "", "", "", "", "", "", "", "yes",
     "no", "", "2 pr", "no", "1", ""],
    ["Brass Cuirass", "armor", "medium", "", "metal", "", "", "", "", "", "", "", "", "", "", "", "", "", "no", "no",
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
    "augs": "augments",
}
KIND_ALIASES = {"weapon": "melee", "melee weapon": "melee", "gun": "firearm", "pistol": "firearm", "rifle": "firearm",
                "shield": "deflection", "equipment": "gear", "item": "gear", "ammunition": "ammo"}
INT_FIELDS = ["dc", "ap_use", "ap_ready", "reach", "range", "increment", "soak", "eva_penalty", "spd_penalty",
              "climb_swim_penalty", "deflect_bonus", "price_dukes", "quantity"]
BOOL_FIELDS = ["deflect_ranged", "deflect_melee", "concealable", "beta", "is_starting_gear"]
KINDS = {k for k, _ in KIND_CHOICES}
SIZES = {s for s, _ in SIZE_CHOICES}
MATERIALS = {m for m, _ in MATERIAL_CHOICES}
ROMAN = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "1": 1, "2": 2, "3": 3, "4": 4}
AUGMENT_LISTS_BY_KIND = {"melee": {"melee"}, "firearm": {"firearm"}, "crossbow": {"crossbow"}, "bow": {"bow"},
                         "armor": {"armor"}, "deflection": {"armor"}}


def template_csv():
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(TEMPLATE_HEADER)
    writer.writerows(TEMPLATE_ROWS)
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
    reader = csv.reader(io.StringIO("\n".join(lines)), delimiter=delimiter)
    rows = [r for r in reader]
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
        raise ValueError(f"can't read price '{v}' (use e.g. '5 pr' or '3 d')")
    amount = float(m.group(1))
    unit = m.group(2) or "pr"
    if unit.startswith("p"):
        amount *= 10
    elif unit.startswith("k"):
        amount *= 100
    return int(round(amount))


def parse_augments(text, kind, errors):
    reg = get_registry()
    lists = AUGMENT_LISTS_BY_KIND.get(kind)
    out = []
    for part in re.split(r"[;,+]", text or ""):
        part = part.strip()
        if not part:
            continue
        m = re.match(r"^(.*?)\s+(?:mq\s*)?(i{1,3}|iv|[1-4])$", part, re.I)
        name, marque = (m.group(1), ROMAN[m.group(2).lower()]) if m else (part, 1)
        matches = [a for a in reg.augments.values() if a["name"].lower() == name.strip().lower()
                   and (not lists or lists.intersection(a["lists"]))]
        if not matches:
            errors.append(f"unknown augment '{name}' for {kind}")
            continue
        out.append([matches[0]["slug"], marque])
    return out


def parse_rows(text):
    header, rows = read_table(text)
    fields = [normalize_header(h) for h in header]
    if "name" not in fields:
        return [{"line": 1, "values": {}, "errors": ["header row needs a 'name' column"]}]
    result = []
    for n, row in enumerate(rows, start=2):
        raw = dict(zip(fields, [c.strip() for c in row]))
        if not any(raw.values()):
            continue
        errors = []
        values = {"name": raw.get("name", ""), "description": raw.get("description", "")}
        if not values["name"]:
            errors.append("name is empty")
        kind = raw.get("kind", "gear").lower() or "gear"
        kind = KIND_ALIASES.get(kind, kind)
        if kind not in KINDS:
            errors.append(f"unknown kind '{kind}'")
        values["kind"] = kind
        size = raw.get("size", "").lower().replace(" ", "-").replace("superheavy", "super-heavy")
        if size not in SIZES:
            errors.append(f"unknown size '{size}'")
        values["size"] = size
        material = raw.get("material", "").lower() or "metal"
        if material not in MATERIALS:
            errors.append(f"unknown material '{material}'")
        values["material"] = material
        variants = [v.strip().lower() for v in re.split(r"[/,;+ ]+", raw.get("variants", "")) if v.strip()]
        bad = [v for v in variants if v not in VARIANTS]
        if bad:
            errors.append(f"unknown variants {', '.join(bad)}")
        values["variants"] = [v for v in variants if v in VARIANTS]
        for f in INT_FIELDS:
            if raw.get(f, "") != "":
                try:
                    values[f] = int(raw[f].lstrip("+").replace("−", "-"))
                except ValueError:
                    errors.append(f"{f} must be a number")
        if "price" in raw and "price_dukes" not in values:
            try:
                values["price_dukes"] = parse_price(raw["price"])
            except ValueError as exc:
                errors.append(str(exc))
        for f in BOOL_FIELDS:
            if raw.get(f, "") != "":
                values[f] = parse_bool(raw[f])
        if raw.get("augments"):
            values["augments"] = parse_augments(raw["augments"], kind, errors)
        result.append({"line": n, "values": values, "errors": errors})
    return result
