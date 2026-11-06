from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.urls import reverse

from catalog.models import ItemFields, ItemTemplate
from rules.engine import effects, tables
from rules.engine.state import CharacterState
from rules.registry import get_registry

SLOT_CHOICES = [
    ("weapon1", "Left hand"),
    ("weapon2", "Right hand"),
    ("wings", "Wings"),
    ("armor", "Armor (worn)"),
    ("deflection", "Deflection item"),
    ("worn", "Worn / active"),
    ("carried", "Carried"),
    ("stored", "Stored"),
    ("released", "Released (living liquid)"),
]


class NarratorSettings(models.Model):
    """Global narrator options (singleton, pk=1)."""

    allow_choose_random_trait = models.BooleanField(
        default=False, help_text="Players may pick their random racial trait instead of rolling")
    allow_reroll_random_trait = models.BooleanField(default=True, help_text="Players may re-roll the racial trait")
    background_story_count = models.PositiveSmallIntegerField(default=1)
    max_starting_level = models.PositiveSmallIntegerField(default=1)
    allow_player_admin_mode = models.BooleanField(
        default=True, help_text="Players who unlocked a character may use admin mode on it")
    # Both only gate new choices (wizard, pickers, random generators); existing characters keep their content.
    enabled_extensions = models.JSONField(default=list, blank=True)
    disabled_races = models.JSONField(default=list, blank=True)

    class Meta:
        verbose_name_plural = "narrator settings"

    def __str__(self):
        return "Narrator settings"

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Character(models.Model):
    STATUS_CHOICES = [("draft", "In creation"), ("active", "Active")]

    name = models.CharField(max_length=120, blank=True)
    player_name = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")
    wizard_step = models.PositiveSmallIntegerField(default=1)
    target_level = models.PositiveSmallIntegerField(default=1)
    password = models.CharField(max_length=128, blank=True)

    race = models.CharField(max_length=40, blank=True)
    nationality = models.CharField(max_length=40, blank=True)
    nationality_custom = models.CharField(max_length=80, blank=True)
    religion = models.CharField(max_length=80, blank=True)
    age = models.CharField(max_length=30, blank=True)
    height = models.CharField(max_length=30, blank=True)
    weight = models.CharField(max_length=30, blank=True)
    personality = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    level = models.PositiveSmallIntegerField(default=1)
    xp = models.PositiveSmallIntegerField(default=0)
    current_hp = models.IntegerField(null=True, blank=True)
    wounds_taken = models.PositiveIntegerField(default=0, help_text="0 = unhurt; at max wounds every hit is fatal")
    money_on_hand = models.IntegerField(default=0, help_text="in dukes")
    money_in_bank = models.IntegerField(default=0, help_text="in dukes")

    # Rule choices (slugs from rules/data/*.json).
    fixed_traits = models.JSONField(default=list, blank=True)
    random_traits = models.JSONField(default=list, blank=True)
    trait_rolls = models.JSONField(default=list, blank=True)
    trait_choices = models.JSONField(default=dict, blank=True)
    skills = models.JSONField(default=dict, blank=True)
    specialties = models.JSONField(default=list, blank=True, help_text='[["slug", level], ...]')
    augments = models.JSONField(default=list, blank=True)
    body_augments = models.JSONField(default=list, blank=True, help_text='[["slug", marque], ...]')
    stories = models.JSONField(default=list, blank=True)
    specialty_choices = models.JSONField(default=dict, blank=True,
                                         help_text='choices made when learning, e.g. {"<battle-theme slug>": "singing"}')

    # Play state.
    stance = models.CharField(max_length=120, blank=True)
    toggles = models.JSONField(default=list, blank=True)
    misc = models.JSONField(default=dict, blank=True)
    fight = models.JSONField(default=dict, blank=True,
                             help_text='fight mode: {"active": bool, "ap": AP left, "my_turn": bool, "round": n}')
    story_notes = models.TextField(blank=True, help_text="campaign journal; '# Heading' lines start a new block")
    plan = models.JSONField(default=list, blank=True,
                            help_text='planned level-ups: [{"level": n, "type": "specialty|skill|augment|note", ...}]')

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated"]

    def __str__(self):
        return self.name or f"Unnamed character #{self.pk}"

    def get_absolute_url(self):
        if self.status == "draft":
            return reverse("wizard", args=[self.pk])
        return reverse("sheet", args=[self.pk])

    # --- password -------------------------------------------------------------
    def set_password(self, raw):
        self.password = make_password(raw)

    def check_password(self, raw):
        return bool(self.password) and check_password(raw, self.password)

    # --- rules ----------------------------------------------------------------
    @property
    def race_data(self):
        return get_registry().races.get(self.race)

    @property
    def nationality_name(self):
        if self.nationality == "other" or not self.nationality:
            return self.nationality_custom
        nat = get_registry().nationalities.get(self.nationality)
        return nat["name"] if nat else self.nationality

    def to_state(self, include_items=True):
        items = []
        if include_items and self.pk:
            items = [i.to_item_state(slot=i.slot) for i in self.items.all()]
        lost = 0
        effect_keys = []
        custom = []
        if self.pk:
            for e in self.effects.filter(active=True):
                lost += e.lost_wounds
                if e.key:
                    effect_keys.append(e.key)
            custom = [c.as_modifier() for c in self.custom_modifiers.all()]
        return CharacterState(
            race=self.race or "human",
            level=self.level,
            fixed_traits=list(self.fixed_traits),
            random_traits=list(self.random_traits),
            trait_choices=dict(self.trait_choices),
            skills={k: int(v) for k, v in self.skills.items()},
            specialties=[(s, lvl) for s, lvl in self.specialties],
            augments=list(self.augments),
            body_augments=[(s, m) for s, m in self.body_augments],
            stories=list(self.stories),
            custom_modifiers=custom,
            items=items,
            stance=self.stance,
            toggles=set(self.toggles),
            misc={k: int(v) for k, v in self.misc.items() if v},
            effects=effect_keys,
            lost_wounds=lost,
        )

    def compute(self):
        from rules.engine.stats import compute

        return compute(self.to_state())

    @property
    def pending_levelups(self):
        if self.status != "active" or self.level >= tables.MAX_LEVEL:
            return 0
        return 1 if self.xp >= tables.XP_PER_LEVEL else 0


