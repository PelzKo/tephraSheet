"""The bow augment "armsmith-bow-burn-trail-everburning" is now "armsmith-bow-burn-trail" (package I). Rewrites every
JSON field that can hold augment slugs (also "aug:<slug>" keys, plans, snapshots, logs), trashed rows included.
The registry keeps resolving the old slug (rules.registry.AUGMENT_ALIASES)."""
import json
import re

from django.db import migrations, models

OLD, NEW = "armsmith-bow-burn-trail-everburning", "armsmith-bow-burn-trail"
MODELS = [("characters", m) for m in ("Character", "InventoryItem", "Automaton", "LevelLog", "CharacterSnapshot",
                                       "ActionLog")] + [("catalog", "ItemTemplate")]


def _rewrite(apps, replace):
    for app, name in MODELS:
        model = apps.get_model(app, name)
        fields = [f.name for f in model._meta.fields if isinstance(f, models.JSONField)]
        for obj in model._base_manager.only("pk", *fields).iterator():
            changed = []
            for f in fields:
                text = json.dumps(getattr(obj, f))
                new = replace(text)
                if new != text:
                    setattr(obj, f, json.loads(new))
                    changed.append(f)
            if changed:
                obj.save(update_fields=changed)


def forward(apps, schema_editor):
    _rewrite(apps, lambda text: text.replace(OLD, NEW))  # the old slug is a unique string


def backward(apps, schema_editor):
    _rewrite(apps, lambda text: re.sub(re.escape(NEW) + r"(?!-everburning)", OLD, text))


class Migration(migrations.Migration):
    dependencies = [("characters", "0030_backfill_effect_amount"), ("catalog", "0011_house_rule")]

    operations = [migrations.RunPython(forward, backward)]
