"""Operations that change characters according to the rules (used by the views)."""

import random

from django.db import transaction

from catalog.models import ItemTemplate
from rules.engine import creation, leveling, tables
from rules.engine.requirements import check_augment, check_specialty
from rules.engine.stats import compute
from rules.registry import get_registry

from .models import Character, InventoryItem, LevelLog, NarratorSettings

NATIONALITY_TYPES = {"nationality"}
RELIGIONS = ["", "Tailemy", "Free Will", "Jinzium (Eternal Church)", "Jinzium (Revivalist)",
             "Infernal Jinzium", "Harabe Mavi", "Path of Gilkoroh", "None / agnostic"]


def state_compute(state):
    return compute(state)


# --------------------------------------------------------------------------- step 1
def set_race(character, race_slug):
    if race_slug == character.race:
        return
    character.race = race_slug
    character.fixed_traits = []
    character.random_traits = []
    character.trait_rolls = []
    character.trait_choices = {}
    reg = get_registry()
    race = reg.races[race_slug]
    if not race.get("fixed_choose"):
        character.fixed_traits = [f"{race_slug}/{t['slug']}" for t in race["fixed"]]
    # Drop nationality stories restricted to another race.
    character.stories = [s for s in character.stories if reg.stories.get(s, {}).get("type") not in NATIONALITY_TYPES]


def roll_random_traits(character, rng=None, keep_chosen=True):
    race = character.race
    slots = creation.trait_slots(race)
    chosen = []
    if keep_chosen and slots["random_choose"]:
        chosen = [k for k in character.random_traits[: slots["random_choose"]]]
    keys, rolls = creation.roll_random_traits(race, chosen=chosen, rng=rng)
    character.random_traits = keys
    character.trait_rolls = list(character.trait_rolls) + rolls
    choices = dict(character.trait_choices)
    choices.update({k: v for k, v in creation.random_trait_choices(keys, rng).items() if k not in choices})
    character.trait_choices = choices


def set_nationality_story(character, slug):
    reg = get_registry()
    stories = [s for s in character.stories if reg.stories.get(s, {}).get("type") not in NATIONALITY_TYPES]
    if slug:
        stories.insert(0, slug)
    character.stories = stories


def random_step1(character, rng):
    r = creation.random_race_and_nationality(rng)
    set_race(character, r["race"])
    character.nationality = r["nationality"]
    character.fixed_traits = r["fixed_traits"] or character.fixed_traits
    character.random_traits = r["random_traits"]
    character.trait_rolls = r["rolls"]
    character.trait_choices = r["trait_choices"]
    set_nationality_story(character, r["stories"][0] if r["stories"] else "")
    character.religion = rng.choice(RELIGIONS[1:])


# --------------------------------------------------------------------------- revalidation
def revalidate(character):
    """Drop specialties/augments that are no longer legal after earlier choices changed."""
    state = character.to_state()
    kept = []
    for slug, level in character.specialties:
        spec = get_registry().specialties.get(slug)
        if not spec:
            continue
        state.specialties = [(s, l) for s, l in kept]
        ok, _ = check_specialty(spec, state, compute(state))
        if ok:
            kept.append((slug, level))
    character.specialties = [list(k) for k in kept]
    state.specialties = kept
    sheet = compute(state)
    capacity = sheet.stats["aug"].total
    augs = []
    for slug in character.augments:
        aug = get_registry().augments.get(slug)
        state.augments = augs
        if aug and check_augment(aug, state, sheet)[0] and len(augs) < capacity:
            augs.append(slug)
    character.augments = augs


# --------------------------------------------------------------------------- steps 4/5
def set_specialty_option(character, slug, value):
    """Store the choice a specialty needs (e.g. Battle Theme: singing or instrument)."""
    spec = get_registry().specialties.get(slug)
    if not spec or value not in spec.get("options", {}).get("options", {}):
        return False
    character.specialty_choices = dict(character.specialty_choices, **{slug: value})
    return True


def fill_random_options(character, rng):
    """Pick random choices for learned specialties that still need one (random characters)."""
    reg = get_registry()
    for slug, _ in character.specialties:
        spec = reg.specialties.get(slug, {})
        if spec.get("options") and slug not in character.specialty_choices:
            set_specialty_option(character, slug, rng.choice(sorted(spec["options"]["options"])))


def missing_options(character):
    """Learned specialties whose choice hasn't been made yet: [spec, ...]."""
    reg = get_registry()
    return [reg.specialties[s] for s, _ in character.specialties
            if reg.specialties.get(s, {}).get("options") and s not in character.specialty_choices]


