from django.db import migrations

# Rule numbers as of 0029 (rules/engine/effects.py), embedded so later rule changes cannot break this migration.
START = {f"status:burning-{t}": 2 ** t for t in (1, 2, 3, 4)}  # AP still needed to extinguish
BANDAGE = ("fatal:arm", "fatal:hand", "fatal:leg")  # 1 = death timer running (no bandaging was tracked before)


def backfill(apps, schema_editor):
    EffectEntry = apps.get_model("characters", "EffectEntry")
    for key, start in START.items():
        EffectEntry.objects.filter(key=key, amount=0).update(amount=start)
    EffectEntry.objects.filter(key__in=BANDAGE, amount=0).update(amount=1)


class Migration(migrations.Migration):

    dependencies = [
        ('characters', '0029_effect_amount'),
    ]

    operations = [
        migrations.RunPython(backfill, migrations.RunPython.noop),
    ]
