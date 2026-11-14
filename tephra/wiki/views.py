import difflib
from urllib.parse import urlencode

from django.contrib import messages
from django.core.cache import cache
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.utils.text import slugify

from rules.extensions import is_offered, offer
from rules.lang import get_language
from rules.lang import gettext as _
from rules.registry import get_registry

from catalog.models import ItemTemplate
from characters import actionlog
from characters.templatetags.tr_tags import item_desc, item_name

from . import content
from .models import WikiPage, WikiRevision

MAX_HITS = 30
MAX_BODY = 100_000  # characters per page
EDIT_LIMIT, EDIT_WINDOW = 30, 3600  # saves per client IP per hour (the narrator is exempt)


def _pages():
    lang = get_language()
    return WikiPage.objects.filter(language__in=["", lang])


def _snippet(text, q, width=90):
    i = text.lower().find(q.lower())
    if i < 0:
        return text[:width * 2]
    start = max(0, i - width)
    return ("…" if start else "") + text[start:i + len(q) + width] + "…"


def search(q):
    """Hits from wiki pages, app docs, the rules reference and the rule data (current language)."""
    ql = q.lower()
    lang = get_language()
    hits = []
    for p in _pages():
        if ql in p.title.lower() or ql in p.body.lower():
            hits.append({"kind": _("Wiki page"), "title": p.title, "url": p.get_absolute_url(),
                         "snippet": _snippet(p.body, q)})
    for d in content.docs(lang):
        if ql in d["title"].lower() or ql in d["body"].lower():
            hits.append({"kind": _("Help"), "title": d["title"], "url": f"/wiki/help/{d['slug']}/",
                         "snippet": _snippet(d["body"], q)})
    for ch in offer(content.reference(lang)):
        for s in ch["sections"]:
            if ql in s["title"].lower() or ql in s["body"].lower():
                hits.append({"kind": _("Rules"), "title": s["title"], "url": f"/wiki/rules/{ch['slug']}/#{s['slug']}",
                             "snippet": _snippet(s["body"], q)})
    for item in ItemTemplate.offered():
        name, desc = item_name(item.name), item_desc(item)
        if ql in name.lower() or ql in item.name.lower() or ql in desc.lower():
            hits.append({"kind": _("Item"), "title": name, "url": "/catalog/?" + urlencode({"q": item.name}),
                         "snippet": _snippet(desc, q)})
    reg = get_registry()
    for s in offer(reg.specialties.values()):
        if ql in s["name"].lower() or ql in s["name_en"].lower() or ql in s["effect"].lower():
            hits.append({"kind": _("Specialty"), "title": s["name"], "url": f"/wiki/specialty/{s['slug']}/",
                         "snippet": _snippet(s["effect"], q)})
    for a in offer(reg.augments.values()):
        if ql in a["name"].lower() or ql in a["name_en"].lower() or ql in a["text"].lower():
            hits.append({"kind": _("Augment"), "title": a["name"], "url": f"/catalog/augments/?q={a['name']}",
                         "snippet": _snippet(a["text"], q)})
    for t in reg.traits.values():
        if not is_offered(reg.races[t["race"]]):
            continue
        if ql in t["name"].lower() or ql in t["text"].lower():
            hits.append({"kind": _("Racial trait"), "title": f"{t['name']} ({reg.races[t['race']]['name']})",
                         "url": f"/wiki/race/{t['race']}/", "snippet": t["text"]})
    # Titles that match first, then the rest.
    hits.sort(key=lambda h: ql not in h["title"].lower())
    return hits


def wiki_index(request):
    q = request.GET.get("q", "").strip()
    lang = get_language()
    hits = search(q)[:200] if len(q) >= 2 else None
    return render(request, "wiki/index.html", {
        "q": q, "hits": hits, "pages": _pages(), "docs": content.docs(lang),
        "chapters": offer(content.reference(lang)), "races": offer(get_registry().races.values())})


def page(request, slug):
    p = get_object_or_404(WikiPage, slug=slug)
    return render(request, "wiki/page.html", {"title": p.title, "html": content.render(p.body), "page": p})


