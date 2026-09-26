"""Guided character creation (p.24-26): ten steps, each choosable or random."""

import random

from django.contrib import messages
from django.shortcuts import redirect, render

from catalog.models import ItemTemplate
from rules.engine import creation, tables
from rules.engine.requirements import augment_lists, check_augment, check_specialty, specialty_warnings
from rules.engine.stats import compute
from rules.registry import get_registry

from .. import access, services
from ..models import InventoryItem, NarratorSettings

STEP_TEMPLATES = {n: f"characters/wizard/step{n}.html" for n, _ in creation.STEPS}


def _redirect(character, step):
    return redirect("wizard_step", pk=character.pk, step=step)


def step_done(character, step):
    """Whether a step has the data it needs (for the progress bar)."""
    if step == 1:
        return bool(character.race and character.nationality and character.random_traits)
    if step == 2:
        return not creation.validate_creation_skills(character.skills)
    if step == 4:
        return len(character.specialties) >= tables.CREATION_SPECIALTIES
    if step == 10:
        return bool(character.name and character.password)
    return step < character.wizard_step


@access.character_view
def wizard(request, character, step=None):
    if character.status != "draft" and not access.in_admin_mode(request, character):
        return redirect("sheet", pk=character.pk)
    step = step or character.wizard_step
    step = max(1, min(10, int(step)))
    if step > 1 and not character.race:
        return _redirect(character, 1)
    if request.method == "POST":
        return handle_post(request, character, step)
    if step > character.wizard_step:
        character.wizard_step = step
        character.save(update_fields=["wizard_step"])
    ctx = {"character": character, "step": step, "steps": [
        {"n": n, "label": label, "done": step_done(character, n), "current": n == step}
        for n, label in creation.STEPS]}
    ctx.update(STEP_CONTEXT[step](request, character))
    return render(request, STEP_TEMPLATES[step], ctx)


def handle_post(request, character, step):
    action = request.POST.get("action", "save")
    # Per-item buttons encode their argument: name="action" value="add:<slug>".
    action, _, arg = action.partition(":")
    if arg:
        post = request.POST.copy()
        post["slug"] = arg
        request.POST = post
    rng = random.Random()
    if action == "random_all":
        services.random_all(character, rng)
        messages.success(request, "Random character rolled. Check each step, then set a name and password.")
        return _redirect(character, 10)
    if action == "random":
        services.random_step(character, step, rng)
        messages.info(request, f"Step {step} filled randomly.")
        return _redirect(character, step)
    errors = STEP_SAVE[step](request, character, action) or []
    for e in errors:
        messages.error(request, e)
    if errors or action in ("save", "roll", "reroll", "race", "add", "remove", "equip"):
        return _redirect(character, step)
    if action == "back":
        return _redirect(character, step - 1)
    if action == "finish":
        return finish(request, character)
    nxt = min(10, step + 1)
    if nxt > character.wizard_step:
        character.wizard_step = nxt
        character.save(update_fields=["wizard_step"])
    return _redirect(character, nxt)


# --------------------------------------------------------------------------- step 1
def ctx_step1(request, character):
    reg = get_registry()
    settings = NarratorSettings.get()
    race = reg.races.get(character.race)
    ctx = {"races": list(reg.races.values()), "race": race, "settings": settings,
           "nationalities": list(reg.nationalities.values()), "religions": services.RELIGIONS,
           "attributes": tables.ATTRIBUTES}
    if race:
        slots = creation.trait_slots(race["slug"])
        ctx["slots"] = slots
        ctx["fixed"] = [dict(t, key=f"{race['slug']}/{t['slug']}") for t in race["fixed"]]
        ctx["random_table"] = [dict(t, key=f"{race['slug']}/{t['slug']}") for t in race["random"]]
        ctx["chosen_random"] = [reg.traits[k] for k in character.random_traits if k in reg.traits]
        ctx["nat_stories"] = creation.nationality_stories(character.nationality, race["slug"])
        ctx["nat_story"] = next((s for s in character.stories
                                 if reg.stories.get(s, {}).get("type") == "nationality"), "")
        ctx["choice_traits"] = [reg.traits[k] | {"key": k} for k in character.fixed_traits + character.random_traits
                                if k in reg.traits and reg.traits[k].get("choice")]
        ctx["can_roll"] = not character.random_traits or settings.allow_reroll_random_trait
    return ctx


