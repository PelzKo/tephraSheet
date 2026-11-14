"""Package I: Stunned outside fight mode, clean Burn Trail slug, aether limit always 3, Rotating Barrels counts the
item's own augments, inventory turrets need the owner's Automata point."""
import json
from importlib import import_module

import pytest
from django.apps import apps
from django.urls import reverse

from catalog.models import ItemTemplate
from characters import transfer
from characters.models import Character, EffectEntry, InventoryItem
from rules.engine.item_requirements import problems
from rules.registry import get_registry

from .test_fb_e_effects import char, play  # noqa: F401  (fixture)

OLD, NEW = "armsmith-bow-burn-trail-everburning", "armsmith-bow-burn-trail"
AUTO, BELT = "armsmith-turret-automated", "armsmith-turret-belt-fed"
RB, RELOAD = "armsmith-firearm-rotating-barrels", "armsmith-firearm-crossbow-automatic-reload"


def test_stunned_outside_fight_adds_nothing(char):  # noqa: F811
    client, c = char
    resp = play(client, c, "effect-add", kind="status", key="status:stunned", amount="2")
    assert b"only has an effect in fight mode" in resp.content
    assert not EffectEntry.objects.filter(key="status:stunned").exists()


def test_burn_trail_has_a_clean_slug_and_the_old_one_resolves():
    reg = get_registry()
    assert reg.augments[NEW]["name"] == "Burn Trail" and NEW in reg.augments
    assert reg.augments[OLD] is reg.augments[NEW] and OLD in reg.augments and reg.augments.get(OLD) is not None
    assert [s for s in reg.augments if s == OLD] == []  # not listed twice in pickers
    assert problems({"kind": "bow", "augments": [[OLD, 1]]}) == problems({"kind": "bow", "augments": [[NEW, 1]]})


def test_burn_trail_german_follows_the_new_slug():
    from rules.lang import set_language

    set_language("de")
    try:
        assert get_registry().augments[NEW]["name"] == "Brandspur"
    finally:
        set_language("en")


@pytest.mark.django_db
def test_import_normalises_the_old_slug():
    c = Character.objects.create(name="Old", augments=[NEW])
    InventoryItem.objects.create(character=c, name="Bow", kind="bow", augments=[["armsmith-bow-combustion", 1], [NEW, 1]])
    data = json.loads(json.dumps(transfer.export_character(c)).replace(NEW, OLD))
    new = transfer.import_character(data, "Copy", "password123")
    assert new.augments == [NEW] and new.items.get().augments[1] == [NEW, 1]


@pytest.mark.django_db
def test_migration_remaps_the_old_slug():
    mig = import_module("characters.migrations.0031_burn_trail_slug")
    c = Character.objects.create(augments=[OLD], narrator_granted=[f"aug:{OLD}"],
                                 plan=[{"level": 2, "type": "augment", "augments": [OLD]}])
    InventoryItem.objects.create(character=c, name="Bow", kind="bow", augments=[[OLD, 2]])
    t = ItemTemplate.objects.create(name="Old bow", kind="bow", augments=[[OLD, 1]])
    mig.forward(apps, None)
    c.refresh_from_db()
    t.refresh_from_db()
    assert c.augments == [NEW] and c.narrator_granted == [f"aug:{NEW}"] and c.plan[0]["augments"] == [NEW]
    assert c.items.get().augments == [[NEW, 2]] and t.augments == [[NEW, 1]]
    mig.backward(apps, None)
    c.refresh_from_db()
    assert c.augments == [OLD] and c.narrator_granted == [f"aug:{OLD}"]


def aether(augs, **kw):
    return {"kind": "melee", "size": "medium", "variants": ["aether"], "augments": [[s, 1] for s in augs], **kw}


def test_aether_limit_is_three_even_with_beta():
    four = ["armsmith-melee-accurate", "armsmith-melee-damaging", "armsmith-melee-powerful", "armsmith-melee-reach"]
    assert problems(aether(four, beta=True)) == ["An aether-shaped weapon takes at most 3 augments."]
    assert not problems(aether(four, beta=True, house_rule=True))


def test_rotating_barrels_counts_the_items_own_augments():
    gun = {"kind": "firearm", "size": "medium", "ap_ready": 3}
    assert problems({**gun, "augments": [[RB, 1]]}) == ["Rotating Barrels: needs at most 2 AP to ready (has 3)"]
    assert not problems({**gun, "augments": [[RB, 1], [RELOAD, 1]]})  # Automatic Reload: 1 less


def turret(augs):
    return {"name": "Turret", "kind": "firearm", "size": "super-heavy", "variants": ["turret"], "ap_ready": 0,
            "augments": augs}


def test_turret_owner_needs_an_automata_point():
    assert not problems(turret([[AUTO, 1]]))  # catalog template: no owner
    assert problems(turret([[AUTO, 1]]), owner={}) == ["Automated: needs 1 points in Automata (has 0)"]
    assert not problems(turret([[AUTO, 1]]), owner={"Automata": 1})
    assert not problems({**turret([[AUTO, 1]]), "house_rule": True}, owner={})


@pytest.mark.django_db
def test_inventory_turret_owner_check_paths(client):
    client.post(reverse("character_new"))
    c = Character.objects.get()
    inv = InventoryItem.objects.create(character=c, **turret([[AUTO, 1]]))
    assert inv.augment_problems == ["Automated: needs 1 points in Automata (has 0)"]  # sheet, admin, audit
    t = ItemTemplate.objects.create(source="custom", **turret([[AUTO, 1]]))
    assert not t.augment_problems
    resp = client.post(reverse("add_to_inventory", args=[t.pk]), {"for": c.pk})
    assert b"Automata" in resp.content and c.items.count() == 1  # asks first
    data = transfer.export_character(c)
    with pytest.raises(transfer.TransferError, match="Automata"):
        transfer.import_character(data, "Copy", "password123")
    c.skills = {"Automata": 1}
    c.save()
    assert not InventoryItem.objects.get(pk=inv.pk).augment_problems


@pytest.mark.django_db
def test_item_form_checks_the_owner():
    from catalog.forms import ItemForm
    from rules import extensions

    extensions.set_offer(["armsmith-extra"])  # turrets
    try:
        data = {"name": "T", "kind": "firearm", "size": "super-heavy", "material": "metal", "variants": ["turret"],
                "ap_ready": "0", "augments_json": json.dumps([[AUTO, 1]])}
        assert ItemForm(data).is_valid()
        form = ItemForm(data, owner={})
        assert not form.is_valid() and "Automata" in str(form.non_field_errors())
        assert ItemForm(data, owner={"Automata": 2}).is_valid()
    finally:
        extensions.set_offer()
