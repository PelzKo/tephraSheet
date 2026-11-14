"""Feedback package C: augment book texts (#8), melee augment rules (#4), term explainer tips (#11)."""
from catalog.forms import ItemForm
from characters.models import Character
from rules.engine.requirements import check_augment
from rules.registry import get_registry


def test_chained_grip_has_book_text():
    reg = get_registry()
    for slug in ("armsmith-melee-chained-grip", "armsmith-firearm-crossbow-chained-grip"):
        text = reg.augments[slug]["text"]
        assert "chain attached to both their wrist" in text and not text.endswith("Weapon")


def test_same_name_augments_get_their_own_list_text():
    reg = get_registry()
    assert "on a weapon" in reg.augments["armsmith-melee-damaging"]["text"]
    assert "Firearm" not in reg.augments["armsmith-melee-damaging"]["text"]
    assert "bow" in reg.augments["armsmith-bow-custom"]["text"]


def test_melee_easily_altered_needs_interchangeable_parts(db):
    reg = get_registry()
    aug = reg.augments["armsmith-melee-easily-altered"]
    c = Character.objects.create(race="human", skills={"Armsmith": 4}, specialties=[["armsmith-weapon-smith", 1]])
    ok, reasons = check_augment(aug, c.to_state(), c.compute())
    assert not ok and any("Interchangeable Parts" in r for r in reasons)
    c.specialties.append(["armsmith-interchangeable-parts-2", 1])
    c.save()
    assert check_augment(aug, c.to_state(), c.compute())[0]


def test_melee_item_refuses_firearm_augments(db):
    base = {"name": "Sabre", "kind": "melee", "size": "medium", "material": "metal", "deflect_melee": "on"}
    assert not ItemForm(dict(base, augments_json='[["armsmith-firearm-crossbow-horrifying", 1]]')).is_valid()
    assert ItemForm(dict(base, augments_json='[["armsmith-melee-horrifying", 1]]')).is_valid()


def test_term_tips_matching():
    from django.utils.safestring import mark_safe

    from characters.templatetags.sheet_tags import effect_html, term_tips

    html = term_tips('Enemies T2 Spirit or Fear T2; "fearless" & 3 unsoakable <b>')
    assert html.count('class="term"') == 3  # T2, Fear T2, unsoakable (not "fearless")
    assert 'title="Frightened (Fear T2): ' in html and "Scared" not in html  # the tier picks one fear level
    assert "&lt;b&gt;" in html and "&quot;fearless&quot; &amp;" in html  # text is escaped
    assert "True dread (Fear T4)" in term_tips("causes fear")  # bare "fear" explains every tier
    assert term_tips(html) is html  # HTML is never wrapped again
    assert term_tips(mark_safe('<a title="fear">x</a>')) == '<a title="fear">x</a>'  # attributes untouched
    assert "\n" not in str(term_tips("Fear")).split(">", 1)[0]  # multi-line tip encoded, survives linebreaksbr
    assert 'class="term"' in effect_html("You are stunned.")


def test_term_tips_german():
    from characters.templatetags.sheet_tags import term_tips
    from rules.lang import set_language

    set_language("de")
    try:
        html = term_tips("Ziel muss Furcht S2 widerstehen, 4 nicht absorbierbarer Schaden, Ehrfurcht")
        assert "Verschreckt (Furcht S2)" in html
        assert ">widerstehen</span>" in html and ">nicht absorbierbarer</span>" in html
        assert html.count('class="term"') == 3  # "Ehrfurcht" is no fear
    finally:
        set_language("en")


def test_catalog_augment_reference_shows_tips(client, db):
    resp = client.get("/catalog/augments/")
    assert resp.status_code == 200
    assert 'class="term" title="' in resp.content.decode()
