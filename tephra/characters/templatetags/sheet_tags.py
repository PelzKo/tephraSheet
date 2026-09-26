import json

from django import template
from django.utils.html import format_html

from rules.engine.modifiers import Value
from rules.engine.tables import format_money as _format_money

register = template.Library()


def _breakdown_json(value):
    rows = []
    for label, amount in value.breakdown:
        rows.append([label, None if amount is None else amount])
    return json.dumps({"total": value.total, "rows": rows, "base": value.base is not None})


@register.simple_tag
def stat(value, title="", css="", signed=False):
    """Render a computed Value; composite values get a breakdown popover (hover or tap)."""
    if value is None:
        return format_html('<span class="val {}">–</span>', css)
    if not isinstance(value, Value):
        text = f"{value:+d}" if signed and isinstance(value, int) else value
        return format_html('<span class="val {}">{}</span>', css, text)
    text = f"{value.total:+d}" if signed else str(value.total)
    if not value.is_composite:
        return format_html('<span class="val {}">{}</span>', css, text)
    return format_html('<button type="button" class="val has-bd {}" data-title="{}" data-bd="{}">{}</button>',
                       css, title, _breakdown_json(value), text)


@register.filter
def signed(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return value
    return f"{value:+d}" if value else "0"


@register.filter
def money(dukes):
    return _format_money(dukes)


@register.filter
def get(mapping, key):
    try:
        return mapping.get(key)
    except AttributeError:
        return None


@register.filter
def total(value):
    return value.total if isinstance(value, Value) else value


@register.filter
def roman(n):
    return {1: "I", 2: "II", 3: "III", 4: "IV"}.get(n, n)


@register.filter
def nonzero(value):
    return value if value else ""


@register.filter
def augment(slug):
    from rules.registry import get_registry

    return get_registry().augments.get(slug)


@register.filter
def specialty(slug):
    from rules.registry import get_registry

    return get_registry().specialties.get(slug)


@register.simple_tag
def xp_pos(i, radius=140, cy=1178, cx=475):
    """Position of experience dot ``i`` (1-12) on the arc."""
    import math

    theta = math.radians(180 - (i - 1) * 180 / 11)
    return {"x": round(cx + radius * math.cos(theta), 1), "y": round(cy - radius * math.sin(theta), 1)}
