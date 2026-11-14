"""Trash (S3), export/import (S4), duplicate (C14) and abandoned drafts (N3): the narrator's /gm/ section."""
import json

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.http import require_POST

from rules.lang import gettext as _
from .. import access, transfer, trash
from ..models import Character, CharacterSnapshot

gm_only = staff_member_required(login_url="gm_login")


def gm_context():
    """Template values for templates/characters/gm/_b2_trash.html."""
    characters = list(Character.objects.prefetch_related("snapshots").order_by("name"))
    return {"trash_entries": trash.entries(), "trash_days": trash.TRASH_DAYS,
            "abandoned_drafts": trash.abandoned_drafts().count(), "draft_days": trash.DRAFT_DAYS,
            "transfer_characters": characters}


def _download(data, name, stamp):
    resp = HttpResponse(json.dumps(data, ensure_ascii=False, indent=1), content_type="application/json")
    resp["Content-Disposition"] = f'attachment; filename="{slugify(name) or "character"}-{stamp:%Y%m%d-%H%M}.json"'
    return resp


@access.character_view
def export_view(request, character):
    return _download(transfer.export_character(character), str(character), timezone.now())


@gm_only
def snapshot_download(request, pk):
    snap = get_object_or_404(CharacterSnapshot, pk=pk)
    return _download(snap.data, f"{snap.character}-level-{snap.level}", snap.created)


def _report(request, err):
    shown = err.errors[:15]
    more = len(err.errors) - len(shown)
    messages.error(request, " · ".join(shown) + (" " + _("… and {n} more.", n=more) if more > 0 else ""))


@gm_only
@require_POST
def import_view(request):
    try:
        data = transfer.parse_upload(request.FILES.get("file"))
        character = transfer.import_character(data, request.POST.get("name", "").strip(),
                                              request.POST.get("password", ""))
    except transfer.TransferError as err:
        _report(request, err)
        return redirect("gm_settings")
    messages.success(request, _("{name} imported as a new character.", name=character))
    return redirect(character.get_absolute_url())


@gm_only
@require_POST
def duplicate_view(request, pk):
    original = get_object_or_404(Character, pk=pk)
    name = request.POST.get("name", "").strip() or _("{name} (copy)", name=original)
    try:
        copy = transfer.duplicate_character(original, name, request.POST.get("password", ""))
    except transfer.TransferError as err:
        _report(request, err)
        return redirect("gm_settings")
    messages.success(request, _("{name} created as a copy.", name=copy))
    return redirect(copy.get_absolute_url())


@gm_only
@require_POST
def drafts_to_trash(request):
    n = trash.abandoned_drafts().update(deleted_at=timezone.now())
    messages.success(request, _("{n} abandoned draft(s) moved to the trash.", n=n))
    return redirect("gm_settings")


@gm_only
@require_POST
def trash_action(request, kind, pk):
    if kind not in trash.KINDS:
        raise Http404
    obj = get_object_or_404(trash.trashed(kind), pk=pk)
    if request.POST.get("action") == "purge":
        obj.delete()
        messages.success(request, _("{name} deleted for good.", name=obj))
    else:
        obj.deleted_at = None
        obj.save(update_fields=["deleted_at"])
        messages.success(request, _("{name} restored.", name=obj))
    return redirect("gm_settings")
