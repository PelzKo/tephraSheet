"""Status effects (p.22-23) and the called-shot chart (p.16-17) as data.

Every effect has a key (stored in ``EffectEntry.key``), a display name, the rule text and the
modifiers it applies while active (same schema as ``curated.py``; ``op: set`` forces a value).
Conditional parts ("vs the source", "rolls with that arm") stay in the text only.
``halve_hp`` halves max HP, ``lost_wounds`` lowers max wounds permanently, ``breather`` means the
effect ends with a breather, ``drop`` makes the hit hand drop what it holds.

Amounts (``EffectEntry.amount``) and AP payments, all rule numbers live here:
``ask`` = the add form asks a number (label); ``add`` = what adding the same effect again does ("stack": +amount,
"renew": higher of both; otherwise a second entry); ``tick`` = damage in fight mode at ``at`` ("end_turn" = AP
refresh, "turn" = start of my turn): ``damage`` (fixed; default the amount) to ``to`` ("hp_wounds", "hp" or
"wounds"), ``decay`` lowers the amount each tick (removed at 0); ``per_ap`` = each AP paid lowers the amount by
that much (removed at 0); ``cost`` = AP that end it (a number, or "amount" = the asked number); ``bandage`` = AP
that stop the death timer (the effect stays); ``stun`` = the asked number of AP is lost from the round's pool;
``refresh_ends`` = removed at the next AP refresh; ``start`` = the amount of an effect that asks nothing; ``max`` caps the asked number.
"""
import re
from functools import cache


def _mods(stats):
    return [{"stat": s, "value": v, "op": "add", "when": "always", "scope": "character"} for s, v in stats.items()]


def _all_rolls(n):
    return _mods({s: n for s in ("acc", "eva", "stk", "def", "pri")})


def _burning(n):
    # The AP to extinguish may be spent over several turns (T3/T4 need more than one turn's pool): the amount is
    # the AP still needed.
    return {"tick": {"at": "end_turn", "damage": n, "to": "hp_wounds"}, "start": n, "per_ap": 1}


