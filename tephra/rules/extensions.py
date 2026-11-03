"""Which rule content is offered for *new* choices (pure Python, like rules.lang).

Rule entries from an extension carry ``"extension": "<key>"`` (``also_in`` lists more keys that show it too);
no key means core. The narrator switches extensions on and races off (``NarratorSettings``); the web request
sets that per request (characters.middleware.LanguageMiddleware).

Only pickers, wizards and random generators filter. Lookups by slug (``get_registry()``, ``to_state``,
``stats.compute``) never do: existing characters keep everything they already have.
"""

import contextvars

# key -> English name; a key is added together with its content.
EXTENSIONS = {}

_offer = contextvars.ContextVar("tephra_offer", default=(frozenset(), frozenset()))


def set_offer(extensions=(), disabled_races=()):
    _offer.set((frozenset(extensions), frozenset(disabled_races)))


def is_offered(entry):
    keys = {entry.get("extension"), *entry.get("also_in", ())} - {None, ""}
    return not keys or bool(keys & _offer.get()[0])


def offer(entries, keep=()):
    """The entries new choices may use, plus the slugs in ``keep`` (what the character already has)."""
    return [e for e in entries if e["slug"] in keep or is_offered(e)]


def offer_races(races, keep=()):
    disabled = _offer.get()[1]
    return [r for r in offer(races, keep) if r["slug"] in keep or r["slug"] not in disabled]
