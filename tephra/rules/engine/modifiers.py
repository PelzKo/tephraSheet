"""Value-with-breakdown and modifier sources."""

from dataclasses import dataclass, field

from .formula import FormulaError, evaluate


@dataclass
class Value:
    """A computed number plus the parts it is made of (for the breakdown tooltip)."""

    parts: list = field(default_factory=list)  # [(label, amount)]
    base: tuple | None = None  # (label, amount); replaced by op=base modifiers
    floor: int | None = None
    override: tuple | None = None  # (label, amount) forces the total (e.g. Raging → 0)
    halved: str = ""

    def add(self, label, amount):
        if amount:
            self.parts.append((label, int(amount)))

    def set_base(self, label, amount):
        if self.base is None or amount >= self.base[1] or self.base[0].startswith("Base"):
            self.base = (label, int(amount))

    @property
    def raw_total(self):
        total = (self.base[1] if self.base else 0) + sum(a for _, a in self.parts)
        if self.floor is not None:
            total = max(self.floor, total)
        return total

    @property
    def total(self):
        if self.override is not None:
            return self.override[1]
        total = self.raw_total
        if self.halved:
            total //= 2
        return total

    @property
    def breakdown(self):
        rows = []
        if self.base is not None:
            rows.append(self.base)
        rows.extend(self.parts)
        if self.floor is not None and self.raw_total == self.floor and \
                (self.base[1] if self.base else 0) + sum(a for _, a in self.parts) < self.floor:
            rows.append((f"minimum {self.floor}", None))
        if self.halved:
            rows.append((f"{self.halved}: halved (round down)", None))
        if self.override is not None:
            rows.append(self.override)
        return rows

    @property
    def is_composite(self):
        return len(self.breakdown) > 1

    def __int__(self):
        return self.total

    def __str__(self):
        return str(self.total)


@dataclass
class Source:
    key: str  # unique, also the toggle key
    label: str  # shown in breakdowns, e.g. "Specialty: Fisticuffs"
    modifiers: list
    kind: str = ""  # trait specialty story custom item augment
    stance_slug: str = ""  # specialty slug when this source is a stance
    item_id: object = None


def mod_amount(mod, variables, marque=None):
    if "by_marque" in mod:
        values = mod["by_marque"]
        return values[max(1, min(4, marque or 1)) - 1]
    if "formula" in mod:
        try:
            return evaluate(mod["formula"], variables)
        except FormulaError:
            return 0
    return mod.get("value", 0)


def is_active(mod, source, state):
    when = mod.get("when", "always")
    if when == "always":
        return True
    if when == "stance":
        return bool(source.stance_slug) and state.stance == source.stance_slug
    if when == "toggle":
        return source.key in state.toggles
    return False
