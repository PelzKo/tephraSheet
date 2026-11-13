"""Read-only wiki content: app docs (docs/<lang>/*.md), the rules reference (chapters 1–5 of the
reference markdown, German in reference_rules_de.md) and safe markdown rendering."""

import html
import re
from functools import cache
from pathlib import Path

import xml.etree.ElementTree as etree
from urllib.parse import urlencode

import markdown
from django.utils.text import slugify
from markdown.inlinepatterns import InlineProcessor

from rules.lang import DEFAULT

BASE = Path(__file__).resolve().parents[1]
DOCS_DIR = BASE / "docs"
SOURCE_DIR = BASE / "rules" / "data" / "source"
EXT_DIR = BASE / "rules" / "data" / "ext"  # <key>/rules.md (+ rules_<lang>.md): extension rules chapters
SAFE_HREF = re.compile(r'href="(?!https?://|/|#|mailto:)[^"]*"')
IMG = re.compile(r'<img alt="([^"]*)" src="([^"]*)"[^>]*>')
CROSS_LINK = r"\[\[([^\]|\n]+)(?:\|([^\]\n]+))?\]\]"


def _by_name(entries, name):
    n = name.strip().lower()
    return next((e for e in entries if n in (e["name"].lower(), e["name_en"].lower(), e.get("slug", ""))), None)


def cross_link(target):
    """``[[target]]`` → (label, url): ``spec:``/``aug:``/``trait:`` name a rule entry (any language, by name or
    slug), anything else is a wiki page title (missing pages link to the new-page form)."""
    from rules.registry import get_registry

    kind, _, name = target.partition(":")
    reg = get_registry()
    if name and kind == "spec" and (s := _by_name(reg.specialties.values(), name)):
        return s["name"], f"/wiki/specialty/{s['slug']}/"
    if name and kind == "aug" and (a := _by_name(reg.augments.values(), name)):
        return a["name"], "/catalog/augments/?" + urlencode({"q": a["name"]})
    if name and kind == "trait" and (t := _by_name(reg.traits.values(), name)):
        return t["name"], f"/wiki/race/{t['race']}/"
    from .models import WikiPage

    page = (WikiPage.objects.filter(slug=slugify(target)).first()
            or WikiPage.objects.filter(title__iexact=target.strip()).first())
    if page:
        return page.title, page.get_absolute_url()
    return target.strip(), "/wiki/new/?" + urlencode({"title": target.strip()})


class _CrossLinks(InlineProcessor):
    def handleMatch(self, m, data):
        label, url = cross_link(m.group(1))
        el = etree.Element("a", {"href": url, "class": "xlink"})
        el.text = (m.group(2) or label).strip()
        return el, m.start(0), m.end(0)


def _image(m):
    """Only same-origin images load; external ones become links so readers' IPs don't leak."""
    alt, src = m.groups()
    # Browsers decode entities, drop tabs/newlines and read a backslash as "/" (so "/\host" is external).
    path = re.sub(r"[\t\n\r]", "", html.unescape(src))
    if path.startswith("/") and not path.startswith("//") and "\\" not in path:
        return m.group(0)
    return f'<a href="{src}">{alt or src}</a>'


def render(text):
    """Markdown → HTML for text anyone may write: raw HTML is escaped, links only to http(s),
    site paths, anchors and mailto, images only from this site, ``[[…]]`` cross-links."""
    md = markdown.Markdown(extensions=["tables", "sane_lists"])
    md.preprocessors.deregister("html_block")  # raw HTML is shown as text, not passed through
    md.inlinePatterns.deregister("html")
    md.inlinePatterns.register(_CrossLinks(CROSS_LINK, md), "cross_link", 175)
    return SAFE_HREF.sub('href="#"', IMG.sub(_image, md.convert(text or "")))


def _split(text, level_re):
    """[(title, body)] split at headings matching ``level_re``."""
    out, title, lines = [], "", []
    for line in text.splitlines():
        m = level_re.match(line)
        if m:
            if title or any(x.strip() for x in lines):
                out.append((title, "\n".join(lines)))
            title, lines = m.group(1).strip(), []
        else:
            lines.append(line)
    if title or any(x.strip() for x in lines):
        out.append((title, "\n".join(lines)))
    return out


@cache
def docs(lang):
    """App how-to pages: [{slug, title, body}] from docs/<lang>/NN-name.md (first line = '# Title')."""
    folder = DOCS_DIR / lang if (DOCS_DIR / lang).is_dir() else DOCS_DIR / DEFAULT
    pages = []
    for path in sorted(folder.glob("*.md")):
        text = path.read_text(encoding="utf8")
        first, _, body = text.partition("\n")
        pages.append({"slug": path.stem.split("-", 1)[-1], "title": first.lstrip("# ").strip(), "body": body})
    return pages


@cache
def reference(lang):
    """Rules reference chapters: [{slug, title, sections: [{slug, title, body}]}]."""
    de = SOURCE_DIR / f"reference_rules_{lang}.md"
    if lang != DEFAULT and de.is_file():
        text = de.read_text(encoding="utf8")
    else:
        full = (SOURCE_DIR / "Tephra_Reference_full.md").read_text(encoding="utf8")
        start = full.index("\n## 1.")
        text = full[start:full.index("\n## 6.", start)]
    sources = [(text, "")]
    for folder in sorted(p for p in EXT_DIR.glob("*") if p.is_dir()):
        path = folder / f"rules_{lang}.md"
        path = path if lang != DEFAULT and path.is_file() else folder / "rules.md"
        if path.is_file():
            sources.append((path.read_text(encoding="utf8"), folder.name))
    chapters = []
    for text, extension in sources:
        for title, body in _split(text, re.compile(r"^## (.+)$")):
            if not title:
                continue
            sections = [{"slug": slugify(t) or f"s{n}", "title": t or title, "body": b}
                        for n, (t, b) in enumerate(_split(body, re.compile(r"^### (.+)$")))]
            chapters.append({"slug": slugify(title), "title": title, "sections": sections, "extension": extension})
    return chapters
