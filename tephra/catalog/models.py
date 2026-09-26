from django.db import models

from rules.engine.state import ItemState

KIND_CHOICES = [
    ("melee", "Melee weapon"),
    ("firearm", "Firearm"),
    ("bow", "Bow"),
    ("crossbow", "Crossbow"),
    ("armor", "Armor"),
    ("deflection", "Deflection item / shield"),
    ("ammo", "Ammunition"),
    ("gear", "Gear"),
    ("animal", "Animal"),
    ("vehicle", "Vehicle"),
]
WEAPON_KINDS = ("melee", "firearm", "bow", "crossbow")
SIZE_CHOICES = [
    ("", "–"),
    ("minimal", "Minimal (armor)"),
    ("light", "Light"),
    ("medium", "Medium"),
    ("heavy", "Heavy"),
    ("super-heavy", "Super-Heavy"),
]
MATERIAL_CHOICES = [("metal", "Metal"), ("wood", "Wood"), ("organic", "Organic"), ("textile", "Textile")]


class ItemFields(models.Model):
    """Fields shared by catalog templates and inventory items.

    Numeric overrides left empty fall back to the size tables of the rules.
    """

    name = models.CharField(max_length=120)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default="gear")
    size = models.CharField(max_length=20, choices=SIZE_CHOICES, blank=True)
    variants = models.JSONField(default=list, blank=True)
    material = models.CharField(max_length=20, choices=MATERIAL_CHOICES, default="metal")
    beta = models.BooleanField(default=False, help_text="Beta item: +2 augment slots")
    concealable = models.BooleanField(default=False)
    hands = models.PositiveSmallIntegerField(
        null=True, blank=True, choices=[(0, "No hand (worn)"), (1, "One-handed"), (2, "Two-handed")],
        help_text="empty = size table (melee/firearm/crossbow: light & medium one-handed; bows always two-handed; "
                  "cloak no hand, shield/parrying dagger one hand)")
    ap_use = models.IntegerField(null=True, blank=True)
    ap_ready = models.IntegerField(null=True, blank=True)
    dc = models.IntegerField("damage class", null=True, blank=True)
    reach = models.IntegerField(null=True, blank=True, help_text="ft (melee)")
    range = models.IntegerField(null=True, blank=True, help_text="base range in ft")
    increment = models.IntegerField(null=True, blank=True, help_text="range increment in ft")
    soak = models.IntegerField("soak class", null=True, blank=True)
    eva_penalty = models.IntegerField(null=True, blank=True)
    spd_penalty = models.IntegerField(null=True, blank=True)
    climb_swim_penalty = models.IntegerField(null=True, blank=True)
    deflect_bonus = models.IntegerField(null=True, blank=True)
    deflect_ranged = models.BooleanField(default=False)
    deflect_melee = models.BooleanField(default=True)
    augments = models.JSONField(default=list, blank=True, help_text='[["augment-slug", marque], ...]')
    modifiers = models.JSONField(default=list, blank=True)
    price_dukes = models.IntegerField(default=0)
    description = models.TextField(blank=True)

    class Meta:
        abstract = True

    ITEM_FIELDS = ["name", "kind", "size", "variants", "material", "beta", "concealable", "hands", "ap_use", "ap_ready",
                   "dc", "reach", "range", "increment", "soak", "eva_penalty", "spd_penalty",
                   "climb_swim_penalty", "deflect_bonus", "deflect_ranged", "deflect_melee", "augments",
                   "modifiers", "price_dukes", "description"]

    def item_values(self):
        return {f: getattr(self, f) for f in self.ITEM_FIELDS}

    @property
    def is_weapon(self):
        return self.kind in WEAPON_KINDS

    @property
    def slot_count(self):
        from rules.engine.tables import MATERIAL_SLOTS

        return MATERIAL_SLOTS.get(self.material, 3) + (2 if self.beta else 0)

    def to_item_state(self, slot=""):
        return ItemState(
            name=self.name, kind=self.kind, size=self.size, slot=slot, variants=list(self.variants or []),
            material=self.material, beta=self.beta, concealable=self.concealable, hands=self.hands,
            ap_use=self.ap_use, ap_ready=self.ap_ready, dc=self.dc,
            reach=self.reach, range=self.range, increment=self.increment, soak=self.soak,
            eva_penalty=self.eva_penalty, spd_penalty=self.spd_penalty,
            climb_swim_penalty=self.climb_swim_penalty, deflect_bonus=self.deflect_bonus,
            deflect_ranged=self.deflect_ranged, deflect_melee=self.deflect_melee,
            modifiers=list(self.modifiers or []), augments=[tuple(a) for a in (self.augments or [])],
            notes=getattr(self, "notes", ""), id=self.pk,
        )


class ItemTemplate(ItemFields):
    """Global catalog entry players can pick from ("found something")."""

    SOURCE_CHOICES = [("book", "Playing Guide"), ("custom", "Custom")]

    is_starting_gear = models.BooleanField(default=False)
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default="custom")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["kind", "name"]
        constraints = [models.UniqueConstraint(fields=["name", "kind"], name="unique_template_name_kind")]

    def __str__(self):
        return self.name