def save_step1(request, character, action):
    reg = get_registry()
    p = request.POST
    errors = []
    race = p.get("race", character.race)
    if race in reg.races:
        services.set_race(character, race)
    if action == "race":
        character.save()
        return []
    settings = NarratorSettings.get()
    slots = creation.trait_slots(character.race) if character.race else {}
    if slots.get("fixed_choose"):
        picked = [k for k in p.getlist("fixed_traits") if k in reg.traits]
        if len(picked) > slots["fixed_choose"]:
            errors.append(f"Choose only {slots['fixed_choose']} racial traits.")
            picked = picked[: slots["fixed_choose"]]
        character.fixed_traits = picked
    chosen = [k for k in p.getlist("chosen_random") if k in reg.traits and k.startswith(f"{character.race}/")]
    if "chosen_random_submitted" in p and slots:
        if settings.allow_choose_random_trait:
            # Narrator lets players pick all random traits instead of rolling.
            character.random_traits = chosen[: slots["random_count"]]
        elif slots.get("random_choose"):
            # Gnome: choose one, roll the rest (the rolled ones are kept unless they duplicate the choice).
            rolled = [k for k in character.random_traits[slots["random_choose"]:] if k not in chosen]
            character.random_traits = chosen[: slots["random_choose"]] + rolled
    if action in ("roll", "reroll"):
        if character.random_traits and not settings.allow_reroll_random_trait and action == "reroll":
            errors.append("The narrator doesn't allow re-rolling racial traits.")
        else:
            if action == "reroll":
                keep = character.random_traits[: slots.get("random_choose", 0)] if slots.get("random_choose") else []
                character.random_traits = keep
            services.roll_random_traits(character)
    for key in list(character.fixed_traits) + list(character.random_traits):
        value = p.get(f"choice:{key}")
        if value:
            character.trait_choices = dict(character.trait_choices, **{key: value})
    nat = p.get("nationality", character.nationality)
    if nat in reg.nationalities:
        if nat != character.nationality:
            services.set_nationality_story(character, "")
        character.nationality = nat
    character.nationality_custom = p.get("nationality_custom", character.nationality_custom)[:80]
    story = p.get("nationality_story")
    if story is not None:
        valid = {s["slug"] for s in creation.nationality_stories(character.nationality, character.race)}
        services.set_nationality_story(character, story if story in valid else "")
    character.religion = p.get("religion", character.religion)[:80]
    if action in ("next", "finish"):
        if not character.race:
            errors.append("Choose a race.")
        if slots.get("fixed_choose") and len(character.fixed_traits) != slots["fixed_choose"]:
            errors.append(f"Choose {slots['fixed_choose']} racial traits.")
        if len([k for k in character.random_traits if k.startswith(character.race + "/")]) < slots.get("random_count", 1):
            errors.append("Roll your random racial trait.")
        if not character.nationality:
            errors.append("Choose a nationality.")
        for key in character.fixed_traits + character.random_traits:
            t = reg.traits.get(key)
            if t and t.get("choice") and not character.trait_choices.get(key):
                errors.append(f"Choose an attribute for {t['name']}.")
    services.revalidate(character)
    character.save()
    return errors


# --------------------------------------------------------------------------- step 2/3
def ctx_step2(request, character):
    sheet = character.compute()
    groups = [{"attribute": a, "skills": [{"name": s, "points": character.skills.get(s, 0),
                                           "total": sheet.skills[s].total, "value": sheet.skills[s]}
                                          for s in skills]} for a, skills in tables.SKILLS.items()]
    return {"groups": groups, "sheet": sheet, "pool": tables.CREATION_SKILL_POINTS}


def save_step2(request, character, action):
    alloc = {}
    for s in tables.ALL_SKILLS:
        try:
            v = int(request.POST.get(f"skill:{s}", 0) or 0)
        except ValueError:
            v = 0
        if v:
            alloc[s] = v
    character.skills = alloc
    errors = creation.validate_creation_skills(alloc) if action in ("next", "finish") else []
    services.revalidate(character)
    character.save()
    return errors


def ctx_step3(request, character):
    return {"sheet": character.compute()}


def save_noop(request, character, action):
    return []


