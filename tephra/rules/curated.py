"""Hand-curated structured data that the markdown cannot express reliably.

Merged over the parsed data by ``build_rules_data`` (curated keys win).

Modifier schema (see rules/engine/modifiers.py):
    stat     acc eva stk def pri spd swim climb fly aug diy wnd hp soak ap
             dc (with scope), ap_ready, reach, essence_slots, armor_degree,
             skill:<Skill>, attr:<Attribute>, roll:<Attribute> (attribute-roll bonus: Misc bubble,
             or only listed with when=note)
    value    int                      | formula: str (safe expression)
    by_marque [I, II, III, IV]        (augments)
    op       add (default) | base (replace base value) | transfer (Raging)
    when     always (default) | stance | toggle | note
    scope    character (default) | weapon (the item it is on) | melee (incl. unarmed)
             | unarmed | ranged
    label    optional short explanation shown in the breakdown
"""


def mod(stat, value=None, formula=None, when="always", scope="character", op="add", label="", **extra):
    d = {"stat": stat, "op": op, "when": when, "scope": scope}
    if value is not None:
        d["value"] = value
    if formula is not None:
        d["formula"] = formula
    if label:
        d["label"] = label
    d.update(extra)
    return d


# --------------------------------------------------------------------------- specialties
# Keyed by specialty name (or slug for duplicate names).
SPECIALTIES = {
    "Drunken Boxing": {"modifiers": [mod("acc", formula="brawl", when="toggle", scope="unarmed",
                                         label="drunken called shot")]},
    "Fisticuffs": {"modifiers": [mod("dc", formula="1 + brawl // 6", when="stance", scope="unarmed")]},
    "Hold Steady": {"modifiers": [mod("note", formula="3 + brawl // 4", when="note",
                                      label="allies' Accuracy bonus vs. your grabbed target")]},
    "Knock Aside": {"modifiers": [mod("note", formula="3 + brawl // 8", when="note",
                                      label="Evade bonus when deflecting bare-handed")]},
    "Raging": {"modifiers": [mod("stk", op="transfer", when="stance", sources=["acc", "eva", "def"],
                                 label="Accuracy, Evade and Defense are added to Strike and set to 0")]},
    "Berserker": {"modifiers": [mod("dc", formula="1 + frenzy // 6", when="stance", scope="melee")]},
    "Heavy Hitter": {"modifiers": [mod("dc", formula="overpower // 4", when="stance", scope="melee")]},
    "Monstrous Attacks": {"modifiers": [mod("dc", formula="2 + overpower // 6", when="toggle", scope="melee",
                                            label="super-heavy melee attack")]},
    "Body of Steel": {"modifiers": [mod("note", formula="def_total", when="note",
                                        label="added to resists")]},
    "Thick Skin": {"modifiers": [mod("soak", formula="1 + resilience // 5")]},
    "Tough Stuff": {"modifiers": [mod("hp", formula="specialties * (1 + resilience // 8)")]},
    "Walking Fortress": {"modifiers": [mod("def", formula="resilience // 3", when="stance")]},
    "Armored Ease": {"modifiers": [mod("armor_degree", value=1, label="armor penalties as one degree lighter")]},
    "Armored Freedom": {"modifiers": [mod("armor_degree", value=2, label="armor penalties two more degrees lighter")]},
    "First Strike": {"modifiers": [mod("acc", formula="espionage", when="toggle", label="first strike")]},
    "Flowing Shadow": {"modifiers": [mod("eva", formula="espionage // 4", when="toggle")]},
    "Pierce the Darkness": {"modifiers": [mod("acc", formula="espionage // 4", when="toggle")]},
    "Improv Fighter": {"modifiers": [mod("acc", formula="expertise // 3", when="toggle",
                                         label="impromptu weapon")]},
    "Demoman": {"modifiers": [mod("note", formula="expertise // 3", when="note", label="explosive DC bonus")]},
    "Chime In": {"modifiers": [mod("note", formula="showmanship // 2", when="note", label="bonus")]},
    "Epic Dance": {"stance": True, "modifiers": [mod("eva", formula="3 + showmanship // 5", when="stance")]},
    "Never Stop the Dance": {"modifiers": [mod("def", formula="3 + showmanship // 5", when="toggle",
                                               label="while dancing")]},
    "Battle Theme": {"stance": True, "modifiers": [mod("acc", formula="3 + showmanship // 5", when="stance")]},
    "Victory Theme": {"modifiers": [mod("stk", formula="3 + showmanship // 5", when="toggle",
                                        label="while Battle Theme plays")]},
    "Walking Darkness": {"modifiers": [mod("eva", value=4, when="stance")]},
    "Blitzkreig": {"modifiers": [mod("note", formula="10 + 5 * (tactical // 5)", when="note",
                                     label="allies' speed bonus toward the target (ft)")]},
    "Flying Fortress": {"modifiers": [mod("note", formula="ace // 2", when="note", label="vehicle Defense bonus")]},
    "Snap Reload": {"modifiers": [mod("ap_ready", value=-1, scope="ranged", label="Snap Reload")]},
    "En-Garde": {"modifiers": [mod("note", value=4, when="note", label="Accuracy on reflexive attacks")]},
    "Void Strike": {"modifiers": [mod("note", formula="5 * grace", when="note", label="extra reach (ft)")]},
    "Don't Tell Me the Odds": {"modifiers": [mod("note", formula="1 + luck // 10", when="note", label="uses")]},
    "Druidic": {"modifiers": [mod("dc", value=2, when="stance", scope="melee",
                                  label="wood/organic weapons")]},
    "Naturalist": {"modifiers": [mod("soak", formula="shamanism // 5", when="toggle")]},
    "Weapon Support": {"modifiers": [mod("note", formula="1 + armsmith // 4", when="note",
                                         label="allies' Accuracy bonus")]},
    "Beta Essence": {"modifiers": [mod("essence_slots", value=2)]},
}

