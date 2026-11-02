"""The story journal: plain text where '# Heading' / '## Heading' lines start a new block.

Inside a block: blank lines separate paragraphs, '- ' starts a list item, **bold** and *italic*."""

import re

from django.utils.html import escape

_HEADING = re.compile(r"^(#{1,3})\s+(.*)$")


def _inline(text):
    text = escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    return re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<i>\1</i>", text)


def _body_html(lines):
    html, para, items = [], [], []

    def flush():
        if para:
            html.append(f"<p>{'<br>'.join(_inline(x) for x in para)}</p>")
            para.clear()
        if items:
            html.append("<ul>" + "".join(f"<li>{_inline(x)}</li>" for x in items) + "</ul>")
            items.clear()

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush()
        elif stripped.startswith(("- ", "* ")):
            if para:
                flush()
            items.append(stripped[2:])
        else:
            if items:
                flush()
            para.append(stripped)
    flush()
    return "".join(html)


def sections(text):
    """[{title, level, html, text}] – text before the first heading is an untitled block."""
    out, title, level, lines = [], "", 1, []

    def push():
        if title or any(x.strip() for x in lines):
            out.append({"title": title, "level": level, "html": _body_html(lines),
                        "text": (title + "\n" + "\n".join(lines)).lower()})

    for line in (text or "").splitlines():
        m = _HEADING.match(line)
        if m:
            push()
            title, level, lines = m.group(2).strip(), len(m.group(1)), []
        else:
            lines.append(line)
    push()
    return out
