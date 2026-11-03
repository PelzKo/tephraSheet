import json

from django.db import migrations

OLD, NEW = '"automata-prosthetic-air-funnel"', '"automata-prosthetic-air-tunnel"'


def rename(apps, schema_editor, old=OLD, new=NEW):
    """The augment was renamed to the book's "Air Tunnel"; move stored slugs along."""
    fields = [("characters", "Character", ("augments", "body_augments", "plan")),
              ("characters", "InventoryItem", ("augments",)),
              ("catalog", "ItemTemplate", ("augments",))]
    for app, model, names in fields:
        for obj in apps.get_model(app, model).objects.all():
            changed = []
            for name in names:
                raw = json.dumps(getattr(obj, name))
                if old in raw:
                    setattr(obj, name, json.loads(raw.replace(old, new)))
                    changed.append(name)
            if changed:
                obj.save(update_fields=changed)


def back(apps, schema_editor):
    rename(apps, schema_editor, NEW, OLD)


class Migration(migrations.Migration):
    dependencies = [("characters", "0013_narrator_offer"), ("catalog", "0004_itemtemplate_acc_bonus_itemtemplate_stk_bonus_and_more")]
    operations = [migrations.RunPython(rename, back)]
