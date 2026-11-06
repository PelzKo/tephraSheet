"""Automatons of a character: the editor page (one form like the Automaton Crafting Sheet). Card actions live in
sheet.play_action."""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from rules.engine import automaton as auto_rules
from rules.engine import tables
from rules.lang import gettext as _
from rules.registry import get_registry

from .. import access
from ..models import Automaton

AUG_ROWS = 2  # empty augment rows offered beyond the filled ones
MISC_STATS = ("acc", "eva", "stk", "def", "pri", "spd", "wnd", "hp")


def _int(value, default=0):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def _augs(post, prefix, n, reg):
    out = []
    for i in range(n):
        slug = post.get(f"{prefix}{i}-slug", "")
        if slug in reg.augments:
            out.append([slug, max(1, min(4, _int(post.get(f"{prefix}{i}-mq"), 1)))])
    return out


def _from_post(auto, post, character):
    reg = get_registry()
    auto.name = post.get("name", "").strip()[:80] or auto.name or _("Automaton")
    if post.get("type") in auto_rules.TYPES:
        auto.type = post["type"]
    auto.marque = max(1, min(4, _int(post.get("marque"), 1)))
    auto.advanced, auto.diy = bool(post.get("advanced")), bool(post.get("diy"))
    auto.movement = {part: post.get(f"move-{part}") for part in ("torso", "groin")
                     if post.get(f"move-{part}") in auto_rules.MOVEMENT}
    auto.core_augments = _augs(post, "core", _int(post.get("core_rows")), reg)
    limbs = []
    for i in range(_int(post.get("limb_count"))):
        if post.get(f"limb{i}-remove"):
            continue
        limbs.append({"name": post.get(f"limb{i}-name", "").strip()[:40] or _("Limb #{n}", n=len(limbs) + 1),
                      "material": post.get(f"limb{i}-material") if post.get(f"limb{i}-material") in tables.MATERIAL_SLOTS
                      else "metal",
                      "beta": bool(post.get(f"limb{i}-beta")),
                      "augments": _augs(post, f"limb{i}-aug", _int(post.get(f"limb{i}-rows")), reg)})
    if post.get("action") == "add_limb":
        limbs.append({"name": _("Limb #{n}", n=len(limbs) + 1), "material": "metal", "beta": False, "augments": []})
    auto.limbs = limbs
    auto.specialties = [s for s in post.getlist("specialties") if s in reg.specialties]
    auto.misc = {k: _int(post.get(f"misc-{k}")) for k in MISC_STATS if _int(post.get(f"misc-{k}"))}
    items = {str(i.pk): i for i in character.items.all()}
    auto.weapon = items.get(post.get("weapon")) if items.get(post.get("weapon"), None) and \
        items[post["weapon"]].is_weapon else None
    auto.armor = items.get(post.get("armor")) if items.get(post.get("armor"), None) and \
        items[post["armor"]].kind == "armor" else None
    auto.equipment = post.get("equipment", "")[:2000]
    auto.notes = post.get("notes", "")[:4000]


def _rows(augs, n_extra):
    return [{"i": i, "slug": a[0], "mq": a[1]} for i, a in enumerate(augs)] + \
        [{"i": len(augs) + j, "slug": "", "mq": 1} for j in range(n_extra)]


@access.character_view
def automaton_edit(request, character, auto_id=None):
    auto = get_object_or_404(Automaton, pk=auto_id, character=character) if auto_id else None
    if request.method == "POST":
        if auto and request.POST.get("action") == "delete":
            auto.delete()
            messages.success(request, _("{name} removed.", name=auto.name))
            return redirect(f"{character.get_absolute_url()}?tab=pets")
        auto = auto or Automaton(character=character)
        _from_post(auto, request.POST, character)
        auto.save()
        if request.POST.get("action") == "done":
            return redirect(f"{character.get_absolute_url()}?tab=pets")
        return redirect("automaton_edit", pk=character.pk, auto_id=auto.pk)
    reg = get_registry()
    t = auto_rules.TYPES[auto.type if auto else "steamer"]
    known = set(character.augments)
    core_options = sorted((a for a in reg.augments.values() if t["core"] in a["lists"]),
                          key=lambda a: (a["slug"] not in known, a["name"]))
    limb_options = sorted((a for a in reg.augments.values() if "prosthetic" in a["lists"]),
                          key=lambda a: (a["slug"] not in known, a["name"]))
    sheet = auto.compute() if auto else None
    limbs = [dict(limb, i=i, rows=_rows(limb.get("augments", []), AUG_ROWS))
             for i, limb in enumerate(auto.limbs if auto else [])]
    return render(request, "characters/automaton_edit.html", {
        "character": character, "auto": auto, "sheet": sheet, "types": Automaton.TYPE_CHOICES,
        "movement": list(auto_rules.MOVEMENT), "core_rows": _rows(auto.core_augments if auto else [], AUG_ROWS + 1),
        "core_options": core_options, "limb_options": limb_options, "known": known, "limbs": limbs,
        "materials": list(tables.MATERIAL_SLOTS), "misc_stats": MISC_STATS, "stat_labels": tables.COMBAT_STAT_LABELS,
        "specialties": sorted(reg.specialties.values(), key=lambda s: (s["skill"] or "", s["name"])),
        "weapons": [i for i in character.items.all() if i.is_weapon],
        "armors": [i for i in character.items.all() if i.kind == "armor"],
    })
