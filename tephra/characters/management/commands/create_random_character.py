"""Create a finished random character (all wizard steps rolled), e.g. as a demo sheet."""

import random

from django.core.management import call_command
from django.core.management.base import BaseCommand

from catalog.models import ItemTemplate
from characters import services
from characters.models import Character


class Command(BaseCommand):
    help = "Create a random, finished character. With --if-empty only when no character exists yet."

    def add_arguments(self, parser):
        parser.add_argument("--level", type=int, default=1, help="starting level (1-12)")
        parser.add_argument("--password", default="demo", help='sheet password (default "demo")')
        parser.add_argument("--name", default="", help="character name (default: random)")
        parser.add_argument("--player", default="Demo", help="player name")
        parser.add_argument("--seed", type=int, default=None, help="random seed for a reproducible character")
        parser.add_argument("--if-empty", action="store_true", help="do nothing if any character exists")

    def handle(self, *args, **opts):
        if opts["if_empty"] and Character.objects.exists():
            self.stdout.write("Characters exist already, no demo character created.")
            return
        if not ItemTemplate.objects.exists():
            call_command("seed_catalog", verbosity=0)
        rng = random.Random(opts["seed"])
        level = max(1, min(12, opts["level"]))
        character = Character.objects.create(name=opts["name"], player_name=opts["player"])
        services.random_all(character, rng)
        character.set_password(opts["password"])
        services.finish_creation(character)
        for _ in range(level - 1):
            errors = services.random_levelup(character, rng, from_xp=False)
            if errors:
                self.stderr.write("; ".join(errors))
                break
        services.reset_health(character)
        character.money_on_hand = services.starting_money(character.level)
        character.save()
        self.stdout.write(self.style.SUCCESS(
            f"Created {character.name} (level {character.level} {character.race_data['name']}), "
            f"password \"{opts['password']}\"."))
