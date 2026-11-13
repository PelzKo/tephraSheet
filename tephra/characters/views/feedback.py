"""Feedback bubble: anyone can send a message; the narrator reviews it on the GM page."""

import json
from urllib.parse import urlsplit, urlunsplit

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from rules.lang import gettext as _
from .. import access
from ..models import Character, Feedback

MAX_MESSAGE = 5000
RATE_WINDOW = 600  # seconds
RATE_LIMIT = 10  # messages per window and address (in the cache, so a new cookie doesn't reset it)


def _client_meta(raw):
    """Browser-supplied details, kept as flat strings/numbers and size-limited."""
    try:
        data = json.loads(raw or "{}")
    except ValueError:
        return {}
    if not isinstance(data, dict):
        return {}
    clean = {}
    for key, value in list(data.items())[:30]:
        if isinstance(value, (bool, int, float)):
            clean[str(key)[:40]] = value
        elif isinstance(value, str):
            clean[str(key)[:40]] = value[:300]
    return clean


def _page_path(request, raw):
    """The page URL as a same-site path; JS sends location.href, so drop our own scheme and host."""
    parts = urlsplit(raw)
    if parts.scheme in ("http", "https") and parts.netloc == request.get_host():
        return urlunsplit(("", "", parts.path, parts.query, parts.fragment))
    return raw  # stored as given, shown as plain text (Feedback.safe_page_url)


@require_POST
def feedback_submit(request):
    rate_key = f"feedback:{access.client_ip(request)}"
    if access.is_limited(rate_key, RATE_LIMIT):
        return JsonResponse({"error": _("Too many messages – please wait a few minutes.")}, status=429)

    text = request.POST.get("message", "").strip()
    if not text:
        return JsonResponse({"error": _("Please write a message.")}, status=400)
    if len(text) > MAX_MESSAGE:
        return JsonResponse({"error": _("Message too long (max {max} characters).", max=MAX_MESSAGE)}, status=400)
    category = request.POST.get("category", "feedback")
    if category not in dict(Feedback.CATEGORY_CHOICES):
        category = "other"

    character = None
    pk = request.POST.get("character", "")
    if pk.isascii() and pk.isdigit():
        character = Character.objects.filter(pk=pk).first()

    meta = _client_meta(request.POST.get("meta"))
    meta.update({
        "user_agent": request.META.get("HTTP_USER_AGENT", "")[:300],
        "narrator": access.is_gm(request),
        "unlocked_characters": sorted(access.unlocked_ids(request)),
    })
    if character:
        meta["admin_mode"] = access.in_admin_mode(request, character)
        meta["character_level"] = character.level
        meta["character_status"] = character.status

    Feedback.objects.create(
        category=category, name=request.POST.get("name", "").strip()[:80], message=text,
        page_url=_page_path(request, request.POST.get("page_url", ""))[:500], page_title=request.POST.get("page_title", "")[:200],
        character=character, character_name=str(character)[:120] if character else "", meta=meta)
    access.hit(rate_key, RATE_WINDOW)
    return JsonResponse({"ok": True})


@staff_member_required(login_url="gm_login")
@require_POST
def feedback_status(request, pk):
    entry = get_object_or_404(Feedback, pk=pk)
    status = request.POST.get("status", "")
    if status in dict(Feedback.STATUS_CHOICES):
        entry.status = status
        entry.save(update_fields=["status"])
    return redirect("gm_settings")


@staff_member_required(login_url="gm_login")
@require_POST
def feedback_delete(request, pk):
    get_object_or_404(Feedback, pk=pk).delete()
    messages.success(request, _("Feedback deleted."))
    return redirect("gm_settings")