AP_SACRIFICE_SPECIALTIES = ["Grief & Hope", "Infallible Faith", "Prayer", "Smite", "Conduit of Faith"]

# Usage conditions: specialties without a formal prerequisite that only work with certain equipment.
# They become soft requirement clauses: learning is allowed, the picker and the sheet warn while unmet.
# Weapon matchers are tested against the weapons in the hands (weapon1 = left, weapon2 = right); a
# matcher with "with_specialty" only counts when that specialty is known (e.g. Pinpoint Shot).
# "hands": 1 uses the item's hands (One-Handing It included). Clause flags: "all" = every equipped
# weapon must match, "other_hand_empty" = exactly this weapon and one free hand.
MELEE_SIZES = ["light", "medium", "heavy", "super-heavy"]
RANGED_KINDS = ["firearm", "bow", "crossbow"]


def weapon(text, *matchers):
    return {"type": "weapon", "text": text, "weapons": list(matchers)}


def match(kinds=None, sizes=None, variant=None, materials=None, with_specialty=None, concealable=False, hands=None):
    return {k: v for k, v in (("kinds", kinds), ("sizes", sizes), ("variant", variant), ("materials", materials),
                              ("with_specialty", with_specialty), ("concealable", concealable),
                              ("hands", hands)) if v}


LIGHT_MELEE = weapon("a light melee weapon", match(["melee"], ["light"]),
                     match(RANGED_KINDS, ["light"], with_specialty="Pinpoint Shot"))
HEAVY_OR_SMALLER = weapon("a heavy or smaller melee weapon", match(["melee"], ["light", "medium", "heavy"]))
HEAVY_PLUS = weapon("a heavy or super-heavy melee weapon", match(["melee"], ["heavy", "super-heavy"]))
SUPER_HEAVY_MELEE = weapon("a super-heavy melee weapon", match(["melee"], ["super-heavy"]))
ONE_HANDED = weapon("a one-handed melee weapon", match(["melee"], hands=1))
MELEE_WEAPON = weapon("a melee weapon", match(["melee"]))
RANGED_WEAPON = weapon("a ranged weapon", match(RANGED_KINDS), match(["melee"], variant="throwing"))
BOW = weapon("a bow", match(["bow"]))