STATUS = [
    {"slug": "bleeding", "name": "Bleeding",
     "text": "HP damage (then wounds) each AP refresh, unsoakable, stacks; each 1 AP spent (victim/adjacent) negates 5.",
     "ask": "Bleeding damage", "add": "stack", "tick": {"at": "end_turn", "to": "hp_wounds"}, "per_ap": 5},
    {"slug": "blinded", "name": "Blinded", "text": "−4 Accuracy and Evade (poor vision, fog, low light: −2).",
     "modifiers": _mods({"acc": -4, "eva": -4})},
    {"slug": "burning-1", "name": "Burning T1", "text": "2 unsoakable damage per turn; 2 AP to extinguish; items singed.",
     **_burning(2)},
    {"slug": "burning-2", "name": "Burning T2",
     "text": "4 unsoakable damage per turn; 4 AP to extinguish; wood/organic/cloth items destroyed.", **_burning(4)},
    {"slug": "burning-3", "name": "Burning T3",
     "text": "8 unsoakable damage per turn; 8 AP to extinguish; leather, cloth and wood destroyed.", **_burning(8)},
    {"slug": "burning-4", "name": "Burning T4",
     "text": "16 unsoakable damage per turn; 16 AP to extinguish; even metal becomes unusable.", **_burning(16)},
    {"slug": "burnt-1", "name": "Burnt T1", "text": "−1 to all Defense rolls.", "modifiers": _mods({"def": -1})},
    {"slug": "burnt-2", "name": "Burnt T2", "text": "−3 to all Defense rolls.", "modifiers": _mods({"def": -3})},
    {"slug": "burnt-3", "name": "Burnt T3", "text": "−5 to all Defense rolls.", "modifiers": _mods({"def": -5})},
    {"slug": "burnt-4", "name": "Burnt T4", "text": "−7 to all Defense rolls.", "modifiers": _mods({"def": -7})},
    {"slug": "deafened", "name": "Deafened", "text": "−2 Evade; −2 on sound-based rolls.", "modifiers": _mods({"eva": -2})},
    {"slug": "disoriented", "name": "Disoriented", "text": "−1 AP per turn; spend 3 AP to re-orient.", "cost": 3,
     "modifiers": _mods({"ap": -1})},
    {"slug": "drowning", "name": "Drowning",
     "text": "Brute roll each turn, target tier starts at T2 and rises; fail → unconscious; die 3 turns later."},
    {"slug": "enraged", "name": "Enraged",
     "text": "−2 on all rolls except attacking the rage source; +2 Accuracy and Strike vs the source; 2 AP to calm.", "cost": 2},
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
    {"slug": "nausea", "name": "Nausea", "text": "−2 on all rolls until 3 AP are spent.", "cost": 3,
     "modifiers": _all_rolls(-2)},
    {"slug": "paralyzed", "name": "Paralyzed", "text": "Helpless; damage goes straight to wounds; no actions."},
    {"slug": "prone", "name": "Prone",
     "text": "−1 Accuracy/Evade/Strike/Defense; speed 5 ft; standing up costs 1 AP (draws reflexes).", "cost": 1,
     "modifiers": _mods({"acc": -1, "eva": -1, "stk": -1, "def": -1}) + [
         {"stat": "spd", "value": 5, "op": "set", "when": "always", "scope": "character"}]},
    {"slug": "stunned", "name": "Stunned", "text": "Lose X AP from the current pool; can still evade and resist.", "ask": "AP lost",
     "stun": True, "refresh_ends": True},
    {"slug": "wet", "name": "Wet", "extension": "living-liquids",
     "text": "Electric damage against you is doubled (Electric Current: unsoakable)."},
    # Aether extension
    {"slug": "irradiated", "name": "Irradiated", "extension": "aether",
     "text": "−2 on all rolls until 1–4 AP (by the augment's marque) are spent.", "ask": "AP to settle", "max": 4,
     "cost": "amount", "modifiers": _all_rolls(-2)},
    *[{"slug": f"highly-irradiated-{t}", "name": f"Highly Irradiated T{t}", "extension": "aether",
       "text": f"−{t + 2} on all rolls until the AP of Irradiated are spent.", "ask": "AP to settle", "max": 4,
       "cost": "amount", "modifiers": _all_rolls(-(t + 2))}
      for t in (1, 2, 3, 4)],
    {"slug": "radiation-burns", "name": "Radiation Burns", "extension": "aether",
     "text": "Unsoakable HP damage at the start of the next turn, 1 less each turn after; renewed by a new hit.", "ask": "Damage", "add": "renew",
     "tick": {"at": "turn", "to": "hp", "decay": 1}},
    {"slug": "static-shock", "name": "Static Shock", "extension": "aether",
     "text": "−2/−4/−6/−8 (by marque) on the next Evade roll within the next turn."},
]

# d12 location numbers on the silhouette -> chart location slug.
LOCATION_NUMBERS = {1: "head", 2: "eyes", 3: "ears", 4: "neck", 5: "torso", 6: "groin",
                    7: "arm", 8: "arm", 9: "hand", 10: "hand", 11: "leg", 12: "leg"}
LOCATION_LABELS = {1: "Head", 2: "Eyes", 3: "Ears", 4: "Neck", 5: "Torso", 6: "Groin",
                   7: "Left arm", 8: "Right arm", 9: "Left hand", 10: "Right hand", 11: "Left leg", 12: "Right leg"}

