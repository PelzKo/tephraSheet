import pytest
from django.urls import reverse

from characters.models import Character, NarratorSettings, Pet
from rules import extensions
from rules.engine.pets import PetState, compute_pet, sp_marque


@pytest.fixture(autouse=True)
def reset_offer():
    yield
    extensions.set_offer()


WOLF_TRAITS = ["blooded", "forcible-will", "howl", "offensive-advantage", "piercing-attacks", "flesh-tearing",
               "pack-instincts", "sharp-senses"]


def test_engine_wolf_like():
    s = compute_pet(PetState(template="medium-land", movement=["swift"], traits=[[t, None] for t in WOLF_TRAITS],
                             wild=True))
    assert s["sp"].total == 8 and s["marque"] == 2
    assert s["stats"]["hp"].total == 9 + 6 * 8  # template + 6 HP per SP
    assert s["stats"]["ap"].total == 4  # wild, marque 2
    assert s["stats"]["spd"].total == 60 and s["attacks"][0]["dmg"] == [6, 12, 18, 24]
    assert [label for label, _v in s["stats"]["hp"].breakdown][0].startswith("Template")


def test_engine_rules():
    assert [sp_marque(n) for n in (3, 4, 8, 9, 13, 14)] == [1, 2, 2, 3, 3, 4]
    gorilla = compute_pet(PetState(template="large-land", traits=[[t, None] for t in
                                   ["hardy", "extra-hardy", "tough-body"]]))
    assert gorilla["stats"]["hp"].total == 12 + 14 * 3 and gorilla["stats"]["wnd"].total == 12 + 2 * 3
    viper = compute_pet(PetState(template="small-land", traits=[["painful", None], ["extra-venoms", None]] +
                                 [["blooded", None]] * 0))
    assert viper["venom_doses"] == 2
    tamed = compute_pet(PetState(template="small-land", traits=[["social", None], ["howl", None], ["blooded", None]]))
    assert tamed["taming"] == 2 and tamed["price_pr"] == 3 * 15


def test_editor_and_actions(admin_client):
    s = NarratorSettings.get()
    s.enabled_extensions = ["pets-and-predators"]
    s.save()
    c = Character.objects.create(race="human", status="active")
    admin_client.post(reverse("pet_new", args=[c.pk]), {"name": "Rex", "template": "medium-land",
                                                         "movement": ["swift"], "traits": ["howl", "blooded"]})
    pet = Pet.objects.get()
    assert pet.traits == [["howl", None], ["blooded", None]]
    page = admin_client.get(reverse("pet_edit", args=[c.pk, pet.pk])).content.decode()
    assert 'name="row1-major"' in page  # 2 SP -> 2 derived rows
    admin_client.post(reverse("play", args=[c.pk, "pet-hp"]), {"id": pet.pk, "amount": 5, "sign": "1"})
    pet.refresh_from_db()
    assert pet.hp_damage == 5
    assert "Rex" in admin_client.get(c.get_absolute_url() + "?tab=pets").content.decode()


def test_editor_gated(admin_client):
    c = Character.objects.create(race="human")
    assert admin_client.get(reverse("pet_new", args=[c.pk])).status_code == 404


def test_presets_recomputed():
    from rules.registry import get_registry
    presets = get_registry().animals["presets"]
    assert len(presets) >= 16
    g = presets["gorilla"]
    s = compute_pet(PetState(template=g["template"], movement=g["movement"], traits=g["traits"],
                             stories=g["stories"], derived=g["derived"], wild=g["wild"]))
    assert s["stats"]["hp"].total == 166 and s["stats"]["wnd"].total == 34
    attacks = {a["name"]: a["dmg"] for a in s["attacks"]}
    assert attacks["Hurl"] == [5, 10, 15, 20] and attacks["Unarmed (limbs)"] == [4, 8, 12, 16]


def test_create_from_preset(admin_client):
    s = NarratorSettings.get()
    s.enabled_extensions = ["pets-and-predators"]
    s.save()
    c = Character.objects.create(race="human", status="active")
    admin_client.post(reverse("pet_new", args=[c.pk]), {"preset": "wolf", "name": ""})
    pet = Pet.objects.get()
    assert pet.name == "Wolf" and pet.origin == "preset" and len(pet.derived) == 8
