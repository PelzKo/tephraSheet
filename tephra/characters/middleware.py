from urllib.parse import urlencode

from django.conf import settings as django_settings
from django.urls import reverse
from django.utils import translation
from django.utils.crypto import salted_hmac

from rules import extensions, lang

from . import access
from .models import NarratorSettings

COOKIE = "tephra_lang"
PASS_COOKIE = "tephra_pass"
PASS_MAX_AGE = 365 * 24 * 3600


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
    (get_registry) and Django's own texts, and which extensions/races new choices offer (rules.extensions)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        code = pick_language(request)
        lang.set_language(code)
        translation.activate(code)
        request.LANGUAGE_CODE = code
        settings = request.narrator_settings = NarratorSettings.get()
        extensions.set_offer(settings.enabled_extensions, settings.disabled_races)
        try:
            response = self.get_response(request)
        finally:
            lang.set_language(lang.DEFAULT)  # don't leak into the next request/test on this thread
            extensions.set_offer()
        response.headers.setdefault("Content-Language", code)
        return response


def _pass_stamp(narrator_settings):
    # derived from the hash, so a new passphrase invalidates every remembered pass
    return salted_hmac(PASS_COOKIE, narrator_settings.passphrase).hexdigest()[:24]


def remember_pass(response, narrator_settings):
    response.set_signed_cookie(PASS_COOKIE, _pass_stamp(narrator_settings), salt=PASS_COOKIE, max_age=PASS_MAX_AGE,
                               secure=django_settings.SESSION_COOKIE_SECURE, httponly=True, samesite="Lax")


def has_pass(request, narrator_settings):
    stamp = request.get_signed_cookie(PASS_COOKIE, default=None, salt=PASS_COOKIE, max_age=PASS_MAX_AGE)
    return stamp == _pass_stamp(narrator_settings)


class PassphraseMiddleware:
    """Group passphrase gate (set on /gm/): without it remembered in this browser only the gate itself,
    static files, the language switch and the narrator logins are reachable. No passphrase = no gate."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        narrator_settings = request.narrator_settings
        if (not narrator_settings.passphrase or access.is_gm(request)
                or request.path.startswith("/" + django_settings.STATIC_URL.lstrip("/"))
                or request.path in {reverse(name) for name in ("passphrase", "set_language", "gm_login", "admin:login")}
                or has_pass(request, narrator_settings)):
            return self.get_response(request)
        if request.headers.get("HX-Request"):
            target = request.headers.get("HX-Current-URL", "/")
        else:
            target = request.get_full_path() if request.method == "GET" else "/"
        return access.redirect_to(request, reverse("passphrase") + "?" + urlencode({"next": target}))


# Strings static/js/app.js shows to the user (it looks them up with t(); keep in sync).
JS_TEXTS = [
    "Total",
    "Not saved – tap to retry",
    "Offline – read only",
    "This makes the balance negative. Continue?",
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
