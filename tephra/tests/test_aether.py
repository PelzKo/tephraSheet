import pytest

from catalog.forms import ItemForm
from characters.models import Character, InventoryItem
from rules import extensions
from rules.engine import effects
from rules.engine.requirements import check_augment, known_augments
from rules.engine.stats import compute
from rules.registry import get_registry


@pytest.fixture(autouse=True)
def reset_offer():
    yield
    extensions.set_offer()


def designer(*specs, **kw):
    return Character.objects.create(race="human", skills={"Gadgetry": 4}, specialties=[[s, 1] for s in specs], **kw)


def test_data():
    reg = get_registry()
    assert reg.specialties["gadgetry-resonator-designer"]["crafts"] == ["resonator"]
    assert len([a for a in reg.augments.values() if a.get("extension") == "aether"]) == 23
    blast = reg.augments["gadgetry-resonator-bright-blast"]
    assert blast["two_marque"] and blast["marques"][1] == blast["marques"][0]


def test_resonator_augments_need_designer(db):
    reg = get_registry()
    state = designer().to_state()
    assert not check_augment(reg.augments["gadgetry-resonator-burning"], state, compute(state))[0]
    state = designer("gadgetry-resonator-designer").to_state()
    assert check_augment(reg.augments["gadgetry-resonator-burning"], state, compute(state))[0]
    assert not check_augment(reg.augments["gadgetry-resonator-fast-black-trap"], state, compute(state))[0]


def test_resonator_basics_grant_five(db):
    state = designer("gadgetry-resonator-designer", "gadgetry-resonator-basics").to_state()
    assert {"gadgetry-resonator-burning", "gadgetry-resonator-self-lit"} <= known_augments(state)


def test_aether_weapon_lists_resonator_effects(db):
    c = designer()
    InventoryItem.objects.create(character=c, name="Aether Resonator", kind="resonator", slot="worn", hands=0,
                                 augments=[["gadgetry-resonator-burning", 2]])
    InventoryItem.objects.create(character=c, name="Aether blade", kind="melee", size="medium", slot="weapon1",
                                 variants=["aether"])
    InventoryItem.objects.create(character=c, name="Manipulator Glove", kind="gear", slot="worn", hands=0)
    sheet = c.compute()
    assert any("Burning mQ II" in n for n in sheet.weapons[0].notes)
    assert any("Burning mQ II" in n for n in sheet.unarmed.notes)


def test_gated_kind_and_effects(db):
    assert "resonator" not in dict(ItemForm().fields["kind"].choices)
    assert "irradiated" not in {e["slug"] for e in effects.status_list()}
    extensions.set_offer(["aether"])
    assert "resonator" in dict(ItemForm().fields["kind"].choices)
    assert "irradiated" in {e["slug"] for e in effects.status_list()}
    form = ItemForm({"name": "Res", "kind": "resonator", "material": "metal", "deflect_melee": "on",
                     "augments_json": '[["gadgetry-resonator-burning", 1]]'})
    assert form.is_valid(), form.errors
