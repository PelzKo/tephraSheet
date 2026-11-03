"""Specialty eligibility and prerequisite checks (reference §6.1)."""

from functools import cache

from rules.lang import get_language
from rules.lang import gettext as _
from rules.registry import get_registry

from . import tables
from .weapons import hand_layout


@cache
def _names(lang):
    reg = get_registry()
    return {x["name_en"]: x["name"] for coll in (reg.specialties, reg.augments) for x in coll.values()}


def _local(name_en):
    """Translated specialty/augment name for an English name."""
    return _names(get_language()).get(name_en, name_en)


def owned_names(state):
    reg = get_registry()
    return {reg.specialties[s]["name_en"] for s, _l in state.specialties if s in reg.specialties}


def race_family(race_slug):
    """The race plus the races it counts as for requirements (hybrid parents, base race of a variant)."""
    race = get_registry().races.get(race_slug) or {}
    return {race_slug, *race.get("counts_as", [])}


def granted_augments(state):
    """{augment slug: source name} for augments a specialty or racial trait grants ("grants_augments").
    They are known without using augment capacity; a chosen augment that is also granted frees its slot
    (the book's "if you already know it, learn another one instead")."""
    reg = get_registry()
    sources = [reg.specialties.get(s) for s, _l in state.specialties]
    sources += [reg.traits.get(k) for k in [*state.fixed_traits, *state.random_traits]]
    out = {}
    for src in sources:
        for slug in (src or {}).get("grants_augments", []):
            out.setdefault(slug, src["name"])
    return out


def known_augments(state):
    return set(state.augments) | set(granted_augments(state))


def augments_used(state):
    """How much augment capacity the chosen augments use (granted ones are free)."""
    granted = granted_augments(state)
    return sum(1 for a in state.augments if a not in granted)


def check_specialty(spec, state, sheet, ignore_owned=False):
    """Return (ok, reasons). ``sheet`` is the computed Sheet of ``state``."""
    reg = get_registry()
    reasons = []
    owned = [s for s, _l in state.specialties]
    if spec["slug"] in owned and not spec.get("repeatable") and not ignore_owned:
        reasons.append(_("already learned"))
    if spec["general"]:
        if not any(sheet.skills[s].total >= 1 for s in tables.SCIENCE_SKILLS):
            reasons.append(_("needs at least 1 point in a Science skill"))
    elif sheet.skills[spec["skill"]].total < 1:
        reasons.append(_("needs at least 1 point in {skill}", skill=_(spec["skill"])))
    names = owned_names(state)
    for clause in spec.get("requires", []):
        if clause.get("soft"):
            continue
        t = clause["type"]
        if t == "skill":
            have = sheet.skills[clause["skill"]].total
            if have < clause["min"]:
                reasons.append(_("needs {min} points in {skill} (has {have})", min=clause["min"], skill=_(clause["skill"]), have=have))
        elif t == "attribute":
            have = sheet.attributes[clause["attribute"]].total
            if have < clause["min"]:
                reasons.append(_("needs {attribute} {min} (has {have})", attribute=_(clause["attribute"]), min=clause["min"], have=have))
        elif t == "stat":
            have = sheet.specialty_totals.get(clause["stat"], 0)
            if have < clause["min"]:
                label = _(tables.COMBAT_STAT_LABELS[clause["stat"]])
                reasons.append(_("needs +{min} {stat} from specialties (has +{have})", min=clause["min"], stat=label, have=have))
        elif t == "specialty":
            if not names.intersection(clause["any"]):
                reasons.append(_("needs {names}", names=_(" or ").join(_local(n) for n in clause["any"])))
        elif t == "stances":
            count = 0
            for slug, _l in state.specialties:
                s = reg.specialties.get(slug)
                if s and s.get("stance") and (not clause.get("skill") or s["skill"] == clause["skill"]):
                    count += 1
            if count < clause["min"]:
                if clause.get("skill"):
                    reasons.append(_("needs {min} {skill} stances known (has {have})", min=clause["min"], skill=_(clause["skill"]), have=count))
                else:
                    reasons.append(_("needs {min} stances known (has {have})", min=clause["min"], have=count))
        elif t == "ap":
            have = tables.action_points(state.level)
            if have < clause["min"]:
                reasons.append(_("needs {min} AP per turn (has {have})", min=clause["min"], have=have))
        elif t == "augment":  # by slug: same-name augments on different lists are different augments
            if not known_augments(state).intersection(clause["any"]):
                reasons.append(_("needs {names}", names=_(" or ").join(
                    reg.augments[a]["name"] if a in reg.augments else a for a in clause["any"])))
        elif t == "race":
            if not race_family(state.race).intersection(clause["any"]):
                reasons.append(_("only for {races}", races=_(" or ").join(
                    reg.races[r]["name"] if r in reg.races else r for r in clause["any"])))
        elif t == "skill_specialty":
            if not any(reg.specialties[s]["skill"] == clause["skill"] and s != spec["slug"]
                       for s in owned if s in reg.specialties):
                reasons.append(_("needs another {skill} specialty", skill=_(clause["skill"])))
    return not reasons, reasons


