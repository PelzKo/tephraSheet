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
    current_wounds = models.IntegerField(null=True, blank=True)
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

    class Meta:
        ordering = ["slot", "name"]

    def __str__(self):
        return self.name

    @property
    def hands_label(self):
        if not self.is_weapon and self.kind != "deflection":
            return ""
        return {0: "no hand", 1: "one-handed", 2: "two-handed"}[tables.item_hands(self.to_item_state())]

    @classmethod
    def from_template(cls, character, template, slot="carried", quantity=1):
        return cls(character=character, template=template, slot=slot, quantity=quantity,
                   **template.item_values())


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
        return effects.LOCATION_LABELS.get(self.location, "") if self.location else ""

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
