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
                             kind="firearm", ap_ready=0))
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


def _import(client, text):
    rows = client.post(reverse("catalog_import"), {"action": "preview", "text": text}).context["rows"]
    client.post(reverse("catalog_import"), {"action": "commit", "target": "catalog"})
    return rows


@pytest.mark.django_db
def test_csv_update_rows_are_checked_merged_with_the_existing_item(client):
    tiny = ItemTemplate.objects.create(name="Tiny", kind="melee", size="light", source="custom")
    rows = _import(client, "name,kind,augments\nTiny,melee,Gnome-Sized\n")  # size only on the saved item
    assert rows[0]["status"] == "update", rows[0]["errors"]
    tiny.refresh_from_db()
    assert tiny.augments == [["armsmith-melee-gnome-sized", 1]]
    rows = _import(client, "name,kind,size\nTiny,melee,heavy\n")  # leaves Gnome-Sized on a heavy item
    assert rows[0]["status"] == "error" and any("Gnome-Sized" in e for e in rows[0]["errors"])
    assert ItemTemplate.objects.get(pk=tiny.pk).size == "light"
    legacy = ItemTemplate.objects.create(name="Old", kind="melee", size="medium", augments=[[SIG, 1]], source="custom")
    assert _import(client, "name,kind,description\nOld,melee,still mine\n")[0]["status"] == "update"
    assert ItemTemplate.objects.get(pk=legacy.pk).description == "still mine"
    house = ItemTemplate.objects.create(name="House", kind="melee", size="light", house_rule=True, source="custom",
                                        augments=[["armsmith-melee-gnome-sized", 1]])
    assert _import(client, "name,kind,size\nHouse,melee,heavy\n")[0]["status"] == "update"
    assert ItemTemplate.objects.get(pk=house.pk).size == "heavy"


@pytest.mark.django_db
def test_import_parser_errors_never_reach_the_catalog_lookup(client):
    for text in ("kind,size\nmelee,medium\n", "name,kind\n,melee\nX,laser\n"):  # no name column; blank name, bad kind
        rows = _import(client, text)
        assert rows and all(r["status"] == "error" and r["errors"] for r in rows)
    assert not ItemTemplate.objects.exists()


@pytest.mark.django_db
def test_character_preview_keeps_valid_catalog_updates_importable(client):
    ItemTemplate.objects.create(name="Tiny", kind="melee", size="light", source="custom")
    client.post(reverse("character_new"))
    c = Character.objects.get()
    url = reverse("catalog_import") + f"?for={c.pk}"
    text = "name,kind,augments\nTiny,melee,Gnome-Sized\n"  # fails as a new item (no size), fine merged with Tiny
    resp = client.post(url, {"action": "preview", "text": text})
    assert resp.context["rows"][0]["errors"] and resp.context["rows"][0]["status"] == "update"
    assert 'name="action" value="commit"' in resp.content.decode()
    client.post(url, {"action": "commit", "target": "inventory"})
    assert not InventoryItem.objects.filter(character=c).exists()  # inventory still refuses it as a new item
    client.post(url, {"action": "preview", "text": text})
    client.post(url, {"action": "commit", "target": "catalog"})
    assert ItemTemplate.objects.get(name="Tiny").augments == [["armsmith-melee-gnome-sized", 1]]