USAGE_CONDITIONS = {
    # Frenzy / Overpower: weapon size
    "Fray Fighter": [HEAVY_OR_SMALLER],
    "Hundred Strikes": [HEAVY_OR_SMALLER],
    "Unquenchable Thirst": [HEAVY_OR_SMALLER],
    "Heavy Hitter": [HEAVY_PLUS],
    "Keep Them Down": [HEAVY_PLUS],
    "Chipping Away": [HEAVY_PLUS],
    "Armor Sunder": [HEAVY_PLUS],
    "Monstrous Attacks": [SUPER_HEAVY_MELEE],
    "Titanic Strength": [SUPER_HEAVY_MELEE],
    "Robust Toss": [weapon("a medium or larger throwing weapon", match(["melee"], MELEE_SIZES[1:], "throwing"),
                           match(["melee"], MELEE_SIZES[1:], with_specialty="Hurl"))],
    # Espionage / Swashbuckling / Agility
    "Heartseeker": [LIGHT_MELEE],
    "Critical Hits": [LIGHT_MELEE],
    "Hairsplitter": [LIGHT_MELEE],
    "Invisible Blade": [dict(weapon("only light, concealable melee weapons",
                                    match(["melee"], ["light"], concealable=True)), all=True)],
    "Fisticuffs": [{"type": "free_hand", "text": "a free hand"}],
    "En-Garde": [dict(ONE_HANDED, text="a one-handed melee weapon with the other hand empty",
                      other_hand_empty=True)],
    "Lightning Slash": [ONE_HANDED],
    "Flickering": [ONE_HANDED],
    "Side-Swipe": [ONE_HANDED],
    "Parry": [MELEE_WEAPON],
    "Riposte": [MELEE_WEAPON],
    "Beat Parry": [MELEE_WEAPON],
    "Experienced Parries": [MELEE_WEAPON],
    "Druidic": [weapon("a wooden or organic weapon", match(materials=["wood", "organic"]))],
    # Resilience / Swashbuckling: deflection items and armor
    "Blast Proof": [{"type": "deflection", "text": "a shield", "shield": True}],
    "Brace for Impact": [{"type": "deflection", "text": "a shield", "shield": True}],
    "Protector": [{"type": "deflection", "text": "a shield", "shield": True}],
    "Sword and Board": [{"type": "deflection", "text": "a deflection item"}],
    "Armored Ease": [{"type": "armor_worn", "text": "armor worn"}],
    "Armored Freedom": [{"type": "armor_worn", "text": "armor worn"}],
    "Naturalist": [{"type": "armor_material", "text": "wooden or organic armor",
                    "materials": ["wood", "organic"]}],
    # Marksmanship / Faith: ranged weapons
    "Arching Shot": [BOW],
    "Flight of Arrows": [BOW],
    "Flesh Biter": [BOW],
    "Efficient Ranger": [weapon("a heavy or super-heavy bow", match(["bow"], ["heavy", "super-heavy"]))],
    "Snap Reload": [weapon("a firearm or crossbow", match(["firearm", "crossbow"]))],
    "Stable Shot": [weapon("a super-heavy bow, crossbow or firearm", match(RANGED_KINDS, ["super-heavy"]))],
    "Penetrating Shot": [RANGED_WEAPON],
    "Point Blank": [RANGED_WEAPON],
    "Knock-Off": [RANGED_WEAPON],
    "Turret": [RANGED_WEAPON],
    "Smiting Shot": [RANGED_WEAPON],
    # Ace: both hands on the controls
    **{name: [{"type": "hands_empty", "text": "both hands empty (on the controls)"}] for name in [
        "Focused Flying", "Fine-Tuned Flying", "Fully Focused Flying"]},
}

# Conditions the sheet can't check; shown highlighted in the specialty details.
USAGE_NOTES = {
    "Turret": "Only while stationary and on your feet (not mounted). Moving ends the stance.",
}

# Choices made when learning a specialty (stored in Character.specialty_choices).
SPECIALTY_OPTIONS = {
    "Battle Theme": {"label": "How do you perform?", "options": {
        "singing": "Singing (a called shot to your neck cancels it)",
        "instrument": "Playing an instrument (a sunder or disarm cancels it)"}},
}