def _weapon_matches(m, item, owned, oh):
    if m.get("with_specialty") and m["with_specialty"] not in owned:
        return False
    return (not m.get("kinds") or item.kind in m["kinds"]) and (not m.get("sizes") or item.size in m["sizes"]) \
        and (not m.get("variant") or m["variant"] in item.variants) \
        and (not m.get("materials") or item.material in m["materials"]) \
        and (not m.get("concealable") or item.concealable) \
        and (not m.get("hands") or tables.item_hands(item, oh) == m["hands"])


def _is_shield(item):
    return "shield" in item.name.lower() or (item.deflect_ranged and item.deflect_melee)


def soft_clause_met(clause, state):
    """Whether a soft (usage) requirement is satisfied by the current equipment."""
    t = clause["type"]
    armor = state.armor
    if t == "armor":
        size = armor.size if armor is not None and armor.size in tables.ARMOR_ORDER else "none"
        idx = tables.ARMOR_ORDER.index(size)
        return not ("min" in clause and idx < tables.ARMOR_ORDER.index(clause["min"]) or
                    "max" in clause and idx > tables.ARMOR_ORDER.index(clause["max"]))
    if t == "armor_worn":
        return armor is not None
    if t == "armor_material":
        return armor is not None and armor.material in clause["materials"]
    if t in ("weapon", "free_hand", "hands_empty"):
        layout = hand_layout(state)
        if t == "free_hand":
            return layout["free"] >= 1
        if t == "hands_empty":
            return layout["free"] == 2
        owned, oh = owned_names(state), layout["one_handing"]

        def fits(w):
            return any(_weapon_matches(m, w, owned, oh) for m in clause["weapons"])

        if clause.get("all"):
            return bool(state.weapons) and all(fits(w) for w in state.weapons)
        if clause.get("other_hand_empty"):
            held = [i for i in (layout["left"], layout["right"]) if i is not None]
            return len(held) == 1 and layout["free"] == 1 and fits(held[0])
        return any(fits(w) for w in state.weapons)
    if t == "specialty":
        return bool(owned_names(state).intersection(clause["any"]))
    if t == "deflection":
        d = state.deflection
        return d is not None and (not clause.get("shield") or _is_shield(d))
    return False  # "note": can't be checked, always reminded


def specialty_warnings(spec, state):
    """Unmet soft requirements (armor worn, equipped weapon, vehicle …). They never block learning."""
    warnings = []
    for clause in spec.get("requires", []):
        if clause.get("soft") and not soft_clause_met(clause, state):
            if clause.get("note"):  # the clause brings its own sentence
                warnings.append(_(clause["note"]))
            else:
                warnings.append(_("needs {what}", what=_(clause["text"])) + _currently(clause, state))
    return warnings


def _currently(clause, state):
    if clause["type"] in ("armor", "armor_worn", "armor_material"):
        armor = state.armor
        return " " + (_("(wearing {name})", name=armor.name) if armor is not None else _("(no armor worn)"))
    if clause["type"] in ("weapon", "free_hand", "hands_empty"):
        layout = hand_layout(state)
        names = [i.name for i in (layout["left"], layout["right"], layout["blocked_by"], layout["wings"]) if i]
        names = list(dict.fromkeys(names))
        return " " + (_("(holding: {names})", names=", ".join(names)) if names else _("(hands empty)"))
    return ""


def character_warnings(state):
    """[(specialty name, [warnings])] for learned specialties whose soft requirements are unmet."""
    reg = get_registry()
    out = []
    for slug, _l in state.specialties:
        spec = reg.specialties.get(slug)
        warnings = specialty_warnings(spec, state) if spec else []
        if warnings:
            out.append((spec["name"], warnings))
    return out


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
    for slug, _l in state.specialties:
        s = reg.specialties.get(slug)
        if s:
            lists.update(s.get("crafts", []))
    return lists


def check_augment(aug, state, sheet):
    reasons = []
    known = known_augments(state)
    if aug["slug"] in known:
        reasons.append(_("already known"))
    lists = augment_lists(state)
    if not lists.intersection(aug["lists"]):
        reasons.append(_("needs a crafting specialty for {lists}", lists=" / ".join(_(x) for x in aug["lists"])))
    if sheet.skills[aug["skill"]].total < 1:
        reasons.append(_("needs points in {skill}", skill=_(aug["skill"])))
    reg = get_registry()
    known_names = {reg.augments[a]["name_en"] for a in known if a in reg.augments}
    names = owned_names(state)
    for q in aug.get("qualifiers_en", []):
        if q.startswith("req. "):
            needed = [n.strip() for n in q[5:].split(" or ")]
            if not any(n in known_names or n in names for n in needed):
                reasons.append(_("needs {names}", names=_(" or ").join(_local(n) for n in needed)))
    return not reasons, reasons


def augment_capacity(sheet):
    return max(0, sheet.stats["aug"].total)
