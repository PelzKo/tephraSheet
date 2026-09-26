"""Level-up (p.27) and learning augments."""

import random

from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from rules.engine import leveling, tables
from rules.registry import get_registry

from .. import access, services
from .wizard import augment_options, specialty_options


def _delta_from(post):
    delta = {}
    two = post.get("skill_two")
    if two in tables.ALL_SKILLS:
        delta[two] = delta.get(two, 0) + 2
    for key in ("skill_one_a", "skill_one_b"):
        s = post.get(key)
        if s in tables.ALL_SKILLS:
            delta[s] = delta.get(s, 0) + 1
    return delta


def _catch_up(character):
    return character.level < character.target_level


def _state_with_delta(character, delta):
    state = character.to_state()
    for s, p in delta.items():
        state.skills[s] = state.skills.get(s, 0) + p
    state.level += 1
    return state


@access.character_view
def levelup(request, character):
    catch_up = _catch_up(character)
    if character.level >= tables.MAX_LEVEL or (not catch_up and character.xp < tables.XP_PER_LEVEL
                                                and not access.in_admin_mode(request, character)):
        messages.info(request, f"You need {tables.XP_PER_LEVEL} XP to level up.")
        return redirect("sheet", pk=character.pk)
    new_level = character.level + 1
    if request.method == "POST":
        if request.POST.get("action") == "random":
            errors = services.random_levelup(character, random.Random(), from_xp=not catch_up)
        else:
            delta = _delta_from(request.POST)
            retrofit = (request.POST.get("retrofit_old", ""), request.POST.get("retrofit_new", ""))
            specialty = request.POST.get("specialty", "")
            errors = [] if specialty else ["Choose a new specialty."]
            if not errors:
                options = {s: request.POST.get(f"opt:{s}", "") for s in (specialty, retrofit[1]) if s}
                errors = services.apply_levelup(character, delta, specialty, retrofit=retrofit, from_xp=not catch_up,
                                                options=options)
        if errors:
            character.refresh_from_db()
            for e in errors:
                messages.error(request, e)
            return redirect("levelup", pk=character.pk)
        messages.success(request, f"{character.name} reached level {character.level}!")
        if not _catch_up(character) and catch_up:
            character.money_on_hand = services.starting_money(character.level)
            character.save(update_fields=["money_on_hand"])
        sheet = character.compute()
        if sheet.stats["aug"].total > len(character.augments):
            messages.info(request, "You can learn new augments.")
            return redirect("augments", pk=character.pk)
        if _catch_up(character):
            return redirect("levelup", pk=character.pk)
        return redirect("sheet", pk=character.pk)
    reg = get_registry()
    owned = [reg.specialties[s] for s, _ in character.specialties if s in reg.specialties]
    sheet = character.compute()
    return render(request, "characters/levelup.html", {
        "character": character, "new_level": new_level, "sheet": sheet, "catch_up": catch_up,
        "skills_by_attr": tables.SKILLS, "retrofit": leveling.retrofit_allowed(new_level),
        "owned": owned, "ap_now": tables.action_points(character.level),
        "ap_new": tables.action_points(new_level),
    })


@require_POST
@access.character_view
def levelup_options(request, character):
    """HTMX partial: specialties eligible after applying the chosen skill points."""
    delta = _delta_from(request.POST)
    errors = leveling.validate_levelup_skills(delta) if delta else ["Choose your skill points first."]
    state = _state_with_delta(character, delta)
    sheet, groups = specialty_options(character, extra_state=state)
    reg = get_registry()
    retrofit_targets = []
    old = request.POST.get("retrofit_old")
    if old in reg.specialties:
        attr = reg.specialties[old]["attribute"]
        retrofit_targets = sorted((s for s in reg.specialties.values() if s["attribute"] == attr),
                                  key=lambda s: (s["skill"] or "", s["name"]))
    return render(request, "characters/partials/levelup_options.html", {
        "character": character, "groups": groups, "errors": errors, "sheet": sheet,
        "selected": request.POST.get("specialty", ""), "retrofit_targets": retrofit_targets,
        "retrofit_new": request.POST.get("retrofit_new", ""), "stat_cols": tables.COMBAT_STATS,
    })


@access.character_view
def augments_view(request, character):
    if request.method == "POST":
        action = request.POST.get("action")
        slug = request.POST.get("slug", "")
        if action == "add":
            errors = services.set_augments(character, list(character.augments) + [slug])
            for e in errors:
                messages.error(request, e)
        elif action == "swap":
            # Retrofitting augments: when learning a new one you may swap one of the same skill.
            old = request.POST.get("old", "")
            reg = get_registry()
            if old in character.augments and slug in reg.augments and old in reg.augments and \
                    reg.augments[old]["skill"] == reg.augments[slug]["skill"]:
                augs = [a for a in character.augments if a != old]
                errors = services.set_augments(character, augs + [slug])
                for e in errors:
                    messages.error(request, e)
            else:
                messages.error(request, "Augments can only be swapped for one of the same skill.")
        elif action == "remove" and access.in_admin_mode(request, character):
            character.augments = [a for a in character.augments if a != slug]
        elif action == "random":
            services.random_augments(character, random.Random())
        character.save()
        return redirect("augments", pk=character.pk)
    sheet, groups, lists = augment_options(character)
    reg = get_registry()
    return render(request, "characters/augments.html", {
        "character": character, "sheet": sheet, "groups": groups, "lists": lists,
        "capacity": sheet.stats["aug"].total,
        "known": [reg.augments[a] for a in character.augments if a in reg.augments],
        "admin_mode": access.in_admin_mode(request, character),
    })
