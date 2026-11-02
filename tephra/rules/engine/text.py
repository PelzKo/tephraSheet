"""Helpers for rule texts."""

import re

_TIER_LINE = re.compile(r"\d")


def split_tiers(effect):
    """Split a specialty effect into (body, [T1, T2, T3, T4]) when it ends with the four tier
    results (one short line each, with a number). The book sometimes glues T1 to the end of the
    paragraph ("… armor offers little protection. Ignores 1 soak class"): then T1 is the part after
    the last sentence. Returns (effect, None) when there is no tier list."""
    lines = (effect or "").split("\n")

    def short(line):
        return len(line) <= 100 and _TIER_LINE.search(line)

    if len(lines) >= 5 and all(short(x) for x in lines[-4:]):
        return "\n".join(lines[:-4]), lines[-4:]
    if len(lines) >= 4 and all(short(x) for x in lines[-3:]):
        head, sep, t1 = lines[-4].rpartition(". ")
        if sep and short(t1):
            return "\n".join(lines[:-4] + [head + "."]), [t1] + lines[-3:]
    return effect, None
