"""Narrator pages on /gm/: action log, party overview, group actions and undo."""

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST

from rules.lang import gettext as _
from rules.registry import get_registry

from .. import actionlog
from ..models import ActionLog, Character, Throttle
from .general import card_values
from .sheet import _int, play

PAGE_SIZE = 50
narrator_only = staff_member_required(login_url="gm_login")


@narrator_only
def action_log(request):
    g = request.GET
    qs = ActionLog.objects.select_related("character")
    if g.get("character", "").isdigit():
        qs = qs.filter(character_id=int(g["character"]))
    if g.get("action"):
        qs = qs.filter(action__startswith=g["action"])
    if g.get("actor") in dict(ActionLog.ACTOR_CHOICES):
        qs = qs.filter(actor=g["actor"])
    if parse_date(g.get("start", "")):
        qs = qs.filter(created__date__gte=parse_date(g["start"]))
    if parse_date(g.get("end", "")):
        qs = qs.filter(created__date__lte=parse_date(g["end"]))
    page = Paginator(qs, PAGE_SIZE).get_page(g.get("page"))
    return render(request, "characters/gm/action_log.html", {
        "page": page, "rows": [(e, actionlog.changes(e)) for e in page],
        "characters": Character.objects.order_by("name"), "actors": ActionLog.ACTOR_CHOICES,
        "actions": sorted({a.split(":")[0] for a in ActionLog.objects.values_list("action", flat=True).distinct()}),
        "f": g})


def _stance_label(slug):
    reg = get_registry()
    if slug.startswith("trait:"):
        return reg.traits.get(slug[6:], {}).get("name", slug)
    return reg.specialties.get(slug, {}).get("name") or (_("Footing") if slug == "footing" else slug)


def party_rows():
    now = timezone.now()
    fails = dict(Throttle.objects.filter(key__startswith="unlock-fail:", expires__gt=now).values_list("key", "count"))
    rows = []
    for c in Character.objects.filter(status="active").prefetch_related("effects").order_by("name"):
        values = card_values(c)
        rows.append({
            "c": c, "max_hp": values["max_hp"], "max_wounds": values["max_wounds"],
            "hp": c.current_hp if c.current_hp is not None else values["max_hp"],
            "ap": c.fight.get("ap") if c.fight.get("active") else None,
            "stance": _stance_label(c.stance) if c.stance else "",
            "effects": [e.text for e in c.effects.all() if e.active],
            "fails": fails.get(f"unlock-fail:{c.pk}", 0)})
    return rows


@narrator_only
def party(request):
    template = "characters/gm/_party_table.html" if request.headers.get("HX-Request") else "characters/gm/party.html"
    return render(request, template, {"rows": party_rows()})


GROUP_ACTIONS = {"xp": "xp", "breather": "breather", "end_fight": "fight_stop"}


@narrator_only
@require_POST
def group_action(request):
    """XP / breather / end of fight for every active character, each through the normal play action (logged)."""
    what = request.POST.get("what", "")
    if what not in GROUP_ACTIONS:
        return redirect("gm_settings")
    data = {"delta": _int(request.POST.get("amount"))} if what == "xp" else {}
    # Each character's own info bars are collected and shown with its name in one message.
    seen = len(list(messages.get_messages(request)))
    lines = []
    for c in Character.objects.filter(status="active").order_by("name"):
        play(request, c.pk, GROUP_ACTIONS[what], data)
        texts = [str(m) for m in messages.get_messages(request)][seen:]
        seen += len(texts)
        lines.append(f"{c}: {' '.join(texts)}" if texts else str(c))
    if lines:
        messages.success(request, _("Done for {n} characters.", n=len(lines)) + " " + " · ".join(lines))
    else:
        messages.info(request, _("No active characters."))
    return redirect("gm_settings")


@narrator_only
@require_POST
def undo(request, pk):
    character = get_object_or_404(Character, pk=pk)
    entry = actionlog.last_entry(character, levelup=request.POST.get("what") == "levelup")
    if not entry:
        messages.error(request, _("Nothing to undo."))
    else:
        try:
            actionlog.undo(request, entry)
        except actionlog.UndoError as exc:
            messages.error(request, str(exc))
        else:
            messages.success(request, _("Undone: {changes}", changes=actionlog.summary(entry.after, entry.before)))
    return redirect(f"{character.get_absolute_url()}?tab=story")
