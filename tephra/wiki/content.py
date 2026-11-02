"""Read-only wiki content: app docs (docs/<lang>/*.md), the rules reference (chapters 1–5 of the
reference markdown, German in reference_rules_de.md) and safe markdown rendering."""

import re
from functools import cache
from pathlib import Path

import markdown
from django.utils.text import slugify

from rules.lang import DEFAULT

BASE = Path(__file__).resolve().parents[1]
DOCS_DIR = BASE / "docs"
SOURCE_DIR = BASE / "rules" / "data" / "source"
SAFE_HREF = re.compile(r'href="(?!https?://|/|#|mailto:)[^"]*"')


def render(text):
    """Markdown → HTML for text anyone may write: raw HTML is escaped, links only to http(s),
    site paths, anchors and mailto."""
    html = markdown.markdown((text or "").replace("<", "&lt;"), extensions=["tables", "sane_lists"])
    return SAFE_HREF.sub('href="#"', html)


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
    chapters = []
    for title, body in _split(text, re.compile(r"^## (.+)$")):
        if not title:
            continue
        sections = [{"slug": slugify(t) or f"s{n}", "title": t or title, "body": b}
                    for n, (t, b) in enumerate(_split(body, re.compile(r"^### (.+)$")))]
        chapters.append({"slug": slugify(title), "title": title, "sections": sections})
    return chapters
