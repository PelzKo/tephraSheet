import importlib

import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
from django.urls import reverse

from catalog.importer import MAX_ROWS, export_csv, parse_rows
from catalog.models import ItemTemplate
from characters.models import Character, InventoryItem


@pytest.fixture
def catalog(db):
    call_command("seed_catalog")


@pytest.fixture
def gm(client, catalog):
    User.objects.create_user("gm", password="pw", is_staff=True)
    client.login(username="gm", password="pw")
    return client


@pytest.fixture
def char(client, catalog):
    client.post(reverse("character_new"))
    return Character.objects.get()


def _book(**filters):
    return ItemTemplate.objects.filter(source="book", extension="", **filters).exclude(size="heavy").first()


def test_seed_keeps_edits_and_hidden_items(catalog):
    edited, hidden = ItemTemplate.objects.filter(source="book")[:2]
    ItemTemplate.objects.filter(pk=edited.pk).update(size="heavy", modified=True)
    ItemTemplate.objects.filter(pk=hidden.pk).update(deleted_at="2026-01-01T00:00Z")
    gone = ItemTemplate.objects.filter(source="book").last()
    gone.delete()
    call_command("seed_catalog")
    edited.refresh_from_db()
    hidden.refresh_from_db()
    assert edited.size == "heavy" and hidden.deleted_at
    assert ItemTemplate.objects.filter(name=gone.name, kind=gone.kind).exists()  # missing rows are created
    assert not ItemTemplate.offered().filter(pk=hidden.pk).exists()


def test_migration_marks_only_changed_book_items(catalog):
    mig = importlib.import_module("catalog.migrations.0010_a3_mark_modified")
    from django.apps import apps
    item = ItemTemplate.objects.filter(source="book").first()
    ItemTemplate.objects.filter(pk=item.pk).update(price_dukes=item.price_dukes + 1)
    mig.mark_modified(apps, None)
    assert list(ItemTemplate.objects.filter(modified=True)) == [item]


def test_narrator_edit_hide_restore_reset(gm):
    item = _book()
    url = reverse("item_edit", args=[item.pk])
    form = gm.get(url).context["form"]
    assert form.fields["name"].disabled and form.fields["kind"].disabled
    data = {k: v for k, v in form.initial.items() if v is not None and k not in ("variants", "beta", "concealable",
                                                                                 "deflect_ranged", "deflect_melee",
                                                                                 "memento", "is_starting_gear")}
    data.update(name="Renamed", size="heavy", variants=item.variants)
    gm.post(url, data)
    item.refresh_from_db()
    assert item.modified and item.size == "heavy" and item.name != "Renamed"
    gm.post(url, {"delete": "1"})
    item.refresh_from_db()
    assert item.deleted_at and ItemTemplate.objects.filter(pk=item.pk).exists()
    assert item in gm.get(reverse("catalog") + "?source=hidden").context["items"]
    gm.post(url, {"reset": "1"})
    item.refresh_from_db()
    assert not item.modified and not item.deleted_at and item.size != "heavy"


def test_book_items_read_only_for_players(client, catalog):
    item = _book()
    assert client.post(reverse("item_edit", args=[item.pk]), {"delete": "1"}).status_code == 302
    assert ItemTemplate.objects.get(pk=item.pk).deleted_at is None


def test_list_source_filter_and_paging(client, catalog):
    ItemTemplate.objects.create(name="Homebrew", kind="gear", source="custom")
    ctx = client.get(reverse("catalog") + "?source=custom").context
    assert [i.name for i in ctx["items"]] == ["Homebrew"]
    assert all(i.source == "book" for i in client.get(reverse("catalog") + "?source=book").context["items"])
    assert client.get(reverse("catalog") + "?source=hidden").context["items"].paginator.count > 1  # players: ignored
    ItemTemplate.objects.bulk_create(ItemTemplate(name=f"Filler {n}", kind="general") for n in range(60))
    total = ItemTemplate.offered().count()
    page2 = client.get(reverse("catalog") + "?page=2").context["items"]
    assert page2.paginator.count == total and len(page2) == total - 100 > 0
    ext = client.get(reverse("catalog") + "?ext=core").context["items"]
    assert ext.paginator.count == ItemTemplate.offered().filter(extension="").count()


