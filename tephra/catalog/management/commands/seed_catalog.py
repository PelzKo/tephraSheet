"""Load the Playing Guide items (rules/data/catalog.json) into the catalog. Idempotent.

Only creates missing items: narrator edits stay, hidden (deleted) book items stay hidden.
"""

from django.core.management.base import BaseCommand

from catalog.models import ItemTemplate, book_entries


class Command(BaseCommand):
    help = "Create missing book items in the global catalog"

    def handle(self, *args, **opts):
        existing = set(ItemTemplate.objects.values_list("name", "kind"))
        missing = [ItemTemplate(**values, source="book") for key, values in book_entries().items() if key not in existing]
        ItemTemplate.objects.bulk_create(missing)
        self.stdout.write(f"catalog: {len(missing)} created")
