"""Level-up planner: plan the skills, specialty and augments of coming levels and preview the sheet."""

from django.contrib import messages
from django.shortcuts import redirect, render

from rules.engine import leveling, tables
from rules.engine.requirements import check_augment, check_specialty
from rules.engine.stats import compute
from rules.extensions import is_offered, offer
from rules.lang import gettext as _
from rules.registry import get_registry

from .. import access
from ..services import legal_in_state

PREVIEW_STATS = ["ap", "acc", "eva", "stk", "def", "pri", "spd", "hp", "wnd", "aug", "diy", "soak"]


def planned_state(character, upto=None):
    """Character state with every planned level up to ``upto`` applied, plus a check per level:
    [(entry, [problems])]. Specialties are checked against the state right before they are learned."""
    reg = get_registry()
    state = character.to_state()
    checks = []
    for entry in sorted(character.plan, key=lambda e: e["level"]):
        if entry["level"] <= character.level or (upto and entry["level"] > upto):
            continue
        problems = []
        skills = entry.get("skills") or {}
        if skills:
            problems += leveling.validate_levelup_skills(skills)
        for s, pts in skills.items():
            state.skills[s] = state.skills.get(s, 0) + pts
        state.level = entry["level"]
        old, new = (entry.get("retrofit") or ["", ""])[:2]
        if old and new:
            owned = {s for s, _l in state.specialties}
            problems += leveling.validate_retrofit(old, new)
            if not leveling.retrofit_allowed(entry["level"]):
                problems.append(_("Retrofitting specialties is only possible at levels 4, 8 and 12."))
            elif old not in owned:
                problems.append(_("The specialty to replace is not learned."))
            elif new in reg.specialties:
                legal_before = legal_in_state(state)
                state.specialties = [(s, l) for s, l in state.specialties if s != old]
                problems += _spec_problems(reg.specialties[new], state)
                state.specialties.append((new, dict(character.specialties).get(old, entry["level"])))
                broken = [reg.specialties[s]["name"] for s in legal_before - legal_in_state(state) if s != old]
                if broken:
                    problems.append(_("Can't replace {name}: {names} would lose a prerequisite.",
                                      name=reg.specialties[old]["name"], names=", ".join(broken)))
        spec = reg.specialties.get(entry.get("specialty", ""))
        if spec:
            problems += _spec_problems(spec, state)
            state.specialties.append((spec["slug"], entry["level"]))
        sheet = compute(state)
        capacity = sheet.stats["aug"].total
        for slug in entry.get("augments", []):
            aug = reg.augments.get(slug)
            if not aug or slug in state.augments:
                continue
            ok, reasons = check_augment(aug, state, sheet)
            if not is_offered(aug):
                problems.append(_("{name}: not offered by the narrator.", name=aug["name"]))
            elif not ok:
                problems.append(f"{aug['name']}: {'; '.join(reasons)}")
            elif len(state.augments) >= capacity:
                problems.append(_("Only {count} augments can be learned.", count=capacity))
            state.augments.append(slug)
        checks.append((entry, problems))
    return state, checks


def _spec_problems(spec, state):
    if not is_offered(spec):
        return [_("{name}: not offered by the narrator.", name=spec["name"])]
    ok, reasons = check_specialty(spec, state, compute(state))
    return [] if ok else [f"{spec['name']}: {'; '.join(reasons)}"]


def preview_rows(current, preview):
    """Before/after rows of two sheets: (stat rows, changed skill rows)."""
    rows = []
    for stat in PREVIEW_STATS:
        now, then = current.stats[stat].total, preview.stats[stat].total
        rows.append({"stat": stat, "label": _(tables.COMBAT_STAT_LABELS.get(stat, stat.upper())), "now": now,
                     "then": then, "diff": then - now})
    skill_rows = [{"skill": s, "now": current.skills[s].total, "then": preview.skills[s].total,
                   "diff": preview.skills[s].total - current.skills[s].total}
                  for s in tables.ALL_SKILLS if preview.skills[s].total != current.skills[s].total]
    return rows, skill_rows


