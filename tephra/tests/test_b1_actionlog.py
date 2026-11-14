"""b1-actionlog: action log (X1), undo (X2), admin diff (C9), party overview (N1), group actions (N2), feedback (N4)."""

import random
from datetime import timedelta

import pytest
from django.core import mail
from django.core.cache import cache
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone

from characters import actionlog, services
from rules.engine import tables
from characters.models import ActionLog, Character, EffectEntry, Feedback, InventoryItem, NarratorSettings

HX = {"HTTP_HX_REQUEST": "true"}


def make(name="Ada", **kw):
    c = Character(name=name, race="human", **{"status": "active", **kw})
    c.set_password("password1")
    c.save()
    return c


def play(client, c, action, data=None):
    return client.post(reverse("play", args=[c.pk, action]), data or {}, **HX)


def unlocked_client(client, c):
    client.post(reverse("unlock", args=[c.pk]), {"password": "password1"})
    return client


def test_play_action_logs_only_changed_fields(client, db):
    c = make()
    unlocked_client(client, c)
    play(client, c, "xp", {"delta": "2"})
    e = ActionLog.objects.get(action="play:xp")
    assert e.before == {"xp": 0} and e.after == {"xp": 2}
    assert e.actor == "session" and e.actor_detail == "Ada" and e.ip and e.character == c
    play(client, c, "fight_spend", {"amount": "1"})  # not in a fight: no change, no row
    assert not ActionLog.objects.filter(action="play:fight_spend").exists()
    assert ActionLog.objects.filter(action="unlock", character=c).exists()


def test_failed_unlock_logged_and_shown_in_party(client, admin_client, db):
    c = make()
    client.post(reverse("unlock", args=[c.pk]), {"password": "wrong"})
    assert ActionLog.objects.get(action="unlock:failed").actor == "anonymous"
    html = admin_client.get(reverse("gm_party"), **HX).content.decode()
    assert "Ada" in html and "<b>1</b>" in html  # one failed unlock
    assert admin_client.get(reverse("gm_party")).status_code == 200
    assert client.get(reverse("gm_party")).status_code == 302  # narrator only


def test_undo_last_play_action(admin_client, db):
    c = make()
    play(admin_client, c, "xp", {"delta": "2"})
    play(admin_client, c, "effect_add", {"text": "Dazed"})
    # The newest play action (effect) first: switched off again.
    admin_client.post(reverse("gm_undo", args=[c.pk]))
    assert not EffectEntry.objects.get(text="Dazed").active
    admin_client.post(reverse("gm_undo", args=[c.pk]))
    c.refresh_from_db()
    assert c.xp == 0
    assert ActionLog.objects.filter(action__startswith="undo:").count() == 2


def test_undo_refused_when_changed_since(admin_client, db):
    c = make()
    play(admin_client, c, "xp", {"delta": "2"})
    Character.objects.filter(pk=c.pk).update(xp=5)  # changed outside the logged action
    resp = admin_client.post(reverse("gm_undo", args=[c.pk]), follow=True)
    c.refresh_from_db()
    assert c.xp == 5
    assert "changed again" in resp.content.decode()


def test_undo_refuses_item_changes_and_players(client, admin_client, db):
    c = make()
    item = InventoryItem.objects.create(character=c, name="Rope")
    play(admin_client, c, "drop", {"id": item.pk})
    with pytest.raises(actionlog.UndoError):
        actionlog.undo(None, actionlog.last_entry(c))
    unlocked_client(client, c)
    assert client.post(reverse("gm_undo", args=[c.pk])).status_code == 302
    assert not ActionLog.objects.filter(action__startswith="undo:").exists()


@pytest.fixture
def leveled(admin_client, db):
    call_command("seed_catalog")
    c = Character.objects.create()
    services.random_all(c, random.Random(1))
    services.finish_creation(c)
    c.xp = tables.XP_PER_LEVEL + 1
    c.save()
    before = (c.level, sorted(map(tuple, c.specialties)), dict(c.skills))
    admin_client.post(reverse("levelup", args=[c.pk]), {"action": "random"})
    c.refresh_from_db()
    assert c.level == 2
    return c, before


def test_reverse_levelup(admin_client, leveled):
    c, (level, specs, skills) = leveled
    entry = ActionLog.objects.get(action="levelup", character=c)
    assert entry.before["level"] == 1 and entry.after["level"] == 2
    admin_client.post(reverse("gm_undo", args=[c.pk]), {"what": "levelup"})
    c.refresh_from_db()
    assert (c.level, sorted(map(tuple, c.specialties)), dict(c.skills), c.xp) == (level, specs, skills, tables.XP_PER_LEVEL + 1)
    assert not c.level_logs.filter(level=2).exists()
    assert c.current_hp <= c.compute().max_hp


