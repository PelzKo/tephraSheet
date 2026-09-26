import random

import pytest

from rules.engine import creation, leveling, tables
from rules.engine.formula import FormulaError, evaluate
from rules.engine.requirements import check_specialty
from rules.engine.state import CharacterState, ItemState
from rules.engine.stats import compute
from rules.registry import get_registry

REG = get_registry()


def spec(name):
    return REG.specialties_by_name[name]["slug"]


def human(**kw):
    base = dict(race="human", fixed_traits=["human/relentless", "human/peerless"], random_traits=["human/adaptable"],
                skills={"Brawl": 3, "Resilience": 2, "Frenzy": 2, "Agility": 1, "Tactical": 1, "Luck": 1})
    base.update(kw)
    return CharacterState(**base)


def test_data_counts():
    assert len(REG.specialties) == 462
    assert len(REG.races) == 6
    per_skill = {}
    for s in REG.specialties.values():
        per_skill[s["skill"]] = per_skill.get(s["skill"], 0) + 1
    assert per_skill["Brawl"] == 21 and per_skill["Showmanship"] == 23 and per_skill[None] == 2


def test_formula():
    assert evaluate("1 + brawl // 6", {"brawl": 12}) == 3
    assert evaluate("min(2, x)", {"x": 5}) == 2
    with pytest.raises(FormulaError):
        evaluate("__import__('os')", {})


def test_relentless_hp_and_specialty_columns():
    st = human(specialties=[(spec("Block with a Grab"), 1), (spec("Dirty Fighting"), 1), (spec("Fluid"), 1)])
    sheet = compute(st)
    # 10 + 9 + 7 specialty HP + Relentless 3 + 1 per specialty
    assert sheet.max_hp == 26 + 3 + 3
    assert sheet.stats["acc"].total == 2  # 1 + 1 + 0
    assert sheet.stats["eva"].total == 1 + 2
    assert sheet.max_wounds == 12
    assert sheet.stats["ap"].total == 3
    assert sheet.attributes["Brute"].total == 7
    assert sheet.specialty_totals["hp"] == 26


def test_elf_unarmed_dc_and_melee_bonus():
    st = CharacterState(race="elf", random_traits=["elf/danger-sense"])
    sheet = compute(st)
    assert sheet.unarmed.dc.total == 3
    assert sheet.stats["hp"].total == 4
    assert sheet.stats["pri"].total == 3
    assert sheet.stats["spd"].total == 30


def test_gnome_light_armor_speed():
    st = CharacterState(race="gnome", random_traits=["gnome/wiry", "gnome/bend-sight"],
                        items=[ItemState(name="Leather", kind="armor", size="light", slot="armor", id=1)])
    sheet = compute(st)
    assert sheet.stats["spd"].total == 10
    assert sheet.stats["eva"].total == 1 + 1 - 1
    assert sheet.stats["soak"].total == 2
    assert sheet.unarmed.dc.total == 1


def test_firearm_uses_accuracy_and_augments():
    gun = ItemState(name="Rifle", kind="firearm", size="heavy", slot="weapon1", id=7,
                    augments=[("armsmith-firearm-crossbow-accurate", 2), ("armsmith-firearm-crossbow-damaging", 1)])
    st = CharacterState(race="farishtaa", items=[gun])
    sheet = compute(st)
    block = sheet.weapons[0]
    assert block.stk is None
    assert block.acc.total == 1 + 2  # Piercing Scrutiny + Accurate mQ II
    assert block.dc.total == 6 + 1
    assert block.damage == [7, 14, 21, 28]
    assert block.ap_ready.total == 1


def test_super_heavy_needs_footing():
    hammer = ItemState(name="Hammer", kind="melee", size="super-heavy", slot="weapon1", id=1)
    st = CharacterState(race="satyr", items=[hammer])
    assert compute(st).weapons[0].acc.total == -3
    st.stance = "footing"
    assert compute(st).weapons[0].acc.total == 0


def test_stance_and_toggle():
    slug = spec("Fisticuffs")
    st = human(specialties=[(slug, 1)])
    assert compute(st).unarmed.dc.total == 2
    st.stance = slug
    assert compute(st).unarmed.dc.total == 2 + 1  # Brawl 3 → +1 + 0
    st = human(random_traits=["human/momentum"])
    assert compute(st).stats["pri"].total == 0
    st.toggles = {"trait:human/momentum"}
    assert compute(st).stats["pri"].total == 5


