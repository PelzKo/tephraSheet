from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify

from rules.extensions import is_offered, offer
from rules.lang import get_language
from rules.lang import gettext as _
from rules.registry import get_registry

from . import content
from .models import WikiPage, WikiRevision

MAX_HITS = 30


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
    for ch in content.reference(lang):
        for s in ch["sections"]:
            if ql in s["title"].lower() or ql in s["body"].lower():
                hits.append({"kind": _("Rules"), "title": s["title"], "url": f"/wiki/rules/{ch['slug']}/#{s['slug']}",
                             "snippet": _snippet(s["body"], q)})
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
        "chapters": content.reference(lang), "races": offer(get_registry().races.values())})


def page(request, slug):
    p = get_object_or_404(WikiPage, slug=slug)
    return render(request, "wiki/page.html", {"title": p.title, "html": content.render(p.body), "page": p})


def edit(request, slug=None):
    p = get_object_or_404(WikiPage, slug=slug) if slug else None
    if request.method == "POST":
        title = request.POST.get("title", "").strip()[:160]
        body = request.POST.get("body", "")
        name = request.POST.get("name", "").strip()[:80]
        if not title:
            messages.error(request, _("Give the page a title."))
            return render(request, "wiki/edit.html", {"page": p, "title": title, "body": body, "name": name})
        if request.POST.get("delete") and p and request.user.is_staff:
            p.delete()
            messages.success(request, _("Page deleted."))
            return redirect("wiki")
        if p is None:
            base = slugify(title)[:100] or "page"
            new_slug, n = base, 2
            while WikiPage.objects.filter(slug=new_slug).exists():
                new_slug, n = f"{base}-{n}", n + 1
            p = WikiPage(slug=new_slug)
        else:
            WikiRevision.objects.create(page=p, title=p.title, body=p.body, edited_by=p.updated_by)
        p.title, p.body, p.updated_by = title, body, name
        p.language = request.POST.get("language", "") if request.POST.get("language", "") in ("", get_language()) else ""
        p.save()
        messages.success(request, _("Page saved."))
        return redirect(p)
    return render(request, "wiki/edit.html", {"page": p, "title": p.title if p else "", "body": p.body if p else "",
                                              "name": p.updated_by if p else ""})


def help_page(request, slug):
    d = next((d for d in content.docs(get_language()) if d["slug"] == slug), None)
    if not d:
        raise Http404
    return render(request, "wiki/page.html", {"title": d["title"], "html": content.render(d["body"]), "kind": _("Help")})


def rules_chapter(request, slug):
    ch = next((c for c in content.reference(get_language()) if c["slug"] == slug), None)
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
