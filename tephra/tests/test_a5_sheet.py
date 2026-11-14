"""a5-sheet: play actions and sheet UI (drafts/conflicts, breather, money, give, companions, print, refresh)."""

import pytest
from django.urls import reverse

from characters.models import Automaton, Character, EffectEntry, InventoryItem, JournalRevision, Pet
from characters.views.sheet import text_stamp
from rules.engine import effects as fx

# A called-shot effect that ends with a breather, as (silhouette number, kind).
BREATHER_LOC, BREATHER_KIND = next((n, k) for n in fx.LOCATION_LABELS for k in fx.CALLED_KINDS
                                   if fx.EFFECTS.get(fx.called_key(n, k), {}).get("breather"))
BREATHER_KEY = fx.called_key(BREATHER_LOC, BREATHER_KIND)

HX = {"HTTP_HX_REQUEST": "true"}


def make(name="Ada", password=None, **kw):
    c = Character(name=name, race="human", status="active", **kw)
    if password:
        c.set_password(password)
    c.save()
    return c


def play(client, c, action, data=None):
    return client.post(reverse("play", args=[c.pk, action]), data or {}, **HX)


def test_journal_conflict_keeps_both_texts(admin_client, db):
    c = make(story_notes="old")
    base = text_stamp("old")
    play(admin_client, c, "story", {"story_notes": "device A", "base": base})
    c.refresh_from_db()
    assert c.story_notes == "device A"
    assert JournalRevision.objects.get(character=c).text == "old"
    # Device B still edits from "old": refused, both versions shown.
    resp = play(admin_client, c, "story", {"story_notes": "device B", "base": base})
    c.refresh_from_db()
    assert c.story_notes == "device A"
    html = resp.content.decode()
    assert "data-conflict" in html and "device A" in html and "device B" in html
    # Saving again from the conflict view (new base) works.
    play(admin_client, c, "story", {"story_notes": "merged", "base": text_stamp("device A")})
    c.refresh_from_db()
    assert c.story_notes == "merged"


def test_notes_conflict_and_story_append(admin_client, db):
    c = make(notes="n1", story_notes="# Day 1")
    play(admin_client, c, "notes", {"notes": "mine", "base": text_stamp("other")})
    c.refresh_from_db()
    assert c.notes == "n1"
    play(admin_client, c, "story-append", {"line": "Met the captain."})
    c.refresh_from_db()
    assert c.story_notes == "# Day 1\nMet the captain."
    assert JournalRevision.objects.filter(character=c).count() == 1


def test_journal_revisions_capped(db):
    c = make()
    for i in range(JournalRevision.KEEP + 5):
        JournalRevision.record(c, f"t{i}")
    assert JournalRevision.objects.filter(character=c).count() == JournalRevision.KEEP


def test_breather_does_all_bookkeeping(admin_client, db):
    c = make(current_hp=1, fight={"active": True, "ap": 1, "my_turn": False, "round": 2})
    EffectEntry.objects.create(character=c, kind="wound", key=BREATHER_KEY, text="Blinded", location=1)
    pet = Pet.objects.create(character=c, name="Viper", template="small-land", traits=[["painful", None]], venom_used=1)
    resp = play(admin_client, c, "breather")
    c.refresh_from_db()
    pet.refresh_from_db()
    assert c.current_hp == c.compute().max_hp and c.fight == {}
    assert not c.effects.filter(active=True).exists()
    assert pet.venom_used == 0
    html = resp.content.decode()
    assert "fight mode" in html and "Viper" in html


