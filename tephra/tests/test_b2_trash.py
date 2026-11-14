"""b2-trash: trash (S3), export/import + snapshots (S4), duplicate (C14), abandoned drafts (N3), level history (C3/C15)."""
import io
import json
import random
from datetime import timedelta

import pytest
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone

from catalog.models import ItemTemplate
from characters import services, transfer, trash
from characters.models import (Automaton, Character, CharacterSnapshot, CustomModifier, EffectEntry, InventoryItem,
                               LevelLog, Pet)
from wiki.models import WikiPage, WikiRevision

PW = "longpassword"


@pytest.fixture(autouse=True)
def catalog(db):
    call_command("seed_catalog", stdout=io.StringIO())


def finished(seed=3, name="Ada"):
    c = Character.objects.create(name=name)
    services.random_all(c, random.Random(seed))
    c.set_password(PW)
    services.finish_creation(c)
    return c


def upload(data, name="c.json"):
    from django.core.files.uploadedfile import SimpleUploadedFile
    raw = data if isinstance(data, bytes) else json.dumps(data).encode()
    return SimpleUploadedFile(name, raw, content_type="application/json")


# --------------------------------------------------------------------------- S3 trash
def test_deleted_character_goes_to_trash_and_is_hidden(admin_client, client, db):
    c = finished()
    admin_client.post(reverse("delete_character", args=[c.pk]))
    assert not Character.objects.filter(pk=c.pk).exists()
    assert Character.all_objects.get(pk=c.pk).deleted_at
    assert c.name not in client.get("/").content.decode()
    assert client.get(reverse("unlock", args=[c.pk])).status_code == 404
    assert admin_client.get(reverse("sheet", args=[c.pk])).status_code == 404
    gm = admin_client.get(reverse("gm_settings")).content.decode()
    assert "Trash" in gm and c.name in gm
    admin_client.post(reverse("gm_trash", args=["character", c.pk]), {"action": "restore"})
    assert Character.objects.filter(pk=c.pk).exists()


def test_wiki_trash_keeps_revisions_and_slug(admin_client, db):
    p = WikiPage.objects.create(slug="lore", title="Lore", body="x")
    WikiRevision.objects.create(page=p, title="Lore", body="old")
    admin_client.post(reverse("wiki_edit", args=["lore"]), {"delete": "1"})
    assert not WikiPage.objects.filter(slug="lore").exists()
    assert WikiRevision.objects.filter(page=p).count() == 1
    assert admin_client.get(reverse("wiki_page", args=["lore"])).status_code == 404
    # A new page with the same title gets another slug instead of hitting the unique constraint.
    admin_client.post(reverse("wiki_new"), {"title": "Lore", "body": "new"})
    assert WikiPage.objects.get(title="Lore").slug == "lore-2"
    admin_client.post(reverse("gm_trash", args=["wiki", p.pk]), {"action": "purge"})
    assert not WikiPage.all_objects.filter(pk=p.pk).exists()


def test_custom_catalog_item_goes_to_trash(admin_client, db):
    item = ItemTemplate.objects.create(name="Odd Spoon", kind="general", source="custom")
    admin_client.post(reverse("item_edit", args=[item.pk]), {"delete": "1"})
    item.refresh_from_db()
    assert item.deleted_at and not ItemTemplate.offered().filter(pk=item.pk).exists()
    assert [e["obj"] for e in trash.entries()] == [item]


def test_purge_trash_after_30_days(db):
    old, new = finished(name="Old"), finished(name="New")
    book = ItemTemplate.objects.create(name="Book Thing", kind="general", source="book")
    long_ago = timezone.now() - timedelta(days=31)
    Character.objects.filter(pk=old.pk).update(deleted_at=long_ago)
    Character.objects.filter(pk=new.pk).update(deleted_at=timezone.now())
    ItemTemplate.objects.filter(pk=book.pk).update(deleted_at=long_ago)
    call_command("purge_trash", stdout=io.StringIO())
    assert not Character.all_objects.filter(pk=old.pk).exists()
    assert not LevelLog.objects.filter(character_id=old.pk).exists()
    assert Character.all_objects.filter(pk=new.pk).exists()
    assert ItemTemplate.objects.filter(pk=book.pk).exists()  # hidden book items never leave (seed would re-add)


