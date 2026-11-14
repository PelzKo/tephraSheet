import io
import json
from datetime import timedelta

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from catalog.forms import ItemForm
from catalog.importer import parse_rows
from characters import trash, transfer
from characters.models import Character, InventoryItem
from rules.registry import get_registry

PW = "longpassword"


def _augs(lst, n):
    return [a["slug"] for a in get_registry().augments.values() if a["lists"] == [lst]][:n]


def _whip(augs, **extra):  # light organic whip: 1 augment slot
    return ItemForm({"name": "Whip", "kind": "melee", "size": "light", "material": "organic", "deflect_melee": "on",
                     "augments_json": json.dumps([[s, 1] for s in augs]), **extra}, catalog=False)


@pytest.mark.django_db
def test_house_rule_whip_takes_two_augments_and_firearm_augment():
    two_melee, fire = _augs("melee", 2), _augs("firearm", 1)
    assert not _whip(two_melee).is_valid()  # flag off: still refused
    assert not _whip(fire).is_valid()
    for augs in (two_melee, two_melee + fire):
        form = _whip(augs, house_rule="on")
        assert form.is_valid(), form.errors
        assert form.save(commit=False).house_rule


@pytest.mark.django_db
def test_house_rule_item_computes_and_other_items_stay_checked(client):
    client.post(reverse("character_new"))
    char = Character.objects.get()
    odd = _augs("melee", 2) + _augs("firearm", 1) + _augs("armor", 1)
    InventoryItem.objects.create(character=char, name="Whip", kind="melee", size="light", material="organic",
                                 slot="weapon1", augments=[[s, 4] for s in odd], house_rule=True)
    from rules.engine import stats
    stats.compute(char.to_state())  # unusual augment combos must not crash the engine
    assert client.get(char.get_absolute_url() + "?tab=inventory").status_code == 200
    # another item without the flag is still refused
    assert not _whip(_augs("melee", 2)).is_valid()


def test_import_house_rule_column_skips_kind_filter():
    fire = get_registry().augments[_augs("firearm", 1)[0]]["name_en"]
    rows = parse_rows(f"name,kind,augments,house_rule\nWhip,melee,{fire} I,yes\nStick,melee,{fire} I,no\n")
    assert not rows[0]["errors"] and rows[0]["values"]["house_rule"]
    assert rows[1]["errors"]


def _png(size=(900, 700), fmt="PNG"):
    buf = io.BytesIO()
    Image.new("RGB", size, "red").save(buf, fmt)
    return SimpleUploadedFile(f"me.{fmt.lower()}", buf.getvalue(), content_type="image/png")


@pytest.fixture
def char(client, db, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    c = Character.objects.create(name="Ada", status="active")
    c.set_password(PW)
    c.save()
    client.post(reverse("unlock", args=[c.pk]), {"password": PW})
    return c


def test_portrait_upload_resized_served_privately_and_removed(client, char, tmp_path):
    url = reverse("portrait", args=[char.pk])
    assert client.post(url, {"portrait": _png()}).status_code == 302
    char.refresh_from_db()
    path = tmp_path / char.portrait.name
    with Image.open(path) as img:
        assert img.format == "WEBP" and max(img.size) == 600 and not img.getexif()
    resp = client.get(url)
    assert resp.status_code == 200 and "private" in resp["Cache-Control"]
    assert "portrait" not in transfer.export_character(char)["character"]
    client.post(url, {"remove": "1"})
    char.refresh_from_db()
    assert not char.portrait and not path.exists()


def test_portrait_rejects_non_image_and_big_file(client, char):
    url = reverse("portrait", args=[char.pk])
    client.post(url, {"portrait": SimpleUploadedFile("x.png", b"not an image", content_type="image/png")})
    client.post(url, {"portrait": _png(fmt="GIF")})
    client.post(url, {"portrait": SimpleUploadedFile("big.png", b"0" * (2 * 1024 * 1024 + 1))})
    char.refresh_from_db()
    assert not char.portrait


def test_portrait_needs_access(client, char):
    url = reverse("portrait", args=[char.pk])
    client.post(url, {"portrait": _png()})
    client.post(reverse("lock", args=[char.pk]))
    assert client.get(url).status_code == 302  # to the unlock page
    assert client.post(url, {"remove": "1"}).status_code == 302
    char.refresh_from_db()
    assert char.portrait


def test_portrait_not_duplicated_and_removed_on_purge(client, char, tmp_path, django_capture_on_commit_callbacks):
    client.post(reverse("portrait", args=[char.pk]), {"portrait": _png()})
    char.refresh_from_db()
    path = tmp_path / char.portrait.name
    twin = transfer.duplicate_character(char, "Twin", PW)
    assert not twin.portrait
    Character.objects.filter(pk=char.pk).update(deleted_at=timezone.now() - timedelta(days=31))
    with django_capture_on_commit_callbacks(execute=True):
        trash.purge()
    assert not Character.all_objects.filter(pk=char.pk).exists() and not path.exists()
