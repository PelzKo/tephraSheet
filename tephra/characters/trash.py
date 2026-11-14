"""Trash (S3): characters, wiki pages and custom catalog items get ``deleted_at`` instead of being deleted.

The narrator restores or deletes them for good on /gm/; ``purge_trash`` deletes what has been in the trash
for TRASH_DAYS. Book catalog items the narrator hid also carry ``deleted_at`` but never leave the database
(``seed_catalog`` would bring them back), so they are not part of the trash.
"""
from datetime import timedelta

from django.utils import timezone

from catalog.models import ItemTemplate
from wiki.models import WikiPage
from .models import Character

TRASH_DAYS = 30
DRAFT_DAYS = 30  # N3: drafts untouched this long count as abandoned


def trashed(kind):
    """Queryset of the rows of one kind in the trash ("character", "wiki", "item")."""
    if kind == "character":
        return Character.all_objects.filter(deleted_at__isnull=False)
    if kind == "wiki":
        return WikiPage.all_objects.filter(deleted_at__isnull=False)
    if kind == "item":
        return ItemTemplate.objects.filter(deleted_at__isnull=False, source="custom")
    raise KeyError(kind)


KINDS = ("character", "wiki", "item")


def entries():
    """Everything in the trash, newest first: [{kind, obj, deleted_at, purge_on}]."""
    out = [{"kind": k, "obj": o, "deleted_at": o.deleted_at, "purge_on": o.deleted_at + timedelta(days=TRASH_DAYS)}
           for k in KINDS for o in trashed(k)]
    return sorted(out, key=lambda e: e["deleted_at"], reverse=True)


def purge(days=TRASH_DAYS):
    """Delete for good what has been in the trash for ``days``; {kind: count}."""
    limit = timezone.now() - timedelta(days=days)
    return {k: trashed(k).filter(deleted_at__lte=limit).delete()[1].get(trashed(k).model._meta.label, 0)
            for k in KINDS}


def abandoned_drafts():
    return Character.objects.filter(status="draft", updated__lt=timezone.now() - timedelta(days=DRAFT_DAYS))
