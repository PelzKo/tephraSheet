import pytest
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse

from characters import access
from characters.models import Character, Feedback, NarratorSettings, card_cache_key
from characters.views import general


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def gated(db):
    s = NarratorSettings.get()
    s.passphrase = make_password("open sesame")
    s.save()
    return s


def make_char(password="secret12"):
    c = Character.objects.create(name="Hero", status="active")
    c.set_password(password)
    c.save()
    return c


# S1 passphrase gate

def test_no_passphrase_no_gate(client, db):
    assert client.get("/").status_code == 200


def test_gate_redirects_and_remembers(client, gated):
    resp = client.get("/wiki/")
    assert resp.status_code == 302 and resp.url.startswith(reverse("passphrase"))
    assert client.post(reverse("feedback"), {"message": "x"}).status_code == 302
    assert client.get(reverse("passphrase")).status_code == 200
    assert client.get("/static/css/app.css").status_code != 302
    assert b"Wrong passphrase" in client.post(reverse("passphrase"), {"passphrase": "nope"}).content
    resp = client.post(reverse("passphrase"), {"passphrase": "open sesame", "next": "/wiki/"})
    assert resp.url == "/wiki/"
    assert client.get("/wiki/").status_code == 200
    # a new passphrase invalidates the remembered pass
    gated.passphrase = make_password("other phrase")
    gated.save()
    assert client.get("/wiki/").status_code == 302


def test_gate_rejects_foreign_next_and_htmx(client, gated):
    resp = client.post(reverse("passphrase"), {"passphrase": "open sesame", "next": "https://evil.example/"})
    assert resp.url == "/"
    client.cookies.clear()
    resp = client.post("/c/1/play/damage/", HTTP_HX_REQUEST="true", HTTP_HX_CURRENT_URL="/c/1/")
    assert resp.status_code == 200 and resp["HX-Redirect"].startswith(reverse("passphrase"))


def test_gate_staff_and_login_exempt(client, gated):
    assert client.get(reverse("gm_login")).status_code == 200
    assert client.get(reverse("admin:login")).status_code == 200
    User.objects.create_user("gm", password="pw-for-gm-123", is_staff=True)
    client.login(username="gm", password="pw-for-gm-123")
    assert client.get("/wiki/").status_code == 200


def test_gate_throttle(client, gated):
    for _ in range(8):
        client.post(reverse("passphrase"), {"passphrase": "nope"})
    resp = client.post(reverse("passphrase"), {"passphrase": "open sesame"})
    assert b"Too many" in resp.content


def test_gm_sets_and_removes_passphrase(client, db):
    User.objects.create_user("gm", password="pw-for-gm-123", is_staff=True)
    client.login(username="gm", password="pw-for-gm-123")
    data = {"background_story_count": 1, "max_starting_level": 1, "new_passphrase": "short"}
    assert client.post(reverse("gm_settings"), data).status_code == 200  # too short, form error
    assert not NarratorSettings.get().passphrase
    data["new_passphrase"] = "our group phrase"
    client.post(reverse("gm_settings"), data)
    assert NarratorSettings.get().passphrase.startswith("pbkdf2")
    client.post(reverse("gm_settings"), {**data, "new_passphrase": "", "remove_passphrase": "on"})
    assert NarratorSettings.get().passphrase == ""


# B2 feedback page_url

def test_feedback_page_url_xss(client, db):
    client.post(reverse("feedback"), {"message": "a", "page_url": "javascript:alert(1)"})
    client.post(reverse("feedback"), {"message": "b", "page_url": "http://testserver/wiki/?q=1"})
    client.post(reverse("feedback"), {"message": "c", "page_url": "//evil.example/x"})
    bad, path, slashes = Feedback.objects.order_by("pk")
    assert path.page_url == "/wiki/?q=1" and path.safe_page_url == "/wiki/?q=1"
    assert bad.safe_page_url == "" and slashes.safe_page_url == ""
    User.objects.create_user("gm", password="pw-for-gm-123", is_staff=True)
    client.login(username="gm", password="pw-for-gm-123")
    html = client.get(reverse("gm_settings")).content.decode()
    assert 'href="javascript' not in html and 'href="//evil' not in html
    assert 'href="/wiki/?q=1"' in html


def test_feedback_odd_character_and_ip_throttle(client, db):
    assert client.post(reverse("feedback"), {"message": "x", "character": "²"}).status_code == 200
    for _ in range(9):
        client.post(reverse("feedback"), {"message": "x"})
    client.cookies.clear()  # a fresh cookie no longer resets the limit
    assert client.post(reverse("feedback"), {"message": "x"}).status_code == 429


