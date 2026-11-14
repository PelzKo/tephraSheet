"""Augment conditions on the item they are placed on (book: "Requires: placed on weapon with Custom", "light weapon",
"throwing weapon" …). The rules are the augments' "item" field (curated.AUGMENT_ITEM_RULES, classified in
rules/data/AUDIT_augment_requirements.md). Pure: works on a plain dict of item values (ItemFields.item_values())."""

from rules.lang import gettext as _
from rules.registry import get_registry

from . import tables

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
    if "max_ready" in rule and base_ready(item) > rule["max_ready"]:
        out.append(_("needs at most {max} AP to ready (has {have})", max=rule["max_ready"], have=base_ready(item)))
    if not variants & set(rule.get("needs_waived_by", [])):
        for group in rule.get("needs", []):
            if not on & set(group):
                out.append(_("needs {names} on the same item", names=_names(group, reg)))
    clash = [s for s in rule.get("excludes", []) if s in on]
    if clash:
        out.append(_("can't be combined with {names}", names=", ".join(reg.augments[s]["name"] for s in clash)))
    return out


def problems(item):
    """["<augment>: <reason>", …] for every augment on ``item`` whose item conditions aren't met (order of the
    augments doesn't matter). House-rule items have none."""
    if item.get("house_rule"):
        return []
    reg = get_registry()
    out = []
    for slug in dict.fromkeys(s for s, _m in item.get("augments") or []):
        name = reg.augments[slug]["name"] if slug in reg.augments else slug
        out += [_("{augment}: {reason}", augment=name, reason=r) for r in augment_reasons(slug, item)]
    return out


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