def test_pet_damage_flows_into_wounds_and_is_capped(admin_client, db):
    c = make()
    pet = Pet.objects.create(character=c, name="Rex", template="medium-land")
    play(admin_client, c, "pet-hp", {"id": pet.pk, "amount": 10 ** 9, "sign": "1"})
    pet.refresh_from_db()
    from rules.engine.pets import compute_pet
    s = compute_pet(pet.to_state())
    assert pet.hp_damage == s["stats"]["hp"].total and pet.wounds_taken == s["stats"]["wnd"].total
    play(admin_client, c, "pet-wound", {"id": pet.pk, "delta": 5})
    play(admin_client, c, "pet-venom", {"id": pet.pk, "delta": 5})
    pet.refresh_from_db()
    assert pet.wounds_taken == s["stats"]["wnd"].total and pet.venom_used == 0


def test_automaton_wounds_capped(admin_client, db):
    c = make()
    auto = Automaton.objects.create(character=c, name="Bolt")
    play(admin_client, c, "auto-damage", {"id": auto.pk, "amount": 10 ** 6, "sign": "1"})
    auto.refresh_from_db()
    assert auto.wounds_taken == auto.compute()["stats"]["wnd"].total


def test_money_ops(admin_client, db):
    c = make(money_on_hand=100, money_in_bank=0)
    play(admin_client, c, "money", {"op": "to_bank", "amount": 3, "unit": "pr"})
    c.refresh_from_db()
    assert (c.money_on_hand, c.money_in_bank) == (70, 30)
    play(admin_client, c, "money", {"op": "spend", "amount": 1, "unit": "k", "where": "bank"})
    play(admin_client, c, "money", {"op": "gain", "amount": 5, "unit": "d", "where": "hand"})
    c.refresh_from_db()
    assert (c.money_on_hand, c.money_in_bank) == (75, -70)


def test_give_item_and_money_needs_unlocked_target(client, db):
    a, b = make("Ada", "pw-a", money_on_hand=50), make("Bob", "pw-b")
    rope = InventoryItem.objects.create(character=a, name="Rope", kind="gear", quantity=3)
    client.post(reverse("unlock", args=[a.pk]), {"password": "pw-a"})
    play(client, a, "give-item", {"id": rope.pk, "to": b.pk, "quantity": 1})
    rope.refresh_from_db()
    assert rope.quantity == 3 and not b.items.exists()  # Bob not unlocked here
    client.post(reverse("unlock", args=[b.pk]), {"password": "pw-b"})
    play(client, a, "give-item", {"id": rope.pk, "to": b.pk, "quantity": 1})
    play(client, a, "give-money", {"to": b.pk, "amount": 3, "unit": "pr"})
    play(client, a, "give-money", {"to": b.pk, "amount": 1, "unit": "k"})  # more than on hand: refused
    rope.refresh_from_db()
    a.refresh_from_db()
    b.refresh_from_db()
    assert rope.quantity == 2 and b.items.get().quantity == 1
    assert (a.money_on_hand, b.money_on_hand) == (20, 30)
    assert "gave" in a.story_notes and "Bob" in a.story_notes and "received" in b.story_notes
    play(client, a, "give-item", {"id": rope.pk, "to": b.pk})  # the whole rest of the stack moves
    rope.refresh_from_db()
    assert rope.character_id == b.pk and rope.quantity == 2


def test_effect_lifetime_shown(admin_client, db):
    c = make(fight={"active": True, "ap": 3, "my_turn": True, "round": 4})
    play(admin_client, c, "effect-add", {"kind": "called", "location": BREATHER_LOC, "which": BREATHER_KIND})
    e = EffectEntry.objects.get(character=c)
    assert e.fight_round == 4 and e.ends_with_breather
    html = admin_client.get(c.get_absolute_url() + "?tab=inventory").content.decode()
    assert "ends with breather" in html and "added in round 4" in html


def test_wound_message_offers_called_shot_button(admin_client, db):
    c = make()
    hp = c.compute().max_hp
    html = play(admin_client, c, "damage", {"amount": hp + 1}).content.decode()
    assert "addCalled('wound')" in html
    c.wounds_taken = c.compute().max_wounds
    c.save()
    html = play(admin_client, c, "damage", {"amount": 1, "direct": 1}).content.decode()
    assert "addCalled('fatal')" in html


