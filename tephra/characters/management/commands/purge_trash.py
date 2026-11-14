from django.core.management.base import BaseCommand

from characters import trash


class Command(BaseCommand):
    help = f"Delete characters, wiki pages and custom catalog items that have been in the trash for {trash.TRASH_DAYS} days."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=trash.TRASH_DAYS)

    def handle(self, *args, **opts):
        counts = trash.purge(opts["days"])
        self.stdout.write("purge_trash: " + ", ".join(f"{n} {k}" for k, n in counts.items()))