def test_quick_feet_base_speed_and_farishtaa_ace():
    st = human(random_traits=["human/quick-feet"])
    assert compute(st).stats["spd"].total == 35
    st = CharacterState(race="farishtaa", skills={"Ace": 1})
    assert compute(st).skills["Ace"].total == 3


def test_ap_by_level_and_fatigue():
    st = human(level=4)
    assert compute(st).stats["ap"].total == 4
    st = human(specialties=[(spec("Fluid"), 1)], effects=["status:fatigued"])
    assert compute(st).max_hp == (7 + 3 + 1) // 2


def test_requirements():
    st = human(specialties=[])
    sheet = compute(st)
    crushing = REG.specialties[spec("Crushing Grip")]
    ok, reasons = check_specialty(crushing, st, sheet)
    assert not ok and "Strike" in reasons[0]
    st.specialties = [(spec("Dirty Fighting"), 1), (spec("Fisticuffs"), 1)]
    ok, _ = check_specialty(crushing, st, compute(st))
    assert ok
    marks = REG.specialties_by_name["Monkey Wrestler"]
    assert not check_specialty(marks, st, compute(st))[0]  # needs 5 Brawl
    no_skill = REG.specialties_by_name["Gunsmith"]
    assert "needs at least 1 point in Armsmith" in check_specialty(no_skill, st, compute(st))[1]


def test_creation_skill_validation():
    assert creation.validate_creation_skills({"Brawl": 3, "Ace": 2, "Luck": 2, "Faith": 1, "Grace": 1, "Tactical": 1}) == []
    assert creation.validate_creation_skills({"Brawl": 4, "Ace": 2, "Luck": 2, "Faith": 1, "Grace": 1}) != []
    assert creation.validate_creation_skills(creation.random_skills(random.Random(3))) == []


def test_levelup_validation():
    assert leveling.validate_levelup_skills({"Brawl": 2, "Ace": 1, "Luck": 1}) == []
    assert leveling.validate_levelup_skills({"Brawl": 3, "Ace": 1}) != []
    assert leveling.validate_retrofit(spec("Fluid"), spec("Adrenaline Surge")) == []
    assert leveling.validate_retrofit(spec("Fluid"), spec("Gunsmith")) != []


@pytest.mark.parametrize("seed", range(25))
def test_random_character_is_legal(seed):
    rng = random.Random(seed)
    r = creation.random_race_and_nationality(rng)
    st = CharacterState(race=r["race"], fixed_traits=r["fixed_traits"], random_traits=r["random_traits"],
                        trait_choices=r["trait_choices"], stories=r["stories"], skills=creation.random_skills(rng))
    picked = creation.random_specialties(st, compute, tables.CREATION_SPECIALTIES, rng)
    assert len(picked) == 3
    creation.random_augments(st, compute, rng)
    sheet = compute(st)
    assert len(st.augments) <= sheet.stats["aug"].total
    assert sheet.max_wounds == 12
    if r["race"] == "gnome":
        assert len([k for k in st.random_traits if k.startswith("gnome/")]) == 2


def test_effects_apply_modifiers():
    st = human(effects=["status:prone", "wound:eyes"])
    sheet = compute(st)
    assert sheet.stats["spd"].total == 5  # prone forces 5 ft
    assert ("Effect: Blinded", -4) in sheet.stats["acc"].breakdown
    assert sheet.stats["def"].total == compute(human()).stats["def"].total - 1


def test_racial_roll_bonus_in_attribute_misc():
    st = CharacterState(race="elf", random_traits=[], skills={"Brawl": 1})
    sheet = compute(st)
    assert sheet.attr_misc["Brute"].breakdown == [("Racial trait: Big Boned", 2)]
    assert sheet.attributes["Brute"].total == 3
    assert sheet.attributes["Spirit"].total == -3
    st.misc = {"attr:Brute": 1}
    sheet = compute(st)
    assert ("Manual Misc Change", 1) in sheet.attr_misc["Brute"].breakdown
    assert sheet.attributes["Brute"].total == 4