# B4 unlock throttling

def test_client_ip_uses_last_forwarded_hop(rf):
    req = rf.get("/", HTTP_X_FORWARDED_FOR="1.1.1.1, 2.2.2.2", REMOTE_ADDR="127.0.0.1")
    assert access.client_ip(req) == "2.2.2.2"
    assert access.client_ip(rf.get("/", REMOTE_ADDR="3.3.3.3")) == "3.3.3.3"


@override_settings(UNLOCK_MAX_ATTEMPTS=100, UNLOCK_MAX_ATTEMPTS_PER_CHARACTER=5)
def test_unlock_per_character_limit_ignores_spoofed_ips(client, db):
    c = make_char()
    url = reverse("unlock", args=[c.pk])
    for i in range(5):
        client.post(url, {"password": "wrong"}, REMOTE_ADDR=f"10.0.0.{i}")
    resp = client.post(url, {"password": "secret12"}, REMOTE_ADDR="10.0.0.99")
    assert b"Too many" in resp.content


def test_unlock_spoofed_forwarded_header_does_not_reset(client, db):
    c = make_char()
    url = reverse("unlock", args=[c.pk])
    for i in range(8):
        client.post(url, {"password": "wrong"}, HTTP_X_FORWARDED_FOR=f"9.9.9.{i}, 5.5.5.5")
    resp = client.post(url, {"password": "secret12"}, HTTP_X_FORWARDED_FOR="8.8.8.8, 5.5.5.5")
    assert b"Too many" in resp.content


# B5 password length

def test_password_min_length(client, db):
    c = make_char()
    client.post(reverse("unlock", args=[c.pk]), {"password": "secret12"})
    url = reverse("password", args=[c.pk])
    client.post(url, {"password": "short", "confirm": "short"})
    c.refresh_from_db()
    assert c.check_password("secret12")
    client.post(url, {"password": "longenough", "confirm": "longenough"})
    c.refresh_from_db()
    assert c.check_password("longenough")


def test_old_short_password_still_unlocks(client, db):
    c = make_char("abc")
    resp = client.post(reverse("unlock", args=[c.pk]), {"password": "abc"})
    assert resp.url == c.get_absolute_url()


# B6 narrator login

def test_gm_login_throttled(client, db):
    User.objects.create_user("gm", password="pw-for-gm-123", is_staff=True)
    for _ in range(8):
        client.post(reverse("gm_login"), {"username": "gm", "password": "wrong"})
    resp = client.post(reverse("gm_login"), {"username": "gm", "password": "pw-for-gm-123"})
    assert b"Too many" in resp.content and "_auth_user_id" not in client.session


def test_admin_moved():
    assert reverse("admin:index") == "/narrator-admin/"


# B16

def test_htmx_after_unlock_expiry(client, db):
    c = make_char()
    resp = client.post(reverse("play", args=[c.pk, "damage"]), HTTP_HX_REQUEST="true")
    assert resp.status_code == 200 and resp["HX-Redirect"] == reverse("unlock", args=[c.pk])


# B21

def test_card_values_cached_and_invalidated(db, monkeypatch, client):
    c = Character.objects.create(name="Hero", status="active", race="human")
    calls = []
    real = Character.compute
    monkeypatch.setattr(Character, "compute", lambda self: calls.append(1) or real(self))
    client.get("/")
    client.get("/")
    assert len(calls) == 1
    c.save()
    assert cache.get(card_cache_key(c.pk, "en")) is None
    client.get("/")
    assert len(calls) == 2


# S5 / S6

def test_gm_page_shows_server_info(client, db, tmp_path, settings):
    settings.BACKUP_DIR = tmp_path
    (tmp_path / "tephra-2026-01-01.sql.gz").write_bytes(b"x")
    User.objects.create_user("gm", password="pw-for-gm-123", is_staff=True)
    client.login(username="gm", password="pw-for-gm-123")
    html = client.get(reverse("gm_settings")).content.decode()
    assert "SQLite" in html and "No backup found" not in html
    assert general.last_backup() is not None


def test_lock_all(client, db):
    c = make_char()
    client.post(reverse("unlock", args=[c.pk]), {"password": "secret12"})
    assert b"Lock all" in client.get("/").content
    client.post(reverse("lock_all"))
    assert client.get(reverse("sheet", args=[c.pk])).url == reverse("unlock", args=[c.pk])