# --------------------------------------------------------------------------- races
RACES = {
    "human": {"fixed_choose": 2},
    "ayodin": {},
    "elf": {},
    "farishtaa": {},
    # Gnomes choose one random trait and roll one more (duplicates re-rolled).
    "gnome": {"unarmed_dc": 1, "random_count": 2, "random_choose": 1},
    "satyr": {},
}

RACIAL_TRAITS = {
    "human/favored-attribute": {"choice": "attribute"},
    "human/innovative": {"modifiers": [mod("diy", 1), mod("aug", 2)]},
    "human/relentless": {"modifiers": [mod("hp", formula="3 + specialties")]},
    "human/great-height": {"modifiers": [mod("stk", 2)]},
    "human/hardy-stout": {"modifiers": [mod("hp", 6)]},
    "human/momentum": {"modifiers": [mod("pri", 5, when="toggle", label="battle is expected")]},
    "human/monkeys-uncle": {"modifiers": [mod("climb", 10)]},
    "human/quick-feet": {"modifiers": [mod("spd", 35, op="base")]},
    "human/reactionary": {"modifiers": [mod("pri", 3)]},
    "ayodin/versatile-wing-fins": {"modifiers": [mod("eva", 1)]},
    "ayodin/born-in-the-seas": {"modifiers": [mod("swim", 10)]},
    "ayodin/natural-touch": {"modifiers": [mod("dc", 3, op="base", scope="unarmed")]},
    "ayodin/terror-from-the-deep": {"modifiers": [mod("stk", 3, when="toggle", scope="melee",
                                                      label="vs adjacent foes")]},
    "elf/big-boned": {"modifiers": [mod("roll:Brute", 2)]},
    "elf/tough": {"modifiers": [mod("hp", 4)]},
    "elf/tree-ripping-strength": {"modifiers": [mod("dc", 1, scope="melee")]},
    "elf/weak-souls": {"modifiers": [mod("roll:Spirit", -3)]},
    "elf/depleted-essence": {"modifiers": [mod("essence_slots", -1)]},
    "elf/danger-sense": {"modifiers": [mod("pri", 3)]},
    "elf/flight-without-wings": {"modifiers": [mod("spd", 10)]},
    "elf/fruit-of-the-fallen": {"negates": ["elf/weak-souls", "farishtaa/botched-surgery:weak-souls"],
                                "modifiers": [mod("roll:Spirit", 3, when="note", label="when using Heroics")]},
    "elf/noble-creature": {"modifiers": [mod("stk", formula="level", when="toggle", label="attack +1 AP")]},
    "farishtaa/born-to-be-airborne": {"modifiers": [mod("skill:Ace", 2)]},
    "farishtaa/piercing-scrutiny": {"modifiers": [mod("acc", 1)]},
    "farishtaa/botched-surgery": {"modifiers": [
        mod("dc", 1, scope="melee", label="Tree-Ripping Strength"),
        mod("roll:Spirit", -3, label="Weak Souls"),
    ]},
    "farishtaa/dancers-body": {"modifiers": [mod("roll:Dexterity", 2)]},
    "farishtaa/prominent-host": {"reroll_on": "elf"},
    "farishtaa/tinge-of-insanity": {"modifiers": [mod("acc", 4, when="toggle", label="at 0 HP"),
                                                  mod("stk", 4, when="toggle", label="at 0 HP")]},
    "farishtaa/unexplainable-memories": {"modifiers": [mod("roll:Cunning", 2)]},
    "gnome/greater-spirit": {"modifiers": [mod("roll:Spirit", 3)]},
    "gnome/light-build": {"modifiers": [mod("roll:Brute", -2)]},
    "gnome/small-stature": {"modifiers": [mod("eva", 1)]},
    "gnome/smaller-weapons": {"modifiers": []},
    "gnome/random-racial-traits": {"modifiers": []},
    "gnome/piercing-sight": {"modifiers": [mod("acc", 2, scope="ranged", label="Piercing Sight")]},
    "gnome/ripcord-muscles": {"negates": ["gnome/light-build"],
                              "modifiers": [mod("stk", 2), mod("dc", 2, op="base", scope="unarmed")]},
    "gnome/wiry": {"modifiers": [mod("eva", 1)]},
    "gnome/growth-intensity": {"modifiers": []},
    "satyr/built-to-last": {"modifiers": [mod("hp", 6)]},
    "satyr/expecting-the-worst": {"modifiers": [mod("pri", 4)]},
    "satyr/fleet-of-foot": {"modifiers": [mod("spd", 10)]},
    "satyr/frightening-combatant": {"modifiers": [mod("dc", 4, op="base", scope="unarmed")]},
    "satyr/brothers-in-arms": {"modifiers": [mod("acc", 2, when="toggle", label="adjacent to a satyr ally")]},
}

