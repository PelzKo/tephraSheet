"""Admin mode: raise/lower any value and edit choices without rule validation."""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from rules.engine import tables
from rules.registry import get_registry

from .. import access
from ..models import Character, CustomModifier
from .sheet import _respond

MISC_KEYS = set(tables.COMBAT_STATS) | {"soak", "swim", "climb", "fly", "ap"} | \
    {f"attr:{a}" for a in tables.ATTRIBUTES} | {f"skill:{s}" for s in tables.ALL_SKILLS}


@require_POST
def toggle_admin(request, pk):
    character = get_object_or_404(Character, pk=pk)
    if not access.admin_mode_allowed(request, character):
        messages.error(request, "Admin mode is not allowed.")
        return redirect("sheet", pk=pk)
    on = request.POST.get("on") == "1"
    access.set_admin_mode(request, character, on)
    messages.info(request, "Admin mode on: values can be changed freely." if on else "Admin mode off.")
    return redirect(request.POST.get("next") or character.get_absolute_url())


@require_POST
@access.admin_view
def misc_adjust(request, character):
    key = request.POST.get("key", "")
    if key in MISC_KEYS:
        try:
            delta = int(request.POST.get("delta", 0))
        except ValueError:
            delta = 0
        misc = dict(character.misc)
        misc[key] = misc.get(key, 0) + delta
        if not misc[key]:
            del misc[key]
        character.misc = misc
        character.save(update_fields=["misc"])
    return _respond(request, character)


@access.admin_view
def edit_choices(request, character):
    reg = get_registry()
    if request.method == "POST":
        p = request.POST
        action = p.get("action", "save")
        if action == "save":
            if p.get("race") in reg.races:
                character.race = p["race"]
            for f in ("name", "player_name", "religion", "age", "height", "weight", "nationality_custom"):
                if f in p:
                    setattr(character, f, p.get(f, "")[:120])
            if p.get("nationality") in reg.nationalities:
                character.nationality = p["nationality"]
            for f in ("level", "xp", "target_level"):
                try:
                    setattr(character, f, max(0 if f == "xp" else 1, min(99 if f == "xp" else 12, int(p.get(f)))))
                except (TypeError, ValueError):
                    pass
            character.fixed_traits = [k for k in p.getlist("fixed_traits") if k in reg.traits]
            character.random_traits = [k for k in p.getlist("random_traits") if k in reg.traits]
            choices = {}
            for k in character.fixed_traits + character.random_traits:
                if p.get(f"choice:{k}"):
                    choices[k] = p[f"choice:{k}"]
            character.trait_choices = choices
            skills = {}
            for s in tables.ALL_SKILLS:
                try:
                    v = int(p.get(f"skill:{s}", 0) or 0)
                except ValueError:
                    v = 0
                if v:
                    skills[s] = v
            character.skills = skills
            character.stories = [s for s in p.getlist("stories") if s in reg.stories]
            specs = []
            for slug, level in character.specialties:
                if p.get(f"remove_spec:{slug}"):
                    continue
                try:
                    level = int(p.get(f"spec_level:{slug}", level))
                except ValueError:
                    pass
                specs.append([slug, level])
            character.specialties = specs
            messages.success(request, "Saved (no rule validation in admin mode).")
        elif action == "add_specialty":
            slug = p.get("slug")
            if slug in reg.specialties:
                try:
                    level = int(p.get("level") or character.level)
                except ValueError:
                    level = character.level
                character.specialties = list(character.specialties) + [[slug, level]]
        elif action == "add_body_augment":
            slug = p.get("slug")
            if slug in reg.augments:
                character.body_augments = list(character.body_augments) + [[slug, int(p.get("marque", 1))]]
        elif action == "remove_body_augment":
            character.body_augments = [a for a in character.body_augments if a[0] != p.get("slug")]
        elif action == "add_modifier":
            try:
                CustomModifier.objects.create(character=character, source=p.get("source", "Custom")[:120],
                                              stat=p.get("stat"), value=int(p.get("value")),
                                              when=p.get("when", "always"), scope=p.get("scope", "character"))
            except (TypeError, ValueError):
                messages.error(request, "Invalid modifier.")
        elif action == "remove_modifier":
            character.custom_modifiers.filter(pk=p.get("id")).delete()
        elif action == "reset_misc":
            character.misc = {}
        character.save()
        return redirect("edit_choices", pk=character.pk)
    race = reg.races.get(character.race)
    all_traits = [t for t in reg.traits.values()]
    specialties = sorted(reg.specialties.values(), key=lambda s: (s["attribute"], s["skill"] or "", s["name"]))
    essence = [a for a in reg.augments.values() if set(a["lists"]) & {"essence", "prosthetic"}]
    return render(request, "characters/edit_choices.html", {
        "character": character, "races": reg.races.values(), "race": race,
        "nationalities": reg.nationalities.values(), "all_traits": all_traits,
        "skills_by_attr": tables.SKILLS, "stories": reg.stories.values(),
        "owned": [(reg.specialties[s], lvl) for s, lvl in character.specialties if s in reg.specialties],
        "specialties": specialties, "body_augments": [(reg.augments[s], m) for s, m in character.body_augments
                                                      if s in reg.augments],
        "essence_augments": essence, "modifiers": character.custom_modifiers.all(),
        "stat_choices": CustomModifier.STAT_CHOICES, "scope_choices": CustomModifier.SCOPE_CHOICES,
        "when_choices": CustomModifier.WHEN_CHOICES, "attributes": tables.ATTRIBUTES,
        "misc": character.misc,
    })
