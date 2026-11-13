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


# --------------------------------------------------------------------------- level-up: B10, B12, XP, retrofit, C5–C8
def levelup_post(client, c, **extra):
    data = {"action": "apply", "skill_two": "Brawl", "skill_one_a": "Luck", "skill_one_b": "Faith", **extra}
    return client.post(reverse("levelup", args=[c.pk]), data, follow=True)


def free_spec(c, **want):
    reg = get_registry()
    owned = {s for s, _ in c.specialties}
    return next(s for s in reg.specialties.values() if s["slug"] not in owned and not s["requires"]
                and s["skill"] in ("Brawl", "Luck", "Faith") and not s.get("options")
                and all(s.get(k) == v for k, v in want.items()))


def test_levelup_keeps_damage_and_xp_rules(client_char):
    client, c = client_char
    finished(client, c)
    c.xp, c.wounds_taken = 14, 2
    c.current_hp = c.compute().max_hp - 5
    c.save()
    max_before = c.compute().max_hp
    levelup_post(client, c, specialty=free_spec(c)["slug"])
    c.refresh_from_db()
    assert c.level == 2 and c.xp == 2 and c.wounds_taken == 2
    assert c.current_hp == c.compute().max_hp - 5 and c.compute().max_hp >= max_before
    # Admin mode below 10 XP: the XP stay.
    c.xp = 4
    c.save()
    levelup_post(client, c, specialty=free_spec(c)["slug"])
    c.refresh_from_db()
    assert c.level == 3 and c.xp == 4


def test_catch_up_money_once_and_progress(client_char):
    client, c = client_char
    services.random_all(c, random.Random(5))
    c.set_password("pw")
    c.target_level = 2
    services.finish_creation(c)
    assert c.money_on_hand == services.starting_money(2)
    client.post(reverse("unlock", args=[c.pk]), {"password": "pw"})
    c.money_on_hand = 3  # spent in play
    c.target_level = 3  # the narrator raises the target later
    c.save()
    page = client.get(reverse("levelup", args=[c.pk])).content.decode()
    assert "Level 2 of 3" in page
    levelup_post(client, c, specialty=free_spec(c)["slug"])
    c.refresh_from_db()
    assert c.level == 2 and c.money_on_hand == 3
    resp = client.get(reverse("augments", args=[c.pk])).content.decode()
    assert "Continue levelling" in resp


def test_levelup_preview_table(client_char):
    client, c = client_char
    finished(client, c)
    spec = free_spec(c)
    resp = client.post(reverse("levelup_preview", args=[c.pk]), {"skill_two": "Brawl", "specialty": spec["slug"]})
    assert resp.status_code == 200 and b"Brawl" in resp.content and b'class="changed"' in resp.content


def test_plan_tidy_and_differs_note_and_planned_augment(client_char):
    client, c = client_char
    finished(client, c)
    from characters.views.wizard import augment_options
    spec = free_spec(c)
    listed = [o["aug"]["slug"] for _g, items in augment_options(c)[1] for o in items if not o["known"]]
    aug = listed[0]
    c.plan = [{"level": 2, "skills": {}, "specialty": spec["slug"], "augments": [aug], "note": ""},
              {"level": 3, "skills": {}, "specialty": "", "augments": [], "note": "later"}]
    c.xp = 20
    c.save()
    other = next(
        s for s in get_registry().specialties.values() if s["slug"] != spec["slug"] and not s["requires"]
        and s["skill"] == "Brawl" and s["slug"] not in {x for x, _ in c.specialties} and not s.get("options"))
    resp = levelup_post(client, c, specialty=other["slug"])
    assert "Level 2 differs from your plan." in resp.content.decode()
    c.refresh_from_db()
    assert [e["level"] for e in c.plan] == [2, 3]
    page = client.get(reverse("augments", args=[c.pk])).content.decode()
    assert "planned for this level" in page
    levelup_post(client, c, specialty=free_spec(c)["slug"])
    c.refresh_from_db()
    assert [e["level"] for e in c.plan] == [3]


def test_retrofit_refuses_breaking_dependents_and_logs(db):
    reg = get_registry()
    dep = next(s for s in reg.specialties.values()
               if any(cl["type"] == "specialty" and not cl.get("soft") for cl in s["requires"])
               and len(next(cl for cl in s["requires"] if cl["type"] == "specialty")["any"]) == 1)
    need_name = next(cl for cl in dep["requires"] if cl["type"] == "specialty")["any"][0]
    need = reg.specialties_by_name[need_name]
    c = Character.objects.create(race="human", status="active", level=3, skills={s: 10 for s in
                                 [need["skill"], dep["skill"]] if s})
    c.specialties = [[need["slug"], 1], [dep["slug"], 2]]
    c.save()
    assert dep["slug"] in services.legal_specialties(c)
    target = next(s for s in reg.specialties.values() if s["attribute"] == need["attribute"]
                  and not s["requires"] and s["slug"] != need["slug"] and s["skill"] == need["skill"])
    fresh = next(s for s in reg.specialties.values() if not s["requires"] and s["skill"] == need["skill"]
                 and s["slug"] not in (need["slug"], target["slug"], dep["slug"]) and not s.get("options"))
    skills = {need["skill"]: 2, "Luck": 1, "Faith": 1} if need["skill"] not in ("Luck", "Faith") else None
    errors = services.apply_levelup(c, skills, fresh["slug"], retrofit=(need["slug"], target["slug"]), from_xp=False)
    assert errors and "would lose a prerequisite" in errors[0]
    c.refresh_from_db()
    c.specialties = [[need["slug"], 1]]
    c.save()
    assert not services.apply_levelup(c, skills, fresh["slug"], retrofit=(need["slug"], target["slug"]),
                                      from_xp=False)
    log = LevelLog.objects.get(character=c, level=4)
    assert log.data["retrofit_level"] == 1


