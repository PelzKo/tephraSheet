"""Status effects (p.22-23) and the called-shot chart (p.16-17) as data.

Every effect has a key (stored in ``EffectEntry.key``), a display name, the rule text and the
modifiers it applies while active (same schema as ``curated.py``; ``op: set`` forces a value).
Conditional parts ("vs the source", "rolls with that arm") stay in the text only.
``halve_hp`` halves max HP, ``lost_wounds`` lowers max wounds permanently, ``breather`` means the
effect ends with a breather, ``drop`` makes the hit hand drop what it holds.
"""


def _mods(stats):
    return [{"stat": s, "value": v, "op": "add", "when": "always", "scope": "character"} for s, v in stats.items()]


def _all_rolls(n):
    return _mods({s: n for s in ("acc", "eva", "stk", "def", "pri")})


STATUS = [
    {"slug": "bleeding", "name": "Bleeding",
     "text": "HP damage (then wounds) each AP refresh, unsoakable, stacks; each 1 AP spent (victim/adjacent) negates 5."},
    {"slug": "blinded", "name": "Blinded", "text": "−4 Accuracy and Evade (poor vision, fog, low light: −2).",
     "modifiers": _mods({"acc": -4, "eva": -4})},
    {"slug": "burning-1", "name": "Burning T1", "text": "2 unsoakable damage per turn; 2 AP to extinguish; items singed."},
    {"slug": "burning-2", "name": "Burning T2",
     "text": "4 unsoakable damage per turn; 4 AP to extinguish; wood/organic/cloth items destroyed."},
    {"slug": "burning-3", "name": "Burning T3",
     "text": "8 unsoakable damage per turn; 8 AP to extinguish; leather, cloth and wood destroyed."},
    {"slug": "burning-4", "name": "Burning T4",
     "text": "16 unsoakable damage per turn; 16 AP to extinguish; even metal becomes unusable."},
    {"slug": "burnt-1", "name": "Burnt T1", "text": "−1 to all Defense rolls.", "modifiers": _mods({"def": -1})},
    {"slug": "burnt-2", "name": "Burnt T2", "text": "−3 to all Defense rolls.", "modifiers": _mods({"def": -3})},
    {"slug": "burnt-3", "name": "Burnt T3", "text": "−5 to all Defense rolls.", "modifiers": _mods({"def": -5})},
    {"slug": "burnt-4", "name": "Burnt T4", "text": "−7 to all Defense rolls.", "modifiers": _mods({"def": -7})},
    {"slug": "deafened", "name": "Deafened", "text": "−2 Evade; −2 on sound-based rolls.", "modifiers": _mods({"eva": -2})},
    {"slug": "disoriented", "name": "Disoriented", "text": "−1 AP per turn; spend 3 AP to re-orient.",
     "modifiers": _mods({"ap": -1})},
    {"slug": "drowning", "name": "Drowning",
     "text": "Brute roll each turn, target tier starts at T2 and rises; fail → unconscious; die 3 turns later."},
    {"slug": "enraged", "name": "Enraged",
     "text": "−2 on all rolls except attacking the rage source; +2 Accuracy and Strike vs the source; 2 AP to calm."},
    {"slug": "fatigued", "name": "Fatigued", "text": "Max HP halved (round down).", "halve_hp": True},
    {"slug": "fear-1", "name": "Scared (Fear T1)", "text": "−2 on all resist rolls (−4 vs the source)."},
    {"slug": "fear-2", "name": "Frightened (Fear T2)", "text": "−2 on all rolls (−4 vs the source).",
     "modifiers": _all_rolls(-2)},
    {"slug": "fear-3", "name": "Terrified (Fear T3)",
     "text": "−2 on all rolls (−4 vs the source); ≥1 AP per turn moving away; can't approach.",
     "modifiers": _all_rolls(-2)},
    {"slug": "fear-4", "name": "True dread (Fear T4)",
     "text": "−4 on all rolls (−6 vs the source); can only try to overcome it (1 AP per re-roll).",
     "modifiers": _all_rolls(-4)},
    {"slug": "nausea", "name": "Nausea", "text": "−2 on all rolls until 3 AP are spent.",
     "modifiers": _all_rolls(-2)},
    {"slug": "paralyzed", "name": "Paralyzed", "text": "Helpless; damage goes straight to wounds; no actions."},
    {"slug": "prone", "name": "Prone",
     "text": "−1 Accuracy/Evade/Strike/Defense; speed 5 ft; standing up costs 1 AP (draws reflexes).",
     "modifiers": _mods({"acc": -1, "eva": -1, "stk": -1, "def": -1}) + [
         {"stat": "spd", "value": 5, "op": "set", "when": "always", "scope": "character"}]},
    {"slug": "stunned", "name": "Stunned", "text": "Lose X AP from the current pool; can still evade and resist."},
]

# d12 location numbers on the silhouette -> chart location slug.
LOCATION_NUMBERS = {1: "head", 2: "eyes", 3: "ears", 4: "neck", 5: "torso", 6: "groin",
                    7: "arm", 8: "arm", 9: "hand", 10: "hand", 11: "leg", 12: "leg"}
LOCATION_LABELS = {1: "Head", 2: "Eyes", 3: "Ears", 4: "Neck", 5: "Torso", 6: "Groin",
                   7: "Left arm", 8: "Right arm", 9: "Left hand", 10: "Right hand", 11: "Left leg", 12: "Right leg"}

