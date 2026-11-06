"""Character creation rules (p.24-26): validation and legal random choices per step."""

import random as _random

from rules.extensions import offer, offer_races
from rules.lang import gettext as _
from rules.registry import get_registry

from . import tables
from .requirements import augments_used, check_augment, check_specialty, story_allowed

STEPS = [
    (1, "Race & Nationality"),
    (2, "Skills"),
    (3, "Attributes"),
    (4, "Specialties"),
    (5, "Augments"),
    (6, "Weapons & Armor"),
    (7, "Gear"),
    (8, "Derived Statistics"),
    (9, "Background Stories"),
    (10, "Finishings"),
]

FIRST_NAMES = ["Ada", "Barnaby", "Cornelius", "Delphine", "Ezekiel", "Florence", "Gideon", "Hester",
               "Ignatius", "Jemima", "Lucinda", "Mortimer", "Octavia", "Percival", "Quincy", "Rosalind",
               "Silas", "Theodora", "Ulysses", "Violet", "Wendell", "Xanthe", "Zebulon", "Imogen"]
LAST_NAMES = ["Ashcombe", "Brassworth", "Cogsley", "Dunmore", "Emberly", "Fairweather", "Gearhart",
              "Hollowell", "Ironside", "Kettleby", "Lockhart", "Marlowe", "Nettlefield", "Pembrooke",
              "Quillfeather", "Ravensworth", "Steamwright", "Thistlewood", "Valvebridge", "Whitlock"]
PERSONALITIES = ["curious and reckless", "stoic and dutiful", "charming but vain", "grim and pragmatic",
                 "idealistic dreamer", "sardonic tinkerer", "loyal to a fault", "greedy but good-hearted",
                 "quiet observer", "boisterous show-off"]


def rng_or_default(rng):
    return rng or _random.Random()


# --------------------------------------------------------------------------- step 1
def trait_slots(race_slug):
    """How many fixed traits must be chosen and how random traits are obtained."""
    race = get_registry().races[race_slug]
    return {
        "fixed_choose": race.get("fixed_choose"),
        "random_count": race.get("random_count", 1),
        "random_choose": race.get("random_choose", 0),
    }


def resolve_random_trait(race_slug, roll_value, rng=None):
    """Map a d12 roll to a trait key, following redirects (Farishtaa Prominent Host → elf table)."""
    reg = get_registry()
    trait = reg.random_table(race_slug)[roll_value]
    if trait.get("reroll_on") and not trait["reroll_on"].startswith("@"):  # "@choice" (Pure Strain) is optional
        other = trait["reroll_on"]
        roll2 = rng_or_default(rng).randint(1, 12)
        return [f"{race_slug}/{trait['slug']}", f"{other}/{reg.random_table(other)[roll2]['slug']}"], roll2
    return [f"{race_slug}/{trait['slug']}"], None


def roll_random_traits(race_slug, chosen=(), rng=None):
    """Fill the race's random-trait slots. ``chosen`` are trait keys picked by the player."""
    rng = rng_or_default(rng)
    slots = trait_slots(race_slug)
    keys = list(chosen)
    rolls = []
    while len([k for k in keys if k.startswith(race_slug + "/")]) < slots["random_count"]:
        value = rng.randint(1, 12)
        new, _l = resolve_random_trait(race_slug, value, rng)
        if new[0] in keys or new[0] in get_registry().races[race_slug].get("reroll", []):
            continue  # re-roll duplicates (gnomes) and the race's re-roll results (True-Meld)
        rolls.append(value)
        keys.extend(new)
    return keys, rolls


def random_fixed_choice(race_slug, rng=None):
    rng = rng_or_default(rng)
    race = get_registry().races[race_slug]
    n = race.get("fixed_choose")
    if not n:
        return []
    pool = [t for t in race["fixed"] if not t.get("always")]
    return [f"{race_slug}/{t['slug']}" for t in rng.sample(pool, min(n, len(pool)))]


ALCHEMY_LISTS = ["acid", "gas", "medicine", "poison"]


def choice_options(kind, trait=None):
    """[(value, English label)] for a trait choice: "attribute", "skill" (any), "skill:<Attribute>", "race" (core
    races), "alchemy_list", "option" (the trait's "choice_options"). ``choice_options``/``choice_exclude`` on the
    trait narrow any kind."""
    trait = trait or {}
    if trait.get("choice_options"):
        return [(o, o) for o in trait["choice_options"]]
    if kind == "attribute":
        return [(a, a) for a in tables.ATTRIBUTES if a not in trait.get("choice_exclude", [])]
    if kind == "skill":
        return [(s, s) for s in tables.ALL_SKILLS if s not in trait.get("choice_exclude", [])]
    if kind.startswith("skill:"):
        return [(s, s) for s in tables.SKILLS.get(kind[6:], [])]
    if kind == "race":
        return [(r["slug"], r["name"]) for r in get_registry().races.values() if not r.get("extension")]
    if kind == "alchemy_list":
        return [(x, x) for x in ALCHEMY_LISTS]
    return []