# --------------------------------------------------------------------------- stories
STORIES = {
    "stormship-engineer": {"modifiers": [mod("skill:Engineer", 1)]},
    "crusader-of-tailemy": {"modifiers": [mod("stk", 1, when="toggle", label="vs heretics")]},
    "paladin-of-tailemy": {"modifiers": [mod("soak", 1, when="toggle", label="defending a Tailemite")]},
    "devout-of-tailemy": {"modifiers": [mod("roll:Spirit", 1, when="toggle", label="attended a sermon this week")]},
}

NATIONALITY_STORY_GROUP = {
    "Evanglessian": "Evangless", "Dalvozzean": "Dalvozzea", "Izedan": "Izeda",
    "Paldoran Exile": "Paldorus", "Zel Haud": "Zelhost",
}

# --------------------------------------------------------------------------- augments
# (section heading prefix, (skill, [augment lists])) — lists match [CRAFT:x] tags.
AUGMENT_SECTIONS = [
    ("General alchemical augments", ("Alchemy", ["acid", "gas", "medicine", "poison"])),
    ("Acid augments", ("Alchemy", ["acid"])),
    ("Gas augments", ("Alchemy", ["gas"])),
    ("Medicine augments", ("Alchemy", ["medicine"])),
    ("Poison augments", ("Alchemy", ["poison"])),
    ("Firearm & crossbow augments", ("Armsmith", ["firearm", "crossbow"])),
    ("Melee & throwing weapon augments", ("Armsmith", ["melee"])),
    ("Bow augments", ("Armsmith", ["bow"])),
    ("Armor & shield augments", ("Armsmith", ["armor"])),
    ("Boiler augments", ("Automata", ["steamer"])),
    ("Brainworks augments", ("Automata", ["fusebox"])),
    ("Analytics augments", ("Automata", ["clockwork"])),
    ("Prosthetics", ("Automata", ["prosthetic"])),
    ("Essence augments", ("Bio-Flux", ["essence"])),
    ("Bio-zapper augments", ("Bio-Flux", ["biozapper"])),
    ("Auto & clanker augments", ("Engineer", ["auto", "clanker"])),
    ("Vehicle armoring augments", ("Engineer", ["vehicle armor"])),
    ("Gadgetry – explosives", ("Gadgetry", ["explosive"])),
    ("Gadgetry – eyewear", ("Gadgetry", ["eyewear"])),
    ("Gadgetry – trinkets", ("Gadgetry", ["trinket"])),
]

