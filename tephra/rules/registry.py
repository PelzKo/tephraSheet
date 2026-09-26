"""In-memory access to the committed rule data (rules/data/*.json).

Reference data is read-only book content, so it lives in JSON rather than the
database; characters reference entries by slug.
"""

import json
from functools import cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"


def _load(name):
    with open(DATA_DIR / f"{name}.json", encoding="utf8") as fh:
        return json.load(fh)


class Registry:
    def __init__(self):
        self.specialties = {s["slug"]: s for s in _load("specialties")}
        self.races = {r["slug"]: r for r in _load("races")}
        self.stories = {s["slug"]: s for s in _load("stories")}
        self.nationalities = {n["slug"]: n for n in _load("nationalities")}
        self.augments = {a["slug"]: a for a in _load("augments")}
        self.traits = {}
        for race in self.races.values():
            for kind in ("fixed", "random"):
                for t in race[kind]:
                    t = dict(t, kind=kind, race=race["slug"], key=f"{race['slug']}/{t['slug']}")
                    self.traits[t["key"]] = t
        self.specialties_by_name = {}
        for s in self.specialties.values():
            self.specialties_by_name.setdefault(s["name"], s)

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
def get_registry():
    return Registry()