# --------------------------------------------------------------------------- step 4
def specialty_options(character, level=None, extra_state=None):
    state = extra_state or character.to_state()
    if level:
        state.level = level
    sheet = compute(state)
    reg = get_registry()
    owned = {s for s, _ in state.specialties}
    groups = {}
    for spec in reg.specialties.values():
        skill = spec["skill"] or "General (Sciences)"
        if spec["skill"] and sheet.skills[spec["skill"]].total < 1 and spec["slug"] not in owned:
            continue
        if spec["general"] and not any(sheet.skills[s].total for s in tables.SCIENCE_SKILLS):
            continue
        ok, reasons = check_specialty(spec, state, sheet)
        groups.setdefault(skill, []).append({"spec": spec, "ok": ok, "reasons": reasons,
                                             "warnings": specialty_warnings(spec, state),
                                             "owned": spec["slug"] in owned})
    order = {s: i for i, s in enumerate(tables.ALL_SKILLS)}
    return sheet, sorted(groups.items(), key=lambda kv: order.get(kv[0], 99))


def ctx_step4(request, character):
    sheet, groups = specialty_options(character)
    reg = get_registry()
    chosen = [reg.specialties[s] for s, _ in character.specialties if s in reg.specialties]
    return {"sheet": sheet, "groups": groups, "chosen": chosen, "needed": tables.CREATION_SPECIALTIES,
            "stat_cols": tables.COMBAT_STATS, "stat_labels": tables.COMBAT_STAT_LABELS}


def save_step4(request, character, action):
    errors = []
    if action == "add":
        if len(character.specialties) >= tables.CREATION_SPECIALTIES:
            return [f"You can only choose {tables.CREATION_SPECIALTIES} specialties now; remove one first."]
        slug = request.POST.get("slug", "")
        errors = services.add_specialties_sequentially(character, [slug], level=1,
                                                       options={slug: request.POST.get(f"opt:{slug}", "")})
    elif action == "remove":
        slug = request.POST.get("slug")
        character.specialties = [s for s in character.specialties if s[0] != slug]
        services.revalidate(character)
    elif action in ("next", "finish") and len(character.specialties) != tables.CREATION_SPECIALTIES:
        errors.append(f"Choose exactly {tables.CREATION_SPECIALTIES} specialties.")
    character.save()
    return errors


# --------------------------------------------------------------------------- step 5
def augment_options(character, state=None):
    state = state or character.to_state()
    sheet = compute(state)
    reg = get_registry()
    lists = augment_lists(state)
    groups = {}
    for aug in reg.augments.values():
        if not lists.intersection(aug["lists"]):
            continue
        ok, reasons = check_augment(aug, state, sheet)
        known = aug["slug"] in state.augments
        key = f"{aug['skill']} – {aug['section']}"
        groups.setdefault(key, []).append({"aug": aug, "ok": ok or known, "reasons": reasons, "known": known,
                                           "marque": tables.marque_for_points(sheet.skills[aug["skill"]].total)})
    return sheet, sorted(groups.items()), lists


def ctx_step5(request, character):
    sheet, groups, lists = augment_options(character)
    reg = get_registry()
    return {"sheet": sheet, "groups": groups, "lists": lists, "capacity": sheet.stats["aug"].total,
            "known": [reg.augments[a] for a in character.augments if a in reg.augments]}


def save_step5(request, character, action):
    errors = []
    if action == "add":
        errors = services.set_augments(character, list(character.augments) + [request.POST.get("slug", "")])
    elif action == "remove":
        character.augments = [a for a in character.augments if a != request.POST.get("slug")]
    character.save()
    return errors


# --------------------------------------------------------------------------- step 6
def ctx_step6(request, character):
    templates = ItemTemplate.objects.all()
    equipped = {i.slot: i for i in character.items.filter(slot__in=["weapon1", "weapon2", "armor", "deflection"])}
    return {"weapons": templates.filter(kind__in=["melee", "firearm", "bow", "crossbow"]),
            "armors": templates.filter(kind="armor"), "deflections": templates.filter(kind="deflection"),
            "equipped": equipped, "sheet": character.compute()}


def save_step6(request, character, action):
    for slot in ("weapon1", "weapon2", "armor", "deflection"):
        value = request.POST.get(slot)
        if value is None:
            continue
        current = character.items.filter(slot=slot).first()
        if value == "":
            if current:
                current.delete()
            continue
        if current and current.template_id and str(current.template_id) == value:
            continue
        tpl = ItemTemplate.objects.filter(pk=value).first()
        if not tpl:
            continue
        left = character.items.filter(slot="weapon1").first()
        if slot == "weapon2" and left and services.item_hands(character, left) == 2:
            return [f"{left.name} needs both hands, so the right hand stays empty."]
        if current:
            current.delete()
        result = services.equip(character, InventoryItem.from_template(character, tpl), slot)
        if result["moved"]:
            return [f"{tpl.name} needs a free hand: put away {', '.join(result['moved'])}."]
    return []


