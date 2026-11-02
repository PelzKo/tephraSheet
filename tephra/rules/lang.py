"""Current language and UI translations (pure Python, usable by the rules engine).

UI texts are translated by their English wording: ``locale/<code>/*.json`` hold
{"English text": "translation"} maps (all files of a language are merged) and
``locale/<code>/_meta.json`` holds {"name": "Deutsch"}. Rule content (specialties, traits …)
is translated in ``rules/data/i18n/<code>/`` (see rules/registry.py). Adding a language means
adding both folders; nothing else has to change. The web request sets the language
(characters.middleware.LanguageMiddleware)."""

import contextvars
import json
from functools import cache
from pathlib import Path

LOCALE_DIR = Path(__file__).resolve().parents[1] / "locale"
DEFAULT = "en"
_current = contextvars.ContextVar("tephra_language", default=DEFAULT)


@cache
def languages():
    """{code: native name}, English first."""
    out = {DEFAULT: "English"}
    if LOCALE_DIR.is_dir():
        for meta in sorted(LOCALE_DIR.glob("*/_meta.json")):
            out[meta.parent.name] = json.loads(meta.read_text(encoding="utf8"))["name"]
    return out


def set_language(code):
    _current.set(code if code in languages() else DEFAULT)


def get_language():
    return _current.get()


@cache
def catalog(code):
    merged = {}
    curated = LOCALE_DIR.parent / "rules" / "data" / "i18n" / code / "curated.json"
    if curated.is_file():  # labels/notes of rules/curated.py
        merged.update(json.loads(curated.read_text(encoding="utf8")))
    for path in sorted((LOCALE_DIR / code).glob("*.json")):
        if path.name != "_meta.json":
            merged.update(json.loads(path.read_text(encoding="utf8")))
    return merged


def gettext(text, /, **kwargs):
    """Translate ``text`` (its English wording) into the current language. ``{name}``
    placeholders are filled from ``kwargs``."""
    lang = _current.get()
    if lang != DEFAULT and text:
        text = catalog(lang).get(text) or text
    return text.format(**kwargs) if kwargs else text


_ = gettext