class InventoryItem(ItemFields):
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name="items")
    template = models.ForeignKey(ItemTemplate, null=True, blank=True, on_delete=models.SET_NULL)
    slot = models.CharField(max_length=20, choices=SLOT_CHOICES, default="carried")
    quantity = models.PositiveIntegerField(default=1)
    notes = models.CharField(max_length=255, blank=True)
    wounds_taken = models.PositiveSmallIntegerField(default=0, help_text="turrets: wounds the turret has taken")

    class Meta:
        ordering = ["slot", "name"]

    def __str__(self):
        return self.name

    @property
    def hands_label(self):
        if not self.is_weapon and self.kind != "deflection":
            return ""
        return {0: "no hand", 1: "one-handed", 2: "two-handed"}[tables.item_hands(self.to_item_state())]

    @property
    def turret_wounds_left(self):
        return tables.TURRET_WOUNDS - self.wounds_taken if "turret" in (self.variants or []) else None

    @classmethod
    def from_template(cls, character, template, slot="carried", quantity=1):
        return cls(character=character, template=template, slot=slot, quantity=quantity,
                   **template.item_values())


class Pet(models.Model):
    """An animal of a character (Pets & Predators). Built from a template, movement, special traits, training
    stories and derived-stat rows; the stat block comes from rules/engine/pets.py."""

    ORIGIN_CHOICES = [("tamed", "Tamed"), ("bioengineered", "Bio-engineered"), ("bought", "Bought"),
                      ("preset", "Narrator / sample")]

    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name="pets")
    name = models.CharField(max_length=100)
    origin = models.CharField(max_length=14, choices=ORIGIN_CHOICES, default="tamed")
    preset = models.CharField(max_length=60, blank=True)
    template = models.CharField(max_length=30)
    movement = models.JSONField(default=list, blank=True)
    traits = models.JSONField(default=list, blank=True, help_text='[["trait-slug", choice or null], ...]')
    stories = models.JSONField(default=list, blank=True)
    derived = models.JSONField(default=list, blank=True)
    sp_bonus = models.SmallIntegerField(default=0)
    wild = models.BooleanField(default=False, help_text="untamed: gets the wild Additional AP")
    levels = models.PositiveSmallIntegerField(default=0, help_text="bio-engineered: levels instead of SP")
    stance = models.CharField(max_length=40, blank=True)
    hp_damage = models.PositiveSmallIntegerField(default=0)
    wounds_taken = models.PositiveSmallIntegerField(default=0)
    venom_used = models.PositiveSmallIntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return self.name

    def to_state(self):
        from rules.engine.pets import PetState

        return PetState(template=self.template, movement=list(self.movement), traits=[list(t) for t in self.traits],
                        stories=list(self.stories), derived=list(self.derived), sp_bonus=self.sp_bonus,
                        origin=self.origin, wild=self.wild, stance=self.stance, levels=self.levels)


