"""Leveling rules (p.27)."""

import random as _random

from rules.registry import get_registry

from . import tables
from .requirements import check_specialty


def can_level_up(level, xp):
    return level < tables.MAX_LEVEL and xp >= tables.XP_PER_LEVEL


def validate_levelup_skills(delta):
    """+2 points in one skill, +1 point in two *other* skills."""
    points = sorted((p for p in delta.values() if p), reverse=True)
    errors = []
    if points != [2, 1, 1]:
        errors.append("Place +2 points in one skill and +1 point in two other skills.")
    if any(s not in tables.ALL_SKILLS for s in delta):
        errors.append("Unknown skill.")
    return errors


def retrofit_allowed(new_level):
    return new_level in tables.RETROFIT_LEVELS


def validate_retrofit(old_slug, new_slug):
    """Swap one specialty for another within the same attribute."""
    reg = get_registry()
    old, new = reg.specialties.get(old_slug), reg.specialties.get(new_slug)
    if not old or not new:
        return ["Unknown specialty."]
    if old["attribute"] != new["attribute"]:
        return [f"Retrofitting must stay within the same attribute ({old['attribute']})."]
    return []


def random_levelup_skills(state, rng=None):
    rng = rng or _random.Random()
    owned = [s for s, p in state.skills.items() if p]
    pool = list(tables.ALL_SKILLS)
    # Mostly grow existing skills.
    first = rng.choice(owned) if owned and rng.random() < 0.8 else rng.choice(pool)
    rest = [s for s in (owned if len(owned) > 2 else pool) if s != first]
    others = rng.sample(rest, 2)
    return {first: 2, others[0]: 1, others[1]: 1}


def random_levelup_specialty(state, compute, rng=None):
    rng = rng or _random.Random()
    sheet = compute(state)
    options = [s for s in get_registry().specialties.values() if check_specialty(s, state, sheet)[0]]
    if not options:
        return None
    weights = [1 + (sheet.skills[s["skill"]].total if s["skill"] else 0) for s in options]
    return rng.choices(options, weights=weights, k=1)[0]["slug"]
