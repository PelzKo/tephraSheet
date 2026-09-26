"""Compute every sheet value from a CharacterState (reference §2.4 formulas)."""

from dataclasses import dataclass, field

from rules.registry import get_registry

from . import effects, tables
from .formula import var_name
from .modifiers import Source, Value, is_active, mod_amount
from .state import CharacterState

CHARACTER_STATS = ["acc", "eva", "stk", "def", "pri", "spd", "swim", "climb", "fly",
                   "aug", "diy", "wnd", "hp", "soak", "ap", "essence_slots"]
MISC_LABEL = "Manual Misc Change"


@dataclass
class Sheet:
    state: CharacterState
    race: dict
    skills: dict = field(default_factory=dict)  # skill -> Value
    attributes: dict = field(default_factory=dict)  # attribute -> Value
    stats: dict = field(default_factory=dict)  # stat -> Value
    attr_misc: dict = field(default_factory=dict)  # attribute -> Value (racial roll bonuses + manual misc)
    roll_notes: dict = field(default_factory=dict)  # attribute -> [(label, amount)] conditional roll bonuses
    notes: list = field(default_factory=list)  # [(source label, text)]
    specialty_rows: list = field(default_factory=list)
    specialty_totals: dict = field(default_factory=dict)
    specialty_misc: dict = field(default_factory=dict)
    specialty_total_values: dict = field(default_factory=dict)  # column -> Value (for the Totals row)
    sources: list = field(default_factory=list)
    toggles: list = field(default_factory=list)  # [{key, label, active, effects}]
    stances: list = field(default_factory=list)  # [{slug, label, active}]
    weapons: list = field(default_factory=list)  # WeaponBlock
    unarmed: object = None
    armor: dict | None = None
    deflection: dict | None = None
    traits: list = field(default_factory=list)
    variables: dict = field(default_factory=dict)
    armor_degree: int = 0
    scoped: list = field(default_factory=list)  # [(source, mod)] with a weapon scope
    ap_ready_mods: list = field(default_factory=list)
    hands: dict = field(default_factory=dict)  # weapons.hand_layout + left_block/right_block

    def __getitem__(self, key):
        return self.stats[key]

    @property
    def max_hp(self):
        return self.stats["hp"].total

    @property
    def max_wounds(self):
        return self.stats["wnd"].total


def active_trait_keys(state):
    """Fixed + random trait keys actually in effect (negations applied)."""
    reg = get_registry()
    race = reg.races[state.race]
    if race.get("fixed_choose"):
        fixed = [k for k in state.fixed_traits if k in reg.traits]
    else:
        fixed = [f"{race['slug']}/{t['slug']}" for t in race["fixed"]]
    keys = fixed + [k for k in state.random_traits if k in reg.traits]
    negated = set()
    for k in keys:
        negated.update(reg.traits[k].get("negates", []))
    return [k for k in keys if k not in negated], negated


def collect_sources(state):
    reg = get_registry()
    sources = []
    trait_keys, negated = active_trait_keys(state)
    for key in trait_keys:
        t = reg.traits[key]
        mods = t.get("modifiers", [])
        if key == "farishtaa/botched-surgery" and "farishtaa/botched-surgery:weak-souls" in negated:
            mods = [m for m in mods if not m["stat"].startswith("roll:Spirit")]
        sources.append(Source(f"trait:{key}", f"Racial trait: {t['name']}", mods, kind="trait"))
    for slug, _level in state.specialties:
        s = reg.specialties.get(slug)
        if not s:
            continue
        sources.append(Source(f"spec:{slug}", f"Specialty: {s['name']}", s.get("modifiers", []),
                              kind="specialty", stance_slug=slug if s.get("stance") else ""))
    for slug in state.stories:
        s = reg.stories.get(slug)
        if s:
            sources.append(Source(f"story:{slug}", f"Story: {s['name']}", s.get("modifiers", []), kind="story"))
    for n, cm in enumerate(state.custom_modifiers):
        label = cm.get("source") or "Custom"
        sources.append(Source(cm.get("key") or f"custom:{n}", label, [cm], kind="custom"))
    for key in state.effects:
        e = effects.get(key)
        if e and e.get("modifiers"):
            sources.append(Source(f"effect:{key}", f"Effect: {e['name']}", e["modifiers"], kind="effect"))
    for slug, marque in state.body_augments:
        a = reg.augments.get(slug)
        if a:
            sources.append(Source(f"body:{slug}", f"Augment: {a['name']} mQ {roman(marque)}",
                                  [dict(m, marque=marque) for m in a.get("modifiers", [])], kind="augment"))
    for item in state.items:
        if item.slot in ("carried", "stored", ""):
            continue
        key = f"item:{item.id or item.name}"
        if item.modifiers:
            sources.append(Source(key, f"Item: {item.name}", item.modifiers, kind="item", item_id=item.id))
        for slug, marque in item.augments:
            a = reg.augments.get(slug)
            if a:
                sources.append(Source(f"{key}:aug:{slug}", f"{item.name}: {a['name']} mQ {roman(marque)}",
                                      [dict(m, marque=marque) for m in a.get("modifiers", [])],
                                      kind="item-augment", item_id=item.id))
    return sources


