"""Package H: follow-ups to the augment requirements (Automated, Fumble, bow Burn Trail/Everburning, aether-shaped
weapons, confirmation before copying a rule-breaking template, admin confirmation)."""
import json

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from catalog.models import ItemTemplate
from characters import services
from characters.models import Character, InventoryItem
from rules.engine.item_requirements import item_ready, problems
from rules.engine.requirements import check_augment
from rules.registry import get_registry

AUTO, BELT = "armsmith-turret-automated", "armsmith-turret-belt-fed"
SIG, CUSTOM = "armsmith-melee-signature-weapon", "armsmith-melee-custom"


def turret(augs, **kw):
    return {"kind": "firearm", "size": "super-heavy", "variants": ["turret"], "ap_ready": 2, "augments": augs, **kw}


def test_automated_needs_a_turret_with_zero_ready():
    assert problems(turret([[AUTO, 1]])) == ["Automated: needs at most 0 AP to ready (has 2)"]
    assert problems(turret([[AUTO, 1], [BELT, 1]]))  # Belt Fed mQ I: 1 AP left
    assert not problems(turret([[AUTO, 1], [BELT, 3]]))  # mQ III: −2
    reload = "armsmith-firearm-crossbow-automatic-reload"
    assert item_ready(turret([[reload, 1], [BELT, 1]])) == 0  # Automatic Reload: "1 less AP to reload"
    assert not problems(turret([[AUTO, 1], [reload, 3]]))


def test_automated_needs_an_automata_point_to_learn(db):
    aug = get_registry().augments[AUTO]
    c = Character.objects.create(race="human", skills={"Armsmith": 4},
                                 specialties=[["armsmith-gunsmith", 1], ["armsmith-turret-builder", 1]])
    assert "needs 1 points in Automata (has 0)" in check_augment(aug, c.to_state(), c.compute())[1]
    c.skills = {"Armsmith": 4, "Automata": 1}
    c.save()
    assert "needs 1 points in Automata (has 0)" not in check_augment(aug, c.to_state(), c.compute())[1]


def test_fumble_needs_hand_slip_on_the_same_memento(db):
    fumble, slip = "luck-memento-fumble", "luck-memento-hand-slip"
    assert problems({"kind": "gear", "memento": True, "augments": [[fumble, 1]]}) == \
        ["Fumble: needs Hand Slip on the same item"]
    assert not problems({"kind": "gear", "memento": True, "augments": [[slip, 1], [fumble, 1]]})
    c = Character.objects.create(race="human", skills={"Luck": 4}, specialties=[["luck-mementos", 1]])
    assert not any("Hand Slip" in r for r in check_augment(get_registry().augments[fumble], c.to_state(), c.compute())[1])


def test_living_liquid_requirements_are_on_the_same_liquid():
    for aug, needed in (("alchemy-living-liquid-defensive", "alchemy-living-liquid-interior-platelets"),
                        ("alchemy-living-liquid-lifting-liquid", "alchemy-living-liquid-lighter-than-air-liquid")):
        assert problems({"kind": "living-liquid", "augments": [[aug, 1]]})
        assert not problems({"kind": "living-liquid", "augments": [[needed, 1], [aug, 1]]})


def test_bare_requirements_without_items_stay_learning_requirements():
    reg = get_registry()
    for slug in ("alchemy-acid-thick-rust", "bio-flux-essence-metal-exoskeleton", "bio-flux-essence-osmote",
                 "bio-flux-animal-trait-hurl"):
        assert not reg.augments[slug].get("item"), slug


def test_bow_burn_trail_and_everburning_are_two_augments():
    reg = get_registry()
    burn, ever = reg.augments["armsmith-bow-burn-trail"], reg.augments["armsmith-bow-everburning"]
    assert burn["name"] == "Burn Trail" and "dexterity resist" in burn["text"]  # package I: clean slug
    assert ever["name"] == "Everburning" and "extra action points" in ever["text"]
    assert ever["marques"][3].startswith("+4")
    for slug in (burn["slug"], ever["slug"]):
        assert problems({"kind": "bow", "augments": [[slug, 1]]}) and \
            not problems({"kind": "bow", "augments": [["armsmith-bow-combustion", 1], [slug, 1]]})


