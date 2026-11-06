"""Races of Tephra: modifiers of the new races' traits, keyed "<race>/<trait-slug>" (see rules/curated.py)."""

from rules.curated import mod
NOTE = dict(when="note")

# Items that come with the body (services.grant_race_items).
RACES = {
    "abyssal": {"starting_items": [{"name": "Abyssal pressure suit", "slot": "armor"}]},
}

RACIAL_TRAITS = {
    # Abyssal
    "abyssal/massive-pressure-suit": {"modifiers": [
        mod("reach", 5, scope="melee", label="massive-2: reach 10 ft"),
        mod("note", 10, **NOTE, label="starting Brute counts as (move/lift/resist being moved, not poisons)")]},
    "abyssal/feeding-tendrils": {"modifiers": []},  # text only
    "abyssal/vital-armor": {"modifiers": []},        # soak 3 comes from the locked "Abyssal pressure suit" armor item
    "abyssal/collapsed-mantle": {"modifiers": [mod("soak", 1, label="Collapsed Mantle: suit soak 4")]},
    "abyssal/enhanced-graviton": {"modifiers": [mod("spd", 5), mod("swim", 5), mod("climb", 5)]},
    "abyssal/gravity-well": {"modifiers": [
        mod("spd", 5, op="base", when="toggle"), mod("swim", 5, op="base", when="toggle"),
        mod("climb", 5, op="base", when="toggle"),
        mod("note", 10, **NOTE, label="vs efforts to move you while Gravity Well is on")]},
    "abyssal/invasive-relay": {"modifiers": [mod("note", -5, **NOTE, label="Spirit to close your telepathic channel")]},
    # Anura
    "anura/momentous-mass": {"modifiers": [mod("roll:Brute", 2),
                                           mod("note", 5, **NOTE, label="resist being moved / move someone")]},
    "anura/bellowing-bravado": {"modifiers": [mod("note", 5, **NOTE, label="Deafening Roar, Lion's Roar effect roll")]},
    "anura/leap-frog": {"modifiers": [mod("note", 3, **NOTE, label="vs reflexive actions when leaping over an enemy")]},
    "anura/puffed-up": {"modifiers": [mod("note", 8, **NOTE, label="next intimidation after inflating (1 AP)")]},
    "anura/tree-dweller": {"modifiers": [mod("climb", 25, op="base", label="climb at land speed")]},
    # Crazak Transcendent
    "crazak-transcendent/ash-body": {"modifiers": [mod("eva", 1)]},
    "crazak-transcendent/claws": {"modifiers": [mod("dc", 3, op="base", scope="unarmed")]},
    "crazak-transcendent/endless-rage": {"modifiers": [mod("stk", 2)]},
    "crazak-transcendent/natural-frenzy": {"modifiers": [mod("acc", -2, when="toggle", label="frenzy"),
                                                         mod("stk", 3, when="toggle", label="frenzy")]},
    "crazak-transcendent/ogre-body": {"modifiers": [mod("roll:Brute", 4)]},
    "crazak-transcendent/resolve": {"modifiers": [mod("roll:Spirit", 4)]},
    "crazak-transcendent/sloughing-skin": {"modifiers": [mod("note", 5, **NOTE, label="evade / break grabs")]},
    "crazak-transcendent/third-eye": {"modifiers": [mod("acc", 1), mod("note", 2, **NOTE, label="notice rolls")]},
    "crazak-transcendent/additional-arm": {"extra_hands": {"slots": 1, "one_handed_only": False, "label": "Additional arm"}},
    # Daemon
    "daemon/bestial-strength": {"choice": "skill:Brute", "modifiers": [mod("skill:{choice}", 2)]},
    "daemon/inflammatory-appearance": {"modifiers": [mod("note", -3, **NOTE, label="pacify / command without force")]},
    "daemon/great-vitality": {"modifiers": [mod("hp", 6)]},
    "daemon/horrifying-combatant": {"modifiers": [mod("dc", 4, op="base", scope="unarmed")]},
    "daemon/infectious-fury": {"modifiers": [mod("note", 4, **NOTE, label="intimidation / provocation")]},
    "daemon/off-guard-adrenaline": {"modifiers": [mod("stk", 5, when="toggle", label="attacked outside regular combat")]},
    "daemon/passionate-blows": {"modifiers": [mod("stk", 2)]},
    "daemon/warriors-itch": {"modifiers": [mod("pri", 3)]},
    "daemon/built-in-bulwark": {"starting_items": [{"name": "Daemon wing-fins", "slot": "deflection"}]},
    # Ezka
    "ezka/unnatural-appendages": {"modifiers": [mod("note", 4, **NOTE, label="resist prone / being moved")]},
    "ezka/creepy-crawly": {"modifiers": [mod("note", 3, **NOTE, label="intimidation / provocation")]},
    "ezka/almost": {"negates": ["ezka/creepy-crawly"]},
    "ezka/burrower": {"modifiers": [mod("dig", 5)]},
    "ezka/dense-plates": {"modifiers": [mod("soak", 1, armor=["none"], label="natural plates"),
                                       mod("def", 4, armor=["light", "medium", "heavy", "super-heavy"],
                                           label="Dense Plates under armor")]},
    "ezka/faux-hands": {"extra_hands": {"slots": 2, "one_handed_only": True, "label": "Shetoras"}},
    "ezka/serrated-plating": {"modifiers": [mod("dc", 3, op="base", scope="unarmed", when="toggle",
                                                label="shetora attack, bypasses 1 soak")]},
    "ezka/poison-barbs": {"modifiers": [mod("note", 4, **NOTE, label="unsoakable barb damage (0 AP, recharge 1 AP)")]},
    "ezka/twisted-kinship": {"modifiers": [mod("note", 6, **NOTE, label="Cunning tells with mutated beings")]},
}
# Fluoform: same table for each subrace, so generate the keys.
for sub in ("fluoform-khemic", "fluoform-amorphide", "fluoform-homunculus"):
    RACIAL_TRAITS.update({
        f"{sub}/scorch-proof": {"modifiers": [mod("note", 3, **NOTE, label="resist burns / catching fire")]},
        f"{sub}/combustive-grasp": {"negates": [f"{sub}/scorch-proof"]},
        f"{sub}/alchemical-oddity": {"modifiers": [mod("note", 4, **NOTE, label="resist acids, poisons, gases")]},
        f"{sub}/fearsome-form": {"modifiers": [mod("dc", 4, op="base", scope="unarmed")]},
        f"{sub}/grounded": {"modifiers": [mod("note", 1, **NOTE, label="soak vs electrical damage (soakable)")]},
        f"{sub}/hydrophobic": {"modifiers": [mod("swim", 5, op="base", label="submerged max")]},
        f"{sub}/pure-strain": {"choice": "race", "reroll_on": "@choice", "speeds_from_choice": True},
        f"{sub}/rigid-design": {"modifiers": [mod("def", 4)]},
        f"{sub}/slick": {"modifiers": [mod("note", 2, **NOTE, label="evade grabs (+5 to break out)")]},
        f"{sub}/unsightly-undulations": {"modifiers": [mod("note", 4, **NOTE, label="intimidation / provocation")]},
    })