def random_trait_choices(trait_keys, rng=None):
    rng = rng_or_default(rng)
    reg = get_registry()
    out = {}
    for k in trait_keys:
        options = choice_options(reg.traits[k].get("choice") or "", reg.traits[k]) if k in reg.traits else []
        if options:
            out[k] = rng.choice(options)[0]
    return out


def nationality_stories(nationality_slug, race_slug=None):
    reg = get_registry()
    nat = reg.nationalities.get(nationality_slug)
    if not nat or not nat["story_group"]:
        return []
    return [s for s in offer(reg.stories.values())
            if s["type"] == "nationality" and s["group"] == nat["story_group"] and story_allowed(s, race_slug)]


def random_race_and_nationality(rng=None):
    rng = rng_or_default(rng)
    reg = get_registry()
    race = rng.choice([r["slug"] for r in offer_races(reg.races.values())
                       if r.get("group") != "Variant"])  # variants need the narrator's approval
    nats = [n["slug"] for n in offer(reg.nationalities.values()) if n["slug"] != "other"]
    nat = rng.choice(nats)
    fixed = random_fixed_choice(race, rng)
    random_keys, rolls = roll_random_traits(race, rng=rng)
    stories = nationality_stories(nat, race)
    story = [rng.choice(stories)["slug"]] if stories else []
    return {"race": race, "nationality": nat, "fixed_traits": fixed, "random_traits": random_keys,
            "rolls": rolls, "trait_choices": random_trait_choices(fixed + random_keys, rng),
            "stories": story}


# --------------------------------------------------------------------------- step 2
def validate_creation_skills(alloc):
    points = sorted((p for p in alloc.values() if p), reverse=True)
    errors = []
    if any(p < 0 for p in alloc.values()):
        errors.append(_("Skill points can't be negative."))
    if points != sorted(tables.CREATION_SKILL_POINTS, reverse=True):
        errors.append(_("Place 3 points in one skill, 2 points in two skills and 1 point in three skills (six different skills)."))
    unknown = [s for s in alloc if s not in tables.ALL_SKILLS]
    if unknown:
        errors.append(_("Unknown skills: {skills}", skills=", ".join(unknown)))
    return errors


def random_skills(rng=None, prefer=None):
    rng = rng_or_default(rng)
    skills = list(tables.ALL_SKILLS)
    rng.shuffle(skills)
    if prefer:
        skills = [s for s in prefer if s in skills] + [s for s in skills if s not in prefer]
    return {s: p for s, p in zip(skills, tables.CREATION_SKILL_POINTS)}


# --------------------------------------------------------------------------- step 4 / 5
def random_specialties(state, compute, count, rng=None):
    """Pick ``count`` legal specialties one at a time (earlier picks may unlock later ones)."""
    rng = rng_or_default(rng)
    reg = get_registry()
    picked = []
    level = state.level
    for _i in range(count):
        sheet = compute(state)
        options = [s for s in offer(reg.specialties.values())
                   if not s.get("racial") and check_specialty(s, state, sheet)[0]]
        if not options:
            break
        # Prefer the character's own skills; weight by skill points so primaries show up more.
        weights = [1 + (sheet.skills[s["skill"]].total if s["skill"] else 0) for s in options]
        choice = rng.choices(options, weights=weights, k=1)[0]
        state.specialties.append((choice["slug"], level))
        picked.append(choice["slug"])
    return picked


def random_augments(state, compute, rng=None, limit=None):
    rng = rng_or_default(rng)
    reg = get_registry()
    picked = []
    sheet = compute(state)
    free = (sheet.stats["aug"].total - augments_used(state)) if limit is None else limit
    for _i in range(max(0, free)):
        options = [a for a in offer(reg.augments.values()) if check_augment(a, state, sheet)[0]]
        if not options:
            break
        choice = rng.choice(options)
        state.augments.append(choice["slug"])
        picked.append(choice["slug"])
    return picked


# --------------------------------------------------------------------------- step 9 / 10
def background_stories():
    return [s for s in offer(get_registry().stories.values()) if s["type"] in ("background", "personality")]


def random_background(rng=None, count=1):
    rng = rng_or_default(rng)
    options = [s for s in background_stories() if not s.get("requires")]
    return [s["slug"] for s in rng.sample(options, count)]


def random_finishings(race_slug, rng=None):
    rng = rng_or_default(rng)
    ages = {"human": (18, 60), "ayodin": (18, 80), "elf": (25, 200), "farishtaa": (20, 90),
            "gnome": (20, 150), "satyr": (16, 50)}
    heights = {"human": (155, 195), "ayodin": (150, 190), "elf": (190, 230), "farishtaa": (160, 200),
               "gnome": (80, 110), "satyr": (150, 190)}
    lo, hi = ages.get(race_slug, (18, 60))
    hlo, hhi = heights.get(race_slug, (150, 195))
    height = rng.randint(hlo, hhi)
    return {
        "name": f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}",
        "age": str(rng.randint(lo, hi)),
        "height": f"{height} cm",
        "weight": f"{int(height * rng.uniform(0.33, 0.5))} kg",
        "personality": _(rng.choice(PERSONALITIES)),
    }
