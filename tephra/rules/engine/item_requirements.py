"""Augment conditions on the item they are placed on (book: "Requires: placed on weapon with Custom", "light weapon",
"throwing weapon" …). The rules are the augments' "item" field (curated.AUGMENT_ITEM_RULES, classified in
rules/data/AUDIT_augment_requirements.md). Pure: works on a plain dict of item values (ItemFields.item_values())."""

from rules.lang import gettext as _
from rules.registry import get_registry

from . import tables
from .modifiers import mod_amount

# Augments that turn the item into a variant: Aerodynamic lets a melee weapon be thrown "like a weapon designed for
# throwing", so it satisfies Propelled/Returning ("placed on throwing weapon").
GRANTS_VARIANT = {"armsmith-melee-aerodynamic": "throwing"}

READY_TABLES = {"firearm": tables.FIREARMS, "crossbow": tables.CROSSBOWS, "bow": tables.BOWS}


def _names(slugs, reg):
    return _(" or ").join(reg.augments[s]["name"] if s in reg.augments else s for s in slugs)


def base_ready(item):
    """AP to ready before character/augment modifiers: the item's own value, else the size table."""
    if item.get("ap_ready") is not None:
        return item["ap_ready"]
    return (READY_TABLES.get(item.get("kind")) or {}).get(item.get("size") or "", {}).get("ready", 0)


def item_ready(item):
    """AP to ready the item itself: base value plus its own augments' ap_ready modifiers (Belt Fed, Automatic Reload),
    at least 0. The wielder's modifiers (Snap Reload) don't change the item."""
    reg = get_registry()
    total = base_ready(item)
    for slug, marque in item.get("augments") or []:
        for m in (reg.augments.get(slug) or {}).get("modifiers", []):
            if m["stat"] == "ap_ready" and m.get("scope") == "weapon":
                total += mod_amount(m, {}, marque)
    return max(0, total)


def augment_reasons(slug, item):
    """Why augment ``slug`` doesn't fit ``item`` (with the item's augments as they are); [] when it fits."""
    reg = get_registry()
    rule = (reg.augments.get(slug) or {}).get("item") or {}
    on = {s for s, _m in item.get("augments") or []}
    variants = set(item.get("variants") or [])
    out = []
    if rule.get("sizes") and item.get("size") not in rule["sizes"]:
        out.append(_("needs a {sizes} item", sizes=_(" or ").join(_(s.title()) for s in rule["sizes"])))
    if rule.get("materials") and item.get("material") not in rule["materials"]:
        out.append(_("needs a {materials} item", materials=_(" or ").join(_(m.title()) for m in rule["materials"])))
    if rule.get("variants") and not (variants | {GRANTS_VARIANT[s] for s in on if s in GRANTS_VARIANT}) & set(rule["variants"]):
        out.append(_("needs a {variants} weapon", variants=_(" or ").join(
            _(tables.VARIANTS[v]["label"]) for v in rule["variants"])))
    if "max_item_ready" in rule and item_ready(item) > rule["max_item_ready"]:
        out.append(_("needs at most {max} AP to ready (has {have})", max=rule["max_item_ready"], have=item_ready(item)))
    if "aether" in variants and slug not in tables.AETHER_SHAPED["augments"]:  # Aetherform Modules: mark as house rule
        out.append(_("not allowed on an aether-shaped weapon"))
    if not variants & set(rule.get("needs_waived_by", [])):
        for group in rule.get("needs", []):
            if not on & set(group):
                out.append(_("needs {names} on the same item", names=_names(group, reg)))
    clash = [s for s in rule.get("excludes", []) if s in on]
    if clash:
        out.append(_("can't be combined with {names}", names=", ".join(reg.augments[s]["name"] for s in clash)))
    return out


def skill_reasons(aug, skills):
    """Unmet "N points in <skill>" learning clauses of ``aug`` (Automated: 1 point in Automata); skills = {name: points}.
    Shared by learning (requirements.check_augment) and the owner of an inventory item."""
    return [_("needs {min} points in {skill} (has {have})", min=c["min"], skill=_(c["skill"]), have=skills.get(c["skill"], 0))
            for c in aug.get("learn", []) if c["type"] == "skill" and skills.get(c["skill"], 0) < c["min"]]


def problems(item, owner=None):
    """["<augment>: <reason>", …] for every augment on ``item`` whose item conditions aren't met (order of the
    augments doesn't matter). ``owner`` = the owning character's skill points ({name: points}) for inventory items:
    then the augments' skill learning clauses must be met by the owner too (catalog templates: None). House-rule
    items have none."""
    if item.get("house_rule"):
        return []
    reg = get_registry()
    out = []
    for slug in dict.fromkeys(s for s, _m in item.get("augments") or []):
        name = reg.augments[slug]["name"] if slug in reg.augments else slug
        reasons = augment_reasons(slug, item)
        if owner is not None and slug in reg.augments:
            reasons += skill_reasons(reg.augments[slug], owner)
        out += [_("{augment}: {reason}", augment=name, reason=r) for r in reasons]
    return out + count_problems(item)


def count_problems(item):
    """The aether-shaped weapon's augment count limit (3, beta or not) as a list of messages."""
    limit = tables.AETHER_SHAPED["max"]
    if "aether" in (item.get("variants") or []) and len(item.get("augments") or []) > limit:
        return [_("An aether-shaped weapon takes at most {max} augments.", max=limit)]
    return []


def install_notes(aug):
    """Item conditions as sentences for the learning pickers ("Requires Custom on the item when installed.")."""
    reg = get_registry()
    rule = aug.get("item") or {}
    notes = [_("Requires {names} on the item when installed.", names=_names(g, reg)) for g in rule.get("needs", [])]
    if rule.get("sizes"):
        notes.append(_("Only on {sizes} items.", sizes=_(" or ").join(_(s.title()) for s in rule["sizes"])))
    if rule.get("variants"):
        notes.append(_("Only on {variants} weapons.", variants=_(" or ").join(
            _(tables.VARIANTS[v]["label"]) for v in rule["variants"])))
    return notes
