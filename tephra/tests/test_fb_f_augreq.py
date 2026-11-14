"""Package F: augment requirements on the item (GAP 1) and item restrictions (GAP 2)."""
import json
from io import StringIO

import pytest
from django.core.management import call_command
from django.urls import reverse

from catalog.forms import ItemForm
from catalog.importer import parse_rows
from catalog.models import ItemTemplate
from characters import transfer
from characters.models import Character, InventoryItem
from rules.engine.item_requirements import problems
from rules.engine.requirements import _augments_by_name, check_augment
from rules.lang import get_language
from rules.registry import get_registry

PW = "longpassword"
SIG, CUSTOM = "armsmith-melee-signature-weapon", "armsmith-melee-custom"


def item(augs, **kw):
    return {"kind": "melee", "size": "medium", "material": "metal", "variants": [], "ap_ready": None,
            "augments": [[s, 1] for s in augs], **kw}


def test_learning_signature_weapon_without_custom(db):
    c = Character.objects.create(race="human", skills={"Armsmith": 4}, specialties=[["armsmith-weapon-smith", 1]])
    ok, reasons = check_augment(get_registry().augments[SIG], c.to_state(), c.compute())
    assert ok, reasons


def test_extended_blast_needs_marque_two(db):
    aug = get_registry().augments["gadgetry-explosive-extended-blast"]
    c = Character.objects.create(race="human", skills={"Gadgetry": 2}, specialties=[["gadgetry-pyrotechnician", 1]])
    assert check_augment(aug, c.to_state(), c.compute())[1] == ["needs marque II in Gadgetry"]
    c.skills = {"Gadgetry": 5}
    c.save()
    assert check_augment(aug, c.to_state(), c.compute())[0]


def test_every_req_qualifier_is_classified():
    """A "req." qualifier is either an item condition / special learning rule or names a specialty or augment."""
    reg = get_registry()
    names = {s["name_en"] for s in reg.specialties.values()} | set(_augments_by_name(get_language()))
    for aug in reg.augments.values():
        done = {*(aug.get("item") or {}).get("from", []), *aug.get("learn_from", [])}
        for q in aug["qualifiers_en"]:
            if q.startswith("req. ") and q not in done:
                assert all(n in names for n in q[5:].split(" or ")), (aug["slug"], q)


def test_predicates():
    assert problems(item([SIG])) == ["Signature Weapon: needs Custom on the same item"]
    assert problems(item([CUSTOM, SIG])) == problems(item([SIG, CUSTOM])) == []  # order doesn't matter
    assert problems(item([SIG], variants=["aether"])) == []  # aether-shaped: no Custom needed
    assert problems(item([SIG], variants=["synced"]))  # aether-synced is not shaped
    assert problems(item([SIG], house_rule=True)) == []
    assert problems(item(["armsmith-melee-gnome-sized"], size="light")) == []
    assert problems(item(["armsmith-melee-gnome-sized"])) == ["Gnome-Sized: needs a Light item"]
    assert problems(item(["armsmith-melee-streamlined"])) == []
    assert problems(item(["armsmith-melee-streamlined"], size="heavy"))
    assert problems(item(["armsmith-melee-tangling"])) and not problems(item(["armsmith-melee-tangling"],
                                                                              variants=["flexible"]))
    assert problems(item(["armsmith-melee-returning"]))
    assert not problems(item(["armsmith-melee-returning"], variants=["throwing"]))
    assert not problems(item(["armsmith-melee-returning", "armsmith-melee-aerodynamic"]))  # converted to throwing
    # AND of two groups / OR inside a group
    turret = "armsmith-turret-"
    assert len(problems(item([turret + "devastatingly-accurate"], kind="firearm"))) == 2
    assert not problems(item([turret + s for s in ("automated", "deadly-accurate", "devastatingly-accurate")],
                             kind="firearm"))
    assert problems(item(["gadgetry-explosive-clinging"], kind="gear"))
    assert not problems(item(["gadgetry-explosive-clinging", "gadgetry-explosive-roaming"], kind="gear"))
    # reload: size table (heavy firearm: 1 AP) or the item's own value
    rb = ["armsmith-firearm-rotating-barrels"]
    assert not problems(item(rb, kind="firearm", size="heavy"))
    assert problems(item(rb, kind="firearm", size="heavy", ap_ready=3))
    assert problems(item(["armsmith-munition-split-shot", "armsmith-munition-syringed"], kind="ammo"))


