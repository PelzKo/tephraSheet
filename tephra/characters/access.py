"""Per-character password unlocking and admin-mode helpers."""

from functools import wraps

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect

from .models import Character, NarratorSettings

SESSION_KEY = "unlocked_characters"
ADMIN_KEY = "admin_mode_characters"


def is_gm(request):
    return request.user.is_authenticated and request.user.is_staff


def unlocked_ids(request):
    return set(request.session.get(SESSION_KEY, []))


def unlock(request, character):
    ids = unlocked_ids(request)
    ids.add(character.pk)
    request.session[SESSION_KEY] = sorted(ids)


def lock(request, character):
    request.session[SESSION_KEY] = sorted(unlocked_ids(request) - {character.pk})
    request.session[ADMIN_KEY] = sorted(set(request.session.get(ADMIN_KEY, [])) - {character.pk})


def can_access(request, character):
    return is_gm(request) or character.pk in unlocked_ids(request)


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


def throttle_key(request, character):
    ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", "")).split(",")[0].strip()
    return f"unlock-fail:{character.pk}:{ip}"


def is_throttled(request, character):
    return cache.get(throttle_key(request, character), 0) >= settings.UNLOCK_MAX_ATTEMPTS


def register_failure(request, character):
    key = throttle_key(request, character)
    cache.set(key, cache.get(key, 0) + 1, settings.UNLOCK_LOCKOUT_SECONDS)


def clear_failures(request, character):
    cache.delete(throttle_key(request, character))


def character_view(view):
    """Load ``Character`` by ``pk`` and require it to be unlocked (or the GM)."""

    @wraps(view)
    def wrapper(request, pk, *args, **kwargs):
        character = get_object_or_404(Character, pk=pk)
        if not can_access(request, character):
            return redirect("unlock", pk=character.pk)
        return view(request, character, *args, **kwargs)

    return wrapper


def admin_view(view):
    @wraps(view)
    def wrapper(request, pk, *args, **kwargs):
        character = get_object_or_404(Character, pk=pk)
        if not can_access(request, character):
            return redirect("unlock", pk=character.pk)
        if not in_admin_mode(request, character):
            return redirect("sheet", pk=character.pk)
        return view(request, character, *args, **kwargs)

    return wrapper