# --------------------------------------------------------------------------- N3 abandoned drafts
def test_abandoned_drafts_to_trash(admin_client, db):
    old, fresh, active = Character.objects.create(), Character.objects.create(), finished()
    stale = timezone.now() - timedelta(days=31)
    Character.objects.filter(pk__in=[old.pk, active.pk]).update(updated=stale)
    assert "Move 1 abandoned draft(s)" in admin_client.get(reverse("gm_settings")).content.decode()
    admin_client.post(reverse("gm_drafts_to_trash"))
    assert set(Character.objects.values_list("pk", flat=True)) == {fresh.pk, active.pk}


# --------------------------------------------------------------------------- S4 export/import, C14
def full_character():
    c = finished()
    sword = InventoryItem.objects.create(character=c, name="Saber", kind="melee", slot="weapon1")
    EffectEntry.objects.create(character=c, kind="status", text="Dazed")
    CustomModifier.objects.create(character=c, source="Story: X", stat="acc", value=1)
    Pet.objects.create(character=c, name="Rex", template="medium-land")
    Automaton.objects.create(character=c, name="Tin", weapon=sword)
    c.story_notes = "# Day 1\nWe met."
    c.save()
    return c


def test_export_import_round_trip(admin_client, db):
    c = full_character()
    data = json.loads(admin_client.get(reverse("export_character", args=[c.pk])).content)
    assert "password" not in data["character"]
    resp = admin_client.post(reverse("gm_import"), {"file": upload(data), "name": "Ada II", "password": PW})
    new = Character.objects.get(name="Ada II")
    assert resp.status_code == 302 and new.pk != c.pk and new.check_password(PW)
    assert new.story_notes == c.story_notes and new.specialties == c.specialties and new.skills == c.skills
    names = sorted(c.items.values_list("name", flat=True))
    assert sorted(new.items.values_list("name", flat=True)) == names and "Saber" in names
    assert new.automatons.get().weapon == new.items.get(name="Saber")
    assert new.effects.count() == new.custom_modifiers.count() == new.pets.count() == 1
    assert abs(new.level_logs.get().created - c.level_logs.get().created) < timedelta(milliseconds=1)  # JSON: ms
    assert Character.objects.get(pk=c.pk).name == "Ada"  # original untouched


@pytest.mark.parametrize("mutate, message", [
    (lambda d: d.update(evil=1), "Unknown keys"),
    (lambda d: d["character"].update(is_staff=True), "unknown fields"),
    (lambda d: d["character"].update(specialties=[["no-such-specialty", 1]]), "no-such-specialty"),
    (lambda d: d["character"].update(race="martian"), "martian"),
    (lambda d: d["character"].update(level="many"), "level"),
    (lambda d: d["items"].append({"name": "x" * 500}), "items 1"),
    (lambda d: d.update(format="other"), "not a TephraSheet"),
])
def test_import_validates_strictly(admin_client, db, mutate, message):
    data = transfer.export_character(finished())
    mutate(data)
    before = Character.all_objects.count()
    with pytest.raises(transfer.TransferError) as err:
        transfer.import_character(data, "X", PW)
    assert message in str(err.value)
    assert Character.all_objects.count() == before


def test_duplicate_remaps_id_based_toggle_keys(db):
    c = full_character()
    cm = c.custom_modifiers.get()
    sword = c.items.get(name="Saber")
    c.toggles = [f"custom:{cm.pk}", f"item:{sword.pk}", f"item:{sword.pk}:aug:x", "custom:99999", "spec:foo"]
    c.save()
    twin = transfer.duplicate_character(c, "Twin", PW)
    new_cm, new_sword = twin.custom_modifiers.get(), twin.items.get(name="Saber")
    assert twin.toggles == [f"custom:{new_cm.pk}", f"item:{new_sword.pk}", f"item:{new_sword.pk}:aug:x", "spec:foo"]
    assert new_cm.as_modifier()["key"] in twin.toggles


