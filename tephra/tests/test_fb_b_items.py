import random

import pytest
from django.contrib.messages import get_messages
from django.core.management import call_command
from django.urls import reverse

from catalog.models import ItemTemplate
from characters import services
from characters.models import ActionLog, Character, InventoryItem, NarratorSettings, Pet
from rules import extensions
from rules.registry import get_registry


@pytest.fixture(autouse=True)
def reset_offer():
    yield
    extensions.set_offer()


@pytest.fixture
def char(client, db):
    call_command("seed_catalog")
    client.post(reverse("character_new"))
    return Character.objects.get()


def _form_data(client, url):
    form = client.get(url).context["form"]
    data = {k: v for k, v in form.initial.items() if v is not None and k in form.fields}
    data.update({k: form[k].value() for k in form.fields if form[k].value() not in (None, [])})
    return {k: v for k, v in data.items() if v is not None}


def test_inventory_edit_of_catalog_copy_saves_without_unique_error(client, char):
    whip = ItemTemplate.objects.filter(source="book").first()
    inv = InventoryItem.from_template(char, whip, slot="carried")
    inv.save()
    url = reverse("inventory_item_edit", args=[char.pk, inv.pk])
    data = _form_data(client, url)
    data["reach"] = 10
    resp = client.post(url, data)
    assert resp.status_code == 302, resp.context["form"].errors
    inv.refresh_from_db()
    whip_after = ItemTemplate.objects.get(pk=whip.pk)
    assert inv.reach == 10 and whip_after.reach == whip.reach  # template untouched
    assert ActionLog.objects.filter(action="inventory:edit").exists()


NEW_ITEM = {"name": "Lucky Revolver", "kind": "firearm", "size": "medium", "material": "metal", "augments_json": "[]"}


def test_create_for_character_is_inventory_only_by_default(client, char):
    resp = client.post(reverse("item_create") + f"?for={char.pk}", {**NEW_ITEM, "slot": "weapon1", "for": char.pk})
    assert resp.status_code == 302
    inv = InventoryItem.objects.get(character=char, name="Lucky Revolver")
    assert inv.slot == "weapon1" and inv.template is None  # equip rules still applied
    assert not ItemTemplate.objects.filter(name="Lucky Revolver").exists()


def test_create_for_character_also_to_catalog(client, char):
    client.post(reverse("item_create") + f"?for={char.pk}", {**NEW_ITEM, "for": char.pk, "add_to_catalog": "1"})
    tpl = ItemTemplate.objects.get(name="Lucky Revolver", kind="firearm")
    assert tpl.source == "custom" and InventoryItem.objects.get(character=char).template == tpl
    assert ActionLog.objects.filter(action="catalog:create").exists()


def test_create_for_character_existing_name_stays_inventory_only(client, char):
    book = ItemTemplate.objects.filter(source="book", kind="melee").first()
    resp = client.post(reverse("item_create") + f"?for={char.pk}",
                       {**NEW_ITEM, "name": book.name, "kind": "melee", "for": char.pk, "add_to_catalog": "1"})
    assert resp.status_code == 302
    assert ItemTemplate.objects.filter(name=book.name, kind="melee").count() == 1
    inv = InventoryItem.objects.get(character=char, name=book.name)
    assert inv.template is None
    assert any("only added to the inventory" in str(m) for m in get_messages(resp.wsgi_request))


def test_create_in_catalog_refuses_existing_name(client, char):
    book = ItemTemplate.objects.filter(source="book", kind="melee").first()
    resp = client.post(reverse("item_create"), {**NEW_ITEM, "name": book.name, "kind": "melee"})
    assert resp.status_code == 200 and resp.context["form"].errors
    resp = client.post(reverse("item_create"), NEW_ITEM)
    assert resp.status_code == 302 and ItemTemplate.objects.filter(name="Lucky Revolver").exists()


def test_wizard_finish_without_password_shows_error(client, char):
    services.random_all(char, random.Random(1))
    page = client.get(reverse("wizard_step", args=[char.pk, 10])).content.decode()
    assert 'value="finish" formnovalidate' in page  # the browser must not block the submit silently
    resp = client.post(reverse("wizard_step", args=[char.pk, 10]), {"action": "finish", "name": "Ann"})
    assert resp.status_code == 302 and resp["Location"].endswith("/10/#messages")
    assert "Set a password for your character." in [str(m) for m in get_messages(resp.wsgi_request)]
    assert 'id="messages"' in client.get(resp["Location"]).content.decode()
    char.refresh_from_db()
    assert char.status == "draft"


def test_planner_hides_owned_and_earlier_planned_specialties(client, char):
    services.random_all(char, random.Random(3))
    char.set_password("pw")
    services.finish_creation(char)
    client.post(reverse("unlock", args=[char.pk]), {"password": "pw"})
    reg = get_registry()
    owned = char.specialties[0][0]
    planned = next(s for s in reg.specialties if s not in dict(char.specialties) and not reg.specialties[s]["requires"]
                   and not reg.specialties[s].get("repeatable"))
    url = reverse("planner", args=[char.pk])
    client.post(url, {"action": "save", "level": "2", "specialty": planned})
    slugs = lambda lvl: {s["slug"] for s in client.get(url + f"?edit={lvl}").context["specialties"]}  # noqa: E731
    later = slugs(3)
    assert owned not in later and planned not in later
    assert planned in slugs(2)  # the entry's own pick stays selectable
    assert owned in {s["slug"] for s in client.get(url + "?edit=4").context["owned_specialties"]}


def test_pet_has_one_movement_type(admin_client, db):
    NarratorSettings.objects.update_or_create(pk=NarratorSettings.get().pk,
                                              defaults={"enabled_extensions": ["pets-and-predators"]})
    c = Character.objects.create(race="human", status="active")
    resp = admin_client.post(reverse("pet_new", args=[c.pk]),
                             {"name": "Rex", "template": "medium-land", "movement": ["swift", "climbing"]})
    assert resp.status_code == 302
    assert Pet.objects.get().movement == ["swift"]
    page = admin_client.get(reverse("pet_edit", args=[c.pk, Pet.objects.get().pk])).content.decode()
    assert 'type="radio" name="movement"' in page
