import pytest
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.management import call_command
from django.urls import reverse

from catalog.models import ItemTemplate
from wiki import views
from wiki.content import render
from wiki.models import WikiPage


@pytest.fixture(autouse=True)
def _clear_cache():
    cache.clear()


def _page(**kw):
    return WikiPage.objects.create(slug=kw.pop("slug", "lore"), title=kw.pop("title", "Lore"), body=kw.pop("body", "v1"))


def _edit(client, p, body, **extra):
    data = {"title": p.title, "body": body, "name": "Ana", "updated": p.updated.isoformat()}
    return client.post(reverse("wiki_edit", args=[p.slug]), {**data, **extra})


def test_render_code_html_and_images():
    html = render("a `x<y` <b>raw</b>\n\n![far](https://evil.example/t.png) ![near](/static/img/gear.svg) ![p](//evil.example/x)")
    assert "<code>x&lt;y</code>" in html and "&lt;b&gt;raw" in html and "<b>" not in html
    assert 'src="https://evil' not in html and '<a href="https://evil.example/t.png">far</a>' in html
    assert '<img alt="near" src="/static/img/gear.svg"' in html and "src=\"//" not in html


@pytest.mark.django_db
def test_cross_links_resolve_and_escape():
    _page(slug="the-docks", title="The Docks")
    html = render('[[The Docks]] [[the docks|harbour]] [[spec:Battle Theme]] [[New "<x>" Place]] `[[The Docks]]`')
    assert '<a class="xlink" href="/wiki/p/the-docks/">The Docks</a>' in html
    assert '<a class="xlink" href="/wiki/p/the-docks/">harbour</a>' in html
    assert 'href="/wiki/specialty/showmanship-battle-theme/"' in html
    assert "/wiki/new/?title=New+%22%3Cx%3E%22+Place" in html and "<x>" not in html
    assert "<code>[[The Docks]]</code>" in html


@pytest.mark.django_db
def test_history_diff_and_staff_restore(client):
    p = _page(body="old line")
    assert _edit(client, p, "new line").status_code == 302
    p.refresh_from_db()
    rev = p.revisions.get()
    resp = client.get(reverse("wiki_history", args=[p.slug]), {"rev": rev.pk})
    assert b'class="del">-old line' in resp.content and b'class="add">+new line' in resp.content
    url = reverse("wiki_restore", args=[p.slug, rev.pk])
    assert client.post(url).status_code == 404  # players cannot restore
    client.force_login(User.objects.create_user("gm", password="x", is_staff=True))
    assert b"Restore" in client.get(reverse("wiki_history", args=[p.slug])).content
    client.post(url)
    p.refresh_from_db()
    assert p.body == "old line" and p.revisions.first().body == "new line"


@pytest.mark.django_db
def test_edit_conflict_refused(client):
    p = _page(body="base")
    stale = p.updated.isoformat()
    _edit(client, p, "first save")
    resp = _edit(client, p, "second save", updated=stale)
    p.refresh_from_db()
    assert resp.status_code == 409 and p.body == "first save"
    assert b"first save" in resp.content and b"second save" in resp.content
    # The re-rendered form carries the new stamp, so saving again overwrites on purpose.
    assert _edit(client, p, "second save").status_code == 302


@pytest.mark.django_db
def test_size_cap_and_edit_rate_limit(client, monkeypatch):
    p = _page()
    assert _edit(client, p, "x" * (views.MAX_BODY + 1)).status_code == 200
    p.refresh_from_db()
    assert p.body == "v1"
    monkeypatch.setattr(views, "EDIT_LIMIT", 2)
    for n in range(2):
        p.refresh_from_db()
        assert _edit(client, p, f"edit {n}").status_code == 302
    p.refresh_from_db()
    assert _edit(client, p, "spam").status_code == 429
    # A forged first X-Forwarded-For hop does not dodge the limit; the proxy-added last hop counts.
    p.refresh_from_db()
    assert _edit(client, p, "spam", HTTP_X_FORWARDED_FOR="1.2.3.4, 127.0.0.1").status_code == 429


@pytest.mark.django_db
def test_search_covers_catalog_and_header_box(client):
    ItemTemplate.objects.create(name="Grappling Hook", kind="general", description="Climb walls.")
    resp = client.get(reverse("wiki"), {"q": "grappling"})
    assert b"Grappling Hook" in resp.content and b"/catalog/?q=Grappling+Hook" in resp.content
    assert b'class="inline header-search"' in client.get(reverse("character_list")).content


def test_german_translations_complete():
    """W6: fails when a UI text has no German entry (all locale/de/*.json files merged)."""
    try:
        call_command("i18n_check", lang="de")
    except SystemExit as e:
        pytest.fail(f"i18n_check --lang de reported gaps (exit {e.code})")