def test_bow_burn_trail_german():
    from rules.lang import set_language

    set_language("de")
    try:
        reg = get_registry()
        assert reg.augments["armsmith-bow-burn-trail"]["name"] == "Brandspur"
        assert reg.augments["armsmith-bow-everburning"]["name"] == "Ewiges Feuer"
    finally:
        set_language("en")


def aether(augs, **kw):
    return {"kind": "melee", "size": "medium", "variants": ["aether"], "augments": [[s, 1] for s in augs], **kw}


def test_aether_shaped_weapons_take_listed_augments_only():
    assert problems(aether(["armsmith-melee-cryothermal"])) == \
        ["Cryothermal: not allowed on an aether-shaped weapon"]
    assert not problems(aether([SIG]))  # listed, no Custom needed
    assert not problems(aether(["armsmith-melee-cryothermal"], house_rule=True))  # Aetherform Modules
    assert not problems({**aether(["armsmith-melee-cryothermal"]), "variants": ["synced"]})
    four = ["armsmith-melee-accurate", "armsmith-melee-damaging", "armsmith-melee-powerful", "armsmith-melee-reach"]
    assert problems(aether(four)) == ["An aether-shaped weapon takes at most 3 augments."]
    assert problems(aether(four, beta=True))  # package I: 3 with beta too


@pytest.mark.django_db
def test_aether_limit_in_the_form_and_picker(client):
    from catalog.forms import ItemForm
    from characters.models import NarratorSettings
    from rules import extensions

    s = NarratorSettings.get()
    s.enabled_extensions = ["aether"]
    s.save()
    extensions.set_offer(["aether"])
    data = {"name": "Shaped", "kind": "melee", "size": "medium", "material": "metal", "variants": ["aether"],
            "augments_json": json.dumps([["armsmith-melee-cryothermal", 1]])}
    assert not ItemForm(data).is_valid()
    assert ItemForm({**data, "house_rule": "on"}).is_valid()
    r = client.post(reverse("augment_check"), {**data, "augments_json": "[]"}).json()
    assert "armsmith-melee-cryothermal" in r["options"] and "armsmith-melee-accurate" not in r["options"]
    # the count limit is in the picker too: 3 augments are full (beta or not)
    from rules.engine import tables
    full = [[a, 1] for a in list(tables.AETHER_SHAPED["augments"])[:3]]
    r = client.post(reverse("augment_check"), {**data, "augments_json": json.dumps(full)}).json()
    other = next(a for a in tables.AETHER_SHAPED["augments"] if a not in [f[0] for f in full])
    assert "at most 3" in r["options"].get(other, "")
    r = client.post(reverse("augment_check"), {**data, "beta": "on", "augments_json": json.dumps(full)}).json()
    assert "at most 3" in r["options"].get(other, "")
    extensions.set_offer()


@pytest.fixture
def owner(client):
    client.post(reverse("character_new"))
    return Character.objects.get()


@pytest.mark.django_db
def test_adding_a_rule_breaking_template_asks_first(client, owner):
    old = ItemTemplate.objects.create(name="Old", kind="melee", size="medium", augments=[[SIG, 1]], source="custom")
    url = reverse("add_to_inventory", args=[old.pk])
    resp = client.post(url, {"for": owner.pk, "quantity": "2", "slot": "carried"})
    body = resp.content.decode()
    assert "Do you really want to do that?" in body and "Signature Weapon: needs Custom" in body
    assert 'name="confirm" value="1"' in body and 'name="quantity" value="2"' in body
    assert not InventoryItem.objects.filter(character=owner).exists()
    client.post(url, {"for": owner.pk, "quantity": "2", "slot": "carried", "confirm": "1"})
    assert InventoryItem.objects.get(character=owner).quantity == 2
    ok = ItemTemplate.objects.create(name="Fine", kind="melee", size="medium", augments=[[CUSTOM, 1], [SIG, 1]])
    house = ItemTemplate.objects.create(name="House", kind="melee", size="medium", augments=[[SIG, 1]],
                                        house_rule=True)
    for t in (ok, house):
        client.post(reverse("add_to_inventory", args=[t.pk]), {"for": owner.pk})
        assert InventoryItem.objects.filter(character=owner, name=t.name).exists()