def add_specialties_sequentially(character, slugs, level=1, options=None):
    """Add specialties one by one, rejecting illegal ones. Returns list of error strings.
    ``options`` ({slug: value}) supplies the choice for specialties that need one."""
    errors = []
    reg = get_registry()
    for slug in slugs:
        spec = reg.specialties.get(slug)
        if not spec:
            errors.append(f"Unknown specialty {slug}.")
            continue
        if options is not None and spec.get("options") and \
                (options.get(slug) or "") not in spec["options"]["options"]:
            errors.append(f"{spec['name']}: {spec['options']['label']}")
            continue
        state = character.to_state()
        ok, reasons = check_specialty(spec, state, compute(state))
        if not ok:
            errors.append(f"{spec['name']}: {'; '.join(reasons)}")
            continue
        character.specialties = list(character.specialties) + [[slug, level]]
        if options:
            set_specialty_option(character, slug, options.get(slug))
    return errors


def random_specialties(character, count, level, rng):
    state = character.to_state()
    state.level = level
    before = len(state.specialties)
    creation.random_specialties(state, compute, count, rng)
    character.specialties = [list(s) for s in character.specialties] + \
        [[s, level] for s, _ in state.specialties[before:]]


def set_augments(character, slugs):
    errors = []
    reg = get_registry()
    state = character.to_state()
    state.augments = []
    sheet = compute(state)
    capacity = sheet.stats["aug"].total
    kept = []
    for slug in slugs:
        aug = reg.augments.get(slug)
        if not aug:
            continue
        state.augments = kept
        ok, reasons = check_augment(aug, state, sheet)
        if not ok:
            errors.append(f"{aug['name']}: {'; '.join(reasons)}")
            continue
        if len(kept) >= capacity:
            errors.append(f"Only {capacity} augments can be learned.")
            break
        kept.append(slug)
    character.augments = kept
    return errors


def random_augments(character, rng):
    state = character.to_state()
    creation.random_augments(state, compute, rng)
    character.augments = state.augments


# --------------------------------------------------------------------------- equipment
HAND_SLOTS = ("weapon1", "weapon2")  # left hand, right hand
WINGS_TRAIT = "ayodin/wings-as-arms"


class EquipError(ValueError):
    pass


def one_handing(character):
    """One-Handing It: two-handed weapons (except bows) fit in one hand."""
    reg = get_registry()
    return any(reg.specialties.get(s, {}).get("name") == "One-Handing It" for s, _ in character.specialties)


def has_wings(character):
    return WINGS_TRAIT in character.random_traits or WINGS_TRAIT in character.fixed_traits


def item_hands(character, item):
    return tables.item_hands(item.to_item_state(), one_handing(character))


def equip(character, item, slot):
    """Put ``item`` into ``slot`` and move displaced items to "carried".

    - A two-handed item always goes into the left hand and empties the right one.
    - A shield or parrying dagger (deflection item that needs a hand) blocks the right hand.
    - The wings slot (Wings as Arms) only takes one-handed items.
    Returns {"moved": [names put away], "notice": pop-up text or ""}; raises EquipError."""
    moved = []
    others = InventoryItem.objects.filter(character=character)
    if item.pk:
        others = others.exclude(pk=item.pk)

    def carry(items):
        for o in items:
            o.slot = "carried"
            o.save(update_fields=["slot"])
            moved.append(o.name)

    hands = item_hands(character, item)
    shield = [o for o in others.filter(slot="deflection") if item_hands(character, o) >= 1]
    if slot == "wings":
        if not has_wings(character):
            raise EquipError("Only characters with Wings as Arms can hold items in their wings.")
        if hands != 1 or item.kind == "deflection":
            raise EquipError(f"The wings can only hold one-handed items, and {item.name} is not one.")
        carry(others.filter(slot="wings"))
    elif slot in HAND_SLOTS:
        if item.kind == "deflection":
            slot = "deflection"
        elif hands == 2:
            slot = "weapon1"
            carry(list(others.filter(slot__in=HAND_SLOTS)) + shield)
        else:
            carry(others.filter(slot=slot))
            other = "weapon2" if slot == "weapon1" else "weapon1"
            carry([o for o in others.filter(slot=other) if item_hands(character, o) == 2])
            if slot == "weapon2":
                carry(shield)
    if slot == "deflection":
        carry(others.filter(slot="deflection"))
        if hands >= 1:  # the shield takes the right hand
            carry(list(others.filter(slot="weapon2")) +
                  [o for o in others.filter(slot="weapon1") if item_hands(character, o) == 2])
    elif slot == "armor":
        carry(others.filter(slot="armor"))
    item.slot = slot
    item.save()
    notice = ""
    if slot in HAND_SLOTS + ("wings",) and tables.needs_firing_position(item.to_item_state()):
        notice = f"{item.name} has rotating barrels: you need to be in a firing position to fire it."
    return {"moved": moved, "notice": notice}


