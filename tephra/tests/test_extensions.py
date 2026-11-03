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


def test_suulrai_gated_in_wizard_and_random(admin_client):
    reg = get_registry()
    assert reg.nationalities["suulraili"]["extension"] == "suulrai"
    assert list(reg.nationalities)[-1] == "other"
    c = Character.objects.create(race="human")
    url = reverse("wizard_step", args=[c.pk, 1])
    assert 'value="suulraili"' not in admin_client.get(url).content.decode()
    assert all(creation.random_race_and_nationality()["nationality"] != "suulraili" for _ in range(40))
    s = NarratorSettings.get()
    s.enabled_extensions = ["suulrai"]
    s.save()
    page = admin_client.get(url).content.decode()
    assert 'value="suulraili"' in page and "(Suulrai)" in page


def test_keyin_druid_only_for_gnomes():
    extensions.set_offer(["suulrai"])
    assert "keyin-druid" in {s["slug"] for s in creation.nationality_stories("suulraili", "gnome")}
    human = {s["slug"] for s in creation.nationality_stories("suulraili", "human")}
    assert "keyin-druid" not in human and "tech-bootlegger" in human


def test_suulraili_character_keeps_nationality_when_disabled(admin_client):
    c = Character.objects.create(race="human", nationality="suulraili", stories=["tech-bootlegger"], status="active")
    page = admin_client.get(c.get_absolute_url()).content.decode()
    assert "Tech-Bootlegger" in page and "Suulraili" in page


def _prosthetician(**kw):
    return Character.objects.create(race="human", skills={"Automata": 3}, specialties=[["automata-prosthetician", 1]], **kw)


def test_granted_augments_are_known_and_free(db, monkeypatch):
    from characters import services
    from rules.engine.requirements import augments_used, check_augment, known_augments
    from rules.engine.stats import compute
    reg = get_registry()
    monkeypatch.setitem(reg.specialties["automata-prosthetician"], "grants_augments",
                        ["automata-prosthetic-barbed", "automata-prosthetic-glowing"])
    c = _prosthetician(augments=["automata-prosthetic-barbed", "automata-prosthetic-air-blaster"])
    state = c.to_state()
    assert {"automata-prosthetic-barbed", "automata-prosthetic-glowing"} <= known_augments(state)
    assert augments_used(state) == 1  # Barbed was chosen before, now granted: its slot is free again
    ok, reasons = check_augment(reg.augments["automata-prosthetic-glowing"], state, compute(state))
    assert not ok and "already known" in reasons
    ok, _ = check_augment(reg.augments["automata-prosthetic-overglow"], state, compute(state))  # req. Glowing
    assert ok
    chosen, granted = services.known_augment_entries(c)
    assert [a["slug"] for a in chosen] == ["automata-prosthetic-air-blaster"]
    assert {a["granted_by"] for a in granted} == {"Prosthetician"}


def test_augment_and_race_requirement_clauses(db):
    from rules.engine.requirements import check_specialty
    from rules.engine.stats import compute
    spec = dict(get_registry().specialties["automata-prosthetician"], slug="x", requires=[
        {"type": "augment", "any": ["automata-prosthetic-barbed"]}, {"type": "race", "any": ["gnome"]}])
    state = _prosthetician().to_state()
    ok, reasons = check_specialty(spec, state, compute(state))
    assert not ok and len(reasons) == 2
    state = _prosthetician(augments=["automata-prosthetic-barbed"]).to_state()
    state.race = "gnome"
    assert check_specialty(spec, state, compute(state))[0]


def test_achievement_stories_not_offered_in_wizard(admin_client, monkeypatch):
    story = get_registry().stories["royalist"]
    monkeypatch.setitem(story, "type", "achievement")
    c = Character.objects.create(race="human", stories=["royalist"])
    url = reverse("wizard_step", args=[c.pk, 9])
    assert 'value="royalist"' not in admin_client.get(url).content.decode()
    admin_client.post(url, {"action": "save", "stories": ["militarist"]})
    c.refresh_from_db()
    assert "royalist" in c.stories  # narrator-granted story survives the wizard