# --------------------------------------------------------------------------- step 7
def ctx_step7(request, character):
    gear = ItemTemplate.objects.filter(is_starting_gear=True)
    have = {i.template_id: i for i in character.items.filter(slot="carried")}
    return {"gear": [{"t": g, "item": have.get(g.pk)} for g in gear],
            "money": tables.format_money(character.money_on_hand or services.starting_money(1))}


def save_step7(request, character, action):
    selected = set(request.POST.getlist("gear"))
    existing = {str(i.template_id): i for i in character.items.filter(slot="carried", template__is_starting_gear=True)}
    for tid, item in existing.items():
        if tid not in selected:
            item.delete()
        else:
            q = request.POST.get(f"qty:{tid}")
            if q and q.isdigit() and int(q) != item.quantity:
                item.quantity = max(1, int(q))
                item.save(update_fields=["quantity"])
    for tid in selected - set(existing):
        tpl = ItemTemplate.objects.filter(pk=tid, is_starting_gear=True).first()
        if tpl:
            q = request.POST.get(f"qty:{tid}", "1")
            InventoryItem.from_template(character, tpl, quantity=max(1, int(q) if q.isdigit() else 1)).save()
    if not character.money_on_hand:
        character.money_on_hand = services.starting_money(1)
        character.save(update_fields=["money_on_hand"])
    return []


# --------------------------------------------------------------------------- step 8
def ctx_step8(request, character):
    return {"sheet": character.compute()}


# --------------------------------------------------------------------------- step 9
def ctx_step9(request, character):
    reg = get_registry()
    settings = NarratorSettings.get()
    by_type = {}
    for s in reg.stories.values():
        if s["type"] == "nationality":
            continue
        by_type.setdefault(s["type"], []).append(s)
    return {"by_type": by_type, "selected": set(character.stories), "count": settings.background_story_count}


def save_step9(request, character, action):
    reg = get_registry()
    picked = [s for s in request.POST.getlist("stories") if s in reg.stories]
    count = NarratorSettings.get().background_story_count
    backgrounds = [s for s in picked if reg.stories[s]["type"] in ("background", "personality")]
    errors = []
    if len(backgrounds) > count:
        errors.append(f"The narrator allows {count} background/personality stories.")
        return errors
    services.set_background_stories(character, picked)
    character.save()
    return errors


# --------------------------------------------------------------------------- step 10
def ctx_step10(request, character):
    return {"settings": NarratorSettings.get(), "levels": range(1, NarratorSettings.get().max_starting_level + 1)}


def save_step10(request, character, action):
    p = request.POST
    for f in ("name", "player_name", "age", "height", "weight"):
        if f in p:
            setattr(character, f, p.get(f, "").strip()[:120])
    if "personality" in p:
        character.personality = p.get("personality", "")
    if "notes" in p:
        character.notes = p.get("notes", "")
    errors = []
    try:
        level = int(p.get("target_level", character.target_level or 1))
    except ValueError:
        level = 1
    character.target_level = max(1, min(level, NarratorSettings.get().max_starting_level))
    pw, pw2 = p.get("password", ""), p.get("password2", "")
    if pw or pw2:
        if pw != pw2:
            errors.append("Passwords don't match.")
        elif len(pw) < 3:
            errors.append("Password needs at least 3 characters.")
        else:
            character.set_password(pw)
    if action == "finish":
        if not character.name:
            errors.append("Give your character a name.")
        if not character.password:
            errors.append("Set a password for your character.")
    character.save()
    return errors


def finish(request, character):
    missing = [label for n, label in creation.STEPS if n in (1, 2, 4) and not step_done(character, n)]
    if missing:
        messages.error(request, "Incomplete: " + ", ".join(missing))
        return _redirect(character, 10)
    services.finish_creation(character)
    access.unlock(request, character)
    if services.needs_catch_up(character):
        messages.info(request, f"Now level up to level {character.target_level}.")
        return redirect("levelup", pk=character.pk)
    messages.success(request, f"{character.name} is ready for adventure!")
    return redirect("sheet", pk=character.pk)


STEP_CONTEXT = {1: ctx_step1, 2: ctx_step2, 3: ctx_step3, 4: ctx_step4, 5: ctx_step5, 6: ctx_step6,
                7: ctx_step7, 8: ctx_step8, 9: ctx_step9, 10: ctx_step10}
STEP_SAVE = {1: save_step1, 2: save_step2, 3: save_noop, 4: save_step4, 5: save_step5, 6: save_step6,
             7: save_step7, 8: save_noop, 9: save_step9, 10: save_step10}