def test_reverse_levelup_refused_after_xp_change(admin_client, leveled):
    c, _before = leveled
    play(admin_client, c, "xp", {"delta": "1"})
    admin_client.post(reverse("gm_undo", args=[c.pk]), {"what": "levelup"})
    c.refresh_from_db()
    assert c.level == 2


def test_admin_edit_logged_as_diff(admin_client, db):
    c = make(player_name="Bo")
    admin_client.post(reverse("toggle_admin", args=[c.pk]), {"on": "1"})
    resp = admin_client.post(reverse("edit_choices", args=[c.pk]),
                             {"action": "save", "player_name": "Cy", "race": "human", "level": "1", "xp": "4"}, follow=True)
    e = ActionLog.objects.get(action="admin:save")
    assert e.before["player_name"] == "Bo" and e.after == {"player_name": "Cy", "xp": 4}
    assert "player_name: Bo → Cy" in resp.content.decode()


def test_group_actions(admin_client, client, db):
    a = make("Ada", current_hp=0, fight={"active": True, "ap": 2})
    b = make("Bo", current_hp=0)
    make("Draft", status="draft")
    admin_client.post(reverse("gm_group_action"), {"what": "xp", "amount": "3"})
    admin_client.post(reverse("gm_group_action"), {"what": "breather"})
    a.refresh_from_db(), b.refresh_from_db()
    assert a.xp == b.xp == 3 and a.fight == {}
    assert a.current_hp == a.compute().max_hp
    assert Character.objects.get(name="Draft").xp == 0
    assert ActionLog.objects.filter(action="play:xp").count() == 2
    assert client.post(reverse("gm_group_action"), {"what": "xp", "amount": "5"}).status_code == 302
    a.refresh_from_db()
    assert a.xp == 3


def test_action_log_page_filters_and_prune(admin_client, db):
    a, b = make("Ada"), make("Bo")
    actionlog.log(None, "play:xp", a, {"xp": 0}, {"xp": 1})
    actionlog.log(None, "play:xp", b, {"xp": 0}, {"xp": 2})
    html = admin_client.get(reverse("gm_action_log"), {"character": a.pk, "action": "play"}).content.decode()
    assert "<td>play:xp</td>" in html and "xp</b>: 0 → 1" in html and "0 → 2" not in html
    old = ActionLog.objects.create(actor="system", action="old")
    ActionLog.objects.filter(pk=old.pk).update(created=timezone.now() - timedelta(days=200))
    cache.delete("actionlog-prune")
    actionlog.log(None, "play:xp", a, {"xp": 1}, {"xp": 2})
    assert not ActionLog.objects.filter(pk=old.pk).exists()


def test_story_tab_shows_history(client, db):
    c = make()
    unlocked_client(client, c)
    play(client, c, "damage", {"amount": "1"})
    html = client.get(reverse("sheet", args=[c.pk])).content.decode()
    assert "play:damage" in html and "Undo last action" not in html  # read-only for players


def test_settings_log_hides_passphrase_hash(admin_client, db):
    admin_client.post(reverse("gm_settings"), {"background_story_count": "1", "max_starting_level": "1",
                                               "new_passphrase": "a long phrase"})
    e = ActionLog.objects.get(action="settings")
    assert e.after["passphrase"] == "changed" and e.before["passphrase"] is False


def test_feedback_note_and_mail(admin_client, client, db, settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEBUG, settings.EMAIL_HOST = False, ""
    NarratorSettings.objects.update_or_create(pk=1, defaults={"feedback_email": "gm@example.org"})
    client.post(reverse("feedback"), {"message": "no host"})
    assert not mail.outbox  # no EMAIL_HOST: off
    settings.EMAIL_HOST = "smtp.example.org"
    client.post(reverse("feedback"), {"message": "hello"})
    assert mail.outbox[0].to == ["gm@example.org"] and "hello" in mail.outbox[0].body
    f = Feedback.objects.get(message="hello")
    admin_client.post(reverse("gm_feedback_note", args=[f.pk]), {"note": "fixed in 1.2"})
    client.post(reverse("gm_feedback_note", args=[f.pk]), {"note": "hacked"})
    f.refresh_from_db()
    assert f.note == "fixed in 1.2"
