import pytest
from django.core.management import call_command
from django.urls import reverse

from characters import services
from characters.models import Character, InventoryItem
from rules import extensions
from rules.registry import get_registry


@pytest.fixture(autouse=True)
def reset_offer():
    yield
    extensions.set_offer()


def char(race, random=(), **kw):
    c = Character.objects.create(race=race, **kw)
    reg = get_registry()
    c.fixed_traits = [f"{race}/{t['slug']}" for t in reg.races[race]["fixed"]]
    c.random_traits = [f"{race}/{r}" for r in random]
    c.save()
    return c


def test_part_a_data():
    ext = [r for r in get_registry().races.values() if r.get("extension") == "races-of-tephra"]
    assert len(ext) >= 8
    for r in ext:
        assert sorted(t["roll"] for t in r["random"]) == list(range(1, 13)), r["slug"]


def test_abyssal_body(db):
    call_command("seed_catalog")
    c = char("abyssal", ["collapsed-mantle"])
    services.grant_race_items(c)
    suit = c.items.get(slot="armor")
    assert suit.name == "Abyssal pressure suit"
    sheet = c.compute()
    assert sheet.unarmed.dc.total == 6 and sheet.stats["soak"].total == 4
    plate = InventoryItem.objects.create(character=c, name="Plate", kind="armor", size="medium")
    with pytest.raises(services.EquipError):
        services.equip(c, plate, "armor")


def test_ezka_dig_and_dense_plates(db):
    c = char("ezka", ["burrower"])
    assert c.compute().stats["dig"].total == 20
    c = char("ezka", ["dense-plates"])
    soak, defense = c.compute().stats["soak"].total, c.compute().stats["def"].total
    InventoryItem.objects.create(character=c, name="Mail", kind="armor", size="medium", slot="armor")
    sheet = c.compute()
    assert sheet.stats["def"].total == defense + 4 and sheet.stats["soak"].total == soak - 1 + 3


def test_choices_and_pure_strain(db):
    c = char("daemon", trait_choices={"daemon/bestial-strength": "Overpower"})
    assert c.compute().skills["Overpower"].total == 2
    c = char("fluoform-khemic", ["pure-strain"], trait_choices={"fluoform-khemic/pure-strain": "elf"})
    elf = get_registry().races["elf"]
    assert c.compute().stats["spd"].total == elf["speed"]


def test_extra_arm_and_fluoform_subrace(db):
    c = char("crazak-transcendent", ["additional-arm"])
    assert services.has_wings(c) and c.compute().hands["extra_label"] == "Additional arm"
    c = char("fluoform-amorphide")
    s = c.compute().stats
    assert s["essence_slots"].total == 1 + char("human").compute().stats["essence_slots"].total


def test_gated_in_wizard(admin_client):
    c = Character.objects.create()
    url = reverse("wizard_step", args=[c.pk, 1])
    assert 'value="abyssal"' not in admin_client.get(url).content.decode()
    from characters.models import NarratorSettings
    s = NarratorSettings.get()
    s.enabled_extensions = ["races-of-tephra"]
    s.save()
    assert 'value="abyssal"' in admin_client.get(url).content.decode()


def test_part_b_traits(db):
    human = char("human").compute()
    s = char("obezyany").compute()
    assert s.attr_misc["Brute"].total == -4 and s.attr_misc["Dexterity"].total == 4
    s = char("obezyany", ["gorilla-build"]).compute()
    assert s.attr_misc["Brute"].total == 4 and s.attr_misc["Dexterity"].total == -4
    s = char("karshin", ["fhtagn"]).compute()
    assert (s.stats["swim"].total, s.stats["climb"].total) == (15, 25)
    assert char("manticore").compute().unarmed.dc.total == 4
    sim = char("simulacron")
    assert sim.compute().stats["swim"].total == 0
    sim.fixed_traits = sim.fixed_traits + ["simulacron/gnome-sized"]
    sim.save()
    assert sim.compute().stats["spd"].total == 15
    assert human.stats["spd"].total == 25


def test_restrained_rage_and_botched_surgery_partial_negation(db):
    notes = [n for _l, n in char("manticore", ["restrained-rage"], level=6).compute().notes]
    assert any("halved" in n for n in notes) and not any("resists vs provocation:" in n for n in notes)
    c = char("farishtaa", ["botched-surgery"])
    c.random_traits = c.random_traits + ["elf/fruit-of-the-fallen"]
    c.save()
    assert c.compute().attr_misc["Spirit"].total == 0  # Weak Souls part negated, Tree-Ripping stays


def test_racial_specialty_and_story_race_checks(db):
    from rules.engine.requirements import check_specialty, known_augments, story_allowed
    from rules.engine.stats import compute
    reg = get_registry()
    venom = reg.specialties["manticore-venom-carrier"]
    m, h = char("manticore").to_state(), char("human").to_state()
    assert check_specialty(venom, m, compute(m))[0] and not check_specialty(venom, h, compute(h))[0]
    assert story_allowed(reg.stories["fury-walker"], "manticore") and not story_allowed(reg.stories["fury-walker"], "human")
    assert story_allowed(reg.stories["walks-with-the-furious"], "human")
    assert not story_allowed(reg.stories["walks-with-the-furious"], "manticore")
    cure = char("manticore", ["dedicated-to-the-cure"]).to_state()
    assert "alchemy-rage-suppressant" in known_augments(cure)


def test_being_provoked_toggle(db):
    toggles = char("manticore").compute().toggles
    assert any(t["label"] == "Being provoked" for t in toggles)