@pytest.mark.parametrize("field, value", [
    ("fight", ["bad"]), ("fight", {"ap": "3"}), ("plan", [{"level": "x"}]), ("plan", ["bad"]),
    ("toggles", {"a": 1}), ("toggles", [1]), ("skills", {"Brute": "2"}), ("misc", []),
    ("specialty_choices", {"x": 1}), ("narrator_granted", "spec:x"), ("trait_rolls", {}),
])
def test_import_validates_json_field_shapes(db, field, value):
    data = transfer.export_character(finished())
    data["character"][field] = value
    with pytest.raises(transfer.TransferError, match=field):
        transfer.import_character(data, "X", PW)


def test_import_validates_child_json_fields_and_ids(db):
    data = transfer.export_character(full_character())
    data["pets"][0]["traits"] = {"a": 1}
    data["items"][0]["id"] = "1"
    with pytest.raises(transfer.TransferError) as err:
        transfer.import_character(data, "X", PW)
    assert "traits" in str(err.value) and "id" in str(err.value)


def test_import_refuses_big_file_and_short_password(admin_client, db):
    data = transfer.export_character(finished())
    with pytest.raises(transfer.TransferError):
        transfer.import_character(data, "X", "short")
    big = upload(b" " * (transfer.MAX_BYTES + 1))
    with pytest.raises(transfer.TransferError, match="too big"):
        transfer.parse_upload(big)
    assert admin_client.post(reverse("gm_import"), {"file": upload(b"{nope"), "password": PW}).status_code == 302


def test_import_needs_narrator(client, db):
    data = transfer.export_character(finished())
    client.post(reverse("gm_import"), {"file": upload(data), "name": "Sneaky", "password": PW})
    assert not Character.objects.filter(name="Sneaky").exists()


def test_export_needs_unlock(client, db):
    c = finished()
    assert client.get(reverse("export_character", args=[c.pk])).status_code == 302
    client.post(reverse("unlock", args=[c.pk]), {"password": PW})
    resp = client.get(reverse("export_character", args=[c.pk]))
    assert resp.status_code == 200 and "attachment" in resp["Content-Disposition"]


def test_duplicate_copies_everything(admin_client, db):
    c = full_character()
    admin_client.post(reverse("gm_duplicate", args=[c.pk]), {"name": "Twin", "password": PW})
    twin = Character.objects.get(name="Twin")
    assert twin.items.count() == c.items.count() and twin.automatons.count() == twin.pets.count() == 1 and twin.level_logs.count() == 1
    assert twin.check_password(PW) and not twin.check_password("other")


# --------------------------------------------------------------------------- S4 snapshots
def test_snapshot_before_each_levelup_keeps_ten(admin_client, db):
    c = finished()
    services.random_levelup(c, random.Random(1), from_xp=False)
    snap = CharacterSnapshot.objects.get(character=c)
    assert snap.level == 1 and snap.data["character"]["level"] == 1
    resp = admin_client.get(reverse("gm_snapshot", args=[snap.pk]))
    assert json.loads(resp.content)["character"]["level"] == 1
    for _n in range(CharacterSnapshot.KEEP + 1):
        CharacterSnapshot.record(c, transfer.export_character(c))
    assert c.snapshots.count() == CharacterSnapshot.KEEP


def test_failed_levelup_stores_no_snapshot(db):
    c = finished()
    assert services.apply_levelup(c, {}, "no-such-specialty")
    assert not CharacterSnapshot.objects.exists()


# --------------------------------------------------------------------------- C3/C15 level history
def test_level_history_on_story_tab_and_print(admin_client, db):
    c = finished()
    services.random_levelup(c, random.Random(1), from_xp=False)
    html = admin_client.get(reverse("sheet", args=[c.pk]) + "?tab=story").content.decode()
    assert "Level history" in html and "print-history" in html and "Print with level history" in html
    log = c.level_logs.get(level=2)
    from rules.registry import get_registry
    assert get_registry().specialties[log.data["specialty"]]["name"] in html
