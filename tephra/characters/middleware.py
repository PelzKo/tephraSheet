from django.utils import translation

from rules import lang

COOKIE = "tephra_lang"


def pick_language(request):
    """Session/cookie choice, else the browser's Accept-Language, else English."""
    known = lang.languages()
    chosen = request.session.get(COOKIE) or request.COOKIES.get(COOKIE)
    if chosen in known:
        return chosen
    for part in request.META.get("HTTP_ACCEPT_LANGUAGE", "").split(","):
        code = part.split(";")[0].strip().lower()[:2]
        if code in known:
            return code
    return lang.DEFAULT


class LanguageMiddleware:
    """Sets the language for templates ({% t %}), Python (rules.lang.gettext), the rule data
    (get_registry) and Django's own texts."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        code = pick_language(request)
        lang.set_language(code)
        translation.activate(code)
        request.LANGUAGE_CODE = code
        try:
            response = self.get_response(request)
        finally:
            lang.set_language(lang.DEFAULT)  # don't leak into the next request/test on this thread
        response.headers.setdefault("Content-Language", code)
        return response


# Strings static/js/app.js shows to the user (it looks them up with t(); keep in sync).
JS_TEXTS = [
    "Total",
    "custom effect (no automatic changes)",
    "Pick a status effect from the list, or type your own.",
    "Choose the hit location, then the wounded or fatal effect.",
    "Sort by this column (click again to reverse)",
    "Sending…",
    "Could not send feedback.",
    "Thanks! Your message was sent to the narrator.",
]


def language_context(request):
    return {"languages": lang.languages(), "current_language": lang.get_language(),
            "js_i18n": {s: lang.gettext(s) for s in JS_TEXTS}}
