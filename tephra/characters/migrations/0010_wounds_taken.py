# Wounds now count up (wounds taken, 0 = unhurt) instead of down (wounds left).

from django.db import migrations, models


def to_taken(apps, schema_editor):
    """taken = max − left. Max wounds here = 12 + specialty Wnd bonuses − permanent losses.
    shortcut: ignores race/story/custom Wnd modifiers (none in the book change it); the sheet
    clamps to the real max on the next action."""
    from rules.registry import get_registry

    reg = get_registry()
    Character = apps.get_model("characters", "Character")
    EffectEntry = apps.get_model("characters", "EffectEntry")
    for c in Character.objects.exclude(current_wounds=None):
        max_wounds = 12 + sum(reg.specialties.get(slug, {}).get("bonuses", {}).get("wnd", 0)
                              for slug, _lvl in c.specialties)
        max_wounds -= sum(EffectEntry.objects.filter(character=c, active=True).values_list("lost_wounds", flat=True))
        c.wounds_taken = max(0, max_wounds - c.current_wounds)
        c.save(update_fields=["wounds_taken"])


def to_left(apps, schema_editor):
    Character = apps.get_model("characters", "Character")
    for c in Character.objects.all():
        c.current_wounds = None if not c.wounds_taken else max(0, 12 - c.wounds_taken)
        c.save(update_fields=["current_wounds"])


class Migration(migrations.Migration):

    dependencies = [
        ('characters', '0009_inventoryitem_acc_bonus_inventoryitem_stk_bonus_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='character',
            name='wounds_taken',
            field=models.PositiveIntegerField(default=0, help_text='0 = unhurt; at max wounds every hit is fatal'),
        ),
        migrations.RunPython(to_taken, to_left),
        migrations.RemoveField(model_name='character', name='current_wounds'),
    ]
