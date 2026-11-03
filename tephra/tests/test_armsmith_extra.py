import pytest

from catalog.forms import ItemForm
from catalog.models import ItemTemplate
from characters.models import Character, InventoryItem
from rules import extensions
from rules.engine.requirements import check_augment, specialty_warnings
from rules.engine.stats import compute
from rules.registry import get_registry


@pytest.fixture(autouse=True)
def reset_offer():
    yield
    extensions.set_offer()


def smith(*specs, **kw):
    return Character.objects.create(race="human", skills={"Armsmith": 4},
                                    specialties=[[s, 1] for s in specs], **kw)


def test_data_merged():
    reg = get_registry()
    ext = [s for s in reg.specialties.values() if s.get("extension") == "armsmith-extra"]
    augs = [a for a in reg.augments.values() if a.get("extension") == "armsmith-extra"]
    assert len(ext) == 16 and len(augs) == 53
    assert reg.specialties["armsmith-shield-forger"]["attribute"] == "Sciences"
    assert reg.augments["armsmith-munition-drill-shot"]["two_marque"]


def test_munition_slots():
    assert ItemTemplate(kind="ammo").slot_count == 1
    assert ItemTemplate(kind="ammo", beta=True).slot_count == 3
    assert ItemTemplate(kind="deflection", material="wood").slot_count == 2


def test_shield_augments_raise_deflection(db):
    c = smith()
    shield = InventoryItem.objects.create(character=c, name="Shield", kind="deflection", slot="deflection",
                                          deflect_bonus=4, augments=[["armsmith-shield-improved-deflection", 3],
                                                                     ["armsmith-shield-barricading", 3]])
    assert c.compute().deflection["bonus"].total == 7
    c.toggles = [f"item:{shield.pk}:aug:armsmith-shield-barricading"]
    c.save()
    assert c.compute().deflection["bonus"].total == 12


def test_turret_footing_and_belt_fed(db):
    c = smith()
    InventoryItem.objects.create(character=c, name="Turret", kind="firearm", size="super-heavy", slot="weapon1",
                                 variants=["turret"], ap_ready=2, dc=12,
                                 augments=[["armsmith-turret-belt-fed", 3]])
    block = c.compute().weapons[0]
    assert block.ap_ready.total == 0
    assert any("Footing" in n for n in block.notes)
    assert block.acc.total == c.compute().stats["acc"].total  # no super-heavy −3 for a turret
    c.specialties = [["armsmith-fast-mounting", 1]]
    c.save()
    assert not any("Footing" in n for n in c.compute().weapons[0].notes)


def test_crafting_basics_grant_and_turret_requirements(db):
    reg = get_registry()
    state = smith("armsmith-shield-forger", "armsmith-shield-crafting-basics").to_state()
    ok, reasons = check_augment(reg.augments["armsmith-shield-bulletproofing"], state, compute(state))
    assert not ok and "already known" in reasons
    state = smith("armsmith-gunsmith", "armsmith-turret-builder").to_state()
    ok, reasons = check_augment(reg.augments["armsmith-turret-body-part-seeker"], state, compute(state))
    assert not ok


def test_turret_specialty_warns_without_turret_builder(db):
    spec = get_registry().specialties["armsmith-artillery"]
    assert specialty_warnings(spec, smith().to_state())
    assert not specialty_warnings(spec, smith("armsmith-turret-builder").to_state())


def test_item_form_turret_augments(db):
    extensions.set_offer(["armsmith-extra"])
    base = {"name": "Gun", "kind": "firearm", "size": "super-heavy", "material": "metal",
            "augments_json": '[["armsmith-turret-armored", 1]]', "deflect_melee": "on"}
    assert not ItemForm(base).is_valid()
    assert ItemForm(dict(base, variants=["turret"])).is_valid()
    ammo = ItemForm({"name": "Rounds", "kind": "ammo", "material": "metal", "deflect_melee": "on",
                     "augments_json": '[["armsmith-munition-drill-shot", 1], ["armsmith-munition-heavy", 1]]'})
    assert not ammo.is_valid()  # 2 augments, 1 slot


def test_gated_from_offers():
    names = {s["name_en"] for s in extensions.offer(get_registry().specialties.values())}
    assert "Munitions Crafter" not in names
    extensions.set_offer(["armsmith-extra"])
    assert "Munitions Crafter" in {s["name_en"] for s in extensions.offer(get_registry().specialties.values())}
