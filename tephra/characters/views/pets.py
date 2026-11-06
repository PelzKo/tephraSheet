"""Animals of a character (Pets & Predators): the editor page. Play actions live in sheet.play_action."""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from rules.engine import pets as pet_rules
from rules.engine import tables
from rules.extensions import enabled
from rules.lang import gettext as _
from rules.registry import get_registry

from .. import access
from ..models import Pet

PET_ATTRS = pet_rules.ATTRS


def presets():
    return get_registry().animals.get("presets", {})


def _int(value, default=0):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def _from_post(pet, post, animals):
    pet.name = post.get("name", "").strip()[:100] or pet.name or _("Animal")
    if post.get("template") in animals["templates"]:
        pet.template = post["template"]
    pet.origin = post.get("origin") if post.get("origin") in dict(Pet.ORIGIN_CHOICES) else pet.origin
    pet.movement = [m for m in post.getlist("movement") if m in animals["movement"]]
    pet.traits = [[s, post.get(f"choice:{s}", "").strip()[:60] or None] for s in post.getlist("traits")
                  if s in animals["traits"]]
    pet.stories = [s for s in post.getlist("stories") if s in animals["stories"]]
    pet.wild = bool(post.get("wild"))
    pet.sp_bonus = max(-5, min(20, _int(post.get("sp_bonus"))))
    pet.levels = max(0, min(30, _int(post.get("levels"))))
    pet.notes = post.get("notes", "")[:4000]
    rows = []
    for i in range(_int(post.get("row_count"))):
        attrs = {a: _int(post.get(f"row{i}-{a}")) for a in PET_ATTRS if _int(post.get(f"row{i}-{a}"))}
        rows.append({"attrs": attrs, "major": post.get(f"row{i}-major", ""), "minor": post.get(f"row{i}-minor", "")})
    pet.derived = rows


def _requirement_name(req, animals):
    if req == "any-venom":
        return _("a venom trait")
    if req.startswith("size:"):
        return _("medium or large size")
    return _(" or ").join(animals["traits"].get(r, {}).get("name", r) for r in req.split("|"))


def validate(pet, animals):
    """Problems shown after saving (they never block: the narrator has the last word)."""
    out = []
    owned = {s for s, _c in pet.traits}
    tpl = animals["templates"].get(pet.template, {})
    for slug in owned:
        t = animals["traits"][slug]
        for req in t.get("requires", []):
            if req == "any-venom":
                ok = any(animals["traits"][s].get("is_venom") for s in owned)
            elif req.startswith("size:"):
                ok = tpl.get("size") in ("medium", "large")
            else:
                ok = bool(set(req.split("|")) & owned)
            if not ok:
                out.append(_("{trait} needs {req}.", trait=t["name"], req=_requirement_name(req, animals)))
    for i, row in enumerate(pet.derived, 1):
        if sum(row.get("attrs", {}).values()) != 4:
            out.append(_("Derived #{n}: the attribute points should add up to 4.", n=i))
        if row.get("major") and row.get("major") == row.get("minor"):
            out.append(_("Derived #{n}: the +1 stat must differ from the +2 stat.", n=i))
    return out


@access.character_view
def pet_edit(request, character, pet_id=None):
    pet = get_object_or_404(Pet, pk=pet_id, character=character) if pet_id else None
    if pet is None and "pets-and-predators" not in enabled():
        raise Http404
    animals = get_registry().animals
    if request.method == "POST":
        if pet and request.POST.get("action") == "delete":
            pet.delete()
            messages.success(request, _("{name} removed.", name=pet.name))
            return redirect(f"{character.get_absolute_url()}?tab=pets")
        pet = pet or Pet(character=character, template=next(iter(animals["templates"])))
        preset = presets().get(request.POST.get("preset", ""))
        if preset and not pet.pk:
            pet.name, pet.preset, pet.origin = request.POST.get("name") or preset["name"], preset["slug"], "preset"
            pet.template, pet.movement, pet.traits = preset["template"], preset["movement"], preset["traits"]
            pet.stories, pet.derived, pet.wild = preset.get("stories", []), preset.get("derived", []), preset.get("wild", False)
            pet.notes = preset.get("notes", "")
        else:
            _from_post(pet, request.POST, animals)
        pet.save()
        for problem in validate(pet, animals):
            messages.warning(request, problem)
        if request.POST.get("action") == "done":
            return redirect(f"{character.get_absolute_url()}?tab=pets")
        return redirect("pet_edit", pk=character.pk, pet_id=pet.pk)
    sheet = pet_rules.compute_pet(pet.to_state()) if pet else None
    rows = []
    if pet:
        for i in range(sheet["rows"]):
            row = pet.derived[i] if i < len(pet.derived) else {}
            rows.append({"n": i, "attrs": [(a, (row.get("attrs") or {}).get(a, 0)) for a in PET_ATTRS],
                         "major": row.get("major", ""), "minor": row.get("minor", "")})
    chosen = {s: c for s, c in pet.traits} if pet else {}
    return render(request, "characters/pet_edit.html", {
        "character": character, "pet": pet, "sheet": sheet, "rows": rows, "animals": animals,
        "traits": sorted((dict(t, requires_names=[_requirement_name(r, animals) for r in t.get("requires", [])])
                          for t in animals["traits"].values()), key=lambda t: (t["group"], t["name"])),
        "chosen": chosen, "presets": sorted(presets().values(), key=lambda p: p["name"]),
        "majors": [(k, f"+{v}") for k, v in pet_rules.MAJOR.items()], "minors": [(k, f"+{v}") for k, v in pet_rules.MINOR.items()],
        "origins": Pet.ORIGIN_CHOICES, "stat_labels": tables.COMBAT_STAT_LABELS,
    })
