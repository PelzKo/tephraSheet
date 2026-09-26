import random

import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
from django.urls import reverse

from catalog.importer import parse_rows
from catalog.models import ItemTemplate
from characters import services
from characters.models import Character, Feedback, InventoryItem
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
    # Relentless: 3 + 1 per specialty; Fisticuffs 10, Gunsmith 4, Fluid 7 (the rolled trait may add HP).
    c.random_traits = []
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
    assert any(label == "Manual Misc Change" for label, _ in after.breakdown)
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


def test_effects_play_actions(client_char):
    client, c = client_char
    services.random_all(c, random.Random(3))
    services.finish_creation(c)
    play = lambda a, **d: client.post(reverse("play", args=[c.pk, a]), d, HTTP_HX_REQUEST="true")  # noqa: E731
    full_hp, full_wounds = c.compute().max_hp, c.compute().max_wounds
    assert play("effect-add", kind="status", key="status:fatigued").status_code == 200
    assert c.compute().max_hp == full_hp // 2
    play("effect-add", kind="called", location="2", which="fatal")
    play("effect-add", kind="called", location="5", which="wound")
    play("effect-add", kind="status", text="Poisoned")
    kinds = sorted(c.effects.filter(active=True).values_list("kind", "key"))
    assert kinds == [("fatal", "fatal:eyes"), ("status", ""), ("status", "status:fatigued"), ("wound", "wound:torso")]
    assert c.compute().max_wounds == full_wounds - 1
    resp = client.get(reverse("sheet", args=[c.pk]))
    assert b"Broken ribs" in resp.content and b"Permanently blind" in resp.content
    play("breather")
    assert not c.effects.filter(active=True, key="wound:torso").exists()  # ends with a breather
    play("set-hp", value="1")
    c.refresh_from_db()
    assert c.current_hp == 1


def test_create_random_character_command(catalog):
    call_command("create_random_character", "--if-empty", "--level", "2", "--seed", "5")
    c = Character.objects.get()
    assert c.status == "active" and c.level == 2 and c.check_password("demo")
    call_command("create_random_character", "--if-empty")
    assert Character.objects.count() == 1


def test_two_handed_equip_blocks_right_hand(client_char):
    client, c = client_char
    services.random_all(c, random.Random(4))
    services.finish_creation(c)
    c.items.filter(slot__in=["weapon1", "weapon2"]).update(slot="carried")
    sabre = InventoryItem.objects.create(character=c, name="Sabre", kind="melee", size="medium")
    maul = InventoryItem.objects.create(character=c, name="Maul", kind="melee", size="heavy")
    play = lambda a, **d: client.post(reverse("play", args=[c.pk, a]), d, HTTP_HX_REQUEST="true")  # noqa: E731
    play("equip", id=sabre.pk, slot="weapon1")
    play("equip", id=maul.pk, slot="weapon2")  # two-handed: goes left, sabre is put away
    maul.refresh_from_db(), sabre.refresh_from_db()
    assert (maul.slot, sabre.slot) == ("weapon1", "carried")
    resp = client.get(reverse("sheet", args=[c.pk]))
    assert b"Weapon (Right)" in resp.content and b"Maul needs both hands" in resp.content
    play("equip", id=sabre.pk, slot="weapon2")  # one-handed into the right hand frees the maul
    maul.refresh_from_db()
    assert maul.slot == "carried"


def test_battle_theme_choice_and_cancel(client_char):
    client, c = client_char
    services.random_all(c, random.Random(5))
    services.finish_creation(c)
    theme = get_registry().specialties_by_name["Battle Theme"]
    c.skills = dict(c.skills, Showmanship=3)
    errors = services.add_specialties_sequentially(c, [theme["slug"]], options={theme["slug"]: ""})
    assert errors and "perform" in errors[0]
    assert not services.add_specialties_sequentially(c, [theme["slug"]], options={theme["slug"]: "singing"})
    c.stance = theme["slug"]
    c.save()
    play = lambda a, **d: client.post(reverse("play", args=[c.pk, a]), d, HTTP_HX_REQUEST="true")  # noqa: E731
    resp = play("effect-add", kind="called", location="9", which="wound")  # hand: no effect on singing
    c.refresh_from_db()
    assert c.stance == theme["slug"] and b"cancelled" not in resp.content
    resp = play("effect-add", kind="called", location="4", which="wound")
    c.refresh_from_db()
    assert c.stance == "" and b"Battle Theme has been cancelled" in resp.content


