"""In-memory access to the committed rule data (rules/data/*.json).

Reference data is read-only book content, so it lives in JSON rather than the
database; characters reference entries by slug.

There is one Registry per language: display texts (names, effects, notes …) are replaced by the
translations in ``data/i18n/<lang>/<kind>*.json`` ({slug: {field: text}}). Every entry keeps its
English name in ``name_en``; rules logic that matches by name must use ``name_en``.
"""

import json
from functools import cache
from pathlib import Path

from .lang import DEFAULT, get_language

DATA_DIR = Path(__file__).resolve().parent / "data"
I18N_DIR = DATA_DIR / "i18n"
# Fields that may be translated; everything else (slugs, skills, modifiers, story groups) stays.
TRANSLATED = {
    "specialties": ("name", "group", "cost", "requires_text", "effect", "usage_note"),
    "augments": ("name", "section", "subsection", "notes", "text", "marques", "qualifiers"),
    "stories": ("name", "text"),
    "nationalities": ("name", "summary", "relations"),
}


def _load(name):
    with open(DATA_DIR / f"{name}.json", encoding="utf8") as fh:
        return json.load(fh)


@cache
def translations(lang, kind):
    merged = {}
    for path in sorted((I18N_DIR / lang).glob(f"{kind}*.json")):
        merged.update(json.loads(path.read_text(encoding="utf8")))
    return merged


def _localize(entries, lang, kind):
    for e in entries:
        e["name_en"] = e.get("name", "")
        if kind == "stories":
            e["requires_label"] = e.get("requires", "")  # display only; "requires" stays English for matching
            e["group_label"] = e.get("group", "")
    if lang == DEFAULT:
        return entries
    tr = translations(lang, kind)
    for e in entries:
        t = tr.get(e.get("slug"), {})
        for f in TRANSLATED.get(kind, ()):
            if t.get(f) and (not isinstance(e.get(f), list) or len(t[f]) == len(e[f])):
                e[f] = t[f]
        if kind == "stories":
            e["requires_label"] = t.get("requires") or e["requires_label"]
            e["group_label"] = t.get("group") or e["group_label"]
        if t.get("options") and e.get("options"):
            e["options"] = {"label": t["options"].get("label", e["options"]["label"]),
                            "options": {k: t["options"].get("options", {}).get(k, v)
                                        for k, v in e["options"]["options"].items()}}
    return entries


def _localize_races(races, lang):
    tr = translations(lang, "races") if lang != DEFAULT else {}
    for r in races:
        r["name_en"] = r["name"]
        rt = tr.get(r["slug"], {})
        r["name"] = rt.get("name") or r["name"]
        for kind in ("fixed", "random"):
            for t in r[kind]:
                t["name_en"] = t["name"]
                tt = rt.get("traits", {}).get(t["slug"], {})
                t["name"] = tt.get("name") or t["name"]
                t["text"] = tt.get("text") or t["text"]
    return races


class Registry:
    def __init__(self, lang=DEFAULT):
        self.lang = lang
        self.specialties = {s["slug"]: s for s in _localize(_load("specialties"), lang, "specialties")}
        self.races = {r["slug"]: r for r in _localize_races(_load("races"), lang)}
        self.stories = {s["slug"]: s for s in _localize(_load("stories"), lang, "stories")}
        self.nationalities = {n["slug"]: n for n in _localize(_load("nationalities"), lang, "nationalities")}
        self.augments = {a["slug"]: a for a in _localize(_load("augments"), lang, "augments")}
        self.traits = {}
        for race in self.races.values():
            for kind in ("fixed", "random"):
                for t in race[kind]:
                    t = dict(t, kind=kind, race=race["slug"], key=f"{race['slug']}/{t['slug']}")
                    self.traits[t["key"]] = t
        self.specialties_by_name = {}
        for s in self.specialties.values():
            self.specialties_by_name.setdefault(s["name_en"], s)

    def specialty(self, slug):
        return self.specialties[slug]

    def trait(self, key):
        return self.traits[key]

    def random_table(self, race_slug):
        return {t["roll"]: t for t in self.races[race_slug]["random"]}

    def specialties_for_skill(self, skill):
        return [s for s in self.specialties.values() if s["skill"] == skill]

    def augments_for_lists(self, lists):
        lists = set(lists)
        return [a for a in self.augments.values() if lists.intersection(a["lists"])]


@cache
def _registry(lang):
    return Registry(lang)


def get_registry(lang=None):
    """The rule data in ``lang`` (default: the current language)."""
    return _registry(lang or get_language())
