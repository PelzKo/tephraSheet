"""Feedback bubble: anyone can send a message; the narrator reviews it on the GM page."""

import json
from urllib.parse import urlsplit, urlunsplit

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from rules.lang import gettext as _
from .. import access
from ..models import Character, Feedback, NarratorSettings

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

    entry = Feedback.objects.create(
        category=category, name=request.POST.get("name", "").strip()[:80], message=text,
        page_url=_page_path(request, request.POST.get("page_url", ""))[:500], page_title=request.POST.get("page_title", "")[:200],
        character=character, character_name=str(character)[:120] if character else "", meta=meta)
    access.hit(rate_key, RATE_WINDOW)
    notify(request, entry)
    return JsonResponse({"ok": True})


def mail_configured():
    # settings.py sets the SMTP values only outside DEBUG (Django's own default host is "localhost").
    return not settings.DEBUG and bool(settings.EMAIL_HOST)


def notify(request, entry):
    """Mail new feedback to the narrator's address (/gm/), only when the server has mail settings."""
    to = NarratorSettings.get().feedback_email
    if to and mail_configured():
        send_mail(f"[Tephra] {entry}"[:120], f"{entry.message}\n\n{request.build_absolute_uri('/gm/#feedback')}",
                  None, [to], fail_silently=True)


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
def feedback_note(request, pk):
    entry = get_object_or_404(Feedback, pk=pk)
    entry.note = request.POST.get("note", "")[:MAX_MESSAGE]
    entry.save(update_fields=["note"])
    return redirect("gm_settings")


@staff_member_required(login_url="gm_login")
@require_POST
def feedback_delete(request, pk):
    get_object_or_404(Feedback, pk=pk).delete()
    messages.success(request, _("Feedback deleted."))
    return redirect("gm_settings")


EXPORT_COLUMNS = ["id", "status", "category", "created", "from", "character", "page", "message", "note", "meta"]


def _tsv_cell(value):
    """One line per row: tabs and line breaks inside a field would break the TSV.
    Player text starting with = + - @ gets a leading ' so spreadsheets don't run it as a formula."""
    text = str(value)
    if text[:1] in ("=", "+", "-", "@"):
        text = "'" + text
    return text.replace("\\", "\\\\").replace("\t", "\\t").replace("\r\n", "\\n").replace("\n", "\\n").replace("\r", "\\n")


def export_tsv(entries):
    """Feedback as TSV ordered by status, then category, then date (oldest first).
    Newlines in texts are written as a literal \\n, backslashes as \\\\."""
    status_rank = {s: i for i, (s, _l) in enumerate(Feedback.STATUS_CHOICES)}
    cat_rank = {c: i for i, (c, _l) in enumerate(Feedback.CATEGORY_CHOICES)}
    rows = sorted(entries, key=lambda f: (status_rank.get(f.status, 99), cat_rank.get(f.category, 99), f.created))
    lines = ["\t".join(EXPORT_COLUMNS)]
    for f in rows:
        lines.append("\t".join(_tsv_cell(v) for v in (
            f.pk, f.status, f.category, f.created.isoformat(timespec="minutes"), f.name, f.character_name,
            " ".join(filter(None, [f.page_title, f.page_url])), f.message, f.note,
            json.dumps(f.meta, ensure_ascii=False) if f.meta else "")))
    return "\n".join(lines) + "\n"


@staff_member_required(login_url="gm_login")
@require_POST
def feedback_export(request):
    """Download all feedback as TSV (status as it was before the export); new entries become "In progress"."""
    entries = list(Feedback.objects.all())
    body = export_tsv(entries)
    Feedback.objects.filter(pk__in=[f.pk for f in entries if f.status == "new"]).update(status="progress")
    resp = HttpResponse(body, content_type="text/tab-separated-values; charset=utf-8")
    resp["Content-Disposition"] = f'attachment; filename="tephra_feedback_{timezone.localdate():%Y-%m-%d}.tsv"'
    return resp