def normalize_hands(character):
    """Fix hand slots that break the hand rules (e.g. data from before items had hands).
    The left hand wins over the shield, the shield over the right hand. Returns names put away."""
    items = {i.slot: i for i in character.items.filter(slot__in=["weapon1", "weapon2", "wings", "deflection"])}
    left, right, wings, defl = (items.get(k) for k in ("weapon1", "weapon2", "wings", "deflection"))
    moved = []

    def carry(item):
        item.slot = "carried"
        item.save(update_fields=["slot"])
        moved.append(item.name)

    if right and not left and item_hands(character, right) == 2:
        right.slot, left, right = "weapon1", right, None
        left.save(update_fields=["slot"])
    if left and item_hands(character, left) == 2:
        if right:
            carry(right)
        if defl and item_hands(character, defl) >= 1:
            carry(defl)
    elif right and (item_hands(character, right) == 2 or defl and item_hands(character, defl) >= 1):
        carry(right)
    if wings and (not has_wings(character) or item_hands(character, wings) != 1):
        carry(wings)
    return moved


# --------------------------------------------------------------------------- steps 6/7
def equip_template(character, template, slot):
    item = InventoryItem.from_template(character, template, slot="carried")
    equip(character, item, slot)
    return item


def random_weapons_and_armor(character, rng):
    sheet = character.compute()
    skills = {s: v.total for s, v in sheet.skills.items()}
    weapons = list(ItemTemplate.objects.filter(kind__in=["melee", "firearm", "bow", "crossbow"]))
    # Pick weapons that match the character's strongest combat skills.
    prefs = {"Marksmanship": ["firearm", "bow", "crossbow"], "Swashbuckling": ["melee"], "Overpower": ["melee"],
             "Espionage": ["melee"], "Frenzy": ["melee"], "Brawl": ["melee"], "Ace": ["firearm"]}
    ranked = sorted(prefs, key=lambda s: -skills.get(s, 0))
    kinds = prefs[ranked[0]] if skills.get(ranked[0]) else ["melee", "firearm"]
    first = rng.choice([w for w in weapons if w.kind in kinds] or weapons)
    second = rng.choice([w for w in weapons if w.kind != first.kind] or weapons)
    InventoryItem.objects.filter(character=character, slot__in=["weapon1", "weapon2", "armor", "deflection"]).delete()
    equip_template(character, first, "weapon1")
    left = equip_template(character, second, "carried")
    if item_hands(character, left) == 1 and item_hands(character, character.items.get(slot="weapon1")) == 1:
        equip(character, left, "weapon2")
    armors = list(ItemTemplate.objects.filter(kind="armor", size__in=["minimal", "light", "medium"]))
    if armors:
        equip_template(character, rng.choice(armors), "armor")
    if rng.random() < 0.4 and first.kind == "melee":
        defl = list(ItemTemplate.objects.filter(kind="deflection"))
        if defl:
            equip_template(character, rng.choice(defl), "deflection")


def starting_money(level):
    return tables.STARTING_PRINCES.get(level, 10) * tables.DUKES_PER_PRINCE


def random_gear(character, rng):
    InventoryItem.objects.filter(character=character, slot="carried", template__is_starting_gear=True).delete()
    gear = list(ItemTemplate.objects.filter(is_starting_gear=True))
    must = [g for g in gear if g.name in ("Backpack", "Bedroll", "Rations (1 day)", "Clothing (working)")]
    extra = rng.sample([g for g in gear if g not in must], min(4, len(gear) - len(must)))
    for g in must + extra:
        InventoryItem.from_template(character, g, quantity=3 if g.name.startswith("Rations") else 1).save()
    character.money_on_hand = starting_money(1)


# --------------------------------------------------------------------------- step 9/10
def set_background_stories(character, slugs):
    reg = get_registry()
    keep = [s for s in character.stories if reg.stories.get(s, {}).get("type") in NATIONALITY_TYPES]
    character.stories = keep + [s for s in slugs if s in reg.stories and s not in keep]


def random_step9(character, rng):
    count = NarratorSettings.get().background_story_count
    set_background_stories(character, creation.random_background(rng, count))


