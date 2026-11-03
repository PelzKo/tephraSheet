import pytest
from django.urls import reverse

from wiki.content import render
from wiki.models import WikiPage


def test_render_escapes_html_and_bad_links():
    html = render("# Hi\n<script>x</script> [a](javascript:alert(1)) [b](https://ok.example)\n\n| a | b |\n|---|---|\n| 1 | 2 |")
    assert "<script>" not in html and 'href="#"' in html and 'href="https://ok.example"' in html and "<table>" in html


@pytest.mark.django_db
def test_wiki_pages_search_and_language(client):
    assert client.get(reverse("wiki")).status_code == 200
    client.post(reverse("wiki_new"), {"title": "House rules", "body": "Crits on **12**.", "name": "Ana"})
    page = WikiPage.objects.get()
    assert page.slug == "house-rules"
    client.post(reverse("wiki_edit", args=[page.slug]), {"title": "House rules", "body": "Crits on 11.", "name": "Bo"})
    page.refresh_from_db()
    assert page.body == "Crits on 11." and page.revisions.get().body == "Crits on **12**."
    resp = client.get(reverse("wiki"), {"q": "battle theme"})
    assert b"Battle Theme" in resp.content and b"Specialty" in resp.content
    assert client.get(reverse("wiki"), {"q": "crits"}).content.count(b"House rules") >= 1
    from wiki.content import reference

    chapters = [c for c in reference("en") if not c["extension"]]
    assert len(chapters) == 5 and len([c for c in reference("de") if not c["extension"]]) == 5
    ext = next(c for c in reference("en") if c["extension"] == "explosives")
    assert client.get(reverse("wiki_rules", args=[ext["slug"]])).status_code == 404  # extension off
    assert b"Hit points" in client.get(reverse("wiki_rules", args=[chapters[0]["slug"]])).content
    client.post(reverse("set_language"), {"language": "de", "next": "/wiki/"})
    resp = client.get(reverse("wiki"), {"q": "Schlachthymne"})
    assert b"Schlachthymne" in resp.content and resp.headers["Content-Language"] == "de"
    resp = client.get(reverse("wiki_specialty", args=["showmanship-battle-theme"]))
    assert "Schlachthymne".encode() in resp.content
