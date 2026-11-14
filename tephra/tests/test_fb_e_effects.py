"""Package E: effect amounts (Bleeding, Burning, Radiation Burns, Stunned, neck Bleeding) and AP payments."""

import random

import pytest
from django.core.management import call_command
from django.urls import reverse

from characters import actionlog, services, transfer
from characters.models import Character, EffectEntry

HX = {"HTTP_HX_REQUEST": "true"}


@pytest.fixture
def char(db, admin_client):
    call_command("seed_catalog")
    c = Character.objects.create()
    services.random_all(c, random.Random(1))
    services.finish_creation(c)
    return admin_client, c


def play(client, c, action, **data):
    resp = client.post(reverse("play", args=[c.pk, action]), data, **HX)
    c.refresh_from_db()
    return resp


def add(client, c, key, amount=None):
    data = {"kind": "status", "key": f"status:{key}"} | ({"amount": str(amount)} if amount else {})
    play(client, c, "effect-add", **data)
    return EffectEntry.objects.filter(character=c, key=f"status:{key}", active=True).first()


def fight(client, c):
    play(client, c, "fight-start")
    return c.compute().stats["ap"].total


def test_bleeding_add_and_stack(char):
    client, c = char
    add(client, c, "bleeding", 4)
    e = add(client, c, "bleeding", 3)
    assert e.amount == 7 and EffectEntry.objects.filter(key="status:bleeding").count() == 1
    assert b"Bleeding (7)" in client.get(reverse("sheet", args=[c.pk])).content


def test_bleeding_refresh_damage_rolls_over_into_wounds(char):
    client, c = char
    sheet = c.compute()
    c.current_hp = 3
    c.save()
    fight(client, c)
    add(client, c, "bleeding", 5)
    resp = play(client, c, "fight-end-turn")
    assert c.current_hp == 0 and c.wounds_taken == 2 and b"5 damage" in resp.content
    c.wounds_taken = sheet.max_wounds - 1
    c.save()
    play(client, c, "fight-end-turn")
    assert c.wounds_taken == sheet.max_wounds  # capped, max-wounds logic of the damage action


def test_bleeding_removal_by_ap(char):
    client, c = char
    e = add(client, c, "bleeding", 12)
    play(client, c, "effect-pay", id=e.pk, ap="1")  # outside fight: informational only
    e.refresh_from_db()
    assert e.amount == 7 and e.active and c.fight == {}
    max_ap = fight(client, c)
    play(client, c, "effect-pay", id=e.pk, ap="9")  # capped at 2 AP (exact)
    e.refresh_from_db()
    assert not e.active and e.amount == 0 and c.fight["ap"] == max_ap - 2


def test_bleeding_too_few_ap_in_fight(char):
    client, c = char
    e = add(client, c, "bleeding", 50)
    max_ap = fight(client, c)
    play(client, c, "fight-spend", amount=str(max_ap))
    resp = play(client, c, "effect-pay", id=e.pk, ap="1")
    e.refresh_from_db()
    assert e.amount == 50 and b"Not enough AP" in resp.content


def test_burning_damage_and_extinguish(char):
    client, c = char
    max_hp = c.compute().max_hp
    max_ap = fight(client, c)
    e = add(client, c, "burning-2")
    play(client, c, "fight-end-turn")
    assert c.current_hp == max_hp - 4
    assert e.amount == 4  # AP still needed to extinguish, spendable over several turns
    play(client, c, "effect-pay", id=e.pk, ap="1")
    e.refresh_from_db()
    assert e.active and e.amount == 3 and c.fight["ap"] == max_ap - 1
    play(client, c, "fight-end-turn")
    play(client, c, "effect-pay", id=e.pk, ap="3")
    e.refresh_from_db()
    assert not e.active and c.fight["ap"] == max_ap - 3


def test_radiation_burns_decay_and_renew(char):
    client, c = char
    max_hp = c.compute().max_hp
    fight(client, c)
    e = add(client, c, "radiation-burns", 2)
    play(client, c, "fight-end-turn")  # not at refresh: at the start of the next turn
    assert c.current_hp in (None, max_hp)
    play(client, c, "fight-turn")
    e.refresh_from_db()
    assert c.current_hp == max_hp - 2 and e.amount == 1
    add(client, c, "radiation-burns", 3)  # a new hit renews it
    e.refresh_from_db()
    assert e.amount == 3
    for _ in range(3):
        play(client, c, "fight-end-turn")
        play(client, c, "fight-turn")
    e.refresh_from_db()
    assert not e.active and c.current_hp == max_hp - 2 - 6 and c.wounds_taken == 0


def test_stunned_takes_ap_and_ends_at_refresh(char):
    client, c = char
    max_ap = fight(client, c)
    e = add(client, c, "stunned", 2)
    assert c.fight["ap"] == max_ap - 2 and e.amount == 2
    play(client, c, "fight-end-turn")
    e.refresh_from_db()
    assert not e.active and c.fight["ap"] == max_ap


def test_neck_bleeding_one_wound_per_turn(char):
    client, c = char
    fight(client, c)
    play(client, c, "effect-add", kind="called", location="4", which="wound", amount="2")
    e = EffectEntry.objects.get(key="wound:neck")
    play(client, c, "fight-end-turn")
    play(client, c, "fight-end-turn")
    play(client, c, "fight-end-turn")
    e.refresh_from_db()
    assert c.wounds_taken == 2 and not e.active


def test_fixed_cost_removal_and_bandage(char):
    client, c = char
    max_ap = fight(client, c)
    e = add(client, c, "prone")
    play(client, c, "effect-pay", id=e.pk)
    e.refresh_from_db()
    assert not e.active and c.fight["ap"] == max_ap - 1
    irr = add(client, c, "irradiated", 3)
    assert irr.pay_cost == 3
    assert add(client, c, "highly-irradiated-1", 9).pay_cost == 4  # 1–4 AP by marque
    play(client, c, "effect-add", kind="called", location="11", which="fatal")
    leg = EffectEntry.objects.get(key="fatal:leg")
    assert leg.amount == 1 and leg.pay_cost == 3
    play(client, c, "fight-end-turn")  # a fresh pool for the 3 AP
    play(client, c, "effect-pay", id=leg.pk)
    leg.refresh_from_db()
    assert leg.active and leg.amount == 0 and leg.pay_cost == 0  # timer stopped, the lost limb stays
    play(client, c, "effect-remove", id=irr.pk)  # plain remove still works
    irr.refresh_from_db()
    assert not irr.active


def test_undo_restores_amount(char):
    client, c = char
    e = add(client, c, "bleeding", 12)
    play(client, c, "effect-pay", id=e.pk, ap="1")
    actionlog.undo(None, actionlog.last_entry(c))
    e.refresh_from_db()
    assert e.amount == 12
    play(client, c, "effect-pay", id=e.pk, ap="3")
    actionlog.undo(None, actionlog.last_entry(c))
    e.refresh_from_db()
    assert e.active and e.amount == 12


def test_export_import_carries_amount(char):
    client, c = char
    add(client, c, "bleeding", 9)
    data = transfer.export_character(c)
    assert data["effects"][0]["amount"] == 9
    copy = transfer.import_character(data, "Ada 2", "password1")
    assert copy.effects.get().amount == 9
