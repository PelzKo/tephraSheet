"""Static rule tables (Tephra Playing Guide ch. 1, 2, 5)."""

ATTRIBUTES = ["Brute", "Cunning", "Dexterity", "Spirit", "Sciences"]

SKILLS = {
    "Brute": ["Brawl", "Frenzy", "Overpower", "Resilience"],
    "Cunning": ["Espionage", "Expertise", "Showmanship", "Tactical"],
    "Dexterity": ["Ace", "Agility", "Marksmanship", "Swashbuckling"],
    "Spirit": ["Faith", "Grace", "Luck", "Shamanism"],
    "Sciences": ["Alchemy", "Armsmith", "Automata", "Bio-Flux", "Engineer", "Gadgetry"],
}
ALL_SKILLS = [s for skills in SKILLS.values() for s in skills]
SKILL_ATTRIBUTE = {s: a for a, skills in SKILLS.items() for s in skills}
SCIENCE_SKILLS = SKILLS["Sciences"]

# The ten combat-stat columns of the specialty table (sheet p.2), in sheet order.
COMBAT_STATS = ["acc", "eva", "stk", "def", "pri", "spd", "aug", "diy", "wnd", "hp"]
COMBAT_STAT_LABELS = {
    "acc": "Accuracy", "eva": "Evade", "stk": "Strike", "def": "Defense", "pri": "Priority",
    "spd": "Speed", "aug": "Augments", "diy": "DIY", "wnd": "Wounds", "hp": "Hit Points",
}
# Book abbreviations used in the reference JSON -> internal keys.
BOOK_STAT_KEYS = {"Acc": "acc", "Eva": "eva", "Stk": "stk", "Def": "def", "Pri": "pri",
                  "Spd": "spd", "Aug": "aug", "DIY": "diy", "Wnd": "wnd", "HP": "hp"}

# Creation (p.24): 3 points in 1 skill, 2 in two, 1 in three, all different skills.
CREATION_SKILL_POINTS = [3, 2, 2, 1, 1, 1]
CREATION_SPECIALTIES = 3
CREATION_PRINCES = 10
BASE_WOUNDS = 12
XP_PER_LEVEL = 12
MAX_LEVEL = 12
# Level-up (p.27): +2 in one skill, +1 in two other skills.
LEVELUP_SKILL_POINTS = [2, 1, 1]
RETROFIT_LEVELS = (4, 8, 12)

STARTING_PRINCES = {1: 10, 2: 18, 3: 32, 4: 58, 5: 105, 6: 190, 7: 340, 8: 615,
                    9: 1100, 10: 2000, 11: 3570, 12: 6425}


def action_points(level):
    if level >= 12:
        return 6
    if level >= 8:
        return 5
    if level >= 4:
        return 4
    return 3


def tier(result):
    if result >= 30:
        return 4
    if result >= 20:
        return 3
    if result >= 10:
        return 2
    return 1


# Marque by skill points in the Science skill (p.162).
def marque_for_points(points):
    if points >= 25:
        return 4
    if points >= 15:
        return 3
    if points >= 5:
        return 2
    return 1


SIZES = ["unarmed", "light", "medium", "heavy", "super-heavy"]
SIZE_LABELS = {"unarmed": "Unarmed", "minimal": "Minimal", "light": "Light", "medium": "Medium",
               "heavy": "Heavy", "super-heavy": "Super-Heavy", "none": "Unarmored"}

# Weapons (p.74-79). range/increment in feet.
MELEE = {
    "unarmed": {"ap": 1, "dc": 2, "hands": 0},
    "light": {"ap": 2, "dc": 4, "hands": 1},
    "medium": {"ap": 2, "dc": 6, "hands": 1},
    "heavy": {"ap": 2, "dc": 8, "hands": 2},
    "super-heavy": {"ap": 2, "dc": 10, "hands": 2, "footing": True},
}
THROW_RANGE = {"light": 25, "medium": 75, "heavy": 50, "super-heavy": 25}
FIREARMS = {
    "light": {"ap": 2, "dc": 2, "hands": 1, "ready": 0, "range": 50, "increment": 10},
    "medium": {"ap": 2, "dc": 4, "hands": 1, "ready": 1, "range": 100, "increment": 25},
    "heavy": {"ap": 2, "dc": 6, "hands": 2, "ready": 1, "range": 200, "increment": 50},
    "super-heavy": {"ap": 2, "dc": 8, "hands": 2, "ready": 2, "range": 300, "increment": 100, "footing": True},
}
BOWS = {
    "light": {"ap": 2, "dc": 3, "hands": 2, "ready": 0, "range": 25, "increment": 10},
    "medium": {"ap": 2, "dc": 5, "hands": 2, "ready": 0, "range": 50, "increment": 10},
    "heavy": {"ap": 3, "dc": 7, "hands": 2, "ready": 0, "range": 75, "increment": 25},
    "super-heavy": {"ap": 3, "dc": 9, "hands": 2, "ready": 0, "range": 200, "increment": 75, "footing": True},
}
CROSSBOWS = {
    "light": {"ap": 2, "dc": 3, "hands": 1, "ready": 1, "range": 25, "increment": 10},
    "medium": {"ap": 2, "dc": 5, "hands": 1, "ready": 1, "range": 50, "increment": 10},
    "heavy": {"ap": 2, "dc": 7, "hands": 2, "ready": 2, "range": 100, "increment": 25},
    "super-heavy": {"ap": 2, "dc": 9, "hands": 2, "ready": 3, "range": 150, "increment": 50, "footing": True},
}
WEAPON_TABLES = {"melee": MELEE, "firearm": FIREARMS, "bow": BOWS, "crossbow": CROSSBOWS}
# Firearms and crossbows use the Accuracy roll for damage (p.76, 79).
ACCURACY_DAMAGE_KINDS = {"firearm", "crossbow"}
RANGED_KINDS = {"firearm", "bow", "crossbow"}