RACIAL_TRAITS.update({
    "fluoform-khemic/khemic": {"modifiers": [mod("roll:Cunning", 3, **NOTE, label="interacting with people")]},
    "fluoform-amorphide/amorphide": {"modifiers": [mod("essence_slots", 1), mod("eva", 1), mod("def", -2)]},
    "fluoform-amorphide/rigid-design": {"modifiers": [
        mod("eva", -1, label="Rigid Design cancels amorphide Evade"),
        mod("def", 2, label="Rigid Design cancels amorphide penalty"), mod("def", 4)]},
    "fluoform-homunculus/homunculus": {"choice": "alchemy_list", "modifiers": [mod("essence_slots", -1)]},
})
ONGOING_TRAITS = {
    "abyssal/gravity-well": {"start": 1, "upkeep": 0, "stop": 1},
}

# Part B
RACIAL_TRAITS.update({
# gleedrin
"gleedrin/born-engineer": {"modifiers": [mod("skill:Engineer", 2)]},
"gleedrin/efficiency-above-all": {"modifiers": [mod("diy", 1)]},
"gleedrin/branding-touch": {"modifiers": [mod("note", formula="1 + min(1, level // 4) + min(1, level // 8)", when="note",
                                              label="heat damage on touch")]},
"gleedrin/cavern-carver": {"modifiers": [mod("note", 15, when="note", label="dig speed (ft)")]},
"gleedrin/worthy-challenge": {"modifiers": []},                       # text only, like satyr/born-hero
# karshin
"karshin/predatory": {"modifiers": [mod("stk", 2)]},
"karshin/sharkskin-grip": {"modifiers": [mod("note", 3, when="note", label="to maintain grabs (also for grabbers)")]},
"karshin/blood-in-the-water": {"modifiers": [mod("roll:Cunning", 2, when="note", label="tracking by smell (+4 fresh blood)")]},
"karshin/glint-in-the-void": {"modifiers": [mod("roll:Cunning", 2, when="note", label="intimidate/provoke"),
                                            mod("roll:Cunning", -2, when="note", label="pacify")]},
"karshin/dead-rock": {"modifiers": [mod("soak", 2),
                                    mod("eva", -4, when="toggle", label="metal or heavier-than-medium armor")]},
"karshin/deep-scale-slimer": {"negates": ["karshin/sharkskin-grip"],
                              "modifiers": [mod("note", 3, when="note", label="to evade/break grabs")]},
"karshin/feeding-frenzy": {"modifiers": [mod("note", 2, when="note", label="Strike per melee kill this combat (use Misc)")]},
"karshin/fhtagn": {"modifiers": [mod("swim", 15, op="base"), mod("climb", 25, op="base")]},
"karshin/killing-claw": {"modifiers": [mod("dc", 4, op="base", scope="unarmed", when="toggle", label="claw hand")]},
"karshin/partially-boneless": {"modifiers": [mod("eva", 1)]},
# manticore (unarmed_dc 4 is the race base, no modifier)
"manticore/bestial-form": {"modifiers": [mod("roll:Brute", 2)]},
"manticore/stigma-of-fear": {"modifiers": [mod("roll:Cunning", -4, when="note", label="pacify/positively influence"),
                                           mod("roll:Cunning", 2, when="note", label="intimidate when revealed")]},
"manticore/progressive-madness": {"modifiers": [mod("note", formula="level", when="note", label="penalty to resists vs provocation"),
                                                mod("stk", 2, when="toggle", label="provoked (vs provoker)"),
                                                mod("eva", -1, when="toggle", label="provoked")]},
"manticore/restrained-rage": {"negates": ["manticore/progressive-madness:note"],
                              "modifiers": [mod("note", formula="level // 2", when="note", label="penalty to resists vs provocation (halved)")]},
"manticore/dedicated-to-the-cure": {"modifiers": [mod("skill:Alchemy", 2)], "grants_augments": ["alchemy-rage-suppressant"]},
"manticore/feral-roar": {"modifiers": [mod("stk", formula="ap_total", when="toggle", label="Feral Roar (allies too; enemies −same)")]},
"manticore/furious-backlash": {"modifiers": [mod(s, 5, when="toggle", label="at 0 HP until half HP")
                                             for s in ("stk", "spd", "swim", "climb", "fly")]},
"manticore/hooked-tail": {"modifiers": [mod("note", 4, when="note", label="to sustain tail grabs")]},
"manticore/pack-mentality": {"modifiers": [mod("stk", 2, when="toggle", label="adjacent manticore ally (or +2 Defense)")]},
"manticore/savage-strength": {"modifiers": [mod("roll:Brute", 3), mod("roll:Dexterity", -2)]},
"manticore/takedown": {"modifiers": [mod("dc", 1, scope="melee", when="toggle", label="target wounded or under a fatal effect")]},
# obezyany
"obezyany/multi-dextrous": {"modifiers": [mod("roll:Dexterity", 4)]},
"obezyany/frail-body": {"modifiers": [mod("roll:Brute", -4)]},
"obezyany/clever-monkey": {"modifiers": [mod("roll:Cunning", 3)]},
"obezyany/gorilla-build": {"negates": ["obezyany/frail-body", "obezyany/multi-dextrous:roll:Dexterity"],
                           "modifiers": [mod("roll:Brute", 4), mod("roll:Dexterity", -4)]},
"obezyany/hard-back": {"modifiers": [mod("soak", 1)]},
"obezyany/monkeys-are-bastards": {"modifiers": [mod("eva", 2, when="note", label="vs melee attacks and grabs")]},
"obezyany/numerous-spots": {"modifiers": [mod("def", 4)]},
"obezyany/shaman-in-training": {"modifiers": [mod("skill:Shamanism", 2)]},
"obezyany/firebreather": {"modifiers": [mod("note", 4, when="note", label="Flame Breath DC (2 AP, 10 ft, Strike)")]},
# simulacron
"simulacron/gnome-sized": {"modifiers": [mod("eva", 1, label="Small Stature"), mod("roll:Brute", -2, label="Light Build"),
                                         mod("spd", 15, op="base"), mod("dc", 1, op="base", scope="unarmed", label="Smaller Weapons")]},
"simulacron/buoyant": {"negates": ["simulacron/cannot-swim"], "modifiers": [mod("swim", 20, op="base")]},
"simulacron/bio-mechanical-components": {"negates": ["simulacron/bio-flux-immunity"]},
"simulacron/electrical-shielding": {"negates": ["simulacron/metal-body"]},
"simulacron/exoskeleton": {"modifiers": [mod("def", 4)]},
"simulacron/mechanical-knowledge": {"modifiers": [mod("aug", 2)], "augments_any_crafting_skill": True},
})
# Narrator decision: Progressive Madness is an "Other" toggle named "Being provoked".
RACIAL_TRAITS["manticore/progressive-madness"]["toggle_label"] = "Being provoked"
