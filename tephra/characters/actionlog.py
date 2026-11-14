"""Action log (who changed what) and the narrator's undo built on it.

``log(request, action, obj, before, after)`` stores only the fields that differ between the two value dicts
(``values()``/``snapshot()``); an action that changed nothing writes no row. Rows older than ``KEEP_DAYS``
are pruned on write, at most once a day."""

import hashlib
import json
from datetime import timedelta

from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from rules.lang import gettext as _

from . import access
from .models import ActionLog, Character, EffectEntry

KEEP_DAYS = 180
SKIP = {"id", "password", "created", "updated"}
# Row keys in a character snapshot. Only effects (switched on/off, never deleted) can be restored by undo.
FIXED_ROWS = ("item", "pet", "automaton", "modifier")


def _text(value):
    return f"[{len(value)} chars #{hashlib.sha1(value.encode()).hexdigest()[:6]}]" if value else ""


def values(obj, exclude=()):
    """Field values of a model instance as plain JSON; long texts become length + short hash."""
    out = {}
    for f in obj._meta.concrete_fields:
        if f.name not in SKIP and f.name not in exclude:
            v = f.value_from_object(obj)
            out[f.name] = _text(v or "") if f.get_internal_type() == "TextField" else v
    return json.loads(json.dumps(out, default=str))


def snapshot(character):
    """The character's fields plus one short line per item, active effect, companion and custom modifier."""
    data = values(character)
    for i in character.items.all():
        data[f"item:{i.pk}"] = f"{i.name} ×{i.quantity} ({i.slot})" + (f" W{i.wounds_taken}" if i.wounds_taken else "")
    data.update({f"effect:{e.pk}": e.text for e in character.effects.filter(active=True)})
    data.update({f"pet:{p.pk}": f"{p.name}: HP−{p.hp_damage} W{p.wounds_taken} V{p.venom_used}"
                 for p in character.pets.all()})
    data.update({f"automaton:{a.pk}": f"{a.name}: HP−{a.hp_lost} W{a.wounds_taken} {','.join(a.toggles)}"
                 for a in character.automatons.all()})
    data.update({f"modifier:{m.pk}": f"{m.source}: {m.stat} {m.value:+d} ({m.when})"
                 for m in character.custom_modifiers.all()})
    return data


def diff(before, after):
    keys = [k for k in sorted(before.keys() | after.keys()) if before.get(k) != after.get(k)]
    return {k: before[k] for k in keys if k in before}, {k: after[k] for k in keys if k in after}


def actor(request):
    if request is None:
        return "system", ""
    if access.is_gm(request):
        return "narrator", request.user.get_username()
    ids = access.unlocked_ids(request)
    if ids:
        return "session", ", ".join(str(c) for c in Character.objects.filter(pk__in=ids).order_by("pk"))[:200]
    return "anonymous", ""


def log(request, action, obj=None, before=None, after=None, character=None, label=""):
    """Write one row. With both ``before`` and ``after`` only the differences are kept (none → no row)."""
    before, after = (json.loads(json.dumps(v, default=str)) if v is not None else None for v in (before, after))
    if before is not None and after is not None:
        before, after = diff(before, after)
        if not before and not after:
            return None
    if character is None:
        character = obj if isinstance(obj, Character) else getattr(obj, "character", None)
    kind, detail = actor(request)
    entry = ActionLog.objects.create(
        actor=kind, actor_detail=detail, ip=access.client_ip(request) if request else "", action=action[:40],
        character=character if character and character.pk else None,
        object_type=obj._meta.model_name if obj is not None else "", object_id=getattr(obj, "pk", None),
        object_label=str(label or obj or "")[:120], before=before or {}, after=after or {})
    if cache.add("actionlog-prune", 1, 24 * 3600):
        ActionLog.objects.filter(created__lt=timezone.now() - timedelta(days=KEEP_DAYS)).delete()
    return entry


def _short(value):
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    return text if len(text) <= 60 else text[:57] + "…"


def changes(entry_or_pair):
    """[(field, old, new)] of a log entry (or a (before, after) pair), values shortened for display."""
    before, after = (entry_or_pair.before, entry_or_pair.after) if isinstance(entry_or_pair, ActionLog) \
        else entry_or_pair
    return [(k, _short(before[k]) if k in before else "–", _short(after[k]) if k in after else "–")
            for k in sorted(before.keys() | after.keys())]


def summary(before, after):
    return "; ".join(f"{k}: {old} → {new}" for k, old, new in changes((before, after)))


# --------------------------------------------------------------------------- undo (narrator)
class UndoError(Exception):
    pass


def last_entry(character, levelup=False):
    """The newest not yet undone play action (or level-up) of the character."""
    qs = character.actions.filter(undone=False)
    return (qs.filter(action="levelup") if levelup else qs.filter(action__startswith="play:")).first()


@transaction.atomic
def undo(request, entry):
    """Restore the before-values of ``entry`` if nothing changed them since (current values == after-values).
    A level-up reversal keeps current HP but takes away the max-HP difference, and drops its LevelLog."""
    character = Character.objects.select_for_update().get(pk=entry.character_id)
    now = snapshot(character)
    keys = set(entry.before) | set(entry.after)
    levelup = entry.action == "levelup"
    if levelup:
        keys.discard("current_hp")
    text_fields = {f.name for f in Character._meta.concrete_fields if f.get_internal_type() == "TextField"}
    fixed = sorted(k for k in keys if k.split(":")[0] in FIXED_ROWS or k in text_fields)
    if fixed:
        raise UndoError(_("Not undone: changes to {what} can't be undone automatically. Change them by hand.",
                          what=", ".join(fixed)))
    moved = sorted(k for k in keys if now.get(k) != entry.after.get(k))
    if moved:
        raise UndoError(_("Not undone: {what} changed again since then.", what=", ".join(moved)))
    old_max = character.compute().max_hp
    for k in keys:
        if k.startswith("effect:"):
            EffectEntry.objects.filter(character=character, pk=int(k[7:])).update(active=k in entry.before)
        else:
            setattr(character, k, entry.before[k])
    if levelup:
        character.level_logs.filter(level=entry.after.get("level")).delete()
        new_max = character.compute().max_hp
        if character.current_hp is not None:
            character.current_hp = max(0, min(new_max, character.current_hp - (old_max - new_max)))
    character.save()
    character.clamp_trackers()
    entry.undone = True
    entry.save(update_fields=["undone"])
    log(request, f"undo:{entry.action}"[:40], character, now, snapshot(character))
