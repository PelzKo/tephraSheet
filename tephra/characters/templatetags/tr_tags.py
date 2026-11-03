"""{% t "English text" name=value %} and {{ value|t }}: UI translation (see rules/lang.py).
Loaded as a template builtin, so no {% load %} is needed."""

from django import template
from django.utils.html import format_html

from rules.lang import gettext

register = template.Library()


@register.simple_tag
def t(*args, **kwargs):
    # *args: a placeholder may itself be called "text"
    return gettext(args[0], **kwargs)


@register.filter(name="t")
def t_filter(text):
    return gettext(str(text)) if text not in (None, "") else text


def _item_tr(name):
    from rules.lang import DEFAULT, get_language
    from rules.registry import translations

    lang = get_language()
    return translations(lang, "catalog").get(name, {}) if lang != DEFAULT else {}


@register.filter
def item_name(name):
    """Book catalog item name in the current language (custom items keep their name)."""
    return _item_tr(name).get("name") or name


@register.filter
def item_desc(item):
    """Description of a catalog/inventory item in the current language."""
    desc = getattr(item, "description", "") or ""
    return _item_tr(item.name).get("description") or (gettext(desc) if desc else desc)


@register.filter
def ext_name(entry):
    """Short name of the extension a rule entry (or item) comes from; "" for core content."""
    from rules.extensions import EXTENSIONS

    key = entry.get("extension") if isinstance(entry, dict) else getattr(entry, "extension", "")
    return gettext(EXTENSIONS.get(key, key)) if key else ""


@register.simple_tag
def ext_badge(entry):
    name = ext_name(entry)
    return format_html('<span class="tag ext" title="{}">{}</span>', gettext("Extension"), name) if name else ""
