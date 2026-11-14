import json

from django import template
from django.utils.html import format_html

from catalog.models import SIZE_CHOICES

from rules.engine.modifiers import Value
from rules.engine.tables import format_money as _format_money

register = template.Library()


def _breakdown_json(value):
    rows = []
    for label, amount in value.breakdown:
        rows.append([label, None if amount is None else amount])
    return json.dumps({"total": value.total, "rows": rows, "base": value.base is not None})


def signed_text(n):
    return f"{n:+d}" if n else "0"


@register.simple_tag
def stat(value, title="", css="", signed=False):
    """Render a computed Value. Every value with at least one source gets a breakdown popover
    (hover, click or tap), so each number on the sheet can explain itself."""
    if value is None:
        return format_html('<span class="val {}">–</span>', css)
    if not isinstance(value, Value):
        text = signed_text(value) if signed and isinstance(value, int) else value
        return format_html('<span class="val {}">{}</span>', css, text)
    text = signed_text(value.total) if signed else str(value.total)
    if not value.breakdown:
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


_SIZE_RANK = {value: n for n, (value, _label) in enumerate(SIZE_CHOICES) if value}


@register.filter
def size_rank(size):
    """Sort key for item sizes (minimal → super-heavy); empty for items without a size."""
    return _SIZE_RANK.get(size, "")


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
    # Strings, not floats: a German locale would render 475.3 as "475,3" and break the SVG.
    return {"x": f"{cx + radius * math.cos(theta):.1f}", "y": f"{cy - radius * math.sin(theta):.1f}"}


TIER_RANGES = ["1–9", "10–19", "20–29", "30+"]


@register.filter
def effect_html(text, marques=False):
    """Specialty effect as HTML: the text, then the four tier results as numbered gears.
    With an argument (augment book text) the four lines are the results per marque, mQ I–IV."""
    from django.utils.html import escape
    from django.utils.safestring import mark_safe

    from rules.engine.text import split_tiers

    body, tiers = split_tiers(text or "")
    html = f'<p class="effect">{escape(body)}</p>' if body.strip() else ""
    if tiers:
        def gear(n):
            if marques:
                return f'<span class="tier-gear" title="mQ {roman(n)}"><span>{roman(n)}</span></span>'
            return f'<span class="tier-gear" title="Tier {n} (roll {TIER_RANGES[n - 1]})"><span>{n}</span></span>'

        rows = "".join(f'<li>{gear(n)}<span class="tier-text">{escape(t)}</span></li>'
                       for n, t in enumerate(tiers, 1))
        html += f'<ol class="tier-results" aria-label="Results by tier">{rows}</ol>'
    return mark_safe(html)


@register.filter
def aug_tip(slug_marque):
    """Hover/tap text for an augment on an item: its effect at that marque, then the book text."""
    slug, m = slug_marque[0], slug_marque[1]
    a = augment(slug)
    if not a:
        return ""
    value = a["marques"][m - 1] if 0 < m <= len(a["marques"]) else ""
    head = f"mQ {roman(m)}: {value}" if value and value != "–" else ""
    return "\n".join(x for x in (head, a.get("text") or a.get("notes") or "") if x)