CALLED_SHOTS = {
    "head": {"name": "Head", "resist": "Brute",
             "normal": {"name": "Disoriented", "text": "−1 AP per turn until the end of your next turn.",
                       "modifiers": _mods({"ap": -1})},
             "wound": {"name": "Disoriented", "text": "Disoriented 1 turn per 3 damage; can't re-orient.",
                       "modifiers": _mods({"ap": -1})},
             "fatal": {"name": "Beheaded", "text": "Instant death."}},
    "eyes": {"name": "Eyes", "resist": "Dexterity",
             "normal": {"name": "Eyes hit", "text": "−2 Accuracy and Evade until the end of your next turn.",
                       "modifiers": _mods({"acc": -2, "eva": -2})},
             "wound": {"name": "Blinded", "text": "Blinded until breather: −4 Accuracy/Evade.",
                       "modifiers": _mods({"acc": -4, "eva": -4}), "breather": True},
             "fatal": {"name": "Permanently blind", "text": "−4 Accuracy/Evade, −1 max wounds.",
                       "modifiers": _mods({"acc": -4, "eva": -4}), "lost_wounds": 1}},
    "ears": {"name": "Ears", "resist": "Cunning",
             "normal": {"name": "Ears hit", "text": "−2 Evade until the end of your next turn.",
                       "modifiers": _mods({"eva": -2})},
             "wound": {"name": "Deafened", "text": "Deafened until breather: −2 Evade and sound rolls.",
                       "modifiers": _mods({"eva": -2}), "breather": True},
             "fatal": {"name": "Permanently deaf", "text": "−2 Evade, −1 max wounds.",
                       "modifiers": _mods({"eva": -2}), "lost_wounds": 1}},
    "neck": {"name": "Neck", "resist": "Brute",
             "normal": {"name": "Stunned", "text": "Lose 1 AP."},
             "wound": {"name": "Bleeding", "text": "1 wound per turn, 1 turn per 3 damage."},
             "fatal": {"name": "Slit throat", "text": "Die at the end of your next turn."}},
    "torso": {"name": "Torso", "resist": "Brute",
              "normal": {"name": "Knocked back", "text": "Knocked back 5 ft (the attacker may follow for 0 AP)."},
              "wound": {"name": "Broken ribs", "text": "Every action needs Brute T2 or lose 1 AP; until breather.",
                        "breather": True},
              "fatal": {"name": "Slain", "text": "Dead."}},
    "groin": {"name": "Groin", "resist": "Spirit",
              "normal": {"name": "Nausea", "text": "−2 on all rolls until 3 AP are spent.",
                        "modifiers": _all_rolls(-2)},
              "wound": {"name": "Purge", "text": "Only move at half speed for 3 turns, −4 Evade.",
                        "modifiers": _mods({"eva": -4})},
              "fatal": {"name": "Gutted", "text": "Recover 10 damage before the end of your next turn or die."}},
    "arm": {"name": "Arm", "resist": "Brute",
            "normal": {"name": "Arm hit", "text": "−2 on rolls with that arm until the end of your next turn."},
            "wound": {"name": "Sprained arm", "text": "−6 on rolls with that arm until breather.", "breather": True},
            "fatal": {"name": "Severed arm",
                      "text": "−2 max wounds; two-arm tasks impossible/−6; die in 3 turns unless 3 AP bandaging.",
                      "lost_wounds": 2}},
    "hand": {"name": "Hand", "resist": "Dexterity",
             "normal": {"name": "Dropped item",
                       "text": "Drop the held item (1 AP to pick it up again).", "drop": True},
             "wound": {"name": "Bruised hand", "text": "Can't wield anything with it until breather.",
                       "breather": True},
             "fatal": {"name": "Severed hand", "text": "−1 max wounds; die in 6 turns unless 3 AP bandaging.",
                       "lost_wounds": 1}},
    "leg": {"name": "Leg", "resist": "Dexterity",
            "normal": {"name": "Slowed or tripped",
                      "text": "Attacker's choice: slowed (+1 AP to move) or tripped (prone)."},
            "wound": {"name": "Sprained leg", "text": "−10 Speed (min 5), prone; until breather.",
                      "modifiers": _mods({"spd": -10}), "breather": True},
            "fatal": {"name": "Severed leg",
                      "text": "−20 Speed (min 5), two-leg tasks −6, −1 max wounds; die in 3 turns unless 3 AP bandaging.",
                      "modifiers": _mods({"spd": -20}), "lost_wounds": 1}},
}


CALLED_KINDS = ("normal", "wound", "fatal")  # display order: Normal, Wounded, Fatal
CALLED_LABELS = {"normal": "Normal", "wound": "Wounded", "fatal": "Fatal"}


def _build_index():
    index = {}
    for s in STATUS:
        index[f"status:{s['slug']}"] = dict(s, kind="status")
    for loc, data in CALLED_SHOTS.items():
        for kind in CALLED_KINDS:
            index[f"{kind}:{loc}"] = dict(data[kind], kind=kind, location=data["name"])
    return index


EFFECTS = _build_index()


def get(key):
    return EFFECTS.get(key or "")


def called_key(number, kind):
    """Effect key for a silhouette location number (1-12) and ``normal``/``wound``/``fatal``."""
    loc = LOCATION_NUMBERS.get(number)
    return f"{kind}:{loc}" if loc and kind in CALLED_KINDS else ""