def test_soft_requirements_warn_but_allow():
    from rules.engine.requirements import character_warnings, specialty_warnings

    mountain = REG.specialties_by_name["Unassailable Mountain"]
    st = human(skills={"Resilience": 3}, specialties=[])
    assert check_specialty(mountain, st, compute(st))[0]
    assert "heavy or heavier armor" in specialty_warnings(mountain, st)[0]
    st.specialties = [(mountain["slug"], 1)]
    assert character_warnings(st)[0][0] == "Unassailable Mountain"
    st.items = [ItemState(name="Plate", kind="armor", size="heavy", slot="armor")]
    assert not character_warnings(st)
    # "any AP-sacrifice specialty" is a hard requirement.
    devoted = REG.specialties_by_name["Devoted Peers"]
    st = human(skills={"Faith": 1}, specialties=[])
    ok, reasons = check_specialty(devoted, st, compute(st))
    assert not ok and "Smite" in reasons[0]
    st.specialties = [(spec("Prayer"), 1)]
    assert check_specialty(devoted, st, compute(st))[0]


def test_usage_conditions():
    from rules.engine.requirements import specialty_warnings

    chipping = REG.specialties_by_name["Chipping Away"]
    st = human(skills={"Overpower": 1}, specialties=[])
    assert check_specialty(chipping, st, compute(st))[0]
    assert "heavy or super-heavy melee weapon" in specialty_warnings(chipping, st)[0]
    st.items = [ItemState(name="Maul", kind="melee", size="heavy", slot="weapon1")]
    assert not specialty_warnings(chipping, st)
    en_garde = REG.specialties_by_name["En-Garde"]
    assert specialty_warnings(en_garde, st)  # a heavy weapon is two-handed …
    st.specialties = [(spec("One-Handing It"), 1)]
    assert not specialty_warnings(en_garde, st)  # … unless One-Handing It
    protector = REG.specialties_by_name["Protector"]
    st.items.append(ItemState(name="Cloak", kind="deflection", slot="deflection"))
    assert specialty_warnings(protector, st)
    st.items[-1] = ItemState(name="Tower Shield", kind="deflection", slot="deflection")
    assert not specialty_warnings(protector, st)
    assert not specialty_warnings(REG.specialties_by_name["Ram"], st)  # vehicles are not checked


def test_hand_conditions():
    from rules.engine.requirements import specialty_warnings
    from rules.engine.weapons import hand_layout

    fist, garde = REG.specialties_by_name["Fisticuffs"], REG.specialties_by_name["En-Garde"]
    blade, flying = REG.specialties_by_name["Invisible Blade"], REG.specialties_by_name["Focused Flying"]
    st = human(specialties=[])
    assert not specialty_warnings(fist, st) and not specialty_warnings(flying, st)
    assert specialty_warnings(garde, st) and specialty_warnings(blade, st)
    dagger = ItemState(name="Dagger", kind="melee", size="light", slot="weapon1", concealable=True)
    st.items = [dagger]
    assert not specialty_warnings(garde, st) and not specialty_warnings(blade, st)
    assert specialty_warnings(flying, st)
    st.items.append(ItemState(name="Sabre", kind="melee", size="medium", slot="weapon2"))
    assert specialty_warnings(garde, st) and specialty_warnings(blade, st)  # sabre isn't concealable
    assert specialty_warnings(fist, st)  # both hands full
    maul = ItemState(name="Maul", kind="melee", size="heavy", slot="weapon2")
    st.items = [maul]
    layout = hand_layout(st)
    assert layout["left"] is maul and layout["blocked_by"] is maul and layout["free"] == 0
    assert specialty_warnings(fist, st)
    st.items = [ItemState(name="Axe", kind="melee", size="heavy", slot="weapon1", hands=1)]
    assert hand_layout(st)["free"] == 1 and not specialty_warnings(garde, st)


def test_weapon_breakdown_shows_character_sources():
    st = human(items=[ItemState(name="Sabre", kind="melee", size="medium", slot="weapon1")],
               effects=["status:blinded"])
    acc = compute(st).weapons[0].acc
    assert ("Effect: Blinded", -4) in acc.breakdown
    assert acc.total == compute(st).stats["acc"].total