WEAPON_PRICES_DUKES = {  # p.85
    ("melee", "light"): 10, ("melee", "medium"): 70, ("melee", "heavy"): 150,
    ("firearm", "light"): 20, ("firearm", "medium"): 50, ("firearm", "heavy"): 120, ("firearm", "super-heavy"): 200,
    ("bow", "light"): 5, ("bow", "medium"): 10, ("bow", "heavy"): 50, ("bow", "super-heavy"): 170,
    ("crossbow", "light"): 20, ("crossbow", "medium"): 40, ("crossbow", "heavy"): 70, ("crossbow", "super-heavy"): 140,
}

ROTATING_BARRELS = "armsmith-firearm-rotating-barrels"
CRANK_FREE = "armsmith-firearm-crank-free"


def _augment_slugs(item):
    return {a[0] for a in item.augments}


def base_hands(item):
    """Hands from the item or its size table; deflection items: cloak 0, shield/parrying dagger 1.
    Rotating Barrels add a hand (unless Crank-Free)."""
    if item.hands is not None:
        hands = item.hands
    elif item.kind == "deflection":
        default = next((v for v in DEFLECTION.values() if v["label"].lower() in item.name.lower()), None)
        hands = default["hands"] if default else 1
    else:
        table = WEAPON_TABLES.get(item.kind)
        hands = table.get(item.size, {}).get("hands", 1) if table else 1
    augs = _augment_slugs(item)
    if item.kind == "firearm" and ROTATING_BARRELS in augs and CRANK_FREE not in augs:
        hands = min(2, hands + 1)
    return hands


def needs_firing_position(item):
    """A two-handed firearm with Rotating Barrels can only be fired from a firing position."""
    augs = _augment_slugs(item)
    if item.kind != "firearm" or ROTATING_BARRELS not in augs or CRANK_FREE in augs:
        return False
    plain = item.hands if item.hands is not None else FIREARMS.get(item.size, {}).get("hands", 1)
    return plain >= 2


def item_hands(item, one_handing=False):
    """Hands an item needs (0 = worn, e.g. a cloak). One-Handing It lets two-handed weapons be
    wielded in one hand, except bows."""
    hands = base_hands(item)
    if one_handing and hands == 2 and item.kind != "bow":
        return 1
    return hands


# Melee variants (p.75): each −1 DC.
VARIANTS = {
    "flexible": {"label": "Flexible", "dc": -1, "note": "can make grabs"},
    "polearm": {"label": "Polearm", "dc": -1, "reach": 5, "note": "+5 ft reach"},
    "throwing": {"label": "Throwing", "dc": -1, "note": "can be thrown"},
    "impromptu": {"label": "Impromptu", "dc": 0, "acc": -3, "stk": -3, "note": "not designed as a weapon"},
    "double-barreled": {"label": "Double-barreled", "dc": 0, "note": "fire twice before readying"},
}
SUPER_HEAVY_NO_FOOTING = -3

# Armor (p.80). penalties are positive numbers that get subtracted.
ARMOR_ORDER = ["none", "minimal", "light", "medium", "heavy", "super-heavy"]
ARMOR = {
    "none": {"soak": 0, "eva": 0, "spd": 0, "climb_swim": 0, "price": 0, "don": "–"},
    "minimal": {"soak": 1, "eva": 0, "spd": 0, "climb_swim": 0, "price": 10, "don": "3 AP"},
    "light": {"soak": 2, "eva": 1, "spd": 5, "climb_swim": 5, "price": 50, "don": "6 AP"},
    "medium": {"soak": 3, "eva": 2, "spd": 5, "climb_swim": 10, "price": 150, "don": "24 AP (12 with help)"},
    "heavy": {"soak": 4, "eva": 3, "spd": 10, "climb_swim": 15, "price": 400, "don": "3 min (1 min with help)"},
    "super-heavy": {"soak": 5, "eva": 4, "spd": 10, "climb_swim": 20, "price": 750, "don": "10 min (3 min with help)"},
}

DEFLECTION = {
    "parrying-dagger": {"label": "Parrying Dagger", "bonus": 3, "ranged": False, "melee": True, "price": 10, "hands": 1},
    "cloak": {"label": "Cloak", "bonus": 3, "ranged": False, "melee": True, "price": 10, "hands": 0},
    "shield": {"label": "Shield", "bonus": 4, "ranged": True, "melee": True, "price": 40, "hands": 1},
}

# Augment slots by material (p.162/177); beta +2.
MATERIAL_SLOTS = {"metal": 3, "wood": 2, "organic": 1, "textile": 1}

DUKES_PER_PRINCE = 10
DUKES_PER_KING = 100


def format_money(dukes):
    dukes = int(dukes or 0)
    princes, rest = divmod(abs(dukes), DUKES_PER_PRINCE)
    sign = "-" if dukes < 0 else ""
    if rest and princes:
        return f"{sign}{princes} pr {rest} d"
    if rest:
        return f"{sign}{rest} d"
    return f"{sign}{princes} pr"
