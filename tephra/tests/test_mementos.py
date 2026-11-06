import pytest

from catalog.forms import ItemForm
from characters.models import Character, InventoryItem
from rules import extensions
from rules.engine import tables
from rules.engine.requirements import check_augment
from rules.engine.stats import compute
from rules.registry import get_registry


@pytest.fixture(autouse=True)
def reset_offer():
    yield
    extensions.set_offer()


def lucky(*specs):
    return Character.objects.create(race="human", skills={"Luck": 1}, specialties=[[s, 1] for s in specs])


def charm(c, augs, slot="carried", memento=True):
    return InventoryItem.objects.create(character=c, name="Charm", kind="general", slot=slot, memento=memento,
                                        augments=augs)


def test_data_and_max():
    reg = get_registry()
    assert reg.specialties["luck-mementos"]["crafts"] == ["memento"]
    assert len([a for a in reg.augments.values() if "memento" in a["lists"]]) == 48
    assert [tables.max_mementos(n) for n in (0, 1, 4, 24)] == [0, 1, 2, 7]


def test_learning(db):
    reg = get_registry()
    state = lucky("luck-mementos").to_state()
    sheet = compute(state)
    assert check_augment(reg.augments["luck-memento-keen"], state, sheet)[0]
    assert not check_augment(reg.augments["luck-memento-hand-slip"], state, sheet)[0]  # needs Feeling Lucky
    assert not check_augment(reg.augments["luck-memento-master-of-fortune"], state, sheet)[0]  # needs Moneymaker


def test_carried_memento_applies_and_stacks_once(db):
    c = lucky()
    base = c.compute().stats["acc"].total
    charm(c, [["luck-memento-keen", 2]])
    assert c.compute().stats["acc"].total == base + 2
    charm(c, [["luck-memento-keen", 3]])
    assert c.compute().stats["acc"].total == base + 3  # same Spirit augment twice: highest only
    charm(c, [["luck-memento-keen", 4]], slot="stored")
    assert c.compute().stats["acc"].total == base + 3  # stored: no effect


def test_carried_non_memento_does_nothing(db):
    c = lucky()
    base = c.compute().stats["acc"].total
    charm(c, [["luck-memento-keen", 2]], memento=False)
    assert c.compute().stats["acc"].total == base


def test_item_form_memento_slots(db):
    extensions.set_offer(["mementos"])
    data = {"name": "Die", "kind": "general", "material": "metal", "deflect_melee": "on", "binding": 0,
            "augments_json": '[["luck-memento-keen", 1], ["luck-memento-magical-numbers", 1]]'}
    assert not ItemForm(data).is_valid()  # not a memento
    assert not ItemForm(dict(data, memento="on")).is_valid()  # 1 + 3 slots > 3
    assert ItemForm(dict(data, memento="on", beta="on")).is_valid()
    extensions.set_offer()
    assert "memento" not in ItemForm().fields
