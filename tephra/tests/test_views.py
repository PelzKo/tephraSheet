import random

import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
from django.urls import reverse

from catalog.importer import parse_rows
from catalog.models import ItemTemplate
from characters import services
from characters.models import Character, InventoryItem
from rules.registry import get_registry


@pytest.fixture
def catalog(db):
    call_command("seed_catalog")


@pytest.fixture
def client_char(client, catalog):
    resp = client.post(reverse("character_new"))
    character = Character.objects.get()
    assert resp.status_code == 302
    return client, character


def test_list_empty(client, db):
    assert client.get("/").status_code == 200


def test_manual_wizard_flow(client_char):
    client, c = client_char
    url = lambda n: reverse("wizard_step", args=[c.pk, n])  # noqa: E731
    assert client.get(url(1)).status_code == 200
    assert client.get(url(2)).url == url(1)  # race first
    client.post(url(1), {"action": "race", "race": "human"})
    c.refresh_from_db()
    assert c.race == "human"
    for n in range(1, 11):
        assert client.get(url(n)).status_code == 200, n
    resp = client.post(url(1), {"action": "roll", "race": "human",
                                "fixed_traits": ["human/relentless", "human/favored-attribute"]})
    c.refresh_from_db()
    assert len(c.random_traits) == 1 and c.trait_rolls
    resp = client.post(url(1), {"action": "next", "race": "human", "nationality": "evanglessian",
                                "fixed_traits": ["human/relentless", "human/favored-attribute"],
                                "choice:human/favored-attribute": "Brute", "religion": "Tailemy"})
    assert resp.url == url(2)
    skills = {"skill:Brawl": 3, "skill:Resilience": 2, "skill:Frenzy": 2, "skill:Agility": 1,
              "skill:Armsmith": 1, "skill:Luck": 1}
    assert client.post(url(2), {"action": "next", **skills}).url == url(3)
    reg = get_registry()
    for name in ("Fisticuffs", "Gunsmith", "Fluid"):
        client.post(url(4), {"action": f"add:{reg.specialties_by_name[name]['slug']}"})
    c.refresh_from_db()
    assert len(c.specialties) == 3
    assert client.post(url(4), {"action": "next"}).url == url(5)
    aug = "armsmith-firearm-crossbow-accurate"
    client.post(url(5), {"action": f"add:{aug}"})
    c.refresh_from_db()
    assert c.augments == [aug]
    rifle = ItemTemplate.objects.get(name__startswith="Heavy firearm")
    client.post(url(6), {"action": "next", "weapon1": rifle.pk, "weapon2": "", "armor": "", "deflection": ""})
    assert c.items.filter(slot="weapon1").count() == 1
    backpack = ItemTemplate.objects.get(name="Backpack")
    client.post(url(7), {"action": "next", "gear": [backpack.pk], f"qty:{backpack.pk}": 1})
    client.post(url(9), {"action": "next", "stories": ["bartender"]})
    resp = client.post(url(10), {"action": "finish", "name": "Ada Cogsley", "password": "brass", "password2": "brass"})
    c.refresh_from_db()
    assert c.status == "active", resp
    assert c.money_on_hand == 100
    sheet_resp = client.get(reverse("sheet", args=[c.pk]))
    assert sheet_resp.status_code == 200
    assert b"Ada Cogsley" in sheet_resp.content
    # Relentless: 3 + 1 per specialty; Fisticuffs 10, Gunsmith 4, Fluid 7.
    assert c.compute().max_hp == 21 + 3 + 3