def test_install_notes_shown_when_learning():
    from rules.engine.item_requirements import install_notes
    assert install_notes(get_registry().augments[SIG]) == ["Requires Custom on the item when installed."]


def _form(augs, instance=None, **extra):
    data = {"name": "Sabre", "kind": "melee", "size": "medium", "material": "metal", "deflect_melee": "on",
            "augments_json": json.dumps([[s, 1] for s in augs]), **extra}
    return ItemForm(data, instance=instance)


@pytest.mark.django_db
def test_form_refuses_forged_configurations():
    assert not _form([SIG]).is_valid()
    assert _form([CUSTOM, SIG]).is_valid()
    assert not _form(["armsmith-melee-gnome-sized"]).is_valid()
    assert _form(["armsmith-melee-gnome-sized"], size="light").is_valid()
    assert not _form(["armsmith-melee-tangling"]).is_valid()
    assert _form(["armsmith-melee-tangling"], variants=["flexible"]).is_valid()
    assert _form([SIG], house_rule="on").is_valid()
    for bad in ('[["no-such-augment", 1]]', '[["armsmith-melee-custom", 9]]', '{"a": 1}', '[["armsmith-melee-custom"]]'):
        assert not ItemForm({"name": "X", "kind": "melee", "augments_json": bad, "house_rule": "on"}).is_valid(), bad


@pytest.mark.django_db
def test_changing_a_saved_item_rechecks_but_legacy_items_keep_unrelated_edits():
    good = ItemTemplate.objects.create(name="Blade", kind="melee", size="medium", augments=[[CUSTOM, 1], [SIG, 1]])
    assert not _form([SIG], instance=good, name="Blade").is_valid()  # removing Custom flags Signature Weapon
    gnome = ItemTemplate.objects.create(name="Tiny", kind="melee", size="light", augments=[["armsmith-melee-gnome-sized", 1]])
    assert not _form(["armsmith-melee-gnome-sized"], instance=gnome, name="Tiny", size="heavy").is_valid()
    legacy = ItemTemplate.objects.create(name="Old", kind="melee", size="medium", augments=[[SIG, 1]])
    assert legacy.augment_problems
    form = _form([SIG], instance=legacy, name="Old", description="still mine")
    assert form.is_valid(), form.errors  # nothing that decides the fit changed
    form.save()
    assert ItemTemplate.objects.get(pk=legacy.pk).description == "still mine"


def test_csv_import_checks_item_conditions():
    rows = parse_rows("name,kind,size,augments\nBlade,melee,medium,Signature Weapon\nOk,melee,medium,Custom;Signature Weapon\n")
    assert any("Custom" in e for e in rows[0]["errors"])
    assert not rows[1]["errors"]


@pytest.mark.django_db
def test_character_import_refuses_bad_items_and_duplicate_keeps_them():
    c = Character.objects.create(name="A", race="human")
    InventoryItem.objects.create(character=c, name="Old", kind="melee", size="medium", augments=[[SIG, 1]])
    data = transfer.export_character(c)
    with pytest.raises(transfer.TransferError) as exc:
        transfer.import_character(data, "B", PW)
    assert any("Signature Weapon" in e for e in exc.value.errors)
    twin = transfer.duplicate_character(c, "Twin", PW)
    assert InventoryItem.objects.get(character=twin).augment_problems


@pytest.mark.django_db
def test_picker_check_agrees_with_the_form(client):
    url = reverse("augment_check")
    base = {"kind": "melee", "size": "medium", "material": "metal"}
    r = client.post(url, {**base, "augments_json": json.dumps([[SIG, 1]])}).json()
    assert r["selected"][SIG] == "needs Custom on the same item"
    assert "armsmith-melee-tangling" in r["options"] and CUSTOM not in r["options"]
    r = client.post(url, {**base, "variants": ["flexible"], "augments_json": "[]"}).json()
    assert "armsmith-melee-tangling" not in r["options"]
    assert client.post(url, {**base, "house_rule": "on", "augments_json": json.dumps([[SIG, 1]])}).json()["selected"] == {}


@pytest.mark.django_db
def test_warning_badge_and_audit_command(client):
    ItemTemplate.objects.create(name="Old", kind="melee", size="medium", augments=[[SIG, 1]], source="custom")
    assert "does not meet" in client.get(reverse("catalog") + "?q=Old").content.decode()
    out = StringIO()
    call_command("audit_item_augments", stdout=out)
    assert "catalog" in out.getvalue() and "Signature Weapon: needs Custom" in out.getvalue()
