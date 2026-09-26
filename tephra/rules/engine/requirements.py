"""Specialty eligibility and prerequisite checks (reference §6.1)."""

from rules.registry import get_registry

from . import tables


def owned_names(state):
    reg = get_registry()
    return {reg.specialties[s]["name"] for s, _ in state.specialties if s in reg.specialties}


def check_specialty(spec, state, sheet, ignore_owned=False):
    """Return (ok, reasons). ``sheet`` is the computed Sheet of ``state``."""
    reg = get_registry()
    reasons = []
    owned = [s for s, _ in state.specialties]
    if spec["slug"] in owned and not spec.get("repeatable") and not ignore_owned:
        reasons.append("already learned")
    if spec["general"]:
        if not any(sheet.skills[s].total >= 1 for s in tables.SCIENCE_SKILLS):
            reasons.append("needs at least 1 point in a Science skill")
    elif sheet.skills[spec["skill"]].total < 1:
        reasons.append(f"needs at least 1 point in {spec['skill']}")
    names = owned_names(state)
    for clause in spec.get("requires", []):
        t = clause["type"]
        if t == "skill":
            have = sheet.skills[clause["skill"]].total
            if have < clause["min"]:
                reasons.append(f"needs {clause['min']} points in {clause['skill']} (has {have})")
        elif t == "attribute":
            have = sheet.attributes[clause["attribute"]].total
            if have < clause["min"]:
                reasons.append(f"needs {clause['attribute']} {clause['min']} (has {have})")
        elif t == "stat":
            have = sheet.specialty_totals.get(clause["stat"], 0)
            if have < clause["min"]:
                label = tables.COMBAT_STAT_LABELS[clause["stat"]]
                reasons.append(f"needs +{clause['min']} {label} from specialties (has +{have})")
        elif t == "specialty":
            if not names.intersection(clause["any"]):
                reasons.append("needs " + " or ".join(clause["any"]))
        elif t == "stances":
            count = 0
            for slug, _ in state.specialties:
                s = reg.specialties.get(slug)
                if s and s.get("stance") and (not clause.get("skill") or s["skill"] == clause["skill"]):
                    count += 1
            if count < clause["min"]:
                where = f" {clause['skill']}" if clause.get("skill") else ""
                reasons.append(f"needs {clause['min']}{where} stances known (has {count})")
        elif t == "ap":
            have = tables.action_points(state.level)
            if have < clause["min"]:
                reasons.append(f"needs {clause['min']} AP per turn (has {have})")
        elif t == "skill_specialty":
            if not any(reg.specialties[s]["skill"] == clause["skill"] and s != spec["slug"]
                       for s in owned if s in reg.specialties):
                reasons.append(f"needs another {clause['skill']} specialty")
        # "note" clauses are situational (e.g. armor worn) and not enforced when learning.
    return not reasons, reasons


def eligible_specialties(state, sheet):
    """All specialties with eligibility info, grouped for the picker."""
    reg = get_registry()
    out = []
    for spec in reg.specialties.values():
        ok, reasons = check_specialty(spec, state, sheet)
        out.append({"spec": spec, "ok": ok, "reasons": reasons})
    return out


def augment_lists(state):
    """Augment lists the character can learn from (via [CRAFT:x] specialties)."""
    reg = get_registry()
    lists = set()
    for slug, _ in state.specialties:
        s = reg.specialties.get(slug)
        if s:
            lists.update(s.get("crafts", []))
    return lists


def check_augment(aug, state, sheet):
    reasons = []
    if aug["slug"] in state.augments:
        reasons.append("already known")
    lists = augment_lists(state)
    if not lists.intersection(aug["lists"]):
        reasons.append("needs a crafting specialty for " + " / ".join(aug["lists"]))
    if sheet.skills[aug["skill"]].total < 1:
        reasons.append(f"needs points in {aug['skill']}")
    reg = get_registry()
    known_names = {reg.augments[a]["name"] for a in state.augments if a in reg.augments}
    names = owned_names(state)
    for q in aug.get("qualifiers", []):
        if q.startswith("req. "):
            needed = [n.strip() for n in q[5:].split(" or ")]
            if not any(n in known_names or n in names for n in needed):
                reasons.append(f"needs {q[5:]}")
    return not reasons, reasons


def augment_capacity(sheet):
    return max(0, sheet.stats["aug"].total)
