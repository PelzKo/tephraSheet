"""Load the Playing Guide items (rules/data/catalog.json) into the catalog. Idempotent."""

import json

from django.core.management.base import BaseCommand

from catalog.models import ItemTemplate
from rules.registry import DATA_DIR


class Command(BaseCommand):
    help = "Create/update book items in the global catalog"

    def handle(self, *args, **opts):
        items = json.loads((DATA_DIR / "catalog.json").read_text(encoding="utf8"))
        fields = set(ItemTemplate.ITEM_FIELDS) | {"is_starting_gear"}
        created = updated = 0
        for item in items:
            values = {k: v for k, v in item.items() if k in fields and k not in ("name", "kind")}
            values["source"] = "book"
            _, was_created = ItemTemplate.objects.update_or_create(
                name=item["name"], kind=item["kind"], defaults=values)
            created += was_created
            updated += not was_created
        self.stdout.write(f"catalog: {created} created, {updated} updated")