def roman(n):
    return {1: "I", 2: "II", 3: "III", 4: "IV"}.get(n, str(n))


def compute(state: CharacterState) -> Sheet:
    reg = get_registry()
    race = reg.races[state.race]
    sheet = Sheet(state=state, race=race)
    sources = collect_sources(state)
    sheet.sources = sources

    # --- skills & attributes -------------------------------------------------
    for skill in tables.ALL_SKILLS:
        v = Value()
        v.add("Skill points", state.skills.get(skill, 0))
        sheet.skills[skill] = v
    for src in sources:
        for m in src.modifiers:
            if m["stat"].startswith("skill:") and is_active(m, src, state):
                skill = m["stat"].split(":", 1)[1]
                if skill in sheet.skills:
                    sheet.skills[skill].add(src.label, mod_amount(m, {}, m.get("marque")))
    for key, amount in state.misc.items():
        if key.startswith("skill:") and key[6:] in sheet.skills:
            sheet.skills[key[6:]].add(MISC_LABEL, amount)
    for attr, skills in tables.SKILLS.items():
        v = Value()
        for skill in skills:
            v.add(skill, sheet.skills[skill].total)
        sheet.attributes[attr] = v
        sheet.attr_misc[attr] = Value()
        sheet.roll_notes[attr] = []

    variables = {var_name(s): sheet.skills[s].total for s in tables.ALL_SKILLS}
    variables.update(level=state.level, specialties=len(state.specialties))

    for src in sources:
        for m in src.modifiers:
            stat = m["stat"]
            if stat.startswith("attr:") and is_active(m, src, state):
                attr = stat.split(":", 1)[1]
                if attr in sheet.attributes:
                    sheet.attributes[attr].add(src.label, mod_amount(m, variables, m.get("marque")))
            elif stat.startswith("roll:"):
                # Unconditional roll bonuses go into the attribute's Misc bubble; conditional ones
                # (when="note", e.g. "when using Heroics") are only listed below the circle.
                attr = stat.split(":", 1)[1]
                if attr not in sheet.attributes:
                    continue
                if m.get("when") == "note":
                    text = m.get("label") or f"{attr} rolls"
                    sheet.roll_notes[attr].append((f"{src.label} ({text})", mod_amount(m, variables)))
                elif is_active(m, src, state):
                    label = src.label + (f" ({m['label']})" if m.get("label") else "")
                    sheet.attr_misc[attr].add(label, mod_amount(m, variables))
    for key, amount in state.misc.items():
        if key.startswith("attr:") and key[5:] in sheet.attributes:
            sheet.attr_misc[key[5:]].add(MISC_LABEL, amount)
    for attr, misc in sheet.attr_misc.items():
        for label, amount in misc.parts:
            sheet.attributes[attr].add(label, amount)
    variables.update({var_name(a): v.total for a, v in sheet.attributes.items()})

    # --- combat stats -------------------------------------------------------
    stats = {s: Value() for s in CHARACTER_STATS}
    stats["spd"].set_base(f"Base ({race['name']})", race["speed"])
    stats["swim"].set_base(f"Base ({race['name']})", race["swim"])
    stats["climb"].set_base(f"Base ({race['name']})", race["climb"])
    stats["wnd"].set_base("Base wounds", tables.BASE_WOUNDS)
    stats["ap"].set_base(f"Level {state.level}", tables.action_points(state.level))
    stats["essence_slots"].set_base("Base", 0)

    # Specialty bonus columns (sheet p.2), once each regardless of use.
    col_totals = {c: 0 for c in tables.COMBAT_STATS}
    for slug, level in state.specialties:
        s = reg.specialties.get(slug)
        if not s:
            continue
        row = {c: s["bonuses"].get(c, 0) for c in tables.COMBAT_STATS}
        sheet.specialty_rows.append({"slug": slug, "name": s["name"], "level": level, "bonuses": row,
                                     "skill": s["skill"] or "General", "specialty": s})
        for c, amount in row.items():
            col_totals[c] += amount
            stats[c].add(f"Specialty: {s['name']}", amount)
    sheet.specialty_misc = {c: state.misc.get(c, 0) for c in tables.COMBAT_STATS}
    sheet.specialty_totals = {c: col_totals[c] + sheet.specialty_misc[c] for c in tables.COMBAT_STATS}
    for c in tables.COMBAT_STATS:
        v = Value()
        for row in sheet.specialty_rows:
            v.add(f"Specialty: {row['name']}", row["bonuses"][c])
        v.add(MISC_LABEL, sheet.specialty_misc[c])
        sheet.specialty_total_values[c] = v
    variables.update({f"{c}_specialties": col_totals[c] for c in tables.COMBAT_STATS})

    transfers = []
    for src in sources:
        for m in src.modifiers:
            stat = m["stat"]
            if stat.startswith(("skill:", "attr:", "roll:")):
                continue
            if m.get("when") == "note" or stat == "note":
                amount = mod_amount(m, variables, m.get("marque"))
                sheet.notes.append((src.label, f"{m.get('label', '')}: {amount:+d}" if m.get("label") else f"{amount:+d}"))
                continue
            if not is_active(m, src, state):
                continue
            scope = m.get("scope", "character")
            if scope != "character" or stat in ("dc", "reach"):
                sheet.scoped.append((src, m))
                continue
            if m.get("op") == "transfer":
                transfers.append((src, m))
                continue
            amount = mod_amount(m, variables, m.get("marque"))
            label = src.label + (f" ({m['label']})" if m.get("label") and m.get("when") == "toggle" else "")
            if stat == "armor_degree":
                sheet.armor_degree += amount
            elif stat == "ap_ready":
                sheet.ap_ready_mods.append((label, amount))
            elif stat in stats:
                if m.get("op") == "set":
                    stats[stat].override = (f"{label}: set to {amount}", amount)
                elif m.get("op") == "base":
                    stats[stat].set_base(label, amount)
                else:
                    stats[stat].add(label, amount)

    for stat in CHARACTER_STATS:
        if stat in state.misc:
            stats[stat].add(MISC_LABEL, state.misc[stat])

    # Armor penalties (p.80), reduced by Armored Ease/Freedom degrees.
    armor = state.armor
    if armor is not None:
        sheet.armor = armor_block(armor, sheet.armor_degree)
        a = sheet.armor
        stats["soak"].add(f"Armor: {armor.name}", a["soak"])
        stats["eva"].add(f"Armor penalty: {armor.name}", -a["eva_penalty"].total)
        stats["spd"].add(f"Armor penalty: {armor.name}", -a["spd_penalty"].total)
        stats["swim"].add(f"Armor penalty: {armor.name}", -a["climb_swim_penalty"].total)
        stats["climb"].add(f"Armor penalty: {armor.name}", -a["climb_swim_penalty"].total)
    stats["spd"].floor = 5  # crawling at 5 ft is always possible
    stats["swim"].floor = 0
    stats["climb"].floor = 0

    if state.lost_wounds:
        stats["wnd"].add("Permanent fatal effects", -state.lost_wounds)
    if any((effects.get(k) or {}).get("halve_hp") for k in state.effects):
        stats["hp"].halved = "Fatigued"

    for src, m in transfers:
        moved = sum(stats[s].total for s in m.get("sources", []))
        stats[m["stat"]].add(f"{src.label} (stance)", moved)
        for s in m.get("sources", []):
            stats[s].override = (f"{src.label} (stance): set to 0", 0)

    sheet.stats = stats
    variables.update({f"{s}_total": v.total for s, v in stats.items()})
    sheet.variables = variables

    # Deflection item.
    if state.deflection is not None:
        d = state.deflection
        default = next((v for v in tables.DEFLECTION.values() if v["label"].lower() in d.name.lower()), None)
        bonus = Value()
        if d.deflect_bonus is not None:
            bonus.set_base(f"Item: {d.name}", d.deflect_bonus)
        else:
            bonus.set_base(f"{default['label']} (standard)" if default else "No bonus set", default["bonus"] if default else 0)
        sheet.deflection = {"item": d, "name": d.name, "bonus": bonus,
                            "ranged": d.deflect_ranged, "melee": d.deflect_melee}

    # Traits list for sheet p.2.
    trait_keys, _ = active_trait_keys(state)
    for key in trait_keys:
        t = reg.traits[key]
        choice = state.trait_choices.get(key)
        sheet.traits.append({"key": key, "name": t["name"], "text": t["text"], "choice": choice,
                             "kind": t["kind"], "roll": t.get("roll")})

    # Toggles and stances.
    for src in sources:
        toggle_mods = [m for m in src.modifiers if m.get("when") == "toggle"]
        if toggle_mods:
            sheet.toggles.append({"key": src.key, "label": src.label,
                                  "detail": ", ".join(describe_mod(m, variables) for m in toggle_mods),
                                  "active": src.key in state.toggles})
        if src.stance_slug:
            stance_mods = [m for m in src.modifiers if m.get("when") == "stance"]
            sheet.stances.append({"slug": src.stance_slug, "label": src.label.replace("Specialty: ", ""),
                                  "detail": ", ".join(describe_mod(m, variables) for m in stance_mods),
                                  "active": state.stance == src.stance_slug})
    sheet.stances.append({"slug": "footing", "label": "Footing", "detail": "needed for super-heavy items",
                          "active": state.stance == "footing"})

    from .weapons import hand_layout, unarmed_block, weapon_block

    sheet.weapons = [weapon_block(sheet, w) for w in sorted(state.weapons, key=lambda i: i.slot)]
    layout = hand_layout(state)
    sheet.hands = layout
    for side in ("left", "right", "wings"):
        item = layout[side]
        layout[f"{side}_block"] = weapon_block(sheet, item) if item is not None and item in state.weapons else None
    sheet.unarmed = unarmed_block(sheet)
    return sheet


