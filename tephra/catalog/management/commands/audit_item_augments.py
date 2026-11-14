"""Report catalog items and inventory items whose augments don't meet their item conditions. Changes nothing."""

from django.core.management.base import BaseCommand

from catalog.models import ItemTemplate
from characters.models import InventoryItem


class Command(BaseCommand):
    help = "List catalog and inventory items whose augments don't fit them (read-only)"

    def handle(self, *args, **opts):
        count = 0
        for label, qs in (("catalog", ItemTemplate.objects.exclude(augments=[])),
                          ("inventory", InventoryItem.objects.exclude(augments=[]).select_related("character"))):
            for item in qs:
                problems = item.augment_problems
                if problems:
                    count += 1
                    owner = f" ({item.character})" if label == "inventory" else ""
                    self.stdout.write(f"{label} #{item.pk} {item.name}{owner}: " + "; ".join(problems))
        self.stdout.write(f"{count} item(s) do not meet their augment conditions")