@pytest.fixture
def staff(client):
    user = User.objects.create_superuser("gm", "gm@example.com", "pw")
    client.force_login(user)
    return user


def _admin_item_data(**kw):
    t = ItemTemplate(name="Blade", kind="melee", size="medium")
    data = {f.name: getattr(t, f.name) for f in ItemTemplate._meta.fields if f.editable and f.name != "id"}
    data = {k: ("" if v is None else json.dumps(v) if isinstance(v, (list, dict)) else v) for k, v in data.items()}
    data = {k: v for k, v in data.items() if v is not False}
    return {**data, **kw}


@pytest.mark.django_db
def test_admin_item_save_needs_confirmation(client, staff):
    url = reverse("admin:catalog_itemtemplate_add")
    data = _admin_item_data(augments=json.dumps([[SIG, 1]]))
    resp = client.post(url, data)
    assert resp.status_code == 200 and "Do you really want to do that?" in resp.content.decode()
    assert not ItemTemplate.objects.filter(name="Blade").exists()
    assert client.post(url, {**data, "confirm_violations": "on"}).status_code == 302
    assert ItemTemplate.objects.get(name="Blade").augments == [[SIG, 1]]
    house = _admin_item_data(name="House", augments=json.dumps([[SIG, 1]]), house_rule="on")
    assert client.post(url, house).status_code == 302


@pytest.mark.django_db
def test_character_rule_violations(db):
    c = Character.objects.create(race="human", skills={"Armsmith": 4}, specialties=[["armsmith-weapon-smith", 1]],
                                 augments=[CUSTOM])
    assert services.rule_violations(c) == []
    c.skills = {}
    assert any(v.startswith("Weapon Smith:") for v in services.rule_violations(c))
    assert any(v.startswith("Custom:") for v in services.rule_violations(c))
    c.narrator_granted = ["spec:armsmith-weapon-smith", f"aug:{CUSTOM}"]
    assert services.rule_violations(c) == []


@pytest.mark.django_db
def test_random_characters_have_no_violations():
    from django.core.management import call_command

    for seed in (1, 2, 3):
        call_command("create_random_character", "--level", "4", "--seed", str(seed), stdout=open("/dev/null", "w"))
    for c in Character.objects.all():
        assert services.rule_violations(c) == [], (c.race, services.rule_violations(c))


@pytest.mark.django_db
def test_admin_character_save_needs_confirmation(client, staff):
    c = Character.objects.create(name="Lad", race="human", skills={}, specialties=[["armsmith-weapon-smith", 1]])
    page = client.get(reverse("admin:characters_character_change", args=[c.pk]))
    form = page.context["adminform"].form
    data = {k: ("" if v is None else json.dumps(v) if isinstance(v, (list, dict)) else v)
            for k, v in form.initial.items() if k in form.fields and v is not False and k != "portrait"}
    formsets = {}
    for fs in page.context["inline_admin_formsets"]:
        p = fs.formset.prefix
        formsets.update({f"{p}-TOTAL_FORMS": "0", f"{p}-INITIAL_FORMS": "0"})
    data.update(formsets, name="Lad2")
    url = reverse("admin:characters_character_change", args=[c.pk])
    resp = client.post(url, data)
    assert resp.status_code == 200 and "Weapon Smith" in resp.content.decode()
    assert Character.objects.get(pk=c.pk).name == "Lad"
    assert client.post(url, {**data, "confirm_violations": "on"}).status_code == 302
    assert Character.objects.get(pk=c.pk).name == "Lad2"
