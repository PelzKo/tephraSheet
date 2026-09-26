"""d12 helpers (p.8)."""

import random as _random


def d12(rng=None):
    return (rng or _random).randint(1, 12)


def roll(bonus=0, rng=None):
    """Rule #2: natural 12s roll again and add. Rule #1: a natural 1 adds no bonuses."""
    rng = rng or _random
    first = rng.randint(1, 12)
    dice = [first]
    while dice[-1] == 12:
        dice.append(rng.randint(1, 12))
    if first == 1:
        return {"dice": dice, "total": 1, "bonus": 0}
    return {"dice": dice, "total": sum(dice) + bonus, "bonus": bonus}
