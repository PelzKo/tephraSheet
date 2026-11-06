import pytest
from django.urls import reverse

from characters.models import Character, InventoryItem
from rules import extensions
from rules.engine import tables
from rules.engine.liquids import liquid_block
from rules.engine.requirements import check_augment
from rules.engine.state import ItemState
from rules.engine.stats import compute
from rules.registry import get_registry


@pytest.fixture(autouse=True)
def reset_offer():
    yield
    extensions.set_offer()


def test_data_and_diy_table():
    reg = get_registry()
    assert reg.specialties["alchemy-liquid-life-giver"]["crafts"] == ["living-liquid"]
    assert len([a for a in reg.augments.values() if "living-liquid" in a["lists"]]) == 31
    assert [tables.max_liquids(d) for d in (0, 1, 12, 14)] == [0, 2, 6, 6]


def test_learning(db):
    reg = get_registry()
    state = Character.objects.create(race="human", skills={"Alchemy": 1},
                                     specialties=[["alchemy-liquid-life-giver", 1]]).to_state()
    sheet = compute(state)
    assert check_augment(reg.augments["alchemy-living-liquid-accurate-attacks"], state, sheet)[0]
    assert not check_augment(reg.augments["alchemy-living-liquid-defensive"], state, sheet)[0]


def test_liquid_block():
    base = liquid_block(ItemState(name="Slime", kind="living-liquid"))["stats"]
    assert (base["hp"].total, base["spd"].total, base["dc"].total, base["evaporation"].total) == (20, 20, 2, 5)
    improper = liquid_block(ItemState(name="Slime", kind="living-liquid", variants=["improper"]))["stats"]
    assert (improper["hp"].total, improper["evaporation"].total) == (10, 10)
    s = liquid_block(ItemState(name="Slime", kind="living-liquid", augments=[
        ("alchemy-living-liquid-hearty-ooze", 2), ("alchemy-living-liquid-walking-weapon", 3),
        ("alchemy-living-liquid-fluid-liquid", 1), ("alchemy-living-liquid-stable", 4)]))["stats"]
    assert (s["hp"].total, s["dc"].total, s["evaporation"].total) == (28, 5, 7)
    assert any("Hearty Ooze" in label for label, _v in s["hp"].breakdown)


def test_release_damage_and_evaporate(admin_client):
    c = Character.objects.create(race="human", status="active")
    vial = InventoryItem.objects.create(character=c, name="Slime", kind="living-liquid", quantity=2,
                                        augments=[["alchemy-living-liquid-accurate-attacks", 1]])
    acc = c.compute().stats["acc"].total
    play = lambda a, **d: admin_client.post(reverse("play", args=[c.pk, a]), d)  # noqa: E731
    play("liquid-release", id=vial.pk, improper="0")
    vial.refresh_from_db()
    liquid = c.items.get(slot="released")
    assert vial.quantity == 1 and c.compute().stats["acc"].total == acc  # liquid bonus never hits the character
    assert "Slime" in admin_client.get(c.get_absolute_url()).content.decode()
    play("liquid-damage", id=liquid.pk, amount=12)
    play("liquid-end-turn", id=liquid.pk)  # 12 + 5 = 17 of 20
    liquid.refresh_from_db()
    assert liquid.wounds_taken == 17
    play("liquid-end-turn", id=liquid.pk)
    assert not c.items.filter(slot="released").exists()  # evaporated: card gone
    play("liquid-release", id=vial.pk, improper="1")
    assert not c.items.filter(pk=vial.pk).exists()
    assert "improper" in c.items.get(slot="released").variants
