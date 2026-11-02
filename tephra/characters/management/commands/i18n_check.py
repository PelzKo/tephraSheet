"""List UI texts that have no translation: every {% t "…" %} in templates and every
_("…") / gettext("…") in Python, checked against locale/<code>/*.json."""

import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from rules import lang

PATTERNS = [re.compile(r'{%\s*t\s+"((?:[^"\\]|\\.)*)"'), re.compile(r"{%\s*t\s+'((?:[^'\\]|\\.)*)'"),
            re.compile(r'\b(?:_|gettext)\(\s*"((?:[^"\\]|\\.)*)"'), re.compile(r"\b(?:_|gettext)\(\s*'((?:[^'\\]|\\.)*)'")]


def used_texts(base):
    found = {}
    for path in list(base.glob("templates/**/*.html")) + [p for p in base.glob("**/*.py")
                                                         if "migrations" not in p.parts and ".venv" not in p.parts
                                                         and p.name not in ("i18n_check.py", "tr_tags.py")]:
        text = path.read_text(encoding="utf8")
        for pat in PATTERNS:
            for m in pat.finditer(text):
                found.setdefault(m.group(1).replace('\\"', '"').replace("\\'", "'"), str(path.relative_to(base)))
    return found


class Command(BaseCommand):
    help = "Report UI texts without a translation (per language)"

    def add_arguments(self, parser):
        parser.add_argument("--lang", help="only this language code")

    def handle(self, *args, **opts):
        base = Path(settings.BASE_DIR)
        texts = used_texts(base)
        missing_total = 0
        for code in lang.languages():
            if code == lang.DEFAULT or (opts.get("lang") and code != opts["lang"]):
                continue
            cat = lang.catalog(code)
            missing = sorted((t, f) for t, f in texts.items() if t not in cat)
            missing_total += len(missing)
            self.stdout.write(f"{code}: {len(texts) - len(missing)}/{len(texts)} translated")
            for t, f in missing:
                self.stdout.write(f"  {f}: {t}")
        if missing_total:
            raise SystemExit(1)