def _client_ip(request):
    """The client's IP behind the reverse proxy: the last X-Forwarded-For hop is the one the proxy added
    (earlier hops are client-supplied and can be forged)."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    return forwarded.split(",")[-1].strip() or request.META.get("REMOTE_ADDR", "")


def _edit_key(request):
    return f"wiki-edits:{_client_ip(request)}"


def _stamp(p):
    return p.updated.isoformat() if p else ""


def _keep_revision(p):
    WikiRevision.objects.create(page=p, title=p.title, body=p.body, edited_by=p.updated_by)


def edit(request, slug=None):
    p = get_object_or_404(WikiPage, slug=slug) if slug else None
    if request.method == "POST":
        title = request.POST.get("title", "").strip()[:160]
        body = request.POST.get("body", "")
        name = request.POST.get("name", "").strip()[:80]
        # The submitted stamp survives validation errors, so a later save still detects a conflict.
        ctx = {"page": p, "title": title, "body": body, "name": name, "updated": request.POST.get("updated", ""),
               "max_body": MAX_BODY}
        if request.POST.get("delete") and p and request.user.is_staff:
            actionlog.log(request, "wiki:delete", p)
            p.delete()
            messages.success(request, _("Page deleted."))
            return redirect("wiki")
        if not title:
            messages.error(request, _("Give the page a title."))
            return render(request, "wiki/edit.html", ctx)
        if len(body) > MAX_BODY:
            messages.error(request, _("The text is too long (at most {n} characters).", n=MAX_BODY))
            return render(request, "wiki/edit.html", ctx)
        if not request.user.is_staff and cache.get(_edit_key(request), 0) >= EDIT_LIMIT:
            messages.error(request, _("Too many edits from your connection. Please try again later."))
            return render(request, "wiki/edit.html", ctx, status=429)

        def conflict():
            # Someone saved since this form was opened: show both texts; saving again (new stamp) overwrites.
            msg = _("Someone changed this page while you were editing. Compare both texts, then save again to overwrite.")
            messages.error(request, msg)
            return render(request, "wiki/edit.html", dict(ctx, conflict=p, updated=_stamp(p)), status=409)

        if p and request.POST.get("updated") != _stamp(p):
            return conflict()
        language = request.POST.get("language", "") if request.POST.get("language", "") in ("", get_language()) else ""
        if p is None:
            base = slugify(title)[:100] or "page"
            new_slug, n = base, 2
            while WikiPage.objects.filter(slug=new_slug).exists():
                new_slug, n = f"{base}-{n}", n + 1
            p = WikiPage.objects.create(slug=new_slug, title=title, body=body, updated_by=name, language=language)
            actionlog.log(request, "wiki:create", p)
        else:
            with transaction.atomic():
                # Conditional update: a save that slipped in after the check above makes this match nothing.
                saved = WikiPage.objects.filter(pk=p.pk, updated=p.updated).update(
                    title=title, body=body, updated_by=name, language=language, updated=timezone.now())
                if saved:
                    _keep_revision(p)  # p still holds the replaced version
                    actionlog.log(request, "wiki:edit", p, actionlog.values(p, exclude={"updated"}),
                                  actionlog.values(WikiPage.objects.get(pk=p.pk), exclude={"updated"}))
            if not saved:
                p.refresh_from_db()
                return conflict()
        if not request.user.is_staff:  # set, not incr: the file cache's incr drops the timeout
            cache.set(_edit_key(request), cache.get(_edit_key(request), 0) + 1, EDIT_WINDOW)
        messages.success(request, _("Page saved."))
        return redirect(p)
    return render(request, "wiki/edit.html", {
        "page": p, "title": p.title if p else request.GET.get("title", "")[:160], "body": p.body if p else "",
        "name": p.updated_by if p else "", "updated": _stamp(p), "max_body": MAX_BODY})


def _diff(old, new):
    """[(css class, line)] of a unified diff old → new (server-rendered, escaped by the template)."""
    lines = difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm="", n=2)
    return [("add" if ln[0] == "+" else "del" if ln[0] == "-" else "hunk" if ln[0] == "@" else "", ln)
            for ln in list(lines)[2:]]


def history(request, slug):
    p = get_object_or_404(WikiPage, slug=slug)
    revisions = p.revisions.all()
    rev = revisions.filter(pk=request.GET.get("rev")).first() if request.GET.get("rev", "").isdigit() else None
    diff = (_diff(f"# {rev.title}\n\n{rev.body}", f"# {p.title}\n\n{p.body}") if rev else None)
    return render(request, "wiki/history.html", {"page": p, "revisions": revisions, "rev": rev, "diff": diff})


@require_POST
def restore(request, slug, rev):
    if not request.user.is_staff:
        raise Http404
    p = get_object_or_404(WikiPage, slug=slug)
    r = get_object_or_404(WikiRevision, pk=rev, page=p)
    _keep_revision(p)
    before = actionlog.values(p, exclude={"updated"})
    p.title, p.body, p.updated_by = r.title, r.body, r.edited_by
    p.save()
    actionlog.log(request, "wiki:restore", p, before, actionlog.values(p, exclude={"updated"}))
    messages.success(request, _("Version restored. The replaced text is kept in the history."))
    return redirect(p)


def help_page(request, slug):
    d = next((d for d in content.docs(get_language()) if d["slug"] == slug), None)
    if not d:
        raise Http404
    return render(request, "wiki/page.html", {"title": d["title"], "html": content.render(d["body"]), "kind": _("Help")})


def rules_chapter(request, slug):
    ch = next((c for c in offer(content.reference(get_language())) if c["slug"] == slug), None)
    if not ch:
        raise Http404
    sections = [dict(s, html=content.render(s["body"])) for s in ch["sections"]]
    return render(request, "wiki/rules.html", {"chapter": ch, "sections": sections})


def specialty(request, slug):
    s = get_registry().specialties.get(slug)
    if not s:
        raise Http404
    return render(request, "wiki/specialty.html", {"s": s})


def race(request, slug):
    r = get_registry().races.get(slug)
    if not r:
        raise Http404
    return render(request, "wiki/race.html", {"r": r})