CALLED_SHOTS = {
    "head": {"name": "Head", "resist": "Brute",
             "normal": {"name": "Disoriented", "text": "−1 AP per turn until the end of your next turn.", "cost": 3,
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
             "wound": {"name": "Bleeding", "text": "1 wound per turn, 1 turn per 3 damage.", "ask": "Turns (1 per 3 damage)",
                       "tick": {"at": "end_turn", "damage": 1, "to": "wounds", "decay": 1}},
             "fatal": {"name": "Slit throat", "text": "Die at the end of your next turn."}},
    "torso": {"name": "Torso", "resist": "Brute",
              "normal": {"name": "Knocked back", "text": "Knocked back 5 ft (the attacker may follow for 0 AP)."},
              "wound": {"name": "Broken ribs", "text": "Every action needs Brute T2 or lose 1 AP; until breather.",
                        "breather": True},
              "fatal": {"name": "Slain", "text": "Dead."}},
    "groin": {"name": "Groin", "resist": "Spirit",
              "normal": {"name": "Nausea", "text": "−2 on all rolls until 3 AP are spent.", "cost": 3,
                        "modifiers": _all_rolls(-2)},
              "wound": {"name": "Purge", "text": "Only move at half speed for 3 turns, −4 Evade.",
                        "modifiers": _mods({"eva": -4})},
              "fatal": {"name": "Gutted", "text": "Recover 10 damage before the end of your next turn or die."}},
    "arm": {"name": "Arm", "resist": "Brute",
            "normal": {"name": "Arm hit", "text": "−2 on rolls with that arm until the end of your next turn."},
            "wound": {"name": "Sprained arm", "text": "−6 on rolls with that arm until breather.", "breather": True},
            "fatal": {"name": "Severed arm",
                      "text": "−2 max wounds; two-arm tasks impossible/−6; die in 3 turns unless 3 AP bandaging.",
                      "lost_wounds": 2, "bandage": 3}},
    "hand": {"name": "Hand", "resist": "Dexterity",
             "normal": {"name": "Dropped item",
                       "text": "Drop the held item (1 AP to pick it up again).", "drop": True},
             "wound": {"name": "Bruised hand", "text": "Can't wield anything with it until breather.",
                       "breather": True},
             "fatal": {"name": "Severed hand", "text": "−1 max wounds; die in 6 turns unless 3 AP bandaging.",
                       "lost_wounds": 1, "bandage": 3}},
    "leg": {"name": "Leg", "resist": "Dexterity",
            "normal": {"name": "Slowed or tripped",
                      "text": "Attacker's choice: slowed (+1 AP to move) or tripped (prone)."},
            "wound": {"name": "Sprained leg", "text": "−10 Speed (min 5), prone; until breather.",
                      "modifiers": _mods({"spd": -10}), "breather": True},
            "fatal": {"name": "Severed leg",
                      "text": "−20 Speed (min 5), two-leg tasks −6, −1 max wounds; die in 3 turns unless 3 AP bandaging.",
                      "modifiers": _mods({"spd": -20}), "lost_wounds": 1, "bandage": 3}},
}


CALLED_KINDS = ("normal", "wound", "fatal")  # display order: Normal, Wounded, Fatal
CALLED_LABELS = {"normal": "Normal", "wound": "Wounded", "fatal": "Fatal"}


def _tiers(slug):
    return [f"{slug}-{t}" for t in (1, 2, 3, 4)]


# Words in rule texts that get an explainer tip (``term_matches``, template filter ``term_tips``). ``status``: the
# status effects it explains (a tier in the match picks one: "Fear T2"); otherwise ``name``/``text`` explain a general
# rule (reference 1.2/1.3/1.6). Patterns are case-insensitive, whole words; other languages replace pattern/name/text
# in rules/data/i18n/<lang>/effects.json "TERMS".
TERMS = {
    "bleeding": {"pattern": r"bleed(?:ing|s)?", "status": ["bleeding"]},
    "blinded": {"pattern": r"blind(?:ed|ness)?", "status": ["blinded"]},
    "burning": {"pattern": r"burning(?: T[1-4])?", "status": _tiers("burning")},
    "burnt": {"pattern": r"burnt(?: T[1-4])?", "status": _tiers("burnt")},
    "deafened": {"pattern": r"deaf(?:ened)?", "status": ["deafened"]},
    "disoriented": {"pattern": r"disorient(?:ed)?", "status": ["disoriented"]},
    "drowning": {"pattern": r"drown(?:ing|s)?", "status": ["drowning"]},
    "enraged": {"pattern": r"enraged", "status": ["enraged"]},
    "fatigued": {"pattern": r"fatigued?", "status": ["fatigued"]},
    "fear": {"pattern": r"fear(?: T[1-4])?", "status": _tiers("fear")},
    "nausea": {"pattern": r"nause(?:a|ated|ous)", "status": ["nausea"]},
    "paralyzed": {"pattern": r"paraly(?:zed|sed|sis)", "status": ["paralyzed"]},
    "prone": {"pattern": r"prone", "status": ["prone"]},
    "stunned": {"pattern": r"stun(?:ned|s)?", "status": ["stunned"]},
    "wet": {"pattern": r"wet", "status": ["wet"]},
    "tier": {"pattern": r"T[1-4]|tier [1-4]", "name": "Tier",
             "text": "Roll result 1–9 = T1, 10–19 = T2, 20–29 = T3, 30+ = T4. "
                     "Damage = Damage Class × tier, soak = Soak Class × Defense tier."},
    "unsoakable": {"pattern": r"unsoakable", "name": "Unsoakable",
                   "text": "The damage ignores soak: no Defense roll reduces it."},
    "resist": {"pattern": r"resist(?:s|ed|ing|ance)?", "name": "Resist",
               "text": "A roll of the named attribute. Each tier above T1 lowers the incoming effect by 1 tier "
                       "(T2 −1, T3 −2, T4 −3)."},
}


@cache
def _term_regex(lang):
    tr = _translations().get("TERMS", {})
    alts = "|".join(f"(?P<{key}>{tr.get(key, {}).get('pattern', t['pattern'])})" for key, t in TERMS.items())
    return re.compile(rf"\b(?:{alts})\b", re.I)


def term_tip(key, matched):
    """Tip text for a matched term: the status effect(s) or the general rule, in the current language."""
    term = TERMS[key]
    if "status" in term:
        slugs = term["status"]
        tier = re.search(r"[1-4]", matched)
        if tier and len(slugs) == 4:
            slugs = [slugs[int(tier.group()) - 1]]
        return "\n".join(f"{e['name']}: {e['text']}" for e in (get(f"status:{s}") for s in slugs))
    tr = _translations().get("TERMS", {}).get(key, {})
    return f"{tr.get('name', term['name'])}: {tr.get('text', term['text'])}"


def term_matches(text):
    """(start, end, tip) for every explained term in plain ``text``."""
    from rules.lang import get_language

    for m in _term_regex(get_language()).finditer(text):
        yield m.start(), m.end(), term_tip(m.lastgroup, m.group())


def _build_index():
    index = {}
    for s in STATUS:
        index[f"status:{s['slug']}"] = dict(s, kind="status")
    for loc, data in CALLED_SHOTS.items():
        for kind in CALLED_KINDS:
            index[f"{kind}:{loc}"] = dict(data[kind], kind=kind, location=data["name"])
    return index


EFFECTS = _build_index()


def _translations():
    from rules.lang import DEFAULT, get_language
    from rules.registry import translations

    lang = get_language()
    return translations(lang, "effects") if lang != DEFAULT else {}


def get(key):
    """The effect with its name/text in the current language (see rules/data/i18n/<lang>/effects.json)."""
    e = EFFECTS.get(key or "")
    if not e:
        return e
    tr = _translations()
    if not tr:
        return e
    kind, _, slug = key.partition(":")
    t = tr.get("STATUS", {}).get(slug) if kind == "status" else tr.get("CALLED_SHOTS", {}).get(slug, {}).get(kind)
    loc = tr.get("CALLED_SHOTS", {}).get(slug, {}).get("name") if kind != "status" else None
    return dict(e, **{k: v for k, v in (t or {}).items() if k in ("name", "text")}, **({"location": loc} if loc else {}))


def location_label(number):
    return _translations().get("LOCATION_LABELS", {}).get(str(number)) or LOCATION_LABELS.get(number, "")


def location_labels():
    return {n: location_label(n) for n in LOCATION_LABELS}


def called_label(kind):
    return _translations().get("CALLED_LABELS", {}).get(kind) or CALLED_LABELS[kind]


def status_list():
    """Status effects offered in the effect picker (extension ones only while switched on)."""
    from rules.extensions import offer

    return [get(f"status:{s['slug']}") | {"slug": s["slug"]} for s in offer(STATUS)]


def called_key(number, kind):
    """Effect key for a silhouette location number (1-12) and ``normal``/``wound``/``fatal``."""
    loc = LOCATION_NUMBERS.get(number)
    return f"{kind}:{loc}" if loc and kind in CALLED_KINDS else ""