def test_copy_as_new_item(client, catalog):
    item = _book(augments__isnull=False)
    form = client.get(reverse("item_create") + f"?copy={item.pk}").context["form"]
    assert form.initial["name"].startswith(item.name) and form.initial["size"] == item.size


def test_export_round_trips_through_importer(catalog):
    items = list(ItemTemplate.objects.all())
    rows = parse_rows(export_csv(items))
    assert [r["errors"] for r in rows if r["errors"]] == []
    for item, row in zip(items, rows):
        for k, v in row["values"].items():
            assert getattr(item, k) == v, (item.name, k)


def test_import_preview_statuses_and_counts(client, catalog):
    book = _book()
    ItemTemplate.objects.create(name="Old Custom", kind="gear", source="custom", price_dukes=5)
    ItemTemplate.objects.create(name="Same Custom", kind="gear", source="custom", price_dukes=5)
    text = (f"name,kind,price_dukes\n{book.name},{book.kind},1\nOld Custom,gear,9\nSame Custom,gear,5\n"
            f"Brand New,gear,1\n{'x' * 121},gear,1\n")
    resp = client.post(reverse("catalog_import"), {"action": "preview", "text": text})
    assert [r["status"] for r in resp.context["rows"]] == ["skipped", "update", "unchanged", "new", "error"]
    resp = client.post(reverse("catalog_import"), {"action": "commit", "target": "catalog"}, follow=True)
    msg = str(list(resp.context["messages"])[0])
    assert "1 new, 1 updated, 1 unchanged, 1 skipped" in msg and "1 with errors" in msg
    assert ItemTemplate.objects.get(name="Old Custom").price_dukes == 9


def test_narrator_import_marks_modified_keeps_starting_gear(gm):
    item = ItemTemplate.objects.filter(source="book", is_starting_gear=True).first()
    gm.post(reverse("catalog_import"), {"action": "preview", "text": f"name,kind,price_dukes\n{item.name},{item.kind},77\n"})
    gm.post(reverse("catalog_import"), {"action": "commit", "target": "catalog"})
    item.refresh_from_db()
    assert item.modified and item.price_dukes == 77 and item.is_starting_gear


def test_import_caps(client, catalog):
    rows = parse_rows("name\n" + "x\n" * (MAX_ROWS + 1))
    assert len(rows) == 1 and rows[0]["errors"]
    from django.core.files.uploadedfile import SimpleUploadedFile
    big = SimpleUploadedFile("big.csv", b"name\n" + b"x" * 1_000_001)
    resp = client.post(reverse("catalog_import"), {"action": "preview", "file": big})
    assert resp.context["rows"] is None


def test_add_to_inventory_checks(client, char):
    url = lambda t: reverse("add_to_inventory", args=[t.pk])  # noqa: E731
    priced = ItemTemplate.objects.filter(price_dukes__gt=0, extension="").first()
    char.money_on_hand = priced.price_dukes - 1
    char.save()
    client.post(url(priced), {"for": char.pk, "pay": "1"})
    char.refresh_from_db()
    assert char.money_on_hand == priced.price_dukes - 1 and not char.items.exists()
    # odd digits and foreign redirects don't crash or leave the site
    resp = client.post(url(priced), {"for": char.pk, "quantity": "²", "next": "https://evil.example/"})
    assert resp.status_code == 302 and resp.url.startswith("/")
    assert client.get(reverse("catalog") + "?for=²").status_code == 200
    ext = ItemTemplate.objects.exclude(extension="").first()
    if ext:  # extension switched off -> not offered
        assert client.post(url(ext), {"for": char.pk}).status_code == 404
    assert InventoryItem.objects.filter(character=char).count() == 1
