import pytest
from django.urls import reverse

from wiki.content import docs


def test_help_pages_exist_in_every_language():
    slugs = {lang: [d["slug"] for d in docs(lang)] for lang in ("en", "de")}
    assert slugs["en"] == slugs["de"]
    assert "narrator" in slugs["en"]


@pytest.mark.django_db
@pytest.mark.parametrize("slug", [d["slug"] for d in docs("en")])
def test_help_pages_render(client, slug):
    assert client.get(reverse("wiki_help", args=[slug])).status_code == 200


def test_every_help_link_target_exists():
    from pathlib import Path
    import re

    base = Path(__file__).resolve().parents[1] / "templates"
    used = {m for p in base.glob("**/*.html")
            for m in re.findall(r'help_link\.html" with slug="([^"]+)"', p.read_text(encoding="utf8"))}
    assert len(used) >= 6
    for lang in ("en", "de"):
        assert used <= {d["slug"] for d in docs(lang)}


@pytest.mark.django_db
def test_catalog_shows_help_link(client):
    assert b'href="/wiki/help/items/"' in client.get(reverse("catalog")).content
