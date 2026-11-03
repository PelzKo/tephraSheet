import pytest

from characters.models import Character
from rules import extensions
from rules.engine import tables
from rules.engine.requirements import augment_points, check_augment, check_specialty, known_augments
from rules.engine.stats import compute
from rules.registry import get_registry


@pytest.fixture(autouse=True)
def reset_offer():
    yield
    extensions.set_offer()


def state_of(skills, specs, augments=()):
    return Character.objects.create(race="human", skills=skills, specialties=[[s, 1] for s in specs],
                                    augments=list(augments)).to_state()


def test_data():
    reg = get_registry()
    ext = [a for a in reg.augments.values() if a.get("extension") == "explosives"]
    assert len(ext) == 59
    assert reg.augments["gadgetry-explosive-banshee"]["lists"] == ["explosive", "firebomb", "squib"]
    assert reg.augments["gadgetry-explosive-flare"]["marques"][3] == "light 25 ft (+25 dim) for 8 turns"
    assert reg.augments["gadgetry-explosive-gear-rattler"]["marques"][2].endswith("uncontrollable 3 AP")
    assert reg.stories["survived-the-bombrats"]["type"] == "achievement"


def test_squib_producer_learns_shared_augments_with_alchemy(db):
    reg = get_registry()
    state = state_of({"Alchemy": 1}, ["alchemy-squib-producer"])
    sheet = compute(state)
    assert check_augment(reg.augments["gadgetry-explosive-delay"], state, sheet)[0]
    assert check_augment(reg.augments["alchemy-squib-run-away-bomb"], state, sheet)[0]
    assert not check_augment(reg.augments["gadgetry-explosive-jumping"], state, sheet)[0]  # explosive list only
    assert augment_points(reg.augments["gadgetry-explosive-delay"], sheet, {"squib"}) == 1


def test_anti_handling_needs_delay_and_same_name_augments_stay_apart(db):
    reg = get_registry()
    state = state_of({"Gadgetry": 3}, ["gadgetry-pyrotechnician", "gadgetry-firebomber"])
    sheet = compute(state)
    assert not check_augment(reg.augments["gadgetry-explosive-anti-handling-fuse"], state, sheet)[0]
    # Battlefield Scorcher needs the firebomb Extended Blast, the explosive one doesn't count
    state = state_of({"Gadgetry": 3}, ["gadgetry-pyrotechnician", "gadgetry-firebomber"],
                     ["gadgetry-explosive-extended-blast"])
    assert not check_augment(reg.augments["gadgetry-firebomb-battlefield-scorcher"], state, compute(state))[0]
    state = state_of({"Gadgetry": 3}, ["gadgetry-pyrotechnician", "gadgetry-firebomber"],
                     ["gadgetry-firebomb-extended-blast"])
    assert check_augment(reg.augments["gadgetry-firebomb-battlefield-scorcher"], state, compute(state))[0]


def test_scanning_activator_needs_remote_activation(db):
    spec = get_registry().specialties["gadgetry-reflexive-detonation"]
    state = state_of({"Gadgetry": 3}, ["gadgetry-pyrotechnician"])
    assert not check_specialty(spec, state, compute(state))[0]
    state = state_of({"Gadgetry": 3}, ["gadgetry-pyrotechnician"], ["gadgetry-explosive-remote-activation"])
    assert check_specialty(spec, state, compute(state))[0]


def test_bomb_building_basics_grants_six(db):
    state = state_of({"Gadgetry": 3}, ["gadgetry-pyrotechnician", "gadgetry-bomb-building-basics"])
    assert {"gadgetry-explosive-damaging", "gadgetry-explosive-quick-set"} <= known_augments(state)


def test_two_marque_values():
    melter = get_registry().augments["gadgetry-explosive-melter"]["marques"]
    assert melter[tables.marque_for_points(14) - 1] == melter[0]
    assert melter[tables.marque_for_points(15) - 1] == melter[2]