def planned_for(character, level):
    return next((e for e in character.plan if e["level"] == level), None)


@access.character_view
def planner(request, character):
    reg = get_registry()
    future = list(range(character.level + 1, tables.MAX_LEVEL + 1))
    if request.method == "POST":
        p = request.POST
        try:
            level = int(p.get("level", 0))
        except ValueError:
            level = 0
        plan = [e for e in character.plan if e["level"] != level]
        if p.get("action") == "save" and level in future:
            skills = {}
            for key, pts in (("skill_two", 2), ("skill_one_a", 1), ("skill_one_b", 1)):
                if p.get(key) in tables.ALL_SKILLS:
                    skills[p[key]] = skills.get(p[key], 0) + pts
            entry = {"level": level, "skills": skills,
                     "specialty": p.get("specialty") if p.get("specialty") in reg.specialties else "",
                     "augments": [a for a in p.getlist("augments") if a in reg.augments],
                     "retrofit": [p.get(k) if p.get(k) in reg.specialties else "" for k in ("retrofit_old", "retrofit_new")]
                     if leveling.retrofit_allowed(level) else ["", ""],
                     "note": p.get("note", "").strip()[:500]}
            if skills or entry["specialty"] or entry["augments"] or entry["note"] or all(entry["retrofit"]):
                plan.append(entry)
            messages.success(request, _("Plan for level {level} saved.", level=level))
        elif p.get("action") == "clear":
            plan = []
        character.plan = sorted(plan, key=lambda e: e["level"])
        character.save(update_fields=["plan"])
        return redirect(f"{request.path}?edit={level}")

    try:
        edit = int(request.GET.get("edit") or 0)
    except ValueError:
        edit = 0
    if edit not in future:
        edit = next((lvl for lvl in future if not planned_for(character, lvl)), future[0] if future else 0)
    current = character.compute()
    state, checks = planned_state(character)
    rows, skill_rows = preview_rows(current, compute(state))
    entry = planned_for(character, edit) or {}
    retrofit = entry.get("retrofit") or ["", ""]
    owned = {s for s, _l in planned_state(character, upto=edit - 1)[0].specialties}  # learned or planned before this level
    specialties = sorted(offer(reg.specialties.values(), keep={entry.get("specialty"), *retrofit, *owned}),
                         key=lambda s: (s["skill"] or "~", s["name"]))
    entry_skills = sorted((entry.get("skills") or {}).items(), key=lambda kv: -kv[1])
    twos = [s for s, v in entry_skills if v == 2]
    ones = [s for s, v in entry_skills if v == 1]
    return render(request, "characters/planner.html", {
        "character": character, "future": future, "edit": edit, "entry": entry,
        "edit_two": twos[0] if twos else "", "edit_one_a": ones[0] if ones else "",
        "edit_one_b": ones[1] if len(ones) > 1 else "",
        "checks": [{"entry": e, "problems": probs,
                    "specialty": reg.specialties.get(e.get("specialty", "")),
                    "retrofit": [reg.specialties[s] for s in e.get("retrofit") or [] if s in reg.specialties],
                    "augments": [reg.augments[a] for a in e.get("augments", []) if a in reg.augments]}
                   for e, probs in checks],
        "rows": rows, "skill_rows": skill_rows, "plan_level": state.level,
        "skills_by_attr": tables.SKILLS,
        "retrofit_level": leveling.retrofit_allowed(edit),
        "retrofit": retrofit,
        "specialties": [s for s in specialties if s["slug"] not in owned or s.get("repeatable")
                        or s["slug"] in {entry.get("specialty"), retrofit[1]}],
        "owned_specialties": [s for s in specialties if s["slug"] in owned],
        "augments": sorted(offer(reg.augments.values(), keep=entry.get("augments", [])),
                          key=lambda a: (a["skill"], a["name"])),
    })
