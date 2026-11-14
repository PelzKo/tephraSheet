"""Feedback package A: header search contrast, augment page width, augment tips and gears."""

import re
from pathlib import Path

from django.conf import settings
from django.urls import reverse

from catalog.forms import augment_choices_json
from characters.models import Character, InventoryItem
from characters.templatetags.sheet_tags import aug_tip, effect_html

CSS = (Path(settings.BASE_DIR) / "static/css/app.css").read_text()
HORRIFYING = "armsmith-melee-horrifying"


def _rule(selector):
    return re.search(re.escape(selector) + r"\s*\{([^}]*)\}", CSS).group(1)


def test_inputs_set_dark_text_on_light_background():
    # The topbar's light text color must not leak into the header search field (#13).
    rule = _rule("input[type=text], input[type=password], input[type=number], input[type=search], select, textarea")
    assert "background: #fffdf7" in rule and "color: var(--ink)" in rule


def test_marque_pills_wrap_and_feedback_dialog_centers_on_phones():
    # A nowrap pill with a 120-character marque text widened the augment page to ~1360px (#10).
    assert "nowrap" not in _rule(".pill-bonus")
    assert re.search(r"@media \(max-width: 600px\) \{ \.fb-backdrop \{[^}]*justify-content: center", CSS)


def test_augment_tip_on_inventory_and_weapon(admin_client, db):
    c = Character.objects.create(name="Ada", race="human", status="active")
    InventoryItem.objects.create(character=c, name="Whip", kind="melee", size="light", slot="weapon1",
                                 augments=[[HORRIFYING, 1]])
    tip = aug_tip([HORRIFYING, 1])
    assert tip.startswith("mQ I: T2 Spirit to resist T1 fear\n") and len(tip) > 60
    html = admin_client.get(reverse("sheet", args=[c.pk]) + "?tab=inventory").content.decode()
    first_line = 'title="mQ I: T2 Spirit to resist T1 fear'
    assert html.count(first_line) >= 2  # inventory row + weapon block
    assert aug_tip(["no-such-augment", 1]) == ""


def test_augment_texts_get_marque_gears(client, db):
    html = effect_html("Body.\nT1 x 1\nT2 x 2\nT3 x 3\nT4 x 4", "mq")
    assert html.count('class="tier-gear"') == 4 and 'title="mQ IV"><span>IV</span>' in html
    assert "roll 1–9" in effect_html("Body.\nT1 x 1\nT2 x 2\nT3 x 3\nT4 x 4")  # specialties unchanged
    page = client.get(reverse("augment_reference")).content.decode()
    assert 'title="mQ IV"' in page
    assert any("tier-gear" in o["text_html"] for o in augment_choices_json()["melee"])
