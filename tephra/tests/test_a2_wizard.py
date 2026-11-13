import random

import pytest
from django.core.management import call_command
from django.urls import reverse

from catalog.models import ItemTemplate
from characters import services
from characters.models import Character, InventoryItem, LevelLog, NarratorSettings
from rules import extensions
from rules.registry import get_registry


@pytest.fixture(autouse=True)
def reset_offer():
    yield
    extensions.set_offer()


@pytest.fixture
def client_char(client, db):
    call_command("seed_catalog")
    client.post(reverse("character_new"))
    return client, Character.objects.get()


def step_url(c, n):
    return reverse("wizard_step", args=[c.pk, n])


def abyssal(c):
    s = NarratorSettings.get()
    s.enabled_extensions = ["races-of-tephra"]
    s.save()
    c.race = "abyssal"
    c.fixed_traits = [f"abyssal/{t['slug']}" for t in get_registry().races["abyssal"]["fixed"]]
    c.random_traits = ["abyssal/collapsed-mantle"]
    c.save()
    services.grant_race_items(c)
    return c.items.get(slot="armor")


# --------------------------------------------------------------------------- B8, B14, B15, isdigit
def test_step6_keeps_body_armor_and_hides_race_items(client_char):
    client, c = client_char
    suit = abyssal(c)
    resp = client.get(step_url(c, 6))
    assert resp.status_code == 200 and b"Abyssal pressure suit" in resp.content  # shown as text, not an option
    assert f'value="{suit.template_id}"'.encode() not in resp.content
    plate = ItemTemplate.objects.filter(kind="armor").exclude(pk=suit.template_id).first()
    for value in (plate.pk, ""):
        assert client.post(step_url(c, 6), {"action": "save", "armor": value}).status_code == 302
        assert c.items.get(slot="armor").pk == suit.pk


def test_step6_keeps_custom_armor_and_deflection(client_char):
    client, c = client_char
    client.post(step_url(c, 1), {"action": "race", "race": "human"})
    InventoryItem.objects.create(character=c, name="Homemade mail", kind="armor", size="light", slot="armor")
    InventoryItem.objects.create(character=c, name="Pot lid", kind="deflection", size="light", slot="deflection")
    page = client.get(step_url(c, 6)).content.decode()
    assert page.count('value="custom" selected') == 2
    client.post(step_url(c, 6), {"action": "save", "weapon1": "", "weapon2": "", "armor": "custom",
                                 "deflection": "custom"})
    assert set(c.items.values_list("name", flat=True)) == {"Homemade mail", "Pot lid"}


def test_step6_failed_equip_keeps_old_item(client_char, monkeypatch):
    client, c = client_char
    client.post(step_url(c, 1), {"action": "race", "race": "human"})
    first, second = ItemTemplate.objects.filter(kind="armor")[:2]
    client.post(step_url(c, 6), {"action": "save", "armor": first.pk})

    def boom(*a, **k):
        raise services.EquipError("no")
    monkeypatch.setattr(services, "equip", boom)
    client.post(step_url(c, 6), {"action": "save", "armor": second.pk})
    assert c.items.get(slot="armor").template_id == first.pk


def test_unicode_digits_do_not_crash(client_char):
    client, c = client_char
    client.post(step_url(c, 1), {"action": "race", "race": "human"})
    backpack = ItemTemplate.objects.get(name="Backpack")
    resp = client.post(step_url(c, 7), {"action": "save", "gear": [backpack.pk], f"qty:{backpack.pk}": "²"})
    assert resp.status_code == 302 and c.items.get(name="Backpack").quantity == 1
    assert client.post(step_url(c, 6), {"action": "save", "weapon1": "²"}).status_code == 302


# --------------------------------------------------------------------------- B9/C1, B13/C2, C17
def finished(client, c, seed=3):
    services.random_all(c, random.Random(seed))
    c.set_password("pw")
    services.finish_creation(c)
    client.post(reverse("unlock", args=[c.pk]), {"password": "pw"})
    NarratorSettings.objects.update(allow_player_admin_mode=True)
    client.post(reverse("toggle_admin", args=[c.pk]), {"on": "1"})
    return c


def test_reopened_wizard_refuses_random_and_finish(client_char):
    client, c = client_char
    finished(client, c)
    c.current_hp, c.wounds_taken, c.money_on_hand = 3, 2, 7
    c.save()
    before = (list(c.specialties), list(c.augments), c.race, c.name)
    page = client.get(step_url(c, 4)).content.decode()
    assert 'value="random"' not in page and 'value="random_all"' not in page and "Back to sheet" in page
    assert 'value="finish"' not in client.get(step_url(c, 10)).content.decode()
    for step, action in ((4, "random"), (1, "random_all"), (10, "finish"), (7, "random")):
        client.post(step_url(c, step), {"action": action})
    c.refresh_from_db()
    assert (c.specialties, c.augments, c.race, c.name) == before
    assert (c.current_hp, c.wounds_taken, c.money_on_hand) == (3, 2, 7)
    assert LevelLog.objects.filter(character=c).count() == 1
    # Saving step 2 with a leveled skill allocation works.
    c.skills = dict(c.skills, Luck=c.skills.get("Luck", 0) + 2)
    c.save()
    data = {"action": "next", **{f"skill:{s}": v for s, v in c.skills.items()}}
    assert client.post(step_url(c, 2), data).url == step_url(c, 3)


def test_revalidate_reports_and_spares_granted(client_char):
    client, c = client_char
    client.post(step_url(c, 1), {"action": "race", "race": "human"})
    c.refresh_from_db()
    reg = get_registry()
    fisticuffs = reg.specialties_by_name["Fisticuffs"]["slug"]
    c.skills = {"Brawl": 3}
    c.specialties = [[fisticuffs, 1]]
    c.save()
    resp = client.post(step_url(c, 2), {"action": "save"}, follow=True)  # all points removed
    c.refresh_from_db()
    assert c.specialties == []
    assert "Removed because prerequisites are no longer met: Fisticuffs" in resp.content.decode()
    # Narrator-granted entries stay.
    c.specialties, c.narrator_granted = [[fisticuffs, 1]], [f"spec:{fisticuffs}"]
    c.save()
    client.post(step_url(c, 2), {"action": "save"})
    c.refresh_from_db()
    assert c.specialties == [[fisticuffs, 1]]


def test_admin_grants_are_marked_and_kept(client_char):
    client, c = client_char
    finished(client, c)
    reg = get_registry()
    spec = next(s for s in reg.specialties.values() if s["slug"] not in {x for x, _ in c.specialties}
                and s["requires"])
    client.post(reverse("edit_choices", args=[c.pk]), {"action": "add_specialty", "slug": spec["slug"]})
    c.refresh_from_db()
    assert f"spec:{spec['slug']}" in c.narrator_granted
    assert b"Granted by the narrator" in client.get(reverse("sheet", args=[c.pk])).content
    aug = next(a for a in reg.augments.values() if a["slug"] not in c.augments)
    client.post(reverse("augments", args=[c.pk]), {"action": "grant", "slug": aug["slug"]})
    c.refresh_from_db()
    assert aug["slug"] in c.augments and f"aug:{aug['slug']}" in c.narrator_granted
    assert not services.set_augments(c, list(c.augments)) and aug["slug"] in c.augments
    client.post(reverse("augments", args=[c.pk]), {"action": "remove", "slug": aug["slug"]})
    c.refresh_from_db()
    assert f"aug:{aug['slug']}" not in c.narrator_granted
