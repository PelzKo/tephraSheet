"""Build the JSON rule data in rules/data/ from the reference markdown.

Parsed data is combined with the curated structured modifiers in
``rules/curated.py`` (which always win). Run after changing the source file
or the curated data; the generated JSON is committed.
"""

import json
import re
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from rules import curated
from rules.engine.tables import ALL_SKILLS, BOOK_STAT_KEYS
from rules.mdparse import jsonl_block, parse, strip_md

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
SOURCE = DATA_DIR / "source" / "Tephra_Reference_full.md"

STAT_WORDS = {
    "accuracy": "acc", "evade": "eva", "strike": "stk", "defense": "def", "priority": "pri",
    "speed": "spd",
}


class Command(BaseCommand):
    help = "Parse the Tephra reference markdown into rules/data/*.json"

    def handle(self, *args, **opts):
        self.warnings = []
        doc = parse(SOURCE)
        out = {
            "specialties": self.build_specialties(doc),
            "races": self.build_races(doc),
            "stories": self.build_stories(doc),
            "nationalities": self.build_nationalities(doc),
            "augments": self.build_augments(doc),
            "catalog": self.build_catalog(doc),
        }
        for name, data in out.items():
            path = DATA_DIR / f"{name}.json"
            path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf8")
            self.stdout.write(f"{path.name}: {len(data)} entries")
        for w in self.warnings:
            self.stdout.write(self.style.WARNING(w))

    # ------------------------------------------------------------------ specialties
    def build_specialties(self, doc):
        raw = jsonl_block(doc.lines)
        # Effect texts from the per-skill tables, in order, keyed by (skill, name).
        effects = {}
        for table in doc.tables:
            if table.header[:2] != ["Specialty", "Group"]:
                continue
            skill = table.section
            for row in table.rows:
                name = strip_md(row["Specialty"])
                effects.setdefault((skill, name), []).append(strip_md(row.get("Effect", "")))
        names = {d["n"] for d in raw}
        seen = {}
        result = []
        for d in raw:
            skill = d["s"]
            general = skill.startswith("General")
            key = (skill, d["n"])
            idx = seen.get(key, 0)
            seen[key] = idx + 1
            slug = slugify(f"{skill}-{d['n']}") + (f"-{idx + 1}" if idx else "")
            texts = effects.get(key, [])
            effect = texts[idx] if idx < len(texts) else ""
            if not effect:
                self.warnings.append(f"no effect text for specialty {key}")
            tags = d["t"]
            entry = {
                "slug": slug,
                "name": d["n"],
                "attribute": d["a"],
                "skill": None if general else skill,
                "general": general,
                "group": d["g"],
                "bonuses": {BOOK_STAT_KEYS[k]: v for k, v in d["b"].items()},
                "cost": d["c"],
                "requires_text": "" if d["r"] in ("", "—") else d["r"],
                "requires": self.parse_requirements(d["r"], names, d),
                "tags": tags,
                "stance": "[STANCE" in tags or d["c"].lower().startswith("stance"),
                "repeatable": "[REPEATABLE]" in tags,
                "crafts": re.findall(r"\[CRAFT:([^\]]+)\]", tags),
                "effect": effect,
                "modifiers": [],
            }
            cur = curated.SPECIALTIES.get(slug) or curated.SPECIALTIES.get(d["n"])
            if cur:
                entry.update(cur)
            entry["requires"] += [dict(c, soft=True) for c in curated.USAGE_CONDITIONS.get(d["n"], [])]
            if d["n"] in curated.USAGE_NOTES:
                entry["usage_note"] = curated.USAGE_NOTES[d["n"]]
            if d["n"] in curated.SPECIALTY_OPTIONS:
                entry["options"] = curated.SPECIALTY_OPTIONS[d["n"]]
            result.append(entry)
        missing = set(curated.USAGE_CONDITIONS) - names
        if missing:
            self.warnings.append(f"usage conditions for unknown specialties: {sorted(missing)}")
        return result

    def parse_requirements(self, text, names, d):
        text = (text or "").strip()
        if not text or text == "—":
            return []
        clauses = []
        for part in re.split(r";\s*", text):
            part = part.strip()
            if not part:
                continue
            clause = self.parse_requirement_clause(part, names)
            if clause is None:
                self.warnings.append(f"unparsed requirement '{part}' on {d['s']}/{d['n']}")
                clause = {"type": "note", "text": part}
            clauses.append(clause)
        return clauses

    def parse_requirement_clause(self, part, names):
        if part in names:
            return {"type": "specialty", "any": [part]}
        m = re.fullmatch(r"(\d+) ([A-Za-z\- ]+?)(?: \(.*\))?", part)
        if m and m.group(2) in ALL_SKILLS:
            return {"type": "skill", "skill": m.group(2), "min": int(m.group(1))}
        if m and m.group(2) in ("Brute", "Cunning", "Dexterity", "Spirit", "Sciences"):
            return {"type": "attribute", "attribute": m.group(2), "min": int(m.group(1))}
        m = re.fullmatch(r"Spirit attribute (\d+)", part)
        if m:
            return {"type": "attribute", "attribute": "Spirit", "min": int(m.group(1))}
        m = re.fullmatch(r"\+(\d+) (Accuracy|Strike|Evade|Defense|Priority|Speed)(?: from specialties)?", part)
        if m:
            return {"type": "stat", "stat": STAT_WORDS[m.group(2).lower()], "min": int(m.group(1))}
        alts = [a.strip() for a in re.split(r",\s*|\s+or\s+", part) if a.strip()]
        if alts and all(a in names for a in alts):
            return {"type": "specialty", "any": alts}
        m = re.fullmatch(r"(?:≥)?(\d+)\+? (?:(\w+) )?stances? known|(\d+)\+ (\w+) stances", part)
        if m:
            if m.group(3):
                return {"type": "stances", "min": int(m.group(3)), "skill": m.group(4)}
            return {"type": "stances", "min": int(m.group(1))}
        m = re.fullmatch(r"(\d+) AP per turn", part)
        if m:
            return {"type": "ap", "min": int(m.group(1))}
        m = re.fullmatch(r"any other (\w+) specialty", part)
        if m:
            return {"type": "skill_specialty", "skill": m.group(1)}
        if part == "any AP-sacrifice specialty":
            return {"type": "specialty", "any": curated.AP_SACRIFICE_SPECIALTIES}
        # Armor conditions are soft: checked and warned about, but they never block learning.
        m = re.search(r"(minimal|light|medium|heavy|super-heavy) or (heavier|lighter) armor", part)
        if m:
            bound = "min" if m.group(2) == "heavier" else "max"
            return {"type": "armor", bound: m.group(1), "soft": True, "text": part}
        if "armor" in part:
            return {"type": "note", "text": part, "soft": True}
        return None

    # ------------------------------------------------------------------ races
    def build_races(self, doc):
        races = []
        lines = doc.lines
        race_heads = [(i, l) for i, l in enumerate(lines) if re.match(r"^### 3\.[1-6] ", l)]
        for n, (start, head) in enumerate(race_heads):
            end = race_heads[n + 1][0] if n + 1 < len(race_heads) else next(
                i for i, l in enumerate(lines) if l.startswith("### 3.7"))
            name = re.match(r"^### 3\.\d (\w+)", head).group(1)
            block = lines[start:end]
            speed_line = next(l for l in block if l.startswith("**Speed:**"))
            land, swim, climb = [int(x) for x in re.findall(r"\d+", speed_line)[:3]]
            fixed, random_traits = [], []
            mode = None
            j = 0
            while j < len(block):
                line = block[j]
                if line.startswith("**Fixed:**"):
                    mode = "fixed"
                elif line.startswith("**Random"):
                    mode = "random"
                elif mode and line.startswith("|") and j + 1 < len(block) and "---" in block[j + 1]:
                    header = [c.strip() for c in line.strip("|").split("|")]
                    j += 2
                    while j < len(block) and block[j].startswith("|"):
                        cells = [c.strip() for c in block[j].strip("|").split("|")]
                        row = dict(zip(header, cells))
                        trait = {
                            "name": strip_md(row.get("Trait") or row.get("Option")),
                            "text": strip_md(row["Effect"]),
                            "tags": strip_md(row.get("Tags", "")),
                        }
                        if mode == "random":
                            trait["roll"] = int(row["d12"])
                            random_traits.append(trait)
                        else:
                            fixed.append(trait)
                        j += 1
                    continue
                elif mode == "fixed" and line.startswith("- **"):
                    m = re.match(r"- \*\*(.+?):\*\*\s*(.*)", line)
                    text = m.group(2)
                    tags = " ".join(re.findall(r"`([^`]*)`", text))
                    fixed.append({"name": m.group(1), "text": strip_md(re.sub(r"`[^`]*`", "", text)).strip(),
                                  "tags": tags})
                j += 1
            slug = slugify(name)
            race = {"slug": slug, "name": name, "speed": land, "swim": swim, "climb": climb,
                    "unarmed_dc": 2, "fixed_choose": None, "random_count": 1, "random_choose": 0,
                    "fixed": [], "random": []}
            race.update(curated.RACES.get(slug, {}))
            for kind, traits in (("fixed", fixed), ("random", random_traits)):
                for t in traits:
                    tslug = slugify(t["name"])
                    if tslug == "small-creature":
                        continue
                    t["slug"] = tslug
                    t["modifiers"] = []
                    t.update(curated.RACIAL_TRAITS.get(f"{slug}/{tslug}", {}))
                    race[kind].append(t)
            races.append(race)
        return races

    # ------------------------------------------------------------------ stories
    def build_stories(self, doc):
        stories = []

        def add(name, stype, text, group="", requires="", tags=""):
            slug = slugify(name)
            entry = {"slug": slug, "name": name, "type": stype, "group": group, "requires": requires,
                     "text": text, "tags": tags, "modifiers": []}
            entry.update(curated.STORIES.get(slug, {}))
            if any(s["slug"] == slug for s in stories):
                return
            stories.append(entry)

        for t in doc.tables_in("4.2"):
            for r in t.rows:
                add(strip_md(r["Story"]), "nationality", strip_md(r["Effect"]), group=r["Nationality"],
                    requires="" if r["Requires"] == "–" else r["Requires"], tags=strip_md(r["Tags"]))
        for t in doc.tables_in("4.3"):
            for r in t.rows:
                org = strip_md(r["Organization"])
                for part in split_top_level(r["Membership stories (effect)"], ";"):
                    m = re.match(r"\s*(.+?)\s*\((.*)\)\s*(`.*`)?\s*$", part)
                    if not m:
                        continue
                    add(strip_md(m.group(1)), "membership", strip_md(m.group(2)), group=org,
                        tags=strip_md(m.group(3) or ""))
        for t in doc.tables_in("4.4"):
            for r in t.rows:
                name = strip_md(r["Story"])
                requires = ""
                m = re.match(r"(.+?) \(req\. (.+)\)$", name)
                if m:
                    name, requires = m.group(1), m.group(2)
                name = re.sub(r"\s*\(listed under .*\)$", "", name)
                add(name, "background", strip_md(r["Effect"]), requires=requires, tags=strip_md(r["Tags"]))
        for t in doc.tables_in("4.5"):
            religion = strip_md(t.lead.split("–")[0]) if t.lead else ""
            for r in t.rows:
                stype = {"Faith Membership": "faith", "Personality": "personality",
                         "Background": "background"}.get(r.get("Type", "Faith Membership"), "faith")
                add(strip_md(r["Story"]), stype, strip_md(r["Effect"]), group=religion,
                    requires="" if r["Requires"] == "–" else r["Requires"], tags=strip_md(r["Tags"]))
        return stories

    def build_nationalities(self, doc):
        out = []
        for t in doc.tables_in("4.1"):
            for r in t.rows:
                name = strip_md(r["Nationality"]).split(" (")[0]
                out.append({"slug": slugify(name), "name": name, "summary": strip_md(r["Region / summary"]),
                            "relations": strip_md(r["Notable relations"]),
                            "story_group": curated.NATIONALITY_STORY_GROUP.get(name, "")})
        out.append({"slug": "other", "name": "Other", "summary": "Custom nationality (narrator approval).",
                    "relations": "", "story_group": ""})
        return out

    # ------------------------------------------------------------------ augments
    def build_augments(self, doc):
        out = []
        texts = {}
        for bt in doc.book_texts:
            texts.setdefault(bt.name.lower(), []).append(bt)
        for table in doc.tables:
            first = table.header[0]
            if first not in ("Augment", "Explosive augment", "Eyewear augment", "Trinket"):
                continue
            section = next((h for h in reversed(table.headings) if h), "")
            spec = next((v for k, v in curated.AUGMENT_SECTIONS if section.startswith(k)), None)
            if spec is None:
                self.warnings.append(f"augment table in unknown section {section}")
                continue
            skill, lists = spec
            sub = table.lead.strip("* :") if table.lead.startswith("**") else ""
            for r in table.rows:
                raw_name = strip_md(r[first])
                accessory = raw_name.startswith("*Accessory:*")
                raw_name = re.sub(r"^\*Accessory:\*\s*|^–\s*", "", raw_name).strip()
                m = re.match(r"(.+?)\s*\((.+)\)$", raw_name)
                name, qual = (m.group(1), m.group(2)) if m else (raw_name, "")
                entry_lists = list(lists)
                qual_parts = [q.strip() for q in qual.split(";")] if qual else []
                if lists == ["firearm", "crossbow"] or lists == ["auto", "clanker"]:
                    flags = {"F": "firearm", "C": "crossbow"} if lists[0] == "firearm" else {"A": "auto", "C": "clanker"}
                    marks = [flags[q] for q in qual_parts if q in flags]
                    if marks:
                        entry_lists = marks
                qual_parts = [q for q in qual_parts if q not in ("F", "C", "A")]
                marques = [strip_md(r.get(k, "")) for k in ("mQ I", "mQ II", "mQ III", "mQ IV")]
                slots = r.get("Slots", "")
                slug = slugify(f"{skill}-{'-'.join(entry_lists)}-{name}")
                if any(a["slug"] == slug for a in out):
                    slug += "-2"
                book = texts.get(name.lower(), [])
                text = book[0].text if book else ""
                notes = strip_md(r.get("Notes") or r.get("Tool tags") or r.get("Use") or r.get("Cost note") or "")
                if first == "Augment" and r.get("Effect"):
                    marques = [strip_md(r["Effect"]), "", "", ""]
                entry = {
                    "slug": slug, "name": name, "skill": skill, "lists": entry_lists,
                    "section": section.split(" (")[0], "subsection": sub,
                    "slots": int(slots) if slots.isdigit() else (0 if slots in ("0", "–") else None),
                    "qualifiers": qual_parts, "accessory": accessory, "marques": marques, "notes": notes,
                    "size": r.get("Size", ""), "price": r.get("Price I/II/III/IV (pr)", ""),
                    "text": text, "modifiers": [],
                }
                entry.update(curated.AUGMENTS.get(slug, {}))
                out.append(entry)
        return out

    # ------------------------------------------------------------------ catalog seed
    def build_catalog(self, doc):
        items = list(curated.CATALOG_WEAPONS_AND_ARMOR)
        for t in doc.tables_in("5.10"):
            for cells in t.raw_rows:
                for k in range(0, len(cells) - 1, 2):
                    name, price = strip_md(cells[k]), strip_md(cells[k + 1])
                    if not name:
                        continue
                    items.append({"name": name, "kind": "gear", "price_dukes": parse_price(price),
                                  "price_text": price, "is_starting_gear": True,
                                  "description": "Adventuring basics (p.84)."})
        for t in doc.tables_in("5.12"):
            for r in t.rows:
                name = strip_md(r["Item"])
                item = {"name": name, "kind": "gear", "price_dukes": parse_price(r["Price"]),
                        "price_text": strip_md(r["Price"]), "description": strip_md(r["Effect"]),
                        "is_starting_gear": False}
                item.update(curated.CATALOG_BRAND_OVERRIDES.get(name, {}))
                items.append(item)
        for t in doc.tables_in("5.9"):
            if "Cost" not in t.header:
                continue
            for r in t.rows:
                items.append({"name": r["Animal"], "kind": "animal", "price_dukes": parse_price(r["Cost"]),
                              "price_text": r["Cost"], "is_starting_gear": False,
                              "description": "; ".join(f"{k}: {strip_md(v)}" for k, v in r.items() if k not in ("Animal", "Cost"))})
        return items


def split_top_level(text, sep):
    parts, depth, cur = [], 0, ""
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == sep and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur)
    return parts


def parse_price(text):
    """'2 dukes' -> 2, '5 princes' / '5 pr' -> 50, '3,200 pr' -> 32000."""
    text = strip_md(text or "").replace(",", "")
    m = re.search(r"(\d+(?:\.\d+)?)\+?\s*(dukes?|d\b|princes?|pr\b|kings?)", text)
    if not m:
        return 0
    value = float(m.group(1))
    unit = m.group(2)
    if unit.startswith("pr"):
        value *= 10
    elif unit.startswith("k"):
        value *= 100
    return int(value)

