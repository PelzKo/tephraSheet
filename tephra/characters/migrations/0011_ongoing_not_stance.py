# Battle Theme and Epic Dance are no longer stances but toggles ("Other" on the sheet).

from django.db import migrations

ONGOING = ("showmanship-battle-theme", "showmanship-epic-dance")


def forward(apps, schema_editor):
    Character = apps.get_model("characters", "Character")
    for c in Character.objects.filter(stance__in=ONGOING):
        c.toggles = sorted(set(c.toggles) | {f"spec:{c.stance}"})
        c.stance = ""
        c.save(update_fields=["toggles", "stance"])


class Migration(migrations.Migration):

    dependencies = [("characters", "0010_wounds_taken")]

    operations = [migrations.RunPython(forward, migrations.RunPython.noop)]