# Augments whose marque values change sheet numbers. scope=weapon applies to the item it is on.
AUGMENTS = {
    "armsmith-firearm-crossbow-accurate": {"modifiers": [mod("acc", scope="weapon", by_marque=[1, 2, 3, 4])]},
    "armsmith-firearm-crossbow-damaging": {"modifiers": [mod("dc", scope="weapon", by_marque=[1, 2, 3, 4])]},
    "armsmith-firearm-crossbow-bipod": {"modifiers": [mod("acc", scope="weapon", when="toggle", label="bipod set up",
                                                          by_marque=[1, 2, 3, 4])]},
    "armsmith-melee-accurate": {"modifiers": [mod("acc", scope="weapon", by_marque=[1, 2, 3, 4])]},
    "armsmith-melee-damaging": {"modifiers": [mod("dc", scope="weapon", by_marque=[1, 2, 3, 4])]},
    "armsmith-melee-powerful": {"modifiers": [mod("stk", scope="weapon", by_marque=[2, 4, 6, 8])]},
    "armsmith-armor-damage-soaking": {"modifiers": [mod("soak", by_marque=[1, 2, 3, 4])]},
    "armsmith-armor-defensive": {"modifiers": [mod("def", by_marque=[2, 4, 6, 8])]},
    "armsmith-armor-mobile": {"modifiers": [mod("spd", by_marque=[5, 10, 10, 15])]},
    "armsmith-armor-bulletproofing": {"modifiers": [mod("def", when="toggle", label="vs firearms",
                                                        by_marque=[2, 4, 6, 8])]},
    "bio-flux-essence-aerodynamize": {"modifiers": [mod("spd", by_marque=[5, 10, 10, 15])]},
    "bio-flux-essence-energize": {"modifiers": [mod("hp", by_marque=[3, 6, 9, 12])]},
    "bio-flux-essence-limitless-memory": {"modifiers": [mod("attr:Sciences", by_marque=[3, 6, 9, 12])]},
    "bio-flux-essence-marathon-body": {"modifiers": [mod("wnd", by_marque=[1, 2, 3, 4])]},
    "bio-flux-essence-performance-enhancer": {"modifiers": [mod("attr:Brute", by_marque=[1, 2, 3, 4])]},
    "bio-flux-essence-scaleskin": {"modifiers": [mod("soak", by_marque=[1, 2, 3, 4])]},
    "bio-flux-essence-sixth-sense": {"modifiers": [mod("pri", by_marque=[2, 4, 6, 8])]},
    "bio-flux-essence-stonebones": {"modifiers": [mod("spd", by_marque=[-10, -10, -5, 0])]},
}

# --------------------------------------------------------------------------- catalog seed


def _weapon(name, kind, size, variants=(), description="", **extra):
    from rules.engine.tables import WEAPON_PRICES_DUKES

    d = {"name": name, "kind": kind, "size": size, "variants": list(variants),
         "price_dukes": WEAPON_PRICES_DUKES.get((kind, size), 0), "description": description,
         "is_starting_gear": False, "material": "metal"}
    d.update(extra)
    return d


