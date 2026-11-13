"""Keep every row; flag book items the narrator changed since the last seed as modified (K1/B3)."""

import json

from django.db import migrations

FIELDS = ["name", "kind", "size", "variants", "material", "beta", "concealable", "hands", "ap_use", "ap_ready",
          "dc", "reach", "range", "increment", "soak", "eva_penalty", "spd_penalty", "climb_swim_penalty",
          "deflect_bonus", "acc_bonus", "stk_bonus", "deflect_ranged", "deflect_melee", "augments", "modifiers",
          "price_dukes", "description", "extension", "memento", "binding", "is_starting_gear"]


def mark_modified(apps, schema_editor):
    from rules.registry import DATA_DIR

    ItemTemplate = apps.get_model("catalog", "ItemTemplate")
    book = {(i["name"], i["kind"]): i for i in json.loads((DATA_DIR / "catalog.json").read_text(encoding="utf8"))}
    defaults = {f: ItemTemplate._meta.get_field(f).get_default() for f in FIELDS}
    changed = []
    for item in ItemTemplate.objects.filter(source="book"):
        entry = book.get((item.name, item.kind))
        if entry is None or any(getattr(item, f) != entry.get(f, defaults[f]) for f in FIELDS):
            changed.append(item.pk)
    ItemTemplate.objects.filter(pk__in=changed).update(modified=True)


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0009_a3_book_flags"),
    ]

    operations = [migrations.RunPython(mark_modified, migrations.RunPython.noop)]