class Automaton(models.Model):
    """An automaton built by a character (core Automata rules; record like the Automaton Crafting Sheet).
    No password: reachable only from its owner's sheet. Numbers come from rules/engine/automaton.py."""

    TYPE_CHOICES = [("steamer", "Steamer"), ("fusebox", "Fuse box"), ("clockwork", "Clockwork")]

    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name="automatons")
    name = models.CharField(max_length=80)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="steamer")
    marque = models.PositiveSmallIntegerField(default=1, help_text="fuse box: number of specialties by marque")
    advanced = models.BooleanField(default=False, help_text="Beta Boilers / Advanced Brainworks / Advanced Analytics")
    diy = models.BooleanField(default=True, help_text="built and maintained with DIY (not bought)")
    core_augments = models.JSONField(default=list, blank=True)
    limbs = models.JSONField(default=list, blank=True)
    movement = models.JSONField(default=dict, blank=True)
    specialties = models.JSONField(default=list, blank=True)
    misc = models.JSONField(default=dict, blank=True)
    weapon = models.ForeignKey("InventoryItem", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    armor = models.ForeignKey("InventoryItem", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    equipment = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    hp_lost = models.PositiveIntegerField(default=0)
    wounds_taken = models.PositiveIntegerField(default=0)
    toggles = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return self.name

    def to_state(self):
        from rules.engine.automaton import AutomatonState

        return AutomatonState(type=self.type, marque=self.marque, advanced=self.advanced, diy=self.diy,
                              core_augments=[list(a) for a in self.core_augments], limbs=list(self.limbs),
                              movement=dict(self.movement), specialties=list(self.specialties), misc=dict(self.misc),
                              toggles=list(self.toggles),
                              armor=self.armor.to_item_state() if self.armor else None,
                              weapon=self.weapon.to_item_state() if self.weapon else None)

    def compute(self):
        from rules.engine.automaton import compute_automaton

        owner = self.character.compute()
        return compute_automaton(self.to_state(), [s for s, _l in self.character.specialties], owner.stats,
                                 set(self.character.augments))


class EffectEntry(models.Model):
    """An active status effect or called-shot (wounded/fatal) effect. ``key`` points into
    ``rules/engine/effects.py``; custom status effects have no key and no mechanical effect."""

    KIND_CHOICES = [("normal", "Called-shot effect"), ("wound", "Wound effect"), ("fatal", "Fatal effect"),
                    ("status", "Status effect")]

    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name="effects")
    kind = models.CharField(max_length=10, choices=KIND_CHOICES)
    key = models.CharField(max_length=40, blank=True)
    location = models.PositiveSmallIntegerField(null=True, blank=True, help_text="silhouette location 1-12")
    text = models.CharField(max_length=255)
    lost_wounds = models.PositiveSmallIntegerField(default=0, help_text="permanent max-wound loss")
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["kind", "created"]

    def __str__(self):
        return self.text

    @property
    def location_name(self):
        return effects.location_label(self.location) if self.location else ""

    @property
    def rule_text(self):
        data = effects.get(self.key)
        return data["text"] if data else ""


class CustomModifier(models.Model):
    """Narrator-granted stories/alterations or other custom bonuses."""

    WHEN_CHOICES = [("always", "Always"), ("toggle", "Toggle on sheet")]
    SCOPE_CHOICES = [("character", "Character"), ("melee", "Melee attacks"), ("ranged", "Ranged attacks"),
                     ("unarmed", "Unarmed attacks")]
    STAT_CHOICES = [(s, s.upper()) for s in ["acc", "eva", "stk", "def", "pri", "spd", "swim", "climb", "fly",
                                             "aug", "diy", "wnd", "hp", "soak", "dc"]] + \
        [(f"skill:{s}", f"Skill: {s}") for s in tables.ALL_SKILLS] + \
        [(f"attr:{a}", f"Attribute: {a}") for a in tables.ATTRIBUTES]

    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name="custom_modifiers")
    source = models.CharField(max_length=120, help_text="e.g. 'Story: Burn Victim'")
    stat = models.CharField(max_length=40, choices=STAT_CHOICES)
    value = models.IntegerField()
    when = models.CharField(max_length=10, choices=WHEN_CHOICES, default="always")
    scope = models.CharField(max_length=12, choices=SCOPE_CHOICES, default="character")

    def as_modifier(self):
        return {"stat": self.stat, "value": self.value, "when": self.when, "scope": self.scope,
                "op": "add", "source": self.source, "key": f"custom:{self.pk}"}


class LevelLog(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name="level_logs")
    level = models.PositiveSmallIntegerField()
    data = models.JSONField(default=dict)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["level"]


class Feedback(models.Model):
    """Bug report, feature request or general feedback sent via the speech bubble on every page.

    ``meta`` holds what the browser and server knew at the time (sheet tab, viewport, device,
    user agent, admin mode …) so the narrator can reproduce the situation."""

    CATEGORY_CHOICES = [("bug", "Bug"), ("feature", "Feature request"), ("feedback", "Feedback"), ("other", "Other")]
    STATUS_CHOICES = [("new", "New"), ("progress", "In progress"), ("done", "Done"), ("wontfix", "Won't fix")]
    OPEN_STATUSES = ("new", "progress")

    created = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="feedback")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    name = models.CharField(max_length=80, blank=True)
    message = models.TextField()
    page_url = models.CharField(max_length=500, blank=True)
    page_title = models.CharField(max_length=200, blank=True)
    character = models.ForeignKey(Character, null=True, blank=True, on_delete=models.SET_NULL,
                                  related_name="feedback")
    character_name = models.CharField(max_length=120, blank=True, help_text="snapshot, kept if the character is deleted")
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"{self.get_category_display()}: {self.message[:60]}"

    @property
    def is_open(self):
        return self.status in self.OPEN_STATUSES
