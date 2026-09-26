"""Plain data describing a character, independent of Django models."""

from dataclasses import dataclass, field


@dataclass
class ItemState:
    name: str
    kind: str  # melee firearm bow crossbow armor deflection ammo gear animal vehicle
    size: str = ""
    slot: str = ""  # weapon1 weapon2 armor deflection worn carried stored
    variants: list = field(default_factory=list)
    material: str = "metal"
    beta: bool = False
    # Explicit overrides; None = use the size table.
    ap_use: int | None = None
    ap_ready: int | None = None
    dc: int | None = None
    reach: int | None = None
    range: int | None = None
    increment: int | None = None
    soak: int | None = None
    eva_penalty: int | None = None
    spd_penalty: int | None = None
    climb_swim_penalty: int | None = None
    deflect_bonus: int | None = None
    deflect_ranged: bool = False
    deflect_melee: bool = True
    modifiers: list = field(default_factory=list)
    augments: list = field(default_factory=list)  # [(augment_slug, marque 1-4)]
    notes: str = ""
    id: int | None = None


@dataclass
class CharacterState:
    race: str
    level: int = 1
    fixed_traits: list = field(default_factory=list)  # trait keys "race/slug"
    random_traits: list = field(default_factory=list)  # trait keys
    trait_choices: dict = field(default_factory=dict)  # trait key -> chosen value
    skills: dict = field(default_factory=dict)  # allocated points (creation + level-ups)
    specialties: list = field(default_factory=list)  # [(slug, level_gained)] in sheet order
    augments: list = field(default_factory=list)  # known augment slugs
    body_augments: list = field(default_factory=list)  # [(slug, marque)] installed on the character
    stories: list = field(default_factory=list)  # story slugs
    custom_modifiers: list = field(default_factory=list)  # modifier dicts with "source"
    items: list = field(default_factory=list)  # ItemState
    stance: str = ""  # specialty slug, or "footing"
    toggles: set = field(default_factory=set)
    misc: dict = field(default_factory=dict)  # admin overrides: stat / "attr:X" / "skill:X" -> int
    fatigued: bool = False
    lost_wounds: int = 0  # permanent max-wound losses from fatal effects

    def equipped(self, slot):
        return [i for i in self.items if i.slot == slot]

    @property
    def weapons(self):
        return [i for i in self.items if i.slot in ("weapon1", "weapon2")]

    @property
    def armor(self):
        worn = self.equipped("armor")
        return worn[0] if worn else None

    @property
    def deflection(self):
        worn = self.equipped("deflection")
        return worn[0] if worn else None
