"""Minimal parser for the Tephra reference markdown.

Splits the document into heading-scoped blocks and extracts pipe tables and
"Book texts" blocks (``**Name** — *Category*`` followed by ``>`` quote lines).
"""

import re
from dataclasses import dataclass, field

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
BOOK_TEXT_HEAD_RE = re.compile(r"^\*\*(.+?)\*\*\s+—\s+\*(.+?)\*\s*$")


@dataclass
class Table:
    headings: tuple  # heading path (h1..hN) at the table's position
    header: list
    rows: list  # list[dict]
    line: int
    lead: str = ""  # nearest non-table paragraph line above the table
    raw_rows: list = field(default_factory=list)  # list[list[str]] (for duplicate headers)

    @property
    def section(self):
        return self.headings[-1] if self.headings else ""


@dataclass
class BookText:
    headings: tuple
    name: str
    category: str
    text: str


@dataclass
class Document:
    tables: list = field(default_factory=list)
    book_texts: list = field(default_factory=list)
    lines: list = field(default_factory=list)

    def tables_under(self, heading_substring):
        return [t for t in self.tables if any(heading_substring in h for h in t.headings)]

    def tables_in(self, heading_prefix):
        return [t for t in self.tables if t.section.startswith(heading_prefix)]


def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def strip_md(text):
    """Remove bold/italic/code markers, keep <br> as newlines."""
    text = text.replace("<br>", "\n")
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    return text.strip()


def parse(path):
    with open(path, encoding="utf8") as fh:
        lines = fh.read().split("\n")
    doc = Document(lines=lines)
    stack = []
    i = 0
    last_para = ""
    while i < len(lines):
        line = lines[i]
        m = HEADING_RE.match(line)
        if m:
            level = len(m.group(1))
            stack = stack[: level - 1]
            while len(stack) < level - 1:
                stack.append("")
            stack.append(m.group(2).strip())
            last_para = ""
            i += 1
            continue
        if line.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s\-|:]+\|$", lines[i + 1].strip()):
            header = split_row(line)
            rows, raw_rows = [], []
            j = i + 2
            while j < len(lines) and lines[j].startswith("|"):
                cells = split_row(lines[j])
                cells += [""] * (len(header) - len(cells))
                rows.append(dict(zip(header, cells)))
                raw_rows.append(cells)
                j += 1
            doc.tables.append(Table(tuple(stack), header, rows, i + 1, last_para, raw_rows))
            i = j
            continue
        bm = BOOK_TEXT_HEAD_RE.match(line)
        if bm:
            text_lines = []
            j = i + 1
            while j < len(lines) and lines[j].startswith(">"):
                text_lines.append(lines[j][1:].strip())
                j += 1
            doc.book_texts.append(BookText(tuple(stack), bm.group(1).strip(), bm.group(2).strip(), "\n".join(text_lines)))
            i = j
            continue
        if line.strip() and not line.startswith(">"):
            last_para = line.strip()
        i += 1
    return doc


def jsonl_block(lines, start_marker="```jsonl"):
    import json

    out = []
    inside = False
    for line in lines:
        if line.strip() == start_marker:
            inside = True
            continue
        if inside and line.strip() == "```":
            break
        if inside and line.strip():
            out.append(json.loads(line))
    return out