def test_random_all_and_play(client_char):
    client, c = client_char
    client.post(reverse("wizard_step", args=[c.pk, 1]), {"action": "random_all"})
    c.refresh_from_db()
    assert c.race and len(c.specialties) == 3 and c.name
    resp = client.post(reverse("wizard_step", args=[c.pk, 10]),
                       {"action": "finish", "name": c.name, "password": "abc", "password2": "abc"})
    c.refresh_from_db()
    assert c.status == "active"
    sheet_url = reverse("sheet", args=[c.pk])
    assert client.get(sheet_url).status_code == 200
    play = lambda a, **d: client.post(reverse("play", args=[c.pk, a]), d, HTTP_HX_REQUEST="true")  # noqa: E731
    assert play("damage", amount=5).status_code == 200
    play("xp", delta=12)
    c.refresh_from_db()
    assert c.xp == 12
    assert client.get(reverse("levelup", args=[c.pk])).status_code == 200
    resp = client.post(reverse("levelup_options", args=[c.pk]), {"skill_two": "Brawl", "skill_one_a": "Ace",
                                                                 "skill_one_b": "Luck"})
    assert resp.status_code == 200
    client.post(reverse("levelup", args=[c.pk]), {"action": "random"})
    c.refresh_from_db()
    assert c.level == 2 and c.xp == 0 and len(c.specialties) == 4
    for a in ("breather", "toggle", "stance", "notes"):
        assert play(a).status_code == 200
    play("effect-add", kind="status", text="Fatigued")
    assert client.get(sheet_url).status_code == 200


def test_unlock_and_throttle(client, catalog):
    c = Character.objects.create(name="Locked", race="elf", status="active")
    c.set_password("secret")
    c.save()
    assert client.get(reverse("sheet", args=[c.pk])).url == reverse("unlock", args=[c.pk])
    assert b"Wrong password" in client.post(reverse("unlock", args=[c.pk]), {"password": "nope"}).content
    resp = client.post(reverse("unlock", args=[c.pk]), {"password": "secret"})
    assert resp.url == reverse("sheet", args=[c.pk])
    assert client.get(reverse("sheet", args=[c.pk])).status_code == 200


def test_admin_mode_misc(client_char):
    client, c = client_char
    services.random_all(c, random.Random(1))
    services.finish_creation(c)
    client.post(reverse("toggle_admin", args=[c.pk]), {"on": "1"})
    before = c.compute().stats["acc"].total
    resp = client.post(reverse("misc_adjust", args=[c.pk]), {"key": "acc", "delta": "1"}, HTTP_HX_REQUEST="true")
    assert resp.status_code == 200
    c.refresh_from_db()
    after = c.compute().stats["acc"]
    assert after.total == before + 1
    assert any(label == "Misc (admin)" for label, _ in after.breakdown)
    assert client.get(reverse("edit_choices", args=[c.pk])).status_code == 200


def test_catalog_pages_and_import(client_char):
    client, c = client_char
    assert client.get(reverse("catalog")).status_code == 200
    assert client.get(reverse("item_create")).status_code == 200
    text = "name,kind,size,variants,price,augments\nCavalry Sabre,melee,medium,,7 pr,Accurate II\n" \
           "Boarding Pike,melee,heavy,polearm,12 pr,\nBroken,laser,huge,,x,\n"
    rows = parse_rows(text)
    assert [bool(r["errors"]) for r in rows] == [False, False, True]
    assert rows[0]["values"]["augments"] == [["armsmith-melee-accurate", 2]]
    client.post(reverse("catalog_import") + f"?for={c.pk}", {"action": "preview", "text": text})
    client.post(reverse("catalog_import") + f"?for={c.pk}", {"action": "commit", "target": "inventory"})
    assert InventoryItem.objects.filter(character=c).count() == 2
    tsv = "name\tkind\tsize\nPepperbox\tfirearm\tlight\n"
    assert not parse_rows(tsv)[0]["errors"]
    md = "| name | kind | size |\n|---|---|---|\n| Cuirass | armor | medium |\n"
    assert parse_rows(md)[0]["values"]["kind"] == "armor"
    resp = client.post(reverse("item_create") + f"?for={c.pk}", {
        "name": "Lucky Revolver", "kind": "firearm", "size": "medium", "material": "metal",
        "augments_json": '[["armsmith-firearm-crossbow-accurate", 1]]', "slot": "weapon1", "for": c.pk})
    assert resp.status_code == 302
    item = InventoryItem.objects.get(character=c, name="Lucky Revolver")
    assert item.slot == "weapon1"
    assert c.compute().weapons[0].acc.total >= 1


def test_gm_pages(client, catalog):
    User.objects.create_superuser("gm", "gm@example.com", "pw")
    client.login(username="gm", password="pw")
    assert client.get(reverse("gm_settings")).status_code == 200
    c = Character.objects.create(name="X", race="human", status="active")
    assert client.get(reverse("sheet", args=[c.pk])).status_code == 200
