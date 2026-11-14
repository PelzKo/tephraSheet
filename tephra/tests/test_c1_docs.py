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