def test_messages_render_once_on_full_page(admin_client, db):
    c = make()
    pet = Pet.objects.create(character=c, name="Rex", template="medium-land")
    admin_client.post(reverse("play", args=[c.pk, "pet-hp"]), {"id": pet.pk, "amount": 1})  # no HX: redirect
    play(admin_client, c, "xp", {"set": 12})  # HX: message consumed by the partial
    admin_client.post(reverse("play", args=[c.pk, "xp"]), {"delta": "0"})  # non-HX: message on next page
    html = admin_client.get(c.get_absolute_url()).content.decode()
    assert html.count("Enough experience for a new level!") == 1


def test_stamp_endpoint_and_partial_refresh(admin_client, client, db):
    c = make()
    stamp = admin_client.get(reverse("sheet_stamp", args=[c.pk])).json()["stamp"]
    play(admin_client, c, "xp", {"delta": 1})
    assert admin_client.get(reverse("sheet_stamp", args=[c.pk])).json()["stamp"] != stamp
    assert client.get(reverse("sheet_stamp", args=[c.pk])).status_code == 302  # locked
    part = admin_client.get(c.get_absolute_url() + "?tab=story", **HX).content.decode()
    assert part.lstrip().startswith("<div id=\"sheet-body\"") or 'id="sheet-body"' in part[:400]
    assert "<html" not in part


def test_pencil_print_ignores_stance_without_saving(admin_client, db):
    c = make(stance="footing", toggles=["x"])
    html = admin_client.get(c.get_absolute_url() + "?print=pencil").content.decode()
    assert "data-autoprint" in html and "sheet-shell pencil" in html
    c.refresh_from_db()
    assert c.stance == "footing" and c.toggles == ["x"]


def test_print_appendix_and_active_details(admin_client, db):
    c = make(notes="line one\nline two", stance="footing", story_notes="# Day 1\nWe met.")
    html = admin_client.get(c.get_absolute_url()).content.decode()
    assert 'class="print-appendix"' in html and "We met." in html
    assert 'class="active-details"' in html


def test_service_worker(client, db):
    resp = client.get(reverse("service_worker"))
    assert resp.status_code == 200 and resp["Content-Type"].startswith("text/javascript")
    assert 'const STATIC = "/static/"' in resp.content.decode()


@pytest.mark.parametrize("field", ["story_notes", "notes"])
def test_editors_carry_draft_and_base(admin_client, db, field):
    c = make(**{field: "hello"})
    html = admin_client.get(c.get_absolute_url()).content.decode()
    assert f'value="{text_stamp("hello")}" data-draft-base' in html


def test_give_locks_both_characters_first(admin_client, db):
    """A→B and B→A at once must not deadlock: both rows are locked together, in pk order, first."""
    from django.db import connection
    from django.test.utils import CaptureQueriesContext
    a, b = make("Ada"), make("Bob")
    with CaptureQueriesContext(connection) as ctx:
        play(admin_client, b, "give-money", {"to": a.pk, "amount": 0})
    sqls = [q["sql"] for q in ctx.captured_queries]
    both = next(i for i, q in enumerate(sqls) if 'FROM "characters_character"' in q and " IN (" in q and "ORDER BY" in q)
    own = max(i for i, q in enumerate(sqls) if q.endswith(f'"characters_character"."id" = {b.pk} LIMIT 21'))
    assert both < own  # the pair lock comes before the single-row lock in play_action


def test_app_js_reads_request_element_from_event_detail():
    """htmx 2 puts the requesting element in event.detail.elt; requestConfig has no elt."""
    from pathlib import Path
    from django.conf import settings
    js = (Path(settings.BASE_DIR) / "static/js/app.js").read_text(encoding="utf-8")
    assert "requestConfig.elt" not in js and "cfg.elt" not in js
    assert "elt: e.detail.elt" in js and "const elt = e.detail.elt" in js