def random_finishings(character, rng):
    data = creation.random_finishings(character.race, rng)
    character.name = character.name or data["name"]
    character.age = character.age or data["age"]
    character.height = character.height or data["height"]
    character.weight = character.weight or data["weight"]
    character.personality = character.personality or data["personality"]


# --------------------------------------------------------------------------- random per step / all
def random_step(character, step, rng=None):
    rng = rng or random.Random()
    if step == 1:
        random_step1(character, rng)
        character.save()
    elif step == 2:
        character.skills = creation.random_skills(rng)
        revalidate(character)
        character.save()
    elif step == 4:
        character.specialties = []
        character.specialty_choices = {}
        random_specialties(character, tables.CREATION_SPECIALTIES, 1, rng)
        revalidate(character)
        fill_random_options(character, rng)
        character.save()
    elif step == 5:
        character.augments = []
        random_augments(character, rng)
        character.save()
    elif step == 6:
        random_weapons_and_armor(character, rng)
    elif step == 7:
        random_gear(character, rng)
        character.save()
    elif step == 9:
        random_step9(character, rng)
        character.save()
    elif step == 10:
        random_finishings(character, rng)
        character.save()


@transaction.atomic
def random_all(character, rng=None):
    rng = rng or random.Random()
    for step in (1, 2, 4, 5, 6, 7, 9, 10):
        random_step(character, step, rng)
    character.wizard_step = 10
    character.save()


# --------------------------------------------------------------------------- finishing & leveling
def reset_health(character):
    sheet = character.compute()
    character.current_hp = sheet.max_hp
    character.current_wounds = sheet.max_wounds


@transaction.atomic
def finish_creation(character):
    character.status = "active"
    character.wizard_step = 10
    reset_health(character)
    character.save()
    LevelLog.objects.create(character=character, level=1, data={
        "skills": character.skills, "specialties": character.specialties, "augments": character.augments})


@transaction.atomic
def apply_levelup(character, skill_delta, specialty, retrofit=None, augments=(), from_xp=True, options=None):
    """Apply one level-up. ``retrofit`` = (old_slug, new_slug) at levels 4/8/12."""
    errors = leveling.validate_levelup_skills(skill_delta)
    if errors:
        return errors
    new_level = character.level + 1
    skills = dict(character.skills)
    for s, p in skill_delta.items():
        skills[s] = skills.get(s, 0) + p
    character.skills = skills
    character.level = new_level
    if retrofit and retrofit[0] and retrofit[1]:
        if not leveling.retrofit_allowed(new_level):
            return ["Retrofitting specialties is only possible at levels 4, 8 and 12."]
        errs = leveling.validate_retrofit(*retrofit)
        if errs:
            return errs
        old = [list(s) for s in character.specialties]
        idx = next((i for i, (s, _) in enumerate(old) if s == retrofit[0]), None)
        if idx is None:
            return ["The specialty to replace is not learned."]
        replaced_level = old[idx][1]
        del old[idx]
        character.specialties = old
        errs = add_specialties_sequentially(character, [retrofit[1]], level=replaced_level, options=options)
        if errs:
            return errs
    errs = add_specialties_sequentially(character, [specialty], level=new_level, options=options)
    if errs:
        return errs
    if augments:
        errs = set_augments(character, list(character.augments) + [a for a in augments if a not in character.augments])
        if errs:
            return errs
    if from_xp:
        character.xp = max(0, character.xp - tables.XP_PER_LEVEL)
    reset_health(character)
    character.save()
    LevelLog.objects.create(character=character, level=new_level, data={
        "skills": skill_delta, "specialty": specialty, "retrofit": list(retrofit or []), "augments": list(augments)})
    return []


def random_levelup(character, rng=None, from_xp=True):
    rng = rng or random.Random()
    for _ in range(20):
        state = character.to_state()
        delta = leveling.random_levelup_skills(state, rng)
        for s, p in delta.items():
            state.skills[s] = state.skills.get(s, 0) + p
        state.level += 1
        slug = leveling.random_levelup_specialty(state, compute, rng)
        if not slug:
            continue
        state.specialties.append((slug, state.level))
        creation.random_augments(state, compute, rng)
        new_augs = [a for a in state.augments if a not in character.augments]
        errors = apply_levelup(character, delta, slug, augments=new_augs, from_xp=from_xp)
        if not errors:
            fill_random_options(character, rng)
            character.save(update_fields=["specialty_choices"])
            return []
        character.refresh_from_db()
    return ["Could not find a legal random level-up."]


def needs_catch_up(character):
    return character.status == "active" and character.level < character.target_level