def test_planner_checks_augments_capacity_and_retrofit(client_char):
    client, c = client_char
    finished(client, c)
    reg = get_registry()
    url = reverse("planner", args=[c.pk])
    many = [a for a in reg.augments if a not in c.augments][:30]
    client.post(url, {"action": "save", "level": "2", "augments": many})
    page = client.get(url).content.decode()
    assert "augments can be learned" in page or "needs" in page
    old = c.specialties[0][0]
    new = next(s["slug"] for s in reg.specialties.values() if s["attribute"] == reg.specialties[old]["attribute"]
               and s["slug"] != old and not s["requires"])
    client.post(url, {"action": "save", "level": "4", "retrofit_old": old, "retrofit_new": new})
    client.post(url, {"action": "save", "level": "5", "retrofit_old": old, "retrofit_new": new})
    c.refresh_from_db()
    plans = {e["level"]: e for e in c.plan}
    assert plans[4]["retrofit"] == [old, new] and 5 not in plans
    state, checks = __import__("characters.views.planner", fromlist=["x"]).planned_state(c)
    assert new in {s for s, _ in state.specialties} and old not in {s for s, _ in state.specialties}


# --------------------------------------------------------------------------- C4, C11, C16
def test_finish_checklist_lists_open_points(client_char):
    client, c = client_char
    client.post(step_url(c, 1), {"action": "race", "race": "human"})
    page = client.get(step_url(c, 10)).content.decode()
    assert "Still open" in page and "Empty hands: 2" in page
    assert f'href="{step_url(c, 2)}"' in page and f'href="{step_url(c, 6)}"' in page


def test_specialty_picker_show_all_lists_hidden_with_reason(client_char):
    client, c = client_char
    client.post(step_url(c, 1), {"action": "race", "race": "human"})
    from characters.views.wizard import specialty_options
    c.refresh_from_db()
    extensions.set_offer(["races-of-tephra"])
    _sheet, groups = specialty_options(c)
    entries = [o for _k, items in groups for o in items]
    hidden = [o for o in entries if o["hidden"]]
    assert hidden and all(not o["ok"] and o["reasons"] for o in hidden)
    assert any(o["spec"].get("racial") and "another race" in "; ".join(o["reasons"]) for o in hidden)
    page = client.get(step_url(c, 4)).content.decode()
    assert "Show all" in page and 'x-show="all &&' in page


def test_random_character_command_race_and_seed(db, capsys):
    call_command("create_random_character", "--race", "elf", "--seed", "7")
    out = capsys.readouterr().out
    c = Character.objects.get()
    assert c.race == "elf" and "seed 7" in out and c.status == "active"
    call_command("create_random_character")
    assert "seed " in capsys.readouterr().out


def test_planner_retrofit_reports_broken_dependents(db):
    from characters.views.planner import planned_state
    reg = get_registry()
    dep = next(s for s in reg.specialties.values()
               if any(cl["type"] == "specialty" and not cl.get("soft") for cl in s["requires"])
               and len(next(cl for cl in s["requires"] if cl["type"] == "specialty")["any"]) == 1)
    need = reg.specialties_by_name[next(cl for cl in dep["requires"] if cl["type"] == "specialty")["any"][0]]
    target = next(s for s in reg.specialties.values() if s["attribute"] == need["attribute"]
                  and not s["requires"] and s["slug"] != need["slug"] and s["skill"] == need["skill"])
    c = Character.objects.create(race="human", status="active", level=3,
                                 skills={s: 10 for s in [need["skill"], dep["skill"]] if s},
                                 specialties=[[need["slug"], 1], [dep["slug"], 2]],
                                 plan=[{"level": 4, "retrofit": [need["slug"], target["slug"]]}])
    _state, checks = planned_state(c)
    assert any("would lose a prerequisite" in p and dep["name"] in p for p in checks[0][1])


def test_admin_grant_offered_for_eligible_augment(client_char):
    client, c = client_char
    finished(client, c)
    client.post(reverse("toggle_admin", args=[c.pk]), {"on": "1"})
    page = client.get(reverse("augments", args=[c.pk])).content.decode()
    assert page.count('value="grant"') >= page.count('value="add"') + page.count('value="swap"') > 0