CATALOG_WEAPONS_AND_ARMOR = [
    _weapon("Light melee weapon (dagger, knife)", "melee", "light", concealable=True),
    _weapon("Medium melee weapon (sword, axe, mace)", "melee", "medium"),
    _weapon("Heavy melee weapon (greatsword, great axe)", "melee", "heavy"),
    _weapon("Super-heavy melee weapon (massive hammer)", "melee", "super-heavy",
            description="Needs the Footing stance; without it −3 Accuracy and Strike."),
    _weapon("Whip", "melee", "light", ["flexible"], material="organic"),
    _weapon("Flail / chain", "melee", "medium", ["flexible"]),
    _weapon("Spear", "melee", "medium", ["polearm"], material="wood"),
    _weapon("Halberd", "melee", "heavy", ["polearm"]),
    _weapon("Throwing knife", "melee", "light", ["throwing"], concealable=True),
    _weapon("Javelin", "melee", "medium", ["throwing"], material="wood"),
    _weapon("Bolas", "melee", "light", ["throwing", "flexible"], material="organic"),
    _weapon("Light firearm (pocket pistol)", "firearm", "light", concealable=True),
    _weapon("Medium firearm (revolver, pistol)", "firearm", "medium"),
    _weapon("Heavy firearm (rifle, shotgun)", "firearm", "heavy"),
    _weapon("Double-barreled shotgun", "firearm", "heavy", ["double-barreled"]),
    _weapon("Super-heavy firearm (elephant gun)", "firearm", "super-heavy"),
    _weapon("Light bow (slingshot, shortbow)", "bow", "light", material="wood"),
    _weapon("Medium bow", "bow", "medium", material="wood"),
    _weapon("Heavy bow (longbow)", "bow", "heavy", material="wood"),
    _weapon("Super-heavy bow", "bow", "super-heavy", material="wood"),
    _weapon("Light crossbow", "crossbow", "light", material="wood"),
    _weapon("Medium crossbow (pistol crossbow)", "crossbow", "medium", material="wood"),
    _weapon("Heavy crossbow", "crossbow", "heavy", material="wood"),
    _weapon("Super-heavy crossbow (steam crossbow)", "crossbow", "super-heavy"),
    {"name": "Minimal armor (padded clothes)", "kind": "armor", "size": "minimal", "price_dukes": 10,
     "material": "textile", "description": "Don: 3 AP."},
    {"name": "Light armor (leather)", "kind": "armor", "size": "light", "price_dukes": 50,
     "material": "organic", "description": "Don: 6 AP."},
    {"name": "Medium armor (chain, brigandine)", "kind": "armor", "size": "medium", "price_dukes": 150,
     "material": "metal", "description": "Don: 24 AP (12 AP with help)."},
    {"name": "Heavy armor (plate)", "kind": "armor", "size": "heavy", "price_dukes": 400,
     "material": "metal", "description": "Don: 3 min (1 min with help)."},
    {"name": "Super-heavy armor (full plate)", "kind": "armor", "size": "super-heavy", "price_dukes": 750,
     "material": "metal", "description": "Don: 10 min (3 min with help)."},
    {"name": "Parrying Dagger", "kind": "deflection", "size": "light", "deflect_bonus": 3,
     "deflect_ranged": False, "deflect_melee": True, "price_dukes": 10, "material": "metal",
     "description": "Deflect (1 AP, melee only). Also counts as a light weapon."},
    {"name": "Cloak", "kind": "deflection", "size": "light", "deflect_bonus": 3, "deflect_ranged": False,
     "deflect_melee": True, "price_dukes": 10, "material": "textile",
     "description": "Deflect (1 AP, melee only). Hand stays free, can make grabs."},
    {"name": "Shield", "kind": "deflection", "size": "medium", "deflect_bonus": 4, "deflect_ranged": True,
     "deflect_melee": True, "price_dukes": 40, "material": "wood",
     "description": "Deflect (1 AP) vs melee and ranged. Holding things in the shield hand prevents deflecting."},
    {"name": "Cartridges (standard)", "kind": "ammo", "price_dukes": 0, "description": "Base stats."},
    {"name": "Shot cartridges", "kind": "ammo", "price_dukes": 0,
     "description": "No accuracy loss with range; −1 DC per range increment beyond base."},
    {"name": "Sniper cartridges", "kind": "ammo", "price_dukes": 0,
     "description": "−1 Acc per 2 range increments; −1 DC."},
    {"name": "High damage cartridges", "kind": "ammo", "price_dukes": 0,
     "description": "+2 DC; +1 AP readying time."},
    {"name": "Blank cartridges", "kind": "ammo", "price_dukes": 0, "description": "No projectile."},
    {"name": "Arrows / bolts (standard)", "kind": "ammo", "price_dukes": 0, "description": "Base stats."},
    {"name": "Bladed arrows / bolts", "kind": "ammo", "price_dukes": 0,
     "description": "−2 Acc; 1 bleeding per tier of damage dealt."},
    {"name": "Hooked arrows / bolts", "kind": "ammo", "price_dukes": 0,
     "description": "Removing costs 2 AP; attach rope for 1 AP → climb/zip-line."},
    {"name": "Signal arrows / bolts", "kind": "ammo", "price_dukes": 0,
     "description": "Very loud whistle; −1 DC."},
]

CATALOG_BRAND_OVERRIDES = {
    "CRIMSON (clothing line)": {"kind": "armor", "size": "minimal", "material": "textile"},
    "The Lawn-Deformer (chainsaw)": {"kind": "melee", "size": "medium", "material": "metal"},
    "The Fashionable Arrival (flight pack)": {"modifiers": [mod("fly", 40, op="base")]},
    "Grapple Gun": {"modifiers": [mod("climb", 20, when="toggle", label="retracting the cord")]},
}
