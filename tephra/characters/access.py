"""Per-character password unlocking and admin-mode helpers."""

import logging
from datetime import timedelta
from functools import wraps

from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone

from .models import Character, NarratorSettings, Throttle

SESSION_KEY = "unlocked_characters"
STAMP_KEY = "unlocked_stamps"
ADMIN_KEY = "admin_mode_characters"
MIN_PASSWORD = 8  # new character passwords; older shorter ones keep working

security_log = logging.getLogger("tephra.security")


def _stamp(character):
    # tail of the password hash: a password change invalidates every earlier unlock
    return character.password[-16:]


def is_gm(request):
    return request.user.is_authenticated and request.user.is_staff


def unlocked_ids(request):
    return set(request.session.get(SESSION_KEY, []))


def unlock(request, character):
    ids = unlocked_ids(request)
    ids.add(character.pk)
    request.session[SESSION_KEY] = sorted(ids)
    request.session[STAMP_KEY] = {**request.session.get(STAMP_KEY, {}), str(character.pk): _stamp(character)}


def lock(request, character):
    request.session[SESSION_KEY] = sorted(unlocked_ids(request) - {character.pk})
    request.session[ADMIN_KEY] = sorted(set(request.session.get(ADMIN_KEY, [])) - {character.pk})


def can_access(request, character):
    return is_gm(request) or (character.pk in unlocked_ids(request)
                              and request.session.get(STAMP_KEY, {}).get(str(character.pk)) == _stamp(character))


def admin_mode_allowed(request, character):
    if is_gm(request):
        return True
    return can_access(request, character) and NarratorSettings.get().allow_player_admin_mode


def in_admin_mode(request, character):
    return admin_mode_allowed(request, character) and character.pk in request.session.get(ADMIN_KEY, [])


def set_admin_mode(request, character, on):
    ids = set(request.session.get(ADMIN_KEY, []))
    if on:
        ids.add(character.pk)
    else:
        ids.discard(character.pk)
    request.session[ADMIN_KEY] = sorted(ids)


def client_ip(request):
    """The last X-Forwarded-For hop is the one our reverse proxy added (earlier ones are client-controlled)."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[-1].strip()
    return forwarded or request.META.get("REMOTE_ADDR", "")


def is_limited(key, limit):
    return Throttle.objects.filter(key=key, expires__gt=timezone.now(), count__gte=limit).exists()


def hit(key, timeout=None):
    """Count one attempt under ``key``; a locked DB row so parallel workers don't lose counts."""
    now = timezone.now()
    expires = now + timedelta(seconds=timeout or settings.UNLOCK_LOCKOUT_SECONDS)
    with transaction.atomic():
        Throttle.objects.filter(expires__lte=now).exclude(key=key).delete()
        row, created = Throttle.objects.select_for_update().get_or_create(
            key=key, defaults={"count": 1, "expires": expires})
        if not created:
            row.count, row.expires = (row.count + 1, row.expires) if row.expires > now else (1, expires)
            row.save(update_fields=["count", "expires"])
    return row.count


def clear(key):
    Throttle.objects.filter(key=key).delete()


def _unlock_keys(request, character):
    return f"unlock-fail:{character.pk}:{client_ip(request)}", f"unlock-fail:{character.pk}"


def is_throttled(request, character):
    ip_key, char_key = _unlock_keys(request, character)
    return (is_limited(ip_key, settings.UNLOCK_MAX_ATTEMPTS)
            or is_limited(char_key, settings.UNLOCK_MAX_ATTEMPTS_PER_CHARACTER))


def register_failure(request, character):
    for key in _unlock_keys(request, character):
        hit(key)
    security_log.warning("failed unlock of character %s from %s", character.pk, client_ip(request))


def clear_failures(request, character):
    clear(_unlock_keys(request, character)[0])


def lock_all(request):
    for key in (SESSION_KEY, STAMP_KEY, ADMIN_KEY):
        request.session.pop(key, None)


def redirect_to(request, url):
    """htmx swaps a plain redirect's target into the page; ask it to navigate instead."""
    if request.headers.get("HX-Request"):
        return HttpResponse(headers={"HX-Redirect": url})
    return redirect(url)


def to_unlock(request, character):
    return redirect_to(request, reverse("unlock", args=[character.pk]))


def character_view(view):
    """Load ``Character`` by ``pk`` and require it to be unlocked (or the GM)."""

    @wraps(view)
    def wrapper(request, pk, *args, **kwargs):
        character = get_object_or_404(Character, pk=pk)
        if not can_access(request, character):
            return to_unlock(request, character)
        return view(request, character, *args, **kwargs)

    return wrapper


def admin_view(view):
    @wraps(view)
    def wrapper(request, pk, *args, **kwargs):
        character = get_object_or_404(Character, pk=pk)
        if not can_access(request, character):
            return to_unlock(request, character)
        if not in_admin_mode(request, character):
            return redirect("sheet", pk=character.pk)
        return view(request, character, *args, **kwargs)

    return wrapper
