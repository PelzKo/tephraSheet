import pytest
from django.urls import reverse

from characters.models import Character, NarratorSettings
from rules import extensions
from rules.engine import creation
from rules.registry import get_registry


@pytest.fixture(autouse=True)
def reset_offer():
    yield
    extensions.set_offer()


def test_offer_filters_by_extension_and_keeps_owned():
    core, ext, both = {"slug": "a"}, {"slug": "b", "extension": "x"}, {"slug": "c", "extension": "y", "also_in": ["x"]}
    assert extensions.offer([core, ext, both]) == [core]
    assert extensions.offer([core, ext, both], keep={"b"}) == [core, ext]
    extensions.set_offer(["x"])
    assert extensions.offer([core, ext, both]) == [core, ext, both]


def test_disabled_race_not_offered_but_existing_character_keeps_it(admin_client):
    client = admin_client  # the narrator may open every character
    s = NarratorSettings.get()
    s.disabled_races = ["elf"]
    s.save()
    old = Character.objects.create(race="elf")
    new = Character.objects.create()
    page = client.get(reverse("wizard_step", args=[new.pk, 1])).content.decode()
    assert 'value="elf"' not in page and 'value="human"' in page
    client.post(reverse("wizard_step", args=[new.pk, 1]), {"action": "race", "race": "elf"})
    new.refresh_from_db()
    assert new.race == ""
    page = client.get(reverse("wizard_step", args=[old.pk, 1])).content.decode()
    assert 'value="elf"' in page
    old.refresh_from_db()
    assert old.race == "elf" and old.compute()
    extensions.set_offer([], ["elf"])
    assert all(creation.random_race_and_nationality()["race"] != "elf" for _ in range(30))


def test_extension_specialty_hidden_from_random_picks(monkeypatch):
    reg = get_registry()
    hidden = [s for s in reg.specialties.values() if not s["requires"]][:50]
    for s in hidden:
        monkeypatch.setitem(s, "extension", "x")
    assert not {s["slug"] for s in hidden} & {s["slug"] for s in extensions.offer(reg.specialties.values())}
    assert reg.specialties[hidden[0]["slug"]]  # lookups by slug are never filtered


def test_gm_saves_offer_settings(admin_client):
    data = {"background_story_count": 1, "max_starting_level": 1, "disabled_races": ["elf", "gnome"]}
    assert admin_client.post(reverse("gm_settings"), data).status_code == 302
    assert NarratorSettings.get().disabled_races == ["elf", "gnome"]
    assert "2 selected" in admin_client.get(reverse("gm_settings")).content.decode()


def test_missing_prosthetic_augments_parsed():
    reg = get_registry()
    assert reg.augments["automata-prosthetic-arm-grasper"]["subsection"] == "Arm prosthetic augments"
    assert reg.augments["automata-prosthetic-hand-propellers"]["slug"] != "automata-prosthetic-leg-propellers"
    sensor = reg.augments["automata-prosthetic-torso-sensor-array"]
    assert "req. Automata Tinkerer" in sensor["qualifiers"]
    assert "Automaton-Specific" not in reg.augments["automata-prosthetic-leg-propellers"]["text"]


def test_prosthetic_leg_adds_speed(db):
    c = Character.objects.create(race="human", body_augments=[["automata-prosthetic-leg-extreme-speed", 4]])
    base = Character.objects.create(race="human").compute().stats["spd"].total
    assert c.compute().stats["spd"].total == base + 15


def test_augment_requirement_checked_in_german(db):
    from rules import lang
    from rules.engine.requirements import check_augment
    from rules.engine.stats import compute
    c = Character.objects.create(race="human", skills={"Automata": 3}, specialties=[["automata-prosthetician", 1]])
    lang.set_language("de")
    try:
        state = c.to_state()
        ok, reasons = check_augment(get_registry().augments["automata-prosthetic-air-conditioner"], state, compute(state))
    finally:
        lang.set_language(lang.DEFAULT)
    assert not ok and len(reasons) == 1


def test_air_tunnel_slug_migration(db):
    from importlib import import_module

    from django.apps import apps
    rename = import_module("characters.migrations.0014_air_tunnel_slug").rename
    c = Character.objects.create(augments=["automata-prosthetic-air-funnel"],
                                 body_augments=[["automata-prosthetic-air-funnel", 2]])
    rename(apps, None)
    c.refresh_from_db()
    assert c.augments == ["automata-prosthetic-air-tunnel"]
    assert c.body_augments == [["automata-prosthetic-air-tunnel", 2]]