STAT_SHORT = {"acc": "Acc", "eva": "Eva", "stk": "Stk", "def": "Def", "pri": "Pri", "spd": "Speed",
              "swim": "Swim", "climb": "Climb", "fly": "Fly", "aug": "Aug", "diy": "DIY", "wnd": "Wounds",
              "hp": "HP", "soak": "Soak", "dc": "DC", "ap": "AP", "ap_ready": "AP to ready"}


def describe_mod(m, variables):
    if m.get("op") == "transfer":
        return m.get("label", "")
    amount = mod_amount(m, variables, m.get("marque"))
    stat = STAT_SHORT.get(m["stat"], m["stat"])
    scope = m.get("scope", "character")
    scope_txt = "" if scope in ("character", "weapon") else f" ({scope})"
    text = f"{stat} {amount:+d}{scope_txt}" if m.get("op") != "base" else f"{stat} = {amount}{scope_txt}"
    if m.get("label"):
        text += f" – {m['label']}"
    return text


def armor_block(armor, degree=0):
    """Armor values (p.80). Penalties are positive Values (subtracted from the stats), reduced by
    Armored Ease/Freedom degrees; explicit item values win over the size table."""
    size = armor.size if armor.size in tables.ARMOR else "none"
    base = tables.ARMOR[size]
    idx = tables.ARMOR_ORDER.index(size)
    reduced_size = tables.ARMOR_ORDER[max(0, idx - degree)]
    pen_row = tables.ARMOR[reduced_size]
    size_label = tables.SIZE_LABELS.get(size, size)

    def penalty(override, key):
        v = Value()
        if override is not None:
            v.set_base(f"Item: {armor.name}", override)
        else:
            v.set_base(f"{size_label} armor", base[key])
            if pen_row[key] != base[key]:
                v.add(f"Armored Ease/Freedom (as {tables.SIZE_LABELS.get(reduced_size, reduced_size).lower()})",
                      pen_row[key] - base[key])
        return v

    return {
        "item": armor,
        "name": armor.name,
        "size": size_label,
        "soak": base["soak"] if armor.soak is None else armor.soak,
        "eva_penalty": penalty(armor.eva_penalty, "eva"),
        "spd_penalty": penalty(armor.spd_penalty, "spd"),
        "climb_swim_penalty": penalty(armor.climb_swim_penalty, "climb_swim"),
        "degree_reduced": degree if degree and idx else 0,
    }