def test_shield_wings_and_hand_hit(client_char):
    client, c = client_char
    services.random_all(c, random.Random(6))
    services.finish_creation(c)
    c.items.filter(slot__in=["weapon1", "weapon2", "deflection", "wings"]).update(slot="carried")
    sabre = InventoryItem.objects.create(character=c, name="Sabre", kind="melee", size="medium")
    knife = InventoryItem.objects.create(character=c, name="Knife", kind="melee", size="light")
    shield = InventoryItem.objects.create(character=c, name="Shield", kind="deflection")
    cloak = InventoryItem.objects.create(character=c, name="Cloak", kind="deflection")
    maul = InventoryItem.objects.create(character=c, name="Maul", kind="melee", size="heavy")
    services.equip(c, sabre, "weapon1")
    services.equip(c, knife, "weapon2")
    assert services.equip(c, shield, "deflection")["moved"] == ["Knife"]  # the shield takes the right hand
    assert services.equip(c, cloak, "deflection")["moved"] == ["Shield"]
    services.equip(c, knife, "weapon2")  # a cloak takes no hand
    assert set(c.items.filter(slot__in=["weapon1", "weapon2"]).values_list("name", flat=True)) == {"Sabre", "Knife"}
    with pytest.raises(services.EquipError):
        services.equip(c, knife, "wings")  # no Wings as Arms
    c.random_traits = ["ayodin/wings-as-arms"]
    c.save()
    with pytest.raises(services.EquipError):
        services.equip(c, maul, "wings")  # wings take only one-handed items
    services.equip(c, knife, "wings")
    resp = client.get(reverse("sheet", args=[c.pk]))
    assert b"Weapon (Wings)" in resp.content
    play = lambda a, **d: client.post(reverse("play", args=[c.pk, a]), d, HTTP_HX_REQUEST="true")  # noqa: E731
    resp = play("effect-add", kind="called", location="9", which="normal")  # left hand hit: drop the sabre
    sabre.refresh_from_db()
    assert sabre.slot == "carried" and b"You dropped Sabre" in resp.content


def test_rotating_barrels_hands():
    from rules.engine import tables
    from rules.engine.state import ItemState

    pistol = ItemState(name="Pepperbox", kind="firearm", size="light", augments=[(tables.ROTATING_BARRELS, 1)])
    rifle = ItemState(name="Gatling", kind="firearm", size="heavy", augments=[(tables.ROTATING_BARRELS, 1)])
    assert tables.item_hands(pistol) == 2 and not tables.needs_firing_position(pistol)
    assert tables.item_hands(rifle) == 2 and tables.needs_firing_position(rifle)
    pistol.augments.append((tables.CRANK_FREE, 1))
    assert tables.item_hands(pistol) == 1


def test_instrument_battle_theme_sunder(client_char):
    client, c = client_char
    services.random_all(c, random.Random(7))
    services.finish_creation(c)
    theme = get_registry().specialties_by_name["Battle Theme"]
    c.specialties = list(c.specialties) + [[theme["slug"], 1]]
    c.specialty_choices = {theme["slug"]: "instrument"}
    c.stance = theme["slug"]
    c.save()
    assert b"Instrument sundered" in client.get(reverse("sheet", args=[c.pk])).content
    resp = client.post(reverse("play", args=[c.pk, "theme-sundered"]), HTTP_HX_REQUEST="true")
    c.refresh_from_db()
    assert c.stance == "" and b"Battle Theme has been cancelled" in resp.content


def test_catalog_sort_keys_and_inventory_toolbar(client_char):
    client, c = client_char
    html = client.get(reverse("catalog")).content.decode()
    assert 'data-sort="5"' in html or 'data-sort="4"' in html  # size rank (heavy / super-heavy)
    sabre = ItemTemplate.objects.filter(price_dukes__gt=0).first()
    assert f'data-sort="{sabre.price_dukes}"' in html
    client.post(reverse("wizard_step", args=[c.pk, 1]), {"action": "random_all"})
    c.refresh_from_db()
    client.post(reverse("wizard_step", args=[c.pk, 10]),
                {"action": "finish", "name": c.name, "password": "abc", "password2": "abc"})
    InventoryItem.from_template(c, sabre).save()
    html = client.get(reverse("sheet", args=[c.pk]) + "?tab=inventory").content.decode()
    assert "data-inv-toolbar" in html and f'data-price="{sabre.price_dukes}"' in html


def test_feedback_submit_and_gm_review(client_char):
    client, c = client_char
    resp = client.post(reverse("feedback"), {
        "category": "bug", "name": "Ann", "message": "Wings page overlaps", "character": c.pk,
        "page_url": "http://testserver/c/1/", "page_title": "Sheet", "meta": '{"tab": "page2", "viewport": "800x600"}'})
    assert resp.status_code == 200 and resp.json() == {"ok": True}
    fb = Feedback.objects.get()
    assert fb.character == c and fb.character_name == str(c) and fb.category == "bug"
    assert fb.meta["tab"] == "page2" and "user_agent" in fb.meta and fb.status == "new"
    assert client.post(reverse("feedback"), {"message": "  "}).status_code == 400
    for _ in range(9):
        client.post(reverse("feedback"), {"message": "spam"})
    assert client.post(reverse("feedback"), {"message": "one too many"}).status_code == 429

    # Only the narrator can review.
    client.post(reverse("gm_feedback_status", args=[fb.pk]), {"status": "done"})
    fb.refresh_from_db()
    assert fb.status == "new"
    User.objects.create_superuser("gm", "gm@example.com", "pw")
    client.login(username="gm", password="pw")
    assert "Wings page overlaps" in client.get(reverse("gm_settings")).content.decode()
    client.post(reverse("gm_feedback_status", args=[fb.pk]), {"status": "done"})
    fb.refresh_from_db()
    assert fb.status == "done"
    client.post(reverse("gm_feedback_delete", args=[fb.pk]))
    assert not Feedback.objects.filter(pk=fb.pk).exists()
