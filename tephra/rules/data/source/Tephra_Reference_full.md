# Tephra – Character Sheet Tool Reference

**Contents:** 0 Reading guide · 1 Core rules · 2 Creation & leveling · 3 Races · 4 Nationalities, stories, religions · 5 Gear · 6 Specialties (6.3 Brute, 6.4 Cunning, 6.5 Dexterity, 6.6 Spirit, 6.7 Sciences incl. all augments) · 7 Narrator notes · 8 Naming decisions & open points · Appendix A JSON data

> **Source:** *Tephra: The Steampunk RPG – Playing Guide* (Cracked Monocle, © 2012 Daniel Burrow, First Printing May 2012; PDF build May 2013, 288 pages). Page references (`p.`) point to PDF page numbers.
> **Book texts:** Numbers, tables and mechanics are included as data. Effect columns contain short summaries as placeholders. Run the companion script `add_book_texts.py` on your own copy of the PDF to replace them with the exact book texts. The script fills in all specialties (Effect column), all augments, accessories and trinkets (a "Book texts" block under each augment table), and the shop items in §5.12. Racial traits, stories and rules sections remain summaries (see §8).
> **Edition caveat:** This covers the 1st-edition Playing Guide only. Later editions/errata may differ; not checked.

## 0. How to read this document

### 0.1 Data model overview (terminology used by the book)

| Book term | Meaning | Count |
|---|---|---|
| **Attribute** | Brute, Cunning, Dexterity, Spirit, Science(s). Score = sum of its 4 skills (Science has 6) + Misc. | 5 |
| **Skill** | Trained area with points (e.g. Brawl 3). Rolled as d12 + skill points when using its specialties. | 22 |
| **Specialty** | Learnable ability under a skill. Grants fixed **combat-stat bonuses** + an effect. | ~400+ |
| **Combat statistics** | Acc, Eva, Stk, Def, Pri, Spd, Aug, DIY, Wnd, HP (the 10 columns on sheet p.2) | 10 |
| **Augment** | Craftable upgrade (Science skills), applied to items via augment slots. | many |
| **Racial trait** | Fixed traits per race + 1 random trait (d12). | – |
| **Story** | Background / Membership / Personality / Alteration etc. modifiers granted by narrator. | – |

### 0.2 Tag legend for specialty effects

Each specialty/augment summary may carry tags so the tool can decide what to auto-calculate:

| Tag | Meaning |
|---|---|
| `[PASSIVE]` | Always-on modifier (tool can apply automatically). |
| `[STANCE]` | Stance; costs 1 AP to enter unless stated; only one stance at a time. Modifiers only while in stance (tool: toggle). |
| `[ATTACK+X]` | Modifies an attack for +X AP. |
| `[REFLEX]` | Used reflexively (out of turn), AP from next turn's pool. |
| `[ACTION]` | Active use on your turn. |
| `[COND]` | Conditional modifier (applies only in a stated situation → tool: toggle/note). |
| `[SCALE:<Skill>]` | Value scales with points in a skill (formula given). |
| `[STAT:<stat> <mod>]` | Explicit numeric modification of a sheet value (beyond the fixed bonus columns). |
| `[GEAR]` | Changes weapon/armor/item values (damage class, reach, AP cost, slots…). |
| `[AUG]` / `[DIY]` | Grants augment / do-it-yourself choices. |
| `[REQ:…]` | Prerequisite (other specialty, weapon type, …). |
| `[NARR]` | Narrative / non-numeric effect, nothing to calculate. |

Stat abbreviations (book, p.26): **Acc** Accuracy · **Eva** Evade · **Stk** Strike · **Def** Defense · **Pri** Priority · **Spd** Speed · **Aug** Augment · **DIY** Do-it-Yourself · **Wnd** Wounds · **HP** Hit Points.

---

## 1. Core rules that affect character values (Ch. 1, p.8–23)

### 1.1 Dice
- One **d12** for everything. Roll = d12 + relevant modifier (attribute, skill, or combat stat).
- **Rule #1 – "1 is 1":** a natural 1 counts as 1 and no bonuses are added. *Exception:* penalties still apply (blind −4 on a natural 1 → −3).
- **Rule #2 – Pure 12s roll again:** natural 12 → roll again and add; repeat on further 12s. A 1 after a 12 = 13 (Rule #1 no longer applies). Not used for random called-shot location rolls.

### 1.2 Four tiers of success (p.9)

| Tier | Result | Label |
|---|---|---|
| T1 | 1–9 | Barely passing |
| T2 | 10–19 | Solid success |
| T3 | 20–29 | Phenomenal |
| T4 | 30+ | Beyond human |

Formula: `tier = result >= 30 ? 4 : result >= 20 ? 3 : result >= 10 ? 2 : 1` (results < 1 from penalties: book doesn't define tier 0; treat as T1/fail at narrator discretion — **unclear in source**).

### 1.3 Attributes & skills (p.9–10, 18)
- Attributes start at 0. `Attribute = Σ(points in its skills) + Misc` (sheet has a "Misc" circle per attribute).
- Attributes are used for general actions and **resists**.
- **Tiered resist:** each tier above T1 on the resist roll lowers the incoming effect by 1 tier (T1 unaffected, T2 −1, T3 −2, T4 −3).
- **Dodging blasts:** 1 AP reflexive Dexterity roll; must reach tier ≥ blast tier/marque and move ≤ your speed to exit the area.

| Attribute | Skills |
|---|---|
| **Brute** | Brawl, Frenzy, Overpower, Resilience |
| **Cunning** | Espionage, Expertise, Showmanship, Tactical |
| **Dexterity** | Ace, Agility, Marksmanship, Swashbuckling |
| **Spirit** | Faith, Grace, Luck, Shamanism |
| **Science(s)** | Alchemy, Armsmith, Automata, Bio-Flux, Engineer, Gadgetry (+ "Crafting" rules chapter) |

### 1.4 Action points (AP), turns, priority (p.10–11)
- AP per turn by level: **L1–3: 3 · L4–7: 4 · L8–11: 5 · L12: 6**.
- AP refresh at the end of your turn; unused AP are lost. Reflexive AP are taken from the *next* turn's pool.
- **Priority roll** = d12 + Pri bonus. Narrator may grant a circumstantial bonus (normally **+6**) for being ready.
- Combatants ready before combat may already be in stance / have weapons drawn.

### 1.5 Hit points, wounds, healing (p.10–11)
- **HP** = entirely the sum of specialty HP bonuses (+ race/story/item mods). No base HP.
- **Wounds** start at **12** (unless race says otherwise) + specialty Wnd bonuses.
- Damage reduces HP first; at 0 HP damage goes to wounds. Each time you take wounds damage → roll called-shot location → **Wounded effect**. With 0 wounds and hit again → **Fatal effect** each time.
- Unprepared/out of combat: no HP, damage goes straight to wounds.
- **Breather** (15–30 min rest): all HP restored. **Wounds** heal 1 per day.
- **Fatigued:** max HP halved (round down).
- Sheet fields: Hit Points / Max HP / Wounds / Max Wounds.

### 1.6 Attack resolution (p.12)
1. **Accuracy vs Evade:** attacker d12+Acc; defender d12+Eva. Hit if Acc ≥ Eva.
2. **Strike vs Defense:** attacker d12+Stk → tier → `damage = Damage Class × tier`. Defender d12+Def → tier → soaks `Soak Class × tier` (soak class from armor).
- Net damage = damage − soak (implied; min 0).

### 1.7 Standard actions & costs (p.12–15)

| Action | AP | Notes |
|---|---|---|
| Melee attack (weapon) | 2 | Most weapons |
| Unarmed attack | 1 | DC 2 |
| Ranged attack | varies | see weapon |
| Specialty attack | attack + X | multiple different specialties may stack on one attack; same one can't be added twice |
| Called shot | attack +1 | choose location (d12 chart), resistable: target resist attribute must **exceed** attacker's Strike roll (Accuracy roll for firearms/crossbows) |
| Non-lethal attack | as attack | no wound effects; target unconscious at 0 wounds |
| Deflect | 1 (interrupt) | needs shield/deflection item; +4 evade (base rule; see deflection items) |
| Draw/swap item | 1 | |
| Enter stance | 1 | one stance at a time; lost when knocked back/prone; can enter free at combat start. Everyone knows **Footing** (for super-heavy). |
| Grab | as unarmed (1) or whip (2) | choose location, Acc vs Eva, no damage; target breaks free 1 AP Brute/Dex vs Brute/Dex; grabbed hand can't use item |
| Throw (after grab) | 2 | Brute; T1 5 ft, T2 10 ft, T3 10 ft + prone, T4 15 ft + prone; target's Brute tiers down; small creatures +5 ft |
| Move | 1 | 25 ft (race-dependent) |
| Ready a firearm | varies | see weapon |
| Stand up | 1 | kneeling free |
| Sunder | as attack | vs wielded item; melee weapon DC −1 per tier; firearm/crossbow/bow DC −2 per tier; Dex resist tiers down; repairable at breather |
| Coup de grace | 3 | helpless target; pure 12 on strike, target natural 1 on defense, direct wounds |
| Break window / open door / pull lever | 1 | |

**Reflexive attacks:** leaving cover (ranged only) and using/consuming/drawing an item in melee range (melee only).

### 1.8 Called shot chart (d12, p.16–17)

| d12 | Location | Resist | Called-shot effect | Wounded effect | Fatal effect |
|---|---|---|---|---|---|
| 1 | Head | Brute | Disoriented (−1 AP/turn) until end of your next turn | Disoriented 1 turn per 3 dmg, can't re-orient | Beheaded – instant death |
| 2 | Eyes | Dex | −2 Acc & Eva until end of next turn | Blinded until breather: −4 Acc/Eva | Permanently blind: −4 Acc/Eva, **−1 max Wounds** |
| 3 | Ears | Cunning | −2 Eva until end of next turn | Deafened until breather: −2 Eva & sound rolls | Permanently deaf: −2 Eva, **−1 max Wounds** |
| 4 | Neck | Brute | Stunned 1 AP | Bleeding: 1 wound/turn, 1 turn per 3 dmg | Slit throat: die at end of next turn |
| 5 | Torso | Brute | Knocked back 5 ft (attacker may follow for 0 AP) | Broken ribs: every action needs Brute T2 or lose 1 AP; until breather | Slain |
| 6 | Groin | Spirit | Nausea: −2 all rolls until 3 AP spent | Purge: only move at half speed for 3 turns, −4 Eva | Gutted: recover 10 dmg before end of next turn or die |
| 7–8 | Arm | Brute | −2 on rolls with that arm until end of next turn | Sprained arm: −6 on rolls with it until breather | Severed arm: **−2 max Wounds**, two-arm tasks impossible/−6; die in 3 turns unless 3 AP bandaging |
| 9–10 | Hand | Dex | Drop held item (1 AP to pick up) | Bruised hand: can't wield with it until breather | Severed hand: **−1 max Wounds**; die in 6 turns unless 3 AP bandaging |
| 11–12 | Leg | Dex | Attacker's choice: slowed (+1 AP to move) or tripped (prone) | Sprained leg: −10 Spd (min 5), prone; until breather | Severed leg: −20 Spd (min 5), two-leg tasks −6, **−1 max Wounds**; die in 3 turns unless 3 AP bandaging |

Called-shot effects don't stack (renew only), except torso knockback and neck stun. Called shots against a target in wounds/fatals auto-hit that location.

### 1.9 Cover (p.20–21)

| Degree | Examples | Covers up to | Evade bonus | Hide roll mod |
|---|---|---|---|---|
| Soft cover | shrubs, canvas | – | attacker −4 Acc (−2 if silhouette); you get same penalty on Evade | – |
| Poor (T1) | post, side-table, person | 3 locations | +2 | – |
| Light (T2) | bush, couch, tree | 6 locations | +4 | – |
| Medium (T3) | large tree, barrel, trench, corner | 9 locations | +6 | −4 |
| Heavy (T4) | full wall, ducked behind furniture | 11 locations | +8 | ±0 |
| Total | nothing visible | all | can't be targeted | +4 |

- **Taking total cover:** 1 AP (or at end of a move) behind medium/heavy cover; peeking is 0 AP but counts as leaving cover.
- **Firing blindly** from total cover: only hand(s) exposed; −4 Acc (−8 if location unknown).
- Noticing: both roll Cunning (hider gets cover mod). Searching a specific spot auto-finds.
- Precipitation/wind can add/upgrade cover (narrator).

### 1.10 Status effects (p.22–23)

| Status | Mechanical effect |
|---|---|
| Bleeding (status) | HP damage (then wounds) each AP refresh, unsoakable, stacks; each 1 AP spent (victim/adjacent) negates 5 bleed |
| Blinded | −4 Acc & Eva vs target; poor vision/fog/low light −2 |
| Burning T1/T2/T3/T4 | 2/4/8/16 unsoakable dmg per turn; AP to extinguish 2/4/8/16; item destruction escalates (T1 singed, T2 wood/organic/cloth destroyed, T3 leather/cloth/wood, T4 even metal unusable) |
| Burnt T1/T2/T3/T4 | −1/−3/−5/−7 to all Defense rolls (location burns: narrator applies to that body part) |
| Deafened | −2 Eva; −2 on sound-based rolls |
| Disoriented | −1 AP per turn; spend 3 AP to re-orient |
| Drowning | Brute roll each turn, target tier starts at T2 and rises; fail → unconscious; die 3 turns later |
| Enraged | −2 all rolls except attacking rage source; +2 Acc & Stk vs source; 2 AP to calm |
| Fatigued | max HP halved (round down) |
| Fear T1 Scared | −2 all resist rolls (−4 vs source) |
| Fear T2 Frightened | −2 all rolls (−4 vs source) |
| Fear T3 Terrified | −2 all rolls (−4 vs source); ≥1 AP/turn moving away; can't approach |
| Fear T4 True dread | −4 all rolls (−6 vs source); can only try to overcome (1 AP per re-roll) |
| (Fear general) | 1 reflexive AP to attempt overcoming; Spirit always usable as resist; ends at next downtime |
| Nausea | −2 all rolls until 3 AP spent |
| Paralyzed | helpless; damage straight to wounds; no actions |
| Prone | −1 Acc/Eva/Stk/Def; speed 5 ft; stand = 1 AP (draws reflexes); can't stand while grabbed |
| Stunned (X AP) | lose X AP from current pool; still evades/resists |

### 1.11 Battlefield modifiers (p.23)
- **Falling:** 1 wound per 20 ft; each tier above T1 on Dex ignores 2 wounds; roll a wound effect per 2 wounds taken.
- **Terrain speed penalty:** Minor −5 (rocking boat, light forest) · Unsteady −10 (forest, rocks, snow) · Difficult −15 (swamp, snowy mountain) · Impossible −20 (dense jungle, rubble). Crawling at 5 ft always possible.

### 1.12 Social tells (p.19)
Cunning roll, tiered. Lie detecting (resist Cunning), Pacify/Intimidate (resist Spirit), Provoke (resist Cunning). Narrative only.

### 1.13 Stories (p.11)
Background, Membership, Personality, Alteration stories; granted/removed by narrator; give bonuses & penalties. Typically 1 (or 1–2) Background/Personality stories at creation. Details in §5.

---
## 2. Character creation & leveling (Ch. 2, p.24–27)

### 2.1 Creation steps
1. **Race & nationality** – apply racial traits; roll d12 on the race's random-trait table (narrator may allow choosing/re-rolling). Choose nationality (Ch. 4) and nationality stories.
2. **Skills** – place **3** points in 1 skill (primary), **2** points in 2 skills, **1** point in 3 skills. No stacking: 6 different skills at L1.
3. **Attributes** – attribute = Σ its skills.
4. **Specialties** – choose **3**. Must be from skills with ≥1 point (except *general specialties*). Record their combat-stat bonuses.
5. **Augments** – each "Aug +X" from specialties = X augment choices from a Science skill you have points in; can be learned regardless of slot size.
6. **Weapons & armor** – choose by size class (Ch. 5). Accuracy/Strike and Evade/Defense come from specialty bonuses.
7. **Gear** – anything from Starting Gear list (reasonable); **10 princes** pocket cash.
8. **Derived statistics** – AP 3; Speed = race base + specialty Spd bonuses; Priority = Pri bonuses; Wounds = 12 (unless race says otherwise) + Wnd; HP = Σ HP bonuses.
9. **Background stories** – usually 1 (narrator guidelines).
10. Name, personality, etc.

### 2.2 Leveling (p.27)
- 12 levels; **12 XP per level** (clock). At every level after 1st:
  - +2 points in any 1 skill, +1 point in any 2 *other* skills
  - recompute attributes
  - learn **1 new specialty**, apply its bonuses
  - at L4, L8, L12: +1 AP (3 → 4 → 5 → 6)
- Character sheet specialty slots: L1 ×3, then one per level L2–L12 → **14 specialties at L12**.
- **Skill points total:** L1 = 3+2+2+1+1+1 = 10; each level +4 → L12 = 54.

**Retrofitting:**
- Specialties: at L4, L8, L12 you may swap one specialty for another **within the same attribute**.
- Augments: each time you learn a new augment you may swap one augment for another **from the same skill**.

### 2.3 Starting princes by level

| Level | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Princes | 10 | 18 | 32 | 58 | 105 | 190 | 340 | 615 | 1,100 | 2,000 | 3,570 | 6,425 |

Higher-level characters: build at L1, then level up one at a time.

### 2.4 Character sheet fields (p.286–287) — target output of the tool
- **Header:** Player, Character name, Race, Nationality, Religion, Age, Height, Weight.
- **2 weapon blocks:** Description, Size, Type, Reach, AP to Use, AP to Ready, Accuracy, Strike, Damage Class (4 boxes → tiers), Notes/Augments.
- **Circles:** AP, Priority, Speed, Swim Speed, Climb Speed, Fly Speed; Tier table (1–9 / 10–19 / 20–29 / 30+).
- **Armor block:** Description, Size, Soak Class, Evade penalty, Speed penalty, Climb/Swim penalty, Notes/Augments; circles **Evade**, **Defense**.
- **Deflection block:** Item, Evade Bonus (vs Ranged ☐ / vs Melee ☐), "1 AP to activate".
- **Health:** Hit Points, Max HP, Wounds, Max Wounds; Wound Effects, Fatal Effects, Status Effects; body diagram with 12 called-shot locations.
- **Attributes:** 22 skills with points; per attribute a **Misc** field and total. Experience clock (1–12) and Level.
- **Page 2 – Specialties table:** rows L1, L1, L1, L2…L12; columns Accuracy, Evade, Strike, Defense, Priority, Speed, Augments, DIY, Wounds, Hit Points; **Misc** row and **Totals** row.
- Stories, Racial Traits, Money on-hand, Money in bank, Gear, Augments, Notes.

**Implied formulas for the tool:**
```
Accuracy (per weapon) = Σspecialty Acc + misc + race/trait/story/weapon mods
Evade   = Σ Eva + misc + race mods − armor evade penalty (+ deflection when active)
Strike  = Σ Stk + misc + mods ; Defense = Σ Def + misc + mods
Priority= Σ Pri + mods ; Speed = race speed + Σ Spd + mods − armor speed penalty
HP max  = Σ HP + mods ; Wounds max = 12 (race-dependent) + Σ Wnd + mods − permanent losses
Augments known = Σ Aug ; DIY = Σ DIY
AP = 3 / 4 (L4) / 5 (L8) / 6 (L12)
```

---

## 3. Races (Ch. 3, p.28–49)

*Trait texts below are summaries (not yet replaced by book text — see §8).*

Legend: "Speed" = land / swim / climb in feet. Each race lists fixed traits, then a d12 random-trait table.

### 3.1 Human (p.29)
**Speed:** 25 / 15 / 15.
**Fixed:** choose **two** of:
| Option | Effect | Tags |
|---|---|---|
| Favored Attribute | Pick 1 attribute: on a natural 1 with that attribute, you still add bonuses (not its skills). | `[PASSIVE]` |
| Innovative | +1 DIY, +2 Augments (only if starting with a craft). | `[STAT:DIY +1] [STAT:Aug +2]` |
| Peerless | You win all tied rolls (normally aggressor wins). | `[PASSIVE]` |
| Relentless | +3 HP at start, +1 HP per specialty taken. | `[STAT:HP +3 +1×specialties]` |

**Random (d12):**
| d12 | Trait | Effect | Tags |
|---|---|---|---|
| 1 | Accustomed to the Dark | No penalties from poor lighting (blindness still applies). | `[COND]` |
| 2 | Adaptable | No penalties from extreme heat/cold/humidity environments. | `[NARR]` |
| 3 | Easily Reoriented | Re-orienting from disoriented costs 1 AP instead of 3. | `[PASSIVE]` |
| 4 | Emotionally Driven | Can't start a battle fatigued when a friend is endangered. | `[COND]` |
| 5 | Great Height | +2 Strike. | `[STAT:Stk +2]` |
| 6 | Hardy & Stout | +6 HP. | `[STAT:HP +6]` |
| 7 | Momentum | +5 Priority when you know a battle is coming (not when ambushed). | `[COND] [STAT:Pri +5]` |
| 8 | Monkey's Uncle | +10 ft climb speed. | `[STAT:Climb +10]` |
| 9 | Perceptive | +4 on Cunning rolls to notice. | `[COND]` |
| 10 | Quick Feet | Land speed 35 ft instead of 25. | `[STAT:Spd base 35]` |
| 11 | Reactionary | +3 on all priority rolls, even off-guard. | `[STAT:Pri +3]` |
| 12 | Ruckus Rowser | +4 Cunning to intimidate or provoke. | `[COND]` |

### 3.2 Ayodin (p.30–33)
**Speed:** 25 / 35 / 15.
**Fixed:**
- **Amphibious:** breathes air and water. `[NARR]`
- **Versatile Wing-Fins:** +1 Evade. `[STAT:Eva +1]`

**Random (d12):**
| d12 | Trait | Effect | Tags |
|---|---|---|---|
| 1 | Blindsense | Echolocation: see regardless of light unless deafened. | `[COND]` |
| 2 | Born in the Seas | +10 ft swim speed. | `[STAT:Swim +10]` |
| 3 | Built-in Bulwark | Fins count as shields for deflections. | `[GEAR]` |
| 4 | Expressive Flair | +3 Cunning when convincing/changing emotions. | `[COND]` |
| 5 | Inner Silence | +2 Cunning under duress / when intimidated or provoked. | `[COND]` |
| 6 | Master Diving | No falling damage when landing in water. | `[COND]` |
| 7 | Natural Touch | Unarmed DC 3. | `[GEAR] unarmed DC=3` |
| 8 | Passive | +4 Spirit when used as a resist. | `[COND]` |
| 9 | Powerful Paralysis | Anyone you touch: −3 on their next evade roll (expires end of their next turn). | `[COND]` |
| 10 | Terror from the Deep | +3 Strike vs adjacent foes. | `[COND] [STAT:Stk +3 melee-adjacent]` |
| 11 | Vanguard | Adjacent allies +2 Evade (doesn't stack with others having it). | `[COND] aura` |
| 12 | Wings as Arms | Wings can hold one-handed items (not two-handed). | `[GEAR]` |

### 3.3 Elf (p.34–37)
**Speed:** 30 / 20 / 30.
**Fixed:**
| Trait | Effect | Tags |
|---|---|---|
| Big Boned | +2 on all Brute (attribute) rolls. | `[PASSIVE]` |
| Tough | +4 HP. | `[STAT:HP +4]` |
| Tree-Ripping Strength | Unarmed & melee weapons +1 DC. | `[GEAR] melee/unarmed DC +1` |
| Weak Souls | −3 on Spirit attribute rolls (not Spirit skills). | `[PASSIVE]` |
| Depleted Essence | −1 essence manipulation slot (Bio-Flux). | `[GEAR]` |

**Random (d12):**
| d12 | Trait | Effect | Tags |
|---|---|---|---|
| 1 | Gears of the World | +6 Cunning to discern non-organic disturbance of an area. | `[COND]` |
| 2 | Danger Sense | +3 Priority. | `[STAT:Pri +3]` |
| 3 | Ears to the Heavens | Hearing rolls +1 tier. | `[COND]` |
| 4 | Flight without Wings | +10 ft land speed (→ 40). | `[STAT:Spd +10]` |
| 5 | Fruit of the Fallen | Negates Weak Souls; +3 Spirit when using Heroics. | `[PASSIVE]` |
| 6 | Improperly Typecast | +2 Cunning to gather information. | `[COND]` |
| 7 | Like the Grave | After hidden a full turn, +5 to remain unseen. | `[COND]` |
| 8 | Noble Creature | Attack +1 AP: +Strike equal to your level. | `[ATTACK+1] [SCALE:Level]` |
| 9 | Raging Loyalty | When adjacent ally is struck, reflexive melee attack vs assailant in reach. | `[REFLEX]` |
| 10 | Tenacious Grip | +6 to keep holding on to something. | `[COND]` |
| 11 | Unstoppable | Speed penalties from wounds/status reduced by 10 ft. | `[PASSIVE]` |
| 12 | Vaulting Predator | +10 ft forward leap, +2 ft vertical jump. | `[NARR]` |

### 3.4 Farishtaa (p.38–41)
**Speed:** 25 / 15 / 15.
**Fixed:**
| Trait | Effect | Tags |
|---|---|---|
| Born to be Airborne | Start with **2 skill points in Ace** (in addition to normal starting points; may add starting points there as normal). | `[STAT:Ace +2]` |
| Piercing Scrutiny | +1 Accuracy. | `[STAT:Acc +1]` |
| Unpredictable | +2 Cunning when interacting with people. | `[COND]` |

**Random (d12):**
| d12 | Trait | Effect | Tags |
|---|---|---|---|
| 1 | Botched Surgery | Gain elf traits Tree-Ripping Strength and Weak Soul. | `[GEAR] [PASSIVE]` |
| 2 | Dancer's Body | +2 on Dexterity (attribute) rolls. | `[PASSIVE]` |
| 3 | Emotional Unavailability | Fear effects −1 tier (immune to T1 fear). | `[PASSIVE]` |
| 4 | Instant Motion | 1 AP reflexive at combat start: +8 priority roll. | `[REFLEX]` |
| 5 | Halo | 10-ft light aura + slight heat, suppressible. | `[NARR]` |
| 6 | Prominent Host | Roll on the **elf** random trait table instead. | `[RULE]` |
| 7 | Skin-Deep Values | +2 Evade and resist vs called shots to head, eyes, ears. | `[COND]` |
| 8 | Spirit of the Angels | Natural 1 on Spirit attribute still adds bonuses. | `[PASSIVE]` |
| 9 | Superiority Complex | Adjacent foes −2 Defense. | `[COND] aura` |
| 10 | Tinge of Insanity | At 0 HP: +4 Accuracy and +4 Strike. | `[COND]` |
| 11 | Unexplainable Memories | +2 on all Cunning rolls. | `[PASSIVE]` |
| 12 | Undeveloped Wings | No falling damage unless bound/unconscious/bad weather. | `[COND]` |

### 3.5 Gnome (p.42–45)
**Speed:** 15 / 10 / 10.
**Fixed:**
| Trait | Effect | Tags |
|---|---|---|
| Greater Spirit | +3 on Spirit rolls. | `[PASSIVE]` |
| Light Build | −2 on Brute rolls. | `[PASSIVE]` |
| Small Stature | +1 Evade. | `[STAT:Eva +1]` |
| Smaller Weapons | Can't conceal light weapons; unarmed DC 1. | `[GEAR] unarmed DC=1` |
| Random Racial Traits | Choose 1 trait **and** roll 1 (re-roll duplicates) → **2 random traits**. | `[RULE]` |
| (small creature) | Thrown +5 ft extra (grab/throw rule). | `[NARR]` |

**Random (d12):**
| d12 | Trait | Effect | Tags |
|---|---|---|---|
| 1 | Bend Sight | See around corners up to 90°. | `[NARR]` |
| 2 | Deep Pockets | Can conceal light and medium items. | `[NARR]` |
| 3 | Earthshape | 2 AP: raise/lower earth 5 ft in a 5-ft area. | `[ACTION]` |
| 4 | Feel the Earth | Sense vibrations within 15 ft when touching ground (opposed Cunning vs sneaking). | `[COND]` |
| 5 | Growth Intensity | 1 AP: switch to elf size — use elf racial traits instead of gnome while large. | `[ACTION] swaps race traits` |
| 6 | Noiseless | Silent footsteps; sneaking +1 tier. | `[COND]` |
| 7 | Parts of Nature | 3 AP: draw a light basic tool/weapon/torch from tree or earth. | `[ACTION]` |
| 8 | Piercing Sight | Ranged weapons: double range, +2 Accuracy. | `[GEAR] ranged Acc +2, range ×2` |
| 9 | Ripcord Muscles | Negates Light Build; +2 Strike; unarmed DC 2. | `[STAT:Stk +2] [GEAR] unarmed DC=2` |
| 10 | Waterwalk | 1 AP per turn: stand on calm water. | `[ACTION]` |
| 11 | Windwalk | 1 AP: glide 40 ft in one direction. | `[ACTION]` |
| 12 | Wiry | +1 additional Evade. | `[STAT:Eva +1]` |

### 3.6 Satyr (p.46–49)
**Speed:** 35 / 10 / 10.
**Fixed:**
| Trait | Effect | Tags |
|---|---|---|
| Alcohol Immunity | Not negatively affected by alcohol. | `[NARR]` |
| Empathetic | Roll twice, take higher, when detecting lies. | `[COND]` |

**Random (d12):**
| d12 | Trait | Effect | Tags |
|---|---|---|---|
| 1 | Born Hero | Heroics (Spirit): roll twice, take higher. | `[COND]` |
| 2 | Brothers-in-Arms | Adjacent to a satyr ally: both +2 Accuracy (no stacking). | `[COND]` |
| 3 | Built to Last | +6 HP. | `[STAT:HP +6]` |
| 4 | Expecting the Worst | +4 Priority rolls. | `[STAT:Pri +4]` |
| 5 | Fleet of Foot | +10 ft speed (→ 45). | `[STAT:Spd +10]` |
| 6 | Frightening Combatant | Unarmed DC 4 (horns/hooves). | `[GEAR] unarmed DC=4` |
| 7 | Horned & Dangerous | Unarmed horn attacks deal +1 unsoakable bleeding damage. | `[GEAR]` |
| 8 | Natural High | Ignore fatigue if drank alcohol in past few hours (not for multi-day fatigue). | `[COND]` |
| 9 | Poison Immunity | Brute resist vs poison +1 tier. | `[COND]` |
| 10 | Protector | Adjacent allies +2 Defense. | `[COND] aura` |
| 11 | Stable Hoofing | Ignore speed penalties of minor & unsteady terrain. | `[COND]` |
| 12 | Unphased by War | +4 to resist being stunned. | `[COND]` |

### 3.7 Race comparison (for tool defaults)

| Race | Land | Swim | Climb | Fixed stat mods | Unarmed DC | Notes |
|---|---|---|---|---|---|---|
| Human | 25 | 15 | 15 | 2 of 4 options | 2 | |
| Ayodin | 25 | 35 | 15 | Eva +1 | 2 | amphibious |
| Elf | 30 | 20 | 30 | HP +4, melee DC +1, Brute rolls +2, Spirit rolls −3 | 3 (2+1) | −1 essence slot |
| Farishtaa | 25 | 15 | 15 | Acc +1, Ace +2 skill pts | 2 | |
| Gnome | 15 | 10 | 10 | Eva +1, Spirit rolls +3, Brute rolls −2 | 1 | 2 random traits |
| Satyr | 35 | 10 | 10 | – | 2 | |

No race changes the base 12 wounds in this book (verified: none of the race pages mention a different wound count). Fly speed comes only from gear/augments/vehicles.

---
## 4. Nationalities, organizations, stories & religions (Ch. 4, p.50–71)

*Story texts below are summaries (not yet replaced by book text — see §8).*

Stories are mostly narrative. Only a few carry numeric modifiers; those are tagged. Tool suggestion: free-selectable list with optional modifiers.

### 4.1 Nationalities (lore summary)

| Nationality | Region / summary | Notable relations |
|---|---|---|
| **Evanglessian** (most common) | Young human-led empire (founded by Velkya), steam, railways, elite military, airborne navy; open-minded melting pot; Tailemy is state religion. | Dislike Paldoran pirates, oceanic ayodin, Hauds; good with Izedans, Dalvozzeans. |
| **Dalvozzean** | Farishtaa-ruled caste nation in the High Rilausian Forest; capital Daion (white towers above canopy, slums below); ruled by the Nine Wings of Divinity (Day Society). | Tension with Hauds (Siyesh) and Izedans; courteous to rare ayodin/Paldorans. |
| **Izedan** | Desert nomad scavengers (the Quist), caravans, ritual scarification, steam crossbows; pale/bleach-white skin, often bald. | Bad with Hauds; good with Valdru gnomes, satyrs; fascinated by ayodin. |
| **Paldoran Exile** | Radiation-ravaged homeland (aether resonators); people live on giant Stormships, raid for supplies; Infernal Jinzium church. | Shunned widely; hostile with saltwater ayodin; wary of Zel Hauds; best welcome in Evangless. |
| **Zel Haud** | Industrial Haudi province Zelhost (Archduke Zimarati), matriarchal, very tall people; semi-independent of the Empress in Siyesh. | Elitist toward neighbors; legacy of satyr slavery. |

### 4.2 Nationality stories (p.53–61)

| Nationality | Story | Requires | Effect | Tags |
|---|---|---|---|---|
| Evangless | Ayodin of the Exodus | Ayodin | Respected by older Evanglessians (fought with surfacers). | `[NARR]` |
| Evangless | Royalist | – | Sided with Emperor's automaton armies in Civil War; better with Royalists. | `[NARR]` |
| Evangless | Militarist | – | Sided with the military coup; better with Militarists. | `[NARR]` |
| Evangless | Veteran | – | Civil War veteran with war stories. | `[NARR]` |
| Evangless | Settler of the West | – | Can easily calm & direct livestock. | `[NARR]` |
| Evangless | Naturalized Tharmurian | – | Seen as foreigner (white hair, pale). | `[NARR]` |
| Evangless | Evanglessian Nobility | – | Access to most government buildings. | `[NARR]` |
| Evangless | Adopted by Evangless | – | May take 1 nationality story from another nationality. | `[RULE]` |
| Dalvozzea | Savage Elf | – | Survive indefinitely in forests without provisions. | `[NARR]` |
| Dalvozzea | Highborne Elf | Elf | Slightly higher regard than average elf. | `[NARR]` |
| Dalvozzea | Second Generation Farishtaa | Farishtaa | Born farishtaa; elves jealous. | `[NARR]` |
| Dalvozzea | Member of the Night Society | Farishtaa | Access to all facilities except Day Society's. | `[NARR]` |
| Dalvozzea | Miadruid | Gnome | Get along with non-caste Dalvozzeans. | `[NARR]` |
| Dalvozzea | White-Tower Mercenary | – | Regarded like Night Society; stacks prestige with it. | `[NARR]` |
| Dalvozzea | Ashen Angel | – | Rebel tattoo; kinship with rebels; police treat you as terrorist. | `[NARR]` |
| Dalvozzea | Elf of Adoipa | Elf | Admired by other elves. | `[NARR]` |
| Izeda | Disciple of Pain | – | Ritually scarred; pain doesn't slow you (book gives no number — **unclear**; likely narrative). | `[NARR]` |
| Izeda | Raised to Scavenge | – | Can scavenge/sell petty objects. | `[NARR]` |
| Izeda | Asagnu Caravaneer | – | Proud royal caravan. | `[NARR]` |
| Izeda | Caravaneer of Sapience | – | Affinity with vultures. | `[NARR]` |
| Izeda | Sunrage Elf | Elf | Desert elf, weathers prejudice. | `[NARR]` |
| Paldorus | Stowaway | – | Not a colony citizen. | `[NARR]` |
| Paldorus | Chosen by Jinzi | – | Personally invited by the church. | `[NARR]` |
| Paldorus | Paldoran Militant | – | Military raider; shunned/hanged elsewhere. | `[NARR]` |
| Paldorus | Grounded Exile | – | Expelled from Stormship. | `[NARR]` |
| Paldorus | Signs of Radiation | – | Minor skin peeling from radiation. | `[NARR]` |
| Paldorus | **Stormship Engineer** | – | **Start with 1 point in Engineer** (skill). | `[STAT:Engineer +1]` |
| Zelhost | Matriarch | Female | Haudi men bow to you. | `[NARR]` |
| Zelhost | Imperial Traditionalist | – | Get along with Siyeshi Hauds. | `[NARR]` |
| Zelhost | Satyr Servant | Satyr | Flinch when a Haud raises a hand (out of combat). | `[NARR]` |
| Zelhost | Honor without Etiquette | – | Hauds recognize your respectability. | `[NARR]` |
| Zelhost | **National Passtime** | – | +4 Sciences to identify augments in an alchemical solution. | `[COND]` |

> Note: "Deal with the Devil" on p.59 is a lore sidebar (King Caeliph & Jayro Tiin), not a story.

### 4.3 Organizations & membership stories (p.62–65)

| Organization | Summary | Membership stories (effect) |
|---|---|---|
| **The Brimstones** | Western Evangless gang serving cattle barons; mercenary. | Brimstone Thug (free low-grade beef from barons); **Small Government, Big Gun** (+2 resist vs intimidation by non-military officials on baron land) `[COND]` |
| **The Carnival** | "Insane" underground anti-tyranny movement with airship fleet (Varas Dyrashi). | Carnie (ride on Carnival airships); Carnival Performer (sleeper cell; recognize members instantly) |
| **Coaldust Unions** | Labor unions. | Coaldust Laborer (+4 Notice whether a workplace is unsafe) `[COND]`; Coaldust Protestor (find sympathetic employees) |
| **Fulbourne Society** | Old-money aristocratic fraternity; info brokers. | Fulbourne Initiate (access to lodges); Fulbourne Scout (tells T2+ reveal old money); New Blood Fulbourne (access to Society records on you) |
| **Highflyers** | Elite pilots' club (Silver Lining bar, Aldamiir). | Highflyer (badges → unrestricted Evanglessian airspace); Civil War Ace (arrange sanctioned duels); Legendary Highflyer (VIP pass) |
| **LaVrey National Detective Agency** | Largest security force (Jordana LaVrey). | LaVrey Agent (receive job notices); LaVrey Detective (badge); LaVrey Train Guard (stop cargo trains) |
| **Renovators** | Rebuild landmarks (Jed K. Sampson), analytical engines. | Renovator (landmark pictographs); Renovator Foreman (instant historical records via engine); Renovator Designer (access to laborers) |
| **Sons of Strife** | Social-reform movement for a parliament. | Son of Strife (friends among Militarists/unions); Born a Son (journalists interested); Charitable Daughter (allies in low places) |

### 4.4 Background stories (p.66–68)
Usually 1 at creation (narrator may allow more).

| Story | Effect | Tags |
|---|---|---|
| Airborne | Fight unhindered in the air. | `[COND]` |
| Bartender | Mix any drink. | `[NARR]` |
| Burglar | Cunning to spot a target's inventory +1 tier. | `[COND]` |
| Cattle Wrangler | +1 Acc to grab an animal with a whip. | `[COND]` |
| Chef | Sciences roll for cooking: roll twice, take higher. | `[COND]` |
| Clergy (req. a Faith membership story) | Persuading someone of your faith +1 tier. | `[COND]` |
| Conductor | Know layout/function of civilian train cars. | `[NARR]` |
| Cowboy | Cunning to scout during a breather: roll twice, take higher. | `[COND]` |
| Cutpurse | Hand/take items stealthily without provoking reflexes. | `[COND]` |
| Forgery Artist | Forge documents. | `[NARR]` |
| Forest Gatherer | Always find food in the wild. | `[NARR]` |
| Gambler | Each downtime wager ≤10 princes double-or-nothing (odd/even). | `[NARR]` |
| Gentry | Employees of your estate +1 Brute. | `[NARR]` |
| Handy Craftsman | Make all "Adventuring Basics" equipment during downtime. | `[NARR]` |
| Kinematician | Determine a weapon's range via Cunning. | `[NARR]` |
| Lawman | +2 Cunning to catch lawbreakers in the act. | `[COND]` |
| Librarian | Research takes half time. | `[NARR]` |
| Lumberjack | Predict where trees fall. | `[NARR]` |
| Mariner | Know nearby aquatic life. | `[NARR]` |
| Moneylender | Remember names/locations; lend money. | `[NARR]` |
| Mysterious Twin | Take the skills, specialties, XP and stories of a party member who just died. | `[RULE]` |
| Nobility | Signet ring; welcome among elites. | `[NARR]` |
| Physician | Cunning to diagnose: roll twice, take higher. | `[COND]` |
| Railway Worker | Free passenger train rides. | `[NARR]` |
| Repairman | Repair broken items outside battle even if you can't make them. | `[NARR]` |
| Rodeo Rider | +4 Dex to stay mounted when being knocked off. | `[COND]` |
| Raised by the Church (listed under Tailemy) | +2 Cunning to get something from a Tailemite church. | `[COND]` |

### 4.5 Religions & faith membership stories (p.69–71)

**Tailemy** – state religion of Evangless; Beloved Mother sacrificed herself to Aeon to birth the world; holy book *Aktailem*; led by the Triune (Paladin, Crusader, Martyr); embraces change & technology; symbol moth (+ snake = Aeon).

| Story | Type | Requires | Effect | Tags |
|---|---|---|---|---|
| Crusader of Tailemy | Faith Membership | – | +1 Strike vs anyone who declared heresy against the Beloved Mother. | `[COND] [STAT:Stk +1]` |
| Devout of Tailemy | Personality | – | Any week you attended a Tailemite sermon: +1 on all Spirit rolls. | `[COND]` |
| Martyr of Tailemy | Faith Membership | – | Clergy; treated well by believers. | `[NARR]` |
| Ordained by Tailemy | Faith Membership | any other Tailemite membership story | May perform rites & represent the church. | `[NARR]` |
| Paladin of Tailemy | Faith Membership | – | **+1 Soak Class** when defending another Tailemite. | `[COND] [STAT:Soak +1]` |
| Raised by the Church | Background | – | +2 Cunning to get something from a Tailemite church. | `[COND]` |

**Free Will** – Haudi religion (Empress Zoleesha IV) of reason and science; Teachers, Savants, Hierophant; no holy book or rites.

| Story | Requires | Effect | Tags |
|---|---|---|---|
| Free Will Acolyte | – | +1 Spirit when interacting with the hidebound/dogmatic. | `[COND]` |
| Teacher of the Faith | – | May lead services; +2 Cunning on days you do. | `[COND]` |
| Free Will Savant | Teacher of the Faith + published intellectual work | Teacher benefits; may represent Free Will regionally. | `[NARR]` |

**Jinzium** – oldest religion; sun god Jinzi; souls become stars; factions: Eternal Church/Orthodox (Igi, the Elf Who Writes in Fire, Guiding Paradigm), Revivalists (Dalvozzea, Nine Wings; winged farishtaas as angels), Infernal Jinzium (Paldorans, Six Infernals).

| Story | Requires | Effect | Tags |
|---|---|---|---|
| Scion of the Sun | – | +2 Spirit to stay focused on bright, blue days. | `[COND]` |
| Archon | – | May lead services; aid & shelter from congregations. | `[NARR]` |
| Soul of Sol | Archon | May speak for the church. | `[NARR]` |
| Orthodox Jinzist | – | Sermon by Igi fully reassures your faith. | `[NARR]` |
| Starborn Traditionalist | – | Rituals intrigue agnostics. | `[NARR]` |
| Angel Fever | – | Never fatigued in presence of a winged farishtaa. | `[COND]` |

Ayodin religions (p.32, lore only): **Harabe Mavi** (moon goddess Aeon; surface belongs to ayodin) and **Path of Gilkoroh** (martyr saint; freshwater ayodin).

> Other story types referenced but not listed in this book with full tables: **Personality stories** (e.g. *Yobbish*) and **Alteration stories** (e.g. *Burn Victim*) — narrator-awarded; the tool should allow custom stories with custom modifiers.

---
## 5. Gear (Ch. 5, p.72–87)

### 5.1 Currency – the Trust (p.73)

| Coin | = |
|---|---|
| 1 duke | splittable into ½, ¼, ⅛ (magnetic pieces) |
| 1 prince | 10 dukes |
| 1 king | 10 princes = 100 dukes |

Reference prices: one-serving goods ≈ ¼ duke (mug of ale); good sword ≈ 5 princes; average daily wage 1–3 dukes.

| Trust service | Cost |
|---|---|
| Open an account | 5 princes |
| Safebox | 3 princes |
| Safebox in the Vault | 15 princes |
| Deposit/withdraw at own branch | free |
| Deposit/withdraw at another branch | 1 duke |
| Convert currency to princes | 1 duke per 5 princes |

Sheet fields: Money on-hand, Money in bank.

### 5.2 Melee weapons (p.74–75)

| Size | Definition | AP | DC | Hands | Target | Specialty skill hint |
|---|---|---|---|---|---|---|
| Unarmed | no weapon; can't be augmented by armsmith | 1 | 2 (race mods!) | – | adjacent | Brawl |
| Light | fits in pocket; concealable; all small items count | 2 | 4 | 1 | adjacent | Espionage |
| Medium | one-handed, not concealable | 2 | 6 | 1 | adjacent | Swashbuckling |
| Heavy | two-handed | 2 | 8 | 2 | adjacent | Overpower |
| Super-Heavy | two hands to carry and swing; needs **Footing** stance (1 AP; no other stance while in footing) | 2 | 10 | 2 | adjacent | – |

Super-heavy without footing: −3 Accuracy and Strike (as impromptu).

**Variants (stackable, each penalty applies):**

| Variant | Effect | Allowed on |
|---|---|---|
| Flexible | can make grabs (whip, chain, flail); −1 DC | any |
| Polearm | +5 ft reach (attack within 10 ft); −1 DC | medium and heavier |
| Throwing | can be thrown; −1 DC. Throw range: Light 25 ft, Medium 75 ft, Heavy 50 ft; −1 Acc per 10 ft beyond. Non-throwing weapons max 25 ft. A thrown weapon counts as **not melee** for specialties. | any |
| Impromptu | not designed as weapon; narrator assigns size class; −3 Acc and Strike | – |

Examples: flexible polearm = −2 DC, reach 10 ft, can grab; bolas = throwing + flexible.

Standard reach: adjacent (5 ft); polearm 10 ft.

### 5.3 Firearms (p.76–77)
**Firearms use Accuracy for damage:** one roll — Accuracy vs Evade to hit, then tier the same Accuracy result for damage (Strike is not used). Must be readied between shots.

| Size | AP to fire | DC | Hands | AP to ready | Base range | Range increment (−1 Acc each) |
|---|---|---|---|---|---|---|
| Light | 2 | 2 | 1 | 0 | 50 ft | 10 ft |
| Medium | 2 | 4 | 1 | 1 (one-handed) / 0 (two hands) | 100 ft | 25 ft |
| Heavy | 2 | 6 | 2 | 1 | 200 ft | 50 ft |
| Super-Heavy | 2 | 8 | 2 | 2 | 300 ft | 100 ft |

Super-heavy needs Footing; without it −3 Accuracy.
**Double-barreled** (no extra cost): fire twice before readying; reloading +1 AP per round loaded.

**Ammunition** (swap type: 1 AP):

| Ammo | Effect |
|---|---|
| Cartridge | base stats |
| Blank | no projectile |
| Shot | no accuracy loss with range; instead −1 DC per range increment beyond base |
| Sniper cartridge | −1 Acc per **2** range increments; −1 DC |
| High damage cartridge | +2 DC; +1 AP readying time |

### 5.4 Bows (p.78)
Bows use Accuracy to hit and **Strike** for damage (normal). Always two hands. No readying.

| Size | AP | DC | Base range | Increment |
|---|---|---|---|---|
| Light (incl. slingshots) | 2 | 3 | 25 ft | 10 ft |
| Medium | 2 | 5 | 50 ft | 10 ft |
| Heavy | 3 | 7 | 75 ft | 25 ft |
| Super-Heavy | 3 | 9 (wielded as heavy weapon) | 200 ft | 75 ft |

Super-heavy bow needs Footing; without −3 Accuracy.

### 5.5 Crossbows (p.79)
Like firearms: **Accuracy determines damage** (single roll).

| Size | AP to fire | DC | Hands | AP to ready | Base range | Increment |
|---|---|---|---|---|---|---|
| Light | 2 | 3 | 1 | 1 | 25 ft | 10 ft |
| Medium ("pistol crossbow") | 2 | 5 | 1 | 1 | 50 ft | 10 ft |
| Heavy | 2 | 7 | 2 | 2 | 100 ft | 25 ft |
| Super-Heavy | 2 | 9 | 2 | 3 | 150 ft | 50 ft |

Super-heavy needs Footing; without −3 Accuracy.

### 5.6 Arrows & bolts (p.78–79)
Changing bolt type: 1 AP; changing arrow type: free.

| Type | Effect |
|---|---|
| Standard | base |
| Bladed | −2 Acc; 1 bleeding per tier of damage dealt |
| Hooked | removing costs 2 AP (normally 1); attach rope for 1 AP → climb/zip-line |
| Signal | very loud whistle; −1 DC |

### 5.7 Armor (p.80)
Soak works like damage class: `soak = Soak Class × Defense tier`.

| Type | Soak Class | Evade penalty | Speed penalty | Climb & swim penalty | Materials | Don time | Don with help | Price |
|---|---|---|---|---|---|---|---|---|
| Unarmored | 0 | 0 | 0 | 0 | none/organic/textile | – | – | – |
| Minimal | 1 | 0 | 0 | 0 | metal/organic/textile | 3 AP | – | 1 prince |
| Light | 2 | −1 | −5 ft | −5 ft | metal/organic/textile | 6 AP | – | 5 princes |
| Medium | 3 | −2 | −5 ft | −10 ft | metal/organic | 24 AP | 12 AP | 15 princes |
| Heavy | 4 | −3 | −10 ft | −15 ft | metal/organic | 3 min | 1 min | 40 princes |
| Super-Heavy | 5 | −4 | −10 ft | −20 ft | metal | 10 min | 3 min | 75 princes |

(Donning times verified against the page layout.)

### 5.8 Deflection items (p.81)
Deflect = 1 AP (interrupt) whenever attacked; adds bonus to that evade roll.

| Item | Evade bonus | vs | Notes | Materials | Price |
|---|---|---|---|---|---|
| Parrying Dagger | +3 | melee only | also counts as a light weapon | metal/organic/wood | 1 prince |
| Cloak | +3 | melee only | hand stays free, can make grabs | organic/textile | 1 prince |
| Shield | +4 | melee **and** ranged | can hold things in shield hand but then can't deflect | metal/organic/wood | 4 princes |

### 5.9 Animals (p.82–83)
Guide an animal: 1 AP per turn; it spends its own AP to move; shares your turn. Other actions: both you and it spend the normal AP cost.
Upkeep ≈ 1 duke/day.

| Animal | Cost | AP | HP | Wounds | Pri | Speed | Eva | Def | Soak (T1–T4) | Attack |
|---|---|---|---|---|---|---|---|---|---|---|
| Horse | 100 pr | 3 | 16 | 9 | +0 | 50 ft (×2 if all AP spent moving) | −1 | +1 | 3/6/9/12 (hide) | Hoof 2 AP, natural medium, Acc +0, Stk +1, dmg 6/12/18/24 |
| Canine | 35 pr | 3 | 12 | 8 | +0 | 40 ft | +0 | +0 | 2/4/6/8 (hide) | Bite 2 AP, natural medium, Acc +1, Stk +3, dmg 6/12/18/24; +1 Stk per ally within 25 ft with Pack Instincts; can move–attack–move |
| Bird of prey | 45 pr | 3 | 11 | 8 | +0 | 25 ft, 45 ft flight | +1 | +0 | 0 (unarmored) | Talon 2 AP, natural light, Acc +3, Stk +1, dmg 4/8/12/16; after 10+ ft dive target Brute resist vs Agility (+2) or prone |

| Animal | Skills | Attributes | Specialties / stories |
|---|---|---|---|
| Horse | Agility 2, Brawl 1, Overpower 1, Resilience 2, Shamanism 1 | Brute 3, Cunning 0, Dex 2, Spirit 1, Sci 0 | Gallop, Large; Four-Legged, Natural Armor. Mountable. Extra leg locations, no arms/hands. |
| Canine | Espionage 1, Frenzy 1, Resilience 1, Showmanship 2, Tactical 2 | Brute 2, Cunning 4 (+2 tracking scent, +2 on guard), Dex 1, Spirit 0, Sci 0 | Bounding Lunge, Howl (2 AP: allies within 25 ft +1/+2/+3/+4 Stk by Showmanship tier on next attack); Four-Legged, Guard, Natural Armor, Pack Instincts, Scent. Mountable by gnomes. |
| Bird of prey | Ace 1, Agility 2, Espionage 2, Resilience 1, Tactical 1 | Brute 1, Cunning 3 (+10 noticing), Dex 3, Spirit 0, Sci 0 | Death from Above, Thermal Gliding (stance: double flight speed); Eagle Eye, Innate Sense of Direction, Small, Wings. Wings = leg locations. |

### 5.10 Equipment – Adventuring Basics (p.84–85)
Starting characters may take anything reasonable from this list for free.

| Item | Price | Item | Price |
|---|---|---|---|
| Backpack | 2 dukes | Journal | 3 dukes |
| Bedroll | 1 duke | Ladder (10 ft) | 2 dukes |
| Cable (25 ft, metal) | 5 princes | Lantern (light 25 ft) | 2 dukes |
| Case (2 scrolls/maps) | 1 duke | Lockpicks | 3 dukes |
| Chain (10 ft) | 1 prince | Magnifying Glass | 1 prince |
| Chalk | 1 duke | Metal Canister | 4 dukes |
| Charcoal | 1 duke | Musical Instrument | 2 princes |
| Chest | 1 prince | Pole (5 ft, steel) | 5 dukes |
| Clothing (working) | 3 dukes | Pole (5 ft, wood) | 1 duke |
| Clothing (middle-class) | 1 prince | Rope (25 ft) | 4 dukes |
| Clothing (gentry) | 5+ princes | Rations (1 day) | 2 dukes |
| Crowbar | 1 prince | Spyglass | 10 princes |
| Flare | 10 princes | Tent | 2 princes |
| Glass Bottle | 1 duke | Torch | 1 duke |
| Grappling Hook | 3 princes | Vials (set of 5) | 3 dukes |
| Hose (10 ft) | 10 princes | Inkpen | 1 duke |

### 5.11 Weapon & armor prices (p.85)

| Weapon | Price | Weapon | Price |
|---|---|---|---|
| Light melee | 1 prince | Light bow | 5 dukes |
| Medium melee | 7 princes | Medium bow | 1 prince |
| Heavy melee | 15 princes | Heavy bow | 5 princes |
| Super-heavy melee | *not listed* | Super-heavy bow | 17 princes |
| Light firearm | 2 princes | Light crossbow | 2 princes |
| Medium firearm | 5 princes | Medium crossbow | 4 princes |
| Heavy firearm | 12 princes | Heavy crossbow | 7 princes |
| Super-heavy firearm | 20 princes | Super-heavy crossbow | 14 princes |

Armor/shield prices: see §5.7 and §5.8.

### 5.12 Items for sale (p.86–87, brand items)

| Item | Price | Effect | Tags |
|---|---|---|---|
| Elympia Dark (lager) | 4 pr/glass, 40 pr/bottle (10 glasses) | One of the most popular drinks in Evangless, this satyr-brewed dark lager never fails to pick one’s spirits up. It’s rich flavor re- stores 4 hit points per glass. A bottle contains 10 glasses worth. It costs 1 AP per glass to drink. Please drink responsibly. | `[ACTION]` |
| CRIMSON (clothing line) | 30 pr | by Crimson Marshal Lucinda Mirasol This controversial fashion line by the infamous Evanglessian militarist didn’t get its name simply for its creator’s rank; each piece cannot be caught on tier 1 fire! This clothing counts as minimal armor and is guaranteed to look downright dashing in every season. | `[GEAR] armor=minimal` |
| Mindcuffs | 3 pr | Developed by the Dolby Home for the Scientifically Unstable, these handcuffs can be used for one action point grabs. Attach- able to a maximum of two body parts, any hands or legs grabbed become unusable. Perfect for keeping any doomsday-machine obsessed evil genius unable to build, the target can only free a body part by making a tier 2 brute resist or by the cuffs’ owner releasing them. | `[ACTION]` |
| Water Filter | 15 pr | An essential gadget for safari hunters and desert scavengers alike, this handy tool attaches to any flask or bottle. Simply by tipping it over you will pour out any impurities leaving only the cleanest of water behind. It can be used 15 times before breaking and is concealable. | `[NARR]` |
| Any-Altitude Parachute | 4 pr | This state-of-the-art parachute by Spendo deploys quickly for one reflexive action point whenever you’re falling. Never take falling damage again! While not concealable, its multi-stage deployment process ensures it will protect whether you fall 5 feet or 500 feet! SPENDO-BRAND: 91.6% GUARANTEED! | `[REFLEX]` |
| Spendo-Grenade | 3 pr | Sometimes you just have to blow something up. Spendo under- stands. That’s why he created the Spendo-Grenade. This conceal- able bomb is a statuette of Spendo the gnome himself (if Spendo smelled like gunpowder, had dark green skin and clothes, and made ticking sounds like a bomb). It costs 1 action point to ac- tivate the bomb and 2 action points to throw it. It will explode at the beginning of your next turn. It deals 10 damage to everyone in your target square and all squares adjacent to it. People in those squares can spend 1 action point to attempt a resist the impending explosion with their Dexterity. If they recieve a tier 2 result or higher, they take no damage and move out of the blast range. SPENDO-BRAND: 91.6% GUARANTEED! | `[ACTION]` |
| Spendo-Brand Illumitorch | 2 pr | Whether you’re afraid of the dark or simply can’t see in it, Spen- do the gnome has the perfect fix! Torches are hot and can burn you; that’s dangerous! Use Spendo’s illumitorches instead! Eas- ily wielded in one hand and concealable, Spendo illumitorches consist of small hand-cranked bulbs which project light 25 feet around themselves. SPENDO-BRAND: 91.6% GUARANTEED! | `[NARR]` |
| The Lawn-Deformer (chainsaw) | 32 pr | Spendo brings you his newest product in his line of landscaping tools. Designed with vigilante gardeners in mind, this nifty chain- saw acts as a medium weapon. Whenever you successfully hit an opponent, you can spend an action point to deal 1 unsoakable damage to them by spinning the chainsaw blades. This can be done as many times as you have remaining action points during your current turn. SPENDO-BRAND: 91.6% GUARANTEED! | `[GEAR]` |
| Gas-Fabulous (gasmask) | 4 pr | Based on a design by the Coaldust Unions of Evangless, this handy gasmask gives its wearer a +4 to resists against alchemical gases. But you shouldn’t buy from them, oh no! Buy your gas- mask from Spendo and his hard-working artisans will customize the mask’s appearance for free! SPENDO-BRAND: 91.6% GUARANTEED! | `[COND]` |
| Protective Goggles | 10 pr | Spendo doesn’t like dirt in his eyes. Neither should you! These handy industrial goggles protect you from dirt and other things too! They grant you +1 to your soak class against called shots to your eyes and a +3 to Brute resists against anything that would affect your eyes. SPENDO-BRAND: 91.6% GUARANTEED! | `[COND]` |
| Grapple Gun | 6 pr | Perfect for the gentleman thief on the run, this grapple-gun can propel up to 50 feet of chain, rope, or cable and will attach to rocky, magnetic, rough, or slick surfaces. It will increase your climb speed by 20 feet while you retract the cord towards its latch. It costs 1 action point to shoot your grapple-gun, 1 action point to unlatch it, and 1 action point to retract it to climb. Just be wary, this trinket isn’t concealable. MaskedMen Inc. Unleash Your Inner Rogue! | `[GEAR]` |
| Chains of Security | 10 pr | Back by popular demand, Red-Gate Security is proud to present the Chains of Security! Attachable to any item, a single chain can secure an item to its owner’s hands, granting the wielder a +2 on resists against the item being disarmed. reD-gate: Keeping Evangless Safe | `[COND]` |
| Tinted Glasses | 10 pr | Standard-issue for the Evanglessian military police, these styl- ish pieces of eyewear art by Red-Gate Security protect your eyes from the harmful rays of the sun, as well as any flashes of light. Wearing them grants you a +3 to resist being blinded by flashes of light. reD-gate: Keeping Evangless Safe | `[COND]` |
| Heat-Sight Monocle | 10 pr | You’re in the middle of a barfight. Your chosen foe pushes a table on its side and ducks behind it. Your curiousity piques. What is he doing back there? With a Heat-Sight monocle from Masked- Men Incorporated, you could see his heat signature clear as day! This handy monocle allows you to see heat through anything deemed poor cover. MaskedMen Inc. Unleash Your Inner Rogue! | `[COND]` |
| Hidden Intentions (poison) | 8 pr/dose | At MaskedMen Incorporated, we believe subtlety is the greatest weapon in any gentleman’s arsenal. Simply add a dose of Hid- den Intentions to your target’s food or drink. Requiring a Tier 3 Cunning resist to detect the added ingredient in their meal, your target will take 6 unsoakable damage roughly 6 seconds or three action points after they ingest it. MaskedMen Inc. Unleash Your Inner Rogue! | `[ACTION]` |
| Reasonable Doubt (auto lockpick) | 8 pr | The premier product of MaskedMen Incorporated, this automat- ed lockpicking device keeps the lock fingerprint-free. It spends 1 action point lockpicking any lock it’s attached to whenever your action points refresh. One-handed and concealable, you can place it on a lock for 1 action point or throw it at a lock for 2 action points. MaskedMen Inc. Unleash Your Inner Rogue! *Though there are some rumors concerning the legitimacy and morality of MaskedMen Incorporated, all of their agents have been very forthright with us and leave us no reason to question the validity of their company. | `[ACTION]` |
| Graviton Board | 85 pr | A small hoverboard perfect for anyone wanting to travel in style, this premium clanker by Burgenhind Industries may not fly through the air, but it quickly skims across land and the surface of water! With a speed of 40 feet per action point and 12 wounds (losing 5 feet of speed whenever it takes damage), you’ll be the envy of all pedestrians in your path! Burgenhind Industries: Need a Lift? | `[GEAR] vehicle` |
| The Fashionable Arrival (flight pack) | 3,200 pr | The latest in personal transportation clankers by Burgenhind Industries, this graviton-sphere powered pack features a stylish brass finish and fits comfortably on the back of any tailcoat or corset. For every action point you spend moving it, the Fashion- able Arrival will fly up to 40 feet. It has 12 wounds and loses 5 feet of movement whenever damaged. If you aren’t arriving fashion- ably, why show up at all? Burgenhind Industries: Need a Lift? | `[GEAR] Fly 40` |

---
## 6. Specialties (Ch. 6–10, p.88–263; bonuses from Appendix p.279–285)

### 6.1 How specialties work
- **Eligibility:** you need ≥1 point in the specialty's skill (General Science specialties: any Science). Extra requirements are in the *Requires* column (skill points, other specialties, stats such as "+4 Strike" = total Strike bonus from specialties).
- **Bonuses:** each specialty adds its fixed combat-stat bonuses (the 10 sheet columns) **once, when learned**, regardless of whether the effect is used. These are the numbers the tool sums.
- **Groups** (e.g. *Bone-Breaking Specialties*) are thematic trees printed under the skill; usually later members require earlier ones.
- **Cost notation:** `Attack +X AP` = add to a normal attack (different modifiers stack on one attack, same one only once); `Stance` = 1 AP to enter, one stance at a time (exceptions: Resolute, Adaptable, Master of Forms, Shifting); `reflexive` = out of turn from next turn's pool; "2 AP to begin, 1 AP/turn" = maintained effect.
- **Tier tables:** "T1 a / T2 b / T3 c / T4 d" means: roll d12 + **points in that specialty's skill**, tier the result, apply the matching value. Resist notes: *negates* = resist beats your roll → no effect; *tiers down* = each resist tier above T1 lowers the effect by one tier; *marques down* = same for augment marques.
- **"Scale" formulas** use skill points (not attribute). `floor()` = round down.
- See the tag legend in §0.2. The Effect column holds the book text after running `add_book_texts.py`.

### 6.2 Specialty count per skill

| Attribute | Skill | Specialties |
|---|---|---|
| Brute | Brawl | 21 |
| Brute | Frenzy | 21 |
| Brute | Overpower | 20 |
| Brute | Resilience | 22 |
| Cunning | Espionage | 22 |
| Cunning | Expertise | 22 |
| Cunning | Showmanship | 23 |
| Cunning | Tactical | 22 |
| Dexterity | Ace | 23 |
| Dexterity | Agility | 21 |
| Dexterity | Marksmanship | 22 |
| Dexterity | Swashbuckling | 23 |
| Spirit | Faith | 23 |
| Spirit | Grace | 20 |
| Spirit | Luck | 22 |
| Spirit | Shamanism | 23 |
| Sciences | General (Sciences) | 2 |
| Sciences | Alchemy | 19 |
| Sciences | Armsmith | 21 |
| Sciences | Automata | 22 |
| Sciences | Bio-Flux | 19 |
| Sciences | Engineer | 15 |
| Sciences | Gadgetry | 14 |
| | **Total** | **462** |

### 6.3 Brute specialties

**What anyone can do with Brute (attribute uses):** Breath Holding (Brute tier → 15/30/75/200 turns with a last breath; 5/10/20/40 if surprised) · Difficult Lifting (T1 barely, drop after 3 turns, can't move; T2 move +2 AP, 10 turns; T3 move +1 AP, 30 turns; T4 no problem; weight penalties: large rock −3, tree −6, automobile −9, house ceiling −12) · Forceful Intimidation (1 AP, resist Brute or Spirit tiers down; T2/T3/T4 → target can't spend its next 1/2/3 AP against you; one intimidation at a time) · Hold (opposed Brute; defender loses ties) · Pulling (T1 move +3 AP, T2 +2, T3 +1, T4 as a move)

#### Brawl

| Specialty | Group | Bonuses | Cost / type | Requires | Effect | Tags |
|---|---|---|---|---|---|---|
| **Block with a Grab** |  | Acc +1, Eva +1, HP +10 | 0 AP reflexive |  | Cost: 0 AP reflexively<br>When your opponent throws their punch at you, you don’t just block their fist: you grab hold of it. Whenever you successfully evade an attack by an opponent who is within your reach and you are able to grab them, you may automatically (and for 0 action points) attempt a grab upon their hand (or, if they attacked you with a different body part, the grab will be upon that location). | [REFLEX] |
| **Dirty Fighting** |  | Acc +1, Stk +2, HP +9 | Stance |  | stanCe (costs 1 AP to enter)<br>You’re an expert at hitting where it hurts and causing the opponent to flinch. While you are in this stance, every time your opponent fails to resist one of your called shots, they open themselves to reflexive attacks from those adjacent to them. The reflexive attacks cost the normal amount of action points from those who decide to take the opportunity. Since you caused it, you cannot make a reflexive attack from this. | [STANCE] |
| **Drunken Boxing** |  | Acc +1, Eva +1, HP +9 | Called shot +1 AP |  | Cost: Called Shot +1 AP<br>When you make a called shot, it’s so wild and unpredictable that it’s difficult to evade. When you make a drunken called shot (whether you’re sober or not), you roll your die to determine the called shot location randomly. By doing this, you give yourself a bonus to your accuracy equal to your skill in Brawl. | [ATTACK+1] [SCALE:Brawl] Acc +Brawl |
| **Fisticuffs** |  | Stk +2, Pri +1, HP +10 | Stance (needs a free hand) |  | stanCe (costs 1 AP to enter)<br>Bare-knuckle boxing is your forté. When you enter this stance, you are ready to do some serious damage using just your fists. You can only be in this stance if you have at least one hand not holding anything. While in this stance, your unarmed attacks are one damage class higher, plus an additional damage class per 6 skill points you have in Brawl.<br>So, if you have 12 points in Brawl, while you’re in this stance, your unarmed attack would have a damage class of 5 (2 normally, plus 1 for the stance, plus an additional 2 for the 12 points you have in Brawl). | [STANCE] [GEAR] [SCALE:Brawl] unarmedDC += 1 + floor(Brawl/6) |
| **Fluid** |  | Eva +2, Stk +1, HP +7 | 1 AP reflexive |  | Cost: 1 AP reflexively<br>You control all those who attack you. Any time an adjacent opponent attacks you but you successfully evade, you may spend 1 action point reflexively to move your attacker into any adjacent, unoccupied space that has solid, non-lethal ground for them to stand upon. | [REFLEX] |
| **Grapple** |  | Acc +2, Stk +1, HP +10 | Stance (must be grabbing) |  | stanCe (costs 1 AP to enter)<br>Once you grab somebody, you can turn it into a full on grapple, shutting down their ability to move and making it difficult for them to take any actions. You must be grabbing somebody to enter a grapple stance, and you can only stay in this stance while grabbing that person (thus, if they resist, you are knocked out of stance). Anything that would let them break free of the grab will automatically knock you out of this stance. When you switch your grab to a grapple, you are no longer grabbing a single location - instead, you are now grappling their entire body. (For the purposes of other specialties, however, it still counts as a grab.) A person who is grappled by you cannot move, just like being grabbed. If they try to take any action, they suffer penalties on every roll they make. Any time a grappled opponent rolls their die (except for random rolls), roll your Brawl, tier the results, and give them the corresponding penalty to their roll.<br>-3 on the roll<br>-6 on the roll<br>-9 on the roll<br>-12 on the roll | [STANCE] [SCALE:Brawl-tier] |
| **Heavy-Handed** |  | Stk +2, Pri +2, HP +9 | Unarmed attack +1 AP |  | Cost: Unarmed Attack +1 AP<br>The blows from your unarmed attacks are so powerful that they feel like they’re coming from giant hammers. When you make a heavy-handed attack, roll your brawl before you deal damage but after you’ve succeeded in your accuracy roll in order to increase the damage class that you deal.<br>+3 damage class<br>+4 damage class<br>+5 damage class<br>+6 damage class | [ATTACK+1] [SCALE:Brawl-tier] |
| **Hold Steady** |  | Acc +1, Eva +1, HP +10 | Passive |  | You’ll grab the bloke while your friends beat the tar out of him. When you’re grabbing somebody, anybody who attacks that person gains a hefty accuracy bonus. They get +3 on their accuracy roll, +1 for every 4 skill points you have in Brawl (being a +4 at 4 points, a +5 at 8 points, and so forth). | [COND] [SCALE:Brawl] ally Acc = 3 + floor(Brawl/4) |
| **Knock Aside** |  | Acc +1, Eva +1, HP +9 | Deflect (1 AP reflexive) |  | Cost: Deflect (1 AP reflexively)<br>With a swift knock, you can push aside an attack with the sheer force of your body. You may reflexively deflect attacks from melee weapons, bows, or thrown weapons with your bare hands. When you use such a deflection, you gain a bonus to your evade of +3, plus an additional +1 per 8 skill points you have in Brawl (for +4 at 8 skill points, +5 at 16 skill points, and +6 at 24 skill points). | [REFLEX] [SCALE:Brawl] deflect Eva = 3 + floor(Brawl/8) |
| **Monkey Wrestler** |  | Acc +1, Stk +1, HP +10 | Passive | 5 Brawl | reQuires: 5 skill points in Brawl<br>You wrap your legs around their torso, sink your teeth into their arm, grab their face, wrap your elbow around their eyes, and you still have a spare hand to use your dagger. For every 5 points you have in Brawl, you may grab an additional location on a person. Normally you can only grab two locations (assuming you have two hands). You may choose not to use your hands to initiate a grab if you have enough points to do so. | [PASSIVE] [SCALE:Brawl] |
| **Reversal** |  | Acc +1, Eva +1, HP +10 | 2 AP reflexive |  | Cost: 2 AP reflexively<br>The only person who’ll be doing the grabbing in this fight is you. If someone successfully grabs you, you can attempt to reverse the grab and capture your captor. Re-roll your resist for your opponent’s grab, but add your skill in Brawl to the roll. If you succeed, they must roll a resist against your Brawl to avoid getting grabbed on a called-shot location of your choice. | [REFLEX] [SCALE:Brawl] |
| **Shrug Away** |  | Eva +1, Pri +2, HP +10 | Passive (free) |  | Let’s just say that you don’t like being touched. If you are successfully grabbed, you may immediately make another resist (at no action point cost) with your Brawl skill added to the attribute you’re using to resist. | [COND] [SCALE:Brawl] |
| **Throat Jab** |  | Stk +2, Pri +2, HP +11 | Called shot to neck, reflexive; resist Brute (negates) |  | resist: Brute (negates)<br>Cost: Called Shot to the Neck reflexively<br>If anybody adjacent to you begins to speak, you can make a called shot to their neck reflexively in order to shut them up. If they fail on their resist, they cannot talk or use their voice (including using specialties that rely on speaking, like Encouragement) until they either spend 1 action point to clear their throat or they wait until the end of their next turn. | [REFLEX] |
| **Bone-Breaker** | Bone-Breaking | Stk +2, Pri +1, HP +11 | Unarmed called shot +1 AP |  | Cost: Unarmed Called Shot +1 AP<br>You smash a precision blow into the opponent, causing a called shot that’s nearly impossible to resist. Do your called shot normally. If they succeed in resisting, you are able to roll your strike again to make them re-resist. The bone-breaker only does damage based on the original strike.<br>1 re-roll<br>2 re-rolls<br>3 re-rolls<br>4 re-rolls | [ATTACK+1] |
| **Crippling Blow** | Bone-Breaking | Stk +3, Pri +1, HP +9 | Bone-breaking attack +1 AP per location | Bone-Breaker; 8 Brawl | reQuires: Bone-Breaker specialty, 8 skill points in Brawl Cost: Bone-Breaking Attack, +1 AP per location<br>Your bone-breaking attack reverberates through the victim, crippling much of their body. When you make your bone-breaking attack, you may spend an extra action point in order to have the same bone-breaker effect against another called shot location. You may affect as many called shot locations as you’d like - each one costs 1 additional action point.<br>So, say you make a bone-breaker attack against a person’s neck. You get a tier 3 on your bone-breaker, so they have to make (a ridiculous) 4 resists in order to not be effected. In addition, you spend 2 extra action points to activate the called shot effects for the torso and the hand, which now also require 4 resists to avoid. | [ATTACK+X] [REQ] |
| **Combo Flow** | Combo | Acc +1, Stk +2, HP +10 | Passive | 4 Brawl | reQuires: 4 skill points in Brawl<br>You rage like rapids, following the path of least resistance. Every melee attack that you land during a turn grants you a +2 on accuracy and strike rolls for the rest of your turn, and this bonus accumulates with every successful melee attack until the end of your turn.<br>So, if you landed one melee attack, your next attack would have a +2 on accuracy and strike. After your second successful attack, the third one would have a +4 on accuracy and strike. This would continue to grow with every successful attack. | [COND] [SCALE:hits] |
| **Combo Opener** | Combo | Acc +1, Stk +2, HP +10 | Unarmed attack +1 AP | Combo Flow | reQuires: Combo Flow specialty<br>Cost: Unarmed Attack +1 AP<br>You may perform a combo opener in order to improve the potency of your combo flow. If you successfully land your combo opener (which for most purposes just looks like a normal unarmed attack), it might count as having successfully landed multiple attacks.<br>Counts as two attacks (granting a +4 on accuracy and strike for the next attack).<br>Counts as three attacks (granting a +6 on accuracy and strike for the next attack).<br>Counts as four attacks (granting a +8 on accuracy and strike for the next attack).<br>Counts as five attacks (granting a +10 on accuracy and strike for the next attack). | [ATTACK+1] [REQ] |
| **Combo Breaker** | Combo | Acc +1, Eva +1, HP +9 | Free | — | Any time an adjacent opponent successfully damages you with two separate attacks in one turn, you may perform a combo breaker - a free unarmed attack against your assailant that uses your skill in brawl in place of your accuracy. | [REFLEX] [SCALE:Brawl] |
| **Finisher** | Combo | Stk +3, Pri +1, HP +9 | Free | Heavy-Handed | reQuires: Heavy-Handed specialty<br>If you successfully make two unarmed attacks in one turn and still have an additional action point, you can make a finisher. A finisher is just like a heavy-handed attack, except that it does not cost the extra action point to perform. | [COND] [REQ] |
| **Crushing Grip** | Grip | Stk +3, Pri +1, HP +10 | Passive | +4 Strike | reQuires: +4 Strike<br>Your grabs are vicious, crushing the opponent. When you make a grab, you also deal damage as if you were attacking with the attack normally. | [PASSIVE] [REQ:Stk≥4] |
| **Twist** | Grip | Acc +1, Stk +2, HP +10 | 1 AP | Crushing Grip | reQuires: Crushing Grip specialty<br>Cost: 1 AP<br>Once you have a person grabbed with a hand, you may twist that location to inflict pain. For 1 action point, you may automatically deal damage as per an unarmed attack (without the need to roll accuracy and evade). You may also, for 1 action point, activate the called shot that you have grabbed, rolling strike solely to determine the necessary resist but otherwise doing no damage. Though this does deal damage, it does not act as an attack. | [ACTION] [REQ] |

#### Frenzy

| Specialty | Group | Bonuses | Cost / type | Requires | Effect | Tags |
|---|---|---|---|---|---|---|
| **Adrenaline Surge** |  | Eva +1, Stk +1, HP +14 | Passive |  | The deaths of your opponents sends a reinvigorating rush through your body that pushes you to continue fighting. Whenever you deal a fatal effect or kill an opponent, you regain some of your hit points.<br>Immediately regain 3 hit points<br>Immediately regain 6 hit points<br>Immediately regain 9 hit points<br>Immediately regain 12 hit points | [COND] |
| **Backlash** |  | Acc +1, Stk +2, HP +11 | 1 AP reflexive | 7 Frenzy | reQuires: 7 skill points in Frenzy<br>Cost: 1 AP reflexively<br>Large amounts of damage don’t stop you - rather, they enrage you! Any time you take 10 or more damage (after damage soak), you can make a reflexive attack against your assailant using your skill in frenzy in place of your accuracy. This reflexive attack only costs you 1 action point to make. | [REFLEX] [SCALE:Frenzy] |
| **Burning Revenge** |  | Stk +3, Pri +1, HP +11 | 1 AP reflexive |  | Cost: 1 AP reflexively<br>Your foe drives you to greater strength. If an opponent damages you, you may “collect” that damage in order to add it as a bonus on your next strike roll against that opponent. When you are hit, you may spend 1 action point reflexively to savor the damage (after damage soak). The next time you attack that opponent, you gain the damage as a bonus on the strike roll. | [REFLEX] |
| **Carry Through** |  | Acc +1, Stk +2, HP +10 | Melee attack +1 AP per extra foe |  | Cost: Melee Attack +1 AP per adjacent opponent<br>You carry your blow through one opponent and into another. Once you’ve successfully attacked one opponent within your melee reach, you may continue the attack, cleaving through more opponents within your reach. For every additional opponent you choose, you must spend 1 more action point. You may not select the same opponent twice. You must still roll accuracy to determine if you hit, but you deal the same amount of damage that you dealt with the first attack.<br>If you were using any other modifying specialties (that would make it an “Attack +1 AP”), they only apply to the first target. | [ATTACK+X] |
| **Crimson Weapon** |  | Stk +3, Pri +1, HP +10 | Melee attack +1 AP; resist Brute (tiers down) |  | resist: Brute (tiers down)<br>Cost: Melee Attack +1 ap<br>You learn to make your weapon strike slice deep into the flesh of your foes. If an opponent takes damage from your crimson weapon, they will begin bleeding at the start of their next turn (and ever turn thereafter). Bleeding damage is unsoakable, but the opponent can roll their Brute to lower the tier result. A person can stop 10 points worth of bleeding by spending 1 action point patching the wound.<br>Bleed for 2 damage per turn<br>Bleed for 4 damage per turn<br>Bleed for 6 damage per turn<br>Bleed for 8 damage per turn | [ATTACK+1] |
| **Fray Fighter** |  | Eva +1, Stk +2, HP +10 | 3 AP |  | Cost: 3 ap<br>An angry mob of slobbering beasts stare you down, looking to rip you apart piece by piece. For you, this is just another day at work. Using a heavy or smaller melee weapon, you can engage the fray. Roll your tier to determine how many opponents adjacent to you that you hit. They are allowed to roll defense against the attacks.<br>Tier 1 damage to 2 adjacent opponents<br>Tier 1 damage to 3 adjacent opponents<br>Tier 1 damage to 4 adjacent opponents<br>Tier 1 damage to all adjacent opponents | [ACTION] |
| **Hundred Strikes** |  | Acc +1, Stk +2, HP +10 | All AP of the turn (must be at max) |  | Cost: All of the AP you can spend in a single turn When you choose to use your hundred strikes ability, you must still have your maximum amount of action points for the turn and be wielding a heavy or smaller melee weapon. You designate a single adjacent opponent as the target of your hundred strikes. For one action point apiece, you can make a melee attack against that opponent. After every attack, you and the target move a single space. The target chooses which space he will move into, and you must either follow or forego the rest of your turn. | [ACTION] |
| **Liberator** |  | Eva +2, Stk +2, HP +10 | 1 AP reflexive |  | Cost: 1 AP reflexively<br>You don’t like being touched, held, grabbed, or grappled. Whenever you are grabbed, you can make a melee attack called shot against the person grabbing you in whatever way is going to get them off (often by making a called shot against their hand, but you can also make a called shot against their torso to push them away, or a called shot against whatever else they’re using to grab you). You can do this reflexively when they first grab you, and, if you fail, you can continue to make these melee called shots against your assailant for just 1 action point until they let go. | [REFLEX] |
| **Merciless** |  | Acc +1, Stk +2, HP +8 | Stance (can't voluntarily exit) |  | stanCe (costs 1 AP to enter)<br>Once you go down this path, there’s no going back. Once you enter your merciless stance, you cannot voluntarily exit it. Upon entering, you choose a target of the stance. As long as you are aware of the target or believe the target to be within a couple hundred feet, you cannot exit your stance. While in this stance, you can only attack your target and people who are directly preventing you from getting to your target. If you are not engaged with your target, you must spend at least 1 action point every turn moving toward your target.<br>While this stance is active, once per turn you may use your skill in frenzy as a bonus to any one of your combat rolls, or divide it among several. For example, you may add your skill in frenzy to one strike roll, or you may give half of your skill in frenzy to one accuracy roll and the other half to one evade roll. These combat rolls must be made in opposition of the target of your merciless stance. | [STANCE] [SCALE:Frenzy] |
| **Neverending Bloodbath** |  | Stk +2, Spd +5, HP +11 | Passive |  | For every enemy you kill during your turn, you gain 1 action point that can only be used for running toward another enemy. | [COND] |
| **No Escape** |  | Stk +2, Spd +5, HP +10 | As moving, reflexive |  | Cost: As Moving, reflexively<br>Though your enemies may attempt to retreat, you’re prepared to give chase. Any time a foe that you’re engaged with attempts to move away from you using their land speed, you reflexively follow them. If an opponent’s speed is greater than yours (but within 20 feet), you rise to the challenge and match their speed. | [REFLEX] |
| **Raging** |  | Stk +2, Pri +2, HP +9 | Stance |  | stanCe (costs 1 AP to enter)<br>Nothing can stop you. You will destroy everything in your path. When you make an attack while raging, you pull your bonuses from your accuracy, evade, and defense in order to add them to your strike roll. Add your accuracy, evade, and defense bonuses together and apply that number as a bonus to your strike. While in this stance, however, you do not gain any bonuses on your accuracy, evade, or defense rolls. If you leave this stance (either voluntarily or by being forced out of it), you do not gain your bonuses to evade and defense back until the end of your next turn. | [STANCE] [STAT:Stk += Acc+Eva+Def; Acc/Eva/Def → 0] |
| **Straining Blow** |  | Acc +1, Stk +2, HP +13 | As melee attack |  | Cost: as a Melee Attack<br>You push yourself to your maximum, destroying yourself in order to lay waste to your opponents. When you make a straining blow, you may deal 5 unsoakable hit point damage to yourself in order to add a +1 damage class to your attack. You may deal as much damage to yourself as you’d like in order to gain additional damage classes, but you cannot deal more damage to yourself than you have hit points. Once you are out of hit points, you cannot deal straining blows. | [ATTACK+0] |
| **Soulless Blade** |  | Acc +1, Stk +2, HP +9 | 2 AP reflexive |  | Cost: 2 AP reflexively<br>When you mean to finish an opponent, you do so mercilessly. After you’ve made a melee attack that deals wounds damage to the target, you may spend 2 action points reflexively in order to convert it into a soulless blade. Now, instead of rolling on the wounds chart, they roll for a fatal effect. | [REFLEX] |
| **Walking Destruction** |  | Stk +3, Spd +5, HP +10 | Move + melee attack + 2 AP | 15 Frenzy | reQuires: 15 skill points in Frenzy<br>Cost: Move + Melee Attack + 2 AP<br>You make a single move. During this move, you may attack anybody that you become adjacent to. You may not target the same person more than once.<br>Other specialties cannot be applied to this attack. | [ACTION] [REQ] |
| **Berserker** | Bloodlust | Acc +1, Stk +2, HP +12 | Stance |  | stanCe (costs 1 AP to enter)<br>The sight of blood excites you. After successfully dealing damage to an opponent, you a gain +1 damage class against that opponent with all melee weapons. This bonus increases by +1 for every 6 skill points you have in frenzy. This bonus can be used against multiple opponents. | [STANCE] [SCALE:Frenzy] DC += 1 + floor(Frenzy/6) |
| **Bloodlust** | Bloodlust | Acc +1, Stk +2, HP +10 | +1 AP when entering Berserker | Berserker; 6 Frenzy | reQuires: Berserker specialty & 6 skill points in Frenzy Cost: 1 AP<br>In the whirling chaos of battle you are a singular force of destruction - relentless and unstoppable. When you enter into berserker stance, you may spend an additional action point to upgrade your stance and start bloodlusting. While bloodlusting, your damage class with melee weapons increases by 1 for every enemy within<br>25 feet of you.<br>This bonus replaces the normal bonus you would get from your berzerker stance. It is automatically added to all melee weapon attacks, regardless of whether you have attacked the foe before or not.<br>If you are knocked out of berserker stance, you must reenter the stance and spend the extra action point to begin bloodlusting again. | [STANCE] [REQ] [SCALE:enemies] |
| **Unquenchable Thirst** | Bloodlust | Acc +1, Stk +3, HP +11 | +1 AP after Bloodlust | Berserker, Bloodlust; 12 Frenzy | reQuires: Berserker & Bloodlust specialties & 12 skill points in Frenzy<br>Cost: 1 AP<br>Your unquenchable thirst for blood has become a full-fledged obsession. After you have entered your berserker stance and started bloodlusting, you may spend another action point to upgrade to unquenchable thirst. Now, everybody within 25 feet of you acts as an enemy (including allies) for the purpose of determining your bloodlust bonus. You may now make normal melee attacks (with a heavy weapon or smaller) for just 1 action point, but if anybody comes near you, enemy or ally, you are forced to make a reflexive melee attack against them, if at all possible.<br>If you are knocked out of berserker stance, you must re-enter the stance and spend the extra actions point to begin bloodlusting and enter unquenchable thirst again. | [STANCE] [REQ] [GEAR] melee AP=1 |
| **Laugh Like You're Crazy** | Masochistic | Stk +2, Pri +2, HP +10 | Passive; resist Spirit (negates) |  | resist: Spirit (negates)<br>Your a manic, psychotic, laughing vision of evil on the battlefield. For every 10 points of hit point damage you’ve taken, choose one opponent within 25 feet. That opponent is now suffering the effects of tier 1 fear. They may resist using their spirit against your frenzy. If they resist, they cannot be affected again until after their next breather. | [COND] |
| **Marriage to Suffering** | Masochistic | Stk +2, Wnd +1, HP +11 | Passive | Laugh Like You're Crazy | reQuires: Laugh Like Your Crazy specialty<br>When fighting on the edge, you fight even harder. When out of hit points, you gain a +1 damage class per point of wounds lost. This damage bonus is lost if your hitpoints are no long zero. | [COND] [SCALE:wounds lost] |
| **Seize Your Suffering** | Masochistic | Stk +2, Wnd +2, HP +11 | Passive | 8 Frenzy; Laugh Like You're Crazy; Marriage to Suffering | reQuires: 8 skill points in Frenzy, Laugh Like Your Crazy & Marriage to Suffering specialties<br>Taking punishment has become your nourishment on the battlefield. For every point of wounds damage you take, you gain an immediate action point. The action point only lasts for the turn the damage was taken. You may gain no more than 1 action point from this in a single turn than 1 per 8 skill points you have in Frenzy.<br>For example, if you take 3 wounds damage this turn, you gain 3 action points in addition to your normal allotment of action points for this turn. | [COND] [SCALE:Frenzy] |

#### Overpower

| Specialty | Group | Bonuses | Cost / type | Requires | Effect | Tags |
|---|---|---|---|---|---|---|
| **Brickbreaker** |  | Stk +3, Pri +1, HP +10 | As melee attack |  | Cost: as a Melee Attack<br>Through sheer force you are able to break through cover and bypass walls. Whenever an opponent is on the other side of cover, you may attempt to bypass it with your melee attack (they must still be within range of your melee weapon, however). You can only break through cover that is as strong as brick. A reinforced wall of iron could not be broken with brickbreaker, for instance. The cover is not destroyed from the brickbreaker attack, but it is damaged.<br>Bypasses poor cover<br>Bypasses light cover<br>Bypasses medium cover<br>Bypasses heavy cover | [ATTACK+0] |
| **Dragging** |  | Acc +1, Stk +2, HP +11 | Stance |  | stanCe (costs 1 AP to enter)<br>You pull your weapon behind you, letting your weapon take your entire body weight upwards when you swing. Anytime that you deal 10 or more damage (after damage soak), the enemy loses their stance. | [STANCE] |
| **Follow-Through** |  | Acc +1, Stk +2, HP +10 | Passive | 4 Overpower | reQuires: 4 skill points in Overpower<br>While your first attack can leave an opponent realing, your second attack is a true display of your power. If you make two consectutive and successful medium (or larger) melee attacks on your turn against the same opponent, your second attack’s damage is automatically one tier higher. | [COND] |
| **Heavy Hitter** |  | Acc +1, Stk +3, HP +9 | Stance | 4 Overpower | stanCe (costs 1 AP to enter)<br>reQuires: 4 skill points in Overpower<br>Whenever in this stance and using a heavy (or larger) melee weapon, add an extra point to your damage class for every 4 skill points you have in overpower. | [STANCE] [GEAR] [SCALE:Overpower] DC += floor(Overpower/4) |
| **Keep Them Down** |  | Acc +1, Stk +2, HP +11 | Heavy+ melee attack |  | Cost: Heavy (or larger) Melee Attack<br>When an opponent is next to you and prone, you have no problem finishing them off. Whenever attacking a prone opponent with a heavy weapon, your damage automatically tiers up one. | [COND] |
| **Monstrous Attacks** |  | Stk +3, Def +1, HP +10 | Super-heavy melee attack +1 AP |  | Cost: Super-Heavy Melee Attack +1 AP<br>Other people think that super-heavy melee weapons have a damage class of 10. You’re not sure what that means, but you know you can kill those people in one hit! By spending an extra action point when you make an attack with a super-heavy melee weapon, you deal considerably more damage. Your damage class increases by 2, plus an additional +1 per 6 skill points you have in overpower. | [ATTACK+1] [SCALE:Overpower] DC += 2 + floor(Overpower/6) |
| **No Quarter** |  | Stk +3, Pri +1, HP +11 | Heavy+ melee attack +1 AP; resist Dex (negates) |  | resist: Dexterity (negates, see below)<br>Cost: Heavy (or larger) Melee Attack +1 AP<br>You smash down, not targeting a single person, but their entire area. The only escape is for the target to move. When you make a no quarter attack, you are not attacking the person: you are attacking a single space. Anybody in this space is either automatically hit or must spend 1 action point reflexively in order to try to jump out of the space. If they choose to dodge, they roll their dexterity. If their dexterity exceeds your accuracy, they can move to 1 adjacent square. If it fails, you hit them. Note: If you are using any abilities that depend on the opponent’s evade, treat their dexterity as evade. If the opponent chooses not to dodge the attack, assume their evade matches your accuracy. | [ATTACK+1] |
| **One-Handing It** |  | Acc +1, Stk +2, HP +10 | Passive |  | You may wield two-handed weapons in one hand. Reloading a marksmanship weapon and using bows of any size still requires an additional free hand. For all purposes beyond how many hands the weapon requires, this specialty changes nothing. | [PASSIVE] [GEAR] |
| **Robust Toss** |  | Acc +1, Stk +2, HP +11 | Medium+ thrown attack |  | Cost: Medium (or larger) Thrown Attack<br>Just because your opponent is out of reach doesn’t mean you can’t smash their face in. Whenever you use a medium or larger thrown weapon, you may deal extra damage with the attack. If it lands, roll your overpower to determine its extra damage.<br>2 additional damage<br>4 additional damage<br>6 additional damage<br>8 additional damage | [ATTACK+0] |
| **Shield Whack** |  | Acc +1, Stk +3, HP +7 | Melee attack conversion |  | Cost: Melee Attack conversion<br>Most people use their shields for protection, keeping their shield in-between your weapon and their flesh. That’s an advantage that you’ll use. Whenever an opponent attempts to use a shield to deflect one of your attacks, you may instantly convert the attack into a shield whack. Though you’ll deal no damage with the attack, you hit the victim’s shield so hard that it staggers them, causing them to lose their stance, and they are disoriented for their next turn. | [REFLEX] |
| **Solid Assault** |  | Stk +3, Pri +1, HP +11 | Melee attack +1 AP |  | Cost: Melee Attack +1 AP<br>You ready your strike and bring it in smoothly to deal just the right amount of damage. If you successfully hit with your solid assault, you deal damage as though it were one tier higher. | [ATTACK+1] |
| **Stunning Blow** |  | Acc +1, Stk +2, HP +9 | Melee attack +1 AP; resist Brute (tiers down) |  | resist: Brute (tiers down)<br>Cost: Melee Attack +1 AP<br>With a well aimed strike, you stun your opponent. If the opponent fails to resist against your overpower and your receive a tier<br>2 result or higher, the target is stunned. The target may roll their brute in order to resist. For every tier over Tier 1 that they receive, they lower the effect of Stunning Blow by one tier. No effect<br>Stunned for 1 AP<br>Stunned for 2 AP<br>Stunned for 3 AP | [ATTACK+1] |
| **Titanic Strength** |  | Acc +1, Stk +3, HP +8 | Passive | 3 Overpower | reQuires: 3 skill points in Overpower<br>You lift the heaviest of weapons and swing them around as though they were tiny fencing blades. You do not need to enter into a footing stance when you use super-heavy melee weapons. | [PASSIVE] [GEAR] |
| **With Gusto** |  | Stk +3, Pri +1, HP +10 | Passive; resist Brute (negates) | +13 Strike | reQuires: +13 to Strike<br>resist: Brute (negates)<br>When you attack with gusto, your attack is so powerful that no armor can stand against it. If your melee attack deals tier 4 damage (or greater), you negate all of your opponent’s damage soak from their armor unless they can make their resist against your overpower. | [COND] [REQ:Stk≥13] |
| **Chipping Away** | Armor-Breaking | Acc +1, Stk +2, HP +10 | Heavy+ melee attack +1 AP; resist Dex (opposed, negates) |  | resist: Dexterity (tiers down)<br>Cost: Heavy (or larger) Melee Attack +1 AP<br>Your attacks wear on the opponent’s armor, slowly chipping it away until it falls apart. When you make a chipping away attack, you lower the soak class on the target’s armor by 1. The penalty can never send their soak class below zero, but chipping away does stack over time. If the armor’s soak class reaches 0, the armor is effectively destroyed (and any augments on it or bonuses that the target receives for wearing armor are negated). The opponent can negate the chipping away by making a dexterity roll opposed by your overpower roll.<br>Note: Somebody with broken or damaged armor can<br>patch it back together during a breather. | [ATTACK+1] |
| **Armor Sunder** | Armor-Breaking | Acc +1, Stk +2, HP +9 | Heavy+ melee attack +1 AP; resist Dex (tiers down) | Chipping Away | reQuires: Chipping Away specialty<br>resist: Dexterity (tiers down)<br>Cost: Heavy (or larger) Melee Attack +1 AP<br>The biggest obstacle between your sword and their heart is their armor, and you’re not beyond destroying that too. An armor sundering attack lowers the soak class on their armor. The penalty can never send their soak class below zero, but multiple armor sundering attacks can stack. If the armor’s soak class reaches 0, the armor is effectively destroyed (and any augments on it or bonuses that the target receives for wearing armor are negated).<br>-2 soak class<br>-3 soak class<br>-4 soak class<br>-5 soak class<br>note: Somebody with broken or damaged armor can patch it back together during a breather. | [ATTACK+1] [REQ] |
| **Earthquaking Strike** | Earth-Shattering | Acc +1, Stk +2, HP +11 | As heavy+ melee attack; resist Cunning (negates) |  | resist: Cunning (negates)<br>Cost: As a Heavy (or larger) Melee Attack<br>Rather than attacking the target, you attack the ground in front of the target, destroying the ground and destabilizing everyone around unless they can make the a cunning resist against your overpower skill.<br>The person standing in the area attacked is disoriented for one turn<br>Everyone within 5 feet of the area attacked is disoriented for one turn<br>Everyone within 5 feet of the area attacked is disoriented for two turns<br>Everyone within 10 feet of the area attacked is disoriented for three turns | [ATTACK+0] |
| **Rampant Destruction** | Earth-Shattering | Stk +3, Pri +1, HP +11 | Earthquaking Strike +1 AP | Earthquaking Strike | reQuires: Earthquaking Strike specialty<br>Cost: Earthquaking Strike +1 AP<br>With just a bit more effort, you can turn your earthquaking strike into rampant destruction. The effect of your rampant destruction is exactly the same, except this doesn’t just cause the ground around you to vibrate, it causes the ground to explode outward. Roll only once for the earthquaking strike as for the rampant destruction.<br>In the area struck, the ground is destroyed one foot down.<br>In the area effected, the ground is destroyed three feet down.<br>In the area effected, the ground is destroyed ten feet down.<br>In the area effected, the ground is destroyed twenty feet down.<br>note on CoLLapsing struCtures: This is especially effective while standing on a bridge, on the second floor of a building, or while out on the streets with a sewer underneath. Remember, however, that if you are in the area of the rampant destruction’s effect, you too will fall down. | [ATTACK+1] [REQ] |
| **Staggering Strike** | Push Away | Acc +1, Stk +2, HP +9 | Melee attack +1 AP; resist Brute (tiers down) |  | resist: Brute (tiers down)<br>Cost: Melee Attack +1 ap<br>Throwing yourself completely into the attack, you toss your opponent into the air like a rag doll. You knock them back several feet and potentially prone. The target may roll their brute in order to resist.<br>5 feet<br>10 feet<br>10 feet and prone<br>15 feet and prone | [ATTACK+1] |
| **Bullrush** | Push Away | Stk +2, Spd +5, HP +11 | Move + melee attack | Staggering Strike | reQuires: Staggering Strike specialty<br>Cost: Move + Melee Attack<br>When you charge at an opponent, you can throw them backwards. If you run toward an opponent in a straight line (for a minimum of 15 feet) and then make a melee attack, your melee attack is automatically a staggering strike.<br>If you so choose, you may also move with the target (staying adjacent to them) for the distance that you send them from the staggering strike. This extra movement has no cost. | [ACTION] [REQ] |

#### Resilience

| Specialty | Group | Bonuses | Cost / type | Requires | Effect | Tags |
|---|---|---|---|---|---|---|
| **Blast Proof** |  | Eva +1, Def +2, HP +14 | Shield deflection +1 AP reflexive; resist Cunning (tiers down) |  | resist: Cunning (tiers down)<br>Cost: Shield Deflection +1 AP reflexively<br>In the face of explosives, blasts, and storms, you raise your shield and carry on, shielding yourself and your allies from the blast. Whenever you are in the midst of an explosion or similar effect that has a blast area, you can negate the effect upon yourself and potentially adjacent spaces unless the originator of the effect resists against your skill in resilience.<br>Negates effect in your space<br>Negates effect in your space & 1 space behind you Negates effect in your space & 2 spaces behind you Negates effect in your space & 4 spaces behind you | [REFLEX] |
| **Body of Steel** |  | Def +3, Wnd +1, HP +14 | Passive |  | You’re armored training allows you to push past called shots. When an opponent attempts a called shot on you, you may add your defense to the resist against the called shot. | [COND] resist += Def |
| **Brace for Impact** |  | Acc +1, Def +3, HP +15 | As a shield deflection |  | Cost: as a Shield Deflection<br>Instead of attempting to evade the attack, you brace for impact. You may brace for impact at any time that you would normally be able to deflect a blow. Bracing for impact converts your evade bonus for deflecting into a defense bonus instead. | [REFLEX] |
| **Bulwark** |  | Eva +1, Def +2, HP +13 | Stance |  | stanCe (costs 1 AP to enter)<br>You ready yourself for any attack, becoming an untouchable bulwark. While in this stance, roll twice for your defense rolls and take the higher result. You still add your defense bonus to the roll of your choice. | [STANCE] |
| **Interposition** |  | Def +2, Spd +5, HP +13 | Move +1 AP reflexive; resist Dex (negates) |  | resist: Dexterity (negates)<br>Cost: Move +1 AP reflexively<br>You are able to gauge an opponent’s intent to strike a friend, allowing you to interpose yourself between them and one of your allies. You must decide to interpose yourself before your ally rolls their evade. For the cost of a move +1 action point, you may make a single move to place yourself in front of the attack. If the attack is a melee one, you must end your move adjacent to both the ally being attacked and to the person making the attack.<br>If the attack is a ranged one, you must end your move in-between your ally and the person making the attack. Furthermore, the person making the attack is allowed to resist against your resilience. If they successfully resist, the attack hits the intended target instead of you. If the resist fails, the attack automatically hits you. | [REFLEX] |
| **Metal Embrace** |  | Eva +1, Def +3, HP +15 | 1 AP reflexive |  | Cost: 1 AP reflexively<br>Any time you are struck in combat, you may, for 1 action point, make a resilience roll, soaking an amount of additional damage as determined below.<br>Soak 3 additional damage<br>Soak 6 additional damage<br>Soak 9 additional damage<br>Soak 12 additional damage | [REFLEX] |
| **Never Off-Guard** |  | Eva +1, Pri +3, HP +17 | Passive |  | You are always ready for an attack. Normally, your hit points go down after combat while you’re resting or socializing. Your hit points are always, at least partially, ready to go. When not in combat, you always have a number of hit points up equal to twice your skill in Resilience, even when you’re not conscious. Of course, you can’t have more hit points up than your maximum. | [PASSIVE] [SCALE:Resilience] |
| **Press** |  | Stk +2, Def +2, HP +11 | Stance; resist Dex (negates) |  | stanCe (costs 1 AP to enter)<br>resist: Dexterity (negates)<br>You choose a target, and as long as you’re adjacent to that target, you can completely block him from attacking anybody but you. When you enter this stance, choose a target of the stance. To choose a different target, you must re-enter the stance. As long as you are adjacent to the target, if the target tries to attack anybody, they must succeed at the resist. If they fail, they do not attack and, instead, lose 1 action point. | [STANCE] |
| **Protector** |  | Eva +1, Def +3, HP +14 | As shield deflection |  | Cost: as a Shield Deflection<br>You may protect those around you using your shield. Anytime an adjacent ally would be the target of an attack, you may use your shield to deflect the blow for them. The ally gains any bonuses that you would gain for your deflection. | [REFLEX] |
| **Resolute** |  | Def +1, Wnd +1, HP +13 | Passive | 2+ Resilience stances | reQuires: 2 or more stances known from the Resilience skill You are the ultimate sentinel, transforming yourself into an impregnable barrier. When you enter into one of your stances from the resilience skill, you may simultaneously enter all of your known resilience stances and keep all of them active (as long as they don’t negate each other for any reason). They all act as one stance, so if you get knocked out of your stance, you get knocked out of all of your stances. | [STANCE] [REQ] |
| **Second Skin** |  | Eva +1, Def +2, HP +14 | 1 AP reflexive |  | Cost: 1 AP reflexively<br>Attacks which ignore damage soak still have trouble with you. Whenever you are subject to an attack that is going to ignore your damage soak, you may spend 1 action point to convert it into soakable damage.<br>Up to 3 points of unsoakable damage made soakable. Up to 6 points of unsoakable damage made soakable. Up to 9 points of unsoakable damage made soakable. Up to 12 points of unsoakable damage made soakable. | [REFLEX] |
| **Solid Stances** |  | Eva +1, Def +3, HP +13 | Passive |  | You have great balance and you understand how to keep your posture. As long as you’re conscious, you cannot be voluntarily knocked out of your stance(s) from being pushed back or knocked prone. | [PASSIVE] |
| **Thick Skin** |  | Def +3, Wnd +1, HP +11 | Passive |  | Your body naturally soaks some damage. Your body has a natural soak class of 1. Furthermore, for every 5 skill points you have in Resilience, you have an additional soak class of 1. So, if you have a 20 in Resilience, you have would a soak class (without armor) of 5. This soak class stacks with armor. | [PASSIVE] [STAT:Soak += 1 + floor(Resilience/5)] |
| **Tough Stuff** |  | Def +2, Wnd +1, HP +19 | Passive |  | You gain bonus hit points depending on your skill in Resilience and how many specialties you have. For every specialty you have (including this one), you gain 1 extra hit point. For every 8 skill points you have in Resilience, that number increases by 1. Thus, if you have 8 skill points in Resilience and 6 specialties, you would have 12 extra hit points. | [PASSIVE] [STAT:HP += specialties × (1 + floor(Resilience/8))] |
| **Unassailable Mountain** |  | Acc +1, Def +3, HP +12 | 3 AP reflexive | heavy or heavier armor worn | reQuires: you to be wearing heavy (or heavier) armor Cost: 3 AP reflexively<br>For 3 action points, you may greatly increase your damage soak. This can be decided after the damage has been announced. If the attack was a special attack, any other effects from the attack still apply. This ability only works while in heavy (or heavier) armor. To determine how much your soak class increases, roll below:<br>+4 soak class<br>+5 soak class<br>+6 soak class<br>+7 soak class | [REFLEX] [REQ:armor≥heavy] |
| **Walking Fortress** |  | Def +2, Wnd +1, HP +13 | Stance | 3 Resilience | stanCe (costs 1 AP to enter)<br>reQuires: 3 skill points in Resilience<br>While in the Walking Fortress stance, your defense sky-rockets. You gain a +1 to your defense for every 3 skill points you have in resilience. | [STANCE] [SCALE:Resilience] Def += floor(Resilience/3) |
| **Ward** |  | Stk +2, Def +2, HP +11 | Stance; 1 AP reflexive |  | stanCe (costs 1 AP to enter)<br>Cost: 1 AP reflexively<br>You won’t allow your foes to pass by you unscathed. When an opponent moves into your melee range, you can make a reflexive attack against them for 1 action point. If an opponent moves from one space within melee range to another space within melee range, this also leaves them open to your reflexive attacks. A single opponent can only be the target of this specialty once per turn. | [STANCE] [REFLEX] |
| **Armored Ease** | Armored Movement | Eva +1, Def +3, HP +12 | Passive |  | When you are wearing armor, you may consider it one degree lighter at your discretion. Therefore, you can treat your medium armor as light armor for determining penalties but still gain all of the benefits of wearing medium armor. | [PASSIVE] [GEAR] armor penalty degree −1 |
| **Armored Freedom** | Armored Movement | Def +2, Spd +5, HP +14 | Passive | Armored Ease; 7 Resilience | reQuires: Armored Ease specialty & 7 skill points in Resilience Now, while wearing armor, you may consider it two degrees lighter for determining penalties (in addition to the one degree gained from Armored Ease). Thus, you could be wearing super-heavy armor, but only have the penalties of light armor. | [PASSIVE] [GEAR] [REQ] armor penalty degree −2 more |
| **Living Barrier** | Barrier | Def +3, Pri +1, HP +12 | Stance; resist Dex (negates) |  | stanCe (costs 1 AP to enter)<br>Resist: Dexterity (negates)<br>Nothing bypasses you. When you enter your living barrier stance, you strategically place yourself so that you take up three adjacent spaces (as in, your normal space plus two more) and you may attack anything adjacent to your new size.<br>Opponents attempting to move through your new space must make a dexterity resist against your resilience. If the opponent fails, they may not enter your new space and their movement is stopped. | [STANCE] |
| **Living Wall** | Barrier | Def +2, Wnd +1, HP +14 | 1 AP reflexive; resist Dex (negates) | Living Barrier | reQuires: Living Barrier specialty<br>resist: Dexterity (negates)<br>Cost: 1 AP reflexively<br>While in living barrier stance, if an opponent attempts to attack someone through you or inside your newly expanded space, you may spend 1 reflexive action point to intercept this attack. In doing so, you recieve no evade roll (acting as if the evade roll was a<br>1) and are hit with the attack. The opponent may roll a dexterity resist against your resilience still in order to attempt to attack his original target. | [REFLEX] [REQ] |
| **Living Stronghold** | Barrier | Def +2, Wnd +1, HP +15 | Passive; resist Dex | Living Barrier, Living Wall | resist: Dexterity<br>reQuires: Living Barrier & Living Wall specialties Nothing bypasses you. While in living barrier stance, if an opponent attempts to target somebody through you or inside your expanded space and fails their dexterity resist against you, the attack is negated. They lose all of the action points spent to make the attack. | [COND] [REQ] |

### 6.4 Cunning specialties

**What anyone can do with Cunning (attribute uses):** Gather Intel (Cunning tier = depth of knowledge; research/sources may grant re-rolls and +3/+6) · Lockpicking (3 AP to start, one roll per lock: T1 several minutes, not in combat / T2 +9 AP / T3 +3 AP / T4 first try; lock quality lowers tier by 1–3) · Notice (people: Cunning vs their Cunning if hiding or Dex if sneaking; objects: T1 visible, T2 partially hidden, T3 almost entirely hidden, T4 what nobody else would) · Social tells (§1.12)

#### Espionage

| Specialty | Group | Bonuses | Cost / type | Requires | Effect | Tags |
|---|---|---|---|---|---|---|
| **Destabilizing Strike** |  | Acc +1, Stk +2, HP +7 | Attack +1 AP |  | Cost: Attack +1 ap<br>When your opponent is disoriented, you take advantage of their weakened mind and can make a destabilizing strike. A destabilizing strike, if it deals damage, causes the opponent to become open to a reflexive attack from every character within melee range of the target. These reflexive attacks can be made either as unarmed attacks or by using super-heavy or smaller melee weapons, which will only cost 1 action point to perform instead of the normal 2. As the person who made the destabilizing strike, you cannot make a reflexive attack. | [ATTACK+1] [COND] |
| **Feign Fatal Wounds** |  | Acc +1, Eva +2, HP +7 | 1 AP reflexive; resist Cunning (opposed, negates) |  | resist: Cunning (negates)<br>Cost: 1 AP reflexively<br>When you’re struck in combat, you can overplay the success of the attack, making your enemy think you’ve been taken out of the battle or seriously injured. When damage is dealt to you, you may spend 1 action point reflexively in order to trick the opponent into thinking that they have wounded, dealt you a fatal attack, or outright killed you. They may resist with a successful cunning roll (opposed by your espionage roll). If they fail, you may choose to what degree you appear to have been injured (or falling down and feigning death entirely).<br>Do note that if you fall down as a result of feigning death or a serious wound, standing up costs an action point. | [REFLEX] |
| **First Strike** |  | Acc +1, Pri +4, HP +5 | Passive |  | You make it your business knowing that you’re in a fight before your enemies do. If you make the first strike of a combat - either before priority is rolled or by being the first person to act in the combat - your attack gains a bonus on your accuracy roll equal to your skill in espionage. | [COND] [SCALE:Espionage] Acc += Espionage |
| **Flowing Shadow** |  | Acc +1, Eva +1, HP +6 | Passive | 4 Espionage | reQuires: 4 skill points in Espionage<br>You flow within the shadows, keeping your opponents guessing as you weave and dart through the darkness. Any time the person attacking you is blinded or in poor lighting, you can roll your evade two times and take the higher result. In addition, you gain a +1 on your evade rolls per 4 skill points you have in Espionage while in darkness. If the opponent attacking you in unaffected by darkness or relies on a way of finding you that is not based on sight, you do not gain the evade bonus or the ability to roll twice and take the higher result. | [COND] [SCALE:Espionage] Eva += floor(Esp/4) |
| **Heartseeker** |  | Acc +1, Stk +2, HP +6 | Light-weapon melee attack +1 AP |  | Cost: Melee Attack with a Light Weapon +1 AP<br>When wielding a light weapon, you know the best way to get through your enemy’s pesky armor. When you make a heartseeking attack, your opponent has more difficulty soaking it. For the purposes of this attack, lower your opponent’s soak class by 1 for every tier that you receive with your espionage roll. This does not permanently affect the armor.<br>-1 soak class<br>-2 soak class<br>-3 soak class<br>-4 soak class | [ATTACK+1] [REQ:light weapon] |
| **Invisible Blade** |  | Acc +1, Stk +1, HP +7 | Stance |  | stanCe (costs 1 AP to enter)<br>You fight with your weapons palmed, keeping your attacks so tight that your blades are little more than an extension of your fists. When using a weapon that is both light and concealable, you fight as if unarmed: you cannot be disarmed or have your weapon sundered, and your attacks only cost 1 action point to make. For all other purposes, your weapon still counts as a light weapon. | [STANCE] [GEAR] AP=1 |
| **Master Lockpick** |  | Eva +1, Pri +3, HP +7 | Passive |  | Doors are of little bother to you; your skill in lockpicking turns solid barriers into tiny inconveniences. This specialty improves your ability to understand a lock and pick it. When you begin picking a lock, roll for your Master Lockpick to further reduce the action points that you’ll need in order to pick the lock. The AP cost of the lock can never drop below marque I.<br>No luck. Your normal cunning will have to deal with the lock.<br>You can kind of see it. The marque of the lock is reduced by 1 for the purpose of this lockpicking.<br>It’s an average challenge. The marque of the lock is reduced by 2 for the purpose of this lockpicking.<br>Aha! The marque of the lock is reduced by 3 for the purpose of this lockpicking. | [COND] |
| **Pierce the Darkness** |  | Acc +2, Pri +1, HP +7 | Passive | 4 Espionage | reQuires: 4 skill points in Espionage<br>You launch your attack from the victim’s blindspot, ensuring your success. When you are attacking from perfect darkness, poor lighting, fog, or anything else that hampers vision, you gain a +1 on your accuracy roll for every 4 skill points you have in espionage. If the opponent has some way of seeing through the poor visibility you’re hiding in, you do not gain the bonus. | [COND] [SCALE:Espionage] Acc += floor(Esp/4) |
| **Silent Kill** |  | Acc +1, Eva +2, HP +6 | Melee attack +1 AP; resist Cunning |  | resist: Cunning (see below)<br>Cost: Melee Attack +1 AP<br>When you attack somebody, you may attempt to make the attack absolutely silent. This is normally done when going for a killing blow that the target is unaware of, in order to not get caught in the act.<br>You may be stiffling their scream or trying to make your blade not chink against their armor. If the target does not try to make a noise, you simply roll your skill in espionage against anybody listening.<br>If, however, the target screams, yells out, or calls for help, you must attempt to cover their mouth or stab them in the throat: anything to keep the sound from carrying. If this happens, anybody listening can attempt a cunning resist to hear the cry. | [ATTACK+1] |
| **Sinister Strike** |  | Acc +1, Stk +3, HP +7 | Reflexive melee strike +3 AP | 18 Espionage | reQuires: 18 skill points in Espionage<br>Cost: Reflexive Melee Strike +3 AP<br>Your ally has created an opening, and it’s time to go in for the kill. After an ally hits an adjacent opponent, you can reflexively make a sinister strike. This attack deals damage directly to wounds. If it exhausts the target’s wounds, they suffer a fatal effect. | [REFLEX] [REQ] |
| **Fighting Blind** | Nightwalker | Acc +2, Stk +1, HP +6 | Passive |  | You take no penalty for melee fighting while in poor lighting or in absolute darkness.<br>If you do not know where your opponent is, this specialty does not give you a way of locating them, and this Fighting Blind does not negate the ranged penalty for blindess. | [COND] |
| **Deep Blind Senses** | Nightwalker | Acc +1, Eva +1, HP +6 | Passive | Fighting Blind; 5 Espionage | reQuires: Fighting Blind specialty & 5 skill points in Espionage Your hearing, sense of the air vibration, or ability to locate your opponents in the deepest of darknesses allows you to fire accurately upon distant targets even when blind. You may use ranged attacked against opponents at no penalty when blind or in poor lighting up to 5 feet away per skill point you have in espionage. | [COND] [REQ] [SCALE:Espionage] |
| **Cover Expert** | Cover User | Eva +2, Pri +1, HP +5 | Stance |  | stanCe (costs 1 AP to enter)<br>You’re well practiced at taking advantage of whatever cover is available. While you are in this stance, any cover that you take is treated as though it were one level greater. If you exceed heavy cover, you cannot be targeted by a ranged attack. | [STANCE] |
| **Contort** | Cover User | Acc +1, Eva +2, HP +6 | 1 AP | Cover Expert | reQuires: Cover Expert specialty<br>Cost: 1 AP<br>Small barriers can fully eclipse your body as you contort yourself to fit behind them. While in your Cover Expert stance and behind cover, you may contort yourself so that the cover becomes complete cover, and you cannot be targeted by ranged attacks while behind it. You may leave your cover for no action point cost. Additionally, when you are in a hiding spot but somebody is actively searching that spot, they do not automatically find you. Instead, they must still roll their cunning to notice you. If they fail the roll, they do not notice you, even though they were searching your exact area. | [ACTION] [REQ] |
| **Critical Hits** | Critical | Acc +2, Stk +1, HP +5 | Passive |  | Light weapons, while normally less damaging than other weapons, do seem to have a knack for finding soft spots in a target’s defense. When you attack with a light weapon in melee, for every 5 points that your accuracy roll exceeds your target’s evade roll, your attack’s damage class increases by 1. This extra damage class cannot exceed your skill in espionage.<br>Thus, if your opponent rolled a 2 on their evade and you rolled a 12, your attack’s damage class would be 2 higher than normal. | [COND] [SCALE] DC += min(floor((Acc−Eva)/5), Espionage) |
| **Hairsplitter** | Critical | Acc +2, Stk +1, HP +5 | Passive | Critical Hits; +6 Accuracy from specialties | reQuires: Critical Hits specialty & +6 Accuracy (from specialties) Your precision and accuracy is not to be out done. When you are making a melee attack with a light weapon, you gain an additional damage class for every 3 points that your accuracy roll exceeds your target’s evade roll. This bonus replaces your bonus from your Critical Hits specialty. This extra damage class cannot exceed your skill in espionage. | [COND] [REQ:Acc≥6] DC += min(floor((Acc−Eva)/3), Espionage) |
| **Pinpoint Shot** | Critical | Acc +2, Pri +1, HP +6 | Passive | Critical Hits or Heartseeker | reQuires: Either the Critical Hits or Heartseeker specialty You’re just as accurate from a range as you are when you’re standing right next to your victim. You may use any specialty that calls for a melee attack with a light weapon when using a light ranged weapon. | [PASSIVE] [REQ] |
| **Dirt in the Eyes** | Dirt In The Eyes | Eva +2, Pri +1, HP +7 | 2 AP |  | Cost: 2 AP<br>Throwing dirt, blood, water, and other foul substances is an art that has been perfected by dirty fighters for centuries. It’s perfect for catching people off-guard and momentarily blinding them. If you’d like to throw dirt in somebody’s eyes, they must be adjacent to you, and you must succeed at making an accuracy roll against their evade roll. (For all intensive purposes, this is similar to a called shot against the head.) If they have anything protecting their eyes, such as goggles, the target gains a +3 on their evade roll. If you’re successful, the opponent suffers a penalty to their next evade roll equal to your skill in espionage. The target may, if he so chooses, spend 1 action point to rub the subtance out before taking the penalty on his next evade. | [ACTION] [SCALE:Espionage] |
| **Blind & Swing** | Dirt In The Eyes | Acc +1, Stk +2, HP +6 | Melee attack +1 AP | Dirt in the Eyes | reQuires: Dirt in the Eyes specialty<br>Cost: Melee Attack +1 AP<br>You may combine your Dirt in the Eyes attack with a melee attack, more efficiently catching your foes in their crucial moment of weakness. For the cost of a melee attack +1 action point, you may throw dirt in your opponent’s eye and make a melee attack. You resolve your Dirt in the Eyes attack first (which, if successful, gives them a large penalty on their evade roll) and then your attack second. | [ATTACK+1] [REQ] |
| **Distracting Attack** | Disorienting | Acc +2, Pri +1, HP +7 | Melee attack +1 AP; resist Cunning (tiers down) |  | resist: Cunning (tiers down)<br>Cost: Melee Attack +1 AP<br>Your attacks bewilder and confuse your opponent. You can make a melee attack that, if successful, disorients the target (causing them to lose 1 action point per turn) for a handful of turns.<br>1 turn<br>2 turns<br>3 turns<br>4 turns | [ATTACK+1] |
| **Taking Advantage** | Disorienting | Acc +1, Stk +2, HP +8 | Passive | Distracting Attack | reQuires: Distracting Attack specialty<br>When your opponent is disoriented, you know all the tricks for taking advantage of their momentary weakness. When fighting somebody who is disoriented, it does not cost you the extra action point in order to make called shots against the person. | [COND] [REQ] |
| **Brain-Blowing Attack** | Disorienting | Acc +1, Stk +2, HP +9 | Passive | 12 Espionage; Distracting Attack | reQuires: 12 skill points in Espionage & Distracting Attack specialty Your distracting attacks land beautifully, leaving the target fully disoriented for a considerably longer period of time. Whenever you make a distracting attack, you disorient them for twice as long as usual. | [PASSIVE] [REQ] |

#### Expertise

| Specialty | Group | Bonuses | Cost / type | Requires | Effect | Tags |
|---|---|---|---|---|---|---|
| **Appraisal** |  | Acc +1, Eva +1, HP +9 | Once per downtime |  | You’ve got a keen eye for exactly how much something is worth. Though you can figure out the price of most items by looking to the Trust, you’re skill lies in figuring out the price for ancient prized relics, valuable gemstones, and precious works of art. You may only appraise an item once per downtime.<br>You are able to determine the going market value of an item within 10%.<br>You are able to determine the market value of an item, almost to the duke.<br>Not only can you pinpoint the market value for an item, you can deceipher any history or lore about it.<br>You have a knack for knowing the exact price for an item, obscure information about it, and whether it contains any ancient secrets or certain people are searching for it. | [NARR] |
| **Concentrated Focus** |  | Eva +1, Def +3, HP +10 | Passive | 3 Expertise | reQuires: 3 skill points in Expertise<br>Your concentration is so intense that it is difficult to stun you. When making a resist against being stunned, you may add your expertise onto the resist. (If the resist is a cunning roll, add your expertise in addition to the cunning total.) | [COND] [SCALE:Expertise] |
| **Deep Breath** |  | Eva +1, Pri +3, HP +8 | 1 AP (once per turn) | 5 Expertise | Cost: 1 AP<br>reQuires: 5 skill points in Expertise<br>Taking one deep breath, you look around the battlefield, analyzing your environment. As you exhale, time itself grinds to a halt. You receive 1 extra action point when your action points refresh. You may only perform this once per turn. (Simply put, this specialty lets you spend 1 action point in order to gain an extra action point on your next turn, exceeding your normal maximum pool.) | [ACTION] [REQ] |
| **Demoman** |  | Acc +1, Stk +3, HP +8 | Passive | 3 Expertise | reQuires: 3 skill points in Expertise<br>You don’t know how they work, but you sure know how to blow them up! For every 3 skill points you have in expertise, you gain a +1 damage class when attacking automatons and vehicles. This applies to anything you use that has a damage class, including explosives. | [COND] [SCALE:Expertise] DC += floor(Exp/3) |
| **Efficiency Expert** |  | Pri +3, DIY +3, HP +8 | Passive | 3 Expertise | reQuires: 3 skill points in Expertise<br>When you or your friends are crafting items, you’re key to ensuring that no funds are wasted, that no screw is left behind. Not only does your DIY (do-it-yourself) score increase (based on the bonuses granted by this specialty), you improve your allies’ DIY score. When you spend your downtime with your fellow adventurers working on equipment, their DIY score becomes 3 points higher. This bonus cannot increase their effective DIY score beyond 12.<br>If you have multiple efficiency experts, the bonus do not stack. Instead, for every additional efficiency expert you have in your party, you gain an additional +1 DIY. | [COND] [DIY] |
| **Fire Fighter** |  | Def +2, Pri +2, HP +12 | Passive |  | You must’ve had a pyromaniac as a friend growing up - you’re able to make battling back blazing infernos seem like child’s play. If you are putting out fires, you gain 2 extra action points per turn for putting out fires. You cannot catch on fire when extinguishing a fire on another creature. | [COND] |
| **Hurl** |  | Acc +1, Stk +3, HP +9 | Passive |  | You can throw just about anything. Even if an item or weapon is not classified as a throwing weapon, you may throw it as if it were. You do not take penalties for impromptu weapons, and it can go the distance it would go for its size categories (light: 25 feet; medium: 75 feet; and, heavy: 50 feet). | [PASSIVE] [GEAR] |
| **Improv Fighter** |  | Acc +1, Stk +2, HP +10 | Passive | 3 Expertise | reQuires: 3 skill points in Expertise<br>You’re a master of picking up whatever is nearby and using it to its most destructive potential. Barstool, glass, painting, or ladder, you’ve killed with them all. When using an impromptu weapon, your penalties are eliminated. When fighting with such unconventional melee objects, you gain a +1 to accuracy for every 3 points in expertise you have because opponents never expect you to be so talented with them. | [COND] [SCALE:Expertise] Acc += floor(Exp/3) |
| **Mechanic** |  | Eva +1, Def +2, HP +8 | 3 AP |  | Cost: 3 AP<br>Though you may not be the original inventor, you have a knack for seeing problems and figuring out how to fix them. You may repair an adjacent automaton, vehicle, or any mechanical contraption with wounds or hit points.<br>repairs 6 wounds or hit points<br>repairs 12 wounds or hit points<br>repairs 18 wounds or hit points<br>repairs 24 wounds or hit points | [ACTION] |
| **Patch the Bleeding** |  | Def +2, Pri +2, HP +11 | 1 AP |  | Cost: 1 AP<br>You’ve dealt with enough wounds to know how to make them stop bleeding very quickly. You can spend 1 action point to stop<br>10 bleeding damage (as opposed to the normal 5). In addition, if somebody is bleeding out (such as from losing a limb), for every<br>1 action point you spend it counts as 3 action points for the purposes of preventing bleeding out. | [ACTION] |
| **Observance** |  | Eva +1, Def +2, HP +10 | 2 AP; resist Cunning (negates) |  | resist: Cunning (negates)<br>Cost: 2 AP<br>You watch the enemy closely, learning his movements and predicting his actions. Once you have “observed” somebody (an act that takes 2 action points), the next attack they make on you is converted into a normal attack unless they can make the resist against your Expertise. If they had applied any specialties to the attack or were making a called shot, all of these additions are negated. They still expend however many action points they would have, however.<br>For example, an opponent is about to deliver an attack with a heavy weapon (2 AP), but they upgrade it to a solid strike (+1 AP) and called shot to the head (+1 AP). If they’ve been observed, their solid attack to the head becomes a regular attack with their heavy weapon, but still costs the 4 action points they would have used. If the observed opponent made a normal attack with their heavy weapon as their next attack, the observation would be wasted. | [ACTION] |
| **Weak Point** |  | Acc +1, Eva +1, HP +8 | 2 AP |  | Cost: 2 ap<br>After carefully studying your enemy, you are able to locate its weak point and exploit it. You may spend 2 action points studying a single foe, attempting to locate a weakness.<br>You are able to detect any specific weaknesses to called shots the enemy has.<br>You are able to determine what called shots the opponent would have the most trouble resisting or called shot weaknesses it has.<br>You are able to determine any called shot weaknesses it has, which called shots it would have the most trouble resisting, and, when striking a called shot weakness, the effect of the called shot is doubled.<br>You are able to determine any called shot weaknesses it has, which called shots it would have the most trouble resisting, and when striking a called shot weakness, the effect of the called shot is doubled. Furthermore, you are able to determine an immortal creature’s death trigger. | [ACTION] |
| **Trick Counter** |  | Acc +1, Eva +1, HP +9 | 1+ AP reflexive (= upgrade cost); resist Cunning (negates) |  | resist: Cunning (negates)<br>Cost: 1 (or more) ap reflexively<br>Your enemies think they are upgrading their attacks and coming at you with unique tricks. You see through them. Whenever you are being attacked with a specialized attack or called shot (one that would have a cost of attack +1 AP, or attack +2 AP, et cetera), you may spend an equal amount of action points to the upgrade in order to attempt to negate it. The opponent could then resist with a cunning roll against your expertise. If they fail, their attack is converted to normal, though the opponent still spends the same amount of action points.<br>For example, if you are being attacked by a solid strike (attack +1 AP), you can spend 1 action point in order to attempt to make it a normal attack. If they have added multiple specialties on to the attack, you can choose to negate just a portion of it, or negate all specialties, and the opponent resists against losing each specialty separately. | [REFLEX] |
| **Poison Finder** | Anti-Poison | Acc +1, Eva +1, HP +11 | Passive |  | Any time a poison comes within 10 feet of you, you may automatically roll your cunning to perceive it (unless you are not conscious or otherwise have your senses dulled), and you add your skill in expertise to the roll. | [COND] [SCALE:Expertise] |
| **Remove Poison** | Anti-Poison | Def +3, Pri +2, HP +10 | 2 AP |  | Cost: 2 ap<br>You have a knack for drawing poison out of a victim. Any time that you or an adjacent ally has been poisoned, you may attempt to remove it. If the poison has not activated yet, you can attempt to remove all effects. If it has activated, however, you can only remove lingering effects. Thus, if the poison dealt damage upon activation, you would have to remove the poison prior to activation in order to prevent the damage from being dealt. When you remove poison, you are able to negate effects. Once you attempt to remove the poison, you’re able to see what effects the poison is going to have.<br>remove 1 effect<br>remove 2 effects<br>remove 3 effects<br>remove 4 effects<br>Note: Poisons that have the same augment multiple times in order to increase the potency of that augment only count as one effect. | [ACTION] |
| **Combat Insight** | Combat Insights | Eva +1, Pri +2, HP +11 | Passive |  | While others are forced to rely on their brute strength or reflexes to avoid called shots, you see them all coming and react accordingly. You may use your cunning for all called shot resists instead of the normal attribute. | [PASSIVE] |
| **Combat Analytics** | Combat Insights | Acc +1, Eva +1, HP +10 | 1 AP reflexive | 11 Expertise; Combat Insight | reQuires: 11 skill points in Expertise & Combat Insight specialty Cost: 1 AP reflexively<br>You’ve been in combat enough times that nothing surprises you any more. Gone are the days of relying on brute, dexterity, or spirit. Whenever a resist is required of you during combat, you may always use your cunning by spending 1 action point. | [REFLEX] [REQ] |
| **Weapon Appropriations** | Item Appropriation | Acc +1, Eva +1, HP +9 | Passive (downtime in trade location) |  | Though you might not have an armsmith handy, your knack for bargaining and making contacts allows you to get some higher quality weapons than normal. You may add a single weapon augment on to your weapon of choice (be it firearm, crossbow, melee weapon, throwing weapon, or bow). The augment must take up a single slot. The augment begins at marque 1, but increases by marque as though your expertise was determining its marque. (Thus, at 5 skill points in Expertise, you’ll have a marque II augment, 15 skill points will give you a marque III, and 25 skill points a marque IV.)<br>You may only have one such augment on a weapon that you carry, though you may select a different augment during every downtime that you have. (The downtime must occur in a location that has commerce and trade, otherwise you wouldn’t be able to procure the augment.) If the augment does not have a marque, you cannot appropriate it until you reach the equivalent cost for the augment. | [GEAR] [AUG] [SCALE:Expertise] |
| **Quality Weapon** | Item Appropriation | Acc +1, Stk +3, HP +7 | Passive | Weapon Appropriations | reQuires: Weapon Appropriations specialty<br>You’re quite good at getting hand-outs. Your appropriated weapon gains an additional augment (of the same marque). Once you reach 10 skill points in Expertise, you gain a third augment on the weapon. All augments must be on the same weapon. | [GEAR] [REQ] |
| **Field Surgeon** | Surgery | Def +2, Pri +2, HP +10 | 3 AP (patient spends 3 AP reflexively) | 4 Expertise | reQuires: 4 skill points in Expertise<br>Cost: 3 ap<br>The field surgeon patches up major wounds to decrease their allied mortality rate throughout the battlefield. You are that surgeon. You can restore wounds damage, but once you make your attempt, you cannot restore any more wounds damage on a person unless they take more damage to their wounds. Furthermore, you cannot restore more wounds damage than they’ve taken from their most recent attack. Thus, if somebody cut your ally for 3 wounds damage, you could not heal 4 of their wounds. The patient must spend 3 action points reflexively in order to be treated. The patient can do this over multiple turns, pulling action points from their next turn if need be. If you are engaged with a melee attacker, this leaves both you and the patient open to reflexive attacks (which they can make for the normal cost of their attack).<br>restores 1 wound<br>restores 2 wounds<br>restores 3 wounds<br>restores 4 wounds | [ACTION] [REQ] |
| **First Aid** | Surgery | Def +2, Spd +5, HP +9 | Move + Field Surgeon reflexive | Field Surgeon | reQuires: Field Surgeon specialty<br>Cost: Move + Field Surgeon reflexively<br>When somebody near you takes damage, you’re able to leap to the rescue and help them out. When somebody has taken wounds damage that is within one move’s distance of you, you may reflexively move to them and heal them using your Field Surgeon specialties. | [REFLEX] [REQ] |
| **Self-Surgery** | Surgery | Pri +3, Wnd +1, HP +9 | Passive | Field Surgeon | reQuires: Field Surgeon specialty<br>Though its difficulty is beyond most people, you’re able to grit through self-surgery. You may now use Field Surgeon on yourself. | [PASSIVE] [REQ] |

#### Showmanship

| Specialty | Group | Bonuses | Cost / type | Requires | Effect | Tags |
|---|---|---|---|---|---|---|
| **Blindside** |  | Eva +1, Pri +3, HP +8 | 2 AP to begin, 1 AP/turn to continue |  | Cost: 2 AP to begin, 1 AP to continue during subsequent turns Large hand gestures and loud noises keep your opponent focused in a direction of your choosing, allowing you to make them blind to everything in the opposite direction. The target must be within<br>25 feet of you. The opponent acts blind and deaf toward anything from that direction until something attacks them from that direction, at which time your Blindside is cancelled and must be restarted. You may have blindside activated on multiple people at once, but a single opponent can only be the target of one blindside. | [ACTION] |
| **Captive Audience** |  | Acc +1, Eva +1, HP +9 | Stance; resist Cunning (negates) |  | stanCe (costs 1 AP to enter)<br>resist: Cunning (negates)<br>Once you’ve got someone close to you, you never let them go. When entering this stance, choose a single adjacent target. You cannot move away from the target, but you also prevent the target from moving away from you unless they resist. They can attempt to resist immediately when you enter the stance, and then at the end of their turn, when tier action points refresh. If they successfully resist, you exit your stance. | [STANCE] |
| **Catchphrase** |  | Acc +1, Eva +1, HP +8 | 1 AP |  | Cost: 1 AP<br>You reveal your hidden catchphrase and jump into your next action. Saying your catchphrase requires 1 action point, but the next time you roll a tier result for a specialty, you use your showmanship skill in place of the skill the specialty normally requires. | [ACTION] [SCALE:Showmanship] |
| **Chime In** |  | Eva +1, Pri +3, HP +8 | Passive | 2 Showmanship | reQuires: 2 skill points in Showmanship<br>By adding in little snippets of information to help an argument, you add a bonus to another player’s cunning roll whenever they are attempting diplomacy, bluff, or any social interaction. The bonus is a +1 for every 2 skill points you have in showmanship. | [COND] [SCALE:Showmanship] floor(Show/2) |
| **Conveyor** |  | Eva +1, Pri +2, HP +9 | 1 AP reflexive |  | Cost: 1 AP reflexively<br>You can duplicate effects that you see, extending an ally’s buffing range. When an ally creates an effect that affects all allies within a certain range, you can spend 1 action point reflexively in order to also affect all allies within the same range of you. | [REFLEX] |
| **Deafening Roar** |  | Stk +2, Def +2, HP +10 | 1 AP; resist Brute (tiers down) |  | resist: Brute (tiers down)<br>Cost: 1 AP<br>You choose one adjacent opponent and roar so loudly in his ear that his eardrum bursts. The opponent is deafened (suffering a -2 to evade) for a number of turns.<br>1 turns<br>2 turns<br>3 turns<br>4 turns | [ACTION] |
| **Distract** |  | Eva +1, Pri +3, HP +7 | 2 AP reflexive; resist Cunning (negates) |  | resist: Cunning (negates)<br>Cost: 2 AP reflexively<br>Sometimes you’re right in front of them. Other times, they’re not so sure. You can distract an opponent during their turn, momentarily thinking that you’re somewhere else. Whenever an opponent takes an action against you, you may attempt to distract them. Choose another location within 10 feet to create your distraction. If the opponent fails their cunning resist against your showmanship, they - for the purpose of this one action - believe that you are in the location where you caused the distraction. If there is something else there (like a wall or a person), they gain a +10 on the resist. | [REFLEX] |
| **Jester** |  | Acc +1, Eva +1, HP +7 | 2 AP; resist Cunning (tiers down) |  | resist: Cunning (tiers down)<br>Cost: 2 AP<br>You can throw your voice, yell, or dance to bewilder opponents. On-looking opponents within 25 feet may become disoriented simply from laughing at you. Jester can affect multiple people, and all effected may attempt to resist. For every tier that they receive above tier 1, they decrease the amount of turns they are disoriented by 1.<br>1 target is disoriented for 1 turn<br>2 targets are disoriented for 2 turns<br>3 targets are disoriented for 3 turns<br>4 targets are disoriented for 4 turns | [ACTION] |
| **Marionette Strings** |  | Acc +2, Pri +2, HP +6 | 1 AP reflexive |  | Cost: 1 AP reflexively<br>You guide the attack of a nearby ally, ensuring their success. Any time an ally makes an attack within 25 feet, you may use your marionette strings to give them a bonus on their accuracy. This can be decided even after the roll has been made.<br>+2 on their accuracy roll<br>+4 on their accuracy roll<br>+6 on their accuracy roll<br>+8 on their accuracy roll | [REFLEX] |
| **Praise** |  | Acc +1, Eva +1, HP +7 | 1 AP reflexive |  | Cost: 1 AP reflexively<br>You sing the praises of your fellow adventurers. You may spend<br>1 action point reflexively to allow a party member to re-roll any resist, as long as they can hear you. You can only do this once per resist. | [REFLEX] |
| **Sleight of Hand** |  | Eva +2, Pri +2, HP +6 | Passive |  | When you use an item, one second it’s there, the next it’s gone. Your opponents won’t be able to take advantage of you while you use items. Activating and using items does not leave you open to reflexive attacks. | [PASSIVE] |
| **Smoke & Mirrors** |  | Eva +1, Pri +3, HP +7 | 3 AP reflexive; resist Dex (negates) | 3 Showmanship | reQuires: 3 skill points in Showmanship<br>resist: Dexterity (negates)<br>Cost: 3 AP reflexively<br>With the flick of your wrist, you can make an ally within 25 feet appear in one location when they thought they were elsewhere. When an ally has failed an evade roll, you may reflexively move your ally to an adjacent space. The assailant may resist against your showmanship with their dexterity. If you succeed, your ally may immediately move to an adjacent space, and the assailant’s attack automatically misses. | [REFLEX] [REQ] |
| **Throw Off Balance** |  | Eva +1, Pri +2, HP +8 | 1 AP reflexive; resist Cunning (tiers down) |  | resist: Cunning (tiers down)<br>Cost: 1 AP reflexively<br>Just as a melee attack hits one of your allies within 25 feet, you distract the opponent and cause them to do minimal damage. The attacker must roll their strike multiple times and take the lowest roll, but they can use their cunning resist in order to lower the result.<br>The attacker rolls two times and takes the lowest The attacker rolls three times and takes the lowest The attacker rolls four times and takes the lowest The attacker rolls five times and takes the lowest | [REFLEX] |
| **Unmarred Perfection** |  | Eva +1, Pri +2, HP +8 | Stance; resist Cunning or Spirit (negates) |  | stanCe (costs 1 AP to enter)<br>resist: Cunning or Spirit (negates)<br>Opponents regret attacking you, for fear of harming your perfect image. While in this stance, anybody that attempts to attack you in melee must resist or suffer a penalty to their accuracy equal to your skill in showmanship. However, while in this stance, you can make only graceful and non-alarming moves, and thus must roll all strike rolls twice and take the lower result. | [STANCE] [SCALE:Showmanship] |
| **Epic Dance** | Choreographed | Eva +2, Pri +1, HP +6 | 2 AP to begin, 1 AP/turn to continue |  | Cost: 2 AP to begin, 1 AP to continue during subsequent turns You bust out your best dance moves, chaining them together in a beautifully unpredictable fashion. While dancing your epic dance, you gain a +3 to evade. You gain an additional point of evade for every 5 skill points you have in Showmanship. You can only have one epic dance going at any given time.<br>If tripped, your Epic Dance is cancelled and must be restarted. | [STANCE-like] [STAT:Eva += 3 + floor(Show/5)] |
| **Never Stop the Dance** | Choreographed | Eva +1, Def +2, HP +9 | Passive | Epic Dance | reQuires: Epic Dance specialty<br>While performing your epic dance, you use your choreography to block and brace your body against incoming blows. You gain an identical bonus to your defense in addition to the evade bonus you recieve from your epic dance. | [COND] [REQ] [STAT:Def += 3 + floor(Show/5)] |
| **Battle Theme** | Epic Music | Acc +1, Eva +1, HP +7 | 2 AP to begin, 1 AP/turn to continue |  | Cost: 2 AP to begin, 1 AP to continue during subsequent turns Don’t worry, you’ve got this. The epic music in the air says that you can’t fail. While performing your battle theme, you gain a +3 to accuracy rolls. You gain an additional point of accuracy for every 5 skill points you have in showmanship. You can only be singing one battle theme at any given time.<br>If you are singing, a successful called shot to your neck will cancel your battle theme. Alternatively, if you are using a musical instrument, a successful sunder or disarm will also cancel your battle theme. | [STANCE-like] [STAT:Acc += 3 + floor(Show/5)] |
| **Heavenly Serenade** | Epic Music | Eva +1, Pri +2, HP +8 | 2 AP reflexive; resist Spirit (negates) | Battle Theme | reQuires: Battle Theme specialty<br>resist: Spirit (negates)<br>Cost: 2 AP reflexively<br>Your battle theme is so beautiful that it digs deep into people’s souls and prevents them from acting. While performing your battle theme, any time anybody within 25 feet wants to make an action, you can reflexively spend 2 action points to make them roll a resist against your showmanship in order to take that action. If they fail the resist, they instead lose 1 action point. | [REFLEX] [REQ] |
| **Spotlight** | Epic Music | Acc +1, Eva +1, HP +9 | 1 AP reflexive | Battle Theme | reQuires: Battle Theme specialty<br>Cost: 1 AP reflexively<br>You point to an ally within 25 feet, signaling to them that it’s their time to shine. While performing your Battle Theme, you may spend 1 action point reflexively to grant your Battle Theme accuracy bonus to an ally’s accuracy, evade, strike, or defense roll. | [REFLEX] [REQ] |
| **Unified Chorus** | Epic Music | Acc +1, Stk +3, HP +10 | Passive | Battle Theme; 16 Showmanship | reQuires: Battle Theme specialty & 16 skill points in Showmanship Your beautiful song causes your allies to lend you their voices! Any bonuses to accuracy or strike you gain from your Battle Theme now apply to all allies within 25 feet of you. If multiple allies have this specialty, everyone only recieves bonuses from the one with the highest amount of skill points in showmanship. | [COND] [REQ] |
| **Victory Theme** | Epic Music | Acc +1, Stk +2, HP +9 | Passive | Battle Theme | reQuires: Battle Theme specialty<br>You begin to weave a power ballad which drives you forward; your music crying for the utter destruction of your foes. Any bonus to accuracy you recieve from your battle theme also acts as a bonus to your strike. | [COND] [REQ] [STAT:Stk += BattleTheme] |
| **Smokescreen** | Smokescreen | Eva +1, Pri +3, HP +8 | 1 AP |  | Cost: 1 AP<br>When you need to, you’ve always got a way to throw enemies off for just a second or two. You may toss down a smokescreen during your turn that lasts until the end of your turn (when your action points refresh). This smokescreen only envelopes you, but it hides all of your actions while in the smokescreen. If you move, the smokescreen does not move with you and instead disperses. | [ACTION] |
| **Walking Darkness** | Smokescreen | Eva +1, Spd +5, HP +7 | Stance | Smokescreen | stanCe (costs 1 AP to enter)<br>reQuires: Smokescreen specialty<br>More than a simple disappearing act, you walk across the battlefield shrouded by a magician’s smoke cloud. While in this stance, you gain a +4 to evade and all of your actions are considered hidden. If an opponent has some way of knowing where you are that does not rely on sight or can see through perfect darkness, you do not gain the bonus to evade against them. | [STANCE] [REQ] [STAT:Eva +4] |

#### Tactical

| Specialty | Group | Bonuses | Cost / type | Requires | Effect | Tags |
|---|---|---|---|---|---|---|
| **Ally of the Machine** |  | Acc +1, Eva +1, HP +9 | Passive | 6 Automata | reQuires: 6 skill points in Automata<br>Using your keen sense of machinery and the way automatons function, you can now treat automatons as your allies. When using a specialty that allows you to affect your allies, automatons may now act as allies. | [PASSIVE] [REQ] |
| **Armistice** |  | Eva +2, Pri +1, HP +6 | Stance; resist Cunning (negates) |  | stanCe (costs 1 AP to enter)<br>resist: Cunning (negates)<br>Sometimes the best part of a battle is when you’re not fighting in it. When you enter your armistice stance, opponents who attack you are stunned for 1 action point unless they resist against your tactical. However, you must exit your armistice stance (for<br>0 action points) before attacking, else you will be stunned for 2 action points. | [STANCE] |
| **Blitzkreig** |  | Acc +1, Spd +5, HP +8 | Stance |  | stanCe (costs 1 AP to enter)<br>You select the next foe and your allies attack. When you enter into this stance, you select a single target within 50 feet. All of your allies gain a speed bonus when moving toward that target. The bonus is 10 feet, plus 5 feet for every 5 skill points you have in tactical (thus being +15 feet at 5 skill points, +20 feet at 10 skill points, et cetera). | [STANCE] [SCALE:Tactical] 10 + 5×floor(Tac/5) |
| **Call in a Favor** |  | Acc +1, Eva +1, HP +7 | Give 3 AP | 4 Tactical | reQuires: 4 skill points in Tactical<br>When you’re cornered, you call in the guy with the sword to get you out of your dangerous situation. You can give an ally 3 of your action points in order for the ally to run over and attack an opponent adjacent to you. The ally must be willing to make the move and the attack. They may only use these action points for moving toward the designated opponent and attacking, though they may use the action points to upgrade the attack as they see fit. In addition, if the ally has any action points of their own, they may choose to use them reflexively to continue attacking or bolster their attack on the opponent adjacent to you. | [ACTION] [REQ] |
| **Change Formation** |  | Eva +1, Pri +2, HP +7 | 2 AP |  | Cost: 2 AP<br>You call for an immediate change of formation. All of your allies within 50 feet are automatically allowed to change their stance, free of cost, at their discretion. | [ACTION] |
| **Change Places** |  | Eva +1, Spd +5, HP +6 | 1 AP |  | Cost: 1 AP<br>You know where the forces that threaten your team members lie. You can move your ally (as long as your ally is willing). Your ally moves 5 feet<br>Your ally moves 10 feet<br>Your ally moves 15 feet<br>Your ally moves 20 feet | [ACTION] |
| **Crippling Formation** |  | Acc +1, Stk +2, HP +7 | Passive | 3 Tactical | reQuires: 3 skill points in Tactical<br>When an ally makes a called shot within 25 feet of you, you make the shot more difficult to resist. The called shot’s strike roll is effectively 1 point higher for every 3 skill points you have in tactical. This only changes the resist and does not increase the damage or the effect. | [COND] [SCALE:Tactical] |
| **Crossfire** |  | Acc +1, Stk +2, HP +8 | Stance |  | stanCe (costs 1 AP to enter)<br>When you enter this stance, choose a single location (a 5 foot square). If anybody enters into that space, you and all of your allies can make reflexive attacks against that person for only 1 action point. | [STANCE] |
| **Forewarned** |  | Acc +1, Pri +4, HP +6 | 1 AP reflexive (from first turn) |  | Cost: 1 AP reflexively<br>When priority is called for at the beginning of a battle, you may give a +3 to an ally’s priority roll within 25 feet, plus an additional +1 per 3 skill points you have in tactical. Doing so costs 1 action point reflexively (which comes from your first turn’s pool of action points). | [REFLEX] [SCALE:Tactical] |
| **Focused Support** |  | Acc +1, Stk +2, HP +6 | 2 AP to begin, 1 AP/turn | 7 Tactical | reQuires: 7 skill points in Tactical<br>Cost: 2 AP to begin, 1 AP to continue during subsequent turns You can build a bond with another that pushes them to greatness. When you begin your focused support, you choose an ally within<br>25 feet. That ally gains 1 additional action point per turn for as long as you are within 25 feet and continue focusing your support. If you want to change the beneficiary of your focused support, you must begin anew. You can only have one focused support active at any given time. | [ACTION] [REQ] |
| **Lead the March** |  | Pri +2, Spd +5, HP +6 | 1 AP |  | Cost: 1 AP<br>When you lead the march, you give your allies within 25 feet a bonus to their speed. This bonus lasts until the end of your next turn (when your action points refresh). This bonus is granted to you as well. Multiple bonuses from Lead the March do not stack. Speed increases by 10 feet<br>Speed increases by 20 feet<br>Speed increases by 30 feet<br>Speed increases by 40 feet | [ACTION] |
| **Malleable Formation** |  | Acc +1, Spd +5, HP +7 | Passive |  | Your allies can shift and move around the battlefield with ease, keeping your enemies guessing. All allies within 25 feet of you can make a 5 foot movement during their turn for 0 action points. | [COND] aura |
| **Master Tactician** |  | Acc +1, Pri +3, HP +8 | Passive | 15 Tactical | reQuires: 15 skill points in Tactical<br>You’re at your best when thinking on your feet. You receive 1 extra action point per turn which may be used only for reflexes. | [PASSIVE] [REQ] AP +1 (reflex only) |
| **Stand-Off** |  | Eva +1, Pri +2, HP +6 | 1 AP reflexive |  | Cost: 1 AP reflexively<br>Before anybody takes their first turn in a combat, right as priority is about to be determined, you may call for a stand-off. This costs<br>1 action point, but puts the entire combat in a stand-off. Anybody may voluntarily take the first action, but - if they do so - every roll they make during their first turn suffers a penalty equal to your skill in tactical.<br>If multiple people attempt to act first in a stand-off, they roll priority between themselves. After the first person in a standoff acts, everyone determines priority normally and moves after the stand-off breaker. | [REFLEX] [SCALE:Tactical] |
| **Encouragement** | Encouraging | Eva +1, Spd +5, HP +6 | 1 AP reflexive |  | Cost: 1 AP reflexively<br>You call out encouragement, urging your allies to a more assured victory. For 1 action point reflexively, you may give an ally within<br>50 feet a bonus on any one of the following rolls: accuracy, evade, strike, or defense. This bonus must be determined before the roll is made.<br>+2<br>+4<br>+6<br>+8 | [REFLEX] |
| **Inspiring Words** | Encouraging | Eva +1, Pri +2, HP +8 | Passive | 5 Tactical; Encouragement | reQuires: 5 skill points in Tactical & Encouragement specialty Your words of encouragement invoke a deep drive within your allies that brings about confidence, allowing them to continue battling. When using encouragement, all of your within 50 feet recover 1 hit point plus 1 for every 10 skill points you have in tactical. | [COND] [REQ] |
| **Direct the Battle** | Flow Of Battle | Acc +1, Eva +1, HP +8 | Stance |  | stanCe (costs 1 AP to enter)<br>You set the course of battle, proclaiming the next victim of the tide. When you enter this stance, you choose one enemy within 50 feet to be the victim. While you are in this stance, you can allow a single ally per turn to make a special attack or called shot that costs “Attack +1 AP,” without spending the extra action point, so long as it is directed at the target of the stance. | [STANCE] |
| **Concentrated Barrage** | Flow Of Battle | Acc +1, Stk +2, HP +7 | Passive | Direct the Battle | reQuires: Direct the Battle specialty<br>When you enter into your direct the battle stance, you point at a single target and exclaim, “Get that fool!” Every ally within 25 feet can make a special attack or called shot that costs “Attack +1 AP” against the target of your direct the battle stance without spending that extra action point, though each ally only gets this benefit once per turn. | [COND] [REQ] |
| **Overwhelm** | Flow Of Battle | Acc +1, Eva +1, HP +9 | 1 AP reflexive | Direct the Battle | reQuires: Direct the Battle specialty<br>Cost: 1 AP reflexively<br>Any time the target of your direct the battle stance takes damage from an ally, you may use 1 action point to encourage your ally’s attack along.<br>Ally’s attack does an additional 3 damage<br>Ally’s attack does an additional 6 damage<br>Ally’s attack does an additional 9 damage<br>Ally’s attack does an additional 12 damage | [REFLEX] [REQ] |
| **Issue Orders** | Order | Acc +1, Eva +1, HP +7 | 3 AP |  | Cost: 3 AP<br>You yell an order across the battlefield, and one of your allies answers the call. The ally must be within 50 feet and be able to hear you. Your order allows an ally to make a called shot using their bonuses but without spending any of their action points. Ally attempts the called shot<br>Ally attempts the called shot with a +2 on the strike Ally attempts the called shot with a +4 on the strike Ally attempts the called shot with a +6 on the strike | [ACTION] |
| **Complex Orders** | Order | Acc +1, Pri +3, HP +8 | Extra AP = modifier cost | Issue Orders; 5 Tactical | reQuires: Issue Orders specialty & 5 skill points in Tactical When giving an ally a called shot order, you may spend the cost of one of your ally’s attack-modifying specialties to allow that ally to use that attack modifier for free.<br>For instance, if your ally knows Solid Assault (under Overpower) you may spend an extra action point in addition to the Issue Orders cost in order to allow your ally to use their attack modifier for free. This additional action point expenditure can utilize the action point bonus fromDirect the Battle. | [ACTION] [REQ] |
| **Improved Orders** | Order | Acc +1, Eva +1, HP +8 | Passive | Issue Orders; Complex Orders; 8 Tactical | reQuires: Issue Orders specialty, Complex Orders specialty, & 8 skill points in Tactical<br>You are becoming more adept at giving orders to your allies, allowing you 1 free action point per turn for use with the effects of Complex Orders. | [PASSIVE] [REQ] |

### 6.5 Dexterity specialties

**What anyone can do with Dexterity (attribute uses):** Balance (move +1 AP; T1 barely, fall on any other action / T2 re-roll if conditions change or other actions / T3 confident / T4 as solid ground) · Jumping (as a move; long jump T1 10 / T2 20 / T3 30 / T4 40 ft, half without 20-ft run-up; vertical 1 ft per 5 ft forward; catching a ledge usually T2) · Sneaking (move +1 AP, opposed vs listener's Cunning; armor −6, noisy terrain −3 at narrator discretion) · Pickpocket (2 AP, resist Cunning tiers down; one unequipped item)

#### Ace

| Specialty | Group | Bonuses | Cost / type | Requires | Effect | Tags |
|---|---|---|---|---|---|---|
| **Backseat Driver** |  | Acc +1, Eva +1, HP +9 | Stance |  | stanCe (costs 1 AP to enter)<br>While in the Backseat Driver stance, you utilize your ability as a pilot or rider to provide the person who is driving with useful information, allowing them to react more quickly to situations. While you are in this stance, the pilot of a vehicle that you are riding (or the rider of the animal you are on) gets a bonus action point per turn that can be used for maneuvering the vehicle or mount or using Ace specialties. | [STANCE] |
| **Co-Pilot** |  | Acc +1, Eva +3, HP +8 | Reflexive |  | You make a remarkably handy co-pilot when the need arises. If adjacent to a ship’s pilot, you may give them any number of your action points, reflexively, for the pilot to use while maneuvering, accelerating, or slowing the vehicle. | [REFLEX] |
| **Crash Maneuver** |  | Acc +1, Def +3, HP +9 | 3 AP reflexive |  | Cost: 3 AP reflexively<br>When you are driving an airborne vehicle that is crashing to the ground, you can maintain your cool and attempt to prevent yourself from getting hurt in the crash. When the vehicle hits the ground, you can wrest enough control of the vehicle to keep it on a steady path. If you do so, everyone in the vehicle takes less falling damage. The amount depends on the tier of your roll.<br>-3 wounds damage<br>-6 wounds damage<br>-9 wounds damage<br>-12 wounds damage | [REFLEX] |
| **Denial Maneuver** |  | Eva +2, Pri +1, HP +7 | 2 AP reflexive |  | Cost: 2 AP reflexively<br>You twist the vehicle’s controls at the last minute, making it difficult to target specific sections of your vehicle. When someone makes your vehicle the target of their attack, you can spend 2 action points in order to add your Ace skill to the ship’s evade roll. | [REFLEX] [SCALE:Ace] |
| **Driving with Knees** |  | Acc +1, Eva +1, HP +8 | Stance |  | stanCe (costs 1 AP to enter)<br>You are able to control your vehicle or animal mount using your knees. If you are on an animal mount or driving a clanker, you get one free movement per turn. It also requires no hands to pilot your vehicle or animal mount. | [STANCE] |
| **Flying Fortress** |  | Acc +1, Def +3, HP +7 | 2 AP to begin, 1 AP/turn | 2 Ace | reQuires: 2 skill points in Ace<br>Cost: 2 AP to begin, 1 AP to continue during subsequent turns When piloting a vehicle, you are able to maneuver it so that incoming attacks won’t hit anything vital to its continued functioning, ensuring the ultimate defense. Your vehicle gains +1 defense for every 2 points you have in Ace. | [ACTION] [REQ] [SCALE:Ace] vehicle Def += floor(Ace/2) |
| **Hold Together** |  | Eva +1, Def +3, HP +8 | Passive | 7 Ace | reQuires: 7 skill points in Ace<br>During its final moments, even if everything is falling apart around you, you push your vehicle forward one last time. If a vehicle you’re piloting loses all of its wounds, you can still move it normally for one more turn. Autos are forced to remain on their previous speed setting during this final turn. | [COND] [REQ] |
| **Horseman's Cut** |  | Acc +1, Stk +3, HP +7 | Mounted melee attack +1 AP |  | Cost: Mounted Melee Attack +1 AP<br>When attacking a non-mounted opponent atop your mount or vehicle, you are able to make a horsemen’s cut that deals extra damage.<br>+1 damage class<br>+2 damage class<br>+3 damage class<br>+4 damage class | [ATTACK+1] |
| **Hostile Maneuvers** |  | Acc +1, Stk +2, HP +9 | 2 AP to begin, 1 AP/turn | 5 Ace | reQuires: 5 skill points in Ace<br>Cost: 2 AP to begin, 1 AP to continue during subsequent turns You move wrecklessly close to an opponent’s vehicle in an all out siege. While using Hostile Maneuvers, your vehicle suffers -4 defense; however, all attacks made by allies on your vehicle hit for 1 damage class higher for every 5 points you have in Ace. | [ACTION] [REQ] [SCALE:Ace] |
| **Level Flying** |  | Acc +1, Pri +3, HP +8 | Passive |  | While you’re at the helm, nobody on board takes accuracy penalties for shooting from a fast moving vehicle. | [COND] |
| **Quick-Mount** |  | Acc +2, Pri +1, HP +6 | Passive (once per turn) |  | You can now mount or dismount any auto, clanker, or animal mount for no action point cost during your turn, whether you intend to pilot the vehicle or not. You can only make one such quick mounting or dismounting per turn. | [PASSIVE] |
| **Vehicular Teamwork** |  | Acc +1, Eva +1, HP +10 | 2 AP reflexive |  | Cost: 2 AP reflexively<br>When anything flies toward your vehicle, your gut instinct is to move out of the way. When anyone on your piloted vehicle is the target of an attack, you can attempt to move your entire vehicle out of the way first. Before they roll evade, you may roll your vehicle’s evade against the attack. The attacker only rolls accuracy once. If either your vehicle or your passenger roll higher than the accuracy of the attack, the attack misses. | [REFLEX] |
| **Strafe** | Auto Piloting | Acc +1, Eva +1, HP +9 | Free, once per turn |  | You know how to quickly move your auto side-to-side. Once per turn, you can strafe for no action point cost. This does not change the direction your auto is travelling in.<br>5 feet<br>10 feet<br>15 feet<br>25 feet | [ACTION] |
| **Evasive Strafe** | Auto Piloting | Eva +1, Def +2, HP +7 | Passive | Strafe | reQuires: Strafe specialty<br>The quick movements of your auto allow you to shake off incoming attacks. When you strafe, your vehicle gains a bonus to evade until the beginning of your next turn. This bonus is taken away if you stop piloting the vehicle.<br>+1 evade<br>+2 evade<br>+3 evade<br>+4 evade | [COND] [REQ] |
| **Extension of Self** | Clanker Piloting | Acc +1, Eva +1, HP +9 | Passive |  | The movements of your clanker are as smooth as the movements of your body. When piloting a clanker you can move it using any specialty you have related to moving yourself. When doing so, use your skill in Ace for the specialty instead of your skill in the skill the specialty comes from. This does not allow you to move your clanker in ways it can’t on its own, such as jumping or flying. | [PASSIVE] |
| **Piston-Spring** | Clanker Piloting | Eva +1, Def +2, HP +10 | Jump |  | Cost: Jump<br>Whenever piloting a clanker, you have the ability to use its momentum to propel it into the air. This allows you to jump your clanker just like a normal person jumps. | [ACTION] |
| **Focused Flying** | Focusing Flying | Acc +1, Def +3, HP +8 | Stance (both hands on controls, no other actions) |  | stanCe (costs 1 AP to enter)<br>With both hands on the wheel and every ounce of your being put into your piloting, your control of your vehicle greatly increases. While in this stance, you cannot take any action other than controlling your vehicle. You also must use two of your hands to hold onto the controls of your vehicle. Clankers gain 5 feet of speed for every point you have in Ace. Autos gain 10 feet of maximum speed for every point you have in Ace. | [STANCE] [SCALE:Ace] |
| **Fine-Tuned Flying** | Focusing Flying | Def +3, Pri +2, HP +7 | Passive | Focused Flying; 2 Ace | reQuires: Focused Flying specialty & 2 skill points in Ace You put your all into ensuring any attacks made on your vehicle will not penetrate its armor. While in your Focused Flying stance, your vehicle gains a +1 to defense for every 2 skill points you have in Ace. | [COND] [REQ] [SCALE:Ace] |
| **Fully Focused Flying** | Focusing Flying | Acc +1, Eva +1, HP +8 | Passive | Focused Flying; 3 Ace | reQuires: Focused Flying specialty & 3 skill points in Ace By making the continued survival of your vehicle and its crew your main priority, you make yourself more aware of incoming attacks. While in your Focused Flying stance, your vehicle gains a<br>+1 to evade for every 3 skill points you have in Ace. | [COND] [REQ] [SCALE:Ace] |
| **Fearless Mount** | Mounted Cavalry | Acc +1, Pri +3, HP +8 | Passive | 3 Ace | reQuires: 3 skill points in Ace<br>You let your mountable animal know you’re the one in charge. When riding an animal mount, the animal is immune to fear effects. In addition, the animal will be willing to do anything you ask of it (as long as it is capable). | [PASSIVE] [REQ] |
| **One with the Beast** | Mounted Cavalry | Stk +2, Def +2, HP +10 | Stance (mounted) |  | stanCe (costs 1 AP to enter)<br>When mounted, you and your animal mount are perfectly in-sync. You may add its strike and defense bonuses to yours. In addition, your mount may not be directly attacked; you take all incoming attacks, be they aimed at you or your mount. | [STANCE] [STAT:Stk,Def += mount's] |
| **Ram** | Ramming | Acc +1, Stk +3, HP +7 | Move + 1 AP |  | Cost: Move + 1 AP<br>You know how to ram your vehicle into things without damaging yourself. For an extra action point during a move, you can slam the vehicle you’re piloting into a target. This has a damage class of 10. For autos, use your accuracy to tier damage. Clankers will use your strike to tier damage. Ramming anything immediately ends your move, even if you miss. | [ACTION] |
| **Puncture** | Ramming | Acc +1, Def +3, HP +9 | Ram +1 AP |  | Cost: Ram +1 AP (typically the same as Move +2 AP) When you ram a target providing cover, you break it apart. Whether attacking a solid wall or an armored vehicle, you can lower the degree of cover your target provides while still dealing damage. The cover is lowered in degree until someone repairs it during a period of downtime.<br>-1 degree of cover<br>-2 degrees of cover<br>-3 degrees of cover<br>-4 degrees of cover | [ATTACK+1] [REQ:Ram (book omits explicit req)] |

#### Agility

| Specialty | Group | Bonuses | Cost / type | Requires | Effect | Tags |
|---|---|---|---|---|---|---|
| **Battlefield Flow** |  | Eva +1, Pri +2, HP +7 | 0 AP (once between your refreshes) |  | Cost: 0 AP<br>You’re constantly ready to move to a more strategic (or just plain safer) location. You can move 5 feet for free at any point during your turn, or you can do so at the end of any other person’s turn (when their action points refresh). You can only make one such<br>5-foot movement per your turn (that is, between the refreshing periods of your action points). | [ACTION] |
| **Bounding Lunge** |  | Acc +1, Spd +5, HP +7 | Move + attack |  | Cost: Move + Attack<br>You move and make a swipe at an opponent. By using your bounding lunge, you can begin a normal move, attack an opponent during the move, and then finish the same move. | [ACTION] |
| **Charging Ram** |  | Stk +2, Spd +5, HP +6 | Move + melee attack |  | Cost: Move + Melee Attack<br>When you rush toward an opponent, you mean to take them down with one swing. When you move toward an opponent, you gain a bonus on your strike roll equal to +1 for every 5 feet you spend moving toward them. This movement must all be in a straight line, can only come from a single move action, and must be your movement (it cannot be from a vehicle or mount). | [COND] [SCALE:distance] |
| **Free Movement** |  | Pri +2, Spd +5, HP +6 | Free, once per turn | medium or lighter armor | Movement is becoming a way of life. Once per turn (and only during your turn), you can make a single free movement. You must be in medium or lighter armor to do this.<br>10 feet<br>20 feet<br>30 feet<br>40 feet | [ACTION] [REQ:armor≤medium] |
| **Groundfighting** |  | Eva +2, Pri +2, HP +7 | Passive |  | You’re an old hand at hugging the ground and attacking like an erupting geyser. You may switch from standing to prone and back again for no action point cost. You take no penalties for fighting while prone. You take no penalties for fighting in tight areas. | [PASSIVE] |
| **Instant Draw** |  | Acc +1, Pri +3, HP +7 | Passive |  | In your hand or not, it doesn’t matter. You can draw your weapon and other items without using any action points and at any point (even during another person’s turn). You draw items and weapons so fast that you do not leave yourself open to reflexives. (Activating items still leaves you open to reflexives.) | [PASSIVE] |
| **Slow Falling** |  | Acc +1, Eva +2, HP +6 | 2 AP reflexive (must be next to a surface) |  | Cost: 2 AP reflexively<br>When you fall, you are adept at finding ways to slow your decent. You may ignore however much falling distance as your tier result allows. You must be adjacent to something when you’re falling (such as a wall, or through a canopy of trees). You cannot slow your fall in open air. In addition, you can make attacks against enemies along the line of decent or upon landing for no penalty.<br>30 feet<br>60 feet<br>120 feet<br>200 feet | [REFLEX] |
| **Side-Swipe** |  | Acc +1, Eva +1, HP +9 | As melee attack, reflexive |  | Cost: As a melee attack reflexively<br>When an opponent over-extends their attack, your dodge allows you to take advantage of their failure. When you successfully evade a melee attack, you can make a side-swipe with any onehanded melee weapon against your attacker. You can optionally move 5 feet around your opponent (staying adjacent to the attacking opponent) at no additional action point cost. You gain a bonus on your accuracy roll for every point that the attacker’s original accuracy roll missed you by. | [REFLEX] [SCALE:miss margin] |
| **Slipstreaming** |  | Acc +1, Spd +5, HP +8 | Move + 1 AP | 4 Agility | Cost: Move + 1 AP<br>reQuires: 4 skill points in Agility<br>Your incredible speed sets the pace for your allies. For an additional action point while moving, you can designate your exact path as a slipstream line. If any of your allies follow the path of your slipstream for at least 15 feet within the next turn (before the next time your action points refresh), they can make that move at no cost.<br>Note: If the ally would normally require multiple action points to move, they may use your slipstream to move for 1 less action point than they otherwise would. | [ACTION] [REQ] |
| **Snake Bite** |  | Acc +1, Pri +3, HP +7 | 1 AP (first AP of your turn) |  | Cost: 1 ap<br>You lash out at an opponent like a coiled snake before following through with the rest of your attack. You may use your first action point of your turn to make a normal, unaltered melee attack with a medium or smaller weapon. No specialties may alter this attack. | [ACTION] [GEAR] AP=1 |
| **Step Back** |  | Acc +1, Eva +1, HP +7 | 1 AP reflexive |  | Cost: 1 ap reflexively<br>Just before you’re about to take a pounding, you skip back a couple feet and barely dodge the attack. After failing to evade, you may attempt to step back. Roll your agility. If your agility result is a tier higher than the opponent’s damage tier, then you can ignore the blow and move to any adjacent square that is not adjacent to the attacking opponent.<br>If the opponent rolls tier 4 damage, there is no way to step back from it. | [REFLEX] |
| **Terrain Mastery** |  | Pri +4, Spd +5, HP +9 | Passive |  | You excel at crossing a wide variety of landscapes. You ignore penalties for moving through rough terrain. | [PASSIVE] |
| **Wall Runner** |  | Acc +1, Spd +5, HP +8 | Move +1 AP (1 AP with Free Movement) | 6 Agility | reQuires: 6 skill points in Agility<br>Cost: move +1 ap<br>Your feet move so quickly that you can bound up walls. When wall running, if you end your turn (though not necessarily your move) on a vertical surface, you will slip and fall off of it. Note: You may also use this specialty in conjuction with Free Movement for just 1 action point. | [ACTION] [REQ] |
| **Walk Over** |  | Eva +1, Spd +5, HP +7 | Passive |  | A row of enemies form little blockade against you. You can pass through a space occupied by an enemy as though the enemy wasn’t even there. If for some reason this would allow the enemy to attack you, they are denied that privelage. You cannot end your movement in their space - you must pass through. | [PASSIVE] |
| **Blast Dodger** | Explosion Dodging | Eva +1, Spd +5, HP +8 | 0 AP, once per turn |  | Perhaps it’s your nerves, perhaps you’ve been caught up in explosions too many times. Regardless, you’re always ready to get out of dodge. You may jump out of the way of a blast, once per turn, for 0 action points. | [REFLEX] |
| **Soaring Dodge** | Explosion Dodging | Eva +1, Pri +3, HP +9 | 1 AP reflexive per 5 Agility | 5 Agility | reQuires: 5 skill points in Agility<br>Cost: 1 AP reflexively<br>Large blast radiuses? It’s not anything you can’t get out of. While you are dodging a blast, you may spend an additional action point reflexively per 5 skill points you have in agility in order to make extra moves and escape the blast radius. | [REFLEX] [REQ] [SCALE:Agility] |
| **Phase Step** | Phasing | Eva +1, Spd +5, HP +7 | Move; resist Cunning (negates) |  | resist: Cunning (negates)<br>Cost: Move (normally 1 AP)<br>When you move, you may instead phase step. When you phase step, you move quickly and in a way hard to notice. In order to hit you while you move, an opponent must make a Cunning resist against your agility to even notice your movement. | [ACTION] |
| **Fleeting Shade** | Phasing | Eva +1, Spd +5, HP +6 | Move | Phase Step | reQuires: Phase Step specialty<br>Cost: Move<br>Face it, it’s a whole lot harder to hide yourself in broad daylight. When phase-stepping from the open to a hiding place, you may roll below to give yourself a bonus to your dexterity against opponents attempting to notice you so you can get hidden fast.<br>+3 against enemies’ resists in attempt to see you.<br>+6 against enemies’ resists in attempt to see you.<br>+9 against enemies’ resists in attempt to see you.<br>+12 against enemies’ resists in attempt to see you. | [ACTION] [REQ] |
| **Leave No Trace** | Phasing | Eva +1, Spd +5, HP +6 | Move reflexive | Phase Step | reQuires: Phase Step specialty<br>Cost: Move (reflexively)<br>You constantly move through the shadows so that enemies will never be able to keep track of you or where you’ve been. You may Phase Step reflexively when enemies attempt to find you in your hiding place. | [REFLEX] [REQ] |
| **Shifting** | Stance-Shifting | Acc +1, Eva +1, HP +7 | 1 AP reflexive | 2 stances known | reQuires: 2 stances known<br>Cost: 1 AP reflexively<br>You have learned how to switch between your stances using only slight movements, keeping your enemy in the dark about your next strike. When you are in one of your stances, you can shift to another stance at any time, during anybody’s turn. | [REFLEX] [REQ] |
| **Freeform Shifting** | Stance-Shifting | Acc +1, Eva +1, HP +8 | 0 AP once per turn | 12 Agility; Shifting; 3 stances known | reQuires: 12 skill points in Agility, Shifting specialty, & 3 stances Your feet are constantly moving, guaranteeing your opponent never has a clue. You may now use Shifting at no action point cost once per combat turn (between the times when your action points refresh). | [REFLEX] [REQ] |

#### Marksmanship

| Specialty | Group | Bonuses | Cost / type | Requires | Effect | Tags |
|---|---|---|---|---|---|---|
| **Aim** |  | Acc +2, Eva +1, HP +5 | 1 AP per aim roll | 4 Marksmanship | reQuires: 4 skill points in Marksmanship<br>Cost: 1 AP<br>Before you take your shot, you can spend some time lining up your sights and aiming. You can spend any number of action points preparing yourself, and, for every action point you spend aiming, you may roll on the chart in order to gain a bonus to your accuracy. You can start aiming one turn and then fire in a subsequent turn, but if you are attacked after you start aiming (but before you fire), you lose any bonus you would’ve gained from aiming. You cannot gain any more accuracy to an attack than you have skill in marksmanship.<br>+1 to the accuracy roll<br>: +2 to the accuracy roll<br>+3 to the accuracy roll<br>+4 to the accuracy roll | [ACTION] [REQ] [SCALE:Marksmanship cap] |
| **Cover Fire** |  | Acc +1, Eva +2, HP +6 | As ranged attack |  | Cost: as a Ranged Attack<br>While you don’t mind hitting the target, the real goal is to prevent the target from firing at your friend. When you provide cover fire, you take a -6 on your accuracy rolls but also provoke the target into attacking you (see Social Tells in the Chapter 1). You gain a bonus on the cunning roll equal to your skill in marksmanship. | [ATTACK+0] [SCALE:Marksmanship] |
| **Follow Up** |  | Acc +1, Eva +1, HP +7 | Passive |  | When you figure out how to nail that bastard, it’s not hard to do it again. If you land a ranged attack on a target and they do not move from their space before you attack again, you gain a bonus to accuracy and strike for you second attack. As long as the opponent does not move, the bonus continues with every subsequent attack. You do not gain the bonus multiple times; however, you may re-roll with every subsequent attack to gain a higher bonus, at your discretion.<br>+2 to accuracy and strike<br>+4 to accuracy and strike<br>+6 to accuracy and strike<br>+8 to accuracy and strike | [COND] |
| **Head Popper** |  | Acc +1, Eva +1, HP +7 | 1 AP reflexive |  | Cost: 1 AP reflexively<br>When they stick their head out of cover, you pop them right quick. When a foe leaves cover (to any degree), you can instantly make a reflexive ranged attack against them for 1 action point. If there is any dispute as to who gets to make the first attack, you win (unless there are two people with Head Popper, in which case it’ll be decided by a priority roll). | [REFLEX] |
| **Itchy Trigger Finger** |  | Eva +2, Pri +3, HP +8 | Passive |  | Your friends might think you just randomly shot a bush, but you know better. If you have even the inkling that there’s somebody sneaking around within your gun’s range and you’re not aware of them, you can try to shoot them. You take the normal penalties for firing blindly, but they are still targeted. If there are multiple people sneaking around, your shot will target the closest one. If you miss, there is no reason the sneaking person will be identified, and you’ll probably just assume that there is nobody there. | [COND] |
| **Knock-Off** |  | Acc +2, Pri +2, HP +6 | Ranged attack +1 AP; resist Dex (negates) |  | resist: Dexterity (negates)<br>Cost: Ranged Attack +1 AP<br>You take aim at a mounted opponent and attempt to shoot them off their mount or personal vehicle. Use your skill in marksmanship in a roll-off against their dexterity. If you succeed, they are thrown off of their mount or personal vehicle. | [ATTACK+1] |
| **Lockdown Gunner** |  | Acc +1, Pri +3, HP +8 | Passive (reflexive) |  | When the villain pulls out his doomsday device or the assassin draws a vial of poison, you’ll snipe it right out of their hands. You can reflexively attack from a range whenever anybody draws or activates an item. (And, as per normal, you can always make this a called shot to their hand in order to disarm them of the item.) | [REFLEX] |
| **Long Shot** |  | Acc +2, Pri +1, HP +7 | Ranged attack +1 AP |  | Cost: Ranged Attack +1 AP<br>You test the air and adjust accordingly, doubling the range that your weapon is accurate to. (Shooting beyond that range takes accuracy penalties as is normal for your weapon.) | [ATTACK+1] [GEAR] range ×2 |
| **Penetrating Shot** |  | Acc +1, Eva +1, HP +8 | Ranged attack +1 AP |  | Cost: Ranged Attack +1 ap<br>You use your ranged weapon in such a way that their armor offers little protection. For the purposes of this attack, lower your opponent’s soak class by 1 for every tier that you receive with your marksmanship roll. This does not permanently affect the armor. Ignores 1 soak class<br>Ignores 2 soak class<br>Ignores 3 soak class<br>Ignores 4 soak class | [ATTACK+1] |
| **Point Blank** |  | Acc +1, Eva +1, HP +7 | Ranged attack +1 AP |  | Cost: Ranged Attack +1 AP<br>When your opponent’s up close, you don’t lose your calm. You just shoot them. You can make a point blank attack when using a ranged weapon against an adjacent opponent. You gain an immediate accuracy bonus for making the point blank attack.<br>+3 accuracy<br>+6 accuracy<br>+9 accuracy<br>+12 accuracy | [ATTACK+1] |
| **Seeker** |  | Acc +2, Pri +1, HP +7 | Passive |  | By focusing in on the opponent, you can ignore their cover bonuses. Any time an opponent is being granted evade bonuses from cover, you may ignore it up to your skill in marksmanship. Thus, if they have light cover (granting them a +4 to evade) and you have 3 points in marksmanship, they only receive a +1 to evade. | [COND] [SCALE:Marksmanship] |
| **Snap Reload** |  | Acc +1, Pri +4, HP +6 | Passive |  | You’ve been in enough gunfights that you’re quite proficient at readying your firearms and crossbows. You can ready any firearm or crossbow that you’re wielding for one less action point (to a minimum of 0). If you are wielding two or more crossbows or firearms, each one gains the reduction from snap reload. Dexterity<br>Chapter | [PASSIVE] [GEAR] AP to Ready −1 |
| **Sneaky Seconds** |  | Acc +1, Eva +1, HP +7 | Passive | 4 AP per turn | reQuires: 4 action points per turn<br>You let off two shots so fast that, though they might evade the first one, they’re going to run straight into the second. Sneaky seconds activates immediately upon two consecutive ranged attacks being made in the same turn. Regardless of whether the first attack hits or not, the second ranged attack gains a bonus to its accuracy equal to your skill in marksmanship for determining if it hits (damage remains the same).<br>Note: If you can make a third attack in the turn, it does not gain the sneaky seconds bonus. That said, a fourth attack would! | [COND] [REQ:AP≥4] [SCALE:Marksmanship] |
| **Stable Shot** |  | Acc +1, Def +2, HP +8 | Passive | 3 Brute (book says "3 points in Brute") | reQuires: 3 points in Brute<br>You no longer need to be in footing stance to fire a super-heavy bow, crossbow, or firearm. You may do it from a standing, normal position. | [PASSIVE] [GEAR] [REQ] |
| **Turret** |  | Acc +1, Eva +1, HP +5 | Stance (stationary, standing, not mounted) |  | stanCe (costs 1 AP to enter)<br>You find the perfect spot on the battlefield. You sweep around the field, raise your rifle, and fire. Nothing’s going to get to you. While in this stance, you cannot move. You must be stationary and on your feet (you cannot be mounted). If you move, you fall out of your turret stance. For 2 action points reflexively, you can make a ranged attack at anything that moves so much as five feet toward you.<br>If anybody comes into a space adjacent to you, you can make ranged attacks against them for 1 action point during your turn and with a bonus to your damage class, if you hit.<br>+1 damage class<br>+2 damage class<br>+3 damage class<br>+4 damage class | [STANCE] |
| **Warning Shot** |  | Acc +2, Pri +1, HP +7 | As ranged attack |  | Cost: as a Ranged Attack<br>You can take a shot designed to miss, but also designed to scare the gods out of the target. When you take a warning shot, no attack rolls are necessary - instead, you may roll your cunning to intimidate the person from afar (see Social Tells in Chapter 1). You gain a bonus on the intimidation roll equal to your skill in marksmanship. | [ACTION] [SCALE:Marksmanship] |
| **Wing Clipping** |  | Acc +2, Eva +1, HP +6 | Ranged attack +1 AP; resist Brute (physical flight) or Sciences (mechanical) |  | resist: Brute (if the method of flight is physical) or Sciences (if the method of flight is mechanical)<br>Cost: Ranged Attack +1 AP<br>You take aim at a foe flying under their own power and shoot them out of the sky. Use your skill in marksmanship in a roll-off against their resist. If you meet or exceed their resist, you successfully disable their ability to fly. They will be able to fly again once they either successfully resist or they hit ground. They can attempt to resist for free at the end of their turn (when their action points refresh) or by spending 1 action point at any time. Note: If the target has multiple ways of flying, wing clipping will only disable one at a time. | [ATTACK+1] |
| **Arching Shot** | Archery | Acc +1, Stk +3, HP +7 | Bow attack +1 AP |  | Cost: Bow Attack +1 AP<br>You can now make an arching shot. An arching shot is one in which you launch your arrow higher into the air, planning for it to come down at just the right spot to strike your opponent. When using an arching shot, your bow can shoot accurately another 25 feet per point you have in your marksmanship skill. To make this attack, you cannot have a ceiling within 100 feet, | [ATTACK+1] [GEAR] [SCALE:Marksmanship] |
| **Efficient Ranger** | Archery | Acc +1, Stk +2, HP +7 | Passive | 3 Marksmanship | reQuires: 3 skill points in Marksmanship<br>You nock your arrow, pull the string back, and release as though you’ve been doing it since you were a wee babe. You may now make attacks with heavy and super-heavy bows for 2 action points instead of the normal 3. | [PASSIVE] [GEAR] [REQ] bow AP=2 |
| **Flight of Arrows** | Archery | Acc +1, Stk +3, HP +8 | Bow attack +1 AP |  | Cost: Bow Attack +1 AP<br>You release a flight of arrows, having nocked multiple arrows all at once. Make your normal attack. If you hit, instead of doing damage with your strike, you act as if you hit them multiple times with tier 1 damage. Each arrow may be soaked by the opponent’s defense.<br>2 arrows that deal tier 1 damage<br>3 arrows that deal tier 1 damage<br>4 arrows that deal tier 1 damage<br>5 arrows that deal tier 1 damage<br>Note: A flight of arrows acts as multiple attacks for the purposes of determining damage, but other abilities (such as other attackmodifying specialties or bow augments) only affect the target once if they’re applied to the flight of arrows. | [ATTACK+1] |
| **Flesh Biter** | Bleeding Arrow | Acc +1, Stk +2, HP +7 | Bow attack +1 AP |  | Cost: Bow Attack +1 AP<br>You’ve got a knack for using arrows to make the target bleed out. When making a flesh biter attack, the arrow causes the target to start bleeding out. They’ll continue to bleed until they spend 1 action point to stop the bleeding (which will stop up to 5 points of bleeding). The damage will incur at the end of their turn (when their action points refresh).<br>2 point of bleeding<br>4 points of bleeding<br>6 points of bleeding<br>8 points of bleeding | [ATTACK+1] |
| **Flesh Piercing** | Bleeding Arrow | Acc +1, Stk +3, HP +6 | Passive | Flesh Biter | reQuires: Flesh Biter specialty<br>Your flesh biting arrows sink in, dealing excrutiating damage every turn until removed. Bleeding done from a flesh biter is difficult to stop, and acts as though it is twice as much when attempting to stop. (Thus, if the target has 4 points of bleeding on them from a flesh biter, it counts as 8 points for the purposes of stopping the bleeding.) | [PASSIVE] [REQ] |

#### Swashbuckling

| Specialty | Group | Bonuses | Cost / type | Requires | Effect | Tags |
|---|---|---|---|---|---|---|
| **Adaptable** |  | Acc +1, Eva +1, HP +7 | Passive | 2 stances known | reQuires: 2 stances known<br>Your footwork is solid, your training and familiarity perfect, and your stances have become second nature. You can always keep one stance active and you cannot be forcibly removed from that stance. When you enter a stance, you can designate it as your background stance. By designating one as your background stance, you can have two stances going at the same time, one as your background stance and one as your normal stance. If you have two stances active, they cannot be mutually exclusive in any way. | [STANCE] [REQ] |
| **Circle Attack** |  | Acc +1, Stk +2, HP +8 | 1 AP reflexive per deflection |  | Cost: 1 AP reflexively (when melee attacking)<br>When the opponent attempts to deflect your attack, you bring your blade around their protections and into their gut. When an opponent attempts to deflect one of your melee attacks, you can spend 1 action point in order to circle around their deflection. This negates their deflection bonus.<br>If the opponent can make multiple deflections against your attack, you may spend 1 action point per deflection to circle around each one. | [REFLEX] |
| **Counter-Stance** |  | Acc +2, Stk +1, HP +6 | Stance; 1 AP reflexive |  | stanCe (costs 1 AP to enter)<br>Cost: 1 AP reflexively<br>You may declare a counter-stance against one opponent. If at any point you are attacked by the marked opponent, you can make a reflexive attack for 1 action point against that opponent, even before they finish their attack. | [STANCE] [REFLEX] |
| **Efficient Strike** |  | Acc +1, Pri +3, HP +8 | Melee attack +1 AP |  | Cost: Melee Attack +1 AP<br>Focusing on the weakest points of your opponent, you are able to home in on their vitals. When you use an efficient strike, you may add the number by which your accuracy roll exceeded your target’s evade roll as a bonus to your strike. | [ATTACK+1] [SCALE:margin] |
| **Fight Anywhere** |  | Eva +2, Spd +5, HP +6 | Passive |  | Hanging off railing and fighting with your sword in your teeth? No problem! You no longer take penalties for fighting on uneven surfaces, awkward terrain, in an unusual position, with your sword in your teeth, or while hanging from a wall. | [PASSIVE] |
| **Hilt Bash** |  | Acc +1, Stk +2, HP +8 | 0 AP reflexive |  | Cost: 0 AP reflexively<br>When somebody attempts to keep you down, you bash them in the face. Any time an adjacent opponent attempts to negate an attack you’re in the process of making, you may instantly make a melee attack against them with the weapon you’re attacking with at no cost. (And no, the hilt bash can’t be negated.) | [REFLEX] |
| **Opening** |  | Acc +1, Pri +2, HP +6 | 1 AP reflexive |  | Cost: 1 AP reflexively<br>Your keen senses notice when somebody stumbles and leaves themself open. If anybody within melee range of you gets a 1 or lower on their evade (when being attacked by another person), you can immediately attack them for 1 action point, using the evade that they rolled to determine if you hit them. | [REFLEX] |
| **Precise Attack** |  | Acc +1, Stk +2, HP +8 | Melee attack +1 AP |  | Cost: Melee Attack +1 AP<br>A precise attack is one that has an improved chance of hitting. You roll your accuracy multiple times and take the highest result to determine if you hit. (If you roll a pure 12, continue rolling to figure out what the final result is. The pure 12 and attached rolls will only count as one roll.)<br>You roll two dice<br>You roll three dice<br>You roll four dice<br>You roll five dice | [ATTACK+1] |
| **Saluted Opponent** |  | Acc +1, Eva +1, HP +6 | Stance |  | stanCe (costs 1 AP to enter)<br>When you enter into this stance, you select one opponent and you salute him. You gain a bonus on your melee accuracy rolls against that opponent equal to your skill in swashbuckling. When you are in this stance, you take a -2 on evade rolls against all attacks from people other than your saluted opponent.<br>To select a new opponent, you must renew your stance for 1 action point | [STANCE] [SCALE:Swashbuckling] |
| **Sword and Board** |  | Acc +1, Eva +1, HP +8 | Stance |  | stanCe (costs 1 AP to enter)<br>You’re a wiz at fending off incoming attacks. While in this stance, you can make one free deflection per turn. | [STANCE] |
| **Wild Slash** |  | Stk +2, Pri +3, HP +8 | As melee attack |  | Cost: as a Melee Attack<br>Instead of a normal melee attack, you can make a wild slash. This is effectively the same as a melee attack, but you determine your accuracy differently. Instead, roll two dice and don’t add your accuracy. Add the results from the two dice, and that is your accuracy roll.<br>If either die shows a 1, the entire roll is a 1. When using a wild slash, 12s do not explode (that is, you do not re-roll 12s and add the next number) unless both dice show 12s, in which case you may roll both again and add the result to 24. | [ATTACK+0] |
| **En-Garde** | En-Garde | Acc +1, Eva +1, HP +8 | Stance (one-handed melee weapon, other hand empty) |  | stanCe (costs 1 AP to enter)<br>You may only enter this stance when you are wielding a melee weapon in one hand and have the other hand empty, perhaps for balance or perhaps for grabbing things coming your way. While in the en-garde stance, you can take no penalties on your accuracy rolls with melee attacks, and you gain a +4 on all accuracy rolls for reflexive attacks. If you switch weapons or are disarmed, you exit this stance. | [STANCE] [COND] reflex Acc +4 |
| **Find the Gap** | En-Garde | Acc +1, Stk +2, HP +8 | Passive | En-Garde; 8 Swashbuckling | reQuires: En-Garde specialty & 8 skill points in Swashbuckling Armor? Pah! That stuff stands no chance against your fine blade. While in your En-Garde stance, any time you hit an opponent, their soak class is lowered by 1 point for every 8 skill points you have in Swashbuckling for the purposes of the attack. | [COND] [REQ] [SCALE:Swashbuckling] |
| **Lightning Slash** | En-Garde | Acc +2, Pri +2, HP +8 | 1 AP | En-Garde; 16 Swashbuckling | reQuires: En-Garde specialty & 16 skill points in Swashbuckling Cost: 1 AP<br>While in your en-garde stance, you can make lightning slashes for 1 action point apiece. A lightning slash is similar to a normal melee attack, except that it costs 1 action point and you add your skill in swashbuckling in place of your strike in order to determine your damage. A lightning slash must be using a one-handed melee weapon and does not count as an attack. A lightning slash cannot be used in conjunction with any other modifying specialty that allows for “attack +1 AP,” as you are no longer making an attack but a lightning slash. | [ACTION] [REQ] [SCALE:Swashbuckling] |
| **Flickering** | Flickering | Acc +1, Eva +1, HP +7 | One-handed melee attack +1 AP |  | Cost: One-Handed Melee Attack +1 AP<br>Sometimes the last thing the opponent ever sees is your hand going for your weapon. Your attacks are like a flicker, getting in multiple strikes all at once. Make your normal accuracy roll. If you hit, instead of doing damage with your strike, you act as if you hit them multiple times with tier 1 damage. Unfortunately, each “attack” may be soaked by the opponent’s defense.<br>2 attacks that deal tier 1 damage<br>3 attacks that deal tier 1 damage<br>5 attacks that deal tier 1 damage<br>7 attacks that deal tier 1 damage<br>Note: A flickering attack acts as multiple attacks for the purposes of determining damage, but other abilities (such as other attackmodifying specialties or weapon augments) only affect the target once if they’re applied to the flickering attack. | [ATTACK+1] |
| **Torrent of Steel** | Flickering | Acc +1, Pri +2, HP +7 | Flickering +2 AP | Flickering; 25 Swashbuckling | reQuires: Flickering specialty & 25 skill points in Swashbuckling Cost: Flickering +2 AP<br>Small scrapes and scratches? No longer: your flickering attacks blend the opponent into bloodied pieces. Your flickering attacks each deal tier 2 damage. | [ATTACK+2] [REQ] |
| **Footwork Training** | Footwork | Pri +3, Spd +5, HP +8 | Passive |  | At the end of any turn during which you move, you receive a bonus to your accuracy and evade. Roll your swashbuckling at the end of any turn in which you move, and you gain a bonus to your accuracy and evade until the end of your next turn (when your action points refresh).<br>+1<br>+2<br>+3<br>+4 | [COND] |
| **Fancy Footwork** | Footwork | Eva +1, Spd +5, HP +9 | Passive | Footwork Training | reQuires: Footwork Training specialty<br>You are no longer a trainee: your footwork is that of a master. From now on, when determing your footwork training bonus, use the fancy footwork chart.<br>+3<br>+4<br>+5<br>+6 | [COND] [REQ] |
| **Parry** | Parry & Riposte | Acc +1, Stk +2, HP +9 | 1 AP reflexive |  | Cost: 1 AP reflexively<br>When you are hit in melee with an attack that deals tier 1 damage, you have the option of parrying as a reflex. Roll accuracy and add your skill in swashbuckling, and, if you score higher than the accuracy roll that hit you, you negate the blow. | [REFLEX] [SCALE:Swashbuckling] |
| **Beat Parry** | Parry & Riposte | Acc +1, Stk +3, HP +9 | Parry +1 AP; resist Dex (negates) | Parry | reQuires: Parry specialty<br>resist: Dexterity (negates)<br>Cost: Parry +1 AP<br>When you parry, you smash the opponent’s weapon so hard they have a difficult time keeping grasp of it. When you do a beat parry, your parry also acts like a called shot to the hand primarily holding the weapon attacking you. | [REFLEX] [REQ] |
| **Distance Parry** | Parry & Riposte | Acc +1, Spd +5, HP +8 | 1 AP reflexive | Parry | reQuires: Parry specialty<br>Cost: 1 AP reflexively<br>You don’t parry with your blade. Oh no, you parry by simply not being in the place they’re attacking. You can parry by moving. It works exactly as a parry, except that you may also immediately move.<br>Because you’re moving, you cannot distance parry and then riposte. | [REFLEX] [REQ] |
| **Experienced Parries** | Parry & Riposte | Acc +1, Stk +3, HP +8 | 1 AP per damage tier | Parry; 9 Swashbuckling | reQuires: Parry specialty & 9 skill points in Swashbuckling Cost: 1 (or more) AP<br>You’re no longer restricted to parrying the tier 1 attacks - you can push off the best of blows. You can attempt to parry any attack, but you must spend 1 action point per tier of the attack’s damage. (Thus, if an attack is dealing tier 3 damage, you’ll need to use 3 action points in order to attempt the parry.) | [REFLEX] [REQ] |
| **Riposte** | Parry & Riposte | Acc +1, Stk +2, HP +8 | Free after parry | Parry | reQuires: Parry specialty<br>When you successfully parry an attack, you can then immediately make a reflexive attack against the person you parried for no additional action points cost. You may upgrade the riposte as per a normal attack, but the upgrades cost action points as per normal. | [REFLEX] [REQ] |

### 6.6 Spirit specialties

**What anyone can do with Spirit (attribute uses):** Concentration (Spirit tier: T1 lose track … T4 total focus; narrator sets distraction modifiers) · **Heroics** (any resist or critical attribute roll +1 AP reflexive: roll Spirit first → modifier on the other roll T1 −4 / T2 +2 / T3 +6 / T4 +12)

#### Faith

| Specialty | Group | Bonuses | Cost / type | Requires | Effect | Tags |
|---|---|---|---|---|---|---|
| **Blind Faith** |  | Eva +1, Pri +2, HP +8 | As an attack | 6 Faith | reQuires: 6 skill points in Faith<br>Cost: same as an Attack<br>You lash out without hesitation, believing that your next attack is going to land true. When making an unaltered attack (as in, no other specialties are applied to it, including those that do not use action points, such as Critical Hits in Espionage), you may use your skill in Faith in place of your accuracy bonus for the accuracy roll. | [ATTACK+0] [REQ] [SCALE:Faith] |
| **Conviction** |  | Acc +1, Stk +3, HP +8 | Attack +1 AP; resist Spirit (negates) |  | resist: Spirit (negates)<br>Cost: Attack +1 AP<br>Any time you are attacking a corrupted creatures, such as those who have risen from the dead, automatons, or horrible abominations, you can attack with conviction. If the target fails to resist, all of their damage soak is negated. | [ATTACK+1] [COND] |
| **Divine Guidance** |  | Stk +2, Def +2, HP +9 | 2 AP reflexive |  | Cost: 2 AP reflexively<br>You close your eyes and guide your injured ally through faith alone. You can eliminate all status penalties on a person for one turn by giving them divine guidance at the beginning of their turn. Divine guidance negates penalties from wounds, status effects, stuns, et cetera. (It does not negate fatal effects.) Any penalties incurred during their turn begin when their action points refresh, and all of their normal penalties return to them. | [REFLEX] |
| **Flowing Vigor** |  | Eva +1, Def +2, HP +9 | 2 AP to begin, 1 AP to channel |  | Cost: 2 AP to begin and 1 AP to channel<br>You channel life back into an ally within 25 feet, replenishing their hit points. When you begin Flowing Vigor, you spend 2 action points and roll on the tier chart. Thereafter, you may heal that amount of hit points again for only 1 action point. You may continue the channel through your turn and into consecutive turns, but if you take any action other than channeling and moving, Flowing Vigor is broken and must be begun anew.<br>2 hit points<br>4 hit points<br>6 hit points<br>8 hit points | [ACTION] |
| **Grief & Hope** |  | Eva +1, Pri +2, HP +8 | 3 AP (allies may sacrifice 1 AP) |  | Cost: 3 AP (1 AP sacrifices)<br>The healing power of grief and hope can be an awesome sight to behold. You can channel that energy to reinvigorate ailing allies. For three action points, you can call upon your allies within 25 feet to give you their grief and hope in order to save another. When you do this, you can roll your faith to heal 3 hit points per tier you reach. The target of the healing can be any ally within 25 feet. Restores 3 hit points<br>Restores 6 hit points<br>Restores 9 hit points<br>Restores 12 hit points<br>For each action point an ally gives you, the amount of hit points the target heals increases by 2 per tier. Thus, if two people sacrifice an action point each for your channeled healing, the target will heal 7 hit points per tier your faith roll receives. Each ally may only sacrifice 1 action point for any given usage of Grief & Hope. | [ACTION] |
| **Healing Halo** |  | Eva +1, Def +2, HP +10 | Stance |  | stanCe (costs 1 AP to enter)<br>Everyone around you draws upon your divine energies. At the end of every turn that you are in your healing halo stance, you and your living allies within 25 feet regain a small amount of hit points. You and your allies gain 1 hit point, plus 1 for every 5 skill points you have in faith, at the end of every turn that you spent in healing halo (when your action points refresh). | [STANCE] [SCALE:Faith] |
| **Infallible Faith** |  | Eva +1, Def +2, HP +8 | 1 AP reflexive (allies may sacrifice 1 AP) |  | Cost: 1 AP reflexively (1 AP sacrifices)<br>Your allies’ belief in you is infalliable, their faith ensuring that you never fail. You may use infallible faith whenever you must roll a resist. You immediately gain a +2 bonus on the resist. Every ally within 25 feet may also sacrifice a single action point to you, increasing the bonus by another +3 per sacrificing ally. | [REFLEX] |
| **Moral Support** |  | Acc +1, Eva +1, HP +7 | 2 AP reflexive | Spirit attribute 8 | reQuires: a Spirit of 8<br>Cost: 2 AP reflexively<br>When a friend is in need, you can push them forward to greater feats of heroism. Any time you know of an ally within 25 feet being forced to use an attribute as a resist or in some momentary peril (such as having to jump a chasm or wrestle free a powerful device from a crazed maniac), you may roll your heroics (found under the Spirit attribute) and give them the bonus. If you roll poorly and receive a penalty as per your heroics result, that penalty is applied on your ally’s attribute roll, regardless of whether they want it there or not. | [REFLEX] [REQ:Spirit≥8] |
| **Prayer** |  | Acc +1, Def +2, HP +9 | 1 AP (allies may sacrifice 1 AP) |  | Cost: 1 AP (1 AP sacrifices)<br>With your allies on each side of you, you know you’re able to push onward with only their prayers. When you begin the prayer, you roll on the chart, granting yourself temporary hit points. For each action point an ally gives you, roll again on the chart. Each ally may only sacrifice 1 action point for your prayer and must be within 25 feet to do so. Prayer may not be used again until these temporary hit points are gone. If you were damaged at the time the prayer begin, these hit points instead act as healing. Gain 2 temporary hit point<br>Gain 3 temporary hit points<br>Gain 4 temporary hit points<br>Gain 5 temporary hit points<br>Eva HP +1 +8 | [ACTION] |
| **Purify** |  | Eva +1, Pri +2, HP +8 | 2 AP |  | Cost: 2 AP<br>By laying your hands on yourself or an ally, your devotion allows your target to ignore the penalties from an ongoing poison, disease, parasite, called shot, wound, or other effect for a number of turns equal to your skill in faith. The target can not be purified again until the effects of the first purification wear off. If the effect of the penalty would have naturally worn off during the time the purification was occuring, it does not resume once the purification ends.<br>Ignore 1 effect<br>Ignore up to 2 effects<br>Ignore up to 3 effects<br>Ignore all effects | [ACTION] [SCALE:Faith] |
| **Shock of Life** |  | Eva +1, Def +3, HP +11 | 2 AP | 10 Faith | reQuires: 10 skill points in Faith<br>Cost: 2 AP<br>When times seem dire, you know how to shock somebody back into existence. You instantly heal, through touch, a number of hit points equal to twice your skill in faith. This burst of energy, however, has some negative effects on the target. You roll your faith to determine how minor the negative effects are. A target may, at their discretion, ignore the Shock of Life altogether, though this must be decided prior to the faith roll.<br>Target is stunned for 3 AP<br>Target is stunned for 2 AP<br>Target is stunned for 1 AP<br>Target suffers no ill effect | [ACTION] [REQ] [SCALE:Faith] |
| **Devoted Peers** | Ap Sacrifice Upgrade | Eva +1, Def +2, HP +10 | Passive | any AP-sacrifice specialty | reQuires: any specialty that calls upon sacrificial action points Your friends are loyal and devoted like few others. When you call upon them to sacrifice their action points for your specialties, they may sacrifice up to two action points each. | [PASSIVE] [REQ] |
| **Self-Sacrifice** | Ap Sacrifice Upgrade | Eva +1, Stk +2, HP +8 | Passive | 4 AP per turn; any AP-sacrifice specialty | reQuires: 4 action points per turn & any specialty that calls upon sacrificial action points Your faith is so strong that it alone can guide your attacks. When you call upon others to sacrifice action points to your specialties, you may sacrifice your own action points as well. You, however, are not limited, and may sacrifice as many action points as you have available to you. | [PASSIVE] [REQ] |
| **Silent Devotion** | Ap Sacrifice Upgrade | Eva +2, Pri +1, HP +7 | Passive | any AP-sacrifice specialty | reQuires: any specialty that calls upon sacrificial action points Your beliefs do not need to be yelled, exclaimed, or shouted. When you call upon others to sacrifice action points to you, you do so by your willpower alone. You may now ask for your allies’ sacrifices with complete silence and no outward visual or audible cues to your foes. | [PASSIVE] [REQ] |
| **Appointed Champion** | Champion | Eva +1, Def +2, HP +9 | Stance |  | stanCe (costs 1 AP to enter)<br>You mark a nearby ally as your champion and channel your faith into him. While in this stance, any time said champion would need to make a spirit roll, he may choose to let you roll for him and apply your spirit attribute’s bonus. | [STANCE] |
| **Conduit of Faith** | Champion | Acc +1, Eva +1, HP +8 | Passive | Appointed Champion | reQuires: Appointed Champion specialty<br>You draw the breath from nearby allies and empower your champion. Anyone within 25 feet may sacrifice their last action point they have for the turn (at the end of their turn, when their action points refresh) to your appointed champion. It must be their last action point, and the action point is immediately added to the appointed champion’s pool of action points. | [COND] [REQ] |
| **Proclaim the Heretic** | Inquisition | Eva +1, Stk +2, HP +8 | Stance; 1 AP reflexive |  | stanCe (costs 1 AP to enter)<br>Cost: 1 AP reflexively<br>You proclaim an enemy to be a heretic, an unfaithless vagabond, and now no one will lose their courage against him. Choose a single opponent when you enter this stance. When that heretic attacks you or one of your allies, you or the ally can spend 1 action point in order to roll the spirit attribute instead of defense in order to determine damage soaked.<br>To proclaim a different heretic, you will need to change stance (costing 1 action point). | [STANCE] |
| **Light in the Dark** | Inquisition | Acc +1, Eva +1, HP +8 | Passive | Proclaim the Heretic | reQuires: Proclaim the Heretic specialty<br>Your allies are protected by your faith when confronting the heretic. You and all of your allies may choose to use your spirit in place of their defense bonus when soaking damage dealt by the proclaimed heretic. Making this choice does not cost anybody any action points. | [COND] [REQ] |
| **Smite** | Smiting | Acc +1, Stk +1, HP +8 | Melee attack +1 AP (allies within 25 ft sacrifice 1 AP) |  | Cost: Melee Attack +1 AP (1 AP sacrifices)<br>Your allies’ belief in your attack guides your hand against the unfaithful. You call for your allies’ faith, and their prayers give your attack strength. When you begin to make a smite, you call for your allies within 25 feet to sacrifice 1 action point in order to empower your attack. Any ally who can hear you (or knows that you called for their belief) and is within range can, reflexively, sacrifice the action point. If your attack lands, your attack deals damage as if it were one damage class higher for every action point an ally sacrificed to you. If nobody sacrificed an action point for the smite, it is treated like a normal attack.<br>An ally can only sacrifice one action point per smite, and if the smite misses, the sacrificed action points are simply lost. | [ATTACK+1] |
| **Assured Success** | Smiting | Acc +2, Pri +1, HP +6 | Passive | Smite | reQuires: Smite specialty<br>When you smite your foes, your blade is guided by faith into the enemy. For every action point sacrificed for your smite, the attack gains a +1 on the accuracy roll. | [COND] [REQ] |
| **Impassioned Victory** | Smiting | Acc +1, Stk +3, HP +7 | Passive | 17 Faith; Smite | reQuires: 17 skill points in Faith & Smite specialty When your smite fells an evil foe, the attack is inspiring and leads your allies on to greater deeds. When your smite kills or incapacitates the person being attacked, all of those who sacrificed action points to empower your smite instantly regain those sacrificed action points. | [COND] [REQ] |
| **Smiting Shot** | Smiting | Acc +1, Pri +2, HP +8 | Passive | Smite | reQuires: Smite specialty<br>Your allies’ faith steadies your shot and flies with the bullet. You may now make ranged smites, be it with a bow, firearm, or other ranged weapon. | [PASSIVE] [REQ] |
| **Zealous Smite** | Smiting | Acc +1, Stk +2, HP +7 | Passive | Smite; 7 Faith | reQuires: Smite specialty & 7 skill points in Faith Your smite does not merely deal great destruction but is also a weapon of finesse and a tool of your faith. Any action point sacrificed to your smite can, instead of increasing your attack’s damage class, be used like a normal action point for modifying the attack with another specialty that you know. For example, if you have the Conviction specialty (normally made as an attack +1 AP) and you make a Smite, you can convert one of the action points sacrificed to you in order to make your Smite into a Smite with Conviction. | [COND] [REQ] |

#### Grace

| Specialty | Group | Bonuses | Cost / type | Requires | Effect | Tags |
|---|---|---|---|---|---|---|
| **Bloodsoak** |  | Eva +1, Def +2, HP +9 | Passive | 4 Grace | reQuires: 4 skill points in Grace<br>Your blood does not flow freely at another person’s convenience. Through unearthly bodily training, you can keep yourself from bleeding from deep gashes. When you would suffer bleeding damage, you may ignore 1 point per 4 skill points you have in Grace. | [PASSIVE] [REQ] [SCALE:Grace] |
| **Connection** |  | Acc +2, Pri +1, HP +7 | Stance; resist Spirit (negates) |  | stanCe (costs 1 AP to enter)<br>resist: Spirit (negates)<br>When you lock eyes with an opponent, they cannot easily break the gaze. To make this connection, an opponent within 100 feet makes a spirit roll opposed by your grace. If you succeed, their gaze is locked with yours. They cannot move behind any cover that would break the gaze or attack anybody else. If somebody or something walks between the two of you, that will give the opponent an automatic and free resist to break the gaze. The opponent can back away (moving with a -10 feet move penalty), and the connection is automatically broken at 100 feet. If the opponent is actively avoiding your gaze (potentially because they know you have this ability), you might need to be creative in order to force them to look toward you. If a connection is made through a mirror, the connected people must stay at that angle or the connection is lost. | [STANCE] |
| **Danger Sense** |  | Eva +1, Pri +5, HP +9 | Passive; 1 AP reflexive to warn; resist Cunning (negates) | 5 Grace | reQuires: 5 skill points in Grace<br>resist: Cunning (negates)<br>Cost: 1 AP reflexively (to warn others)<br>When a sniper locks onto you from a thousand feet away, you can feel it in your bones and through the chill on your neck. When you or an adjacent ally are about to be attacked, roll your grace against the first attacker’s cunning. If your grace meets or exceeds their cunning, you may have your hit points up and make a full evade roll against the attack.<br>If you spend 1 action point reflexively, you may warn others in your vicinity so that they have the same bonus. This warning is done as the attack is launched, so an opponent cannot stop his first attack from going off after the warning is given. | [COND] [REQ] |
| **Destabilize** |  | Acc +1, Stk +2, HP +8 | Attack +1 AP; resist Dex or Spirit (tiers down) |  | resist: Dexterity or Spirit (target’s discretion, tiers down) Cost: Attack +1 AP<br>Your attack disrupts their center of gravity, ensuring that they won’t be able to enter a stance for several moments. If the opponent is in a stance, they are knocked out of it unless they can resist against your skill in grace.<br>If the target is not in a stance, however, the target cannot enter a stance until they spend some action points to stabilize again.<br>Destabilized until 1 action point is spent to stabilize Destabilized until 2 action points are spent to stabilize Destabilized until 3 action points are spent to stabilize Destabilized until 4 action points are spent to stabilize | [ATTACK+1] |
| **Dispel Pain** |  | Eva +1, Def +3, HP +9 | 1 AP reflexive |  | Cost: 1 AP reflexively<br>When an opponent successful lands a called shot on you, you can dispel the pain. Doing so allows you to re-roll the resist, and you add your grace to the roll. | [REFLEX] [SCALE:Grace] |
| **Force of Self** |  | Acc +1, Eva +1, HP +7 | Stance; resist Spirit (negates) |  | stanCe (costs 1 AP to enter)<br>resist: Spirit (negates)<br>Your aura is so powerful that nobody can even come close to you. When you enter this stance, anybody attempting to step into an adjacent space to you must make a successful resist. If they cannot make the resist, they can spend another action point in order to try again. If somebody is already standing next to you, they are unaffected. However, if you and anybody adjacent to you is separated, and they try to move next to you again, they must again succeed in rolling the resist. You can allow allies to stand next to you. | [STANCE] |
| **Inner Calm** |  | Eva +1, Pri +2, HP +10 | Stance |  | stanCe (costs 1 AP to enter)<br>You center yourself, calming your emotions and focusing your mind. While you are in your inner calm stance, you cannot be disoriented. If you become disoriented while outside of this stance, you may enter this stance to end the disorientation. | [STANCE] |
| **Iron Palm** |  | Acc +1, Stk +2, HP +10 | Unarmed called shot +1 AP |  | Cost: Unarmed Called Shot +1 AP<br>When you hit the opponent, your attack sends ripples through their body, activating multiple called shot effects as if you had hit each one separately. When you make a called shot with your iron palm, your called shot affects multiple locations. Affects called shot and an adjacent location of your choice Affects called shot and two adjacent locations<br>Affects called shot and any two called shot locations Affects called shot and any three called shot locations | [ATTACK+1] |
| **Master of Forms** |  | Acc +1, Eva +1, HP +8 | Passive | 6 Grace; 2 stances known | reQuires: 6 skill points in Grace & 2 stances known You can enter multiple stances, gaining all of their effects. You can have one stance active per 3 skill points you have in grace. You must enter each one separately (spending 1 action point for each stance). Of course, you cannot enter two mutually-exclusive stances. For instance, if a stance says that you cannot move while in that stance, you cannot be in another stance that requires you to move every turn. | [STANCE] [REQ] [SCALE:Grace] |
| **Parting Waves** |  | Eva +1, Pri +2, HP +8 | 1 AP reflexive; resist Dex (negates) |  | resist: Dexterity (negates)<br>Cost: 1 AP reflexively<br>Any time you successfully evade an attack from a melee weapon, you can reflexively spend 1 action points in order to disarm the opponent of the weapon they attacked you with. They must make a dexterity resist against your skill in grace in order to keep their weapon. If they fail, the weapon clatters to their feet. | [REFLEX] |
| **Shocking Soul** |  | Acc +1, Stk +2, HP +8 | 2 AP reflexive | 9 Grace | reQuires: 9 skill points in Grace<br>Cost: 2 AP reflexively<br>If you are successfully struck by a melee attack, you can immediately channel the power of your soul through their weapon and into your assailant. The enemy takes 1 unsoakable damage per point you have in grace. | [REFLEX] [REQ] [SCALE:Grace] |
| **Spirit Break** |  | Acc +1, Eva +1, HP +8 | 1 AP reflexive |  | Cost: 1 AP reflexively<br>You focus your mind and your thoughts, reaching out to the people around you. Every time someone rolls their Spirit attribute within 25 feet of you, you may lower the result of the roll by your grace. | [REFLEX] [SCALE:Grace] |
| **Spiritual Seal** |  | Acc +1, Eva +1, HP +9 | Attack +1 AP |  | Cost: Attack +1 AP<br>Your attack can seal the spirit on another person, causing them to be unable to tap into their strength of will. The target of your attack takes a penalty on all of their spirit skills (faith, grace, luck, and shamanism) and the spirit attribute until the end of your next turn.<br>-3<br>-6<br>-9<br>-12 | [ATTACK+1] |
| **Void Strike** |  | Acc +1, Stk +2, HP +10 | Melee attack +1 AP; target may use Spirit as evade |  | resist: Spirit (as evade; see below)<br>Cost: Melee Attack +1 AP<br>You can guide your ki along the path of your strike, creating a sharp wave that rends through the target. Your melee attack can target those an additional 5 feet away from you per point you have in Grace. Because of the nature of this attack, the target may choose to use his Spirit in place of his evade in order to avoid the attack. If they have a poor spirit, they may use their evade as per normal. | [ATTACK+1] [GEAR] [SCALE:Grace] reach += 5×Grace |
| **Ki Flow** | Ki-Unleashing | Eva +1, Stk +1, HP +10 | 2 AP; resist Brute or Spirit (negates) |  | resist: Brute or Spirit (negates, target’s discretion) Cost: 2 AP<br>Through meditation and will, you have refined the control of your internal energy. Your spirit strains against your flesh, manifesting itself in moments of duress. Enemy’s near you are pushed away from you when you manifest your ki flow.<br>Enemies within 5 feet of you must resist being pushed away 5 feet.<br>Enemies within 10 feet of you must resist being pushed away 5 feet.<br>Enemies within 15 feet of you must make resist being pushed away 5 feet.<br>Enemies within 20 feet of you must resist being pushed away 5 feet. | [ACTION] |
| **Ki Rage** | Ki-Unleashing | Eva +1, Stk +2, HP +8 | Ki Flow +1 AP (3 AP total) | Ki Flow | reQuires: Ki Flow specialty<br>Cost: Ki Flow +1 AP (3 AP total)<br>The ki pressure that surrounds you has taken on a life of its own. When you release your ki flow on the battlefield, it damages all enemies that are affected by it. In addition to being pushed back, they also take a few points of unsoakable damage.<br>3 damage<br>6 damage<br>9 damage<br>12 damage | [ACTION] [REQ] |
| **Feather in the Wind** | Light-As-Air | Eva +1, Spd +5, HP +6 | 1 AP (as a move) |  | Cost: 1 AP (as a normal move)<br>You may move across the air, over water, and skip across lava as though you were completely weightless. When you move like this, you can only move your normal speed weightlessly, and it must be a horizontal direction (you cannot move upwards). You may spend your next action point to continue moving weightlessly, but during that brief second between moving weightlessly, your weight returns. If you are falling when you activate weightlessness, you remain falling, but can move your speed horizontally. Any penalties you have to speed (such as from armor or crippling attacks) affect your weightless speed. | [ACTION] |
| **Weightless** | Light-As-Air | Acc +1, Eva +1, HP +8 | Stance (2 AP reflexive under duress) | Feather in the Wind | stanCe (costs 1 AP to enter)<br>reQuires: Feather in the Wind specialty<br>When you are standing in a single spot, you can control your body’s weight so that it is at equilibrium with its surroundings. If you are on water in your weightless stance, you will not sink. If you are in the air, in your weightless stance, you will not fall. If you stop moving weightlessly while in this stance (with your Feather in the Wind specialty), your weight does not return. If you are trying to enter this stance under duressed conditions (such as while falling), you may do so for 2 action points, and may do so reflexively.<br>You cannot jump from a point that would not normally support your weight, such as from the surface of a pond or on the edge of a palm leaf. | [STANCE] [REQ] |
| **Touch of Paralysis** | Paralyzing | Acc +1, Stk +2, HP +7 | Unarmed attack +2 AP; resist Brute (negates) |  | resist: Brute (negates)<br>Cost: Unarmed Attack +2 AP<br>You strike out at major nerve clusters and pressure points, twisting the target into a statue of agony. When you hit the target with touch of paralysis, you also roll to determine the tier. The target is allowed to resist against a roll of your grace every time they would take damage from the paralysis, and, once successfully resisted, the effect ends. A person can be effected by only one touch of paralysis at any given time, with the greater result overtaking the previous.<br>The target takes 1 point of damage every time they try to move.<br>The target takes 3 points of damage every time they try to move.<br>The target takes 5 points of damage every time they try to move.<br>The target takes 7 points of damage every time they try to move. | [ATTACK+2] |
| **Blocked Ki** | Paralyzing | Acc +1, Stk +2, HP +8 | Unarmed attack +1 AP; resist Brute or Spirit (tiers down) | Touch of Paralysis | reQuires: Touch of Paralysis specialty<br>resist: Brute or Spirit (target’s discretion, tiers down) Cost: Unarmed Attack +1 AP<br>You strike one of your opponent’s chakra points, disrupting their natural energy flow. This causes a massive blockage that explodes in pain when the opponent makes even the slightest of movements. The opponent receives 1 point of unsoakable damage with each action point they spend. The opponent may spend the indicated amount of action point meditating, trying to unblock their blocked ki.<br>1 AP to unblock the ki channel<br>2 AP to unblock the ki channel<br>3 AP to unblock the ki channel<br>4 AP to unblock the ki channel | [ATTACK+1] [REQ] |

#### Luck

| Specialty | Group | Bonuses | Cost / type | Requires | Effect | Tags |
|---|---|---|---|---|---|---|
| **Confident in your Luck** |  | Acc +1, Eva +1, HP +7 | 1 AP reflexive |  | Cost: 1 AP reflexively<br>You know the odds. You know that you’re oozing out good luck. When you so choose, you may use your skill in luck in place of any other resist. Is somebody trying to push you around and you need a Brute resist to get out of it? Just spend 1 action point to use your skill in luck in place of your Brute attribute. | [REFLEX] [SCALE:Luck] |
| **Don't Tell Me the Odds** |  | Eva +2, Pri +2, HP +6 | 1 AP reflexive |  | Cost: 1 AP reflexively<br>You refuse to accept a bad hand dealt by fate and push on to succeed. You can spend 1 action point reflexively to get a +1 on any roll, but you can only use it if the bonus will raise your roll high enough that it will reach a higher tier result. This bonus increases by +1 for every 10 points you have in luck. | [REFLEX] [SCALE:Luck] 1 + floor(Luck/10) |
| **Cheat Fate** |  | Acc +2, Eva +1, HP +6 | Stance |  | stanCe (costs 1 AP to enter)<br>Using your natural luck, you are able to prevent certain outcomes from being rolled. When you enter this stance, choose a single number from 2 to 11. If anybody near you rolls the number you chose, they must re-roll it. If the same number is rolled on the re-roll, it is kept. | [STANCE] |
| **Equalizing Force** |  | Acc +1, Eva +1, HP +6 | 2 AP reflexive |  | Cost: 2 AP reflexively<br>Luck is the great balancer, bringing good luck to the misfortunate and bad luck to the fortunate. You can use equalizing force whenever you see somebody roll a die. For 2 action points, you change the die rolled to a 6.<br>If the target had rolled a 12, the 12 is now a 6 but they roll again and add the results. If they had rolled a 1, it is now a 6, but they can’t add any of their bonuses to the 6. Now, a 6 is a 6 is a 6. This specialty cannot be used to alter wound effect or fatal effect rolls or any roll that requires a random die roll. | [REFLEX] |
| **Hex** |  | Eva +1, Pri +3, HP +7 | 2 AP reflexive; resist Dex or Spirit (negates) |  | resist: Dexterity or Spirit (target’s discretion, negates) Cost: 2 AP reflexively<br>When your enemies are moving toward you, there’s always some loose piece of rubble or a stray twig that trips them up. For 2 action points, when anybody is moving directly toward you and is within 25 feet, you can cause them to trip. They make an opposed resist against your luck roll. If you meet or exceed their resist, they fall to the ground and are prone (normally costing an action point to stand up). | [REFLEX] |
| **Jackpot** |  | Acc +1, Stk +3, HP +8 | Passive | 4 Luck | reQuires: 4 skill points in Luck<br>Lucky hits are rare to find, so you squeeze them for all their worth. When rolling strike or accuracy to determine damage, increase your damage class by 2 every time you roll a pure 12. This damage class increase only affects the one attack. | [COND] [REQ] |
| **Jinx** |  | Acc +1, Stk +2, HP +9 | Passive (when attacked) |  | Any time you are attacked, you can jinx that opponent. To do so, you willingly take a 1 on the evade and defense rolls of the incoming attack, letting them land a full blow against you. You can only choose to do this if you would have gained the full bonuses to your evade and defense in the first place. Your attacker is now jinxed. The next time they are attacked (be it from you or an ally), you may add your skill in luck to either the accuracy or strike roll. | [REFLEX] [SCALE:Luck] |
| **Roll of the Dice** |  | Acc +1, Eva +2, HP +8 | Free each turn start | any other Luck specialty | reQuires: Any 1 other specialty from the Luck skill The fates of fortune seem drawn to you, giving you every opportunity to take a gamble. At the begining of your turn you can make one free roll for the sole purpose of activating one of your other luck specialties. Dice rolled this way can be stored without spending action points. | [PASSIVE] [REQ] |
| **Roulette** |  | Acc +2, Pri +1, HP +6 | Attack +1 AP |  | Cost: Attack +1 AP<br>The more you’re willing to risk, the greater the rewards. When you announce your attack choose a number ranging from 1 through<br>12. Now roll your die without adding anything to it. If you get that number or higher, you get the number you chose as a bonus on your accuracy roll. If you get under that number, you resolve the attack as per normal. | [ATTACK+1] |
| **Spot of Misfortune** |  | Acc +1, Eva +1, HP +7 | 2 AP to create, 1 AP reflexive to enact; resist Spirit (negates) | 3 Luck | reQuires: 3 skill points in Luck<br>resist: Spirit (negates)<br>Cost: 2 AP to create, 1 AP reflexively to enact<br>You know when an area is filled with bad luck. Choose a 5 foot spot within 25 feet of you. Any time somebody makes a combat roll (accuracy, evade, strike, or defense) while in that spot, you may spend 1 action point to cause them to take a 1 on that roll. They can resist with their spirit opposed by your skill in luck. When you use spot of misfortune on an opponent, they get a feeling that they’re standing in an unlucky location. You can make one such location for every 3 points you have in luck. You can create a spot of misfortune inside a vehicle only if the vehicle has a cockpit larger than 10 feet by 10 feet. Otherwise, the vehicle is simply inside the spot of misfortune and can move out of it. | [ACTION] [REQ] [SCALE:Luck] |
| **Free from Failure** | Failure Avoidance | Eva +1, Pri +2, HP +7 | Stance | 6 Luck | stanCe (costs 1 AP to enter)<br>reQuires: 6 skill points in Luck<br>While you might still do poorly, you have confidence that you’ll never fail completely. While in this stance, your natural 1s are not<br>1s. You may still add appropriate bonuses to rolls of 1. You may only do this if you rolled the 1 - having a specialty or effect that causes you to take an effective 1 can’t be affected by Free from Failure. | [STANCE] [REQ] |
| **Steady Friends** | Failure Avoidance | Acc +1, Eva +1, HP +8 | 1 AP reflexive | 10 Luck; Free from Failure | reQuires: 10 skill points in Luck & Free from Failure specialty Cost: 1 AP reflexively<br>Your confidence extends to your friends and allies. When an ally within 25 feet rolls a natural 1 and you are in your Free from Failure stance, you may allow your ally to add their normal bonuses to the natural 1. | [REFLEX] [REQ] |
| **Curse** | Foul Luck | Eva +1, Def +2, HP +9 | 1 AP to store, 1 AP reflexive to use; resist Spirit (negates) |  | resist: Spirit (negates)<br>Cost: 1 AP to store, 1 AP reflexively to use<br>Your streaks of bad luck cause people to avoid you for fear of your bad vibes rubbing off on to them. When you roll a 1 in combat, you may spend 1 action point to save that roll. Your roll remains a natural 1.<br>You may spend one action point to give another person within 50 feet the same result. They roll their spirit against your skill in luck to resist this effect. You may store a number of 1s equal to 1 plus 1 per 3 skill points you have in luck. These 1s are stored until your next breather and may only be used on any dice rolled during combat. | [REFLEX] [SCALE:Luck] |
| **Fumble** | Foul Luck | Acc +1, Eva +1, HP +8 | 1 AP + one stored 1; resist Spirit (negates) | Curse | reQuires: Curse specialty<br>resist: Spirit (negates)<br>Cost: 1 AP<br>Your foe gets overly excited and drops their weapon before they’re even able to deliver an attack. When you’ve stored natural 1s with curse, you can spend an action point and one of your stored natural 1s to roll your luck against a target within 25 feet. If they fail to resist, they drop their weapon as if they had been disarmed. | [ACTION] [REQ] |
| **Ace Up My Sleeve** | Luck Holder | Eva +1, Pri +2, HP +6 | 1 AP reflexive to store, 1 AP to use |  | Cost: 1 AP reflexively to grab the die, 1 AP to use You’ve become strategic in your use of luck. You’re able to store your successes and use them at more opportune times. Any time you roll a pure 12 on a combat roll, you can store it. To do this you must leave the die where it landed with the 12 showing and announce to the table that you are storing that pure 12. You then re-roll for the roll that you saved the die on.<br>You can use a saved pure 12 on any combat roll.<br>You must use the saved pure 12 before your next breather. You can save one pure 12, plus an additional pure 12 per 4 skill points you have in luck. | [REFLEX] [SCALE:Luck] |
| **Leading the Lucky Life** | Luck Holder | Acc +1, Eva +1, HP +9 | 1 AP | Ace Up My Sleeve | reQuires: Ace Up My Sleeve specialty<br>Cost: 1 AP<br>You cash in on your saved fortune for a rush of revitalizing energy. When using Ace Up My Sleeve to store pure 12s, you can instead use 1 action point to remove one of your saved 12s and roll your luck to restore your hit points.<br>You restore 7 hit points<br>You restore 14 hit points<br>You restore 21 hit points<br>You restore 28 hit points | [ACTION] [REQ] |
| **Second Chance** | Luck Holder | Eva +1, Wnd +1, HP +10 | 1 AP reflexive + stored 12; resist Spirit (negates) | Ace Up My Sleeve | reQuires: Ace Up My Sleeve specialty<br>resist: Spirit (negates)<br>Cost: 1 AP reflexively<br>When things look their darkest you always seem to luck out of the deadly blows. When hit by an attack which would normally give you a fatal effect and you’ve stored a pure 12 with Ace Up My Sleeve, you can spend 1 reflexive action point and a stored 12 to recieve a wound effect instead of recieving the fatal effect. The attacker may roll a spirit resist to negate this effect. | [REFLEX] [REQ] |
| **Lucky Number 7** | Lucky #7 | Eva +1, Pri +2, HP +6 | Stance |  | stanCe (costs 1 AP to enter)<br>You have a habit of getting twice as many pure rolls as anyone else. Any time your die rolls a 7, it becomes a “pure 7,” and you may roll again and add the results. Fancy that! | [STANCE] |
| **Luckier Number 7** | Lucky #7 | Eva +1, Pri +2, HP +7 | Passive | Lucky Number 7; 16 Luck | reQuires: Lucky Number 7 specialty & 16 skill points in Luck Not only are natural 7s lucky for you, they are overwhelmingly lucky. Now, when you are in your Lucky Number 7 stance and roll a 7, you can pick up the 7 and put it down as a 12. 7s equal 12s. And then you can re-roll them. | [STANCE] [REQ] |
| **Feeling Lucky** | Ranged Evading | Eva +2, Pri +1, HP +6 | 1 AP reflexive; resist Spirit (tiers down) |  | resist: Spirit (tiers down)<br>Cost: 1 AP reflexively<br>Ranged marksmanship and archery weapons have a habit of not working when they’re used to kill you. Hopefully that luck continues. When being fired upon by a ranged weapon, the opponent is allowed to resist. If they fail, roll your tier to determine the ill effect that happens to them.<br>You roll twice on your evade and take the highest result. The weapon fails to fire.<br>The weapon fails to fire and the ammo is destroyed. The weapon must be readied again, if applicable.<br>The weapon backfires, dealing tier 1 damage to the user. | [REFLEX] |
| **Unfriendly Fire** | Ranged Evading | Acc +1, Eva +2, HP +5 | 2 AP reflexive; resist Dex (tiers down) | Feeling Lucky | reQuires: Feeling Lucky specialty<br>resist: Dexterity (negates)<br>Cost: 2 AP reflexively<br>Sometimes your enemies miss you. Sometimes their guns misfire. Sometimes they explode in their hands. And sometimes your enemies accidently shoot each other. This specialty makes the latter happen more often.<br>When you are shot at with a firearm, crossbow, or bow, you can attempt to make the attack unfriendly fire for 2 action points. Choose a target within 10 feet of you. They are the new target of the shot. The original attacker still determines if they hit against the new target’s evade, but you roll your luck in order to determine what tier of damage is done. For every tier that the original attacker rolls their resist above tier 1, they lower the damage by 1 tier. The new target can attempt to soak damage, as per normal. If the attack was special (that is, had specialties modifying it), all of the specialty modifiers are lost and the attack becomes a normal attack. The original attacker keeps the extra action points required to make the attack special. | [REFLEX] [REQ] |
| **Unfriendly Artillery** | Ranged Evading | Acc +1, Eva +1, HP +7 | Passive | Feeling Lucky; Unfriendly Fire | reQuires: Feeling Lucky specialty & Unfriendly Fire specialty When your divert an attack into a new target through sheer luck alone, it has the potential to be very powerful. Your unfriendly fire no longer loses the specialty modifiers from the original attack, and the original attacker does not regain their action points from adding those specialty modifiers. | [COND] [REQ] |

#### Shamanism

| Specialty | Group | Bonuses | Cost / type | Requires | Effect | Tags |
|---|---|---|---|---|---|---|
| **Control Beast** |  | Acc +1, Eva +1, HP +8 | 3 AP |  | Cost: 3 AP<br>You are able to calm an animal and gain its loyalty. You may even be able to redirect its anger.<br>If you attempt to use this ability on an animal under another shaman’s control, the owner and you must make opposed shamanism rolls. If you succeed, you can attempt to control it. If you fail, nothing occurs.<br>The animal becomes cautious, only attacking if forced The animal becomes passive and will not attack<br>The animal becomes passive and willing to help you The animal becomes your ally, and will not attack you. You may direct it to attack another, at your discretion. | [ACTION] |
| **Druidic** |  | Acc +1, Stk +2, HP +8 | Stance |  | stanCe (costs 1 AP to enter)<br>Warped metal feels unnatural in your hand, and you’ve always felt more at home wielding your ancestral, tribal weaponry. When in this stance, wood and organic weapons (not including unarmed attacks) deal 2 damage classes higher. | [STANCE] [GEAR] DC +2 (wood/organic) |
| **Fire Resistance** |  | Eva +1, Def +3, HP +10 | Passive |  | Your natural body heat increases. Your love of the flame has begun to manifest as you become more and more resistant to fire. Any time you take damage from fire or a fire-based attack, you soak a fair deal of the damage.<br>3 damage from heat or fire soaked<br>6 damage from heat or fire soaked<br>9 damage from heat or fire soaked<br>12 damage from heat or fire soaked | [COND] |
| **Geomancer** |  | Acc +1, Eva +1, HP +7 | Passive | Topographer | reQuires: Topographer specialty<br>Choose an extreme terrain: jungle, desert, swamp, tundra, high atmosphere, or the abyss (deep underwater); or an extreme weather condition: raging thunderstorm, hurricane, tornado, blizzard, meteor shower, sand-storm, or heat wave. When fighting in these chosen conditions, you may use your skill in shamanism in place of any tiered skill roll. | [COND] [REQ] |
| **Hardened Trainer** |  | Acc +1, Def +2, HP +10 | Passive |  | Through years of dealing with animals, you are keen at fighting against them. When you are fending off an animal, you gain a bonus to your defense equal to your skill in shamanism. | [COND] [SCALE:Shamanism] |
| **Lion's Roar** |  | Stk +2, Pri +2, HP +9 | 2 AP; resist Spirit (negates) |  | resist: Spirit (negates)<br>Cost: 2 AP<br>You breathe deeply and let out a mighty roar that strikes fear into the heart of all nearby enemies. When making such a warcry, all opponents within 50 feet who can hear you must roll a spirit resist against your Shamanism. If they do not resist, they become frightened, suffering the effects of Tier 2 fear. | [ACTION] |
| **Naturalist** |  | Eva +1, Def +2, HP +9 | Passive | 5 Shamanism | reQuires: 5 skill points in Shamanism<br>Coating yourself in metal makes you uneasy. You gain an additional soak class for every 5 skill points you have in Shamanism while wearing organic or wooden armor. | [COND] [REQ] [STAT:Soak += floor(Sham/5)] |
| **Parasite** |  | Stk +2, Pri +2, HP +7 | 2 AP to begin, 1 AP/turn; resist Brute (tiers down) |  | resist: Brute (tiers down)<br>Cost: 2 AP to begin, 1 AP to continue during subsequent turns By stomping in constant rythm, you draw out nearby insect colonies to assault an opponent within 25 feet. On the turn the swarm attacks, and every turn thereafter, roll on the called shot chart. The victim must roll to resist against your shamanism or suffer the effects of this called shot.<br>Anything that would effect an area disrupts the swarm and it must be reformed (for 2 action points). If at any point you lose the ability to move your legs or are knocked prone, the swarm is disrupted. | [ACTION] |
| **Still as Stone** |  | Acc +1, Eva +1, HP +6 | Stance |  | stanCe (costs 1 AP to enter)<br>Stalking your prey like a crouched cougar, you wait for the exact correct moment to pounce, still as the world around you and blending in as if you were a part of the scene itself. Whether you’re in the quiet meadows and copses of the forest or a backalley in the night, you can blend in with your surroundings perfectly while standing still. When you enter this stance, you gain a bonus equal to your skill in Shamanism to hide when you have cover. | [STANCE] [SCALE:Shamanism] |
| **Tactics of the Wolf** |  | Acc +1, Stk +3, HP +8 | Melee attack, reflexive |  | Cost: Melee Attack reflexively<br>You’ve learned to approach combat like a pack of wolves attacking their prey: all at once. When somebody attacks an adjacent opponent, you can make a reflexive attack against that opponent. If you hit, you gain a bonus on your strike.<br>You gain +3 on the strike roll<br>You gain +6 on the strike roll<br>You gain +9 on the strike roll<br>You gain +12 on the strike roll | [REFLEX] |
| **Topographer** |  | Eva +1, Pri +2, HP +7 | Passive |  | Be it huricane, heatwave, blizzard, or sleet, you are able to function in all weather conditions without penalty. In addition, you take no penalties for moving through rough or unsafe terrain. | [PASSIVE] |
| **Avian Wrath** | Bird Calling | Acc +1, Eva +1, HP +7 | 2 AP to begin, 1 AP/turn |  | Cost: 2 AP to begin, 1 AP to continue during subsequent turns Raising your hands above you and whistling, you call down death from above. Native animals dive down and attack your victim, a victim who can be up to 50 feet away. Depending on your surroundings, these creatures might be fish, bats, birds, or even insects, though they’re never larger than a human’s fist. When you first call the animals, you must make an accuracy roll against the target’s evade (just like a normal attack). If you hit them with your summoned avians, they deal damage as per the tiers below. This damage can be soaked.<br>Anything that would affect an area (such as an explosion or gas) disrupts the swarm (forcing you to start over, if you so desire). If at any point you lose the ability to speak, the swarm is disrupted. You may not talk while continuing an avian wrath or use any specialties requiring the use of your voice. Animals deal 6 inital damage, 3 damage when continued Animals deal 12 inital damage, 6 damage when continued Animals deal 18 inital damage, 9 damage when continued Animals deal 24 inital damage, 12 damage when continued | [ACTION] |
| **Blacken the Sky** | Bird Calling | Acc +1, Eva +1, HP +8 | Passive; resist Cunning (negates) | Avian Wrath | reQuires: Avian Wrath specialty<br>resist: Cunning (negates)<br>When using avian wrath, the swarm of squaking animals becomes so dense that it distracts your foe. Every turn an opponent is hit by your avian wrath, they must resist against your Shamanism or be disoriented (losing 1 action point). Once your avian wrath stops, they become re-oriented. | [COND] [REQ] |
| **Pitch Black** | Bird Calling | Acc +1, Eva +1, HP +8 | Passive | Avian Wrath; Blacken the Sky | reQuires: Avian Wrath & Blacken the Sky specialties When using Avian Wrath, your swarm becomes so thick and fast that it blocks out all light around your victim. The victim is now blinded while they remain the target of the avian wrath. | [COND] [REQ] |
| **Venom Immunity** | Chemical Immunity | Eva +1, Def +2, HP +10 | Passive |  | Being stung, being bitten, having venom injected into your body: these things used to be a big deal, but they’re less worrisome now-a-days. When you are attempting to resist a poison, add your skill in shamanism to the resist roll. | [COND] [SCALE:Shamanism] |
| **Alchemical Resistance** | Chemical Immunity | Eva +1, Def +3, HP +9 | Passive | Venom Immunity | reQuires: Venom Immunity specialty<br>You’ve trained your body to ward off venoms, both natural and unnatural. When resisting any alchemical substances (gases, acids, poisons, et cetera), add your skill in Shamanism to the roll. | [COND] [REQ] [SCALE:Shamanism] |
| **Protect the Monarch** | Protective Swarm | Def +2, Pri +1, HP +9 | 2 AP to begin, 1 AP/turn |  | Cost: 2 AP to begin, 1 AP to continue during subsequent turns By vibrating your vocal cords, you trgger a defense mechanism in nearby creatures that swarm you, protecting you from harm. As with all swarms, these are creatures native to the terrain ranging from fishes to small woodland creatures and even insects, though they are never larger than a fist.<br>Anything that would affect an area disrupts the swarm and it must be reformed again (costing 2 action points). If at any point you lose the ability to speak, the swarm is disrupted. You may not talk while continuing a protect the monarch or use any specialties requiring you to use your voice. You may only be covered in one swarm at a time.<br>+1 soak class<br>+2 soak class<br>+3 soak class<br>+4 soak class | [ACTION] [STAT:Soak +1..+4] |
| **Devoted Drones** | Protective Swarm | Def +3, Pri +1, HP +10 | Passive | Protect the Monarch | reQuires: Protect the Monarch specialty<br>The swarm covering your body is willing to die in order to protect you. When using protect the monarch, the swarm is only disrupted when dismissed (such as when you stop spending action points on it) or until your next breather. | [PASSIVE] [REQ] |
| **Hive Exodus** | Protective Swarm | Def +2, Spd +5, HP +7 | Passive | Protect the Monarch | reQuires: Protect the Monarch specialty<br>Be it from lifting you up into the air or dragging you across the battlefield, each turn you spend with Protect the Monarch active, your swarm may move you in any direction. If moved into the air the swarm maintains you there each turn until disturbed. You are moved 5 feet<br>You are moved 10 feet<br>You are moved 15 feet<br>You are moved 20 feet | [COND] [REQ] |
| **Colony of One** | Swarming Insect | Acc +1, Stk +1, HP +8 | 2 AP to begin, 1 AP/turn; resist Brute or Dex (negates, as grab) |  | resist: Brute or Dexterity (negates, as per a grab) Cost: 2 AP to begin, 1 AP to continue during subsequent turns By humming at a very low frequency, you are able to call a swarm of native insects or animals to overwhelm your victim and hold them in place. These creatures can be anything smaller than your fist and native to the area. The swarm uses your accuracy when making a grab against its target no farther then 50 feet away. In order for the victim to break free they must roll resist against your skill in shamanism (using their brute or dexterity). Anything that would affect an area (such as an explosion or gas) disrupts the swarm (forcing you to start over, if you so desire). If at any point you lose the ability to speak, the swarm is disrupted. You may not talk while continuing a colony of one or use any specialties requiring the use of your voice. The swarm grabs one called shot location<br>The swarm grabs one called shot location<br>The swarm grabs two called shot locations<br>The swarm grabs two called shot locations | [ACTION] |
| **Drag Down** | Swarming Insect | Acc +1, Stk +1, HP +8 | Passive; resist Brute (negates) | Colony of One | reQuires: Colony of One specialty<br>resist: Brute (negates)<br>The vermin swarm pulls its opponents to the ground. Any foe successfully grabbed by your Colony of One is also brought prone unless they can make a brute resist against your Shamanism. | [COND] [REQ] |
| **Hive Mind** | Swarming Insect | Acc +1, Eva +1, HP +9 | Passive | Colony of One | reQuires: Colony of One specialty<br>When continuing a swarm, it is no longer disrupted when you are knocked prone or rendered unable to speak. This means you may now freely speak and use specialties requiring speech without having to call out your swarms again. | [PASSIVE] [REQ] |
| **Pressure Cooker** | Swarming Insect | Acc +1, Stk +2, HP +9 | Passive | Colony of One | reQuires: Colony of One specialty<br>The swarm of creatures holding down the victim begins to move rapidly, cooking them with sheer friction. Each turn after grabbing a target with colony of one, a point or more of unsoakable damage is dealt to the target.<br>Takes 1 unsoakable damage<br>Takes 2 unsoakable damage<br>Takes 3 unsoakable damage<br>Takes 4 unsoakable damage | [COND] [REQ] |

### 6.7 Sciences specialties

#### Crafting system (Sciences, p.162–163) — rules common to all six Science skills
- **Learning augments:** every "Aug +X" bonus = X augments you may learn from lists you have access to (via a crafting specialty such as Gunsmith). A crafting specialty itself grants **2 augments** from its list (this is the Aug +2 in its bonus). An augment known once is known under every list with the same name (e.g. *Accurate*).
- **Placing:** each augment only once per item; items have **3 slots** (wood 2, organic 1 where stated), **Beta** +2 (only the crafter can reliably use; others need a Sciences tier one higher than the item's highest marque; mQ IV → need tier 5), **Prototype** = beta usable by anyone (market price of the extra 2 augments often doubled).
- **Complex augments** take several slots (noted per augment). Accessories take 0 slots.
- **Marque by skill points in that Science skill:**

| Skill points | 0–4 | 5–14 | 15–24 | 25+ |
|---|---|---|---|---|
| Marque | I | II | III | IV |

  Some augments are "always mQ X for cost" and learnable at any skill.
- **DIY (Do-It-Yourself):** number of free, self-maintained items per type (see each skill's DIY table); they stop working after more than one downtime away from you. Effective DIY caps at 12 (Efficiency Expert).
- **Buying/crafting quality items:** pay the price as if one marque lower (material cost = 1/5 market price); item keeps your marque; only where materials are available.
- **Downtime:** all crafting/re-augmenting happens in downtime (narrator-controlled). Retrofitting: whenever you learn a new augment you may swap one known augment from the same skill.
- **Disassemble/Understand:** see Sciences attribute uses.

**What anyone can do with Sciences (attribute uses):** Disassemble (Sciences tier: T1 small practical things / T2 simple trap/item mQ I–II / T3 complicated mQ III / T4 clever mQ IV) · Understand (T1 basic function / T2 + mQ I augments / T3 up to mQ II / T4 up to mQ III)

#### General (Sciences)

| Specialty | Group | Bonuses | Cost / type | Requires | Effect | Tags |
|---|---|---|---|---|---|---|
| **Learn Augments** |  | Aug +4, DIY +1, HP +4 | Passive (repeatable) |  | You learn the granted augments. You can take this specialty multiple times. | [AUG] [REPEATABLE] |
| **Nothing up my Sleeve** |  | Acc +1, Aug +2, HP +4 | Once between downtimes |  | You are known for always having the right item for the right job. At any given moment, you can craft an item on the fly, acting as though you already had it. It must be concealable (thus, you can’t just pull a tank or heavy rifle out of your pocket). You can only do this once between downtimes, and the item must be something you know how to craft (as in, you have taken the basic crafting specialty for the item and any augments you are going to put on it).<br>c A<br>Sometimes, you’ll<br>curate” augment<br>text, but they do<br>other.<br>Anytime<br>which section of<br>bows, bows, and<br>ment 4 different t<br>The Cost of Prototyping<br>Many inventors can produce beta objects: creations that exceed the normal augment limit of 3. These beta designs, however, are so difficult to use that only the original inventor can typically control them. But while many crafters can build betas, very few can build prototypes. Prototypes are objects that exceed the typical augment limit of 3 but that anybody can use.<br>The materials cost for creating the extra aug-<br>ments for prototypes is the same as it always is. However, because prototypes are so rare, those who create them will typically inflate the price for the extra effort and skill required to craft the items. When buying off the market, the extra 2 augments that prototypes allow will often be double the price of the normal 3 augment item.<br>gments with the Same Name c<br>find an “Accurate” augment under bow augments and an “Acnder weapon augments. They might have slightly different flavor the exact same thing. Well, if you learn one, you’ve learned the you learn an augment, you know that augment regardless of the book it falls under. If you learn how to craft firearms, crosselee weapons, there is no need to learn the “Damaging” augimes. Just learn it once, and you’re good to go! | [ACTION] |

#### Alchemy

| Specialty | Group | Bonuses | Cost / type | Requires | Effect | Tags |
|---|---|---|---|---|---|---|
| **Self-Made Immunity** | Immunity | Def +2, Aug +1, HP +8 | Passive | Acid Brewer, Gas Brewer or Poison Brewer | reQuires: Either Acid Brewer, Gas Brewer, or Poison Brewer specialty Due to prolonged exposures with your chemicals, your body has become immune to all of your harmful conconctions. Any harmful potions that you create, including contact poisons, can no longer harm you. | [PASSIVE] [REQ] |
| **Immunizations** | Immunity | Def +2, Aug +1, HP +6 | During a breather (15+ min) | Self-Made Immunity | reQuires: Self-Made Immunity specialty<br>You can brew your potions based on your friend’s chemical makeup, ensuring that they are also immune to your harmful concoctions. During any breather (a period of 15 minutes or more), you can immunize an ally against your harmful potions. From that point on, they are immune to any potions that you create until you specify that they are not. You can also designate potions against which they are not immune. | [ACTION] [REQ] |
| **On-the-Fly Brewer** | On-The-Fly | Eva +1, Aug +2, HP +4 | 3 AP per augment slot (0-slot augments 1 AP) |  | Cost: 3 AP per augment slot<br>You carry many of your basic chemicals on you and can mix them during the heat of battle to create that all-so-necessary potion. You can create any potion on-the-fly as long as you have some basic chemicals on you. You can never have any more of your own potions brewed than your DIY score would allow. You may divide the action points spent brewing your potions over as many turns as you would like. Augments that do not have a slot cost require only 1 action point to be put in the potion. | [ACTION] |
| **Expiration** | On-The-Fly | Eva +1, Aug +2, HP +4 | Passive | On-the-Fly Brewer | reQuires: On-the-Fly Brewer specialty<br>Any of the chemicals that you brew on-the-fly can be brewed with an expiration time. The potion may either activate upon expiring or become a dud. If you set the potion to activate, acids will eat through the vial, and gases will be automatically released. Once the dud potion expires, it’s little more useful than water (and fails to even provide the hydrating benefits of water). You may set the potion to expire within up to 5 turns. The potion will expire at the end of your turn, based on the number of turns set. | [COND] [REQ] |
| **Herbalist** | On-The-Fly | Aug +2, DIY +1, HP +5 | Passive | On-the-Fly Brewer | reQuires: On-the-Fly Brewer specialty<br>The world is your chemistry set. You have no need for urban chemicals, and can create your potions with only those things found in the wild. Lost in the forest? The herbs will provide everything you need. Stuck in a dank dungeon? Look for an underground stream and some moss. You can use On-the-Fly Brewer without any need for basic chemicals, and can do so almost anywhere. | [PASSIVE] [REQ] |
| **Rapid Mixer** | On-The-Fly | Eva +1, Aug +1, HP +5 | 1 AP per augment slot (0-slot free) | On-the-Fly Brewer | reQuires: On-the-Fly Brewer specialty<br>Cost: 1 AP per augment slot<br>You have little need for pre-prepared potions. You can now brew potions on-the-fly for only 1 action point per augment slot used in the potion. Augments that cost 0 slots on the potion may be placed on the potion for no action point cost. | [ACTION] [REQ] |
| **Walking Chemical Plant** | On-The-Fly | Eva +1, Aug +1, HP +5 | Passive | On-the-Fly Brewer; Expiration | reQuires: On-the-Fly Brewer & Expiration specialty You can brew potions well past your normal DIY score. You may brew as many potions as you’d like; however, all potions you brew past your DIY limit expire and become duds within a number of turns after you brew them. (At your discretion, you can cause them to expire earlier.)<br>Expires at the end of your next turn<br>Expires up to 2 turns later<br>Expires up to 3 turns later<br>Expires up to 4 turns later<br>General Alchemy Augments<br>These are augments that, once learned, can be placed on almost any acid, gas, medicine, or poison. | [COND] [REQ] |
| **Acid Brewer** | Crafting Acids | Aug +2, DIY +1, HP +5 | Passive (crafting) |  | When we say acids, we’re not talking about citrus-based cleaning supplies. We’re talking about acids that eat through metals within seconds, acids that burn skin, and acids that reduce the iron of a sword to its original form. You can now brew acids. Acids are often used to attack a single person.<br>Without spending any money, you can brew and maintain several acids based on your current Do-It-Yourself (DIY) score. These acids can then be upgraded with augments. You’ll learn 2 augments from this specialty which can be selected under “acid augments” below. These augments have marques. At lower levels, you’ll start with Marque I augments. As your skill in Alchemy improves, your marques will increase. See the “Crafting” page at the beginning of this chapter for more information. Each acid can be upgraded with 3 augments. Sometimes an augment will take up multiple augment slots. For example, the “flesh burner” augment is worth 2 slots, so an acid only has 1 more available slot for an augment after “flesh burner” has been applied.<br>resisting aCiDs<br>All acids can be resisted with a brute roll. For every tier of brute rolled above Tier 1, the marque of the acid is reduced by 1. numBer oF aCiDs you Can maintain<br>Without needing to buy chemicals, you can brew some acids entirely out of scraps. These acids must be constantly maintained by you and stop working soon after leaving your care. You can build and maintain a number of acids based on your DIY score. You can brew new acids or augment old ones during any period of downtime you have.<br>your Diy: 1 2 3 4 5 6<br>you Can BuiLD: 3 4 4 4 5 5<br>your Diy: 7 8 9 10 11 12<br>you Can BuiLD: 5 6 6 6 7 7<br>the Cost oF aCiDs<br>If you need to brew an acid that you can’t build for free from your DIY score, you will need to buy the materials for it. Every augment will increase the price. The higher the marque, the greater the price. The market price for an augment can be found in the chart below.<br>marQue I II III IV<br>market priCe 3 princes 15 princes 75 princes 375 princes If you are brewing the augment, you pay 1/5th the price, which is the same as if you were buying an augment one marque lower. (As in, the material cost for a Marque III augment is the market price fo a Marque II augment.) The material cost for a Marque 1 augment is 6 dukes. | [AUG] [DIY] [CRAFT:acid] |
| **Beta Acids** | Crafting Acids | Aug +2, DIY +1, HP +5 | Passive | 4 Alchemy; Acid Brewer | reQuires: 4 skill points in Alchemy & Acid Brewer specialty Your acids go far beyond what most other chemists dream of, yet they are difficult for most people to use. Such acids have two more slots for you to place augments into.<br>If anybody other than you attempts to use one of your beta acids, they must succeed in rolling a science result one tier higher than the highest level marque you have on your acid. If your acid has a Marque IV augment, it is impossible for them to use it (unless they can somehow obtain a tier result of 5 with their science attribute). | [CRAFT] [REQ] |
| **Prototype Acids** | Crafting Acids | Aug +1, DIY +1, HP +6 | Passive | 16 Alchemy; Acid Brewer; Beta Acids | reQuires: 16 skill points in Alchemy, Acid Brewer, & Beta Acids You’ve perfected your beta acids and made them user-friendly. Now anybody can use an acid that you designate as being a prototype. | [CRAFT] [REQ] |
| **Gas Brewer** | Crafting Gases | Aug +4, DIY +1, HP +4 | Passive (crafting) |  | You can whip up the most eye-bleeding, mouth-gagging, toxic gases around. You can now brew gases.<br>Gases affect the space that the gas was released, and every adjacent space. Every turn, the gas has a chance of leaving, which the narrator will roll for at the end of the every turn after they throw it. The likelihood of the gas dissipating is based on how windy it is, with Tier 1 being absolutely no wind (such as a small, airtight room) and Tier 4 being a very windy area (such as during a storm or aboard a fast-flying ironbird). See the sidebar: Dispersing Gases.<br>Without spending any money, you can brew and maintain several gases based on your current Do-It-Yourself (DIY) score. These gases can then be upgraded with augments. You’ll learn 2 augments from this specialty, which can be selected under “gas augments” below. These augments have marques. At lower levels, you’ll start with Marque I augments. As your skill in Alchemy improves, your marques will increase. See the “Crafting” page at the beginning of this chapter for more information. Each gas can be upgraded with 3 augments. Sometimes an augment will take up multiple augment slots. For example, the “blinding” augment is worth 2 slots, so a gas only has 1 more available slot for an augment after “blinding” has been applied. resisting gases<br>All gases can be resisted with a brute roll. For every tier of brute rolled above Tier 1, the marque of the gas is reduced by 1. numBer oF gases you Can maintain<br>Without needing to buy chemicals, you can brew some gases entirely out of scraps. These gases must be constantly maintained by you and stop working soon after leaving your care. You can build and maintain a number of gases based on your DIY score. You can brew new gases or augment old ones during any period of downtime you have.<br>your Diy: 1 2 3 4 5 6<br>you Can BuiLD: 3 3 4 4 4 5<br>your Diy: 7 8 9 10 11 12<br>you Can BuiLD: 5 5 6 6 6 7<br>the Cost oF gases<br>If you need to brew a gas that you can’t create for free from your DIY score, you will need to buy the materials for it. Every augment will increase the price. The higher the marque, the greater the price. The market price for an augment can be found in the chart below.<br>marQue I II III IV<br>market priCe 4 princes 20 princes 100 princes 500 princes Dispersing Gases<br>The conditions of the battlefield often determine the amount of time a gas can remain on the field without dispersing naturally. When determining if a gas is dispersed, the narrator rolls to determine whether or not the gas is dispersed, giving no special bonuses to the roll unless otherwise stated. Gases cannot be deployed underwater, and the conditions of wind have the greatest effect on the dispersing of gases. Each turn, the narrator rolls and must surpass the required roll based on the tier of the wind to determine if the gas remains.<br>tier 1 T is h s e ta g g a n s a w nt i l a l i s r t . ay on a roll of 2 or higher. Tier 1 wind tier 2 T is h a e b g r a e s e z w e i . ll stay on a roll of 5 or higher. Tier 2 wind tier 3 T is h a e g g u a s s t . will stay on a roll of 9 or higher. Tier 3 wind tier 4 T is h a e s g tr a o s n w g i l g l u st s a t. y on a roll of 12 or higher. Tier 4 wind Gases can also be dispersed by certain other forces. When something moves through the area, it will disperse the gas unless the narrator rolls a 5 or more. If a bomb goes off in the gas, it will disperse the gas unless the narrator rolls a 9 or more. Gases with expirations disperse naturally or cannot be deployed when they expire.<br>If you are brewing the augment, you pay 1/5th the price, which is the same as if you were buying an augment one marque lower. (As in, the material cost for a Marque III augment is the market price fo a Marque II augment.) The material cost for a Marque 1 augment is 8 dukes. | [AUG] [DIY] [CRAFT:gas] |
| **Beta Gases** | Crafting Gases | Aug +2, DIY +1, HP +4 | Passive | 4 Alchemy; Gas Brewer | reQuires: 4 skill points in Alchemy & Gas Brewer specialty Your gases are much more lethal than most, yet they are difficult for most people to use. Such gases have two more slots for you to place augments into.<br>If anybody other than you attempts to use one of your beta gases, they must succeed in rolling a science result one tier higher than the highest level marque you have on your gas. If your gas has a Marque IV augment, it is impossible for them to use it (unless they can somehow obtain a tier result of 5 with their science attribute). | [CRAFT] [REQ] |
| **Prototype Gases** | Crafting Gases | Aug +1, DIY +1, HP +4 | Passive | 16 Alchemy; Gas Brewer; Beta Gases | reQuires: 16 skill points in Alchemy, Gas Brewer, & Beta Gases You’ve perfected your beta gases and made them user-friendly. Now anybody can use a gas that you designate as being a prototype. | [CRAFT] [REQ] |
| **Medicine Brewer** | Crafting Medicines | Aug +2, DIY +1, HP +5 | Passive (crafting) |  | Medicinal potions are used to restore hit points, heal wounds, fight off poisons, and a variety of other beneficiary effects. All medicinal potions must be injected or ingested.<br>Without spending any money, you can brew and maintain several medicines based on your current Do-It-Yourself (DIY) score. These medicines can then be upgraded with augments. You’ll learn 2 augments from this specialty, which can be selected under “medicine augments” below. These augments have marques. At lower levels, you’ll start with Marque I augments. As your skill in Alchemy improves, your marques will increase. See the “Crafting” page at the beginning of this chapter for more information.<br>Each medicine can be upgraded with 3 augments.<br>Sometimes an augment will take up multiple augment slots. For example, the “heavy push” augment is worth 3 slots, so a medicine has 0 available slot for an augment after “heavy push” has been applied.<br>numBer oF meDiCines you Can maintain<br>Without needing to buy chemicals, you can brew some medicines entirely out of scraps. These medicines must be constantly maintained by you and stop working soon after leaving your care. You may build and maintain a number of medicines based on your DIY score. You may brew new medicines or augment old ones during any period of downtime you have.<br>your Diy: 1 2 3 4 5 6<br>you Can BuiLD: 5 5 5 6 6 6<br>your Diy: 7 8 9 10 11 12<br>you Can BuiLD: 7 7 7 8 8 9<br>the Cost oF meDiCines<br>If you need to brew a medicines that you can’t create for free from your DIY score, you will need to buy the materials for it. Every augment will increase the price. The higher the marque, the greater the price. The market price for an augment can be found in the chart below.<br>marQue I II III IV<br>market priCe 4 princes 20 princes 100 princes 500 princes If you are brewing the augment, you pay 1/5th the price, which is the same as if you were buying an augment one marque lower. (As in, the material cost for a Marque III augment is the market price fo a Marque II augment.) The material cost for a Marque 1 augment is 8 dukes. | [AUG] [DIY] [CRAFT:medicine] |
| **Beta Medicines** | Crafting Medicines | Aug +2, DIY +1, HP +6 | Passive | 4 Alchemy; Medicine Brewer | reQuires: 4 skill points in Alchemy & Medicine Brewer specialty While it is impossible for others to administer your medicines, they’re well worth the hassle. Your beta medicines have two more slots for you to place augments into.<br>If anybody other than you attempts to use one of your beta medicines, they must succeed in rolling a science result one tier higher than the highest level marque you have on your medicine. If your medicine has a Marque IV augment, it is impossible for them to use it (unless they can somehow obtain a tier result of 5 with their science attribute). | [CRAFT] [REQ] |
| **Prototype Medicine** | Crafting Medicines | Aug +1, DIY +1, HP +7 | Passive | 16 Alchemy; Medicine Brewer; Beta Medicines | reQuires: 16 skill points in Alchemy, Medicine Brewer, & Beta Medicine specialties<br>You’ve perfected your beta medicines and made them user-friendly. Now anybody can use a medicine that you designate as being a prototype. | [CRAFT] [REQ] |
| **Poison Brewer** | Crafting Poisons | Aug +2, DIY +1, HP +4 | Passive (crafting) |  | Poisons are rarely seen as the most savory tools of war; nonetheless, they remain ever popular. Poisons kill, disable, and bring great discomfort to those injected with them.<br>Poisons are always a little difficult to find, requiring a tier 2 cunning result to notice. A person can always volunteer to look at something to see if it is poisoned, such as trying to notice poison on a sword or in a drink.<br>Poisons must either be consumed by the target or injected (as can happen on the battlefield, when a blade is coated in poison). The basic poison will activate within the target after the target has used 3 action points.<br>Without spending any money, you can brew and maintain several poisons based on your current Do-It-Yourself (DIY) score. These poisons can then be upgraded with augments. You’ll learn 2 augments from this specialty, which can be selected under “poison augments” below. These augments have marques. At lower levels, you’ll start with Marque I augments. As your skill in Alchemy improves, your marques will increase. See the “Crafting” page at the beginning of this chapter for more information. Each poison can be upgraded with 3 augments. Sometimes an augment will take up multiple augment slots. For example, the “hallucinogenic” augment is worth 2 slots, so a poison only has 1 available slot for an augment after “hallucinogenic” has been applied.<br>resisting poisons<br>All poisons can be resisted with a brute roll. For every tier of brute rolled above Tier 1, the marque of the poison is reduced by 1.<br>numBer oF poisons you Can maintain<br>Without needing to buy chemicals, you can brew some poisons entirely out of scraps. These poisons must be constantly maintained by you and stop working soon after leaving your care. You can brew and maintain a number of poisons based on your DIY score. You can brew new poisons or augment old ones during any period of downtime you have.<br>your Diy: 1 2 3 4 5 6<br>you Can BuiLD: 3 3 3 4 4 4<br>your Diy: 7 8 9 10 11 12<br>you Can BuiLD: 4 5 5 5 5 6<br>the Cost oF poisons<br>If you need to brew a poison that you can’t create for free from your DIY score, you will need to buy the materials for it. Every augment will increase the price. The higher the marque, the greater the price. The market price for an augment can be found in the chart below.<br>marQue I II III IV<br>market priCe 4 princes 20 princes 100 princes 500 princes If you are brewing the augment, you pay 1/5th the price, which is the same as if you were buying an augment one marque lower. (As in, the material cost for a Marque III augment is the market price fo a Marque II augment.) The material cost for a Marque 1 augment is 8 dukes. | [AUG] [DIY] [CRAFT:poison] |
| **Beta Poisons** | Crafting Poisons | Aug +2, DIY +1, HP +4 | Passive | 4 Alchemy; Poison Brewer | reQuires: 4 skill points in Alchemy & Poison Brewer specialty Your poisons are difficult to use but oh-so-effective. Your beta poisons have two more slots for you to place augments into. If anybody other than you attempts to use one of your beta poisons, they must succeed in rolling a science result one tier higher than the highest level marque you have on your poisons. If your poison has a Marque IV augment, it is impossible for them to use it (unless they can somehow obtain a tier result of 5 with their science attribute). | [CRAFT] [REQ] |
| **Prototype Poisons** | Crafting Poisons | Aug +1, DIY +1, HP +5 | Passive | 16 Alchemy; Poison Brewer; Beta Poisons | reQuires: 16 skill points in Alchemy, Poison Brewer, & Beta Poisons specialties<br>You’ve perfected your beta poisons and made them user-friendly. Now anybody can use a poison that you designate as being a prototype. | [CRAFT] [REQ] |

##### Alchemy – potion rules (p.164–165)
- **Draw & drink:** 1 AP; provokes melee reflexes (attack, arm called shot = disarm, sunder the potion).
- **Throw:** 2 AP (must be drawn), damage as unarmed, range 25 ft; miss → lands nearby and breaks. Tossing to an ally needs no roll; catching needs a free hand (0 AP), may drink reflexively on catch.
- **Apply poison to weapon:** 3 AP; used on the first damaging hit (after soak); not on bullets; one poison per weapon.
- **Resisting:** acids, gases, poisons (default): Brute; each tier above T1 lowers the potion's marque by 1.
- **Beta** = +2 slots (5 total), only the crafter can use reliably; **Prototype** = anyone can.

**DIY → number of potions you can maintain for free**

| DIY | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Acids | 3 | 4 | 4 | 4 | 5 | 5 | 5 | 6 | 6 | 6 | 7 | 7 |
| Gases | 3 | 3 | 4 | 4 | 4 | 5 | 5 | 5 | 6 | 6 | 6 | 7 |
| Medicines | 5 | 5 | 5 | 6 | 6 | 6 | 7 | 7 | 7 | 8 | 8 | 9 |
| Poisons | 3 | 3 | 3 | 4 | 4 | 4 | 4 | 5 | 5 | 5 | 5 | 6 |

**Augment market price per marque** (brewing yourself = price of one marque lower; mQ I material cost given separately)

| Type | mQ I | mQ II | mQ III | mQ IV | mQ I material cost |
|---|---|---|---|---|---|
| Acid | 3 pr | 15 pr | 75 pr | 375 pr | 6 dukes |
| Gas | 4 pr | 20 pr | 100 pr | 500 pr | 8 dukes |
| Medicine | 4 pr | 20 pr | 100 pr | 500 pr | 8 dukes |
| Poison | 4 pr | 20 pr | 100 pr | 500 pr | 8 dukes |

**Gas dispersal** (narrator roll each turn, gas stays on ≥): wind T1 stagnant 2+ · T2 5+ · T3 gust 9+ · T4 strong gust 12+. Something moving through: stays on 5+; bomb in gas: 9+. No gases underwater.

##### General alchemical augments (any acid, gas, medicine, poison)

| Augment | Slots | Effect | Cost note |
|---|---|---|---|
| Contact | 1 | Potion works on contact — throw at ally, no catching/drinking needed. | always priced as mQ I; learnable at any skill |
| Solid | 1 | Pill/glob with coating; works underwater/in liquids until broken. | always mQ I |

**Book texts:**

**Contact** — *General Alchemical Augment*  
> The potion seeps through skin and armor, going straight into the blood stream. You can now simply throw the vial at an ally in order for the potion to affect them. They do not need to catch it and drink it themselves.  
> Note: This augment always acts as marque I for the purposes of determining cost, though you can learn this augment despite your skill in alchemy.  

**Solid** — *General Alchemical Augment*  
> You develop your alchemical substances as a pill or small glob with a protective coating. The substance takes on a solid state, so that it can exist underwater or in other liquids. It will stay that way until broken.  
> Note: This augment always acts as marque I for the purposes of determining cost, though you can learn this augment despite your skill in alchemy.  


##### Acid augments (p.166–167)

| Augment | Slots | mQ I | mQ II | mQ III | mQ IV | Notes |
|---|---|---|---|---|---|---|
| Burns | 1 | T1 burns (−1 Def) | T2 burns (−3 Def) | T3 (−5 Def) | T4 (−7 Def) | resistable; until breather |
| Flesh Burner | 2 | 6 dmg or −1 DC/soak | 12 / −2 | 18 / −3 | 24 / −4 | vs living/organic; on organic armor lowers soak (not resistable); called shot on organic weapon lowers DC; repair at breather |
| Metal Melter | 2 | 6 dmg or −1 DC/soak | 12 / −2 | 18 / −3 | 24 / −4 | vs automatons/metal vehicles/metal armor & weapons; same rules |
| Rusting | 2 | −5 speed, −10 swim/climb | −10, −10 | −10, −15 | −15, −15 | vs medium+ metal armor; automatons/vehicles: regular speed only |
| Splash | 1 | +1 adjacent space | +2 | +3 | +4 | |
| Thick Rust (req. Rusting) | 1 | −3 Dex | −6 Dex | −9 Dex | −12 Dex | doffing armor costs double AP; cleaned at breather |
| Wood Wrecker | 2 | 6 dmg or −1 DC/soak | 12 / −2 | 18 / −3 | 24 / −4 | vs wooden creations/armor/weapons |

**Book texts:**

**Burns** — *Acid Augment*  
> This acid burns the skin of the person it is thrown on. This is resistable and goes away after taking a breather.  
> Tier 1 burns (giving you a -1 on defense rolls)  
> Tier 2 burns (giving you a -3 on defense rolls)  
> Tier 3 burns (giving you a -5 on defense rolls)  
> Tier 4 burns (giving you a -7 on defense rolls)  

**Flesh Burner** — *Acid Augment*  
> takes up 2 augment sLots on the aCiD  
> Flesh burning acid damages living people and organic tissue. If used on a person, it deals damage to them. If simply thrown on somebody, it will lower the soak class of the person’s armor (and cannot be resisted). (If thrown on a person wearing organic armor, it will affect the armor first.) If a called shot is made to the person’s organic weapon (or another wielded item), it will lower the damage class of the weapon. If used on an organic trinket or gizmo of any sorts, it will render the item unusable until the item can be hammered out. Normally a weapon or armor can be banged back to its original form during a breather (15 minutes or more).  
> 6 damage or a -1 to damage or soak class  
> 12 damage or a -2 to damage or soak class  
> 18 damage or a -3 to damage or soak class  
> 24 damage or a -4 to damage or soak class  

**Metal Melter** — *Acid Augment*  
> takes up 2 augment sLots on the aCiD  
> This melts away metals, causing them to lose their form and substance. If used on an automaton, metal vehicle, or somebody inexplicably made of metal, it deals damage to them. If simply thrown on somebody wearing armor, it will lower the soak class of the person’s armor (and cannot be resisted). (If thrown on a metal creation wearing armor, it will affect the armor first until the armor is gone.) If a called shot is made to the person’s weapon (or another wielded item), it will lower the damage class of the weapon. If used on a trinket or gizmo of any sorts, it will render the item unusable until the item can be hammered out. Normally a weapon or armor can be banged back to its original form during a breather (15 minutes or more).  
> 6 damage or a -1 to damage or soak class  
> 12 damage or a -2 to damage or soak class  
> 18 damage or a -3 to damage or soak class  
> 24 damage or a -4 to damage or soak class  

**Rusting** — *Acid Augment*  
> takes up 2 augment sLots on the aCiD  
> The acid rapidly begins to rust armor and washes out important lubrication, causing the armor to lock up. When an opponent is in medium or heavier metal armor, and is splashed with the acid, it begins to grind on itself, decreasing movement speed.  
> -5 speed, -10 swim and climb speeds  
> -10 speed, -10 swim and climb speeds  
> -10 speed, -15 swim and climb speeds  
> -15 speed, -15 swim and climb speeds  
> Automatons and vehicles effected by the rusting augment take the penalty to regular speed only.  

**Splash** — *Acid Augment*  
> Your acids splash against multiple spots. The marque of this augment determines how many adjacent spaces the acid will splash into an effect.  
> Affects 1 adjacent space  
> Affects 2 adjacent spaces  
> Affects 3 adjacent spaces  
> Affects 4 adjacent spaces  

**Thick Rust** — *Acid Augment*  
> reQuires: Rusting Augment  
> The acid gets into the finer pieces of the armor, beginning to rust in even the smallest movements. The opponent takes a penalty to dexterity and also must spend twice as many action points to get out of their armor. The armor can be cleaned out during the next breather.  
> -3 dexterity  
> -6 dexterity  
> -9 dexterity  
> -12 dexterity  

**Wood Wrecker** — *Acid Augment*  
> takes up 2 augment sLots on the aCiD  
> This melts away wood, causing it to lose its form and substance. If used on a wooden automaton, vehicle, or somebody inexplicably made of wood, it deals damage to them. If simply thrown on somebody wearing wooden armor, it will lower the soak class of the person’s armor (and cannot be resisted). (If thrown on a wooden creation wearing wooden armor, it will affect the armor first, until the armor is gone.) If a called shot is made to the person’s wooden weapon (or another wielded item), it will lower the damage class of the weapon. If used on a wooden trinket or gizmo of any sorts, it will render the item unusable until the item can be hammered out. Normally a weapon or armor can be banged back to its original form during a breather (15 minutes or more).  
> 6 damage or a -1 to damage or soak class  
> 12 damage or a -2 to damage or soak class  
> 18 damage or a -3 to damage or soak class  
> 24 damage or a -4 to damage or soak class  


##### Gas augments (p.169–170)

| Augment | Slots | mQ I | mQ II | mQ III | mQ IV | Notes |
|---|---|---|---|---|---|---|
| Area of Effect | 2 | within 10 ft | 15 ft | 20 ft | 25 ft | can be made smaller |
| Arm Mutation | 1 | −1 for 3 turns | −2 / 4 turns | −3 / 5 turns | −4 / 6 turns | on rolls using the arm; resist needs Resilience(?) one tier above marque (book says "resilience result") |
| Blinding | 2 | 1 turn | 2 | 3 | 4 | −4 Acc/Eva in gas; lingers after leaving for listed turns |
| Corrosive | 1 | 3 dmg | 6 | 9 | 12 | HP damage at end of each turn inside |
| Confusing | 1 | 1 turn | 2 | 3 | 4 | auto-1 on Cunning rolls; lasts after leaving |
| Fogging | 1 | poor lighting (−2 Acc/Eva) | – | – | – | always mQ I cost; also for shooting through |
| Internal Burning | 1 | 1 dmg for 3 AP | 2 dmg for 4 AP | 3 for 5 AP | 4 for 6 AP | damage per AP spent; target may forgo AP |
| Lingering | 1 | re-roll dispersal 1× | 2× | 3× | 4× | |
| Luminescent Gas | 1 | −3 sneak/hide | −6 | −9 | −12 | resisted by Dex; washes off (water, 1 turn rain, 12 AP) |
| Paranoia | 3 | attack nearest at −3 Acc/Stk | −2 | −1 | no penalty | next AP (or 2) must attack nearest; resist Cunning or Spirit |
| Replicating | 2 | spreads to adjacent areas | within 10 ft | 15 ft | 20 ft | when someone dies in it; indefinitely |
| Slowing | 1 | −5 ft speed | −10 | −15 | −20 | 3 turns, min 5 ft |
| Sticky | 1 | −1 Evade | −2 | −3 | −4 | 3 turns |
| Stunning | 1 | stunned 1 AP | 1 AP | 2 AP | 2 AP | |
| Thick | 1 | wind counts 1 tier lower; moves with vehicle deck | – | – | – | always mQ I |

**Book texts:**

**Area Of Effect** — *Gas Augment*  
> takes up 2 augment sLots on the gas  
> Your gas affects more areas. You can, at your discretion, make the area of effect smaller than your normal marque allows. within 10 feet of the original space  
> within 15 feet of the original space  
> within 20 feet of the original space  
> within 25 feet of the original space  

**Arm Mutation** — *Gas Augment*  
> Your gas causes the nerves in their arm to become unwound, for their flesh to warp, and for their arms to become largely unusable. If effected with an arm mutation, the target may resist with a resilience result one tier higher than the mark of this augment. Any time the target makes a roll that uses the arm, including accuracy and strike (and evade if they attempt to deflect), the target suffers a penalty on the roll. The mutation lasts for a number of turns based on the mark.  
> -1 for 3 turns  
> -2 for 4 turns  
> -3 for 5 turns  
> -4 for 6 turns  

**Blinding** — *Gas Augment*  
> takes up 2 augment sLots on the gas  
> A blinding chemical burns the eyes of everyone within the area of the gas, to the point where opening their eyes is painful. Those within the blinding area suffer a -4 on accuracy and evade rolls. People may leave the area of the gas, but they remain blinded for a number of turns afterwards based on the marque of this gas (though this is resistable).  
> 1 turn  
> 2 turns  
> 3 turns  
> 4 turns  

**Corrosive** — *Gas Augment*  
> A corrosive chemical weapon deals damage to everything it hits. They can melt skin, destroy lungs, or worse. The corrosive does hit point damage to every person inside, every time they end their turn inside the corrosive gas (though this is resistable).  
> 3 damage  
> 6 damage  
> 9 damage  
> 12 damage  

**Confusing** — *Gas Augment*  
> Confusing gas disorients the target, making them unable to make cunning rolls. If the target fails to resist, they will automatically take a 1 on any cunning rolls they make. Furthermore, the confused victim will be unaware of their own confusion, and will naturally default to cunning if that is their highest attribute. Any person affected by the gas will remain in a confused state for a number of turns after leaving the gas (though this is resistable).  
> 1 turn  
> 2 turns  
> 3 turns  
> 4 turns  

**Fogging** — *Gas Augment*  
> A fogging gas blurs the vision of everyone within the area the weapon effects. Those within the fogging are effectively in poor lighting, suffering a -2 on accuracy and evade rolls. If somebody leaves the area they are no longer effected, or if somebody enters the area, they enter into the poor lighting. If somebody is trying to shoot through the fogging gas, they take the penalty as well. Note: This augment always acts as marque I for the purposes of determining cost, though you can learn this aug- ment despite your skill in alchemy.  

**Internal Burning** — *Gas Augment*  
> This gas burns mucles of the target with every action they take. They take damage with every action point they spend until the internal burning exhausts (though this is resistable). They may choose, however, to forgo action points - that is, if they have 3 action points for the turn, the target can wait for those 3 action points, and no damage will be done.  
> 1 damage for 3 action points  
> 2 damage for 4 action points  
> 3 damage for 5 action points  
> 4 damage for 6 action points  

**Lingering** — *Gas Augment*  
> Whatever you used, it stays where it was and continues to work its magic. If the narrator does not roll high enough for the gas to stay in the area, the narrator will re-roll. The narrator will do this a number of times based on the marque of the lingering. re-roll one time  
> re-roll two times  
> re-roll three times  
> re-roll four times  

**Luminescent Gas** — *Gas Augment*  
> The gas coats the skin and clothes of those within its range and glows, causing them to have extreme difficulty hiding. Instead of the normal brute resist, luminescent is resisted by dexterity. Opponents who are already hidden are automatically forced to re-roll if they fail to entirely resist the luminescence, this time with the penalty.  
> Luminescence will naturally wash off with water, after being in rain for 1 turn, or if the target can spend 12 action points brushing it off.  
> -3 on sneaking and hiding rolls  
> -6 on sneaking and hiding rolls  
> -9 on sneaking and hiding rolls  
> -12 on sneaking and hiding rolls  

**Paranoia** — *Gas Augment*  
> takes up 3 augment sLots on the gas  
> This chemical distresses the target and causes them to see things that aren’t there. Any affected by the paranoia must spend their next available action point (or two, if their only attack requires two action points) to attack the person closest to them, regardless of whether they are friend or foe. The paranoia makes the attack wild, however, and the targets suffer a penalty on their accuracy and strike rolls during this attack.  
> Instead of the normal brute resist, cunning or spirit can be used for the resist (at the target’s discretion).  
> -3 on accuracy and strike rolls for the paranoia attack  
> -2 on accuracy and strike rolls for the paranoia attack  
> -1 on accuracy and strike rolls for the paranoia attack no penalty on the accuracy or strike rolls for the paranoia attack  

**Replicating** — *Gas Augment*  
> takes up 2 augment sLots on the gas  
> Replicating gases feed on death, spreading further out with each victim it claims. Any time somebody dies in replicating gas, it feeds on the body to create more of itself, spreading out to affect everything within several adjacent areas of the original victim. It will continue to spread indefinitely.  
> spreads to adjacent areas  
> spreads to adjacent areas within 10 feet  
> spreads to adjacent areas within 15 feet  
> spreads to adjacent areas within 20 feet  

**Slowing** — *Gas Augment*  
> Those affected by your gas get stiff joints, feel frozen, instantly gain arthritis, or for some other reason can’t seem to move as fast as they once did. Their speed is reduced by the specified footage for three turns (though this reduction is resistable). They can never go below 5 feet.  
> 5 feet speed reduction  
> 10 feet speed reduction  
> 15 feet speed reduction  
> 20 feet speed reduction  

**Sticky** — *Gas Augment*  
> This chemical weapon causes the victims to become sticky, slowing down their reflexes. The target suffers a penalty on evade rolls for three turns (though this penalty is resistable).  
> -1 on evade rolls  
> -2 on evade rolls  
> -3 on evade rolls  
> -4 on evade rolls  

**Stunning** — *Gas Augment*  
> Your targets are stunned when they get hit by this gas. They are stunned for the specified action points (though this is resistable). stunned for 1 action point  
> stunned for 1 action point  
> stunned for 2 action points  
> stunned for 2 action points  

**Thick** — *Gas Augment*  
> This gas hugs the ground it’s released at. Winds in the area act as if they’re one tier lower when determining how long the gas lasts. In addition, if used on board a moving vehicle, the gas will sink onto the vehicle’s deck and move with the vehicle. Note: This augment always acts as marque I for the purposes of determining cost, though you can learn this augment despite your skill in alchemy.  


##### Medicine augments (p.171–172)

| Augment | Slots | mQ I | mQ II | mQ III | mQ IV | Notes |
|---|---|---|---|---|---|---|
| Antitoxin | 1 | +3 vs poisons | +6 | +9 | +12 | 1 hour; immediate re-roll vs current poison |
| Heavy Push | 3 | 10 unsoakable per extra AP, up to 2 AP | 9 dmg, up to 3 | 7 dmg, up to 4 | 6 dmg, up to 5 | max 1 extra AP per turn; unused vanish at breather |
| Improved Push (req. Push) | 2 | +10 HP | +20 | +30 | +40 | not above max |
| Liquid Skin | 2 | heal 1 wound | 2 | 3 | 4 | natural 1 on target's d12 → healing becomes damage |
| Pain Reliever | 1 | ignore 1 wound effect (locations 6–12) | 2 | 3 | 4 | until breather |
| Push | 1 | +4 HP | +8 | +12 | +16 | not above max |
| Slow Heart | 1 | +1 Acc | +2 | +3 | +4 | until breather (optional) |
| Stimulant | 1 | fatigue delayed 2 h | 4 h | 8 h | 24 h | once until rest |
| Styptic | 1 | stops all current bleeding | – | – | – | always mQ I |

**Book texts:**

**Antitoxin** — *Medicine Augment*  
> When you take an antitoxin, you gain a specified bonus against all poisons for the next hour. In addition, if you are currently poisoned, you may instantly reroll your resist against the poison with the bonus against it.  
> +3  
> +6  
> +9  
> +12  

**Heavy Push** — *Medicine Augment*  
> takes up 3 augment sLots on the meDiCine  
> While push stimulates the body to help it get over the beating it’s taken, heavy push takes it to a dangerous level. The muscles rip and the body cannot deal with the stress it’s being put under. This causes the heavy push to deal damage to the adminstrator, but gains action points instead. You can only use 1 extra action point per turn, and the damage is unsoakable. Any unused extra action points will go away during your next breather.  
> 10 backlash damage for each additional action point used, up to 2 extra action points  
> 9 backlash damage for each additional action point used, up to 3 extra action points  
> 7 backlash damage for each additional action point used, up to 4 extra action points  
> 6 backlash damage for each additional action point used, up to 5 extra action points  

**Improved Push** — *Medicine Augment*  
> takes up 2 augment sLots on the meDiCine  
> reQuires: Push augment known  
> Improved push takes your grandpappy’s old style push potions and gives them a jolt of electricity, making them push that much harder. Improved push potions return your hit points to you, though you cannot go over your maximum.  
> restores 10 hit points  
> restores 20 hit points  
> restores 30 hit points  
> restores 40 hit points  

**Liquid Skin - Wound Healing** — *Medicine Augment*  
> takes up 2 augment sLots on the meDiCine  
> Liquid skin instantly heals wounds damage. Healing this quickly, however, does so by infuriating the body’s natural regenerative system, and, made slightly wrong, can be very dangerous. When this is administered, the target rolls their die. If they receive a 1 on the twelve-sided die, they take the healing as damage.  
> 1 wound healed  
> 2 wounds healed  
> 3 wounds healed  
> 4 wounds healed  

**Pain Reliever** — *Medicine Augment*  
> Pain relieving medicines are designed to allow you to keep pushing on despite huge amounts of physical pain. When under the effects of pain killers you can ignore the wound effects 6-12 until your next breather.  
> Can ignore 1 such wound effect  
> Can ignore 2 such wound effects  
> Can ignore 3 such wound effects  
> Can ignore 4 such wound effects  

**Push - Hit Point Regain** — *Medicine Augment*  
> Push is a body stimulant that allows a person a boost in stamina, to ignore their wounds and to take a lot more punishment before falling. Push refills a person’s hit points, though it will not go over their maximum.  
> Restores 4 hit points  
> Restores 8 hit points  
> Restores 12 hit points  
> Restores 16 hit points  

**Slowheart** — *Medicine Augment*  
> This potion slows the target’s heart, releases stress, and allows the person to relax and breath easily. If the target chooses, they may ignore the calming effects of slowheart, but if they go with the flow and slow down a little bit, their accuracy will improve. The bonus lasts until their next breather.  
> +1  
> +2  
> +3  
> +4  

**Stimulant** — *Medicine Augment*  
> This stimulant is used to forego fatigue. If you are exhausted, taking a stimulant will push off the fatigue for a number of hours as specified by the potion’s marque. Once a stimulant has been used, the fatigue returns after the designated amount of time and another stimulant will have no effect until you rest.  
> 2 hours  
> 4 hours  
> 8 hours  
> 24 hours  

**Styptic** — *Medicine Augment*  
> A styptic is a useful substance that, when poured on a wound, dries the blood and keeps it from bleeding. Any person that this is administered to stops bleeding and will not bleed from any wounds or attacks they have suffered up to this point. Note: This augment always acts as marque I for the purposes of determining cost, though you can learn this augment despite your skill in alchemy.  


##### Poison augments (p.174–175)

| Augment | Slots | mQ I | mQ II | mQ III | mQ IV | Notes |
|---|---|---|---|---|---|---|
| Anti-Toxin Suppressor | 1 | negates mQ I antitoxins | II | III | IV | antitoxin must be 1 marque higher |
| Blinding | 2 | 2 turns | 4 | 6 | 8 | −4 Acc/Eva |
| Contortion | 3 | stay prone until 2 AP used/forgone | 4 AP | 6 AP | 8 AP | prone: −1 combat rolls, 5 ft move |
| Disorienting | 1 | 2 turns | 4 | 6 | 8 | −1 AP/turn |
| Dizzying | 1 | 2 turns | 4 | 6 | 8 | speed halved |
| Hallucinogenic | 2 | T2 Cunning to move, 1 turn | T2 for any action, 2 turns | T3, 3 turns | T3, 4 turns | fail = 1 AP wandering |
| Instant | 1 | acts immediately on delivery | – | – | – | always priced mQ II |
| Irresistible | 1 | resist Brute counts 1 tier lower | – | – | – | always priced mQ II |
| Painful | 1 | 6 HP dmg | 12 | 18 | 24 | |
| Push-Back | 2 | for 1 h push potions damage instead of heal | – | – | – | always priced mQ III; Brute-resistable |
| Slow-Acting | 1 | 4 h – 1 day | 3 h – 3 days | 2 h – 1 week | 1 h – 1 month | set at creation |
| Stunning | 1 | 1 AP | 2 | 3 | 4 | |
| Thirst | 1 | −1 Acc/Eva | −2 | −3 | −4 | until end of 3 turns |
| Undetectable | 1 | Cunning T3 to find | T3 | T4 | T4 | base is T2 |

**Book texts:**

**Anti-Toxin Suppressor** — *Poison Augment*  
> Anti-toxin suppressors are built into poisons specifically to target anti-toxins. If an anti-toxin is used against a poison that has a suppressor brewed into it, the suppressor will entirely negate the effects of the anti-toxin unless the anti-toxin is one marque higher than the suppressor.  
> Negates Marque I anti-toxins  
> Negates Marque II anti-toxins  
> Negates Marque III anti-toxins  
> Negates Marque IV anti-toxins  

**Blinding** — *Poison Augment*  
> takes up 2 augment sLots on the poison  
> This poison blinds the person, causing them to temporarily lose their eyesight. Being blind causes the target to take a -4 on accuracy and evade rolls. It lasts for an amount of time based on the marque.  
> 2 turns  
> 4 turns  
> 6 turns  
> 8 turns  

**Contortion** — *Poison Augment*  
> takes up 3 augment sLots on the poison  
> The target’s body siezes up and they fall to the ground, prone. Whle prone, you suffer a -1 on all combat rolls (accuracy, evade, strike, and defense) and cannot move more than 5 feet per turn. The target cannot willingly stand from prone until the target has used or forgone a specified number of action points, and if somebody lifts them, they immediately fall back down.  
> 2 action points  
> 4 action points  
> 6 action points  
> 8 action points  

**Disorienting** — *Poison Augment*  
> A disorienting poison causes the person’s nerves to be shot, for them to swoon and be unable to focus. A disorienting poison disorients the target (causing them to lose 1 action point per turn) until the end of a specified number of turns.  
> 2 turn  
> 4 turns  
> 6 turns  
> 8 turns  

**Dizzying** — *Poison Augment*  
> This poison dizzies the target, causing them to waver and fail to walk in a straight line. While dizzied, the target’s speed is cut in half (rounded down). The dizzying effect lasts until the end of a specified number of turns.  
> 2 turns  
> 4 turns  
> 6 turns  
> 8 turns  

**Hallucinogenic** — *Poison Augment*  
> takes up 2 augment sLots on the poison  
> A hallucinogenic poison causes the brain to spaz out and see things that are definitely not there (or so we think). A hallucinogenic poison forces the target to make a cunning roll every time he wants to take an action. A failure causes the target to spend one action point moving aimlessly (at the narrator’s discretion).  
> Tier 2 Cunning results required to move for 1 turn  
> Tier 2 Cunning results required to make any actions for  
> 2 turns  
> Tier 3 Cunning results required to make any actions for  
> 3 turns  
> Tier 3 Cunning results required to make any actions for  
> 4 turns  

**Instant** — *Poison Augment*  
> This poison now blossoms very quickly. Upon delivery being made, it occurs instantaneously. The poison acts as soon as it is delivered.  
> Note: This augment always acts as marque II for the purposes of determining cost, though you can learn this augment despite your skill in alchemy.  

**Irresistible** — *Poison Augment*  
> When a poison is made irresistible, the brute result required to resist the poison increases. Characters must act as if their brute roll to resist the blast was one tier lower.  
> Note: This augment always acts as marque II for the purposes of determining cost, though you can learn this augment despite your skill in alchemy.  

**Painful** — *Poison Augment*  
> Your poison does what poisons do best - it deals damage to their hit points. The painful augment does straight hit point damage (though it is resistable as per normal).  
> 6 damage  
> 12 damage  
> 18 damage  
> 24 damage  

**Push-Back** — *Poison Augment*  
> takes up 2 augment sLots on the poison  
> Push back is a rather devious poison used specifically to counter enemies who rely on push potions (that is, potions that restore their hit points). For the hour after somebody fails to resist a poison with push-back, any push potion they take will deal damage to them instead of restoring their hit points. The damage dealt is equal to the amount of hit points that would have been restored, but this is now resistable with your Brute.  
> Note: This augment always acts as marque III for the purposes of determining cost, though you can learn this augment despite your skill in alchemy.  

**Slow-Acting** — *Poison Augment*  
> A slow-acting poison takes longer to occur and is therefore harder to trace back to the person who administered it. Within the scope of your marque, you determine when the effect kicks in. You make this decision when you create the poison, and cannot alter it thereafter.  
> 4 hours - 1 day  
> 3 hours - 3 days  
> 2 hours - 1 week  
> 1 hour - 1 month  

**Stunning** — *Poison Augment*  
> The poison stuns the opponent, causing the opponent to respond slowly and lose action points. The target is stunned for the specified amount of action points.  
> 1 action point stunned  
> 2 action points stunned  
> 3 action points stunned  
> 4 action points stunned  

**Thirst** — *Poison Augment*  
> The poison interacts with the water in the person’s body, making it almost impossible for the water to function normally. This quickly dehydrates the person, causing them to lose focus. Due to this, they take a penalty on accuracy and evade rolls until the end of three turns.  
> -1 on accuracy and evade rolls  
> -2 on accuracy and evade rolls  
> -3 on accuracy and evade rolls  
> -4 on accuracy and evade rolls  

**Undetectable** — *Poison Augment*  
> When a poison is made undetectable, the cunning tier required to find it is increased.  
> Tier 3 Cunning result  
> Tier 3 Cunning result  
> Tier 4 Cunning result  
> Tier 4 Cunning result  




#### Armsmith

| Specialty | Group | Bonuses | Cost / type | Requires | Effect | Tags |
|---|---|---|---|---|---|---|
| **Belt Feeder** |  | Eva +2, Aug +1, HP +7 | 2 AP to begin, 1 AP/turn |  | Cost: 2 AP to begin, 1 AP to continue during subsequent turns You can feed in ammunition, allowing an adjacent gunman to keep firing without interuption. When you begin belt feeding, you select an adjacent ally. For that turn and every subsequent turn that you continue belt feeding (at the cost of 1 action point per turn), the targeted ally does not have to spend action points to ready their firearm. This only works on firearms that have a readying cost of 4 or less. If either you or your adjacent ally become separated, you must re-begin the belt feeding. | [ACTION] |
| **Interchangeable Parts** |  | Pri +2, Aug +1, HP +5 | 3 AP to swap (general version, p.176) |  | Cost: 3 AP<br>Your weapons are designed so that their parts can be replaced and altered in the middle of battle. This gives the weapons additional slots for augments, but these augments are not always active. At any time, a person can switch out the augments for 3 action points, activating one augment but deactivating another augment. You may replace multiple augments at the same time all for the cost of 3 action points.<br>This specialty works within the marque system. The amount of interchangeable slots the weapon has depends on the marque of its creator.<br>1 interchangeable slot for an augment<br>2 interchangeable slots for augments<br>3 interchangeable slots for augments<br>4 interchangeable slots for augments | [CRAFT] [SCALE:marque] |
| **Rapid Replacements** |  | Eva +1, DIY +1, HP +6 | 2 AP replace / 1 AP fix |  | Cost: 2 AP (to replace) or 1 AP (to fix)<br>Your sniper’s rifle just got snapped in two, and your brawler just got his chain cut in half. No worries - you’re there to help. For two action points, you can replace any broken weapon that you created (with the same weapon) as long as the current wielder is adjacent to you. Furthermore, if a weapon’s damage class has been lowered for any reason, you can return it to optimum efficiency for one action point. | [ACTION] |
| **Temporary Attachments** |  | Aug +2, DIY +1, HP +5 | 1 AP per augment slot |  | Cost: 1+ AP<br>Suddenly, in the heat of battle, your friend wants his sword to be sheathed in fire. Normally that would be insane. For you, though, that requires surprisingly little effort. You can apply an augment you know to a weapon you or an adjacent ally are wielding for just 1 action point. If the augment takes up multiple augment slots, it costs that many action points to attach (so an augment that would take up 2 augment slots would cost 2 action points to Crafting F | [ACTION] [GEAR] |
| **Weapon Support** |  | Acc +1, Aug +1, HP +6 | Stance |  | stanCe (costs 1 AP to enter)<br>You provide support repairs and guidance to adjacent allies on the battlefield, tweaking their weapons as they mow down opponents. Any ally using a weapon that you either created or augmented gains a bonus to their accuracy as long as they are adjacent to you while in your Weapon Support stance. The bonus is +1 plus an additional +1 per 4 skill points you have in Armsmith (so +2 at<br>4 skill points, +3 at 8 skill points, and so forth). If you have the Rapid Replacement specialty, an adjacent ally’s weapon cannot be broken so long as you remain adjacent to them and in the Weapon Support stance.<br>irear ms<br>&<br>numBer oF Firearms you Can maintain<br>Without needing to buy pieces or parts, you can build some fire- arms entirely out of scraps. These firearms must be constantly maintained by you and stop working soon after leaving your care. You can build and maintain a number of firearms based on your DIY score. You can build new firearms or augment old ones during any period of downtime you have.<br>your Diy: 1 2 3 4 5 6<br>you Can BuiLD: 2 2 3 3 3 4<br>your Diy: 7 8 9 10 11 12<br>you Can BuiLD: 4 4 5 5 5 6<br>the Cost oF Firearms<br>If you need to build a firearm that you can’t build for free from your DIY score, you will need to buy the materials for it. A firearm will have a base materials cost. It is 1/5th the market price.<br>Every augment will increase the price. The higher the marque, the greater the price. The market price for an augment can be found in the chart below.<br>marQue I II III IV<br>market priCe 25 princes 125 princes 625 princes 3,125 princes If you are building the augment,<br>you pay 1/5th the price, which is<br>the same as if you were buying an Firearms<br>a th u e g m m e a n te t r o ia n l e c m os a t r q fo u r e a l o M we a r r . q ( u A e s I i I n I , Light Firearm 2 princes augment is the market price fo a Medium Firearm 5 princes Marque II augment.) The material Heavy Firearm 12 princes c p o ri s n t c f e o s r . a Marque 1 augment is 5 Super-Heavy Firearm 20 princes | [STANCE] [SCALE:Armsmith] ally Acc = 1 + floor(Arm/4) |
| **Gunsmith** | Crafting Firearms & Crossbows | Aug +2, DIY +1, HP +4 | Passive (crafting) |  | You can now create new firearms and upgrade them. These firearms can be of any size, type, or material. You can craft any firearm from the light peashooters to the super-heavy rifles. Without spending any money, you can build and maintain several firearms based on your current Do-It-Yourself (DIY) score. These firearms can then be upgraded with augments. You’ll learn 2 augments from this specialty, which can be selected under “firearm & crossbow augments” below. These augments have marques. At lower levels, you’ll start with Marque I augments. As your skill in Armsmith improves, your marques will increase. See the “Crafting” page at the beginning of this chapter for more information.<br>Each firearm can be upgraded with 3 augments. Sometimes an augment will take up multiple augment slots. For example, the “damaging” augment is worth 2 slots, so a firearm only has 1 more available slot for an augment after “damaging” has been applied.<br>attach). The temporary attachment doesn’t last long: it will stop functioning at the beginning of end of your next turn (when your action points refresh).<br>The weapon you are attaching the temporary augment to does not need to have free augment slots: this is a bonus augment that does not fit into a weapon’s normal maximum number of augments. | [AUG] [DIY] [CRAFT:firearm] |
| **Beta Firearms** | Crafting Firearms & Crossbows | Aug +2, DIY +1, HP +4 | Passive | 4 Armsmith; Gunsmith | reQuires: 4 skill points in Armsmith & Gunsmith specialty Your firearms are overly complex, but they can accomplish quite a bit. Such firearms have two more slots for you to place augments into.<br>If anybody other than you attempts to use one of your beta firearms, they must succeed in rolling a science result one tier higher than the highest level marque you have on your firearm. If your firearm has a Marque IV augment, it is impossible for them to use it (unless they can somehow obtain a tier result of 5 with their science attribute). | [CRAFT] [REQ] |
| **Prototype Firearms** | Crafting Firearms & Crossbows | Aug +1, DIY +1, HP +6 | Passive | 16 Armsmith; Gunsmith; Beta Firearms | reQuires: 16 skill points in Armsmith, Gunsmith, & Beta Firearms You’ve perfected your beta firearms and made them user-friendly. Now anybody can use a firearm that you designate as being a prototype.<br>Aug HP +2 +4 | [CRAFT] [REQ] |
| **Crossbow Craftsman** | Crafting Firearms & Crossbows | Aug +2, DIY +1, HP +4 | Passive (crafting) |  | You can now create new crossbows and upgrade them. These crossbows can be of any size, type, or material. You can craft any crossbow from the light hand-crossbow to the super-heavy ballistas.<br>Without spending any money, you can build and maintain several crossbows based on your current Do-It-Yourself (DIY) score. These crossbows can then be upgraded with augments. You’ll learn 2 augments from this specialty, which can be selected under “firearm & crossbow augments” below. These augments have marques. At lower levels, you’ll start with Marque I augments. As your skill in Armsmith improves, your marques will increase. See the “Crafting” page at the beginning of this chapter for more information.<br>Each crossbow can be upgraded with 3 augments.<br>Sometimes an augment will take up multiple augment slots. For example, the “damaging” augment is worth 2 slots, so a crossbow only has 1 more available slot for an augment after “damaging” has been applied.<br>numBer oF CrossBows you Can maintain<br>Without needing to buy pieces or parts, you can build some crossbows entirely out of scraps. These crossbows must be constantly maintained by you and stop working soon after leaving your care. You can build and maintain a number of crossbows based on your DIY score. You can build new crossbows or augment old ones during any period of downtime you have.<br>your Diy: 1 2 3 4 5 6<br>you Can BuiLD: 3 3 4 4 4 5<br>your Diy: 7 8 9 10 11 12<br>you Can BuiLD: 5 5 6 6 6 7<br>the Cost oF CrossBows<br>If you need to build a crossbows<br>that you can’t build for free from Crossbows<br>your DIY score, you will need to<br>buy the materials for it. Light Crossbow 2 princes A crossbow will have a Medium Crossbow 4 princes base materials cost. It is 1/5th the Heavy Crossbow 7 princes market price. Super-Heavy Crossbow 14 princes<br>Every augment will in-<br>crease the price. The higher the marque, the greater the price. The market price for an augment can be found in the chart below.<br>marQue I II III IV<br>market priCe 25 princes 125 princes 625 princes 3,125 princes If you are building the augment, you pay 1/5th the price, which is the same as if you were buying an augment one marque lower. (As in, the material cost for a Marque III augment is the market price fo a Marque II augment.) The material cost for a Marque 1 augment is 5 princes. | [AUG] [DIY] [CRAFT:crossbow] |
| **Beta Crossbows** | Crafting Firearms & Crossbows | Aug +2, DIY +1, HP +4 | Passive | 4 Armsmith; Crossbow Craftsman | reQuires: 4 skill points in Armsmith & Crossbow Crafter specialty Your crossbows are overly complex, but they can accomplish quite a bit. Such crossbows have two more slots for you to place augments into.<br>If anybody other than you attempts to use one of your beta crossbows, they must succeed in rolling a science result one tier higher than the highest level marque you have on your crossbow. If your crossbow has a Marque IV augment, it is impossible for them to use it (unless they can somehow obtain a tier result of 5 with their science attribute). | [CRAFT] [REQ] |
| **Prototype Crossbows** | Crafting Firearms & Crossbows | Aug +1, DIY +1, HP +6 | Passive | 16 Armsmith; Crossbow Craftsman; Beta Crossbows | reQuires: 16 skill points in Armsmith, Crossbow Crafter, & Beta Crossbows specialties<br>You’ve perfected your beta crossbows and made them userfriendly. Now anybody can use a crossbow that you designate as being a prototype. | [CRAFT] [REQ] |
| **Weapon Smith** | Crafting Melee Weapons & Throwing Weapons | Aug +2, DIY +1, HP +4 | Passive (crafting) |  | You can create new melee weapons and throwing weapons and upgrade them. These weapons can be of any size, type, or material. You can craft anything from a metal stiletto to a wooden pike to a sword made from bone.<br>Without spending any money, you can build and maintain several weapons based on your current Do-It-Yourself (DIY) score. These weapons can then be upgraded with augments. You’ll learn 2 augments from this specialty, which can be selected under “weapon augments” below. These augments have marques. At lower levels, you’ll start with Marque I augments. As your skill in Armsmith improves, your marques will increase. See the “Crafting” page at the beginning of this chapter for more information. Each weapon can be<br>upgraded with 3 augments. Weapons<br>Some materials can only be<br>upgraded twice (like wooden Light Melee Weapon 1 princes weapons) or just once (like Medium Melee Weapon 7 princes o au rg g a m n e ic n t o w n i e l s l ) t . ak S e o m up et i m m u e l s t ip a l n e Heavy Melee Weapon 15 princes augment slots. For example, One-Handed Polearm 5 princes the “damaging” augment is Two-Handed Polearm 12 princes w ha o s r t 1 h m 2 o s r lo e t a s v , a s i o l a a b w le e s a l p o o t n fo o r n a l n y Basic Non-Rigid Weapon 1 princes augment after “damaging” has Larger Non-Rigid Weapon 4 princes been applied.<br>numBer oF weapons you Can maintain<br>Without needing to buy pieces or parts, you can build some weapons entirely out of scraps. These weapons must be constantly maintained by you and stop working soon after leaving your care. You may build and maintain a number of weapons based on your DIY score. You may build new weapons or augment old ones during any period of downtime you have.<br>your Diy: 1 2 3 4 5 6<br>you Can BuiLD: 2 2 3 3 3 4<br>your Diy: 7 8 9 10 11 12<br>you Can BuiLD: 4 4 5 5 5 6<br>the Cost oF weapons<br>If you need to build a weapon that you can’t build for free from your DIY score, you will need to buy the materials for it. A weapon will have a base materials cost. It is 1/5th the market price.<br>Every augment will increase the price. The higher the & Throwing Weapons<br>marque, the greater the price. The market price for an augment can be found in the chart below.<br>marQue I II III IV<br>market priCe 25 princes 125 princes 625 princes 3,125 princes If you are building the augment, you pay 1/5th the price, which is the same as if you were buying an augment one marque lower. (As in, the material cost for a Marque III augment is the market price fo a Marque II augment.) The material cost for a Marque 1 augment is 5 princes. | [AUG] [DIY] [CRAFT:melee] |
| **Beta Weapons** | Crafting Melee Weapons & Throwing Weapons | Aug +2, DIY +1, HP +4 | Passive | 4 Armsmith; Weapon Smith | reQuires: 4 skill points in Armsmith & Weaponsmith specialty Your weapons are overly complex, but they can accomplish quite a bit. Such weapons can be upgraded with 2 more augments (bringing the total for metal melee weapons up to 5 augmentable slots).<br>If anybody other than you attempts to use one of your beta weapons, they must succeed in rolling a sciences result one tier higher than the highest marque you have on your weapon. If your weapon has a Marque IV augment, it is impossible for them to use it (unless they can somehow obtain a tier result of 5 with their sciences attribute). | [CRAFT] [REQ] |
| **Prototype Weapons** | Crafting Melee Weapons & Throwing Weapons | Aug +1, DIY +1, HP +5 | Passive | 16 Armsmith; Weapon Smith; Beta Weapons | reQuires: 16 skill points in Armsmith, Weapon Smith, & Beta Weapons specialties<br>You’ve perfected your beta weapons and made them user-friendly. Now anybody can use a weapon that you designate as being a prototype. | [CRAFT] [REQ] |
| **Interchangeable Parts** | Crafting Melee Weapons & Throwing Weapons | Pri +2, Aug +1, HP +5 | 3 AP to swap (melee version, p.182) | Weapon Smith | reQuires: Weapon Smith specialty<br>Cost: 3 AP<br>Your weapons are designed so that their parts can be replaced and altered in the middle of battle. This gives the weapons additional slots for augments, but these augments are not always active. At any time, a person may switch out the augments for 3 action points, activating one augment but deactivating another augment. You may replace multiple augments at the same time all for the cost of 3 action points.<br>This specialty works within the marque system. The amount of interchangeable slots the weapon has depends on the marque of its creator.<br>1 interchangeable slot for an augment<br>2 interchangeable slots for augments<br>3 interchangeable slots for augments<br>4 interchangeable slots for augments | [CRAFT] [REQ] |
| **Bowyer** | Crafting Bows | Aug +2, DIY +1, HP +4 | Passive (crafting) |  | You can now create new bows of any size and upgrade them. Without spending any money, you can build and maintain several bows based on your current Do-It-Yourself (DIY) score. These bows can then be upgraded with augments. You’ll learn 2 augments from this specialty, which can be selected under “bow augments” below. These augments have marques. At lower levels, you’ll start with Marque I augments. As your skill in Armsmith improves, your marques will increase. See the “Crafting” page at the beginning of this chapter for more information. Each bow can be upgraded with 3 augments. Some materials can only be upgraded twice (like wooden bows) or just once (like organic ones). Sometimes an augment will take up multiple augment slots. For example, the “damaging” augment is worth 2 slots, so a metal bow only has 1 more available slot for an augment after “damaging” has been applied.<br>numBer oF Bows you Can maintain<br>Without needing to buy pieces or parts, you can carve some bows entirely out of scraps. These bows must be constantly maintained by you and stop working soon after leaving your care. You may build and maintain a number of bows based on your DIY score. You may build new bows or augment old ones during any period of downtime you have.<br>your Diy: 1 2 3 4 5 6<br>you Can BuiLD: 2 2 3 3 3 4<br>your Diy: 7 8 9 10 11 12<br>you Can BuiLD: 4 4 5 5 5 6<br>the Cost oF Bows<br>If you need to build a bow that you can’t build for free from your DIY score, you will need to buy the materials for it. A bow will have a base mate-<br>rials cost. It is 1/5th the market price. Bows<br>Every augment will increase Light Bows 5 dukes<br>t g h r e e a p te ri r c t e h . e T p h r e ic h e. i g T h h e e r m th a e r k m e a t r p q r u ic e e , t f h o e r Medium Bows 1 prince an augment can be found in the chart Heavy Bows 5 princes below. Super-Heavy Bows 17 princes<br>marQue I II III IV<br>market priCe 25 princes 125 princes 625 princes 3,125 princes If you are building the augment, you pay 1/5th the price, which is the same as if you were buying an augment one marque lower. (As in, the material cost for a Marque III augment is the market price fo a Marque II augment.) The material cost for a Marque 1 augment is 5 princes. | [AUG] [DIY] [CRAFT:bow] |
| **Beta Bows** | Crafting Bows | Aug +2, DIY +1, HP +4 | Passive | 4 Armsmith; Bowyer | reQuires: 4 skill points in Armsmith & Bowyer specialty Your bows are surprisingly complex, but they can do a lot more than standard bows. Such bows can be upgraded with 2 more augments (bringing the total for metal bow up to 5 augmentable slots).<br>If anybody other than you attempts to use one of your beta bows, they must succeed in rolling a sciences result one tier higher than the highest marque you have on your bow. If your bow has a Marque IV augment, it is impossible for them to use it (unless they can somehow obtain a tier result of 5 with their sciences attribute). | [CRAFT] [REQ] |
| **Prototype Bows** | Crafting Bows | Aug +1, DIY +1, HP +4 | Passive | 16 Armsmith; Bowyer; Beta Bows | reQuires: 16 skill points in Armsmith, Bowyer, & Beta Bows spe- You’ve perfected your beta bows and made them user-friendly. Now anybody can use a bow that you designate as being a prototype. | [CRAFT] [REQ] |
| **Armor Smith** | Crafting Armor | Aug +2, DIY +1, HP +5 | Passive (crafting) |  | You can now create armor and upgrade it. You can upgrade any type of armor.<br>Without spending any money, you can build and maintain several suits of armor based on your current Do-It-Yourself (DIY) score. These armors can then be upgraded with augments. You’ll learn 2 augments from this specialty, which can be selected under “armor augments” below. These augments have marques. At lower levels, you’ll start with Marque I augments. As your skill in Armsmith improves, your marques will increase. See the “Crafting” page at the beginning of this chapter for more information. Each armor can be upgraded<br>with 3 augments. Some materials can Armor<br>only be upgraded twice (like wooden<br>armors) or just once (like organic ar- Minimal 1 princes mors). Sometimes an augment will take Light 5 princes u th p e m “d u a l m tip a l g e e a s u o g a m ki e n n g t ” s a lo u t g s. m F e o n r t e i x s a w m o p r l t e h , Medium 15 princes<br>2 slots, so a metal suit of armor only has Heavy 40 princes<br>1 more available slot for an augment after Super-Heavy 75 princes “damage soaking” has been applied.<br>numBer oF armors you Can maintain<br>Without needing to buy pieces or parts, you can build some armor entirely out of scraps. These armors must be constantly maintained by you and stop working soon after leaving your care. You may build and maintain a number of armors based on your DIY score. You may build new armors or augment old ones during any period of downtime you have.<br>your Diy: 1 2 3 4 5 6<br>you Can BuiLD: 1 1 1 2 2 2<br>your Diy: 7 8 9 10 11 12<br>you Can BuiLD: 2 3 3 3 3 4<br>the Cost oF armors<br>If you need to build a suit of armor that you can’t build for free from your DIY score, you will need to buy the materials for it. Armor will have a base materials cost. It is 1/5th the market price.<br>Every augment will increase the price. The higher the marque, the greater the price. The market price for an augment can be found in the chart below.<br>marQue I II III IV<br>market priCe 20 princes 100 princes 500 princes 2500 princes If you are building the augment, you pay 1/5th the price, which is the same as if you were buying an augment one marque lower. r mor<br>(As in, the material cost for a Marque III augment is the market price fo a Marque II augment.) The material cost for a Marque 1 augment is 4 princes. | [AUG] [DIY] [CRAFT:armor] |
| **Beta Armor** | Crafting Armor | Aug +2, DIY +1, HP +5 | Passive | 4 Armsmith; Armor Smith | reQuires: 4 skill points in Armsmith & Armor Smith specialty Your armor comes with a lot of weird straps and oddly placed component, but their efficiency is unbreakable. Such armors have two more slots for you to place augments into.<br>If anybody other than you attempts to use one of your beta armors, they must succeed in rolling a science result one tier higher than the highest level marque you have on your armor. If your armor has a Marque IV augment, it is impossible for them to use it (unless they can somehow obtain a tier result of 5 with their science attribute). | [CRAFT] [REQ] |
| **Prototype Armor** | Crafting Armor | Aug +1, DIY +1, HP +6 | Passive | 16 Armsmith; Armor Smith; Beta Armor | reQuires: 16 skill points in Armsmith, Armor Smith, & Beta Armor specialty<br>You’ve perfected your beta armor and made them user-friendly. Now, any of your beta armors that you designate as being prototypes, anybody can use. | [CRAFT] [REQ] |

##### Armsmith – crafting tables (p.177–195)

**DIY → items maintained for free**

| DIY | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Firearms | 2 | 2 | 3 | 3 | 3 | 4 | 4 | 4 | 5 | 5 | 5 | 6 |
| Crossbows | 3 | 3 | 4 | 4 | 4 | 5 | 5 | 5 | 6 | 6 | 6 | 7 |
| Melee/throwing weapons | 2 | 2 | 3 | 3 | 3 | 4 | 4 | 4 | 5 | 5 | 5 | 6 |
| Bows | 2 | 2 | 3 | 3 | 3 | 4 | 4 | 4 | 5 | 5 | 5 | 6 |
| Armor | 1 | 1 | 1 | 2 | 2 | 2 | 2 | 3 | 3 | 3 | 3 | 4 |

**Augment market price** (self-built = price of one marque lower; base item material cost = 1/5 market price)

| Type | mQ I | mQ II | mQ III | mQ IV | mQ I material |
|---|---|---|---|---|---|
| Firearm / crossbow / melee / bow augment | 25 pr | 125 pr | 625 pr | 3,125 pr | 5 pr |
| Armor augment | 20 pr | 100 pr | 500 pr | 2,500 pr | 4 pr |
| Accessory: Chained Grip | 10 pr | 50 pr | 250 pr | 1,250 pr | – |
| Accessory: Alchemic Tube | 15 pr | 75 pr | 375 pr | 1,875 pr | – |

Base item prices (Weapon Smith list): light melee 1 pr, medium 7, heavy 15, one-handed polearm 5, two-handed polearm 12, basic non-rigid 1, larger non-rigid 4. Slots by material: metal 3, wood 2, organic 1 (+2 for beta).

##### Firearm & crossbow augments (p.179–181) — F = firearm only, C = crossbow only

| Augment | Slots | mQ I | mQ II | mQ III | mQ IV | Notes |
|---|---|---|---|---|---|---|
| Accurate | 1 | +1 Acc | +2 | +3 | +4 | `[STAT]` |
| Automatic Reload | 1 | −1 AP reload | −1 | −2 | −2 | `[GEAR]` |
| Bipod | 1 | +1 Acc | +2 | +3 | +4 | set up 2 AP, pack 1 AP `[COND]` |
| Collapsible | 1 | 1 size smaller (concealment) | 2 | 3 | 4 | 3 AP to break down / reassemble |
| Crank-Free (F; req. Rotating Barrels) | 1 | removes extra hand requirement | – | – | – | always priced mQ II |
| Custom | 1 | others −3 Acc & Stk | −6 | −9 | −12 | owner designated at crafting |
| Damaging | 2 | +1 DC | +2 | +3 | +4 | `[STAT]` |
| Deflecting | 1 | use as shield: deflect +4 Eva for 1 reflexive AP | – | – | – | always priced mQ II |
| Delivery (C) | 1 | range −75 ft when delivering | −50 | −25 | none | shoot potions/explosives/items |
| Easily Altered (req. Interchangeable Parts) | 1 | swap parts 2 AP | 2 AP | 1 AP | 1 AP | permanent |
| Gnome-Sized (light only) | 1 | gnome can conceal | – | – | – | always mQ I |
| Horrifying | 2 | enemies T2 Spirit or T1 fear | T3 | T4 | irresistible | once per person per combat |
| Location Seeking | 1 | other called-shot locations −8 Acc | −6 | −4 | −2 | chosen location's called shots cost no extra AP |
| Luminous | 1 | light 25 ft | 50 | 100 | 200 | 1 AP toggle |
| Reinforced | 1 | +1 size category vs sunder | +2 | +3 | +4 | stackable |
| Rotating Barrels (F) | 1 | −5 Acc | −3 | −1 | 0 | no reload time; +1 hand (two-handed → firing position); ammo weapons with reload ≤2 AP |
| Scope | 1 | +50 ft range | +100 | +200 | +300 | stackable |
| Signature Weapon (req. Custom) | 2 | owner regains 1 HP at refresh | 2 | 3 | 4 | |
| Silent | 1 | locate by sound needs Cunning T2 | T3 | T4 | impossible | |
| Small Choke | 1 | doubles shot range; other ammo −3 Acc | – | – | – | always mQ I |
| *Accessory:* Chained Grip | 0 | +2 resist disarm | +4 | +6 | +8 | own price table |

**Book texts:**

**Accurate** — *Firearm & Crossbow Augment*  
> Fine attention has been placed on the quality of your weapon. The user gains a bonus to accuracy with the weapon.  
> +1  
> +2  
> +3  
> +4  

**Automatic Reload** — *Firearm & Crossbow Augment*  
> The crossbow or firearm has a fast reloading mechanism, allowing it to be reloaded much more quickly than normal.  
> 1 less AP to reload  
> 1 less AP to reload  
> 2 less AP to reload  
> 2 less AP to reload  

**Bipod** — *Firearm & Crossbow Augment*  
> You can set up a bipod to level your weapon on. Setting up the bipod requires 2 action points, and then pulling it back up so that you can move again requires 1 action point. While the bipod is set up, however, you gain a bonus on your accuracy.  
> +1  
> +2  
> +3  
> +4  

**Collapsible** — *Firearm & Crossbow Augment*  
> Sometimes discretion is the better part of not having your weaponry confiscated, so you create a clever collapsing mechanism for your weapons which makes them easier to conceal. Any weapon this is applied to can be broken down for 3 acion points and re-assembled for 3 action points. It is treated, for purposes of concealment, as being smaller than it is, but only when broken down.  
> 1 category smaller  
> 2 categories smaller  
> 3 categories smaller  
> 4 categories smaller  

**Crank-Free** — *Firearm Augment*  
> reQuires: Augmented with Rotating Barrels  
> Converting your firearm to be truly automatic, the crank-free firearm no longer increases the need of hands - a one-handed firearm is still one-handed, and a two-handed firearm is still just two-handed.  
> Note: This augment always acts as marque II for the purposes of determining cost, though you can learn this augment despite your skill in armsmith.  

**Custom** — *Firearm & Crossbow Augment*  
> This weapon was designed to be used by one person and one person only. That person must be designated at the time of the weapon’s crafting. If anybody else attempts to use the custom weapon, they suffer a penalty on all accuracy and strike rolls with it.  
> -3  
> -6  
> -9  
> -12  

**Damaging** — *Firearm & Crossbow Augment*  
> takes up 2 augment sLots on a Firearm or CrossBow Your weapon is larger but lighter, dealing extra damage with each shot.  
> +1 damage class  
> +2 damage class  
> +3 damage class  
> +4 damage class  

**Deflecting** — *Firearm & Crossbow Augment*  
> You can use this weapon like a shield, allowing you to deflect incoming attacks (gaining a +4 to evade in exchange for 1 reflexive action point).  
> Note: This augment always acts as marque II for the purposes of determining cost, though you can learn this augment despite your skill in armsmith.  

**Delivery** — *Crossbow Augment*  
> You can launch an alchemic potion, explosives, or other items through your firearm. If the item shot is friendly (as in, you’re not trying to hit the target), you may shoot the item next to them, and they may pick it up for 1 action point. Regardless, a delivery weapon’s range is cut be a small portion whenever it is being used to deliver an item.  
> -75 feet  
> -50 feet  
> -25 feet  
> no penalty  

**Easily Altered** — *Firearm & Crossbow Augment*  
> reQuires: Weapon to be made with Interchangeable Parts The weapon is easily altered, allowing its interchangeable parts to be used and switched around much more quickly than normal. The easily altered augment is a permanent affixture of the weapon, however, and cannot be activated or deactivated with interchangeable parts.  
> 2 AP to interchange parts  
> 2 AP to interchange parts  
> 1 AP to interchange parts  
> 1 AP to interchange parts  

**Gnome-Sized** — *Firearm & Crossbow Augment*  
> reQuires: placed on light weapon  
> You’ve been able to shrink the weapon down so that a gnome will be able to conceal it.  
> Note: This augment always acts as marque I for the purposes of determining cost, though you can learn this augment despite your skill in armsmith.  

**Horrifying** — *Firearm & Crossbow Augment*  
> takes up 2 augment sLots on a Firearm or CrossBow The weapon is so twisted and wicked looking that it could strike fear into the heart of even the bravest of warriors. When first seeing the weapon, all enemies must make a spirit resist or suffer from tier 1 fear. At any time a character can spend an action point to attempt another resist roll. A single person can only evoke the effect of one horrifying weapon per combat.  
> Tier 2 spirit result to resist  
> Tier 3 spirit result to resist  
> Tier 4 spirit result to resist  
> Irresistable (unless they can get a Tier 5 spirit resist)  

**Location Seeking** — *Firearm & Crossbow Augment*  
> When crafting this weapon designate a called shot. The weapon seems to guide itself toward that specific called on your victim’s body with the greatest of ease. Called shots to the designated location do not require an additional action point when made with this weapon. However, attacking any other called shot location with this weapon can be problematic, as it was built with one cause in mind. (This penalty does not apply to normal, unspecified attacks.)  
> -8 on accuracy rolls when attacking a different called shot location  
> -6 on accuracy rolls when attacking a different called shot location  
> -4 on accuracy rolls when attacking a different called shot location  
> -2 on accuracy rolls when attacking a different called shot location  
> Note: When crafting the augment, the word “location” should be replaced with the specified called shot, such as “eye seeking” or “torso seeking.”  

**Luminous** — *Firearm & Crossbow Augment*  
> Your weapon glows. Perhaps you strung lights along its barrel, gave it a glow-in-the-dark coating, or made your weapon transparent with a light set inside. The light extends outwards from your weapon a number of feet determined by the marque of this augment. For 1 action point, you may turn it on, off, or dim it.  
> 25 feet  
> 50 feet  
> 100 feet  
> 200 feet  

**Reinforced** — *Firearm & Crossbow Augment*  
> You build your weapon solidly, giving it little room to break on the battlefield. When somebody attempts to sunder the reinforced weapon, it acts as if it is several size categories larger than it is. Once these “reinforced” size categories are gone, then its actual damage begins to decrease.  
> This augment can be applied multiple times, its effect stacking.  
> 1 reinforced size category  
> 2 reinforced size categories  
> 3 reinforced size categories  
> 4 reinforced size categories  

**Rotating Barrels** — *Firearm Augment*  
> Creating what comes close to being a fully automatic weapon, a firearm with multiple rotating barrels uses a crank to fire. Using rotating barrels increases the need of hands - a one-handed firearm now requires two hands, and a two-handed firearm now requires you to be in a “firing position.” A rotating multi-barrel firearm eliminates the reload time of the firearm, but at a price to accuracy.  
> This augment can only be placed on firearms that use ammunition and have a reload time of 2 action points or less.  
> -5 accuracy  
> -3 accuracy  
> -1 accuracy  
> No accuracy penalty  

**Scope** — *Firearm & Crossbow Augment*  
> The range on your firearm increases greatly. This augment can be applied multiple times, with its increases stacking.  
> +50 feet  
> +100 feet  
> +200 feet  
> +300 feet  

**Signature Weapon** — *Firearm & Crossbow Augment*  
> takes up 2 augment sLots on a Firearm or CrossBow reQuires: placed on weapon with Custom augment  
> Be it a family heirloom or just your perfectly customized weapon, the very sight of it invigorate you. As long as your weapon is in hand there is still hope. You recover a small amount of hit points when your action points refresh. This augment only affects the person this weapon was customized for.  
> recover 1 hit point  
> recover 2 hit points  
> recover 3 hit points  
> recover 4 hit points  

**Silent** — *Firearm & Crossbow Augment*  
> This weapon is whispering death. It makes almost no sound when shot or reloaded, making it almost impossible for people to figure out where it is by sound alone. Any time anybody is attempting to figure out where the weapon was shot from based on sound must make a tier result with their cunning.  
> Tier 2  
> Tier 3  
> Tier 4  
> Impossible (or Tier 5)  

**Small Choke** — *Firearm & Crossbow Augment*  
> Introducing a small choke to a shotgun increases the effective distance of its shot. A small choke doubles the range of the shot fired from it. Other choices of ammunition fired from a small choke suffer a -3 accuracy.  
> Note: This augment always acts as marque I for the purposes of determining cost, though you can learn this augment despite your skill in armsmith.  
> Firearm & Crossbow Accessories  
> You can learn weapon accessories just like augments. However, firearm & crossbow accessories do not take up any augment slots and can only be applied to a weapon once. Each accessory has its own cost associated with it.  

**Chained-Grip** — *Firearm & Crossbow Accessory*  
> The user keeps a chain attached to both their wrist and the weapon, making it difficult - if not impossible - to be disarmed. Whenever the target of a disarm (called shot to the hand), the user gains a bonus to the resist roll.  
> +2 to resist being disarmed  
> +4 to resist being disarmed  
> +6 to resist being disarmed  
> +8 to resist being disarmed  
> marQue I II III IV  
> market priCe 10 princes 50 princes 250 princes 1,250 princes Weapon  


##### Melee & throwing weapon augments (p.183–188)

| Augment | Slots | mQ I | mQ II | mQ III | mQ IV | Notes |
|---|---|---|---|---|---|---|
| Accurate | 1 | +1 Acc | +2 | +3 | +4 | `[STAT]` |
| Aerodynamic | 1 | melee weapon becomes throwable | – | – | – | always mQ I |
| Bone-Shattering | 1 | +1 Stk on all called shots | +3 | +5 | +7 | `[COND]` |
| Chainsaw (melee) | 1 | +1 unsoakable per extra AP after damaging hit | +2 | +3 | +4 | repeatable with remaining AP |
| Collapsible | 1 | 1 size smaller | 2 | 3 | 4 | 3 AP each way |
| Cryothermal | 1 | −2 Stk until your next turn | −4 | −6 | −8 | 1 AP reflexive; Brute resist lowers marque |
| Custom | 1 | others −3 Acc & Stk | −6 | −9 | −12 | |
| Pyrothermal | 1 | T1 burns (−1 Def) | T2 (−3) | T3 (−5) | T4 (−7) | 1 AP reflexive; Brute resist |
| Combustion | 3 | T1 fire | T2 | T2 | T3 | 1 AP reflexive on hit; Dex resist |
| Burn Trail (req. Combustion) | 1 | helpers must Dex-resist = marque or catch fire | – | – | – | always mQ III |
| Everburning (req. Combustion) | 1 | +1 AP to extinguish | +2 | +3 | +4 | |
| Damaging | 2 | +1 DC | +2 | +3 | +4 | `[STAT]` |
| Deflecting | 1 | deflect +4 Eva (1 reflexive AP) | – | – | – | always mQ I (note: II for firearms) |
| Easily Altered | 1 | swap 2 AP | 2 | 1 | 1 | req. Interchangeable Parts |
| Electrical | 1 | +1 unsoakable on hit | +2 | +3 | +4 | ×2 vs metal armor or in water (×4 both) |
| Electrical Archs (req. Electrical) | 1 | jumps 1× (10 ft, Acc vs Eva) | 2× | 3× | 4× | stops on miss |
| Long Archs (req. Electrical Archs) | 1 | arch range 25 ft | 50 | 75 | 100 | |
| Gas Leaks | 1 | holds 1 gas dose | 2 | 3 | 4 | 1 AP per dose released on hit; refill 3 AP |
| Gnome-Sized (light) | 1 | gnome-concealable | – | – | – | always mQ I |
| Horrifying | 2 | T2 Spirit to resist T1 fear | T3 | T4 | irresistible | |
| Inspiring | 2 | allies seeing it regain 1 HP at your refresh | 2 | 2 | 3 | no stacking |
| Jackhammer | 2 | +2 DC vs automatons/vehicles/clockworks/structures | +4 | +6 | +8 | `[COND]` |
| Lightning Pulsing | 2 | −8 Acc while on | −6 | −4 | −2 | attacks unsoakable vs wet/metal-armored; 1 AP toggle |
| Location Seeking | 1 | −8 Acc on other locations | −6 | −4 | −2 | |
| Luminous | 1 | 25 ft | 50 | 100 | 200 | |
| Powerful | 1 | +2 Stk | +4 | +6 | +8 | `[STAT]` |
| Propelled (throwing) | 1 | +20 ft range | +30 | +40 | +60 | |
| Reach | 1 | +5 ft reach | +5 | +10 | +10 | `[GEAR]` |
| Reinforced | 1 | +1 size vs sunder | +2 | +3 | +4 | |
| Returning (throwing) | 1 | −30 ft range | −20 | −10 | none | returns to you |
| Signature Weapon (req. Custom) | 2 | owner +1 HP per refresh | 2 | 3 | 4 | |
| Skullsmasher | 1 | +2 Stk on head/eye called shots | +4 | +6 | +8 | |
| Specialized (req. Custom) | 1 | non-owner takes 2 unsoakable per use | 4 | 6 | 8 | |
| Static | 1 | −1 Eva until your next turn | −2 | −3 | −4 | 1 AP reflexive; Brute resist |
| Streamlined (light/medium) | 3 | attacks cost 1 AP, −3 DC | −2 DC | −1 DC | no penalty | `[GEAR]` |
| Tangling (flexible) | 1 | +2 on rolls to keep grab | +4 | +6 | +8 | |
| *Accessory:* Alchemic Tube | 0 | reload 3 AP | 2 AP | 1 AP | 1 AP reflexive | holds 1 poison/substance |
| *Accessory:* Chained Grip | 0 | +2 resist disarm | +4 | +6 | +8 | |

**Book texts:**

**Accurate** — *Weapon Augment*  
> Fine attention has been placed on the quality of your weapon. The user gains a bonus to accuracy with the weapon.  
> +1  
> +2  
> +3  
> +4  

**Aerodynamic** — *Weapon Augment*  
> You can make your melee weapons into perfectly good throwing weapons. If you apply this augment onto one of your melee weapons, you may throw it like a weapon designed for throwing. Note: This augment always acts as marque I for the purposes of determining cost, though you can learn this augment despite your skill in armsmith.  

**Bone-Shattering** — *Weapon Augment*  
> By increasing the weapon’s density, the weapon allows its wielder to make more effective called shots against his victims.  
> +1 strike against all called shot locations  
> +3 strike against all called shot locations  
> +5 strike against all called shot locations  
> +7 strike against all called shot locations  

**Chainsaw** — *Weapon Augment*  
> reQuires: placed on a melee weapon  
> Cost: 1 AP (after a successful attack)  
> Your weapon has a deadly, barbed spinning edge. If you make a successful attack with a chainsaw weapon that deals damage, you may spend 1 action point (as many times as you have AP left in your turn) to deal additional unsoakable damage as the chainsaw continues to rip into the person.  
> 1 extra damage  
> 2 extra damage  
> 3 extra damage  
> 4 extra damage  

**Collapsible** — *Weapon Augment*  
> Sometimes discretion is the better part of not having your weaponry confiscated, so you create a clever collapsing mechanism for your weapons which makes them easier to conceal. Any weapon this is applied to can be broken down for 3 acion points and re-assembled for 3 action points. It is treated, for purposes of concealment, as being smaller than it is, but only when broken down.  
> 1 category smaller  
> 2 categories smaller  
> 3 categories smaller  
> 4 categories smaller  

**Cryothermal** — *Weapon Augment*  
> resist: Brute (marques down)  
> Cost: 1 AP reflexively during an attack  
> Your weapon leaks a subzero liquid that freezes the opponent upon contact. When you make an attack with a cryothermal weapon, you may spend 1 action point to make the target frosty. Unless your victim can resist the entire effect, they become chilled, making them shiver when they attack.  
> Victim suffers a -2 on strike rolls until your next turn Victim suffers a -4 on strike rolls until your next turn Victim suffers a -6 on strike rolls until your next turn Victim suffers a -8 on strike rolls until your next turn  

**Custom** — *Weapon Augment*  
> This weapon was designed to be used by one person and one person only. That person must be designated at the time of the weapon’s crafting. If anybody else attempts to use the custom weapon, they suffer a penalty on all accuracy and strike rolls with it.  
> -3  
> -6  
> -9  
> -12  

**Pyrothermal** — *Weapon Augment*  
> resist: Brute (marques down)  
> Cost to aCtivate: 1 AP reflexively during an attack Your weapon heats up, burning the target. When you attack, you may spend 1 action point to make it pyrothermal. If it hits, the attack burns its target should they fail to resist against your melee attack. These burns last until the victim’s next breather, when they can be treated.  
> Victim suffers Tier 1 burns (-1 on defense rolls) Victim suffers Tier 2 burns (-3 on defense rolls) Victim suffers Tier 3 burns (-5 on defense rolls) Victim suffers Tier 4 burns (-7 on defense rolls)  

**Combustion** — *Weapon Augment*  
> takes up 3 augment sLots on a weapon  
> resist: Dexterity (marques down)  
> Cost to aCtivate: 1 AP reflexively during an attack Fire lashes out around your weapon, catching those struck with it on fire. When you hit an opponent, you can spend 1 action point in order to attempt to catch them on fire. The target may resist with their dexterity (lowering the marques of the combustion).  
> The victim catches on Tier 1 fire  
> The victim catches on Tier 2 fire  
> The victim catches on Tier 2 fire  
> The victim catches on Tier 3 fire  

**Burn Trail** — *Weapon Augment*  
> reQuires: placed on weapon with the Combustion augment Any person attempting to physically aid a victim of your combustion must first make a dexterity resist that equals the marque of your Combusion augment or be set on fire themselves.  
> Note: This augment always acts as marque III for the purposes of determining cost, though you can learn this augment despite your skill in armsmith.  

**Everburning** — *Weapon Augment*  
> reQuires: placed on weapon with the Combustion augment Despite your victim’s best efforts to put themselves out, they seem to continue burning. When catching things on fire through the use of a combustion attack, extra action points are required to put out the fire.  
> 1 extra AP  
> 2 extra AP  
> 3 extra AP  
> 4 extra AP  

**Damaging** — *Weapon Augment*  
> takes up 2 augment sLots on a weapon  
> Your weapon is larger but lighter, dealing extra damage with each blow.  
> +1 damage class  
> +2 damage class  
> +3 damage class  
> +4 damage class  

**Deflecting** — *Weapon Augment*  
> You may use this weapon like a shield, allowing you to deflect incoming attacks (gaining a +4 to evade in exchange for 1 reflexive action point).  
> Note: This augment always acts as marque I for the purposes of determining cost, though you can learn this augment despite your skill in armsmith.  

**Easily Altered** — *Weapon Augment*  
> reQuires: weapon to be made with Interchangeable Parts The weapon is easily altered, allowing its interchangeable parts to be used and switched around much more quickly than normal. The easily altered augment is a permanent affixture of the weapon, however, and cannot be activated or deactivated with interchangeable parts.  
> 2 AP to interchange parts  
> 2 AP to interchange parts  
> 1 AP to interchange parts  
> 1 AP to interchange parts  

**Electrical** — *Weapon Augment*  
> A small metal coil runs down the length of your weapon, leading to a power source that electrifies it. After landing a hit, your victim is shocked for a small amount of unsoakable damage. If the opponent is in metal armor or submersed in water, they take twice the damage. (If they are both in water and metal armor, they take four times the damage.)  
> 1 unsoakable electrical damage  
> 2 unsoakable electrical damage  
> 3 unsoakable electrical damage  
> 4 unsoakable electrical damage  

**Electrical Archs** — *Weapon Augment*  
> reQuires: placed on weapon with the Electrical augment The electricity that runs down your blade now jumps about, hitting multiple victims. Once you’ve hit an opponent, the electricity will arch to another opponent within 10 feet. Roll your accuracy versus their evade. If you meet or exceed it, the second opponent will be hit by the arch (dealing the normal damage for your electricity). The electricity will arch a number of times based on the marque of the augment. If, at any point, you miss a target, the electricity will not continue to jump.  
> Electricity jumps once  
> Electricity jumps twice  
> Electricity jumps thrice  
> Electricity jumps quatrice  

**Gas Leaks** — *Weapon Augment*  
> Cost to aCtivate: 1 AP reflexively during an attack Your weapon is hollow and covered in pores. You can fill your weapon with deadly gases that you release when you hit your opponent. You may choose to release multiple gases at the same time, but each one costs 1 action point. The augment’s marque determines how many gases it can hold. It costs 3 action points to add refill a single canister of gas.  
> Holds up to 1 dose  
> Holds up to 2 doses  
> Holds up to 3 doses  
> Holds up to 4 doses  
> Note: Unless you have doses of alchemical gas loaded into the weapon, this augment grants no bonuses. See Alchemy for the crafting of gases.  

**Gnome-Sized** — *Weapon Augment*  
> Requires: placed on light weapon  
> You’ve been able to shrink the weapon down so that a gnome will be able to conceal it.  
> Note: This augment always acts as marque I for the purposes of determining cost, though you can learn this augment despite your skill in armsmith.  

**Horrifying** — *Weapon Augment*  
> takes up 2 augment sLots on a weapon  
> The weapon is so twisted and wicked looking that it could strike fear into the heart of even the bravest of warriors. When first seeing the weapon, all enemies must make a spirit resist or suffer from tier 1 fear. At anytime, a character may spend an action point to attempt another resist roll. A single person can only evoke the effect of one horrifying weapon per combat.  
> Tier 2 spirit result to resist  
> Tier 3 spirit result to resist  
> Tier 4 spirit result to resist  
> Irresistable (unless they can get a Tier 5 spirit resist)  

**Inspiring** — *Weapon Augment*  
> takes up 2 augment sLots on a weapon  
> This weapon is symbolic to your allies, inspiring them to fight onwards when it’s in your hand. All allies that can see your weapon recover a small amount of hit points when you’re wielding it and your action points refresh. This does not stack with other inspiring weapons.  
> allies recover 1 hit point  
> allies recover 2 hit points  
> allies recover 2 hit points  
> allies recover 3 hit points  

**Jackhammer** — *Weapon Augment*  
> takes up 2 augment sLots on a weapon  
> A small, unbalanced sphere spins in the hilt of the weapon, causing it to vibrate wildly. This allows the weapon to deal tremendous damage to machines, vehicles with moving parts, and stationary structures.  
> +2 damage class against automatons, vehicles, clockworks, and structures  
> +4 damage class against automatons, vehicles, clockworks, and structures  
> +6 damage class against automatons, vehicles, clockworks, and structures  
> +8 damage class against automatons, vehicles, clockworks, and structures  

**Lightning Pulsing** — *Weapon Augment*  
> takes up 2 augment sLots on a weapon  
> Cost to aCtivate anD DeaCtivate: 1 AP  
> Your weapon pulses with lightning, just looking for a target to vaporize. Lightning is a powerful force that is hard to control. It causes the user to take a penalty on their accuracy roll, but the attack is unsoakable if the opponent is wet or in metal armor. The lightning pulse can be turned on or turned off for 1 action point. While it is on, the penalty is always in effect.  
> -8 on the accuracy roll  
> -6 on the accuracy roll  
> -4 on the accuracy roll  
> -2 on the accuracy roll  

**Location Seeking** — *Weapon Augment*  
> When crafting this weapon designate a called shot. The weapon seems to guide itself toward that specific called shot on your victim’s body with the greatest of ease. Called shots to the designated location do not require an additional action point when made with this weapon. However, attacking any other called shot location with this weapon can be problematic, as it was built with one cause in mind. (This penalty does not apply to normal, unspecified attacks.)  
> -8 on accuracy rolls when attacking a different called shot location  
> -6 on accuracy rolls when attacking a different called shot location  
> -4 on accuracy rolls when attacking a different called shot location  
> -2 on accuracy rolls when attacking a different called shot location  
> Note: When crafting the augment, the word “location” should be replaced with the specified called shot, such as “eye seeking” or “torso seeking.”  

**Long Archs** — *Weapon Augment*  
> reQuires: placed on a weapon with Electrical Archs augment Generally, electrical archs will jump from one target to another at a very small distance. The electricity will simply fizzle out if it goes too far. But with longer archs, your weapon’s electricity will take great leaps across the battlefield.  
> Can arch up to 25 feet  
> Can arch up to 50 feet  
> Can arch up to 75 feet  
> Can arch up to 100 feet  

**Luminous** — *Weapon Augment*  
> Your weapon glows. Perhaps you strung lights along its blade, gave it a glow-in-the-dark coating, or made your weapon transparent with a light set inside. The light extends outwards from your weapon a number of feet determined by the marque of this augment. For 1 action point, you may turn it on, off, or dim it.  
> 25 feet  
> 50 feet  
> 100 feet  
> 200 feet  

**Powerful** — *Weapon Augment*  
> Your weapon is stronger than others, be it due to a sharper blade, large striking side, or a heftier head. Regardless, it gives the user a bonus on their strike rolls.  
> +2 on strike  
> +4 on strike  
> +6 on strike  
> +8 on strike  

**Propelled** — *Weapon Augment*  
> reQuires: placed on throwing weapons  
> The weapon sails through the air, being easy to throw and going much further than its mundane counterparts. An easily thrown weapon has a farther range.  
> +20 feet  
> +30 feet  
> +40 feet  
> +60 feet  

**Reach** — *Weapon Augment*  
> You extend the weapon so that it can reach further.  
> 5 feet further  
> 5 feet further  
> 10 feet further  
> 10 feet further  

**Reinforced** — *Weapon Augment*  
> You build your weapon solidly, giving it little room to break on the battlefield. When somebody attempts to sunder the reinforced weapon, it acts as if it is several size categories larger than it is. Once these “reinforced” size categories are gone, then its actual damage begins to decrease.  
> 1 reinforced size category  
> 2 reinforced size categories  
> 3 reinforced size categories  
> 4 reinforced size categories  

**Returning** — *Weapon Augment*  
> reQuires: placed on throwing weapon  
> You can throw your weapon, and it will return to you. Due to this, the range you can throw it is decreased, but you will always have the weapon on hand.  
> -30 feet  
> -20 feet  
> -10 feet  
> no ranged penalty  

**Signature Weapon** — *Weapon Augment*  
> takes up 2 augment sLots on a weapon  
> reQuires: placed on weapon with Custom augment  
> Be it a family heirloom or just your perfectly customized weapon, the very sight of it invigorate you. As long as your weapon is in hand there is still hope. You recover a small amount of hit points when your action points refresh. This augment only affects the person this blade was customized for.  
> recover 1 hit point  
> recover 2 hit points  
> recover 3 hit points  
> recover 4 hit points  

**Skullsmasher** — *Weapon Augment*  
> This weapon has a specially weighted spike designed to cause severe brain trauma when striking against an opponent’s head or eyes.  
> +2 strike when making a called shot to the head or eyes  
> +4 strike when making a called shot to the head or eyes  
> +6 strike when making a called shot to the head or eyes  
> +8 strike when making a called shot to the head or eyes  

**Specialized** — *Weapon Augment*  
> reQuires: placed on weapon with Custom augment  
> Be it from pressurized spikes in its grip or an unearthly balance, when a person attempts to wield the weapon, it causes them harm. The person the weapon was customized for is immune to this effect.  
> The weapon causes its user 2 unsoakable damage with each use  
> The weapon causes its user 4 unsoakable damage with each use  
> The weapon causes its user 6 unsoakable damage with each use  
> The weapon causes its user 8 unsoakable damage with each use  

**Static** — *Weapon Augment*  
> resist: Brute (marques down)  
> Cost to aCtivate: 1 AP reflexively  
> You can make sparks fly off your weapon as you bring it in to decimate your foe. For 1 action point, you can make your attack full of static, causing the target to lose their ability to react as quickly. Meanwhile, their hair also stands on end. Victim suffers a -1 on evade rolls until your next turn Victim suffers a -2 on evade rolls until your next turn Victim suffers a -3 on evade rolls until your next turn Victim suffers a -4 on evade rolls until your next turn  

**Streamlined** — *Weapon Augment*  
> takes up 3 augment sLots on a weapon  
> reQuires: placed on light or medium weapon  
> Made of only the lightest and highest quality parts, this weapon has feels lighter then air. All attacks made with this weapon cost  
> 1 action point.  
> -3 damage class  
> -2 damage class  
> -1 damage class  
> no damage class penalty  

**Tangling** — *Weapon Augment*  
> reQuires: placed on flexible weapon  
> The whip is specially designed to make grabs against the opponent. Whenever used, the whip gains a bonus on all rolls to prevent the target from resisting the grab.  
> +2  
> +4  
> +6  
> +8  
> Weapon Accessories  
> You can learn weapon accessories just like augments. However, weapon accessories do not take up any augment slots and can only be applied to a weapon once. Each weapon accessory has its own cost associated with it.  

**Alchemic Tube** — *Weapon Accessory*  
> The weapon has a container attached to it and a rivet or channel that allows the weapon to strike with poison or another alchemical substance. The container can hold one usage of the substance. After its use, it takes some action points to snap a new alchemical substance into.  
> 3 AP  
> 2 AP  
> 1 AP  
> 1 AP reflexively  
> marQue I II III IV  
> market priCe 15 princes 75 princes 375 princes 1,875 princes  

**Chained-Grip** — *Weapon Accessory*  
> The user keeps a chain attached to both their wrist and the weapon, making it difficult - if not impossible - to be disarmed. Whenever the target of a disarm (called shot to the hand), the user gains a bonus to the resist roll.  
> +2 to resist being disarmed  
> +4 to resist being disarmed  
> +6 to resist being disarmed  
> +8 to resist being disarmed  
> marQue I II III IV  
> market priCe 10 princes 50 princes 250 princes 1,250 princes  


##### Bow augments (p.189–191)

| Augment | Slots | mQ I | mQ II | mQ III | mQ IV | Notes |
|---|---|---|---|---|---|---|
| Accurate | 1 | +1 Acc | +2 | +3 | +4 | |
| Collapsible | 1 | 1 size smaller | 2 | 3 | 4 | |
| Custom | 1 | others −3 | −6 | −9 | −12 | |
| Damaging | 2 | +1 DC | +2 | +3 | +4 | |
| Ground-Mount | 1 | +1 Acc | +2 | +3 | +4 | set 2 AP, pack 1 AP |
| Deflecting | 1 | deflect +4 Eva | – | – | – | always mQ I |
| Easily Altered | 1 | 2 AP | 2 | 1 | 1 | |
| Powerful | 1 | +2 Stk | +4 | +6 | +8 | |
| Quickened Arrows | 1 | +2 Stk (torso called-shot effect only) | +4 | +6 | +10 | |
| Reinforced | 1 | +1 size | +2 | +3 | +4 | |
| Scope | 1 | +50 ft | +100 | +200 | +300 | |
| Silent | 1 | T2 | T3 | T4 | impossible | |
| Versatile | 1 | melee attacks vs adjacent for 2 AP at −1 DC | – | – | – | always mQ II |
| Combustion | 3 | T1 fire | T2 | T2 | T3 | attack +1 AP; Dex resist |
| Burn Trail / Everburning | 1 | as melee versions | | | | |

**Book texts:**

**Accurate** — *Bow Augment*  
> Fine attention has been placed on the quality of your bow. The user gains a bonus to accuracy with the bow.  
> +1  
> +2  
> +3  
> +4  

**Collapsible** — *Bow Augment*  
> Sometimes discretion is the better part of not having your weaponry confiscated, so you create a clever collapsing mechanism for your bows which makes them easier to conceal. Any bow this is applied to can be broken down for 3 acion points and re-assembled for 3 action points. It is treated, for purposes of concealment, as being smaller than it is, but only when broken down.  
> 1 category smaller  
> 2 categories smaller  
> 3 categories smaller  
> 4 categories smaller  

**Custom** — *Bow Augment*  
> This bow was designed to be used by one person and one person only. That person must be designated at the time of the bow’s crafting. If anybody else attempts to use the custom bow, they suffer a penalty on all accuracy and strike rolls with it.  
> -3  
> -6  
> -9  
> -12  

**Damaging** — *Bow Augment*  
> takes up 2 augment sLots on a Bow  
> Your bow is larger but lighter, dealing extra damage with each blow.  
> +1 damage class  
> +2 damage class  
> +3 damage class  
> +4 damage class  

**Ground-Mount** — *Bow Augment*  
> You can set up your bow on the ground, using the earth to steady your shot. Setting up the bow requires 2 action points, and then pulling it back up so that you can move again requires 1 action point. While the bow is set in place, however, you gain a bonus on your accuracy.  
> +1  
> +2  
> +3  
> +4  

**Deflecting** — *Bow Augment*  
> You can use this bow like a shield, allowing you to deflect incoming attacks (gaining a +4 to evade in exchange for 1 reflexive action point).  
> Note: This augment always acts as marque I for the purposes of determining cost, though you can learn this augment despite your skill in armsmith.  

**Easily Altered** — *Bow Augment*  
> reQuires: Weapon to be made with Interchangeable Parts The weapon is easily altered, allowing its interchangeable parts to be used and switched around much more quickly than normal. The easily altered augment is a permanent affixture of the weapon, however, and cannot be activated or deactivated with interchangeable parts.  
> 2 AP to interchange parts  
> 2 AP to interchange parts  
> 1 AP to interchange parts  
> 1 AP to interchange parts  

**Powerful** — *Bow Augment*  
> Your weapon has a greater pull than others, giving the user a bonus on their strike rolls.  
> +2 on strike  
> +4 on strike  
> +6 on strike  
> +8 on strike  

**Quickened Arrows** — *Bow Augment*  
> Your bow fires arrows faster and more forcefully than most, making them have a more powerful knockback effect. Whenever your bow is used to make a called shot against a target’s torso, it gets a bonus to strike just for the called shot effect. The bonus does not affect the damage tier of the attack  
> +2 to Strike for Torso called shots  
> +4 to Strike for Torso called shots  
> +6 to Strike for Torso called shots  
> +10 to Strike for Torso called shots  

**Reinforced** — *Bow Augment*  
> You build your bow solidly, giving it little room to break on the battlefield. Whenever somebody attempts to sunder the reinforced bow, it acts as if it is several size categories larger than it is. Once these “reinforced” size categories are gone, then its actual damage begins to decrease.  
> 1 reinforced size category  
> 2 reinforced size categories  
> 3 reinforced size categories  
> 4 reinforced size categories  

**Scope** — *Bow Augment*  
> The range on your bow increases greatly, improving the range that the bow can accurate hit a target within.  
> +50 feet  
> +100 feet  
> +200 feet  
> +300 feet  

**Silent** — *Bow Augment*  
> This bow is whispering death. It makes almost no sound when an arrow is notched or fired from it, making it almost impossible for people to figure out where it is by sound alone. Any time anybody is attempting to figure out where the bow was shot from based on sound must make a tier result with their cunning.  
> Tier 2  
> Tier 3  
> Tier 4  
> Impossible (or Tier 5)  

**Versatile** — *Bow Augment*  
> Your bow is also an effective melee weapon. You can make attacks against adjacent opponents for 2 action points, although your damage class is at a -1 when doing so.  
> Note: This augment always acts as marque II for the purposes of determining cost, though you can learn this augment despite your skill in armsmith.  

**Combustion** — *Bow Augment*  
> takes up 3 augment sLots on a Bow  
> resist: Dexterity (marques down)  
> Cost to aCtivate: Attack +1 AP  
> Fire lashes out from your bow, allowing you to set your arrows on fire. You can use this to attempt to set your enemy aflame. The target may resist with their dexterity (lowering the marques of the combustion).  
> The victim catches on Tier 1 fire  
> The victim catches on Tier 2 fire  
> The victim catches on Tier 2 fire  
> The victim catches on Tier 3 fire  

**Burn Trail** — *Bow Augment*  
> reQuires: placed on bow with the Combustion augment Any person attempting to physically aid a victim of your combustion must first make a dexterity resist that equals the marque of your Combusion augment or be set on fire themselves.  
> Note: This augment always acts as marque III for the purposes of determining cost, though you can learn this augment despite your skill in armsmith.  

**Everburning** — *Bow Augment*  
> reQuires: placed on bow with the Combustion augment Despite your victim’s best efforts to put themselves out, they seem to continue burning. When catching things on fire through the use of a combustion attack, extra action points are required to put out the fire.  
> 1 extra AP  
> 2 extra AP  
> 3 extra AP  
> 4 extra AP  


##### Armor & shield augments (p.192–195)

| Augment | Slots | mQ I | mQ II | mQ III | mQ IV | Notes |
|---|---|---|---|---|---|---|
| Airmelting | 1 | 2 heat dmg within 5 ft (you take half) | 4 | 6 | 8 | 1 AP |
| Bracings | 1 | can't be knocked prone (1 AP to undo) | – | – | – | always mQ I |
| Bulletproofing | 1 | +2 Def vs firearms | +4 | +6 | +8 | `[COND]` |
| Camouflage | 1 | +2 Cunning to hide outdoors | +4 | +6 | +8 | |
| Crashbreaking | 1 | 1 wound per 30 ft fallen | 40 ft | 50 ft | 60 ft | |
| Damage Soaking | 2 | +1 soak class | +2 | +3 | +4 | `[STAT:Soak]` |
| Defensive | 1 | +2 Def | +4 | +6 | +8 | `[STAT:Def]` |
| Electro-Absorption | 1 | +2 soak vs electrical | +4 | +6 | +8 | electricity becomes soakable |
| Fireproofing | 1 | +1 soak vs fire | +2 | +3 | +4 | fire soakable; fully soaked → no burns/fire |
| Flame Retardant | 1 | immune to T1 fire | T2 | T3 | T4 | |
| Handcrushing | 1 | 4 unsoakable to grabber | 8 | 12 | 16 | 1 AP |
| Injector | 1 | holds 1 potion | 2 | 3 | 4 | inject 0 AP, reload 5 AP |
| Mobile | 1 | +5 ft speed | +10 | +10 | +15 | `[STAT:Spd]` |
| Quick Equip | 1 | don in 10 AP | 6 AP | 3 AP | 1 AP | |
| Razor-Ridged | 1 | grabber takes 3 unsoakable (again each turn) | 6 | 9 | 12 | |
| Reinforced Plating | 1 | +2 resist called shots to one chosen area | +4 | +6 | +8 | |
| Stabilizing Rods | 1 | enter firing stance (Footing) for 0 AP; rooted until 1 AP reset | – | – | – | always mQ III |
| Slippery | 1 | +2 to evade/resist grabs | +4 | +6 | +8 | |
| Steaming | 1 | poor vision (−2 Acc/Eva) within 5 ft | 10 | 15 | 20 | 1 AP toggle off |
| Welded Weapon | 1 | medium weapon welded (can't be disarmed, no draw) | medium | heavy | heavy | |

**Book texts:**

**Airmelting** — *Armor Augment*  
> aCtivation Cost: 1 AP  
> The armor has numerous exhausts, heat valves, and pipes on it that, when released, super-heat the air around the wearer. If you’re wearing this armor and spend 1 action point to release the exhausts, it heats the air around you. Everyone within 5 feet of you takes heat damage, and you take half that amount (unless you have fireproofing).  
> 2 damage  
> 4 damage  
> 6 damage  
> 8 damage  

**Bracings** — *Armor Augment*  
> The armor is braced to prevent you from ever falling prone. Unless you choose to undo the bracings (an action that costs 1 action point), there is no way the wearer of this armor can go prone. Note: This augment always acts as marque I for the purposes of determining cost, though you can learn this augment despite your skill in armsmith.  

**Bulletproofing** — *Armor Augment*  
> The armor is designed to take bullets. Whenever being shot by a firearm, the wearer gains a bonus on their defense roll.  
> +2 defense  
> +4 defense  
> +6 defense  
> +8 defense  

**Camouflage** — *Armor Augment*  
> The armor has been painted, ruffled, and tarnishes added to allow it to blend in more efficiently in natural terrains. When in the uncivilized outdoors, this armor grants a bonus to cunning rolls when attempting to hide.  
> +2  
> +4  
> +6  
> +8  

**Crashbreaking** — *Armor Augment*  
> This armor is designed to help cushion the wearer’s fall by absorbing the shock and keeping the person inside from rattling around. It’s not going to keep you alive in a crashing airship from a high altitude, but it might help out when somebody pushes you over the side of the building. While wearing crashbreaking armor, you can fall further before taking wounds damage.  
> 1 wounds damage per 30 feet fallen  
> 1 wounds damage per 40 feet fallen  
> 1 wounds damage per 50 feet fallen  
> 1 wounds damage per 60 feet fallen  

**Damage Soaking** — *Armor Augment*  
> takes up 2 augment sLots on armor  
> Your armor is so thick that it soaks more damage than normal.  
> +1 damage soak class  
> +2 damage soak class  
> +3 damage soak class  
> +4 damage soak class  

**Defensive** — *Armor Augment*  
> This armor is heavier, with more shock-absorbant plating and less spots for enemy blade’s to find cleavage. This armor provides a bonus to the wearer’s defense.  
> +2 defense  
> +4 defense  
> +6 defense  
> +8 defense  

**Electro-Absorption** — *Armor Augment*  
> The armor re-routes electricity through it and into specially created devices that absorb the shock. Anything that deals electricity damage is not entirely soakable, and attacks that deal electricity damage (even if they are only partially electrical, such as attacks with a pulsing weapon) increase the soak class of the armor.  
> +2 soak class against electrical attacks  
> +4 soak class against electrical attacks  
> +6 soak class against electrical attacks  
> +8 soak class against electrical attacks  

**Fireproofing** — *Armor Augment*  
> While wearing armor that has fireproofing, all fire attacks are soakable. Furthermore, the soak class for the armor is improved against fire. (If the wearer would take burns or be set on fire from a fire attack that is entirely soaked, the extra effects are negated.)  
> +1 soak class against fire  
> +2 soak class against fire  
> +3 soak class against fire  
> +4 soak class against fire  

**Flame Retardant** — *Armor Augment*  
> The armor generally cannot be caught on fire, depending on how intense the fire is.  
> Cannot be caught on tier 1 fire  
> Cannot be caught on tier 2 fire  
> Cannot be caught on tier 3 fire  
> Cannot be caught on tier 4 fire  

**Handcrushing** — *Armor Augment*  
> aCtivation Cost: 1 AP  
> When people add gears to their armor, it’s not merely steampunkthemed decor. Those gears are designed to tear apart anybody who lays a hand on that armor. If a person is grabbing you while wearing this armor, you may spend 1 action point to activate the spinning gears, the hydraulic spikes, or the built-in flamethrower and deal unsoakable damage to the person touching you.  
> 4 damage  
> 8 damage  
> 12 damage  
> 16 damage  
> Note: As a courtesy, feel free to remind the person grabbing you that they can reflexively let go of you for 0 action points whenever they’d like.  

**Injector** — *Armor Augment*  
> Through the use of a magnetic trigger system connected to a liquid injector, this augment creates a quick injection system that allows the wearer to, through the push of a button, inject himself with a dose of a chemical. It requires 5 action points to reload a dose of the chemical after it’s been used, but no action points to inject it. At any given time, the armor can only hold so many chemicals.  
> 1 alchemical potion  
> 2 alchemical potions  
> 3 alchemical potions  
> 4 alchemical potions  

**Mobile** — *Armor Augment*  
> Light, easy to move in, and with enhanced piston-joints to really get you moving, this armor provides a bonus to your speed.  
> +5 feet  
> +10 feet  
> +10 feet  
> +15 feet  

**Quick Equip** — *Armor Augment*  
> Most armor takes a while to equip - not this stuff! It takes only a turn or two.  
> 10 AP to equip  
> 6 AP to equip  
> 3 AP to equip  
> 1 AP to equip  

**Razor-Ridged** — *Armor Augment*  
> Your armor has sharp edges, pointy bits, and moving pieces that keep enemies from grabbing you. Any time an opponent grabs onto you, they automatically take a number of unsoakable damage based on the razor-ridged marque. Every turn that they keep holding on to you, they take that damage again (this damage is dealt at the end of their turn, when their action points refresh).  
> 3 damage  
> 6 damage  
> 9 damage  
> 12 damage  

**Reinforced Plating** — *Armor Augment*  
> Through additional plating being added to various body parts, you are able to decrease the chances of called shots effecting you. When you choose this augment, choose one limb or area on the body (either arm, either leg, the torso, or the head). Thereafter, you gain a bonus whenever attempting to resist a called shot there.  
> +2  
> +4  
> +6  
> +8  

**Stabilizing Rods** — *Armor Augment*  
> Activation Cost: 0 AP (see below)  
> Your armor is built with stabilizing rods in the arms that allow you to automatically enter firing stance for 0 action points. This allows you to fire super-heavy firearms and crossbows immediately. However, you are rooted to the spot you’re in until you spend 1 action point to reset the stabilizing rods back into their original location.  
> Note: This augment always acts as marque III for the purposes of determining cost, though you can learn this augment despite your skill in armsmith.  

**Slippery** — *Armor Augment*  
> While wearing this armor, you are very difficult to grab on to. Any time you are attempting to evade a grab or resist a grab, you gain a bonus on your roll.  
> +2  
> +4  
> +6  
> +8  

**Steaming** — *Armor Augment*  
> Your armor lets off steam, enveloping you and everyone around you in a foggy, hard-to-see-through steam. You may turn it off for  
> 1 action point, but otherwise it makes an area around you difficult to see through. Anybody in the area is affected by poor vision, and takes a -2 to accuracy and evade rolls.  
> 5 feet  
> 10 feet  
> 15 feet  
> 20 feet  

**Welded Weapon** — *Armor Augment*  
> You weld a weapon to your armor. The weapon cannot be disarmed, dropped, or concealed, but it also does not need to be drawn in order to be used. The maximum size of the weapon depends on the mark.  
> Medium  
> Medium  
> Heavy  
> Heavy  




#### Automata

| Specialty | Group | Bonuses | Cost / type | Requires | Effect | Tags |
|---|---|---|---|---|---|---|
| **Automaton Repairs** |  | Def +2, Aug +2, HP +7 | 3 AP |  | Cost: 3 AP<br>You’re able to quickly repair an automaton in battle. To do so, you must be adjacent to it. By making the repairs, you restore a number of wounds to the automaton.<br>10 wounds<br>15 wounds<br>20 wounds<br>30 wounds | [ACTION] |
| **Interchangeable Parts** |  | Aug +2, DIY +1, HP +6 | 3 AP to swap |  | Cost: 3 AP<br>Your automatons are designed so that their parts can be replaced and altered in the middle of battle. This gives the automatons additional slots for augments, but these augments are not always active. At any time, a person may switch out the augments for 3 action points, activating one augment but deactivating another augment. You may replace multiple augments at the same time all for the cost of 3 action points.<br>This specialty works within the marque system. The amount of interchangeable slots the automaton has depends on the marque of its creator.<br>1 interchangeable slot for an augment<br>2 interchangeable slots for augments<br>3 interchangeable slots for augments<br>4 interchangeable slots for augments | [CRAFT] [SCALE:marque] |
| **Steam-Powered Crafter** | Crafting Steamers | Aug +2, DIY +1, HP +4 | Passive (crafting) |  | The first step in crafting your steamer, boilers are the machinery that powers your automaton and gives it motion and strength. Your boiler is automatically housed within the automaton’s torso, onto which you can attach any body parts you wish. Without spending any money, you can build and maintain several steamers based on your current Do-It-Yourself (DIY) score. The boilers in these steamers can then be upgraded with augments. You’ll learn 2 augments from this specialty, which can be selected under “boiler augments” below. These augments have marques. At lower levels, you’ll start with Marque I augments. As your skill in Automata improves, your marques will increase. See the “Crafting” page at the beginning of this chapter for more information.<br>Each boiler can be upgraded with 3 augments. Sometimes an augment will take up multiple augment slots. For example, the “Flight” augment is worth 2 slots, so a boiler only has<br>1 more available slot for an augment after “Flight” has been applied.<br>numBer oF steamers you Can maintain<br>Without needing to buy pieces or parts, you can build some steamers entirely out of scraps. These automatons must be constantly maintained by you and stop working soon after leaving your care. You may build and maintain a number of steamers for free based on your DIY score. You may build new steamers or augment old ones during any period of downtime you have. your Diy: 1 2 3 4 5 6<br>you Can BuiLD: 1 1 1 1 1 2<br>your Diy: 7 8 9 10 11 12<br>you Can BuiLD: 2 2 2 2 2 3<br>the Cost oF steamers<br>If you need to build a steamer that you can’t build for free from your DIY score, you will need to buy the materials for it. A steamer without augments will cost 50 princes. If you are building a steamer, the steamer will have a base materials cost. It is 1/5th the market price (10 princes).<br>Every augment will increase the price. The higher the marque, the greater the price. The market price for an augment can be found in the chart below.<br>marQue I II III IV<br>market priCe 50 princes 250 princes 1250 princes 6250 princes If you are building the augment, you pay 1/5th the price, which is the same as if you were buying an augment one marque lower. (As in, the material cost for a Marque III augment is the market price fo a Marque II augment.) The material cost for a Marque 1 augment is 10 princes.<br>eamer s<br>Using your Steamer<br>Back in the day, steam-powered automatons used coal, so they were often large, hulking affairs that moved slowly and ate up a lot of fuel. Emperor Deylus Luthricien and the royalists changed that during the civil war when they integrated aether technology into their boilers for easier steam generation. Now, steam-powered automatons are fast, lighter-weight, and can be controlled via remote controls and radio waves.<br>ControL methoD<br>Steamers require the use of a two-handed remote control, emitting radio waves to the aether resonators inside the automatons. These remote controls allow the user to be up to 100 feet away and still control the automaton. The automaton can generally do anything a normal person could do (such as walking, jumping, fighting, and deflecting), and it takes the controller the same amount of action points to control the automaton as it would for a normal person to make the action (such as 1 action point to make the automaton move, or 2 action points to make the automaton attack). A single remote control can be used to control all of your automatons. Steamers have no action points of their own; therefore, if your steamer is hit with an attack that lowers its number of action points, your steamer is unaffected. BoDy oF the maChine<br>Steamers will have a Boiler, which will be augmentable with 3 slots. One may later take Beta Boiler to improve on that. Body parts may then be added to the boiler.<br>Your steamer (by default) is built with a head to house its radio receptors and a torso and groin to house its boiler. The two are connected via a neck support. To its torso you may attach either two arms or one unit of movement. Its groin may have a unit of movement attached to it. A unit of movement is either a set of legs, wheels, or a propulsion device. (See the Units of Movement sidebar for more information.) Your steamer has 0 hit points and 30 wounds. Any “bleeding” damage your steamer takes causes steam to eractically leak out of its boiler, making it take bleeding damage in the same fashion as any regular organism. In addition, the rigid structuring of your steamer’s boiler grants it an extra 3 soak class. As your automaton has no mind of its own, it cannot be affected by anything that requires Spirit or Cunning as a resist. Units of Movement<br>Automatons will normally have a unit of movement attached to them. This could be a set of legs, wheels, or a propulsion device .<br>Legs c<br>Legs provide movement. Legs can easily traverse almost any terrain. By having a set of legs (typically two), an automaton will have a speed of 20 feet, can walk up stairs, move over all degrees rough terrain, and generally have little problem getting about as do most tephrans. The legs do not allow the automaton to climb or swim. By having legs, the automaton can be affected by called shots to the legs.<br>wheeLs c<br>Wheels allow for faster movement, though their are some clear disadvantages compared to legs. Wheels will give the automaton a speed of 30 feet, but the automaton will only be able to go up stairs at a speed of 10 feet, and the penalties for moving through rough terrain are doubled. The wheels do not allow the automaton to climb or swim. Wheels can be targeted as called shot locations - they have the same effects as legs. propuLsion DeviCe c<br>Sometimes legs and wheels don’t cut it. Underwater automatons will have propellors or automated fins. Some automatons will stand on wheels but use a rocket to propel them forward. A propulsion device will allow the automaton a speed of 20 feet (on either land, surface waters, or under water). The penalties for moving through rough terrain are doubled, and the propulsion device does not allow the automaton to climb or swim (unless the propulsion device is intended for underwater movement, in which case it does not allow the automaton to move across the land). If a propulsion device is targeted as a called shot location, it has the same effect as if it were a leg. | [AUG] [DIY] [CRAFT:steamer] |
| **Beta Boilers** | Crafting Steamers | Aug +2, DIY +1, HP +4 | Passive | 4 Automata; Steam-Powered Crafter | reQuires: 4 skill points in Automata & Steam-Powered Crafter Your boilers are highly advanced yet difficult for most people to use. Such boilers can be upgraded with 2 more augments (bringing the total up to 5 augmentable slots).<br>If anybody other than you attempts to use one of your beta steamers, they must succeed in rolling a sciences result one tier higher than the highest marque you have on your steamer. If your steamer has a Marque IV augment, it is impossible for them to use it (unless they can somehow obtain a tier result of 5 with their sciences attribute). | [CRAFT] [REQ] |
| **Prototype Boilers** | Crafting Steamers | Aug +1, DIY +1, HP +5 | Passive | 16 Automata; Steam-Powered Crafter; Beta Boilers | reQuires: 16 skill points in Automata, Steam-Powered Crafter, & Beta Boiler specialties<br>You’ve perfected your beta boilers and made them user-friendly. Now anybody can control an automaton with a boiler that you designate as being a prototype. | [CRAFT] [REQ] |
| **Steamer Operator** | Steamer Operator | Acc +1, Eva +1, HP +6 | Passive |  | As a practiced automaton fighter, you can make a steamer move just the way you want it to. Whenever you are operating a steamer, the steamer can use your accuracy, strike, defense, and evade. | [PASSIVE] |
| **Steam Poser** | Steamer Operator | Eva +1, Aug +1, HP +7 | Passive | Steamer Operator; ≥1 stance known | reQuires: Steam Operator & at least one stance known You know how to make a steamer accurately strike a pose. Steamers you control will automatically act as if they are in the same stance(s) as you. The instant you stop being a steamer’s current operator, the steamer loses all its stances. | [PASSIVE] [REQ] |
| **Steam Specialist** | Steamer Operator | Acc +1, Aug +1, HP +6 | Passive | 3 Automata; Steamer Operator | reQuires: 3 skill points in Automata & Steam Operator specialty A true joystick master, you rise above any primitive control scheme put in front of you to make your steamer move just as you do. You can now modify the actions of any steamer you are operating with specialties you know. | [PASSIVE] [REQ] |
| **Fuse Box Builder** | Crafting Fuse Boxes | Aug +2, DIY +1, HP +4 | Passive (crafting) |  | You can now create electric-powered automatons and upgrade the brainworks that power them and grant them artificial intelligence. Tephrans colloquially call them “fuse boxes.” Without spending any money, you can build and maintain one fuse box. The brainworks of this fuse box can then be upgraded with augments. You’ll learn 2 augments from this specialty, which can be selected under “brainworks augments” below. These augments have marques. At lower levels, you’ll start with Marque I augments. As your skill in Automata improves, your marques will increase. See the “Crafting” page at the beginning of this chapter for more information.<br>Each brainworks can be upgraded with 3 augments. Sometimes an augment will take up multiple augment slots. For example, the “Lightning Soul” augment is worth 2 slots, so a brainworks unit only has 1 more available slot for an augment after “Lightning Soul” has been applied.<br>maintaining your Fuse Box<br>Without needing to buy pieces or parts, you can build a single fuse box entirely out of scraps. This automaton must be constantly maintained by you and stops working soon after leaving your care. You can replace your fuse box automaton or augment your current one during any period of downtime you have. the Cost oF Fuse Boxes<br>If you need to build a fuse box that you can’t build for free from your DIY score, you will need to buy the materials for it. The fuse box, unaugmented, will have a base cost depending on its marque. (The marque will determine its number of action points per turn.) If you buy a fuse box and augments, you will add the price of the augments onto the price of the automaton.<br>marQue I II III IV<br>market priCe 200 princes 1000 princes 5000 princes 25000 princes Every augment will increase the price. The higher the marque, the greater the price. The market price for an augment can be found in the chart below.<br>marQue I II III IV<br>market priCe 50 princes 250 princes 1250 princes 6250 princes If you are building the augment, you pay 1/5th the price, which is the same as if you were buying an augment one marque lower. (As in, the material cost for a Marque III augment is the market price fo a Marque II augment.) The material cost for a Marque 1 augment is 10 princes.<br>se Boxes | [AUG] [DIY] [CRAFT:fusebox] |
| **Advanced Brainworks** | Crafting Fuse Boxes | Aug +2, DIY +1, HP +4 | Passive | 4 Automata; Fuse Box Builder | reQuires: 4 skill points in Automata & Fuse Box Builder specialty Your brainworks go far beyond what most other automata builders could conceptually imagine. Such brainworks have two more slots for you to place augments into. | [CRAFT] [REQ] |
| **Superior Brainworks** | Crafting Fuse Boxes | Aug +2, DIY +1, HP +6 | Passive | 6 Automata; Fuse Box Builder | reQuires: 6 skill points in Automata & Fuse Box Builder specialty Your brainworks are far more advanced than the common artificial intelligence. All brainworks you create with your DIY have 3 action points per turn instead of 2. Buying fuse boxes with superior brainworks costs 10,000 princes (a materials cost of 2,000 princes) on top of any other costs. | [CRAFT] [REQ] |
| **Heroic Brainworks** | Crafting Fuse Boxes | Aug +2, DIY +1, HP +5 | Passive | 9 Automata; Fuse Box Builder; Superior Brainworks | reQuires: 9 skill points in Automata, Fuse Box Builder, & Superior Brainworks specialties<br>Brainworks crafted with your DIY can fight with the tenacity of a great warrior and think at the speed of a quick-witted rogue. All brainworks you create with your DIY have 4 action points per turn instead of 3. Buying fuse boxes with superior brainworks costs 50,000 princes (a materials cost of 10,000 princes) on top of any other costs. | [CRAFT] [REQ] |
| **Personality** | Crafting Fuse Boxes | Aug +2, DIY +1, HP +5 | Passive | Fuse Box Builder | reQuires: Fuse Box Builder specialty<br>It’s understandable for a gentleman adventurer to get lonely on the road. The cold embrace of an unfeeling automaton won’t stave off feelings of solitude for long. Luckily for you, there’s an easy solution: give that unfeeling automaton some feelings! Your brainworks can now be built with personality, making the fuse box you put them into feel the same emotional sensations as any other Tephran. This gives them the ability to gain stories (including ones from your nationality) and learn specialties from the Spirit attribute. Buying fuse boxes with personality costs 5,000 princes (a materials cost of 1,000 princes) on top of any other costs.<br>Note: They still cannot gain DIY or augments through stories or specialties.<br>Using your Fuse Box<br>The first electric-powered automatons were invented by the Hazards, and later the technology was adapted and used to create numerous smaller and more efficient automatons that would protect the Hazardlands. Many Evanglessians called electric-powered automatons “Sparkers” or “Fuse Boxes.” Fuse Boxes have the most advanced sensory arrays, and can compute information to such an extent that they seem almost lifelike. This artificial intelligence is known as brainworks. ControL methoD<br>Fuse boxes use their brainworks to act independently. They begin as creations with 2 action points per turn. The sensory array allows the creator to give it verbal commands, like telling it to “attack that man” or “run to my side,” which costs the creator no action points. Your fuse box must roll priority separately from you as it is an autonomous being with its own turns. BoDy oF the maChine<br>Fuse Boxes will begin with Brainworks, which has 3 slots that can be augmented. This can be upgraded with Advanced Brainworks, which gives the automaton more control over itself and an additional 2 slots for its brainworks. Body parts can then be added onto the brainworks.<br>Your fuse box (by default) is built with a head to house its brainworks and a torso and groin to house its drive core. The two are connected via a neck support. To its torso you may attach either two arms or one unit of movement. Its groin may have a unit of movement attached to it. A unit of movement is either a set of legs, wheels, or a propulsion device. (See the Units of Movement sidebar for more information.) Your fuse box’s integrity comes from the electricity its brainworks produces, which at default is 8 hit points. Once out of hit points its brainworks is exposed and your automaton will begin to take wounds damage. Fuse boxes have only 12 points of wounds. Any “bleeding” damage your automaton takes causes lightning to shoot out of its electrical conduit, making it take bleeding damage in the same fashion as any regular organism. Fuse boxes have 2 action points per turn. As sentient machines, fuse boxes can learn specialties based on their marque. They act as if they have 1 point in the skills they have specialties in for the purposes of prerequisites and for the specialty itself. This point does not increase their attributes at all. Has 1 specialty<br>Has 2 specialties<br>Has 3 specialties<br>Has 5 specialties<br>Pirates or Ninjas? Obviously<br>the question is flawed, for<br>automatons rule. | [CRAFT] [REQ] |
| **Clockwork Crafter** | Crafting Clockworks | Aug +2, DIY +1, HP +4 | Passive (crafting) |  | You can now create new kinetically-powered automatons and upgrade the analytical engine that controls its pre-determined responses. Tephrans colloquially call them “clockworks.” Without spending any money, you can build and maintain several clockworks based on your current Do-It-Yourself (DIY) score. The analytical engines of these clockworks can then be upgraded with augments. You’ll learn 2 augments from this specialty, which can be selected under “analytics augments” below. These augments have marques. At lower levels, you’ll start with Marque I augments. As your skill in Automata improves, your marques will increase. See the “Crafting” page at the beginning of this chapter for more information.<br>Each analytics can be upgraded with 3 augments. Sometimes an augment will take up multiple augment slots. For example, the “flight” augment is worth 2 slots, so an analytics unit only has 1 more available slot for an augment after “flight” has been applied.<br>numBer oF CLoCkworks you Can maintain<br>Without needing to buy pieces or parts, you can build some clockworks entirely out of scraps. These automatons must be constantly maintained by you and stop working soon after leaving your care. You may build and maintain a number of clockworks for free based on your DIY score. You may build new clockworks or augment old ones during any period of downtime you have. your Diy: 1 2 3 4 5 6<br>you Can BuiLD: 1 1 1 1 1 2<br>your Diy: 7 8 9 10 11 12<br>you Can BuiLD: 2 2 2 2 2 3<br>the Cost oF CLoCkworks<br>If you need to build a clockwork that you can’t build for free from your DIY score, you will need to buy the materials for it. A clockwork without augments will cost 50 princes. If you are building a clockwork, the clockwork will have a base materials cost. It is 1/5th the market price (10 princes). Every augment will increase the price. The higher the marque, the greater the price. The market price for an augment can be found in the chart below.<br>marQue I II III IV<br>market priCe 50 princes 250 princes 1250 princes 6250 princes If you are building the augment, you pay 1/5th the price, which is the same as if you were buying an augment one marque lower. (As in, the material cost for a Marque III augment is the market price fo a Marque II augment.) The material cost for a Marque 1 augment is 10 princes. | [AUG] [DIY] [CRAFT:clockwork] |
| **Advanced Analytics** | Crafting Clockworks | Aug +2, DIY +1, HP +5 | Passive | 4 Automata; Clockwork Crafter | reQuires: 4 skill points in Automata & Clockwork Crafter specialty Your analytics go far beyond what most other automata builders could conceptually imagine. Such analytics have two more slots for you to place augments into.<br>Using your Clockworks<br>Clockwork automatons are the oldest automatons, as Velkya, the founder of Evangless, was fond of using them. Clockwork automatons have come a long way, however, and now use analytical engines to evaluate their surroundings and enact preprogrammed responses. Clockworks can now work for hours and hours without needing any maintenance (or winding up, as it would be).<br>ControL methoD<br>Clockworks work by using pre-programmed responses called Directives. Without a Directive augmented onto them, a clockwork will not make any actions. Each directive acts separately from the rest. Clockworks don’t have action points, and require no action points from its master to function. Therefore if your clockwork is hit with an attack that lowers its number of action points for a turn, your clockwork is unaffected. Outside of combat you can temporarily turn off and on some (or all) of your clockwork’s directives to avoid it attacking townsfolk. BoDy oF the maChine<br>Clockworks will begin with an analytical engine, which has 3 slots to be augmented with pre-programmed responses. This can be upgraded with Advanced Analytics, which allows for 2 more slots. Some crafters learn how to make punch cards, to re-program their clockworks on the spots. Body parts can then be added onto the analytical engine.<br>Your clockwork (by default) is built with a head to house its analytical engine and a torso and groin to house its perpetual motion clockwork. The two are connected via a neck support. To its torso you may attach either two arms or one unit of movement. Its groin may have a unit of movement attached to it. A unit of movement is either a set of legs, wheels, or a propulsion device. (See the Units of Movement sidebar for more information.)<br>Clockworks have no hit points and 20 points of<br>wounds. Any “bleeding” damage your automaton takes causes springs and cogs to pop out of place within its clockwork, making it take bleeding damage in the same fashion as any regular organism. | [CRAFT] [REQ] |
| **Prosthetician** | Crafting Prosthetics | Aug +2, DIY +1, HP +6 | Passive (crafting) |  | You now have the ability to craft mechanical prosthetics onto people or augment the limbs of automatons. When you create a prosthetic for a person, it works as a limb replacement. Of course, once you affix your prosthetics with hidden cannons, chainsaws, and ridiculous pistons, the comparison stops there. Without spending any money, you can build and maintain several prosthetics based on your current Do-It-Yourself (DIY) score. The prosthetics can then be upgraded with augments. You’ll learn 2 augments from this specialty, which can be selected under “univeral prosthetic augments,” “prosthetic arm augments,” “prosthetic hand augments,” or “prosthetic leg augments,” below. These augments have marques. At lower levels, you’ll start with Marque I augments. As your skill in Automata improves, your marques will increase. See the “Crafting” page at the beginning of this chapter for more information. Each prosthetic can be upgraded with 3 augments. Some materials can only be upgraded twice (like wooden prosthetics) or just once (like organic ones). Sometimes an augment will take up multiple augment slots. For example, if an augment is worth<br>2 slots, a prosthetic only has 1 more available slot for an augment after the 2-slot augment has been applied.<br>numBer oF prosthetiCs you Can maintain<br>Without needing to buy pieces or parts, you can build some prosthetics entirely out of scraps. These prosthetics must be constantly maintained by you and stop working soon after leaving your care. You may build and maintain a number of prosthetics for free based on your DIY score. You may build new prosthetics or augment old ones during any period of downtime you have. Replacing both an arm and hand does count as 2 prosthetics.<br>your Diy: 1 2 3 4 5 6<br>you Can BuiLD: 2 3 3 3 4 4<br>your Diy: 7 8 9 10 11 12<br>you Can BuiLD: 4 5 5 5 6 7<br>the Cost oF prosthetiCs<br>If you need to build prosthetics that you can’t build for free from your DIY score, you will need to buy the materials for it. A prosthetic without augments will cost 25 princes at market value. If you are building a prosthetic, the prosthetic will have a base materials cost. It is 1/5th the market price (5 princes).<br>Every augment will increase the price. The higher the marque, the greater the price. The market price for an augment can be found in the chart below.<br>marQue I II III IV<br>market priCe 25 princes 125 princes 625 princes 3125 princes If you are building the augment, you pay 1/5th the price, which is the same as if you were buying an augment one marque lower. (As in, the material cost for a Marque III augment is the market price fo a Marque II augment.) The material cost for a Marque 1 augment is 5 princes.<br>Using Prosthetics<br>When you first learn to make prosthetics (through the Prosthetician specialty), you can make and augment hands, arms, and legs. If somebody is missing a hand, arm, or leg, you can replace it with a prosthetic. The only lasting penalty to having a prosthetic limb is the permanent loss of wounds that come from losing a limb. Universal prosthetic augments can go on any prosthetics.<br>wounDs & FataLs<br>If you suffer a wound or fatal effect against a prosthetic, the effect is the same, except that you cannot bleed out by having a severed prosthetic.<br>upgraDing automaton LimBs<br>You can add prosthetics onto an automaton or augment its default limbs. If you upgrade the existing limbs, it counts against your limit of prosthetics you can make and maintain with your DIY score. | [AUG] [DIY] [CRAFT:prosthetic] |
| **Beta Prosthetics** | Crafting Prosthetics | Aug +2, DIY +1, HP +6 | Passive | 4 Automata; Prosthetician | reQuires: 4 skill points in Automata & Prosthetician specialty Your prosthetics are quite complex, but they can accomplish quite a bit. Such prosthetics can be upgraded with 2 more augments (bringing the total for metal prosthetics up to 5 augmentable slots).<br>You can only apply beta prosthetics to yourself and automatons that were created by you as either beta (for boilers) or advanced (for analytics and brainworks) models. | [CRAFT] [REQ] |
| **Prototype Prosthetics** | Crafting Prosthetics | Aug +1, DIY +1, HP +7 | Passive | 16 Automata; Prosthetician; Beta Prosthetics | reQuires: 16 skill points in Automata, Prosthetician, & Beta Prosthetics specialties<br>You’ve perfected your beta prosthetics and made them userfriendly. Now anybody can use a prosthetic that you designate as being a prototype. | [CRAFT] [REQ] |
| **Automata Tinkerer** | Crafting Prosthetics | Aug +2, DIY +1, HP +4 | Passive | 3 Automata; Prosthetician | reQuires: 3 skill points in Automata & Prosthetician specialty You can augment all pieces of your automatons - from their eyes to their ears to their torsos. You can learn augments for every part of the automaton’s body.<br>If you have Automata Upgrader, you can use that in conjuction with Automata Tinkerer, causing all of the automaton’s body parts to not cost anything or count against your Do-It- Yourself (DIY) score. | [AUG] [REQ] |
| **Automata Upgrader** | Crafting Prosthetics | Aug +2, DIY +1, HP +4 | Passive | 3 Automata; Prosthetician | reQuires: 3 skill points in Automata & Prosthetician specialty You’ve tinkered and played with your automatons so much that you no longer use your Do-It-Yourself (DIY) score to determine how many of your automaton’s limbs you can upgrade. Whenever you are augmenting the default limbs of your automatons, those limbs do not count against the maximum number of prosthetics you can create. | [CRAFT] [REQ] |
| **Nerve Crafting** | Crafting Prosthetics | Aug +1, DIY +1, HP +7 | Passive | 7 Automata; Prosthetician | reQuires: 7 skill points in Automata & Prosthetician specialty It is normally impossible to attach a prosthetic arm to one’s ribcage, or a prosthetic hand to one’s spine. You, however, have learned how to create nerve endings in a person where none should exist. You may now apply extra prosthetics to a person beyond what they could normally handle (allowing you to add a third arm, an extra hand, maybe even another leg). When you nerve craft somebody, they permanently lose<br>1 wound in order to gain the prosthetic. They gain the wound back if they surgically remove the prosthetic. | [CRAFT] [REQ] [STAT:Wnd −1 per extra limb] |
| **Sensory Builder** | Crafting Prosthetics | Aug +2, DIY +1, HP +7 | Passive | Prosthetician | reQuires: Prosthetician specialty<br>Some of the most difficult things to create prosthetics for are one’s ears and eyes, but you’ve learned the craft. You may now create prosthetics for ears and eyes, and they count against your maximum crafting amount of prosthetics based on your Do-It- Yourself (DIY) score. | [CRAFT] [REQ] |

##### Automata – shared rules (p.196–198)
Three automaton types: **Steamers** (remote-controlled, steam, strongest), **Fuse Boxes** (electric, autonomous brainworks), **Clockworks** (spring-driven, pre-programmed reactions). Prosthetics can be attached to automatons or people.

**Units of movement** (attach to torso instead of arms, and/or to groin):

| Unit | Speed | Notes |
|---|---|---|
| Legs | 20 ft | stairs, all rough terrain; no climb/swim; leg called shots apply |
| Wheels | 30 ft | stairs at 10 ft; rough terrain penalties doubled; targetable like legs |
| Propulsion device | 20 ft (land, surface or underwater version) | rough terrain doubled; underwater version can't move on land |

**Steamer** (p.197): two-handed remote control, range 100 ft, controls all your automatons; controller pays the AP for each action (move 1, attack 2…); steamers have no AP of their own (immune to AP loss). Body: head + neck + torso + groin (boiler); torso: 2 arms or 1 movement unit; groin: 1 movement unit. **0 HP, 30 wounds, +3 natural soak class**; bleeding = steam leak; immune to Spirit/Cunning-resisted effects.
DIY → steamers: DIY 1–5: 1 · 6–11: 2 · 12: 3. Unaugmented steamer 50 pr (materials 10 pr).

**Fuse box** (p.202–203): one DIY fuse box; acts on its own turn (own priority), verbal commands cost you no AP. **2 AP/turn** (3 with Superior, 4 with Heroic Brainworks), **8 HP, 12 wounds**. Knows specialties by marque: mQ I 1 / II 2 / III 3 / IV 5 specialties, treating skills as 1 point. Base price by marque: 200 / 1,000 / 5,000 / 25,000 pr.

**Automaton augment price** (boiler, brainworks, analytical engine): mQ I 50 / II 250 / III 1,250 / IV 6,250 pr; mQ I material 10 pr.

##### Boiler augments (steamers, p.199–201)

| Augment | Slots | mQ I | mQ II | mQ III | mQ IV | Notes |
|---|---|---|---|---|---|---|
| Armored Boiler | 2 | +1 soak | +2 | +3 | +4 | stacks with Brickhouse |
| Automated Boiler Repair | 1 | repairs 1 wound/turn | 2 | 3 | 4 | |
| Brickhouse Boiler | 2 | +1 soak | +2 | +3 | +4 | |
| Fire Absorbing | 1 | fire heat damage heals instead | – | – | – | always mQ II |
| Easy Repairs | 1 | +3 on Automaton Repairs rolls | +6 | +9 | +12 | |
| Flight | 2 | fly 5 ft per AP | 10 | 15 | 25 | armor penalties apply |
| Lightning Resistant | 1 | electricity soakable | – | – | – | always mQ III |
| Passenger | 1 | enter/exit 4 AP | 3 | 2 | 1 | capacity = spaces occupied; passengers untargetable |
| Protected Core | 1 | rebuilt to 10 wounds after defeat (next breather) | 20 | 30 | 40 | |
| Realistic | 1 | +5 to fool Cunning | +10 | +15 | +20 | |
| Reinforced Boiler | 1 | +10 wounds | +20 | +30 | +40 | |
| Resilient Boiler | 1 | +10 wounds | +20 | +30 | +40 | |
| Remotely Remote Controlled | 1 | range 200 ft | 2,000 ft | 2 mi | 20 mi | |
| Shield Mode | 1 | +1 soak while hunkered | +2 | +3 | +4 | 2 AP; acts as medium cover (+6 Eva vs ranged) |
| Tactile Controls | 1 | adds operator's Dexterity | – | – | – | always mQ III |
| Test of Strength Controls | 1 | adds operator's Brute | – | – | – | always mQ II |
| Verbal Command Unit | 1 | voice control without remote | – | – | – | always mQ II; +1 AP if deafened |

**Book texts:**

**Armored Boiler** — *Boiler Augment*  
> Takes up 2 Augment Slots on a Boiler  
> Your boiler has armoring built into it so that it won’t impede your steamer in any way. This increases your steamer’s natural soak class.  
> +1 soak class  
> +2 soak class  
> +3 soak class  
> +4 soak class  
> Note: this augment stacks with the soak class bonus granted from the Brickhouse Boiler augment.  

**Automated Boiler Repair** — *Boiler Augment*  
> The boiler contains internal systems which patch up damage it recieves. While this won’t remove wound effects, every turn it will replenish some wounds damage.  
> 1 wound repaired  
> 2 wounds repaired  
> 3 wounds repaired  
> 4 wounds repaired  

**Brickhouse Boiler** — *Boiler Augment*  
> Takes up 2 Augment Slots on a Boiler  
> The walls of your boiler are exceptionally thick and well-insulated, protecting your steamer from damage.  
> +1 soak class  
> +2 soak class  
> +3 soak class  
> +4 soak class  
> Note: this augment stacks with the soak class  
> bonus granted from the Armored Boiler  
> augment.  

**Fire Absorbing** — *Boiler Augment*  
> You need heat to make steam. Your boiler can already produce heat on its own, but you’re not opposed to other people helping it out. Any heat damage your steamer would take from being on fire instead heals it.  
> Note: This augment always acts as marque II for the purposes of determining cost, though you can learn this augment despite your skill in automata.  

**Easy Repairs** — *Boiler Augment*  
> Used with the Automaton Repairs specialty  
> The automaton is designed in a logical, accessible way that makes repairs easy. Whenever somebody is attempting to repair it via the Automaton Repairs specialty, they gain a bonus on their automata roll.  
> +3 on the Automaton Repairs rolls  
> +6 on the Automaton Repairs rolls  
> +9 on the Automaton Repairs rolls  
> +12 on the Automaton Repairs rolls  

**Flight** — *Boiler Augment*  
> Takes up 2 Augment Slots on a Boiler  
> The automaton has been outfitted with a graviton sphere, allowing it to float and move. It can now fly, with its speed depending on the marque. Any speed penalties you take from armor will penalize this speed.  
> 5 feet of fly speed per action point  
> 10 feet of fly speed per action point  
> 15 feet of fly speed per action point  
> 25 feet of fly speed per action point  

**Lightning Resistant** — *Boiler Augment*  
> The automaton is naturally resistant to lightning and electricity. Electrical damage is now soakable as regular damage. Note: This augment always acts as marque III for the purposes of determining cost, though you can learn this augment despite your skill in automata.  

**Passenger** — *Boiler Augment*  
> Your automaton has a hollow compartment inside, allowing people to ride inside and see out through eye holes or monitors of your design. While inside an automaton, a character cannot be directly targeted but they in turn cannot interact with anything outside of the automaton, although the automaton can still hear all voice commands. Any remote controls for the automaton can still control it from its passenger compartment. The number of people the automaton can hold is equal to the number of spaces it takes up. The amount of action points required by passengers to get into and out of the automaton is based on the marque of this augment.  
> 4 AP to enter or exit the automaton (can take multiple turns)  
> 3 AP to enter or exit the automaton  
> 2 AP to enter or exit the automaton  
> 1 AP to enter or exit the automaton  

**Protected Core** — *Boiler Augment*  
> If your automaton is defeated in battle, its insides are heavily safeguarded to allow for easy repair during your next breather. An automaton with a protected core can be entirely rebuilt in a matter of minutes. The automaton can be repaired up to a certain amount of maximum wounds, based on the marque. It cannot be repaired past its normal maximum number of wounds  
> 10 wounds after repairs  
> 20 wounds after repairs  
> 30 wounds after repairs  
> 40 wounds after repairs  

**Realistic** — *Boiler Augment*  
> resist: Cunning (negates)  
> You’ve designed the body of your automaton to look quite real, replicating the appearance of a living or imaginary creature. Any persons who looks upon it will believe it to be real unless they can beat the automaton’s roll with their Cunning. The automaton’s roll gains a bonus based on the marque of this augment.  
> +5 to fool target  
> +10 to foot target  
> +15 to fool target  
> +20 to fool target  

**Reinforced Boiler** — *Boiler Augment*  
> The boiler is all-around better built, granting it extra points of wounds.  
> +10 wounds  
> +20 wounds  
> +30 wounds  
> +40 wounds  

**Resilient Boiler** — *Boiler Augment*  
> Your steamer has a boiler any engineer would be proud of. Durable and reliable, your steamer has extra points of wounds.  
> +10 wounds  
> +20 wounds  
> +30 wounds  
> +40 wounds  

**Remotely Remote Controlled** — *Boiler Augment*  
> The automaton can be controlled from a great distance. If the user has no way of knowing what the automaton can see, they might be wasting commands.  
> Up to 200 feet away  
> Up to 2,000 feet away  
> Up to 2 miles away  
> Up to 20 miles away  

**Shield Mode** — *Boiler Augment*  
> aCtivation Cost: 2 AP (see below)  
> Your automaton can hunker down into a solid dense mass for two of its controller’s action points, allowing it to be easily used as medium cover (+6 to evade against ranged attacks) for the same number of spaces it normally takes up. While in shield mode, your automaton cannot move or act. You can command it to exit this form for two action points. It also gains extra soak class while this ability is active.  
> +1 soak class  
> +2 soak class  
> +3 soak class  
> +4 soak class  

**Tactile Controls** — *Boiler Augment*  
> Your highly responsive control scheme allows your automaton to use your Dexterity as a bonus to its own as long as you’re are controlling it with a remote control.  
> Note: This augment always acts as marque III for the purposes of determining cost, though you can learn this augment despite your skill in automata.  

**Test Of Strength Controls** — *Boiler Augment*  
> Your steamer has been outfitted with pressurized bags of steam which inflate and deflate to replicate the amount of torque placed on the joystick of its remote control. When the person piloting your steamer is using its remote control, the steamer is able to use its operator’s Brute as a bonus onto its own.  
> Note: This augment always acts as marque II for the purposes of determining cost, though you can learn this augment despite your skill in automata.  

**Verbal Command Unit** — *Boiler Augment*  
> If your automaton has the ability to hear you, you can now issue it verbal commands without the need for a remote control. It still costs you the same amount of action points to get it to perform any action since you have to guide the automaton through every intricacy of the actions they take. The last person to give your steamer any verbal commands is considered your steamer’s current operator. If your steamer is deafened, getting it to perform an action through verbal commands costs an extra action point. Note: This augment always acts as marque II for the purposes of determining cost, though you can learn this augment despite your skill in automata.  


##### Brainworks augments (fuse boxes, p.203–205)

| Augment | Slots | mQ I | mQ II | mQ III | mQ IV | Notes |
|---|---|---|---|---|---|---|
| Alert | 1 | always alert, raises alarms | – | – | – | always mQ I |
| Brute Physics | 1 | +3 Brute | +12 | +31 | +47 | |
| Dexterity Directory | 1 | +3 Dex | +12 | +31 | +47 | |
| Easy Repairs | 1 | +3 | +6 | +9 | +12 | |
| Fuse Box Specialist | 1 | specialties use 2 skill pts | 4 | 10 | 18 | |
| Master Fuse Box (req. Specialist) | 1 | +1 | +3 | +5 | +7 | |
| Flight | 2 | fly 5 ft/AP | 10 | 15 | 20 | |
| Installed Cunning | 1 | +3 Cunning | +12 | +31 | +47 | |
| Lightning Soul | 2 | 8 electric dmg to anyone within 20 ft dealing it bleed | 16 | 24 | 32 | no evade |
| Linguistics | 0 | speaks creator's language poorly | fluently | 3 languages | 10 languages | half cost |
| Mechanical Sharpness | 1 | +2 Acc | +4 | +6 | +8 | |
| Passenger | 1 | 4 AP | 3 | 2 | 1 | |
| Protected Core | 1 | 10 wounds | 20 | 30 | 40 | |
| Realistic | 1 | +5 | +10 | +15 | +20 | |
| Scientific Database | 1 | +3 Sciences | +12 | +31 | +47 | |
| Shock Absorber | 1 | soak electric normally; soaked electricity heals HP | – | – | – | always mQ II |
| Slippery Circuits | 1 | +2 Eva | +3 | +4 | +5 | |
| Spiritual Connection (req. Personality) | 1 | +3 Spirit | +12 | +31 | +47 | |
| Targeting Program | 1 | +2 Acc | +4 | +6 | +8 | |

**Clockwork** (p.206): act only through **Directive** augments (no AP, no controller AP; immune to AP loss; directives can be toggled out of combat). Body like steamer. **0 HP, 20 wounds.** DIY → clockworks: DIY 1–5: 1 · 6–11: 2 · 12: 3. Unaugmented 50 pr (materials 10 pr).

**Book texts:**

**Alert** — *Brainworks Augment*  
> The automaton is always alert (unless when out of power or turned off), and will raise an alarm if its sensors pick up anything.  
> Note: This augment always acts as marque I for the purposes of determining cost, though you can learn this augment despite your skill in automata.  

**Brute Physics** — *Brainworks Augment*  
> Your brainworks is filled with meticulous physics calculators, allowing it to use the power of mind over matter to perform feats of incredible strength. It has a bonus to Brute.  
> +3 Brute  
> +12 Brute  
> +31 Brute  
> +47 Brute  

**Dexterity Directory** — *Brainworks Augment*  
> Your brainworks contains a vast directory of motion capture data taken from some of the world’s greatest acrobats and rogues. Whenever it needs them, your brainworks can make your automaton mimic these athletes, granting it a bonus to Dexterity.  
> +3 Dexterity  
> +12 Dexterity  
> +31 Dexterity  
> +47 Dexterity  

**Easy Repairs** — *Brainworks Augment*  
> Used with the Automaton Repairs specialty  
> The automaton is designed in a logical, accessible way that makes repairs easy. Whenever somebody is attempting to repair it via the Automaton Repairs specialty, they gain a bonus on their automata roll.  
> +3 on the Automaton Repairs rolls  
> +6 on the Automaton Repairs rolls  
> +9 on the Automaton Repairs rolls  
> +12 on the Automaton Repairs rolls  

**Fuse Box Specialist** — *Brainworks Augment*  
> Your fusebox is better at using its specialties. Instead of having  
> 1 point in their skills for using their specialties and for prerequisites, they use the following numbers:  
> 2 skill points for specialties  
> 4 skill points for specialties  
> 10 skill points for specialties  
> 18 skill points for specialties  

**Master Fuse Box** — *Brainworks Augment*  
> reQuires: fusebox augmented with Fuse Box Specialist augment Your fusebox is a master of using their specialties. They have an additional skill bonus for their specialties and for prerequisites on top of their Fusebox Specialist augment  
> +1 skill points for specialties  
> +3 skill points for specialties  
> +5 skill points for specialties  
> +7 skill points for specialties  

**Flight** — *Brainworks Augment*  
> Takes up 2 augment slots on the Brainworks  
> The automaton has been outfitted with a graviton sphere, allowing it to float and move. It can now fly, with its speed depending on the marque. Any speed penalties you take from armor will penalize this speed.  
> 5 feet of flight speed per action point  
> 10 feet of flight speed per action point  
> 15 feet of flight speed per action point  
> 20 feet of flight speed per action point  

**Installed Cunning** — *Brainworks Augment*  
> You’ve given your automaton street-smarts and wit, allowing it to analyze the words of others and its surroundings, as well as allowing it to effectively gather new information. This grants it a bonus to Cunning.  
> +3 Cunning  
> +12 Cunning  
> +31 Cunning  
> +47 Cunning  

**Lightning Soul** — *Brainworks Augment*  
> Takes up 2 augment slots on the Brainworks  
> Electricity is your fuse box’s blood, so when someone makes it bleed, they’re in for quite a shock! Whenever someone deals bleeding damage to your fuse box, including any taken from wounds or fatal effects, bolts of lightning erupt from its body into the person dealing the damage, as long as they are within 20 feet of your fusebox when dealing the damage. The victim of this augment is denied an evade roll.  
> 8 electric damage  
> 16 electric damage  
> 24 electric damage  
> 32 electric damage  

**Linguistics** — *Brainworks Augment*  
> Takes up 0 augment slots on the Brainworks  
> The automaton has learned the basics of language and, with the addition of a soundbox in its mouth, can now process and recreate language.  
> It can speak its creator’s language, though poorly It can speak its creator’s language fluently  
> It can speak three languages fluently  
> It can speak ten languages fluently  
> Note: As an augment that takes up 0 slots, the cost to apply linguistics to an automaton is half as much as a normal augment (rounded down).  

**Mechanical Sharpness** — *Brainworks Augment*  
> The fusebox can make precisely timed actions, granting it a bonus on its accuracy rolls.  
> +2 Accuracy  
> +4 Accuracy  
> +6 Accuracy  
> +8 Accuracy  

**Passenger** — *Brainworks Augment*  
> Your automaton has a hollow compartment inside, allowing people to ride inside and see out through eye holes or monitors of your design. While inside an automaton, a character cannot be directly targeted but they in turn cannot interact with anything outside of the automaton, although the automaton can still hear all voice commands. The number of people the automaton can hold is equal to the number of spaces it takes up. The amount of action points required by passengers to get into and out of the automaton is based on the marque of this augment.  
> 4 AP to enter or exit the automaton (can take multiple turns)  
> 3 AP to enter or exit the automaton  
> 2 AP to enter or exit the automaton  
> 1 AP to enter or exit the automaton  

**Protected Core** — *Brainworks Augment*  
> If your automaton is defeated in battle, its insides are heavily safeguarded to allow for easy repair during your next breather. An automaton with a protected core can be entirely rebuilt in a matter of minutes. The automaton can be repaired up to a certain amount of maximum wounds, based on the marque. It cannot be repaired past its normal maximum number of wounds  
> 10 wounds after repairs  
> 20 wounds after repairs  
> 30 wounds after repairs  
> 40 wounds after repairs  

**Realistic** — *Brainworks Augment*  
> resist: Cunning (negates)  
> You’ve designed the body of your automaton to look quite real, replicating the appearance of a living or imaginary creature. Any persons who looks upon it will believe it to be real unless they can beat the automaton’s roll with their Cunning. The automaton’s roll gains a bonus based on the marque of this augment.  
> +5 to fool target  
> +10 to foot target  
> +15 to fool target  
> +20 to fool target  

**Scientific Database** — *Brainworks Augment*  
> Your automaton is a walking library of information and has deep understanding on the inner workings of itself and other machines, granting it a bonus to Sciences.  
> +3 Sciences  
> +12 Sciences  
> +31 Sciences  
> +47 Sciences  

**Shock Absorber** — *Brainworks Augment*  
> Carefully hidden miniature conduits across your fuse box’s body allow it to soak electric damage normally, even if the electric attack states it denies soak or defense. Any electric damage it soaks is harnessed for energy, replenishing your fusebox’s hit points. Note: This augment always acts as marque II for the purposes of determining cost, though you can learn this augment despite your skill in automata.  

**Slippery Circuits** — *Brainworks Augment*  
> Your automaton always seems to slip right out from under its attackers. Its sensors are in full usage, fully optimizing the automaton for jumping away from harm. It gains a bonus of evade rolls.  
> +2 Evade  
> +3 Evade  
> +4 Evade  
> +5 Evade  

**Spiritual Connection** — *Brainworks Augment*  
> reQuires: Brainworks built with Personality  
> Your brainworks better understands what it means to be ‘alive’ and has been programmed with the mental fortitude of a monk. This allows the automaton to better replicate and control its Tephran emotions, granting it bonuses to Spirit.  
> +3 Spirit  
> +12 Spirit  
> +31 Spirit  
> +47 Spirit  

**Targeting Program** — *Brainworks Augment*  
> Your brainworks can zero in on a target, calculating the exact attack trajectory required to hit them.  
> +2 Accuracy  
> +4 Accuracy  
> +6 Accuracy  
> +8 Accuracy  


##### Analytics augments (clockworks, p.207–210)

| Augment | Slots | mQ I | mQ II | mQ III | mQ IV | Notes |
|---|---|---|---|---|---|---|
| Avenge-Me Directive | 1 | counter-attacks target's attacker 1×/turn | 2× | 2× | 3× | |
| – Hit-Them Subdirective (req. Avenge-Me) | 1 | +3 Acc | +6 | +9 | +12 | while avenging |
| – Hurt-Them Subdirective (req. Avenge-Me) | 1 | +4 Stk | +8 | +12 | +16 | |
| Defend-Your-Area Directive | 1 | attacks non-allies entering adjacent space 1×/turn | 2× | 2× | 3× | |
| – Hedge-Your-Area Subdirective | 1 | +3 Acc | +6 | +9 | +12 | |
| – Mark-Your-Area Subdirective | 1 | +4 Stk | +8 | +12 | +16 | |
| – Secure-Your-Area Subdirective | 1 | also retaliates vs adjacent attackers | – | – | – | always mQ II |
| Follow-Me Directive | 1 | follows target 1×/turn | 2× | 3× | 4× | |
| – Sprint-to-Me Subdirective | 1 | +10 ft per move | +20 | +30 | +40 | |
| – Shadow-Me Subdirective (text says req. Go-There) | 1 | +1 extra move toward target per turn | – | – | – | always mQ I |
| Go-There Directive | 1 | 1 AP (target person) to move it once | – | – | – | always mQ II |
| – March-There Subdirective | 1 | +1 additional guide | +2 | +3 | +4 | |
| – Run-There Subdirective | 1 | +5 ft | +10 | +15 | +25 | |
| Protect-Me Directive | 1 | takes damage for adjacent target 1×/turn | 2× | 3× | 4× | |
| – Protect-Us Subdirective | 1 | +1 protectee | +2 | +3 | +4 | |
| – Protect-Yourself Subdirective | 1 | +4 Def while protecting | +8 | +12 | +16 | |
| – Shield-Yourself Subdirective | 1 | +1 soak while protecting | +2 | +3 | +4 | |
| Do-Not-Die Component | 1 | +10 wounds | +20 | +30 | +40 | |
| Stay-Alive Component | 1 | +10 wounds | +20 | +30 | +40 | |
| Spring-Into-Action Component | 2 | 8 dmg to whoever makes it bleed (10 ft, no evade) | 16 | 24 | 32 | |
| Easy Repairs | 1 | +3 | +6 | +9 | +12 | |
| Flight | 2 | 5 ft/AP | 10 | 15 | 20 | |
| Lightning Resistant | 1 | electricity soakable | – | – | – | always mQ III |
| Passenger | 1 | 4 AP | 3 | 2 | 1 | |
| Protected Core | 1 | 10 | 20 | 30 | 40 | wounds after rebuild |
| Realistic | 1 | +5 | +10 | +15 | +20 | |

**Book texts:**

**Avenge-Me Directive** — *Analytics Augment*  
> Your analytical engine thoughtlessly fights back against those who try and harm the target of this augment. When applying this augment, choose someone (usually yourself) to be its target. When the target of this augment is attacked and the attacker is within range of this clockwork, the clockwork will automatically attack the attacker once, using a weapon if it is wielding one. The number of times the clockwork will do this per combat turn is determined by the marque of this augment.  
> Will perform this action once  
> Will perform this action twice  
> Will perform this action twice  
> Will perform this action thrice  

**Defend-Your-Area Directive** — *Analytics Augment*  
> Your clockwork attacks personnel who enter a space adjacent to them, exempting anyone you’ve pre-programmed them to see as an ally (usually you and any party members you don’t want your automaton to chop into pieces). They will perform this action a number of times per combat turn determined by the marque of this augment. If they are blinded to or cannot recognize someone they are pre-programmed to see as an ally, they will attack them using this augment. They will only attack a specific target once per adjacent space they walk through per turn.  
> Will act out this directive once  
> Will act out this directive twice  
> Will act out this directive twice  
> Will act out this directive thrice  

**Do-Not-Die Component** — *Analytics Augment*  
> Your clockwork is designed to take more hits before its inevitable destruction, not that it cares.  
> +10 wounds  
> +20 wounds  
> +30 wounds  
> +40 wounds  

**Easy Repairs** — *Analytics Augment*  
> Used with the Automaton Repairs specialty  
> The automaton is designed in a logical, accessible way that makes repairs easy. Whenever somebody is attempting to repair it via the Automaton Repairs specialty, they gain a bonus on their automata roll.  
> +3 on the Automaton Repairs rolls  
> +6 on the Automaton Repairs rolls  
> +9 on the Automaton Repairs rolls  
> +12 on the Automaton Repairs rolls  

**Flight** — *Analytics Augment*  
> Takes up 2 augment slots on the Brainworks  
> The automaton has been outfitted with a graviton sphere, allowing it to float and move. It can now fly, with its speed depending on the marque. Any speed penalties you take from armor will penalize this speed.  
> 5 feet of flight speed per action point  
> 10 feet of flight speed per action point  
> 15 feet of flight speed per action point  
> 20 feet of flight speed per action point  

**Follow-Me Directive** — *Analytics Augment*  
> Your clockwork will aimlessly follow the target of this augment. When applying this augment, choose someone (usually yourself) to be its target. Whenever the target of this augment moves, this clockwork will move as far as it can in the same direction, attempting to get to a space adjacent to them.  
> Will move toward their target once per turn  
> Will move toward their target twice per turn  
> Will move toward their target three times per turn Will move toward their target four times per turn  

**Go-There Directive** — *Analytics Augment*  
> aCtivation Cost: 1 AP (see below)  
> Your clockwork is programmed to move where you want it to, although its analytical engine needs guidance when doing so. When applying this augment, choose someone (usually yourself) to be its target. For 1 action point the target of this augment can, through pointing and probably yelling, make your clockwork move once. If your clockwork has a separate directive that makes it move, directing your clockwork somewhere with this augment will not prevent it from carrying out the other directive the first chance it gets.  
> Note: This augment always acts as marque II for the purposes of determining cost, though you can learn this augment despite your skill in automata.  

**Hedge-Your-Area Subdirective** — *Analytics Augment*  
> reQuires: Analytics with the Defend-Your-Area Directive augment When someone causes your automaton to act out their Defend- Your-Area Directive, your clockwork is pre-programmed to not fail its programmer. It gains an accuracy bonus on any attacks made while acting out the Defend-Your-Area Directive.  
> +3 Accuracy  
> +6 Accuracy  
> +9 Accuracy  
> +12 Accuracy  

**Hit-Them Subdirective** — *Analytics Augment*  
> reQuires: Analytics with the Avenge-Me Directive augment When your automaton acts out its Avenge-Me Directive it is accurate about doing so. It gains an accuracy bonus on any attacks made while acting out the Avenge-Me Directive.  
> +3 Accuracy  
> +6 Accuracy  
> +9 Accuracy  
> +12 Accuracy  

**Hurt-Them Subdirective** — *Analytics Augment*  
> reQuires: Analytics with the Avenge-Me Directive augment Your analytical engine is designed to mindlessly put all of its strength into dealing more damage whenever it acts out its Avenge-Me Directive. It gains a strike bonus on any attacks made while acting out the Avenge-Me Directive.  
> +4 Strike  
> +8 Strike  
> +12 Strike  
> +16 Strike  

**Lightning Resistant** — *Analytics Augment*  
> The automaton is naturally resistant to lightning and electricity. Electrical damage is now soakable as regular damage. Note: This augment always acts as marque III for the purposes of determining cost, though you can learn this augment despite your skill in automata.  

**March-There Subdirective** — *Analytics Augment*  
> reQuires: Analytics with the Go-There Directive augment More people can guide your clockwork’s aimless wandering around the battlefield. Based on the marque of this augment, you can program in more targets for your Go-There Directive. One additional guide  
> Two additional guides  
> Three additional guides  
> Four additional guides  

**Mark-Your-Area Subdirective** — *Analytics Augment*  
> reQuires: Analytics with the Defend-Your-Area Directive augment When someone causes your automaton to act out their Defend- Your-Area Directive, your clockwork is designed to make their prey regret it. It gains a strike bonus on any attacks made while acting out the Defend-Your-Area Directive.  
> +4 Strike  
> +8 Strike  
> +12 Strike  
> +16 Strike  

**Passenger** — *Analytics Augment*  
> Your automaton has a hollow compartment inside, allowing people to ride inside and see out through eye holes or monitors of your design. While inside an automaton, a character cannot be directly targeted but they in turn cannot interact with anything outside of the automaton, although the automaton can still hear all voice commands. The number of people the automaton can hold is equal to the number of spaces it takes up. The amount of action points required by passengers to get into and out of the automaton is based on the marque of this augment.  
> 4 AP to enter or exit the automaton (can take multiple turns)  
> 3 AP to enter or exit the automaton  
> 2 AP to enter or exit the automaton  
> 1 AP to enter or exit the automaton  

**Protect-Me Directive** — *Analytics Augment*  
> Your clockwork will witlessly jump in the way of attacks made against the target of this augment. When applying this augment, choose someone (usually yourself) to be its target. When adjacent to the target of this augment, this clockwork will take damage in their stead. This clockwork will only do this a certain number of times per turn determined by the marque of this augment. Will take damage instead of their target once per turn Will take damage instead of their target twice per turn Will take damage instead of their target thrice per turn Will take damage instead of their target four times per  

**Protect-Us Subdirective** — *Analytics Augment*  
> reQuires: Analytics with the Protect-Me Directive augment You can program in additional targets (usually other party members) of your automaton’s Protect-Me Directive, although they still must be adjacent to any persons they attempt to protect.  
> 1 additional protectee  
> 2 additional protectees  
> 3 additional protectees  
> 4 additional protectees  

**Protect-Yourself Subdirective** — *Analytics Augment*  
> reQuires: Analytics with the Protect-Me Directive augment When your automaton acts out its Protect-Me Directive it is better about protecting itself. It gains a defense bonus while acting out the Protect-Me Directive.  
> +4 Defense  
> +8 Defense  
> +12 Defense  
> +16 Defense  

**Protected Core** — *Analytics Augment*  
> If your automaton is defeated in battle, its insides are heavily safeguarded to allow for easy repair during your next breather. An automaton with a protected core can be entirely rebuilt in a matter of minutes. The automaton can be repaired up to a certain amount of maximum wounds, based on the marque. It cannot be repaired past its normal maximum number of wounds.  
> 10 wounds after repairs  
> 20 wounds after repairs  
> 30 wounds after repairs  
> 40 wounds after repairs  

**Realistic** — *Analytics Augment*  
> resist: Cunning (negates)  
> You’ve designed the body of your automaton to look quite real, replicating the appearance of a living or imaginary creature. Any persons who looks upon it will believe it to be real unless they can beat the automaton’s roll with their Cunning. The automaton’s roll gains a bonus based on the marque of this augment.  
> +5 to fool target  
> +10 to foot target  
> +15 to fool target  
> +20 to fool target  

**Run-There Subdirective** — *Analytics Augment*  
> reQuires: Analytics with the Go-There Directive augment While your analytical engine still has difficulties following directions, it is faster in getting to its destination once you set it on the right path. It gains a speed bonus while acting out the Go-There Directive.  
> +5 feet of movement  
> +10 feet of movement  
> +15 feet of movement  
> +25 feet of movement  

**Shadow-Me Subdirective** — *Analytics Augment*  
> reQuires: Analytics with the Go-There Directive augment Your clockwork is designed to stay beside its target no matter what. Whenever your clockwork acts out its Follow-Me Directive, it can make one additional movement towards its target per combat turn.  
> Note: This augment always acts as marque I for the purposes of determining cost, though you can learn this augment despite your skill in automata.  

**Secure-Your-Area Subdirective** — *Analytics Augment*  
> reQuires: Analytics with the Defend-Your-Area Directive augment If someone attempts to attack your automaton while already in a space adjacent to them, your automaton will spend one of its Defend-Your-Area Directive actions (if it has any available) attacking them after they finish their attack. They still will not attack anyone programmed into them as a friendly.  
> Note: This augment always acts as marque II for the purposes of determining cost, though you can learn this augment despite your skill in automata.  

**Shield-Yourself Subdirective** — *Analytics Augment*  
> reQuires: Analytics with the Protect-Me Directive augment When your automaton acts out its Protect-Me Directive it won’t take as much damage. It gains a soak class bonus while acting out the Protect-Me Directive.  
> +1 soak class  
> +2 soak class  
> +3 soak class  
> +4 soak class  

**Spring-Into-Action Component** — *Analytics Augment*  
> Takes up 2 augment slots on the Brainworks  
> You’ve made sure that anyone who attempts to damage the inner clockwork of your automaton will rue the day they do. Whenever someone deals bleeding damage to your wind-up, including any taken from wounds or fatal effects, the clockwork that springs out has been barbed and serrated and will fly in the direction of the person who dealt the damage. With a range of 10 feet, the victim of this augment is denied an evade roll.  
> 8 damage  
> 16 damage  
> 24 damage  
> 32 damage  

**Sprint-To-Me Subdirective** — *Analytics Augment*  
> reQuires: Analytics with the Follow-Me Directive augment Your clockwork’s body inanely lurches towards its target as fast as its body will allow. Your automaton can move further per movement whenever it is carrying out its Follow-Me Directive.  
> +10 feet of movement  
> +20 feet of movement  
> +30 feet of movement  
> +40 feet of movement  

**Stay-Alive Component** — *Analytics Augment*  
> You’ve built your wind-up to continue following its pre-programmed directives well past when most other automatons would have fallen on the battlefield.  
> +10 wounds  
> +20 wounds  
> +30 wounds  
> +40 wounds  


##### Prosthetics (p.211–218)
Replace a lost hand, arm or leg; only lasting penalty is the permanent wound loss from the lost limb. Wound/fatal effects apply but no bleeding out from a severed prosthetic. Arm + hand = 2 prosthetics.
DIY → prosthetics maintained: DIY 1:2, 2:3, 3:3, 4:3, 5:4, 6:4, 7:4, 8:5, 9:5, 10:5, 11:6, 12:7. Unaugmented prosthetic 25 pr (materials 5 pr). Augment price mQ I 25 / II 125 / III 625 / IV 3,125 pr; mQ I material 5 pr.

**Universal prosthetic augments**

| Augment | Slots | mQ I | mQ II | mQ III | mQ IV | Notes |
|---|---|---|---|---|---|---|
| Acid Sprayer | 1 | holds 2 acid doses | 3 | 4 | 6 | unarmed attack sprays 1 dose; refill 3 AP |
| Air Blaster | 1 | push 5 ft (25 ft range, no evade) | 5 | 10 | 15 | 1 AP; Brute resist |
| Air Conditioner (req. Air Blaster) | 1 | +2 heat/cold dmg | 4 | 6 | 8 | 1 AP toggle |
| Air Funnel (req. Air Blaster) | 1 | +5 ft range (+5 ft push) | +10 | +15 | +20 | |
| Barbed | 1 | +2 evade vs grabs on it | +4 | +6 | +8 | |
| Brute Enhancement | 1 | +2 Brute (rolls using it) | +4 | +6 | +8 | |
| Cold Iron (metal; req. Freezer) | 1 | toucher −3 resist vs heat/cold effects | −6 | −9 | −12 | until breather |
| Compartment | 1 | hidden storage (1 AP to take out) | – | – | – | always mQ I |
| Disguised | 1 | Cunning T2 to notice | T3 | T3 | T4 | organic parts +1 marque |
| Flame Exhausts (req. Furnace) | 1 | T1 fire on adjacent | T1 | T2 | T3 | 3 AP; Dex resist |
| Freeze Exhausts (req. Freezer) | 1 | adjacent −2 Eva | −4 | −6 | −8 | 3 AP; Brute resist |
| Freezer | 1 | reactivate 2 AP | 1 AP | 0 AP | 0 AP reflexive | extinguished by heat damage |
| Furnace | 1 | reactivate 2 AP | 1 | 0 | 0 reflexive | no sub-zero penalties; extinguished by water; not wood |
| Glowing | 1 | light adjacent | 10 ft | 15 ft | 20 ft | 1 AP toggle |
| Hidden Blade (req. Weapon Mounting) | 1 | retract concealable weapon for 0 AP | – | – | – | always mQ II |
| Hidden Claymore (req. Hidden Blade) | 1 | retract any weapon for 0 AP | – | – | – | always mQ III |
| Hot Iron (metal; req. Furnace) | 1 | 2 heat dmg on contact | 4 | 6 | 8 | |
| Overglow (req. Glowing) | 1 | blind 1 turn (25 ft) | 2 | 3 | 4 | 1 AP; Cunning resist |
| Poison Injector | 1 | holds 1 poison dose | 2 | 3 | 4 | unarmed attack injects; refill 3 AP |
| Precision | 1 | +2 Dex (rolls using it) | +4 | +6 | +8 | |
| Reinforced | 1 | +4 resist called shots on it | +8 | +12 | +16 | |
| Removable | 1 | remove in 4 AP | 3 | 2 | 1 | |
| Smokestack (req. Furnace or Freezer) | 1 | blinds adjacent | 10 ft | 15 ft | 20 ft | 1 AP; Cunning resist |
| Weapon Mounting | 1 | weapon can't be disarmed/sundered separately; mount 1 AP | – | – | – | always mQ I |

**Arm:** Extendable Hand (req. hand; +5/+10/+10/+15 ft reach, 1 AP to extend) · Grasper (extra pincer "hand", no two-handed use; mQ I).
**Hand:** Flame Pores (req. Furnace; 1 AP after unarmed hit: T1–T4 burns) · Freezing Pores (req. Freezer; unarmed called-shot effects last +1/+2/+3/+4 turns) · Hand-Launcher (2 AP, 50 ft, DC 3/4/5/6) · Retractable (req. Hand-Launcher; returns within 3/2/1 AP/immediately) · Neuromuscular Incapacitator (unarmed hit: none/stun 1/1/2 AP; Brute resist) · Propellers (+10/+15/+20/+25 swim).
**Leg:** Extreme Speed (+5/+5/+10/+15 speed) · Springs (+5/+10/+15/+20 ft jump height) · Propellers (+10/+15/+20/+25 swim).
**Automaton-only (need Automata Tinkerer):** Head – Sensory Transmission (broadcast senses 200 ft / 2,000 ft / 2 mi / 20 mi, 1 AP). Torso – Back-Pack (mQ I; ride on an ally's back) · Mass Propulsion (+5/+10/+15/+20 ft per move, land & flight) · Poison Gas Epicenter (2 slots; 1 AP release gas centered on it; refill 3/3/2/1 AP) · Poison Gas Receptor (req. Epicenter; holds 2/3/4/6 doses) · Sensor Array (mQ II; head augments on torso).

**Book texts:**

**Acid Sprayer** — *Universal Prosthetic Augment*  
> You can insert doses of alchemical acids into the prosthetic. When used in an unarmed attack, the body part will spray a single dose of acid onto your target. Luckily the acid is held in such a way that it will not damage your body part. Depending on the marque of this augment, your body part can hold a certain number of acid doses. It costs 3 action points to add in a single additional dose of acid.  
> Maximum of Two Doses  
> Maximum of Three Doses  
> Maximum of Four Doses  
> Maximum of Six Doses  
> Note: For the crafting of acids, see Alchemy.  

**Air Blaster** — *Universal Prosthetic Augment*  
> resist: Brute (marques down)  
> aCtivation Cost: 1 AP  
> Powerful ventilators have been built into your body part, allowing you to blow a strong, concentrated stream of pure air straight at an opponent within your 25 feet of range. They cannot evade your air blast, but they can resist with their Brute. Your target is pushed back 5 feet  
> Your target is pushed back 5 feet  
> Your target is pushed back 10 feet  
> Your target is pushed back 15 feet  

**Air Conditioner** — *Universal Prosthetic Augment*  
> reQuires: Prosthetic with the Air Blaster augment aCtivation Cost: 1 AP (see below)  
> You are able to superheat or supercool the air from your air blaster, causing it to deal either heat or freezing damage whenever you use it, in addition to its normal effects. For one action point, you can switch your air blaster between heat and freezing damage or turn the effects of this augment on and off. The damage is soakable.  
> 2 heat or freezing damage  
> 4 heat or freezing damage  
> 6 heat or freezing damage  
> 8 heat or freezing damage  

**Air Tunnel** — *Universal Prosthetic Augment*  
> reQuires: Prosthetic with the Air Blaster augment Your air blaster has been overclocked, causing its normal gust of wind to become a miniature tornado erupting from your body part. Whenever you successfully push back your target with your air blaster, they are moved an additional 5 feet backwards. In addition, this augment increases your air blaster’s range.  
> 5 additional feet of range  
> 10 additional feet of range  
> 15 additional feet of range  
> 20 additional feet of range  

**Barbed** — *Universal Prosthetic Augment*  
> You’ve laced the body part with spikes of your design. Whenever someone attempts to grab the body part, you get a bonus on your roll to avoid it.  
> +2 on the evade roll  
> +4 on the evade roll  
> +6 on the evade roll  
> +8 on the evade roll  

**Brute Enhancement** — *Universal Prosthetic Augment*  
> The body part is built for rigidity and power. When the body part is involved in a brute roll, it gains a bonus.  
> +2 to Brute  
> +4 to Brute  
> +6 to Brute  
> +8 to Brute  

**Cold Iron** — *Universal Prosthetic Augment*  
> reQuires: Body Part must be made of metal & the Freezer Augment somewhere on subject’s body  
> This prosthetic leaks small amounts of liquid nitrogen diverted from your freezer. Whenever someone comes into contact with this body part, whether it be them grabbing you or you punching them, they suffer first degree frostbite. This means they will suffer increased sensitivity to heat and cold lasting until their next breather. This augment deactivates if your freezer is extinguished. This effect will not stack with multiple exposures to a cold iron body part.  
> Target suffers a -3 when resisting effects caused by heat, flames, cold, or ice  
> Target suffers a -6 when resisting effects caused by heat, flames, cold, or ice  
> Target suffers a -9 when resisting effects caused by heat, flames, cold, or ice  
> Target suffers a -12 when resisting effects caused by heat, flames, cold, or ice  

**Compartment** — *Universal Prosthetic Augment*  
> Your prosthetic has a small hollow container inside of it, allowing the storage of different items. It costs one action point to take an item out of your compartment.  
> Note: This augment always acts as marque I for the purposes of determining cost, though you can learn this augment despite your skill in automata.  

**Disguised** — *Universal Prosthetic Augment*  
> The prosthetic is disguised as either being a regular part of the body or being covered in something so that it does not appear to be mechanical, and is built to be silent and react like a normal body part. In order to notice your prosthetic for what it truly is, opponents must roll Cunning.  
> Tier 2 Cunning to notice  
> Tier 3 Cunning to notice  
> Tier 3 Cunning to notice  
> Tier 4 Cunning to notice  
> Note: Organic body parts act one marque higher than normal. If this would make it a Marque V, the body part is indistinguishable from a normal limb unless somebody can get a Tier 5 Cunning result to notice.  

**Flame Exhausts** — *Universal Prosthetic Augment*  
> reQuires: Furnace Augment somewhere on subject’s body resist: Dexterity (marques down)  
> aCtivation Cost: 3 AP  
> Exhausts protrude from the prosthetic, flames periodically leaking out of them. For three action points you cause the body part to spray flames onto everyone adjacent to you to set them on fire, although they can still attempt to resist the attack. You cannot activate your flame exhausts if your furnace is extinguished. tier 1 Burning: 2 unsoakable damage per turn, 2 AP to put out the fire  
> tier 1 Burning: 2 unsoakable damage per turn, 2 AP to put out the fire  
> tier 2 Burning: 4 unsoakable damage per turn, 4 AP to put out the fire, wooden and cloth items destroyed tier 3 Burning: 8 unsoakable damage per turn, 8 AP to put out the fire, wooden and cloth items destroyed  

**Freeze Exhausts** — *Universal Prosthetic Augment*  
> reQuires: Freezer augment somewhere on subject’s body resist: Brute (marques down)  
> aCtivation Cost: 3 ap  
> Exhausts protrude from the prosthetic, icy mist periodically leaking out of it. For three action points you cause the body part to spray this mist onto everyone adjacent to you, although they can still attempt to resist the attack. This mist causes your target’s body temperature to rapidly drop, making them sluggish until the start of your next turn. You cannot activate your freeze exhausts if your freezer is extinguished.  
> Target suffers a -2 to evade  
> Target suffers a -4 to evade  
> Target suffers a -6 to evade  
> Target suffers a -8 to evade  

**Freezer** — *Universal Prosthetic Augment*  
> A cooler filled with liquid nitrogen has been built into your prosthetic. This keeps your body cool even in the hottest of environments. However, if the body part is hit by an attack dealing heat damage, the liquid nitrogen inside will evaporate rapidly, extinguishing your freezer. It costs 1 action point to extinguish the freezer yourself, and it will cost action points to reactivate your freezer when extinguished depending on the augment’s marque.  
> 2 AP to reactivate  
> 1 AP to reactivate  
> 0 AP to reactivate  
> 0 AP reflexively to reactivate (can do out of turn)  

**Furnace** — *Universal Prosthetic Augment*  
> Fueled by coal or aether, a live flame burns within you. It keeps your entire body warm, allowing you to take no penalties in subzero environments. If the body part gets splashed with water it will automatically extinguish the flames inside. It costs 1 action point to extinguish the furnace yourself, and it will cost action points to reactivate your furnace when extinguished depending on the augment’s marque.  
> 2 AP to reactivate  
> 1 AP to reactivate  
> 0 AP to reactivate  
> 0 AP reflexively to reactivate (can do out of turn) Note: Your furnace is self-contained and will not burn you, though you cannot apply the furnace augment to a wooden prosthetic.  

**Glowing** — *Universal Prosthetic Augment*  
> Your prosthetic shines through the darkness either from a glowin-the-dark coating, numerous lightbulbs placed in it, or another source of built-in light. Light shines outward from you, dispelling darkness and allowing those within its range to see normally. This can be activated and repressed for 1 action point. Light extends to spaces adjacent to you  
> Light extends outwards up to 10 feet away  
> Light extends outwards up to 15 feet away  
> Light extends outwards up to 20 feet away  

**Hidden Blade** — *Universal Prosthetic Augment*  
> reQuires: Prosthetic augmented with Weapon Mounting The prosthetic has a secret weapon hidden inside that can flip out at a moment’s notice. For no action point cost, you can now retract your weapon into your body, as long as the weapon would normally be concealable.  
> Note: This augment always acts as marque II for the purposes of determining cost, though you can learn this augment despite your skill in automata.  

**Hidden Claymore** — *Universal Prosthetic Augment*  
> reQuires: Prosthetic augmented with Hidden Blade The prosthetic can fit an enormous weapon inside it by breaking down its key components. For no action point cost you can now retract your weapon into your body, even if the weapon would normally not be concealable.  
> Note: This augment always acts as marque III for the purposes of determining cost, though you can learn this augment despite your skill in automata.  

**Hot Iron** — *Universal Prosthetic Augment*  
> reQuires: Prosthetic must be made of metal & the Furnace augment somewhere on subject’s body  
> As long as fire burns within your body, it constantly heats up this body part, making it burn to the touch. Whenever someone comes into contact with this body part, whether it be them grabbing you or you punching them, they take a small amount of heat damage. This doesn’t apply if your furnace is extinguished.  
> 2 heat damage  
> 4 heat damage  
> 6 heat damage  
> 8 heat damage  

**Overglow** — *Universal Prosthetic Augment*  
> reQuires: Prosthetic with the Glowing Augment  
> resist: Cunning (marques down)  
> aCtivation Cost: 1 ap  
> Light erupts from your prosthetic, arcing toward a single target within 25 feet with the potential to blind them (giving them a -4 on accuracy and evade rolls). They can resist with their cunning attribute.  
> Blinds for one turn  
> Blinds for two turns  
> Blinds for three turns  
> Blinds for four turns  

**Poison Injector** — *Universal Prosthetic Augment*  
> You can insert doses of alchemical poison into the prosthetic. When used in an unarmed attack, a single dose of the poisons held inside will automatically inject themselves into your target. Depending on the marque of this augment, your body part can hold a certain number of poison doses. It costs 3 action points to add in a single additional dose of poison.  
> Maximum of 1 Dose  
> Maximum of 2 Doses  
> Maximum of 3 Doses  
> Maximum of 4 Doses  
> Note: For the crafting of poisons, see Alchemy.  

**Precision** — *Universal Prosthetic Augment*  
> The body part is built for precision and flexibility. When the body part is involved in a Dexterity roll, it gains a bonus.  
> +2 to Dexterity  
> +4 to Dexterity  
> +6 to Dexterity  
> +8 to Dexterity  

**Reinforced** — *Universal Prosthetic Augment*  
> The prosthetic is strengthened with internal plating, granting it a resist against called shots.  
> +4 to resist when struck  
> +8 to resist when struck  
> +12 to resist when struck  
> +16 to resist when struck  

**Removable** — *Universal Prosthetic Augment*  
> The prosthetic is easily removable and replacable. If other body parts are connected to it (e.g. if this is placed on the arm, and a hand is attached to the arm) they are removed along with this body part.  
> 4 AP to remove  
> 3 AP to remove  
> 2 AP to remove  
> 1 AP to remove  

**Smokestack** — *Universal Prosthetic Augment*  
> reQuires: Furnace augment or Freezer augment somewhere on subject’s body  
> resist: Cunning (negates)  
> aCtivation Cost: 1 AP (see below)  
> A chimney or metal gratings constantly release clouds of smoke or fog from your furnace. This cloud billows out around you, making you and those within a certain range completely blinded. This will instantly end if your furnace or freezer is extinguished. You can spend one action point to start your smokescreen or to adjust the range of the cloud from affecting characters adjacent to you up to its maximum range detailed by the marque of this augment.  
> Only characters adjacent to you are blinded  
> Anyone up to 10 feet of you are blinded  
> Anyone up to 15 feet of you are blinded  
> Anyone up to 20 feet of you are blinded  

**Weapon Mounting** — *Universal Prosthetic Augment*  
> A weapon of some kind can be mounted into the prosthetic in such a way that in order to sunder or disarm the weapon, the body part itself must be sundered or removed. The weapon can be removed or put into the weapon mounting for 1 action point. Note: This augment always acts as marque I for the purposes of determining cost, though you can learn this augment despite your skill in automata.  

**Extendable Hand** — *Prosthetic Arm Augment*  
> reQuires: placed on an arm with an attached hand The hand attached to your augmented appendage can now be extended outward, whether it be with springs, hydraulics, or some other such method. It costs one action point to extend a limb but no action points to retract it. Extended hands function as normal, able to do anything they normally could do.  
> +5 feet of reach  
> +10 feet of reach  
> +10 feet of reach  
> +15 feet of reach  

**Grasper** — *Prosthetic Arm Augment*  
> A grasper is a small set of pincers that can wield an item just like a hand. A grasper is not dexterous enough to wield items in conjunction with other limbs, preventing it from being able to use two-handed items.  
> Note: This augment always acts as marque I for the purposes of determining cost, though you can learn this augment despite your skill in automata.  

**Flame Pores** — *Prosthetic Hand Augment*  
> reQuires: Furnace augment somewhere on subject’s body aCtivation Cost: 1 AP (after a successful unarmed attack) Holes in the limb make it expel flames from your furnace when it is used in an unarmed strike. As long as your furnace isn’t extinguished, you can spend 1 action point after a successful unarmed attack in order to burn your target. Multiple burns caused by your flame pores will not stack the penalties to a single target’s defense. These burns will go away during the foe’s next breather.  
> Tier 1 Burns (-1 on all defense rolls)  
> Tier 2 Burns (-3 on all defense rolls)  
> Tier 3 Burns (-5 on all defense rolls)  
> Tier 4 Burns (-7 on all defense rolls)  

**Freezing Pores** — *Prosthetic Hand Augment*  
> reQuires: Freezer augment somewhere on subject’s body aCtivation Cost: 1 AP (after a successful unarmed called shot) Holes in the limb make it expel small streams of subzero mist from your freezer which will freeze solid on impact when used in an unarmed attack. As long as your freezer isn’t extinguished, this makes unarmed called shots with this limb ice over the part of your target you hit. This ice will temporarily impede the use of extremities, making called shot effects to extremities (hands, feet, head) last longer.  
> Effects of the called shot last an additional turn Effects of the called shot last two additional turns Effects of the called shot last three additional turns Effects of the called shot last four additional turns  

**Hand-Launcher** — *Prosthetic Hand Augment*  
> aCtivation Cost: 2 AP  
> You are able to fire your hand at an opponent, dealing large amounts of damage, though you do not retain the body part if you fire it (at least until you go find it). The range of your hand is 50 feet.  
> Damage class 3  
> Damage class 4  
> Damage class 5  
> Damage class 6  

**Neuromuscular Incapacitator** — *Prosthetic Hand Augment*  
> resist: Brute (marques down)  
> An electrical current covering your body part disrupts voluntary muscular control of anyone you hit it with during an unarmed attack.  
> Your target vibrates for a second, but is otherwise fine Your target is stunned for one action point  
> Your target is stunned for one action point  
> Your target is stunned for two action points  

**Propellers** — *Prosthetic Hand Augment*  
> Your prosthetic is built with propellers for moving across water, allowing your swim speed to increase based on its marque. Your swim speed is still hindered by your armor.  
> +10 swim speed  
> +15 swim speed  
> +20 swim speed  
> +25 swim speed  

**Retractable** — *Prosthetic Hand Augment*  
> reQuires: Hand-Launcher augment applied to the hand You can have your hand tethered to a rope or chain that automatically returns to you after being fired. Though you do not have to do anything, it does take a little bit of time before the hand returns to you.  
> Returns within 3 AP  
> Returns within 2 AP  
> Returns within 1 AP  
> Returns immediately  

**Extreme Speed** — *Prosthetic Leg Augment*  
> The appendage is streamlined for speed, allowing the user to have greater overland velocity.  
> +5 speed  
> +5 speed  
> +10 speed  
> +15 speed  

**Springs** — *Prosthetic Leg Augment*  
> By melding high-tension springs into your graft, its user gains extra height whenever jumping or leaping.  
> +5 feet jump height  
> +10 feet jump height  
> +15 feet jump height  
> +20 feet jump height  

**Propellers** — *Prosthetic Leg Augment*  
> Your prosthetic is built with propellers for moving across water, allowing your swim speed to increase based on its marque. Your swim speed is still hindered by your armor.  
> +10 swim speed  
> +15 swim speed  
> +20 swim speed  
> +25 swim speed  
> Automaton-Specific  
> While all prosthetic augments can be applied to automatons, the following augments (which would augment an automaton’s head, torso, or groin) cannot be applied to living people. Thus, these are automaton-specific augments that you’ll need the Automaton Tinkerer specialty for.  

**Sensory Transmission** — *Automaton Head Augment*  
> The automaton can broadcast its senses to a single device (often held by the user) for 1 action point. The distance it can broadcast is determined by the marque of the augment.  
> Up to 200 feet away  
> Up to 2,000 feet away  
> Up to 2 miles away  
> Up to 20 miles away  

**Back-Pack** — *Automaton Torso Augment*  
> The automaton has the ability to latch onto an ally’s back, acting as the ally’s backpack. This leaves all of the automaton’s limbs free to act as normal while the ally carries the automaton around. The automaton cannot move while being carried. It takes 1 turn for the automaton to become a back-pack or unpack itself and move under its own power again.  
> Note: This augment always acts as marque I for the purposes of determining cost, though you can learn this augment despite your skill in automata.  

**Mass Propulsion** — *Automaton Torso Augment*  
> Using a propeller, steamjet, or some other such device attached to the torso’s back, your subject is able to increase their thrust while moving. While this cannot give you the ability to fly, it grants bonuses to both land and flight movement speeds.  
> +5 feet per move  
> +10 feet per move  
> +15 feet per move  
> +20 feet per move  

**Poison Gas Epicenter** — *Automaton Torso Augment*  
> Takes up 2 Augment Slots on the Torso  
> aCtivation Cost: 1 AP  
> You can insert a single vial of alchemical gas into the automaton’s torso. Once you activate this augment, the gas starts taking effect. When you end your turn, the gas releases from the automaton’s torso, affecting those around the automaton. This allows the automaton to move the gas around the battlefield. The automaton serves as the center of the gas’s area of effect, although through clever crafting the automaton doesn’t have to worry about the gas spraying onto itself. The gas lasts as long as it normally would. The amount of action points required to refill the gas supply is based off of the marque of this augment. It costs two action points to eject a dose of gas before it has run out on its own. This will cause it to stay in the space the automaton is currently standing in and will no longer move with the automaton.  
> 3 AP to refill gas chamber  
> 3 AP to refill gas chamber  
> 2 AP to refill gas chamber  
> 1 AP to refill gas chamber  
> Note: For the crafting of gases, see Alchemy.  

**Poison Gas Receptor** — *Automaton Torso Augment*  
> reQuires: Torso with the Poison Gas Epicenter augment You’ve upgraded your gas dispenser to hold extra doses of alchemical gases. You still can only release one gas at a time. Maximum of Two Doses  
> Maximum of Three Doses  
> Maximum of Four Doses  
> Maximum of Six Doses  

**Sensor Array** — *Automaton Torso Augment*  
> You’ve crafted a sensor array into your automaton’s torso. This allows you to place automaton head augments on the torso as well as the ability for the automaton to see and hear through its torso.  
> Note: This augment always acts as marque II for the purposes of determining cost, though you can learn this augment despite your skill in automata.  




#### Bio-Flux

| Specialty | Group | Bonuses | Cost / type | Requires | Effect | Tags |
|---|---|---|---|---|---|---|
| **Bio-Invigoration** | Invigoration | Eva +1, Def +3, HP +8 | 3 AP |  | Cost: 3 AP<br>You’ve crafted a complex light device called a bio-invigorator. This can be worn on any called shot location to avoid having to hold it while it’s drawn. You can restore hit points during combat by treating your allies. If you use invigorate on an ally, you must be adjacent to them.<br>You can treat yourself, but you can only heal half as many of your own hit points as you would if you were healing another person. You cannot use Bio-Invigoration to restore hit points to an automaton or other nonliving being. restores 6 hit points (3 of your own)<br>restores 12 hit points (6 of your own)<br>restores 18 hit points (9 of your own)<br>restores 24 hit points (12 of your own) | [ACTION] |
| **Bio-Invigoration Expert** | Invigoration | Eva +1, Pri +3, HP +9 | Passive | Bio-Invigoration | reQuires: Bio-Invigoration specialty<br>You optimize your bio-invigorator. When you use bio-invigoration, you now restore hit points based on this chart: restores 10 hit points (5 of your own)<br>restores 20 hit points (10 of your own)<br>restores 30 hit points (15 of your own)<br>restores 40 hit points (20 of your own) | [COND] [REQ] |
| **Quickshot Bio-Invigoration** | Invigoration | Eva +1, Spd +5, HP +8 | Passive | Bio-Invigoration | reQuires: Bio-Invigoration specialty<br>Cost: 2 AP<br>Combat doesn’t wait for the slow bio-invigorator. You may now use bio-invigoration for only 2 action points. | [PASSIVE] [REQ] |
| **Medical Marvel** | Invigoration | Eva +1, Wnd +1, HP +11 | Passive | Bio-Invigoration | reQuires: Bio-Invigoration specialty<br>You can heal beyond a person’s maximum hit points. If you overheal somebody, the excess hit points stays with them until the end of their turn (when their action points refresh). If their excess hit points are damaged, then that damage is simply negated. For example, you use bio-invigoration on a friend who has a maximum of 50 hit points. He is over-healed, granting him<br>5 extra hit points. Before the end of his next turn, he is stabbed by an attack that deals 4 hit points, leaving him at 51. His turn ends, and his hit points are reduced to 50, effectively leaving him unharmed. | [COND] [REQ] |
| **Self-Administer** | Invigoration | Acc +1, Eva +1, HP +11 | Passive | Bio-Invigoration | reQuires: Bio-Invigoration specialty<br>Though the bio-invigorator was originally difficult to use on yourself, you’ve outfitted it to work on yourself efficiently. When you use bio-invigoration on yourself, you heal just as much as you would restore of another’s hit points. | [PASSIVE] [REQ] |
| **Manipulate Essence** | Essence Manipulation | Aug +2, DIY +1, HP +6 | Passive (crafting, downtime) |  | You have gained the knowledge and skill to manipulate a creature’s essence. Using a bit of pure base essence, you are able to modify genetics during downtime.<br>Without spending any money, you can maintain several people with essence manipulations based on your current Do-It- Yourself (DIY) score. You’ll learn 2 augments from this specialty, which can be selected under “essence augments” below. These augments have marques. At lower levels, you’ll start with Marque I augments. As your skill in Bio-Flux improves, your marques will increase. See the “Crafting” page at the beginning of this chapter for more information.<br>Every person can be upgraded with 3 essence manipulations. Sometimes an augment will take up multiple augment slots. For example, the “regeneration” augment is worth 2 slots, so a person only has 1 more available slot for an augment after “regeneration” has been applied.<br>You have the ability to remove essence augments off of people during downtime as well.<br>numBer oF augmenteD peopLe you Can maintain<br>Without needing to buy workshop space or essence, you can manipulate a few people without spending anything. These people must be constantly maintained by you and their essence reverts back to normal soon after leaving your care, thus losing all of their augments. You may manipulate and maintain a number of people based on your DIY score. You may manipulate or re-augment people during any period of downtime you have. your Diy: 1 2 3 4 5 6<br>you Can BuiLD: 2 2 3 3 3 3<br>your Diy: 7 8 9 10 11 12<br>you Can BuiLD: 3 4 4 4 4 5<br>the Cost oF essenCe manipuLations<br>Essence is a volatile and often illegal substance. Bio-flux specialists are ostracized from their community and their manipulations only carried out in the black market. Because of that, the Trust (the world’s economic caretaker) does not regulate the cost of essence manipulations. Nonetheless, an essence manipulator will still need to pay for the materials of an essence manipulation they choose to do. They can, however, get away with charging whatever they’d like for the actual manipulation.<br>If you need to manipulate essence that you can’t do for free from your DIY score, you will need to buy the materials for it. Every augment increases the market price of the essence manipulation. The higher the marque, the greater the price. The market price for an augment can be found in the chart below. marQue I II III IV<br>market priCe 50 princes 250 princes 1250 princes 6250 princes If you are manipulating the augment, you pay 1/5th the price, which is the same as if you were buying an augment one marque lower. (As in, the material cost for a Marque III augment is the market price fo a Marque II augment.) The material cost for a Marque 1 augment is 10 princes. | [AUG] [DIY] [CRAFT:essence] |
| **Beta Essence** | Essence Manipulation | Aug +2, DIY +1, HP +6 | Passive | 4 Bio-Flux; Manipulate Essence | reQuires: 4 skill points in Bio-Flux & Manipulate Essence specialty You know your own essence well enough to safely twist it and strengthen it enough to add additional modification onto it. You may now act as though your essence have two additional slots. | [CRAFT] [REQ] [STAT:own essence slots +2] |
| **Prototype Essence** | Essence Manipulation | Aug +2, DIY +1, HP +6 | Passive | 16 Bio-Flux; Manipulate Essence; Beta Essence | reQuires: 16 skill points in Bio-Flux, Manipulate Essence, & Beta Essence specialties<br>You are now able to manipulate other creatures as well as you manipulate yourself. You may now treat other creatures as though they had 2 additional slots when manipulating their essence. | [CRAFT] [REQ] |
| **Fast Manipulation** | Essence Manipulation | Eva +1, Aug +2, HP +7 | 3 AP; resist Spirit (negates) | 6 Bio-Flux; Manipulate Essence | reQuires: 6 skill points in Bio-Flux & Manipulate Essence specialty resist: Spirit (negates)<br>Cost: 3 AP<br>You are able to use advanced tools in order to quickly manipulate essence on the battlefield. However, because of the haste of these manipulations, they only last until the subject’s next breather. If the subject so chooses, they may roll a spirit resist against your bio-flux to negate the manipulation. | [ACTION] [REQ] |
| **Body Renewal** | Essence Manipulation | Def +2, Aug +1, HP +9 | 3 AP | Manipulate Essence | reQuires: Manipulate Essence specialty<br>Cost: 3 AP<br>By applying just the right amount of essence to a wounded area, you are able to trigger a muscle memory that reverts the subject’s body back to an undamaged state. You may spend 3 action points to heal your subject of one wound point or one effect caused from them (broken bones, blinded, lost senses, et cetera). | [ACTION] [REQ] |
| **Gene Therapy** | Essence Manipulation | Aug +2, Wnd +1, HP +9 | Once per downtime | 16 Bio-Flux; Manipulate Essence; Body Renewal | reQuires: 16 skill points in Bio-Flux, Manipulate Essence, & Body Renewal specialties<br>You force a living subject’s body to painfully regrow a severed body part or critically injured body part. Once per downtime, you are able to remove a lasting Fatal Effect from your subject. | [ACTION] [REQ] |
| **Bio-Zapper Developer** | Crafting Bio-Zappers | Aug +2, DIY +1, HP +4 | Passive (crafting) |  | You can now create the battle-ready, essence-manipulating biozapper and use it in battle.<br>Without spending any money, you can build and maintain several bio-zappers based on your current Do-It-Yourself (DIY) score. These bio-zappers can then be upgraded with augments. You’ll learn 2 augments from this specialty, which can be selected under “bio-zapper augments” below. These augments have marques. At lower levels, you’ll start with Marque I augments. As your skill in Bio-Flux improves, your marques will increase. See the “Crafting” page at the beginning of this chapter for more information.<br>Each bio-zapper can be upgraded with 3 augments. Some materials can only be upgraded twice (like wooden biozappers) or just once (like organic bio-zappers). Sometimes an augment will take up multiple augment slots. If an augment is worth 2 slots, a metal bio-zapper only has 1 more available slot for an augment after the 2-slot augment has been applied. Bio-zapper augments come in two varieties: those that augment the bio-zapper (like normal) and bio-zapper settings. Only one setting can be active at a time, and switching between settings costs 1 action point.<br>numBer oF Bio-zappers you Can maintain<br>Without needing to buy pieces or parts, you can develop some bio-zappers entirely out of scraps. These bio-zappers must be constantly maintained by you and stop working soon after leaving your care. You may build and maintain a number of bio-zappers based on your DIY score. You may build new bio-zappers or augment old ones during any period of downtime you have. your Diy: 1 2 3 4 5 6<br>you Can BuiLD: 1 1 1 1 2 2<br>your Diy: 7 8 9 10 11 12<br>you Can BuiLD: 2 3 3 3 3 4<br>o-Zappers<br>a way to affect somebody’s essence in a matter of seconds rs came about: a device that vaguely resembles a gun, but e change doesn’t last very long, but, in a battle, it definitely looks like an advanced firearm. You point it at somebody sting 2 action points). You roll your accuracy and they roll ith the bio-zapper.<br>setting, the bio-zapper does nothing). The effect will last your bio-zapper in order to gain different effects. Switching th a new bio-zapper setting, the new effect replaces the old the Cost oF Bio-zappers<br>If you need to build a bio-zapper that you can’t build for free from your DIY score, you will need to buy the materials for it. Every augment increases the market price of the biozapper. The higher the marque, the greater the price. The market price for an augment can be found in the chart below. marQue I II III IV<br>market priCe 40 princes 200 princes 1000 princes 5000 princes If you are building the augment, you pay 1/5th the price, which is the same as if you were buying an augment one marque lower. (As in, the material cost for a Marque III augment is the market price fo a Marque II augment.) The material cost for a Marque 1 augment is 8 princes. | [AUG] [DIY] [CRAFT:biozapper] |
| **Beta Bio-Zappers** | Crafting Bio-Zappers | Aug +2, DIY +1, HP +4 | Passive | 4 Bio-Flux; Bio-Zapper Developer | reQuires: 4 skill points in Bio-Flux & Bio-Zapper Developer specialty Your bio-zappers are complex pieces of machinery, but they can do some crazy things compared to most bio-zappers. Such biozappers can be upgraded with 2 more augments (bringing the total for metal bio-zappers up to 5 augmentable slots). If anybody other than you attempts to use one of your beta bio-zappers, they must succeed in rolling a sciences result one tier higher than the highest marque you have on your biozapper. If your bio-zapper has a Marque IV augment, it is impossible for them to use it (unless they can somehow obtain a tier result of 5 with their sciences attribute). | [CRAFT] [REQ] |
| **Prototype Bio-Zappers** | Crafting Bio-Zappers | Aug +1, DIY +1, HP +4 | Passive | 16 Bio-Flux; Bio-Zapper Developer; Beta Bio-Zappers | reQuires: 16 skill points in Bio-Flux, Bio-Zapper Developer, & Beta Bio-Zappers specialties<br>You’ve perfected your beta bio-zappers and made them userfriendly. Now anybody can use a bio-zapper that you designate as being a prototype. | [CRAFT] [REQ] |
| **Concentrated Stream** | Crafting Bio-Zappers | Acc +1, Aug +2, HP +6 | Bio-zapper attack, then 1 AP/turn |  | Cost: Bio-Zapper Attack to initiate and 1 AP to continue in subsequent turns<br>You lock your weapon onto your target, pull the trigger, and don’t let go. After successfully hitting a target with a bio-zapper, all subsequent attacks with that bio-zapper automatically hit. You must spend one action point each turn to continue your ray. If at any point you do not have a clear line of site to your target or either of you moves out of the range of the bio-zapper, this effect is broken. | [ACTION] |
| **Extra Settings** | Crafting Bio-Zappers | Aug +2, DIY +1, HP +4 | Passive |  | Your bio-zappers are designed to hold extra settings, effectively giving you extra augment slots to place bio-zapper settings into. This specialty works within the marque system. The amount of interchangeable slots the bio-zapper has depends on the marque of its developer. Each extra augment slot increases the price, just like normal, but only a person with this specialty can access the extra settings.<br>1 extra augment slot of a setting<br>2 extra augment slost of a setting<br>3 extra augment slots of a setting<br>4 extra augment slots of a setting | [CRAFT] [SCALE:marque] |
| **Multi-Ray** | Crafting Bio-Zappers | Acc +1, Aug +1, HP +6 | Bio-zapper attack +1 AP |  | Cost: Bio-Zapper Attack +1 AP<br>By double tapping your trigger finger, you are able to quickly launch off two rays. These rays may be launched at different targets. | [ATTACK+1] |
| **Splicer** | Crafting Bio-Zappers | Acc +1, Aug +1, HP +6 | Passive |  | Your bio-zapper settings don’t replace each other; now, they overlap! When you hit an opponent with two different settings, they both affect the target until the target’s next breather. (If you hit the same target with the same setting twice, there’s no effect.) | [PASSIVE] |
| **Tracing** | Crafting Bio-Zappers | Acc +1, Aug +1, HP +7 | Bio-zapper attack +1 AP |  | Cost: Bio-Zapper Attack +1 AP<br>You hold down the button on you bio-zapper, sending a ray arching across the battlefield. Then you move your bio-zapper’s ray until you hit the target, radically increasing its accuracy and your chances of your hitting your target.<br>+4 accuracy<br>+8 accuracy<br>+12 accuracy<br>+16 accuracy | [ATTACK+1] |

##### Bio-Flux – crafting tables (p.220–233)
Pure essence is illegal/black-market; the Trust doesn't regulate prices.
DIY → people maintained with essence augments: DIY 1:2, 2:2, 3:3, 4:3, 5:3, 6:3, 7:3, 8:4, 9:4, 10:4, 11:4, 12:5.
DIY → bio-zappers: DIY 1–4: 1 · 5–7: 2 · 8–11: 3 · 12: 4.
Price per augment: essence mQ I 50 / II 250 / III 1,250 / IV 6,250 pr (mQ I material 10 pr); bio-zapper mQ I 40 / 200 / 1,000 / 5,000 pr (mQ I material 8 pr).

##### Essence augments (on a person; p.222–226) — these directly modify character values

| Augment | Slots | mQ I | mQ II | mQ III | mQ IV | Tool tags |
|---|---|---|---|---|---|---|
| Aerodynamize | 1 | +5 speed | +10 | +10 | +15 | `[STAT:Spd]` |
| Acidic Blood | 1 | melee attacker causing your bleeding takes equal soakable damage | – | – | – | always mQ III |
| Acidic Spit | 1 | 1 AP ranged spit, 10 ft, DC 1 (Strike) | DC 2 | DC 3 | DC 4 | `[GEAR]` natural weapon |
| Amphibious | 1 | breathe underwater | – | – | – | always mQ II |
| Body of Flames | 1 | grabbed/grabbing victims 1 heat/turn | 2 | 3 | 4 | |
| Chameleon | 1 | +2 Cunning hiding (unclothed)/disguise | +4 | +6 | +8 | 1 AP to change |
| Chloroplast | 1 | survive on sunlight & water | – | – | – | always mQ III |
| Electric Flow | 1 | defend vs electricity normally | – | – | – | always mQ II |
| Energize | 1 | **+3 HP** | +6 | +9 | +12 | `[STAT:HP]` |
| Excess Adrenaline | 3 | gain 1 extra AP (stunned equally next refresh) | up to 2 | 2 | 3 | |
| Exoskeleton | 1 | +2 Brute vs called shots | +4 | +6 | +8 | `[COND]` |
| Flame Retardant | 1 | +2 soak vs fire, never denied defense on fire | +3 | +4 | +5 | `[COND]` |
| Flaming Breath | 1 | 2 AP ranged, 10 ft, DC 3 (Strike) | DC 4 | DC 5 | DC 6 | `[GEAR]` |
| Genetic Stability | 1 | +4 resist bio-zappers; negates cosmetic changes | +8 | +12 | +16 | |
| Iron Lung | 1 | +4 Brute vs inhaled things | +8 | +12 | +16 | |
| Jellyskin | 1 | +3 disguise | +5 | +7 | +9 | dents when hit |
| Lead Blood | 1 | blood as ammo at −3 Acc | −2 | −1 | 0 | |
| Limitless Memory | 1 | **+3 Sciences attribute** | +6 | +9 | +12 | `[STAT:Sciences]` |
| Luminescent | 1 | light adjacent | 10 ft | 15 ft | 20 ft | |
| Marathon Body | 1 | **+1 max wounds** | +2 | +3 | +4 | `[STAT:Wnd]` |
| Metal Exoskeleton (req. Exoskeleton) | 1 | armor you're wearing stays active even if broken or destroyed (grants no armor itself) | – | – | – | always mQ III |
| Needles | 1 | throw needles (light throwing attack, DC 3), 10 ft | 15 | 20 | 25 | no draw needed |
| Nobotic | 1 | +5 Cunning to pass as a robot | +10 | +15 | +20 | |
| Osmote (req. Jellyskin) | 1 | grabbed/grappled foe takes 2 unsoakable/turn | 3 | 4 | 5 | |
| Overflow | 1 | +2 on all Spirit resists | +4 | +6 | +8 | `[COND]` |
| Performance Enhancer | 1 | **+1 Brute** | +2 | +3 | +4 | `[STAT:Brute]` |
| Regeneration | 2 | +1 wound recovered/day; wound effects heal 2× faster | +2 | +3 | +4 | |
| Scaleskin | 2 | **+1 soak class** (natural) | +2 | +3 | +4 | `[STAT:Soak]` |
| Scoped Vision | 1 | +4 Notice | +8 | +12 | +16 | `[COND]` |
| Semi-Transparent Skin | 1 | +4 for others diagnosing you | +8 | +12 | +16 | |
| Sixth Sense | 1 | **+2 Priority** | +4 | +6 | +8 | `[STAT:Pri]` |
| Sleepless | 1 | no sleep needed | – | – | – | always mQ III |
| Slimy | 1 | +4 Dex to break grabs | +8 | +12 | +16 | |
| Stonebones | 1 | limbs can't be severed/broken; −10 speed | −10 | −5 | 0 | `[STAT:Spd]` |
| Vile Fumes | 1 | 3 AP: adjacent T2 Brute or disoriented 1 turn | T3 | T3 | T4 | |
| Wall-Crawler | 1 | climb walls & ceilings at normal speed | – | – | – | always mQ III |

**Book texts:**

**Aerodynamize** — *Essence Augment*  
> Your body and features become sleek and slender with curved edges so the wind will always flow with your movements.  
> +5 movement speed  
> +10 movement speed  
> +10 movement speed  
> +15 movement speed  

**Acidic Blood** — *Essence Augment*  
> The blood within your veins is now dark and corrosive. This highlights your veins, making them dark and easily visible. When you recieve bleeding damage from a melee attack, the person inflicting the damage suffers an equal amount of soakable damage from being sprayed by your blood as long as they are adjacent to you.  
> Note: This augment always acts as marque III for the purposes of determining cost, though you can learn this augment despite your skill in bio-flux.  

**Acidic Spit** — *Essence Augment*  
> Cost: 1 AP  
> Your saliva has been changed to become tar-like and acidic. For  
> 1 action point, you can make a ranged attack using your acidic saliva. This attack has a range of 10 feet and uses strike to determine damage.  
> damage class 1  
> damage class 2  
> damage class 3  
> damage class 4  

**Amphibious** — *Essence Augment*  
> You sprout gills and your lungs gain the ability to extract oxygen from water naturally. You can now breathe while underwater. Note: This augment always acts as marque II for the purposes of determining cost, though you can learn this augment despite your skill in bio-flux.  

**Body Of Flames** — *Essence Augment*  
> The skin on your body is unnaturally warm to the touch, to the point that it slightly burns those who touch you. This causes your skin to have a slight red tinge and your hair to lighten. When being grabbed or grabbing, victims take 1 heat damage per turn  
> When being grabbed or grabbing, victims take 2 heat damage per turn  
> When being grabbed or grabbing, victims take 3 heat damage per turn  
> When being grabbed or grabbing, victims take 4 heat damage per turn  

**Chameleon** — *Essence Augment*  
> Cost: 1 AP (see below)  
> Much like the scales of a lizard, you are able to change both the color and texture of your skin and hair. For one action point you may undergo this change.  
> +2 to Cunning rolls when hiding without clothing or disguising yourself  
> +4 to Cunning rolls when hiding without clothing or disguising yourself  
> +6 to Cunning rolls when hiding without clothing or disguising yourself  
> +8 to Cunning rolls when hiding without clothing or disguising yourself  

**Chloroplast** — *Essence Augment*  
> You are able to survive with only a bit of sunlight and water due to large amounts of chloroplasts in your cells. Unfortunately it’s not easy being green, as your appearance becomes splotched with patches of green skin.  
> Note: This augment always acts as marque III for the purposes of determining cost, though you can learn this augment despite your skill in bio-flux.  

**Electric Flow** — *Essence Augment*  
> Thin strains of static electricity flow across your body. When attacked by electricity, these strains help dissipate the electricity, allowing you to defend against electrical attacks as per normal. Note: This augment always acts as marque II for the purposes of determining cost.  

**Energize** — *Essence Augment*  
> Your body chemistry has been modified to grant you a seemingly endless supply of energy. Because of this you rarely feel tired and always shake when sitting still.  
> +3 hit points  
> +6 hit points  
> +9 hit points  
> +12 hit points  

**Excess Adrenaline** — *Essence Augment*  
> takes up 3 essenCe sLots on a person  
> Your body has been modified to produce and use twice the amount of adrenaline of a normal being. While this does speed you up temporarily, it exhausts you immediately afterwards. You are able to gain additional action points during a turn; however, you are stunned for an equal number of action points when your action points refresh. In other words, you’re stealing action points away from your next turn.  
> You can gain 1 action point  
> You can gain up to 2 action points  
> You can gain up to 2 action points  
> You can gain up to 3 action points  

**Exoskeleton** — *Essence Augment*  
> Your bones thicken and elongate, some slightly jutting out of your body. This makes them harder to damage and even more difficult to break.  
> +2 to Brute when resisting a called shot  
> +4 to Brute when resisting a called shot  
> +6 to Brute when resisting a called shot  
> +8 to Brute when resisting a called shot  

**Flame Retardant** — *Essence Augment*  
> Your skin becomes a darkened charcoal color that is less likely to ignite or burn. You are never denied your defense roll when on fire. You also gain extra soak against damage from being on fire and any other damage from fire.  
> You gain a +2 soak against fire  
> You gain a +3 soak against fire  
> You gain a +4 soak against fire  
> You gain a +5 soak against fire  

**Flaming Breath** — *Essence Augment*  
> Cost: 2 AP  
> You’ve grown an extra gland in your thoat that allows you to expel flames from your mouth. For 2 action points, you may make a ranged attack using your fiery saliva. This attack has a range of  
> 10 feet, and uses strike to determine damage.  
> damage class 3  
> damage class 4  
> damage class 5  
> damage class 6  

**Genetic Stability** — *Essence Augment*  
> Your essence has been solidified to a point that bio-fluxing your essence is a gruelling, painful ordeal. This augment negates any cosmetic changes caused by other augments your essence has.  
> +4 when resisting a Bio-Zapper  
> +8 when resisting a Bio-Zapper  
> +12 when resisting a Bio-Zapper  
> +16 when resisting a Bio-Zapper  

**Iron Lung** — *Essence Augment*  
> Your lungs have adapted to filter anything you breathe in, allowing you to breathe normally even when surrounded by noxious gases.  
> +4 to Brute when resisting anything you inhale  
> +8 to Brute when resisting anything you inhale  
> +12 to Brute when resisting anything you inhale  
> +16 to Brute when resisting anything you inhale  

**Jellyskin** — *Essence Augment*  
> Your skin is exceptionally flexible and holds shape when you move it, allowing you to change the structure of your face more easily. Any time you are attempting to disguise yourself, you may gain a bonus to your roll. However, when you are nudged, punched, or attacked, your face retains dents until you can fix your appearance.  
> +3  
> +5  
> +7  
> +9  

**Lead Blood** — *Essence Augment*  
> Your blood is made of molten metal, solidifying into small pellets after leaving your body. Drops of your blood can thus be used as crude ammunition for firearms. It causes you no damage and costs no action points to bleed out bullets, although your firearm must still be readied with them.  
> -3 Accuracy when used as ammo  
> -2 Accuracy when used as ammo  
> -1 Accuracy when used as ammo  
> No accuracy penalty when used as ammo  

**Limitless Memory** — *Essence Augment*  
> Small flashing lights coming from the inside of your head skitter across your crown, a visible sign of the massive amount of information processing going on inside the left side of your brain.  
> +3 to the Sciences attribute  
> +6 to the Sciences attribute  
> +9 to the Sciences attribute  
> +12 to the Sciences attribute  

**Luminescent** — *Essence Augment*  
> You cause your essence to radiate light, making your entire body glow. This light extends only so far.  
> It lights the area adjacent to you  
> It lights up the area 10 feet around you  
> It lights up the area 15 feet around you  
> It lights up the area 20 feet around you  

**Marathon Body** — *Essence Augment*  
> Your body has been enriched to take a beating. This change has made you thick and stocky.  
> Your maximum number of wounds is increased by 1  
> Your maximum number of wounds is increased by 2  
> Your maximum number of wounds is increased by 3  
> Your maximum number of wounds is increased by 4  

**Metal Exoskeleton** — *Essence Augment*  
> reQuires: Exoskeleton augment  
> Your exoskeleton is made of natural metal armoring, weighing you down but acting as a natural kind of armor. You may act as if you were wearing any kind of armor on your body permanently, so if you armor is broken or destroyed, you still act as if you are wearing armor.  
> Note: This augment always acts as marque III for the purposes of determining cost, though you can learn this augment despite your skill in bio-flux.  

**Needles** — *Essence Augment*  
> Cost: same as a Light Throwing Weapon attack (generally 2 AP) Small porcupine needles quickly grow out of your body. You can throw some of your needles at a single target with a damage class of 3 without the need to be drawn.  
> 10 feet of range  
> 15 feet of range  
> 20 feet of range  
> 25 feet of range  

**Nobotic** — *Essence Augment*  
> resist: Cunning (see below)  
> Your body appears to be made out of metal, making you appear to be some kind of robot when you aren’t. You gain a bonus to Cunning against anyone using Notice on you when you’re trying to hide the fact that you’re an organic being.  
> +5, your body appears to be metallic  
> +10, your metallic body is angular and disproportionate  
> +15, your metallic body appears to be made of separate parts bolted together  
> +20, your metallic body looks machine-made with soulless eyes, emitting clear water vapor instead of sweat  

**Osmote** — *Essence Augment*  
> reQuires: Jellyskin augment  
> Your body is capable of actually absorbing the body of an opponent. When you successfully grapple or grab an opponent, your skin sinks through their armor and they automatically begin to take unsoakable damage. Your body is partially transparent and your solid organs bend like rubber. When you absorb organic material, it counts as eating.  
> 2 unsoakable damage per turn  
> 3 unsoakable damage per turn  
> 4 unsoakable damage per turn  
> 5 unsoakable damage per turn  

**Overflow** — *Essence Augment*  
> Your skin tone, regardless of its color, takes on a more vibrant, healthy shade than it previously had. You find it increasingly easy to focus and feel more in tune with yourself.  
> +2 on all spirit resists  
> +4 on all spirit resists  
> +6 on all spirit resists  
> +8 on all spirit resists  

**Performance Enhancer** — *Essence Augment*  
> You instantly swell with muscles all over your body, feeling stronger than usual.  
> +1 Brute  
> +2 Brute  
> +3 Brute  
> +4 Brute  

**Regeneration** — *Essence Augment*  
> takes up 2 essenCe sLots on a person  
> Your body has been modified to heal at a much faster rate than normal. The areas where you’ve taken wounds damage now have yellow skin blemishes. Along with this accelerated wound recovery, lingering wound effects are removed twice as fast. You recover 1 additional wound per day  
> You recover 2 additional wounds per day  
> You recover 3 additional wounds per day  
> You recover 4 additional wounds per day  

**Scaleskin** — *Essence Augment*  
> takes up 2 essenCe sLots on a person  
> Your skin mutates into thick scales, the outer layer of your grafts taking on a bumpy texture. This gives you a small amount of natural armoring.  
> +1 soak class  
> +2 soak class  
> +3 soak class  
> +4 soak class  

**Scoped Vision** — *Essence Augment*  
> This modification manipulates your browline, making it more narrow and focused. Your vision is radically enhanced granting, you the ability to see things others often overlook.  
> +4 to Notice  
> +8 to Notice  
> +12 to Notice  
> +16 to Notice  

**Semi-Transparent Skin** — *Essence Augment*  
> While making your skin partially see-through to reveal the inner workings of your body is horrifying to most, this serves as a useful tool for doctors trying to figure out what ails their patient. When being diagnosed, the person performing the diagnosis gains a bonus on their roll.  
> +4 to being diagnosed  
> +8 to being diagnosed  
> +12 to being diagnosed  
> +16 to being diagnosed  

**Sixth Sense** — *Essence Augment*  
> The frontal lobe of your brain has been enlarged, giving you the ability to sense impending danger. This change in your brain chemistry causes you to have frequent headaches.  
> +2 priority  
> +4 priority  
> +6 priority  
> +8 priority  

**Sleepless** — *Essence Augment*  
> You no longer have a need to sleep, although you still must rest to recover from fatigue and regain hit points during breathers. Thick ringlets form around your eyes.  
> Note: This augment always acts as marque III for the purposes of determining cost, though you can learn this augment despite your skill in bio-flux.  

**Slimy** — *Essence Augment*  
> Your sweat glands naturally secrete a thin layer of grease, making it easier to slip out of grabs.  
> +4 to Dexterity when trying to break a grab  
> +8 to Dexterity when trying to break a grab  
> +12 to Dexterity when trying to break a grab  
> +16 to Dexterity when trying to break a grab  

**Stonebones** — *Essence Augment*  
> Your bones have been augmented to be as hard as steel. Your bones may not be severed or broken. If you receive a fatal effect which would normally remove a limb, your limb stays attached. However you still suffer all other negative effects of the fatal effect. This makes your bones thicker and heavier, reducing your movement speed.  
> -10 feet of movement speed  
> -10 feet of movement speed  
> -5 feet of movement speed  
> movement speed is unaffected  

**Vile Fumes** — *Essence Augment*  
> Cost: 3 AP  
> Your body expels an odor that causes those around you to become nauseated. For 3 action points, you may intensify these gases, forcing all those adjacent to you to make a Brute resist or become disoriented for a turn.  
> tier 2 brute resist  
> tier 3 brute resist  
> tier 3 brute resist  
> tier 4 brute resist  

**Wall-Crawler** — *Essence Augment*  
> Much like a gecko, your hands and feet are covered in small indentures that aid in climbing. You may climb on any ceiling or wall in any direction as per your normal movement speed. Note: This augment always acts as marque III for the purposes of determining cost, though you can learn this augment despite your skill in bio-flux.  
> Crafting B  
> For years bio-flux scientists experimented, attempting to find rather than spending hours in surgery. Eventually, bio-zappe blasts out a ray that instantly morphs the target’s essence. Th gets the job done.  
> A normal bio-zapper comes as a heavy weapon that within 25 feet and pull the trigger (just like a ranged attack c their evade. If you meet or exceed their evade, you hit them You choose the setting on your bio-zapper. (Without until the target’s next breather. You can change the setting on between settings costs 1 action point. If you hit somebody wi one.  


##### Bio-zapper augments (p.228–233) — "setting" = effect delivered by the ray (one active unless Multi-Setting); others modify the device

| Augment | Type | Resist | mQ I | mQ II | mQ III | mQ IV |
|---|---|---|---|---|---|---|
| Accurate | device | – | +1 Acc | +2 | +3 | +4 |
| Armor-Encumbering | setting | Dex | −5 spd (heavy+ armor) | −10 heavy / −5 light-med | −15 / −10 | −20 / −15 |
| Blood Thinning | setting | Brute | patching stops only 3 bleed | 2 | 1 | only at breather |
| Bone Spurring | setting | Spirit | 1 unsoakable per AP spent | 1 | 2 | 2 |
| Collapsible | device | – | 1 size smaller | 2 | 3 | 4 |
| Crippling | setting | Brute | −3 Brute rolls | −6 | −9 | −12 |
| Custom | device | – | others −3 Acc | −6 | −9 | −12 |
| Deflecting | device | – | deflect +4 Eva (always mQ I) | | | |
| Debilitating | setting | Brute | −2 Stk | −4 | −6 | −8 |
| Demoralizing | setting | Cunning | −2 Spirit rolls | −4 | −6 | −8 |
| Discombobulating | setting | Spirit (T2/T3/T3/T4 negates) | can't recover wounds damage | | | |
| Essence Draining | setting | Spirit | 1 essence slot off | 2 | 3 | 4 |
| Exhausting | setting | Spirit | max HP −5 | −10 | −15 | −20 |
| Extended Range | device | – | range 50 ft | 75 | 100 | 150 |
| Eyelid Fusing | setting | Brute (T2/T3/T3/T4 negates) | blinded; 1 AP + 1 wound to rip open | | | |
| Flesh Melting | setting | Brute | soak class −1 (min 0) | −2 | −3 | −4 |
| Growing | setting | Brute | −2 Def (armored targets only) | −4 | −6 | −8 |
| Hesitating | setting | Spirit | dropped 1 priority slot | 2 | 3 | 4 |
| Hexing | setting | Spirit (T2/T3/T3/T4 negates) | can't re-roll pure 12s | | | |
| Hindering | setting | Brute | −2 Dex rolls | −4 | −6 | −8 |
| Intensity | device | – | target −2 to resist | −4 | −6 | −8 |
| Micro-Zapper | device | – | wield as medium weapon | medium | light | light |
| Muffling | setting | Brute (T2/T3/T3/T4 negates) | deafened; 1 AP + 1 wound to rip ears open | | | |
| Multi-Setting | device | – | 2 settings ready | 3 | 4 | 5 |
| Nail Growing | setting | Dex | −2 Acc with firearms/crossbows | −4 | −6 | −8 |
| Nausea-Inducing | setting | Brute (T2/T3/T3/T4 negates) | nausea | | | |
| Perspiring | setting | Brute | −2 disarm resists & keeping grabs | −4 | −6 | −8 |
| Rattling | setting | Brute | −2 resist vs leg called shots | −4 | −6 | −8 |
| Reinforced | device | – | +1 size vs sunder | +2 | +3 | +4 |
| Skin-Papering | setting | Brute | −4 resist burns | −8 | −12 | −16 |
| Skin-Inflaming | setting | Brute | −3 resist catching fire | −6 | −9 | −12 |
| Silencing | setting | Brute (T2/T3/T3/T4 negates) | mute, no vocal specialties; 1 AP + 1 wound to rip open | | | |
| Silent | device | – | Cunning T2 to locate by sound | T3 | T4 | impossible |
| Sluggish | setting | Brute | −5 speed | −10 | −15 | −20 |
| Stupifying | setting | Cunning | −3 Cunning rolls | −6 | −9 | −12 |
| Swelling | setting | Brute | +2 Acc vs chosen location | +4 | +6 | +8 |
| Weakening | setting | Brute | melee DC −1 | −2 | −3 | −4 |

**Book texts:**

**Accurate** — *Bio-Zapper Augment*  
> Fine attention has been placed on the quality of your bio-zapper. You gain a bonus to accuracy with the bio-zapper.  
> +1  
> +2  
> +3  
> +4  

**Armor-Encumbering** — *Bio-Zapper Augment (Setting)*  
> resist: Dexterity (marques down)  
> Your bio-zapper makes your target’s body react as if the clothing on it is much heavier than it actually is. The penalty is greater depending on how much armor the target is wearing.  
> -5 speed penalty (heavy or larger armor)  
> -10 speed penalty (heavy or larger armor) or -5 speed penalty (light or medium armor)  
> -15 speed penalty (heavy or larger armor) or -10 speed penalty (light or medium armor)  
> -20 speed penalty (heavy or larger armor) or -15 speed penalty (light or medium armor)  

**Blood Thinning** — *Bio-Zapper Augment (Setting)*  
> resist: Brute (marques down)  
> The victims blood refuses to clot when bleeding. Patching Bleeding now only stops 3 bleeding damage Patching Bleeding now only stops 2 bleeding damage Patching Bleeding now only stops 1 bleeding damage Bleeding can only be stopped when taking a breather  

**Bone Spurring** — *Bio-Zapper Augment (Setting)*  
> resist: Spirit (marques down)  
> The victim’s bones become spiked inside of their bodies. This causes extreme pain when the victim does anything. The victim takes 1 unsoakable damage for each action point they spend  
> The victim takes 1 unsoakable damage for each action point they spend  
> The victim takes 2 unsoakable damage for each action point they spend  
> The victim takes 2 unsoakable damage for each action point they spend  

**Collapsible** — *Bio-Zapper Augment*  
> Sometimes discretion is the better part of not having your biozapper confiscated, so you create a clever collapsing mechanism for your bio-zapper which makes it easier to conceal. Any biozapper this is applied to can be broken down for 3 acion points and re-assembled for 3 action points. It is treated, for purposes of concealment, as being smaller than it is, but only when broken down.  
> 1 category smaller  
> 2 categories smaller  
> 3 categories smaller  
> 4 categories smaller  

**Crippling** — *Bio-Zapper Augment (Setting)*  
> resist: Brute (marques down)  
> When hit by a crippling ray, your body becomes weak and sickly.  
> -3 on Brute rolls  
> -6 on Brute rolls  
> -9 on Brute rolls  
> -12 on Brute rolls  

**Custom** — *Bio-Zapper Augment*  
> This bio-zapper was designed to be used by one person and one person only. That person must be designated at the time of the bio-zapper’s crafting. If anybody else attempts to use the custom bio-zapper, they suffer a penalty on all accuracy rolls with it.  
> -3  
> -6  
> -9  
> -12  

**Deflecting** — *Bio-Zapper Augment*  
> You may use this bio-zapper like a shield, allowing you to deflect incoming attacks (gaining a +4 to evade in exchange for 1 reflexive action point).  
> Note: This augment always acts as marque I for the purposes of determining cost, though you can learn this augment despite your skill in bio-flux.  

**Debilitating** — *Bio-Zapper Augment (Setting)*  
> resist: Brute (marques down)  
> Your target has sporatic spells of exhaustion, conveniently taking place right as they try to attack.  
> -2 on strike rolls  
> -4 on strike rolls  
> -6 on strike rolls  
> -8 on strike rolls  

**Demoralizing** — *Bio-Zapper Augment (Setting)*  
> resist: Cunning (marques down)  
> Bio-Zappers on this setting rewrite its victim’s face to resemble a cubist painting, making them feel less confident and ugly.  
> -2 on Spirit rolls  
> -4 on Spirit rolls  
> -6 on Spirit rolls  
> -8 on Spirit rolls  

**Discombobulating** — *Bio-Zapper Augment (Setting)*  
> resist: Spirit (negates, see below)  
> Victims hit with rays on this setting have their organs rearranged in such a weird way that it becomes impossible for them to recover from wounds damage (but not wounds effects) while under its effects.  
> tier 2 spirit resist to negate  
> tier 3 spirit resist to negate  
> tier 3 spirit resist to negate  
> tier 4 spirit resist to negate  

**Essence Draining** — *Bio-Zapper Augment (Setting)*  
> resist: Spirit (marques down)  
> Victims hit by this ray see their essence slots temporarily shut down. This not only makes augments to those slots useless but also causes the person to become grotesque like an elf. The person wielding the bio-zapper chooses which, if any, augments on the target are deactivated.  
> 1 essence slot is turned off  
> 2 essence slots are turned off  
> 3 essence slots are turned off  
> 4 essence slots are turned off  

**Exhausting** — *Bio-Zapper Augment (Setting)*  
> resist: Spirit (marques down)  
> Hitting a victim with a ray on the exhausting setting tires the opponent. A quick blast from one of these ensures the victim will not be going the distance.  
> maximum hit points are lowered by 5  
> maximum hit points are lowered by 10  
> maximum hit points are lowered by 15  
> maximum hit points are lowered by 20  

**Extended Range** — *Bio-Zapper Augment*  
> Your bio-zapper can hit targets well past 25 feet. targets up to 50 feet away  
> targets up to 75 feet away  
> targets up to 100 feet away  
> targets up to 150 feet away  

**Eyelid-Fusing** — *Bio-Zapper Augment (Setting)*  
> resist: Brute (negates, see below)  
> Victims unlucky enough to be in the path of a blinding ray find their eye lids fused together, making it impossible for them the see anything without drastic actions. For a single action point they can deal a point of wounds damage to themselves to rip their eyes open. They don’t take a wounds effect for doing so. tier 2 brute resist to negate  
> tier 3 brute resist to negate  
> tier 3 brute resist to negate  
> tier 4 brute resist to negate  

**Flesh Melting** — *Bio-Zapper Augment (Setting)*  
> resist: Brute (marques down)  
> Flesh melting rays cause the victim’s skin to melt and tear, making all attacks against them more deadly. This cannot lower their soak class below zero.  
> soak class lowered by 1  
> soak class lowered by 2  
> soak class lowered by 3  
> soak class lowered by 4  

**Growing** — *Bio-Zapper Augment (Setting)*  
> resist: Brute (marques down)  
> This ray causes the victim to grow just large enough for their armor and clothing to become unbearably tight and uncomfortable. This ray only affects victims in armor.  
> -2 on defense rolls  
> -4 on defense rolls  
> -6 on defense rolls  
> -8 on defense rolls  

**Hesitating** — *Bio-Zapper Augment (Setting)*  
> resist: Spirit (marques down)  
> When hit with this ray, its victim is dropped on the priority list as they hesitate to act, allowing others to take their turn first. If it drops them to the bottom of the priority list, they act there. They must wait until everyone has taken their turn before going. Dropped 1 priority slot  
> Dropped 2 priority slots  
> Dropped 3 priority slots  
> Dropped 4 priority slots  

**Hexing** — *Bio-Zapper Augment (Setting)*  
> resist: Spirit (negates, see below)  
> This ray alters your victim’s body chemistry, causing them to feel drained and demoralized. It forces them to see their own limits. When effected by this ray, victims may no longer re-roll pure 12s. tier 2 spirit resist to negate  
> tier 3 spirit resist to negate  
> tier 3 spirit resist to negate  
> tier 4 spirit resist to negate  

**Hindering** — *Bio-Zapper Augment (Setting)*  
> resist: Brute (marques down)  
> The victim’s equilibrium is thrown off, making acrobatics and fast movements almost impossible.  
> -2 on Dexterity rolls  
> -4 on Dexterity rolls  
> -6 on Dexterity rolls  
> -8 on Dexterity rolls  

**Intensity** — *Bio-Zapper Augment*  
> You have increased your victim’s dosage and in doing so made the blast more difficult to resist.  
> The target gets a -2 to resist the ray’s effects The target gets a -4 to resist the ray’s effects The target gets a -6 to resist the ray’s effects The target gets a -8 to resist the ray’s effects  

**Micro-Zapper** — *Bio-Zapper Augment*  
> You have made your bio-zapper significantly smaller, letting you wield it as a smaller weapon.  
> wields as a medium weapon  
> wields as a medium weapon  
> wields as a light weapon  
> wields as a light weapon  

**Muffling** — *Bio-Zapper Augment (Setting)*  
> resist: Brute (negates, see below)  
> The victim’s ears melt and fuse with the side of their head causing them to become deafened. For a single action point they can deal a point of wounds damage to themselves to rip their ears open. They don’t take a wounds effect for doing so. tier 2 brute resist to negate  
> tier 3 brute resist to negate  
> tier 3 brute resist to negate  
> tier 4 brute resist to negate  

**Multi-Setting** — *Bio-Zapper Augment*  
> This augment allows the bio-zapper to be in two settings at once. This allows you to choose between multiple settings to fire without spending 1 action point to switch between them. You still can only fire from one setting at a time.  
> The zapper may be in 2 settings  
> The zapper may be in 3 settings  
> The zapper may be in 4 settings  
> The zapper may be in 5 settings  

**Nail Growing** — *Bio-Zapper Augment (Setting)*  
> resist: Dexterity (marques down)  
> The victim’s fingers swell, making it difficult for them to smoothly pull the trigger on a firearm.  
> -2 accuracy with a firearm or crossbow  
> -4 accuracy with a firearm or crossbow  
> -6 accuracy with a firearm or crossbow  
> -8 accuracy with a firearm or crossbow  

**Nausea-Inducing** — *Bio-Zapper Augment (Setting)*  
> resist: Brute (negates, see below)  
> Your bio-zapper shakes and rattles your target’s stomach, making them unsettled and nauseous (-2 to all rolls until 3 action points are spent emptying their stomach).  
> tier 2 brute resist to negate  
> tier 3 brute resist to negate  
> tier 3 brute resist to negate  
> tier 4 brute resist to negate  

**Perspiring** — *Bio-Zapper Augment (Setting)*  
> resist: Brute (marques down)  
> Victims hit by a bio-zapper set to perspiring will begin to rapidly sweat. Their sweaty hands make it very difficult to hold on to any items and even more difficult to hold on to a person.  
> -2 to all disarm resists and maintaining grabs  
> -4 to all disarm resists and maintaining grabs  
> -6 to all disarm resists and maintaining grabs  
> -8 to all disarm resists and maintaining grabs  

**Rattling** — *Bio-Zapper Augment (Setting)*  
> resist: Brute (marques down)  
> After being hit by a ray on this setting, the victim’s legs become weak like jelly. Because of this, all called shots to to the legs become much more effective.  
> -2 on resist rolls against the legs  
> -4 on resist rolls against the legs  
> -6 on resist rolls against the legs  
> -8 on resist rolls against the legs  

**Reinforced** — *Bio-Zapper Augment*  
> You build your bio-zapper solidly, giving it little room to break on the battlefield. Whenever somebody attempts to sunder the reinforced bio-zapper, it acts as if it is several size categories larger than it is. Once these “reinforced” size categories are gone, then it will actually break.  
> 1 reinforced size category  
> 2 reinforced size categories  
> 3 reinforced size categories  
> 4 reinforced size categories  

**Skin-Papering** — *Bio-Zapper Augment (Setting)*  
> resist: Brute (marques down)  
> Your bio-zapper makes your target’s skin become thinner, less moist, and burn easier.  
> -4 on resists against burns  
> -8 on resists against burns  
> -12 on resists against burns  
> -16 on resists against burns  

**Skin-Inflaming** — *Bio-Zapper Augment (Setting)*  
> resist: Brute (marques down)  
> Your bio-zapper makes your target’s skin secrete a flammable liquid. They have a harder time resisting catching on fire.  
> -3 on resists against catching on fire  
> -6 on resists against catching on fire  
> -9 on resists against catching on fire  
> -12 on resists against catching on fire  

**Silencing** — *Bio-Zapper Augment (Setting)*  
> resist: Brute (negates, see below)  
> Victims hit by this ray find their mouths sewn shut, their ability to speak or make any sound stripped from them. In addition, victims lose the ability to use any specialties with required vocal components, such as yelling or singing. For a single action point they can deal a point of wounds damage to themselves to rip their lips open. They don’t take a wounds effect for doing so. tier 2 brute resist to negate  
> tier 3 brute resist to negate  
> tier 3 brute resist to negate  
> tier 4 brute resist to negate  

**Silent** — *Bio-Zapper Augment*  
> This bio-zapper is whispering death. It makes almost no sound when fired, making it almost impossible for people to figure out where it is by sound alone. Any time anybody is attempting to figure out where the bio-zapper was shot from based on sound they must make a tier result with their cunning. tier 2 cunning to hear  
> tier 3 cunning to hear  
> tier 4 cunning to hear  
> impossible (unless they can get a tier 5 cunning)  

**Sluggish** — *Bio-Zapper Augment (Setting)*  
> resist: Brute (marques down)  
> Your bio-zapper makes your target’s legs mutate to resemble elephant feet, slowing them down.  
> speed reduced by 5 feet  
> speed reduced by 10 feet  
> speed reduced by 15 feet  
> speed reduced by 20 feet  

**Stupifying** — *Bio-Zapper Augment (Setting)*  
> resist: Cunning (marques down)  
> The stupifying setting causes victims to become dazed and unobservant. They take a penalty on cunning rolls.  
> -3 on cunning rolls  
> -6 on cunning rolls  
> -9 on cunning rolls  
> -12 on cunning rolls  

**Swelling** — *Bio-Zapper Augment (Setting)*  
> resist: Brute (marques down)  
> This setting creates rays that cause the victim’s called shot locations to swell to ridiculous sizes. These swollen called shot are then easier to hit due to their increased size. You must select a single called shot location to affect when firing your bio-zapper set to this setting.  
> +2 accuracy to that called-shot  
> +4 accuracy to that called-shot  
> +6 accuracy to that called-shot  
> +8 accuracy to that called-shot  

**Weakening** — *Bio-Zapper Augment (Setting)*  
> resist: Brute (marques down)  
> The rays fired from this zapper make it difficult for your victim to lift their weapon, much less harm you with it. The damage class on any melee attacks the target makes is lowered. melee damage class lowered by 1  
> melee damage class lowered by 2  
> melee damage class lowered by 3  
> melee damage class lowered by 4  




#### Engineer

| Specialty | Group | Bonuses | Cost / type | Requires | Effect | Tags |
|---|---|---|---|---|---|---|
| **Maintenance** |  | Aug +2, DIY +1, HP +6 | Stance | 2 Engineer | stanCe (costs 1 AP to enter)<br>reQuires: 2 skill points in Engineer<br>Patch up a few bullet holes here, change the pressure valves over there - the job of a mechanic is never done. While in this stance, you make a series of constant small repairs to the section of the ship you’re in. This repairs 1 vehicle wound for every 2 points you have in engineering at the end of your turn (when your action points refresh). | [STANCE] [REQ] [SCALE:Engineer] |
| **Power Surge** |  | Pri +3, Aug +1, HP +6 | 1 AP (not the pilot) |  | Cost: 1 AP<br>When you’re not the pilot, you may tweak the coolant to grant the vehicle greater movement without overheating. This grants the pilot an additional action point in order to move or steer the vehicle once more for the turn. | [ACTION] |
| **Quick Upgrades** |  | Aug +2, DIY +1, HP +5 | Engineer roll per slot swapped |  | You may switch the parts on a vehicle quickly without waiting for downtime. You must know the augment you are about to put onto the part. You choose which slot(s) to empty and which slot(s) to replace. For every slot that you change, you roll your engineer skill to determine how quickly you do so. You must be adjacent to the vehicle in order to change its parts.<br>If changing out the parts requires more action points than you have for the turn, you may do so over multiple, nonconsecutive turns. For example, if it requires 7 action points to change out an augment, you could spend 3 action points this turn, and then wait a couple turns before spending the final 4 action points to switch out the augment. However, once you begin changing out parts, the original augment ceases to function and the new augment does not function until it is completely installed.<br>10 AP<br>7 AP<br>4 AP<br>2 AP | [ACTION] |
| **Vehicle Repairs** |  | Def +2, Aug +1, HP +7 | 3 AP | Auto-Wright or Manual-Wright | reQuires: either Auto-Wright or Manual-Wright specialty Cost: 3 AP<br>You are capable of repairing any vehicle that you are capable of building. You must be either inside or adjacent to the vehicle in order to make these repairs.<br>10 vehicle wounds<br>20 vehicle wounds<br>30 vehicle wounds<br>40 vehicle wounds | [ACTION] [REQ] |
| **Gearhead** | Grease Monkey | Aug +1, DIY +1, HP +5 | Stance (in/adjacent to vehicle) | 2 Engineer | stanCe (costs 1 AP to enter)<br>reQuires: 2 skill points in Engineering<br>By constantly regulating steam in-take and graviton rotations, you’re able to push a vehicle’s engine to its limits. When in this stance and either inside or adjacent to a vehicle, the vehicle’s speed increases by 5 feet per 2 skill points you have in Engineering. Moving away from the vehicle breaks this stance. | [STANCE] [REQ] [SCALE:Engineer] |
| **Gearjunkie** | Grease Monkey | Eva +1, Aug +1, HP +6 | Passive | 5 Engineer; Gearhead | reQuires: 5 skill points in Engineer & Gearhead specialty When you’re working on a vehicle, efficiency is maximized. While in Gearhead stance, you may also grant a vehicle a +1 on evade rolls for every 5 points you have in engineer.<br>Automatic versus Manual Vehicles<br>There are two ways of controlling vehicles, automatically propelled vehicles and those that require manual control. automatiCaLLy propeLLeD vehiCLes (autos) are<br>those that go at a constant speed unless the pilot changes the direction or speed of the vehicle. Autos typically have propellers, wheels, jets, or sails. Autos have a maximum speed, and they travel a set distance every turn (typically at the beginning of the pilot’s turn).<br>manuaL vehiCLes (clankers) require the pilot to<br>spend action points for every movement. Typically these are walking vehicles, where the pilot must move gears and levers every time the clanker wants to move. In effect, every time the pilot spends 1 action point to move the clanker, the clanker moves its speed.<br>You’ll find information on autos starting on this page, with their augments directly after. After autos, you’ll get information on the clankers. Once all of that is done, you can build a vehicle’s hull, providing it with armoring and protection for those inside. | [COND] [REQ] [SCALE:Engineer] |
| **Auto-Wright** | Crafting Vehicles | Aug +2, DIY +1, HP +4 | Passive (crafting) |  | Automatically propelled vehicles are ideal at getting adventurers from point A to point B. You’ll be able to craft everything from jetpacks to gyrocycles, ironbirds, motorcars, powerboats, and more. You can now craft one-person automatically propelled vehicles (called autos for short).<br>Without spending any money, you can build and maintain several autos based on your current Do-It-Yourself (DIY) score. They can then be upgraded with augments. You’ll learn 2 augments from this specialty, which can be selected under “auto augments” below. These augments have marques. At lower levels, you’ll start with Marque I augments. See the “Crafting” page at the beginning of this chapter for more information. Each auto can be upgraded with 3 augments. Some materials can only be upgraded twice (like wooden autos) or just once (like organic ones). Sometimes an augment will take up multiple augment slots. If an augment is worth 2 slots, an auto only has 1 more available slot for an augment after the 2-slot augment has been applied.<br>numBer oF autos you Can maintain<br>Without needing to buy pieces or parts, you can build some autos entirely out of scraps. These vehicles must be constantly maintained by you and stop working soon after leaving your care. You may build and maintain a number of autos for free based on your DIY score. You may build new autos or augment old ones during any period of downtime you have.<br>your Diy: 1 2 3 4 5 6<br>you Can BuiLD: 1 1 1 2 2 2<br>your Diy: 7 8 9 10 11 12<br>you Can BuiLD: 2 3 3 3 3 4<br>the Cost oF autos<br>If you need to build an auto that you can’t build for free from your DIY score, you will need to buy the materials for it. An auto will have a base materials cost. It is 1/5th the market price. The automatic vehicle, unaugmented, will have a base cost depending on its marque. (The marque will determine its maximum speed per turn.) If you buy a vehicle and augments, you will add the price of the augments onto the price of the vehicle.<br>marQue I II III IV<br>market priCe 100 princes 500 princes 2500 princes 12500 princes Every augment will increase the price. The higher the marque, the greater the price. The market price for an augment can be found in the chart below.<br>marQue I II III IV<br>market priCe 70 princes 350 princes 1750 princes 8750 princes If you are building the augment outside of your DIY Score, you pay 1/5th the price, which is the same as if you were buying an augment one marque lower. (As in, the material cost for a Marque III augment is the market price for a Marque II augment.) The material cost for a Marque 1 augment is 14 princes. Piloting your Auto<br>ControL methoD<br>While autos can be propelled by anything in your imagination, at default your craftable mount is grounded, with a maximum land or water surface speed based off of the marque of this specialty. It costs an action point to mount or dismount your auto. Your auto can be turned on and off for one action point. While piloting your auto, your defense and evade (and accuracy and strike, if applicable) are added to that of the vehicle. When you start your auto, select a speed setting between 5 feet per turn and its maximum speed per turn. While turned on, it will move at that speed every turn at the beginning of the pilot’s turn. It costs one action point to change the speed. It also costs one action point to control its movement during a turn, moving up to its current speed setting. If you do not spend the action point to control it, it will automatically move its last set speed in a straight line in the same direction it last moved.<br>BoDy oF the maChine<br>At default your vehicle can hold only one person at a time: its pilot. Your vehicle cannot protect its pilot from harm; the pilot can still be targeted as per normal.<br>Your automatic vehicle has a default maximum wounds of twelve and can be targeted by hostiles without the need of a called shot. Whenever your vehicle takes wounds damage, its maximum speed decreases by 10 feet. Should your automatic vehicle lose all of its wounds, your auto ceases to move. If it is in the air when this happens, anyone riding your vehicle will suffer falling damage. If on water, your vehicle will begin to sink at a rate of twenty feet per turn.<br>This specialty works within the marque system. As your skill in engineering grows, your autos will become faster and more efficient, increasing its maximum speed per turn. Maximum of 150 feet per turn<br>Maximum of 200 feet per turn<br>Maximum of 300 feet per turn<br>Maximum of 500 feet per turn | [AUG] [DIY] [CRAFT:auto] |
| **Beta Autos** | Crafting Vehicles | Aug +2, DIY +1, HP +5 | Passive | 4 Engineer; Auto-Wright | reQuires: 4 skill points in Engineer & Auto-Wright specialty Your automatic vehicles are exceptionally advanced but quite difficult to use. Such autos can be upgraded with 2 more augments (bringing the total for metal autos up to 5 augmentable slots). If anybody other than you attempts to operate one of your autos, they must succeed in rolling a science result one tier higher than the highest level marque you have on your auto. If your auto has a Marque IV augment, it is impossible for them to use it (unless they can somehow obtain a tier result of 5 with their science attribute).<br>If you are a passenger in a beta auto that you created, you can allow another person to pilot the vehicle. | [CRAFT] [REQ] |
| **Prototype Autos** | Crafting Vehicles | Aug +1, DIY +1, HP +6 | Passive | 16 Engineer; Auto-Wright; Beta Autos | reQuires: 16 skill points in Engineer, Auto-Wright, & Beta Autos You’ve perfected your beta autos and made them user-friendly. Now anybody can pilot your automatic vehicle as long as you designate it as being a prototype.<br>Conceptualizing your Vehicle<br>When you first start building vehicles, they’re not going to be full-fledged airships. Taking Auto-Wright will basically give you an engine that you can sit on or strap to your back. At the most basic levels, you probably have little more than a motorized bicycle or a propellered surf-board.<br>By taking augments, you can improve on the vehicle. When you take Aerial Propulsion or Lift, you’ll be able to soar the skies on a rocketpack. Want to take your friends with you? The Passenger and Extra Passengers augments will be your choice. Is your vehicle’s a little too rickety and easily destroyed for your liking? Taking Improved Construction and Sturdy will solve that problem.<br>By adding armoring, your vehicle can become a mobile tank, a weapon platform, a flying gunship, or whatever you can imagine.<br>And though you’ll be able to accomplish a lot, your vehicle’s going to start off simple. Barely a vehicle at all: just an engine, and some basic controls. | [CRAFT] [REQ] |
| **Manual-Wright** | Crafting Vehicles | Aug +2, DIY +1, HP +4 | Passive (crafting) |  | Manual vehicles are complex, powerful vehicles that move under the pilot’s power. You’ll be able to build walkers, steamtanks, ornithopters, motorships, and everything in-between. You can now craft one-person manual vehicles, called clankers for short. Without spending any money, you can build and maintain several clankers based on your current Do-It-Yourself (DIY) score. They can then be upgraded with augments. You’ll learn 2 augments from this specialty, which can be selected under “clanker augments” below. These augments have marques. At lower levels, you’ll start with Marque I augments. See the “Crafting” page at the beginning of this chapter for more information. Each clanker can be upgraded with 3 augments. Some materials can only be upgraded twice (like wooden clankers) or just once (like organic ones). Sometimes an augment will take up multiple augment slots. For example, the “flying” augment is worth 2 slots, so a clanker only has 1 more available slot for an augment after “flying” has been applied.<br>numBer oF CLankers you Can maintain<br>Without needing to buy pieces or parts, you can build some clankers entirely out of scraps. These vehicles must be constantly maintained by you and stop working soon after leaving your care. You may build and maintain a number of clankers for free based on your DIY score. You may build new clankers or augment old ones during any period of downtime you have.<br>your Diy: 1 2 3 4 5 6<br>you Can BuiLD: 1 1 1 2 2 2<br>your Diy: 7 8 9 10 11 12<br>you Can BuiLD: 2 3 3 3 3 4<br>the Cost oF CLankers<br>If you need to build a clanker that you can’t build for free from your DIY score, you will need to buy the materials for it. A clanker will have a base materials cost. It is 1/5th the market price. The manual vehicle, unaugmented, will have a base cost depending on its marque. (The marque will determine its maximum speed per action point spent.) If you buy a vehicle and augments, you will add the price of the augments onto the price of the vehicle. marQue I II III IV<br>market priCe 80 princes 400 princes 2000 princes 10000 princes Every augment will increase the price. The higher the marque, the greater the price. The market price for an augment can be found in the chart below.<br>marQue I II III IV<br>market priCe 60 princes 300 princes 1500 princes 7500 princes If you are building the augment outside of your DIY Score, you pay 1/5th the price, which is the same as if you were buying an augment one marque lower. (As in, the material cost for a Marque III augment is the market price for a Marque II augment.) The material cost for a Marque 1 augment is 12 princes. Piloting your Clanker<br>ControL methoD<br>While manual vehicles can be propelled by anything you imagine, by default your craftable mount is grounded, with a land or water surface speed based off of the marque of this specialty. It costs an action point to mount or dismount your clanker. Your clanker can be turned on and off for one action point. While piloting your clanker, your defense and evade (and accuracy and strike, if applicable) are added to that of the vehicle. It costs the pilot one action point to move the vehicle up to its full movement speed. The vehicle can move as many times per turn as the pilot can spend action points to do so. It can move in any direction without having to spend action points to turn, slow down, or any of that hogwash. It cannot climb or submerge itself. It costs an action point to mount or dismount your vehicle.<br>BoDy oF the maChine<br>At default your vehicle can hold only one person at a time: its pilot. Your vehicle cannot protect its pilot from harm; the pilot can still be targeted as per normal.<br>Your manual vehicle has a default maximum wounds of twelve and can be targetted by hostiles without the need of a called shot. Whenever your vehicle takes wounds damage, its maximum speed decreases by 5 feet. Should your vehicle run out of wounds, your manual vehicle ceases to move. If it is in the air when this happens, anyone riding your manual vehicle will suffer falling damage. If on water, your manual vehicle will begin to sink at a rate of twenty feet per turn. This specialty works within the marque system. As your skill in engineer grows, your clankers will become faster and more efficient, increasing its speed per action point spent. Up to 40 feet per action point spent<br>Up to 80 feet per action point spent<br>Up to 120 feet per action point spent<br>Up to 160 feet per action point spent | [AUG] [DIY] [CRAFT:clanker] |
| **Beta Clankers** | Crafting Vehicles | Aug +2, DIY +1, HP +5 | Passive | 4 Engineer; Manual-Wright | reQuires: 4 skill points in Engineer & Manual-Wright specialty Your manual vehicles are exceptionally advanced but quite difficult to use. Such clankers can be upgraded with 2 more augments (bringing the total for metal clankers up to 5 augmentable slots). If anybody other than you attempts to operate one of your clankers, they must succeed in rolling a science result one tier higher than the highest level marque you have on your vehicle. If your clanker has a Marque IV augment, it is impossible for them to use it (unless they can somehow obtain a tier result of 5 with their science attribute).<br>If you are a passenger in a beta clanker that you created, you can allow another person to pilot the vehicle. | [CRAFT] [REQ] |
| **Prototype Clankers** | Crafting Vehicles | Aug +1, DIY +1, HP +5 | Passive | 16 Engineer; Manual-Wright; Beta Clankers | reQuires: 16 skill points in Engineer, Manual-Wright, & Beta Clankers specialties<br>You’ve perfected your beta clankers and made them user-friendly. Now anybody can pilot your manual vehicle as long as you designate it as being a prototype. | [CRAFT] [REQ] |
| **Vehicle Armorer** | Armoring Vehicles | Aug +2, DIY +1, HP +6 | Passive (crafting) |  | A vehicle without armoring is little more than an engine and some sort of control system. You’ll give it a shell, a hull to keep the pilot, the engine, and everything you love safe. You can now armor vehicles.<br>Without spending any money, you can build and maintain the armoring on several vehicles based on your current Do- It-Yourself (DIY) score. They can then be upgraded with augments. You’ll learn 2 augments from this specialty, which can be selected under “armoring augments” below. These augments have marques. At lower levels, you’ll start with Marque I augments. See the “Crafting” page at the beginning of this chapter for more information.<br>Vehicle armoring can be upgraded with 3 augments. Some materials can only be upgraded twice (like wooden armoring) or just once (if you choose organic armoring). Sometimes an augment will take up multiple augment slots. If an augment is worth 2 slots, armoring only has 1 more available slot for an augment after the 2-slot augment has been applied.<br>amount oF armoring you Can maintain<br>Without needing to buy pieces or parts, you can build the armoring on some vehicles entirely out of scraps. This armoring must be constantly maintained by you and stops functioning soon after leaving your care. You may build and maintain a number of vehicle armoring for free based on your DIY score. You may create more armoring or augment old armoring during any period of downtime you have.<br>your Diy: 1 2 3 4 5 6<br>you Can BuiLD: 1 1 1 2 2 2<br>your Diy: 7 8 9 10 11 12<br>you Can BuiLD: 2 3 3 3 3 4<br>evaDe auto CLank<br>type soak CLass penaLty penaLty penaL<br>Unarmored 0 - -0 ft. -0 ft.<br>Minimal 1 -1 -10 ft. -5 ft.<br>Light 2 -2 -20 ft. -10 ft.<br>Medium 3 -4 -40 ft. -20 ft<br>Heavy 4 -6 -60 ft. -30 ft<br>Super-Heavy 5 -8 -80 ft. -40 ft<br>Vehicles<br>the Cost oF armoring<br>If you need to create armoring that you<br>can’t build for free from your DIY score, Armoring you will need to buy the materials for it.<br>Armoring will have a base materials cost. Minimal 20 princes It is 1/5th the market price. Light 50 princes<br>Armoring, unaugmented, will<br>have a base cost depending on its size. If Medium 100 princes you buy armoring with augments, you will Heavy 300 princes add the price of the augments onto the Super-Heavy 5000 princes price of the vehicle.<br>Every augment will increase the price. The higher the marque, the greater the price. The market price for an augment can be found in the chart below.<br>marQue I II III IV<br>market priCe 150 princes 750 princes 3750 princes 18750 princes If you are building the augment outside of your DIY Score, you pay 1/5th the price, which is the same as if you were buying an augment one marque lower. (As in, the material cost for a Marque III augment is the market price for a Marque II augment.) The material cost for a Marque 1 augment is 30 princes. | [AUG] [DIY] [CRAFT:vehicle armor] |
| **Beta Armoring** | Armoring Vehicles | Aug +2, DIY +1, HP +6 | Passive | 4 Engineer; Vehicle Armorer | reQuires: 4 skill points in Engineer & Vehicle Armorer specialty Your armoring is beyond that seen before, but it is nearly impossible to pilot a vehicle covered in the stuff. Such armoring can be upgraded with 2 more augments (bringing the total for metal armoring up to 5 augmentable slots).<br>y passenger Cover materiaL options<br>None None, Organic, or Textile<br>Poor (+2 evade) Metal, Organic, Textile, or<br>Wood<br>Light (+4 evade) Metal, Organic, Textile, or<br>Wood<br>Medium (+6 evade) Metal, Organic, or Wood<br>Heavy (+8 evade) Metal or Wood<br>. Total (cannot be Metal or Wood<br>targeted)<br>If anybody other than you attempts to operate a vehicle covered in your armoring, they must succeed in rolling a science result one tier higher than the highest level marque you have on your armoring. If your armoring has a Marque IV augment, it is impossible for them to use it (unless they can somehow obtain a tier result of 5 with their science attribute).<br>If you are a passenger in a vehicle that has beta armoring that you created, you can allow another person to pilot the vehicle. | [CRAFT] [REQ] |
| **Prototype Armoring** | Armoring Vehicles | Aug +1, DIY +1, HP +7 | Passive | 16 Engineer; Vehicle Armorer; Beta Armoring | reQuires: 16 skill points in Engineer, Vehicle Armorer, & Beta Armoring specialties<br>You’ve perfected your beta armoring and made it user-friendly. Now anybody can pilot a vehicle covered in your armoring as long as you designate it as being a prototype. | [CRAFT] [REQ] |

##### Engineer – vehicles (p.234–245)
- **Autos** (automatically propelled): set speed 5 ft…max; move at the start of the pilot's turn; 1 AP to change speed, 1 AP to steer (else continues straight). Max speed/turn by marque: 150 / 200 / 300 / 500 ft. **−10 ft max speed per wound damage.**
- **Clankers** (manual): 1 AP per move of full speed, any direction; speed per AP by marque 40 / 80 / 120 / 160 ft. **−5 ft per wound damage.** No climbing/submerging by default.
- Both: 1 AP mount/dismount, 1 AP on/off; hold only the pilot by default; pilot remains targetable; **12 wounds**; targetable without called shot; at 0 wounds stop (fall / sink 20 ft per turn). **Pilot's Defense and Evade (and Acc/Stk if applicable) are added to the vehicle's.**
- DIY → autos, clankers or vehicle armorings maintained: DIY 1–3: 1 · 4–7: 2 · 8–11: 3 · 12: 4.

| Price | mQ I | mQ II | mQ III | mQ IV | mQ I material |
|---|---|---|---|---|---|
| Auto (unaugmented) | 100 pr | 500 | 2,500 | 12,500 | – |
| Auto augment | 70 pr | 350 | 1,750 | 8,750 | 14 pr |
| Clanker (unaugmented) | 80 pr | 400 | 2,000 | 10,000 | – |
| Clanker augment | 60 pr | 300 | 1,500 | 7,500 | 12 pr |
| Vehicle armoring augment | 150 pr | 750 | 3,750 | 18,750 | 30 pr |

**Vehicle armoring types**

| Type | Soak | Evade pen. | Auto speed pen. | Clanker speed pen. | Passenger cover | Materials | Price |
|---|---|---|---|---|---|---|---|
| Unarmored | 0 | 0 | 0 | 0 | none | none/organic/textile | – |
| Minimal | 1 | −1 | −10 | −5 | poor (+2) | metal/organic/textile/wood | 20 pr |
| Light | 2 | −2 | −20 | −10 | light (+4) | metal/organic/textile/wood | 50 pr |
| Medium | 3 | −4 | −40 | −20 | medium (+6) | metal/organic/wood | 100 pr |
| Heavy | 4 | −6 | −60 | −30 | heavy (+8) | metal/wood | 300 pr |
| Super-Heavy | 5 | −8 | −80 | −40 | total | metal/wood | 5,000 pr |

##### Auto & clanker augments (p.238–242) — A = autos only, C = clankers only

| Augment | Slots | mQ I | mQ II | mQ III | mQ IV | Notes |
|---|---|---|---|---|---|---|
| Aerial Propulsion (A) | 1 | fly horizontally at speed (water at half) | – | – | – | always mQ II |
| Alchemy Refill Station | 1 | refill 1 potion per breather | 2 | 3 | 4 | |
| All-Terrain | 1 | not slowed by rough terrain | – | – | – | always mQ I |
| Armsmith Utilities | 1 | repair gear at breather; swap 1 armsmith augment | 2 | 3 | 4 | |
| Blazing Speed (A; req. Improved Speed) | 1 | +50 speed | +100 | +150 | +200 | |
| Blurring Speeds (A) | 1 | +3 Eva at top speed | +4 | +5 | +6 | |
| Buoyancy Release | 1 | 1 AP reflexive: stay afloat; device 6 wounds | 12 | 18 | 24 | |
| Climber | 1 | climb vertical surfaces at speed | – | – | – | always mQ I |
| Difficult Controls | 1 | others +1 AP to pilot | +2 | +3 | +4 | one designee exempt |
| Drill | 1 | through thin soil/sand | ice, thick soil | weak stone, clay | worked stone, soft metal | |
| Ease of Repair | 1 | +2 on Vehicle Repairs/Maintenance | +4 | +6 | +8 | |
| Efficient Movement (C) | 1 | +20 speed | +40 | +60 | +80 | |
| Emergency Parachute | 1 | 1 AP reflexive: descend 10 ft/turn; 3 wounds | 6 | 9 | 12 | |
| Extra Passengers (req. Passenger) | 1 | +1 passenger | +2 | +3 | +4 | |
| Flying (C) | 2 | fly any direction | – | – | – | always mQ II |
| Gliding | 1 | glide 2 turns after stopping (−10 ft alt/turn) | 4 | 6 | 8 | |
| Improved Construction | 1 | +12 wounds | +24 | +36 | +48 | |
| Improved Speed (A) | 1 | +50 speed | +100 | +150 | +200 | |
| Lift (A) | 1 | 20 ft vertical | 40 | 60 | 80 | 1 AP to change lift |
| Passenger | 1 | +1 passenger | – | – | – | always mQ I |
| Power Thrusters (A) | 1 | +100 beyond max speed (−1 wound/turn) | +200 | +300 | +400 | |
| Side Thrusters | 1 | 1 AP reflexive dodge up to 20 ft | 40 | 60 | 80 | |
| Silent Movement | 1 | Cunning T2 to hear | T3 | T4 | undetectable | |
| Speed Durability | 1 | speed only drops after 3 wounds in one attack | 6 | 9 | 12 | |
| Sturdy | 1 | +1 base soak | +2 | +3 | +4 | not sunderable |
| Thick Exhausts | 1 | +1 Eva | +2 | +3 | +4 | |
| Underwater Propulsion | 1 | move underwater (air at half) | – | – | – | always mQ II |
| Weapon Mount | 1 | turret; detach/attach 3 AP | 2 | 1 | 1 reflexive | always in firing position |

**Book texts:**

**Aerial Propulsion** — *Vehicle Augment*  
> Can onLy Be appLieD to autos  
> Your vehicle has jets, wings, propellers, sails, or some other way of moving through the air. You may apply your vehicle speed to moving in the air. You do not gain the ability to move vertically in the air - you can only move horizontally. Aerial propulsion also allows you to move through water, but you move at half your speed (unless you have Underwater Propulsion).  
> Note: This augment always acts as marque II for the purposes of determining cost, though you can learn this augment despite your skill in engineer.  

**Alchemy Refill Station** — *Vehicle Augment*  
> You’ve equipped your vehicle with everything you need in order to refill consumed alchemical substances during a breather (a 15-30 minute break). Over the course of a single breather the refill station in your vehicle will allow an alchemist to refill used alchemical potions they’ve brewed. The alchemy refill station will allow a maximum number of refills per breather based on the marque of this augment. You must be adjacent to or inside the vehicle in order to use the refill station.  
> 1 alchemical potion  
> 2 alchemical potions  
> 3 alchemical potions  
> 4 alchemical potions  

**All Terrain** — *Vehicle Augment*  
> Your vehicle is adept at moving through terrain (either by having rotating machetes on the front or by having a vehicle that’s just great at sliding in-between brush). Your vehicle cannot be slowed by rough terrain.  
> Note: This augment always acts as marque I for the purposes of determining cost, though you can learn this augment despite your skill in engineer.  

**Armsmith Utilities** — *Vehicle Augment*  
> Your vehicle is outfitted with a small forge, extra equipment, and various tools used to fix your armor, weapons, and firearms. A vehicle outfitted with armsmith utilities can be used to repair any broken armor or weaponry during a breather (a 15-30 minute break). A person who knows armsmith augments can also switch out augments on an item. The armsmither may change a number of marques based on the marque of this augment. You must be adjacent to or inside this vehicle in order to use armsmith utilities.  
> 1 armsmith augment may be changed  
> 2 armsmith augments may be changed  
> 3 armsmith augments may be changed  
> 4 armsmith augments may be changed  

**Blazing Speed** — *Vehicle Augment*  
> Can onLy Be appLieD to autos  
> reQuires: vehicle to be augmented to have the Improved Speed Your vehicle is stupidly fast. Your speed is improved based on the marque of this augment. (This bonus stacks with that granted by Improved Speed.)  
> +50 speed  
> +100 speed  
> +150 speed  
> +200 speed  

**Blurring Speeds** — *Vehicle Augment*  
> Can onLy Be appLieD to autos  
> Your vehicle is built to go so fast that nothing else can hit it. When traveling at your top speeds, your vehicle is little more than a blur. You vehicle gains a bonus to its evade rolls whenever you’re moving at its top speed (and until the pilot’s next turn, when the speed is adjusted). The evade bonus is based on the marque of this augment.  
> +3 on evade rolls  
> +4 on evade rolls  
> +5 on evade rolls  
> +6 on evade rolls  

**Buoyancy Release** — *Vehicle Augment*  
> Cost to aCtivate: 1 AP reflexively  
> When your vehicle starts to sink or hits the water and isn’t equipped for staying afloat, you can hit your buoyancy release in order to stay afloat. The pilot may activate the buoyancy release for 1 action point, and it will cause the vehicle to stay afloat despite any injuries the vehicle has taken.  
> A foe may attack the buoyancy release mechanism. The buoyancy has a number of wounds based on the marque of this augment.  
> 6 wounds  
> 12 wounds  
> 18 wounds  
> 24 wounds  

**Climber** — *Vehicle Augment*  
> Whether it be iron hooks built into your treads or a more straightforward set of arms and legs extending from your vehicle, it now has the ability to climb. You may apply your vehicle speed to moving up and down verticle surfaces.  
> Note: This augment always acts as marque I for the purposes of determining cost, though you can learn this augment despite your skill in engineer.  

**Difficult Controls** — *Vehicle Augment*  
> Your vehicle is complex, poorly organized, and the controls aren’t well labeled. In all ways, it is designed for you. Anybody else attempting to pilot your vehicle must spend extra action points in order to change the speed or turn the vehicle.  
> +1 action point to pilot  
> +2 action points to pilot  
> +3 action points to pilot  
> +4 action points to pilot  
> Note: You may designate one other person as being able to pilot your vehicle as well, so they do not take the penalties for the difficult controls.  

**Drill** — *Vehicle Augment*  
> Your vehicle has a drill, and this drill lets you move through the earth. You may apply your vehicle speed to moving through the earth. You may change directions as you drill forward, going up, down, left, or right.  
> The drill does not allow you to drill through all substances. The thickness of the substance you can drill through depends on the marque of this augment. If it is too thick for you to drill through (which will be decided by the narrator), you will not be able to pass through it.  
> Thin soil, dirt, and sands  
> Ice, thick soils, and wet sands  
> Weak stone, compressed soils, and clays  
> Worked stones, mountains, soft metals  

**Ease Of Repair** — *Vehicle Augment*  
> Your vehicle is made so that the gears and engine are easy to access and repair. Whenever somebody is attempting to use the Vehicle Repairs specialty or Maintenance specialty on the vehicle, they gain a bonus on the roll.  
> +2  
> +4  
> +6  
> +8  

**Efficient Movement** — *Vehicle Augment*  
> Can onLy Be appLieD to CLankers  
> You clockwork engines respond seemlessly, letting you squeeze out every ounce of movement from your clanker. Your speed increases.  
> +20 speed  
> +40 speed  
> +60 speed  
> +80 speed  

**Emergency Parachute** — *Vehicle Augment*  
> Cost to aCtivate: 1 AP reflexively  
> When your vehicle starts to lose altitude and is going to crash, you can release your emergency parachute in order to slow your descent. The pilot may activate the emergency parachute for 1 action point, and it will cause the vehicle to float slowly to the ground despite any injuries the vehicle has taken. The vehicle will fall 10 feet per turn.  
> A foe may attack the emergency parachute. The parachute has a number of wounds based on the marque of this augment.  
> 3 wounds  
> 6 wounds  
> 9 wounds  
> 12 wounds  

**Extra Passengers** — *Vehicle Augment*  
> reQuires: vehicle to be augmented to have the Passenger augment You’ve outfitted your vehicle with small compartments, uncomfortable back seats, and barrels that hang from the main seat that are all capable of carrying extra passengers. You may add a number of extra passengers (in addition to the passenger allowed from your Passenger augment). This does not make the vehicle much larger, despite logic dictating otherwise (hey, it’s steampunk!).  
> +1 passengers (to a total of 1 pilot & 2 passengers)  
> +2 passengers (to a total of 1 pilot & 3 passengers)  
> +3 passengers (to a total of 1 pilot & 4 passengers)  
> +4 passengers (to a total of 1 pilot & 5 passengers)  

**Flying** — *Vehicle Augment*  
> Can onLy Be appLieD to CLankers & takes up 2 augment sLots You’ve attached cranked propellers or wings to your clanker, letting you soar through the air. You may move your vehicle through the air, traveling in any direction.  
> Note: This augment always acts as marque II for the purposes of determining cost, though you can learn this augment despite your skill in engineer.  

**Gliding** — *Vehicle Augment*  
> Your vehicle is equipped to glide for a while after the vehicle has stopped moving. If you turn off your vehicle or it can’t move (for any reason) while it’s in the air, the vehicle will glide forward for a number of turns before it loses its ability to glide. It will continue to move forward at its speed but will lose 10 feet of altitude per turn. It will glide for a number of turns based on the marque of this augment.  
> 2 turns  
> 4 turns  
> 6 turns  
> 8 turns  

**Improved Construction** — *Vehicle Augment*  
> Your vehicle is built exceptionally well, made sturdy, strong, and tough to take down. Your vehicle has extra wounds based on the marque of this augment.  
> +12 wounds  
> +24 wounds  
> +36 wounds  
> +48 wounds  

**Improved Speed** — *Vehicle Augment*  
> Can onLy Be appLieD to autos  
> You’ve streamlined your vehicle to make it faster. Your speed is improved based on the marque of this augment.  
> +50 speed  
> +100 speed  
> +150 speed  
> +200 speed  

**Lift** — *Vehicle Augment*  
> Can onLy Be appLieD to autos  
> Your vehicle can support itself through verticle lift, either through a lighter-than-air envelope or a graviton sphere. If you are combining Lift with Aerial Propulsion, you’ll be able to move vertically a certain distance based on the marque of this augment as well as move horizontally based on your speed. Lift only lets you move vertically, and it acts independently of all other speeds. The pilot of the automatic vehicle will need to set the lift speed as well (which costs 1 action point to change).  
> 20 feet of vertical movement  
> 40 feet of vertical movement  
> 60 feet of vertical movement  
> 80 feet of vertical movement  

**Passenger** — *Vehicle Augment*  
> You’ve installed a second seat in your vehicle - good job, now your friend can come with you! You may carry a single passenger in your vehicle. (This does not increase the size of your vehicle.) Note: This augment always acts as marque I for the purposes of determining cost, though you can learn this augment despite your skill in engineer.  

**Power Thrusters** — *Vehicle Augment*  
> Can onLy Be appLieD to autos  
> aCtivation Cost: 0 AP (but done when changing speed) You’ve applied extra thrusters to your vehicle that make you move exceptionally fast. Unfortunately, it makes you so fast that your vehicle starts to break down. Any time you adjust your speed, you can choose to freely activate your power thrusters. This increases the vehicle’s maximum speed based on the marque of this augment. However, every turn that you have your power thrusters activated, your vehicle loses 1 wound.  
> +100 speed beyond your vehicle’s maximum speed  
> +200 speed beyond your vehicle’s maximum speed  
> +300 speed beyond your vehicle’s maximum speed  
> +400 speed beyond your vehicle’s maximum speed  

**Side Thrusters** — *Vehicle Augment*  
> Cost: 1 AP reflexively  
> Side thrusters allow you to quickly toss to the side, bolting out of the way. Side thrusters can be activated at any time for 1 action point, and they send your vehicle a certain distance based on the marque of this augment. You may have your side thrusters send you in any direction (regardless of the direction you’re traveling), and you may go any distance, up to the maximum allowed by the side thrusters. You cannot travel through solid terrain. up to 20 feet  
> up to 40 feet  
> up to 60 feet  
> up to 80 feet  

**Silent Movement** — *Vehicle Augment*  
> Your vehicle is well-greased, quiet, and difficult to hear. When somebody is listening for your vehicle, they must make a cunning result to hear, based on the marque of this augment.  
> Tier 2 cunning to detect  
> Tier 3 cunning to detect  
> Tier 4 cunning to detect  
> Undetectable (unless you can achieve a tier 5 cunning)  

**Speed Durability** — *Vehicle Augment*  
> It’s difficult for attacks to damage your engine. An attack that damages your vehicle must do a certain amount of wounds damage before it decreases your speed. (Normally 1 wound damage would decrease your speed by 10 for autos or 5 feet for clankers.)  
> 3 wounds from a single attack before speed is reduced  
> 6 wounds from a single attack before speed is reduced  
> 9 wounds from a single attack before speed is reduced  
> 12 wounds from a single attack before speed is reduced  

**Sturdy** — *Vehicle Augment*  
> The vehicle is strongly built and gains an increased soak class. This soak class is not from armoring, but rather comes from the basic soak of the vehicle. (As such, it cannot be sundered or broken like normal armoring.) The amount of soak class is based on the marque of this augment.  
> +1 soak class  
> +2 soak class  
> +3 soak class  
> +4 soak class  

**Thick Exhausts** — *Vehicle Augment*  
> Thick steam, smoke, and smog rolls out from your vehicle, clouding the area around you. The exhaust coats your vehicle, making it difficult to target your vehicle. Generally, this is made not to negatively effect the pilot of any gunners on board. The thick exhausts gives you a bonus on your evade based on the marque of the augment. (If the attacker has any ways of negating penalties caused from cover or poor sight, they can negate this as well.)  
> +1 on evade rolls  
> +2 on evade rolls  
> +3 on evade rolls  
> +4 on evade rolls  

**Underwater Propulsion** — *Vehicle Augment*  
> Your vehicle has fins, jets, propellers, or some other way of moving through the water. You may apply your vehicle speed to moving underwater. You can change directions, moving up, down, or forward. Underwater propulsion also allows you to move through the air, but you move at half your speed (unless you have Aerial Propulsion).  
> Note: This augment always acts as marque II for the purposes of determining cost, though you can learn this augment despite your skill in engineer.  

**Weapon Mount** — *Vehicle Augment*  
> You’ve outfitted your vehicle with a weapon turret that you can fire from the cockpit. The weapon is built into the vehicle, and can be augmented as a weapon. If you have any passengers in the vehicle, they can operate the weapon instead. If the weapon requires the wielder to be in firing position, the weapon always counts as being in firing position.  
> You can detach or re-attach the weapon for a number of action points depending on the marque of this augment.  
> 3 action points  
> 2 action points  
> 1 action point  
> 1 action point reflexively  
> Ar moring  


##### Vehicle armoring augments (p.244–245)

| Augment | mQ I | mQ II | mQ III | mQ IV |
|---|---|---|---|---|
| Airtight | cloud level / just below surface | cloud level / deep water | above clouds / ocean floor | edge of atmosphere / abyss |
| Effective Armoring | +2 Def | +4 | +6 | +8 |
| Electro-Absorption | +2 soak vs electricity (fully soakable) | +4 | +6 | +8 |
| Emergency Landing | hull soaks 10 crash dmg | 50 | 100 | 250 |
| Exceptional Structure (req. Structural Integrity) | +20 HP | +40 | +60 | +80 |
| Fireproofing | +1 soak vs fire | +2 | +3 | +4 |
| Flame Retardant | immune T1 fire | T2 | T3 | T4 |
| Greater Crew Cover | cover +1 degree | +2 | +3 | +4 |
| High Mobility | speed penalty 1 degree lighter | 2 | 3 | 4 |
| Internal Oxygen Supply | 10 min | 60 min | 1 day | 1 week |
| Structural Integrity | +10 vehicle HP | +20 | +30 | +40 |
| Thick Armoring | +1 soak | +2 | +3 | +4 |

**Book texts:**

**Airtight** — *Armoring Augment*  
> The vehicle can go higher in the atmosphere or underwater. While the airtightness is a factor, so is the vehicle’s ability to withstand pressure. If there is no way of breathing, oxygen will eventually run out of an airtight vehicle.  
> The vehicle can go to cloud level or just below the surface of water  
> The vehicle can go to cloud level or deep underwater The vehicle can go above clouds or to the ocean’s bot- The vehicle can skim the top of the atmosphere or reach the abysses of the ocean  

**Effective Armoring** — *Armoring Augment*  
> Your vehicle’s armoring is streamlined, slick, and it’s surprisingly easy to ensure that bullets aren’t going to make it through. The pilot gains a bonus on the vehicle’s defense roll.  
> +2 on defense rolls  
> +4 on defense rolls  
> +6 on defense rolls  
> +8 on defense rolls  

**Electro-Absorption** — *Armoring Augment*  
> The armoring re-routes electricity through it and into specially created devices that absorb the shock. Anything that deals electricity damage is now entirely soakable, and attacks that deal electricity damage (even if they are only partially electrical, such as attacks with a pulsing weapon) increase the soak class of the armor.  
> +2 soak class against electrical attacks  
> +4 soak class against electrical attacks  
> +6 soak class against electrical attacks  
> +8 soak class against electrical attacks  

**Emergency Landing** — *Armoring Augment*  
> Your armor is built to withstand crashes. When crashing (though we hope it’s not often), the hull can soak a certain amount of damage and keep it from being inflicted upon the crew.  
> 10 damage  
> 50 damage  
> 100 damage  
> 250 damage  

**Exceptional Structure** — *Armoring Augment*  
> reQuires: armoring to be augmented to have the Structural Integrity augment  
> Your vehicle’s armoring is exceptional, providing greater support and a thicker buffer between your hard, outer shell and the gooey insides. This grants you additional hit points, which stack with those granted by Structural Integrity.  
> +20 hit points  
> +40 hit points  
> +60 hit points  
> +80 hit points  

**Fireproofing** — *Armoring Augment*  
> While coated in armoring that has fireproofing, all fire attacks are soakable. Furthermore, the soak class for the armoring is improved against fire.  
> +1 soak class against fire  
> +2 soak class against fire  
> +3 soak class against fire  
> +4 soak class against fire  

**Flame Retardant** — *Armoring Augment*  
> The armoring generally cannot be caught on fire, depending on how intense the fire is.  
> Cannot be caught on tier 1 fire  
> Cannot be caught on tier 2 fire  
> Cannot be caught on tier 3 fire  
> Cannot be caught on tier 4 fire  

**Greater Crew Cover** — *Armoring Augment*  
> Your vehicle’s armoring is designed to keep you and any passengers alive for significantly longer. The greater crew cover improves the cover by a degree (or more, depending on the marque). For example, if you’re in vehicle with Marque I Greater Crew Cover light armoring, everyone on board can take advantage of medium cover. The maximum cover is total cover, in which the people inside the vehicle cannot be targeted.  
> improves cover by 1 degree  
> improves cover by 2 degrees  
> improves cover by 3 degrees  
> improves cover by 4 degrees  

**High Mobility** — *Armoring Augment*  
> The armor is optimized to be lightweight, easy to move in, and not clutter up your vehicle’s amazing speed. This augment decreases the speed penalty the vehicle takes from wearing the armor. It decreases it by a degree - for example, if you’re using Marque I High Mobility light armoring, it would have the speed penalty of minimal armoring.  
> the speed penalty is 1 degree lighter  
> the speed penalty is 2 degrees lighter  
> the speed penalty is 3 degrees lighter  
> the speed penalty is 4 degrees lighter  

**Internal Oxygen Supply** — *Armoring Augment*  
> Your armoring provides oxygen for your vehicle. It will last for a definite period, depending on the marque.  
> 10 minutes  
> 60 minutes  
> 1 day  
> 1 week  

**Structural Integrity** — *Armoring Augment*  
> The armoring was built to be exceptionally sturdy, granting hit points to the vehicle. Like normal, hit points are damaged before wounds.  
> +10 hit points  
> +20 hit points  
> +30 hit points  
> +40 hit points  

**Thick Armoring** — *Armoring Augment*  
> You’ve thickened your armoring without impeding your creation at all. You grant the armor extra soak.  
> +1 soak class  
> +2 soak class  
> +3 soak class  
> +4 soak class  




#### Gadgetry

| Specialty | Group | Bonuses | Cost / type | Requires | Effect | Tags |
|---|---|---|---|---|---|---|
| **Beta Hacker** |  | Eva +1, Aug +1, HP +8 | Passive |  | Your tinkering and logic has made you adept at hacking into beta equipment. Whenever you are trying to work a beta item, you may add your skill in gadgetry to the roll. In addition, if you receive a result of 40 or higher, you have made a tier 5 result, and can now use marque 4 beta items. | [COND] [SCALE:Gadgetry] |
| **Dud** |  | Acc +1, Eva +1, HP +7 | 1 AP reflexive; resist Cunning (negates) |  | resist: Cunning (negates)<br>Cost: 1 AP reflexively<br>Whenever someone adjacent to you is activating the fuse of an explosive, you can make the explosive a dud. The explosive will not explode, and your enemies must make a Cunning resist to realize the explosive isn’t functioning. | [REFLEX] |
| **Item Breaker** |  | Acc +1, Stk +3, HP +9 | As a sunder | Saboteur | reQuires: Saboteur specialty<br>Cost: same as a Sunder<br>Whenever you successfully sunder an item, you are able to turn off some of its augments until the next breather. Marque 1 augments are turned off<br>Marque 2 augments are turned off<br>Marque 3 augments are turned off<br>Marque 4 augments are turned off | [ATTACK+0] [REQ] |
| **Reverse Engineer** |  | Aug +2, DIY +1, HP +5 | During a breather |  | You are able to move augments from one item to another, including those you yourself are not capable of crafting. When reverse engineering an item, roll your Gadgetry. If you are unsuccessful, the augment is destroyed. Augments may only be moved to an item the augment could normally be attached to. For instance, you cannot move a melee weapon augment to a vehicle. This can be performed during any breather, though the exact amount of time this takes is dependant on the size of the device, at the narrator’s discretion.<br>Can move up to a Marque 1 augment<br>Can move up to a Marque 2 augment<br>Can move up to a Marque 3 augment<br>Can move up to a Marque 4 augment | [ACTION] |
| **Saboteur** |  | Acc +1, Pri +3, HP +8 | 1 AP; resist Dex (negates) |  | resist: Dexterity (negates)<br>Cost: 1 AP<br>You know how to throw a wrench into another person’s plans... and their items. You can turn off a single augment of an item either adjacent to you or being wielded by someone adjacent to you. | [ACTION] |
| **Improvised Improvements** |  | Eva +1, Aug +1, HP +7 | Stance | 4 Gadgetry | Requires: 4 skill points in Gadgeteer<br>stanCe (costs 1 AP to enter)<br>Crafted items seem to perform better when you’re around. When entering this stance, choose augments on any items within 5 feet of your current position, whether you are wielding the item or not. These augments act as if they were 1 marque higher. You can do this to 1 augment for every 4 skill points you have in Gadgetry. If any item whose augments you’re improving moves away from being adjacent to you, the improvements wear off. To reassign which augments you’re improving, you must reenter your Improvised Improvements stance. You cannot make an augment exceed marque 4.<br>Using Explosives<br>Explosives are built to be small and easily thrown, just like a light thrown weapon, and you can aim at an opponent with it just like a regular thrown attack. Even if you don’t hit the opponent, the bomb still lands in the target’s space. When you activate an explosive, it will detonate at the beginning of your next turn. Activating an explosive requires 1 action point. (You can both draw and activate an explosive for just 1 action point.) Throwing it requires 2 action points. The explosive deals 10 damage per marque of the<br>explosive. So, if you create Marque II explosives, you deal 20 damage to anybody in the explosion. Explosives damage every person within the target space and all eight of the adjacent spaces.<br>numBer oF expLosives you Can maintain<br>Without needing to buy pieces or parts, you can build some explosives entirely out of scraps. These explosives must be constantly maintained by you and stop working soon after leaving your care. You may build and maintain a number of explosives based on your DIY score. You may build new explosives or augment old ones during any period of downtime you have. your Diy: 1 2 3 4 5 6<br>you Can BuiLD: 5 6 6 7 7 8<br>your Diy: 7 8 9 10 11 12<br>you Can BuiLD: 8 9 9 10 10 11<br>the Cost oF expLosives<br>If you need to build an explo-<br>sive that you can’t build for free Explosives<br>f n r e o e m d y to o u b r u D y I t Y h e s c m or a e t , e y ri o a u ls w fo il r l Marque I (10 damage) 5 princes it. Marque II (20 damage) 25 princes<br>An explosive will have Marque III (30 damage) 125 princes a base materials cost. It is 1/5th Marque IV (40 damage) 625 princes the market price.<br>Every augment will increase the price. The higher the marque, the greater the price. The market price for an augment can be found in the chart below.<br>marQue I II III IV<br>market priCe 8 princes 40 princes 200 princes 1,000 princes If you are building the augment, you pay 1/5th the price, which is the same as if you were buying an augment one marque lower. (As in, the material cost for a Marque III augment is the market price fo a Marque II augment.) The material cost for a Marque 1 augment is 1 prince and 6 dukes. | [STANCE] [REQ] [SCALE:Gadgetry] |
| **Pyrotechnician** | Crafting Explosives | Aug +2, DIY +1, HP +4 | Passive (crafting) |  | You’re a master of explosives, so full of gunpowder and fuses that you always run the risk of blowing off your left ear. You turn the battlefield into a place of nightmares, your explosions ringing in your enemies’ ears and burns searing off their flesh. You can now create explosives.<br>Without spending any money, you can build and maintain several explosives based on your current Do-It-Yourself (DIY) score. These explosives can then be upgraded with augments. You’ll learn 2 augments from this specialty, which can be selected under “explosive augments” below. These augments have marques. At lower levels, you’ll start with Marque I augments. As your skill in Gadgetry improves, your marques will increase. See the “Crafting” page at the beginning of this chapter for more information.<br>Each explosive can be upgraded with 3 augments. Some materials can only be upgraded twice (like wooden explosives) or just once (like organic ones). Sometimes an augment will take up multiple augment slots. For example, the “gear-rattler” augment is worth 2 slots, so an explosive only has 1 more available slot for an augment after “gear-rattler” has been applied. | [AUG] [DIY] [CRAFT:explosive] |
| **Beta Explosives** | Crafting Explosives | Aug +2, DIY +1, HP +5 | Passive | 4 Gadgetry; Pyrotechnician | reQuires: 4 skill points in Gadgetry & Pyrotechnician specialty Your explosives are exceptionally complex little gizmos, but the pack they punch is not to be underestimated. Such explosives can be upgraded with 2 more augments (bringing the total for metal explosives up to 5 augmentable slots).<br>If anybody other than you attempts to use one of your beta explosives they must succeed in rolling a sciences result one tier higher than the highest marque you have on your explosive. If your explosive has a Marque IV augment, it is impossible for them to use it (unless they can somehow obtain a tier result of 5 with their sciences attribute). | [CRAFT] [REQ] |
| **Prototype Explosives** | Crafting Explosives | Aug +2, DIY +1, HP +6 | Passive | 16 Gadgetry; Pyrotechnician; Beta Explosives | reQuires: 16 skill points in Gadgetry, Pyrotechnician, & Beta Explosives specialties<br>You’ve perfected your beta explosives and made them user-friendly. Now anybody can use an explosive that you designate as being a prototype.<br>Resisting Explosives<br>If a person is within an explosion when it goes off, they’ll take the damage from the explosion. The damage is soakable (meaning that they can roll their defense and soak some or all of the damage).<br>A person can attempt to dive out of the explosion. In order to get out of the explosion as it’s going off, the target must spend 1 action point reflexively in order to try to move. The affected targets must make a dexterity resist in order to escape the blast. For every tier above tier 1 that the person receives with their dexterity, they may lower the marque of the explosion by 1 (normally taking the damage class down by 10). If they lower it at all, they may move to the edge of the blast. If they entirely negate the blast, they move out of it. | [CRAFT] [REQ] |
| **Major Explosion** | Crafting Explosives | Aug +2, DIY +1, HP +4 | Activating fuse +1 AP |  | Cost: Activating the Fuse +1 ap<br>You’re skill with explosives ensures that their blast radius is larger than that of anybody else. When you use major explosion with an explosive, roll below in order to increase the area of effect for the blast.<br>+5 feet spread<br>+10 feet spread<br>+15 feet spread<br>+20 feet spread<br>Note: You can, at your discretion, take a lower spread result. | [ACTION] |
| **Optician** | Crafting Eyewear | Aug +2, DIY +1, HP +4 | Passive (crafting) |  | While you’re friends are out there becoming master swordsmen and crafting great war-engines, you’ve been learning how to craft goggles. You can now create eyewear.<br>Unless you’ve gained extra eyes or somehow have grafted eyewear, you are limited to looking through one piece of eyewear. Even if you have multiple sets of eyes, you can only look through a single piece of eyewear at a time.<br>Without spending any money, you can build and maintain several sets of eyewear based on your current Do-It-Yourself (DIY) score. These eyewears can then be upgraded with augments. You’ll learn 2 augments from this specialty, which can be selected under “eyewear augments” below. These augments have marques. At lower levels, you’ll start with Marque I augments. As your skill in Gadgetry improves, your marques will increase. See the “Crafting” page at the beginning of this chapter for more information.<br>Each eyewear can be upgraded with 3 augments. Some materials can only be upgraded twice (like wooden eyewear) or just once (like organic ones). Sometimes an augment will take up multiple augment slots. For example, the “alert” augment is worth<br>3 slots, so an eyewear has 0 more available slot for an augment after “alert” has been applied.<br>numBer oF eyewears you Can maintain<br>Without needing to buy pieces or parts, you can build some sets of eyewear entirely out of scraps. These eyewears must be constantly maintained by you and stop working soon after leaving your care. You may build and maintain a number of eyewears based on your DIY score. You may build new eyewears or augment old ones during any period of downtime you have. your Diy: 1 2 3 4 5 6<br>you Can BuiLD: 3 3 4 4 4 5<br>your Diy: 7 8 9 10 11 12<br>you Can BuiLD: 5 5 6 6 6 7<br>the Cost oF eyewear<br>If you need to build eyewear that you can’t build for free from your DIY score, you will need to buy the materials for it. Every augment will increase the price. The higher the marque, the greater the price. The market price for an augment can be found in the chart below.<br>marQue I II III IV<br>market priCe 6 princes 30 princes 150 princes 750 princes If you are building the augment, you pay 1/5th the price, which is the same as if you were buying an augment one marque lower. (As in, the material cost for a Marque III augment is the market price fo a Marque II augment.) The material cost for a Marque 1 augment is 1 prince and 2 dukes. | [AUG] [DIY] [CRAFT:eyewear] |
| **Beta Eyewear** | Crafting Eyewear | Aug +2, DIY +1, HP +4 | Passive | 4 Gadgetry; Optician | reQuires: 4 skill points in Gadgetry & Optician specialty You thought you were being clever when you decided to add a bunch of extra lenses and loupes onto your monocle. Instead, now nobody else can figure out how to use them. Such eyewears have two more slots for you to place augments into. If anybody other than you attempts to use one of your beta eyewears, they must succeed in rolling a science result one tier higher than the highest level marque you have on your eyewear. If your eyewear has a Marque IV augment, it is impossible for them to use it (unless they can somehow obtain a tier result of 5 with their science attribute). | [CRAFT] [REQ] |
| **Prototype Eyewear** | Crafting Eyewear | Aug +2, DIY +1, HP +5 | Passive | 16 Gadgetry; Optician; Beta Eyewear | reQuires: 16 skill points in Gadgetry, Optician, & Beta Eyewear You’ve perfected your beta eyewears and made them user-friendly. Now anybody can use an eyewear that you designate as being a prototype. | [CRAFT] [REQ] |
| **Trinket Crafter** | Crafting Trinkets | Aug +2, DIY +1, HP +4 | Passive (crafting) |  | You can create trinkets, a catch-all term for small contraptions that do some really unique things.<br>numBer oF trinkets you Can maintain<br>Without needing to buy pieces or parts, you can build some trinkets entirely out of scraps. These trinkets must be constantly maintained by you and stop working soon after leaving your care. You may build and maintain a number of trinkets based on your DIY score. You may build new trinkets or replace old ones during any period of downtime you have.<br>your Diy: 1 2 3 4 5 6<br>you Can BuiLD: 4 5 5 6 6 7<br>your Diy: 7 8 9 10 11 12<br>you Can BuiLD: 7 8 8 9 9 10<br>the Cost oF trinkets<br>If you need to build a trinket that you can’t build for free from your DIY score, you will need to buy the materials for it. Each trinket has a slight variation in cost, and that cost will be noted below the trinket (in a chart showing the market prices).<br>If you are building the trinket, you pay 1/5th the price, which is the same as if you were buying a trinket one marque lower. (As in, the material cost for a Marque III trinket is the market price fo a Marque II trinket.) The material cost for a Marque<br>1 trinket is 1/5th the price of the Marque I trinket. | [AUG] [DIY] [CRAFT:trinket] |

##### Gadgetry – explosives (p.247–251)
- Thrown like a **light thrown weapon**; lands in the target space even on a miss. **Activate 1 AP** (draw + activate together 1 AP), **throw 2 AP**; detonates at the **start of your next turn**.
- Damage **10 per marque** (mQ I 10 … mQ IV 40) to target space + all 8 adjacent; soakable.
- Escape: 1 AP reflexive Dex resist; each tier above T1 lowers the explosion's marque by 1 (move to edge; fully negated → move out).
- Base price: mQ I 5 pr, II 25, III 125, IV 625. Augment price: 8 / 40 / 200 / 1,000 pr (mQ I material 1 pr 6 dukes).
- DIY → explosives: 1:5, 2:6, 3:6, 4:7, 5:7, 6:8, 7:8, 8:9, 9:9, 10:10, 11:10, 12:11.

| Explosive augment | Slots | mQ I | mQ II | mQ III | mQ IV | Notes |
|---|---|---|---|---|---|---|
| Banshee | 1 | deafened 1 turn | 2 | 3 | 4 | |
| Concealable | 1 | +3 Cunning to hide it | +6 | +9 | +12 | |
| Concussive | 1 | disoriented 1 turn | 2 | 3 | 4 | |
| Damaging | 1 | 11 dmg per marque | 12 | 13 | 14 | |
| Delay | 1 | set timer in turns | – | – | – | always mQ I |
| Extended Blast (req. mQ II explosives) | 1 | +5 ft (at one marque lower damage) | +10 | +15 | +20 | |
| Flare | 1 | light 25 ft (+25 dim) for 2 turns | 4 | 6 | 8 | |
| Flash | 1 | blinded 1 turn | 2 | 3 | 4 | |
| Flypaper | 1 | sticks to organic/wood armor: 2 AP + full resist or no dodge | – | – | – | always mQ II |
| Gear-Rattler | 2 | automaton stunned 1 AP / vehicle uncontrollable 1 AP | 2 | 3 | 4 | |
| Implosion | 1 | pulled 5 ft to center | 10 | 10 | 15 | |
| Knockback | 1 | pushed 5 ft | 10 | 10 + prone | 15 + prone | |
| Latch | 1 | 1 AP to remove or can't dodge; called shot location applies | – | – | – | always mQ II |
| Launching | 1 | +10 ft range | +20 | +30 | +40 | |
| Magnetic | 1 | sticks to metal armor (or heaviest within 5 ft) | – | – | – | always mQ II |
| Melter | 2 | −1 soak class (until breather) | −1 | −2 | −2 | |
| Proximity Fuse | 1 | detonates when someone enters the area | – | – | – | always mQ II |
| Powerful Blast | 1 | Dex resist counts 1 tier lower | – | – | – | always mQ II |
| Quick-Set | 1 | activation −1 AP (usually 0) | – | – | – | always mQ II |
| Remote Activation | 1 | remote trigger 25 ft | 50 | 75 | 100 | 1 AP to trigger |
| Searing | 1 | T1 burns (−1 Def) | T2 (−3) | T3 (−5) | T4 (−7) | |
| Slippery | 1 | picking it up: 2 AP + Dex T2 | T3 | T4 | impossible | |
| Smoking | 1 | blinding smoke for 1 turn | 2 | 3 | 4 | |

**Book texts:**

**Banshee** — *Explosive Augment*  
> The blast releases an ear-splitting wail, causing its victims to become temporarily deafened (and greatly annoying everybody else).  
> Deafened for 1 turn  
> Deafened for 2 turns  
> Deafened for 3 turns  
> Deafened for 4 turns  

**Concealable** — *Explosive Augment*  
> The bomb is camouflaged and can be concealed in its environment or on a character’s body. The character gains bonuses on any cunning rolls used to hide the explosive.  
> +3  
> +6  
> +9  
> +12  

**Concussive** — *Explosive Augment*  
> Characters caught within the blast are subject to a powerful pulse, causing their brains to rattle in their skulls as their heads are jerked by the shockwave.  
> Disoriented for 1 turn  
> Disoriented for 2 turns  
> Disoriented for 3 turns  
> Disoriented for 4 turns  

**Damaging** — *Explosive Augment*  
> The blast is souped-up to be more powerful, dealing greater amounts of total damage to those caught within its range.  
> 11 damage per the Explosive’s Marque  
> 12 damage per the Explosive’s Marque  
> 13 damage per the Explosive’s Marque  
> 14 damage per the Explosive’s Marque  

**Delay** — *Explosive Augment*  
> The bomb can be set to automatically go off in a number of turns specified by the player.  
> Note: This augment always acts as marque I for the purposes of determining cost, though you can learn this augment despite your skill in gadgetry.  

**Extended Blast** — *Explosive Augment*  
> reQuires: Marque II Explosives  
> The bomb has a greater radius of effect. The bomb acts normally, but also blasts out beyond its normal range. The bomb does damage of one marque lower than its own marque beyond its normal range.  
> 5 feet further  
> 10 feet further  
> 15 feet further  
> 20 feet further  

**Flare** — *Explosive Augment*  
> The explosion leaves behind a piece of material which burns brightly like a flare, lighting the area within 25 feet for several turns. Dim light extends for an additional 25 feet from the source.  
> 2 turns  
> 4 turns  
> 6 turns  
> 8 turns  

**Flash** — *Explosive Augment*  
> The blast releases a powerful flash of light, causing temporary blindness to all within the area of the explosion. Blinded for 1 turn  
> Blinded for 2 turns  
> Blinded for 3 turns  
> Blinded for 4 turns  

**Flypaper** — *Explosive Augment*  
> If the target is wearing organic or wooden armor, the bomb sticks to them like a magnet. The target must spend 2 action point and fully resist the augment or be denied their ability to evade the blast.  
> If the target is not wearing organic or wooden armor, it falls to the ground in front of them.  
> Note: This augment always acts as marque II for the purposes of determining cost, though you can learn this augment despite your skill in engineer.  

**Gear-Rattler** — *Explosive Augment*  
> takes up 2 augment sLots on an expLosive  
> The bomb is built to explode in such a way that it disables machinery, rattling gears and causing it to become stunned. When an automaton is effected by this augment, it is stunned for a number of action points.  
> Stunned for 1 AP  
> Stunned for 2 AP  
> Stunned for 3 AP  
> Stunned for 4 AP  
> When a vehicle is effected by an explosive with this augment, it is uncontrollable and moves directly forward for a number of action points.  
> Cannot be controlled for 1 AP  
> Cannot be controlled for 2 AP  
> Cannot be controlled for 3 AP  
> Cannot be controlled for 4 AP  

**Implosion** — *Explosive Augment*  
> Your explosive pulls anyone within its blast radius towards its epicenter when it explodes.  
> Pulled 5 feet towards the explosion’s center  
> Pulled 10 feet towards the explosion’s center  
> Pulled 10 feet towards the explosion’s center  
> Pulled 15 feet towards the explosion’s center  

**Knock Back** — *Explosive Augment*  
> The blast sends out a shock wave which knocks opponents back. Opponents who are unable to dodge the blast are pushed back from the center of the blast and may be knocked prone. Pushed back 5 feet  
> Pushed back 10 feet  
> Pushed back 10 feet and prone  
> Pushed back 15 feet and prone  

**Latch** — *Explosive Augment*  
> The bomb contains a clamp which latches it to opponents. When you throw or otherwise attach the bomb, the opponent must spend 1 action point to remove the bomb or be denied their ability to evade the blast. Also, if you make a called shot when attaching the weapon, the blast counts as a called shot to the called shot location.  
> Note: This augment always acts as marque II for the purposes of determining cost, though you can learn this augment despite your skill in gadgetry.  

**Launching** — *Explosive Augment*  
> The bomb is built to be launchable, increasing the distance that it can be fired.  
> +10 feet  
> +20 feet  
> +30 feet  
> +40 feet  

**Magnetic** — *Explosive Augment*  
> If the target is wearing metal armor, the bomb sticks to them like flypaper. The target must spend 2 action point and fully resist the augment or be denied their ability to evade the blast. If the target is not wearing metal armor, it will stick on to any person within 5 feet wearing the heaviest metal armor. (If multiple people are wearing equally heavy armor within 5 feet, have them roll randomly to see who wins the right to wear the magnetic explosive. The highest roller gets the bomb.) Note: This augment always acts as marque II for the purposes of determining cost, though you can learn this augment despite your skill in gadgetry.  

**Melter** — *Explosive Augment*  
> takes up 2 augment sLots on an expLosive  
> The blast splashes molten metal onto armor and clothing, decreasing its potency and melting through it, causing it to be less useful until it can be repaired (which can normally be done during a breather).  
> -1 soak class  
> -1 soak class  
> -2 soak class  
> -2 soak class  

**Proximity Fuse** — *Explosive Augment*  
> The bomb is set up with a fuse that causes it to detonate when somebody walks within the bomb’s blast area. Characters attempting to pass through the area without detonating the fuse must move no faster than 10 feet per action point and roll to resist setting off the trigger.  
> In order to activate a proximity fuse, you must first spend the usual 1 action point to activate the fuse, then either drop or throw it. The fuse effect becomes active at the end of your turn. Note: This augment always acts as marque II for the purposes of determining cost, though you can learn this augment despite your skill in gadgetry.  

**Powerful Blast** — *Explosive Augment*  
> The blast occurs with such speed that it is more difficult to jump out of its way. Characters who wish to use their dexterity to resist the blast must act as if their dexterity roll to resist the blast was one tier lower.  
> Note: This augment always acts as marque II for the purposes of determining cost, though you can learn this augment despite your skill in gadgetry.  

**Quick-Set** — *Explosive Augment*  
> Activating the fuse on an explosive costs 1 less action point (normally bringing the cost down to 0 action points). Note: This augment always acts as marque II for the purposes of determining cost, though you can learn this augment despite your skill in gadgetry.  

**Remote Activation** — *Explosive Augment*  
> You have a trigger device that lets you activate the explosive from a distance whenever you so desire. It must have been set previously (for at least 1 turn) and you cannot be outside of a certain distance (based on the marque). An explosive with remote activation will not go off until you so designate and using the remote activation costs 1 action point.  
> 25 foot range  
> 50 foot range  
> 75 foot range  
> 100 foot range  

**Searing** — *Explosive Augment*  
> Victims caught within the white phosphorous blast find their skin covered in hot material, searing the skin. These burns will recover during the victim’s next breather.  
> Tier 1 Burns (-1 on defense rolls)  
> Tier 2 Burns (-3 on defense rolls)  
> Tier 3 Burns (-5 on defense rolls)  
> Tier 4 Burns (-7 on defense rolls)  

**Slippery** — *Explosive Augment*  
> When your explosive is thrown, it begins to secrete a slimy liquid, making it difficult to pick up. It costs 2 action points to attempt to pick your explosive up, and the person attempting to do so must roll their Dexterity.  
> Tier 2 Dexterity to pick it up  
> Tier 3 Dexterity to pick it up  
> Tier 4 Dexterity to pick it up  
> Impossible (Unless you can somehow attain a Tier 5 Dexterity result)  

**Smoking** — *Explosive Augment*  
> The blast fills the area with a thick screen of smoke, causing those within the area to be blinded.  
> Dissipates in 1 turn  
> Dissipates in 2 turns  
> Dissipates in 3 turns  
> Dissipates in 4 turns  


##### Gadgetry – eyewear (p.252–254)
One eyewear at a time. Augment price 6 / 30 / 150 / 750 pr (mQ I material 1 pr 2 dukes). DIY → eyewear: 1:3, 2:3, 3:4, 4:4, 5:4, 6:5, 7:5, 8:5, 9:6, 10:6, 11:6, 12:7.

| Eyewear augment | Slots | mQ I | mQ II | mQ III | mQ IV | Notes |
|---|---|---|---|---|---|---|
| Alert | 3 | **+1 Evade** | +2 | +3 | +4 | `[STAT:Eva]` |
| Dark Adaptor | 1 | see normally in poor lighting | poor | total darkness | total | |
| Far-Sight | 1 | +1,000 ft vision | +2,000 | +3,000 | +4,000 | |
| Frightening Faceplate | 1 | +2 Cunning intimidation | +4 | +8 | +16 | |
| Happy Place Vision | 3 | never scared or flustered | – | – | – | always mQ II |
| Heat Detection | 1 | see people through poor cover | light | medium | heavy | |
| Inventory Investigator | 1 | 1 AP: knows if concealed items (25 ft) | how many | identifies them | + all items & augments | |
| Pin-Pointing | 1 | 1 AP before firing: +1 Acc | +2 | +3 | +4 | `[COND]` |
| Poison Detection | 1 | +3 notice poisons | +6 | +9 | +12 | |
| Protective | 1 | +1 soak vs eye called shots, +3 Brute vs eye effects | +2/+6 | +3/+9 | +4/+12 | |
| Tinted | 1 | +3 resist flash-blinding | +6 | +9 | +12 | |
| Weatherproof | 1 | no penalty looking through weather | – | – | – | always mQ II |
| Zoom Lens | 1 | 1 AP: +50 ft range (non-thrown ranged) | +100 | +150 | +200 | |

**Book texts:**

**Alert** — *Eyewear Augment*  
> takes up 3 augment sLots on eyewear  
> Alert goggles have small sirens built into them which go off whenever they sense something headed in your direction. Small lights in the lenses point you in the direction of the objects in question.  
> +1 on evade rolls  
> +2 on evade rolls  
> +3 on evade rolls  
> +4 on evade rolls  

**Dark Adaptor** — *Eyewear Augment*  
> The eyewear is built to allow you to see in the dark as if it were normal daytime vision.  
> Poor Lighting  
> Poor Lighting  
> Total Darkness  
> Total Darkness  

**Far-Sight** — *Eyewear Augment*  
> Far-sight goggles allow the wearer to see things at distances that seem superhuman.  
> Can see 1,000 feet further away with ease  
> Can see 2,000 feet further away with ease  
> Can see 3,000 feet further away with ease  
> Can see 4,000 feet further away with ease  

**Frightening Faceplate** — *Eyewear Augment*  
> You’ve added decoration to your eyewear designed to make your face more intimidating while wearing them. This gives you a bonus when intimidating someone  
> +2 to Cunning for intimidation  
> +4 to Cunning for intimidation  
> +8 to Cunning for intimidation  
> +16 to Cunning for intimidation  

**Happy Place Vision** — *Eyewear Augment*  
> takes up 3 augment sLots on eyewear  
> Regardless of what kind of situation you are in, Happy Place Vision makes whatever you fear the most look like your favorite dessert! While using eyewear with Happy Place Vision, you will never become scared or flustered.  
> Note: This augment always acts as marque II for the purposes of determining cost, though you can learn this augment despite your skill in gadgetry.  

**Heat Detection** — *Eyewear Augment*  
> Your eyewear can pick up heat signitures on other people, allowing you to faintly see people through cover. You can see people through degrees of cover based on your marque.  
> Poor Cover  
> Light Cover  
> Medium Cover  
> Heavy Cover  

**Inventory Investigator** — *Eyewear Augment*  
> Cost: 1 AP to activate  
> Perfect for lawmen searching hoodlums for hidden weaponry (and for pickpockets sizing up a potential target), you’ve augmented your googles with the ability to see some of the items a target within 25 feet has concealed.  
> Can tell if they have concealed items, but can’t identify Knows how many concealed items they have, but can’t identify them  
> Identifies all concealed items on target  
> Identifies all items on target and determines if they are  

**Pin-Pointing** — *Eyewear Augment*  
> Cost: 1 AP to activate  
> The user of pin-pointing eyewear is capable of improving his or her depth perception and accuracy using a cross-hair and a series of finely tuned zoom lenses. The lenses must be adjusted, so the user must spend 1 action point before firing to reap its effects.  
> +1 to accuracy  
> +2 to accuracy  
> +3 to accuracy  
> +4 to accuracy  

**Poison Detection** — *Eyewear Augment*  
> Poison-detecting eyewear reacts to invisible poisons, helping to alert the wearer of possible threatening chemicals.  
> +3 to notice poisons  
> +6 to notice poisons  
> +9 to notice poisons  
> +12 to notice poisons  

**Protective** — *Eyewear Augment*  
> Protective eyewear add extra tiers of soak and resist bonuses against attacks that are directed against the eyes.  
> +1 soak class against called shots to the eyes & +3 on Brute resists against things that affect eyes  
> +2 soak class against called shots to the eyes & +6 on Brute resists against things that affect eyes  
> +3 soak class against called shots to the eyes & +9 on Brute resists against things that affect eyes  
> +4 soak class against called shots to the eyes & +12 on Brute resists against things that affect eyes  

**Tinted** — *Eyewear Augment*  
> Tinted eyewear not only looks super-cool, but also prevents the user from experiencing the negative effects of some flashes of light.  
> +3 to resist being blinded from flashes  
> +6 to resist being blinded from flashes  
> +9 to resist being blinded from flashes  
> +12 to resist being blinded from flashes  

**Weatherproof** — *Eyewear Augment*  
> The eyewear allows you to see well through sleet, snow, and rain. You take no penalty for looking through inclement weather. Note: This augment always acts as marque II for the purposes of determining cost, though you can learn this augment despite your skill in gadgetry.  

**Zoom Lens** — *Eyewear Augment*  
> Cost: 1 AP to activate  
> Zoom lenses are used commonly by long-ranged riflemen in order to increase their range on the battlefield. For an extra action point to adjust, ranged weapon users (except those using throwing weapons) may gain a bonus to their range.  
> +50 feet  
> +100 feet  
> +150 feet  
> +200 feet  


##### Gadgetry – trinkets (p.255–262)
Each trinket has its own size, cost and marque table; material cost = price of one marque lower (mQ I: 1/5 of mQ I price). DIY → trinkets: 1:4, 2:5, 3:5, 4:6, 5:6, 6:7, 7:7, 8:8, 9:8, 10:9, 11:9, 12:10.

| Trinket | Size | Use | mQ I | mQ II | mQ III | mQ IV | Price I/II/III/IV (pr) |
|---|---|---|---|---|---|---|---|
| Aether Pointer | L | 2 AP, Acc vs Eva, Cunning resist | blurry −2 Acc/Eva to end of next turn | 2 turns | 3 | 4 | 4/20/100/500 |
| Alarm Box | L | 1 AP arm; Cunning resist | approacher deafened 1 turn | 2 | 3 | 4 | 4/20/100/500 |
| Alchemical Tooth | L | 0 AP bite-release potion | single use | refill at breather | refill 3 AP | refill 1 AP | 3/15/75/375 |
| Collapsible Ladder | M/H | set up | 10 ft, 10 AP | 20 ft, 7 AP | 30 ft, 4 AP | 40 ft, 2 AP | 5/25/125/625 |
| Engineer's Patch | M | 2 AP on vehicle/automaton | +4 wounds (temp) | 8 | 12 | 16 | 6/30/150/750 |
| Extending Periscope | M | 1 AP per 5 ft | 20 ft | 40 | 60 | 80 | 4/20/100/500 |
| Gasmask | L | 3 AP to put on | +4 resist gases | +8 | +12 | +16 | 4/20/100/500 |
| Grabnet | M | thrown attack; target grabbed & can only remove net | 1 AP to remove | 2 | 3 | 4 | 3/15/75/375 |
| Grapple-Gun | M | 1 AP launch/unlatch/retract, 50 ft line | climb 20 ft per AP | 30 | 40 | 50 | 6/30/150/750 |
| Grease Guzzler | L | 3 AP, 3 uses; Dex T2 or prone | 5×5 ft | 10×5 | 10×10 | 15×10 | 5/25/125/625 |
| Handcuffs | L | 1 AP on grabbed limb; Brute to break | T2 | T3 | T4 | impossible | 3/15/75/375 |
| Hover Pack | H | – | vertical 5 ft per move | 10 | 15 | 20 | 10/50/250/1,250 |
| Illumitorch | L | 1 AP | light 25 ft | 50 | 75 | 100 | 2/10/50/250 |
| Insta-Bridge | M | 1 AP per 10 ft cranked, 5 ft wide | max 25 ft | 50 | 75 | 100 | 6/30/150/750 |
| Jaws of Life | M | 2 AP prying | +4 Brute | +8 | +12 | +16 | 4/20/100/500 |
| Metal Cutter | M | 3 AP | cuts 3 in metal | 6 in | 1 ft | 3 ft | 4/20/100/500 |
| Messenger Sphere | L | 2 AP load, 3 AP launch | 185 ft/turn (~500 mi/day) | 370 | 555 | 925 | 7/35/175/875 |
| Mold-Maker | L | ~2 min | copies light items (base material cost, no augments) | medium | heavy | super-heavy | 3/15/75/375 |
| Mostly-Universal Lock | L | 1 AP lock / ranged called shot throw | 3 AP to pick | 5 | 7 | 10 | 5/25/125/625 (keys 5 dukes, material 1 duke) |
| Omni-Trinket | L+ | swap at breather | combines 2 trinkets | 4 | 6 | 10 | 4/20/100/500 |
| Palm Injector | L | 0 AP inject | reload 4 AP | 3 | 2 | 1 | 3/15/75/375 |
| Parachute Glider | M | 1 AP (reflexive) | no fall damage, hover 1 turn | 2 | 5 | 10 | 5/25/125/625 |
| Pitcase | M | 1 AP place / 3 AP throw (25 ft) | drills 5-ft-wide pit up to 15 ft; or tunnel 15 ft per AP | – | – | – | 25 (no marques) |
| Portable Doorframe | M | deploy/retract | 2 AP | 1 AP | 0 AP | 0 AP reflexive | 4/20/100/500 (heavy cover when closed) |
| Porta-Bull | L | 3 AP, throw 50 ft | lowers cover 1 degree | 2 | 3 | 4 | 5/25/125/625 |
| Propeller Boots | M | 2 AP activate | +5 swim | +10 | +15 | +20 | 4/20/100/500 |
| Pulse Detector | L | 2 AP; Cunning/Spirit resist ≥ marque | heartbeats 25 ft | 50 | 75 | 100 | 6/30/150/750 |
| Reasonable Doubt | L | 1 AP place / 2 AP throw | picks 1 AP per turn | 2 | 3 | 4 | 8/40/200/1,000 |
| Spring-Loaded Sleeve | L | 0 AP release to hand | retract 2 AP | 1 | 0 | 0 reflexive | 3/15/75/375 |
| Toolbelt | M | items count as drawn (0 AP swap), unconcealable, −8 vs sunder | 2 light items | 4 | 6 | 8 | 4/20/100/500 |
| Vacuum of Fire | M | 2 AP release fire (10 ft) | −1 AP to extinguish (min 1) | −2 | −3 | −4 | 10/50/250/1,250 |
| Walker | M | 1 AP, walks 20 ft/turn, triggers traps | 10 dmg to break | 20 | 30 | 40 | 4/20/100/500 |
| Wall-Scaler | L | one hand | climbs 10 ft/turn | 20 | 30 | 40 | 4/20/100/500 |
| Water Filter | L | 2 AP per vial | 3 uses | 15 | 75 | 500 | 3/15/75/375 (DIY-made never breaks) |

(Several trinkets overlap with the Spendo/MaskedMen shop items in §5.12 — shop versions are fixed-marque retail products.)

**Book texts:**

**Aether Pointer** — *Trinket*  
> size: Light  
> resist: Cunning (marques down)  
> aCtivation Cost: 2 AP  
> A miniscule, highly concentrated beam of light is emitted by this contraption through the use of a weak aether resonator. Not large enough to light much of anything, the best use of this object is shining it into the eyes of others for your own enjoyment. (If you attempt to point the aether pointer at somebody’s eyes, you must make an accuracy versus their evade, and then they must resist the effect.)  
> Blurry vision (-2 to accuracy and evade) until the end of their next turn  
> Blurry vision (-2 accuracy & evade) for the next 2 turns Blurry vision (-2 accuracy & evade) for the next 3 turns Blurry vision (-2 accuracy & evade) for the next 4 turns marQue I II III IV  
> market priCe 4 princes 20 princes 100 princes 500 princes  

**Alarm Box** — *Trinket*  
> size: Light  
> resist: Cunning (marques down)  
> aCtivation Cost: 1 AP (see below)  
> This small, unremarkable box can be activated and deactivated for 1 action point. Whenever someone enters a space adjacent to the person carrying an activated alarm box, its pivoting speaker turns toward them and blasts an ear-piercing siren. Afterward, the alarm box shuts down, requiring it to be reactivated. Someone must move towards the alarm box for it to sound; carrying or throwing an alarm box past someone or activating an alarm box for use against someone already adjacent to you will not activate its alarm.  
> Deafened (-2 evade) for 1 turn  
> Deafened (-2 evade) for 2 turns  
> Deafened (-2 evade) for 3 turns  
> Deafened (-2 evade) for 4 turns  
> marQue I II III IV  
> market priCe 4 princes 20 princes 100 princes 500 princes  

**Alchemical Tooth** — *Trinket*  
> size: Light  
> Cost: 0 AP  
> This fake tooth is in reality a small capsule you can fill with a dose of an alchemical potion! For no action point cost during your turn you can bite down on it to release the potion into your system. Tooth is crushed after every use, ruining your smile Tooth can be refilled during a breather (15-30 minute break)  
> Tooth can be refilled for 3 AP  
> Tooth can be refilled for 1 AP  
> marQue I II III IV  
> market priCe 3 princes 15 princes 75 princes 375 princes  

**Collapsible Ladder** — *Trinket*  
> size: Medium or Heavy (when unwound)  
> The collapsible ladder is a bundle of rods that, when unwound, form together to make a ladder. The ladder requires action points to set up and take down, and it only goes so high, depending on the marque of the ladder.  
> 10 feet high and requires 10 AP to set up  
> 20 feet high and requires 7 AP to set up  
> 30 feet high and requires 4 AP to set up  
> 40 feet high and requires 2 AP to set up  
> marQue I II III IV  
> market priCe 5 princes 25 princes 125 princes 625 princes  

**Engineer’s Patch** — *Trinket*  
> size: Medium  
> appLiCation Cost: 2 AP  
> Engineer’s patches are magnetic patches able to quickly attach and shape to an automaton or vehicle, temporarily repairing it. Patches are not a perminant fix. Patches can be hit as a called shot location on the item they’re attached to. If the patch is hit by a called shot, its wearer will lose the regained wounds from the patch as well as take the damage from the attack. Restores 4 wounds  
> Restores 8 wounds  
> Restores 12 wounds  
> Restores 16 wounds  
> marQue I II III IV  
> market priCe 6 princes 30 princes 150 princes 750 princes  

**Extending Periscope** — *Trinket*  
> size: Medium  
> Cost: 1 AP per 5 feet extended  
> You have a one-handed and portable periscope that can be maneuvered around any number of corners, out of water, or out of a cloud of smoke. The periscope is not very discreet in-and-of itself, and trying to be sneaky about it will require a cunning roll as if you were hiding yourself. It costs 1 action point to extend your periscope 5 feet, and the periscope can be extended a maximum distance based on its marque.  
> 20 feet  
> 40 feet  
> 60 feet  
> 80 feet  
> marQue I II III IV  
> market priCe 4 princes 20 princes 100 princes 500 princes  

**Gasmask** — *Trinket*  
> size: Light  
> Cost to put on: 3 AP  
> Not only does this poignant fashion statement require no hands when it’s strapped to your face, it also helps filter your breathing, protecting you from harmful airborne chemicals. Only one can be worn at a time.  
> +4 to resists against alchemical gases  
> +8 to resists against alchemical gases  
> +12 to resists against alchemical gases  
> +16 to resists against alchemical gases  
> marQue I II III IV  
> market priCe 4 princes 20 princes 100 princes 500 princes  

**Grabnet** — *Trinket*  
> size: Medium  
> Cost: as a thrown weapon attack (generally 2 AP) A medium-sized restraining device, people you successfully hit with your net act as if they have been grabbed without you having to be up-close-and-personal with them. While under your net they cannot take any actions other than removing the net capturing them. It can be used on enemies adjacent to you or shot through a firearm with the delivery augment.  
> Costs 1 AP to remove the grabnet  
> Costs 2 AP to remove the grabnet  
> Costs 3 AP to remove the grabnet  
> Costs 4 AP to remove the grabnet  
> marQue I II III IV  
> market priCe 3 princes 15 princes 75 princes 375 princes  

**Grapple-Gun** — *Trinket*  
> size: Medium  
> Cost: 1 AP to launch, 1 AP to unlatch, 1 AP to retract This is a metal grappling hook launching device. The hook is designed to mechanically bend outward, attaching itself onto most surfaces perfectly. You can unlatch the hook from any surface with a simple tug on its line. It can stick to most ledges and flat surfaces regardless of whether it is rocky, magnetic, rough, or slick. The maximum length of chain, cable, or rope that it can successfully propel upwards is 50 feet. How fast it can pull you upwards is based on its marque. If you can get footing on the surface you are climbing, your climb speed is added to the speed of your grappling hook. While hanging from one grappling hook, you can easily fire another one further upwards with your other hand if you have a spare.  
> 20 feet per action point spent retracting  
> 30 feet per action point spent retracting  
> 40 feet per action point spent retracting  
> 50 feet per action point spent retracting  
> marQue I II III IV  
> market priCe 6 princes 30 princes 150 princes 750 princes  

**Grease Guzzler** — *Trinket*  
> size: Light  
> resist: Dexterity (negates, see below)  
> aCtivation Cost: 3 AP  
> This little contraption pours slippery grease all over a small area. Anybody who walks into the space of a grease guzzler must make a Dexterity result of tier 2 or fall prone. Upon standing up and trying to move, they must make the resist again. A grease guzzler may be used up to three times before having to refill it with the slippery grease.  
> Covers a space 5 feet x 5 feet  
> Covers a space 10 feet x 5 feet  
> Covers a space 10 feet x 10 feet  
> Covers a space 15 feet x 10 feet  
> marQue I II III IV  
> market priCe 5 princes 25 princes 125 princes 625 princes  

**Handcuffs** — *Trinket*  
> size: Light  
> resist: Brute (negates)  
> Cost: 1 AP  
> Handcuffs allow you to put a hold on someone you’re already grabbing. Perfect for those gentlemen adventurers of weaker physique, you can attach one cuff of your set to any body part you currently are grabbing. Its extendable chain design allows it to tighten around the biggest (and smallest) of limbs. One set of handcuffs consists of two cuffs which can attach to one limb apiece. They remain attached until the person bound by them is able to break free or until you voluntarily remove them. Until then, the wearer of your handcuffs acts constantly grabbed. They can move, but once both cuffs are grabbing something they can’t use any limbs your handcuffs are attached to.  
> Tier 2 Brute to break free  
> Tier 3 Brute to break free  
> Tier 4 Brute to break free  
> Impossible (Unless you can somehow attain a Tier 5 Brute)  
> marQue I II III IV  
> market priCe 3 princes 15 princes 75 princes 375 princes  

**Hoverpack** — *Trinket*  
> size: Heavy  
> The hover pack is a large boxy backpack that contains a graviton sphere allowing its wearer to hover vertically.  
> May move vertically 5 feet per move  
> May move vertically 10 feet per move  
> May move vertically 15 feet per move  
> May move vertically 20 feet per move  
> marQue I II III IV  
> market priCe 10 princes 50 princes 250 princes 1250 princes  

**Illumitorch** — *Trinket*  
> size: Light  
> aCtivation Cost: 1 AP  
> An illumitorch looks, in many ways, like a normal torch. The difference is that it has a small bulb at the end. By rotating a knob, the illumitorch creates light up to a distance away determined by its marque. It can be dimmed to illuminate anywhere from 5 to the maximum feet away. If you’re using an illumitorch in a small or enclosed area, it’s likely to light the entire area.  
> 25 feet  
> 50 feet  
> 75 feet  
> 100 feet  
> marQue I II III IV  
> market priCe 2 princes 10 princes 50 princes 250 princes  

**Insta-Bridge** — *Trinket*  
> size: Medium  
> Cost: 1 AP (see below)  
> The Insta-Bridge is perfect for the more venturesome traveler. Perfect for passing over ravines or creating handy ramps up hills, the Insta-Bridge is 5 feet wide and hand-cranked. For every action point you spend cranking it, it will extend or retract 10 feet, extending as far as its maximum length. It can be cranked in and out from either of its two ends. While extended out 10 feet or more, the Insta-Bridge becomes too cumbersome to lift.  
> 25 foot maximum length  
> 50 foot maximum length  
> 75 foot maximum length  
> 100 foot maximum length  
> marQue I II III IV  
> market priCe 6 princes 30 princes 150 princes 750 princes  

**Jaws Of Life** — *Trinket*  
> size: Medium  
> Cost: 2 AP to activate  
> The jaws of life is a tool with thin, metal blades sticking out from its base. It’s used for prying things open by sliding its blades into an opening and activating it. Roll brute on behalf of the tool, using the indicated bonus.  
> +4 on the brute roll  
> +8 on the brute roll  
> +12 on the brute roll  
> +16 on the brute roll  
> marQue I II III IV  
> market priCe 4 princes 20 princes 100 princes 500 princes  

**Metal Cutter** — *Trinket*  
> size: Medium  
> Cost: 3 AP  
> The metal cutter looks like a large pair of steam-powered wire snips and functions in much the same way. Using the metal cutter requires 3 action points, but it can automatically cut through a certain thickness of metal.  
> 3 inches of metal  
> 6 inches of metal  
> 1 foot of metal  
> 3 feet of metal  
> marQue I II III IV  
> market priCe 4 princes 20 princes 100 princes 500 princes  

**Messenger Sphere** — *Trinket*  
> size: Light  
> Cost: 2 AP to insert item, 3 AP to activate  
> An efficient mode of communication, the messenger sphere appears as nothing more than a small hollow sphere you can place a single concealable item, most commonly a written note, into. A destination can be programmed into it using dials representing longitude and latitude. When activated sides of the sphere extend outward to form propellors, spinning quickly to create lift. It will then fly toward its destination at a speed based on its marque.  
> 185 feet per turn (roughly 500 miles a day)  
> 370 feet per turn (roughly 1000 miles a day)  
> 555 feet per turn (roughly 1500 miles a day)  
> 925 feet per turn (roughly 2500 miles a day)  
> marQue I II III IV  
> market priCe 7 princes 35 princes 175 princes 875 princes  

**Mold-Maker** — *Trinket*  
> size: Light  
> A trinket made for the more thrifty adventurer, the mold-maker is a blanket which hardens when it is wrapped around items of a size determined by its marque. This allows you to recreate any item you come across at its base material cost without the need of a crafter specializing in that field. The mold-maker only copies the shape of an item and thus cannot replicate augments of any kind. After so many uses the mold-maker will become stuck in the form of the last item it copied. The mold-maker takes about two minutes to use.  
> Can wrap around light or smaller items  
> Can wrap around medium or smaller items  
> Can wrap around heavy or smaller items  
> Can wrap around super-heavy or smaller items  
> Note: Most merchants won’t appreciate you making molds of their wares. Please use responsibly.  
> marQue I II III IV  
> market priCe 3 princes 15 princes 75 princes 375 princes  

**Mostly-Universal Lock** — *Trinket*  
> size: Light  
> Cost: 1 AP to lock a held item, Ranged Called Shot to throw As the name implies, this lock can secure almost anything. Doors, luggage, handcuffs, vehicles and more can be sealed shut with this device, and it takes anyone trying to lockpick it two free hands and an amount of action points based on the marque of this augment to do so. If thrown accurately, it will automatically lock any compatible item it lands on.  
> If you crafted the lock, you can also craft keys for it at no cost. Keys allow you to unlock the lock for 1 action point.  
> 3 AP to pick the lock  
> 5 AP to pick the lock  
> 7 AP to pick the lock  
> 10 AP to pick the lock  
> marQue I II III IV  
> market priCe 5 princes 25 princes 125 princes 625 princes Note: Making keys for a Mostly-Universal Lock has a material cost of 1 dukes per key and a market cost of 5 dukes.  

**Omni-Trinket** — *Trinket*  
> size: Light (see below)  
> Tired of having to switch between all of your trinkets? The omnitrinket combines trinkets together into a single item, allowing you to hold multiple trinkets at once! The omni-trinket at default is a light item, but increases in size to match the largest sized item attached to it. Items attached can be switched out during a breather (a 15-30 minute break). You must spend action points to use each item individually; you cannot combine actions to reduce action point cost.  
> Combines up to 2 Trinkets  
> Combines up to 4 Trinkets  
> Combines up to 6 Trinkets  
> Combines up to 10 Trinkets  
> marQue I II III IV  
> market priCe 4 princes 20 princes 100 princes 500 princes  

**Palm Injector** — *Trinket*  
> size: Light  
> aCtivation Cost: 0 AP  
> This trinket puts a small button in your palm, hooked up to an injector line. When you push the button (an action that requires no action points), you are injected with a single alchemical substance of your choosing. Replacing the alchemical substance after use requires a number of action points based on the marque of the palm injector.  
> 4 action points to reload  
> 3 action points to reload  
> 2 action points to reload  
> 1 action point to reload  
> Alchemical substance not included.  
> marQue I II III IV  
> market priCe 3 princes 15 princes 75 princes 375 princes  

**Parachute Glider** — *Trinket*  
> size: Medium  
> Cost: 1 AP (can be done reflexively)  
> Designed with daredevils in mind, the parachute glider is a trinket you can wear on your back. Not only will it prevent you from taking any damage from falling, it will also keep you aloft by gliding in place without falling for a number of turns based on its marque, allowing you to keep on fighting any airborne foes who sank your battle-airship. Your fall begins when your action points refresh after your final turn of gliding. The parachute glider includes a ripchord allowing you to end your time gliding prematurely for no action point cost.  
> 1 turn before falling  
> 2 turns before falling  
> 5 turns before falling  
> 10 turns before falling  
> marQue I II III IV  
> market priCe 5 princes 25 princes 125 princes 625 princes  

**Pitcase** — *Trinket*  
> size: Medium  
> Cost: 1 AP to place, 3 AP to throw  
> This trendy leather briefcase can quickly reveal the metal spiral on its side to be a collapsible drill. When placed in an adjacent space or thrown up to 25 feet away, the pitcase will drill a circle 5 feet in diameter downwards up to 15 feet (you can set it to a lower distance manually for no action point cost at any time before use). It can also be held to tunnel you in any direction at a rate of 15 feet per action point. The pitcase cannot burrow through worked stones, mountains, metals or similar materials.  
> Note: This market price for this trinket is 25 princes (and so costs 5 princes to make).  

**Portable Doorframe** — *Trinket*  
> size: Medium  
> Cost: Based on Marque (see below)  
> Designed for true eccentrics, this gadget produces a free-standing doorframe, complete with door and knobs on both sides, at a moment’s notice. This doorframe accomplishes little past putting a door between you and any pursuers, although they can simply open it for 1 action point or alternatively move around it. It easily attaches to any wall or to other doorframes, although opening it while it’s attached to a wall will reveal the solid wall behind it. It provides heavy cover to anyone standing behind it while it is freestanding and closed.  
> 2 AP to deploy/retract  
> 1 AP to deploy/retract  
> 0 AP to deploy/retract  
> 0 AP to deploy/retract (and can be done reflexively) marQue I II III IV  
> market priCe 4 princes 20 princes 100 princes 500 princes  

**Porta-Bull** — *Trinket*  
> size: Light  
> Cost: 3 AP  
> Enemies behind cover will fear your crafty visage when you walk up to their barricades and smash them with your tiny trinket. The porta-bull is a handheld device designed to attach to a single piece of cover and repeatedly beat it with a hydraulic ram until it breaks. It can be thrown a maximum of 50 feet. After a certain amount of damage to the cover it attaches itself to, the porta-bull will fall off and will need to be picked up before it can be used again. Any damage it does to a piece of cover lasts until someone can repair the cover outside of combat. This device has too much trouble staying attached to flat, unmoving surfaces to be able to ever attach to a living creature.  
> Lowers cover by one degree before falling off  
> Lowers cover by two degrees before falling off  
> Lowers cover by three degrees before falling off Lowers cover by four degrees before falling off  
> Note: The porta-bull is not strong enough to damage anything considered full cover.  
> marQue I II III IV  
> market priCe 5 princes 25 princes 125 princes 625 princes  

**Propeller Boots** — *Trinket*  
> size: Medium  
> These boots are simple looking enough, except for the large flipout device on the back. Once activated (for just 2 action points), the boots activate a propeller on the back that comes around over the heel of the boot. This grants a speed bonus to the wearer when swimming.  
> +5 to swim speed  
> +10 to swim speed  
> +15 to swim speed  
> +20 to swim speed  
> marQue I II III IV  
> market priCe 4 princes 20 princes 100 princes 500 princes  

**Pulse Detector** — *Trinket*  
> size: Light  
> Resist: Cunning or Spirit (negates, see below)  
> aCtivation Cost: 2 AP  
> This is a small, flat, metal device with a glass cover. It is able to pick up on the heartbeats of organisms around it. After picking up on a heart beat, the trinket will display it by raising small pins under the glass in the direction of the heart beat’s source. Somebody who is aware of the pulse detector can attempt to hide their heartbeat, which requires a cunning or spirit resist (target’s choice) with a result equal to the item’s marque. Detects heart beats within 25 feet  
> Detects heart beats within 50 feet  
> Detects heart beats within 75 feet  
> Detects heart beats within 100 feet  
> marQue I II III IV  
> market priCe 6 princes 30 princes 150 princes 750 princes  

**Reasonable Doubt** — *Trinket*  
> size: Light  
> Cost: 1 AP to place, 2 AP to throw  
> Worried about getting fingerprints on a lock? Perhaps you simply prefer to have someone, or something, else do the dirty work? The Reasonable Doubt lockpicking device will attach to any lock and quickly get to work picking it for you. When your action points refresh it will spend a number of action points picking the lock based off of its marque.  
> 1 AP per turn spent lockpicking  
> 2 AP per turn spent lockpicking  
> 3 AP per turn spent lockpicking  
> 4 AP per turn spent lockpicking  
> marQue I II III IV  
> market priCe 8 princes 40 princes 200 princes 1000 princes  

**Spring-Loaded Sleeve** — *Trinket*  
> size: Light  
> Cost: 0 AP to activate  
> The spring loaded sleeve holds a light weapon or small item (such as a potion vial or explosive). With a flick, you can release the spring, sending the item straight into your hand. (If your hand is not free, it’ll fall at your feet... and break, if it’s a potion vial.) Retracting the spring takes a few seconds, depending on the marque of the sleeve.  
> 2 AP to retract  
> 1 AP to retract  
> 0 AP to retract  
> 0 AP reflexively to retract (can do it during anyone’s turn)  
> marQue I II III IV  
> market priCe 3 princes 15 princes 75 princes 375 princes  

**Toolbelt** — *Trinket*  
> size: Medium  
> This utilitarian fashion accessory can store a number of light-size items. These items are considered drawn, allowing you to switch between them at no action point cost during your turn. Unfortunately any items attached to your toolbelt are unconcealable and suffer a -8 when resisting sundering. Wearing the toolbelt does not require hands.  
> Can hold two light items  
> Can hold four light items  
> Can hold six light items  
> Can hold eight light items  
> marQue I II III IV  
> market priCe 4 princes 20 princes 100 princes 500 princes  

**Vacuum Of Fire** — *Trinket*  
> size: Medium  
> Cost: 2 AP to release fire  
> What appears to be nothing more than a common household cleaning appliance is actually the latest in fire-fighting technology. When aimed at a fire of any kind within 10 feet, this suction device will decrease the amount of action points required to put the fire out to a minimum of 1 action point. Once the required action points have been spent, you can choose to extinguish the fire normally or suck the fire into your vacuum. If you choose the latter, you can spray the fire back out onto a different area or person. It retains whatever tier of fire it was previously and can be blasted anywhere within 10 feet. The vacuum can hold one charge of fire at a time. If the fire it ingests would normally destroy it from the outside, it will destroy it from the inside as well, the flame extinguishing afterwards. You can permanently extinguish a flame inside of your vacuum for no action point cost at any time.  
> -1 AP to extinguish flame (to a minimum of 1)  
> -2 AP to extinguish flame (to a minimum of 1)  
> -3 AP to extinguish flame (to a minimum of 1)  
> -4 AP to extinguish flame (to a minimum of 1)  
> marQue I II III IV  
> market priCe 10 princes 50 princes 250 princes 1250 princes  

**Walker** — *Trinket*  
> size: Medium  
> Cost: 1 AP to activate  
> This is a device that walks forward in a straight line at a speed of  
> 20 feet per turn. It weighs roughly equivalent to a gnome and sets off most traps it walks across.  
> Will take 10 damage before breaking  
> Will take 20 damage before breaking  
> Will take 30 damage before breaking  
> Will take 40 damage before breaking  
> marQue I II III IV  
> market priCe 4 princes 20 princes 100 princes 500 princes  

**Wall-Scaler** — *Trinket*  
> size: Light  
> This handheld item has a rotating, barbed head at the end. It will snatch on to any wall it is put up against and climb up it, leaving small indentions along the wall. It requires one hand to hold on to, and cannot climb up very solid walls (like a wall made out of steel) or inclines.  
> Wall-scaler can move 10 feet per turn  
> Wall-scaler can move 20 feet per turn  
> Wall-scaler can move 30 feet per turn  
> Wall-scaler can move 40 feet per turn  
> marQue I II III IV  
> market priCe 4 princes 20 princes 100 princes 500 princes  

**Water-Filter** — *Trinket*  
> size: Light  
> Cost: 2 AP per vial  
> Ideal for travelers entering less-hospitable areas of the world (or afraid of poisons), this bottle cap fits onto most vials of liquid. Its perforated top can be used to pour out any unwanted particles and chemicals, leaving you with a vial of pure water. This filter will break with repeated uses.  
> 3 uses before breaking  
> 15 uses before breaking  
> 75 uses before breaking  
> 500 uses before breaking  
> Note: A water filter made with your DIY will never break unless it leaves your care.  
> marQue I II III IV  
> market priCe 3 princes 15 princes 75 princes 375 princes  




---

## 7. Narrator chapter (Ch. 11, p.264–277) — only tool-relevant bits
- 12 XP per level (clock metaphor). Suggested award: ~1 XP per contentious situation; 3–4 XP per 4–6 h session (4/session → level every 3 sessions; 3/session → every 4). The rest of the chapter is narrator advice and NPC guidance — not extracted.

## 8. Naming decisions, corrections & open points
Rule applied: **chapter names are used, never appendix names.**

| Item | Resolution |
|---|---|
| Medical Marvel | Appendix lists it as a second "Bio-Invigoration Expert"; chapter name Medical Marvel used (Eva +1, Wnd +1, HP +11). Bio-Invigoration Expert appears once. |
| Superior Brainworks | Appendix: "Epic Brainworks" → chapter name used |
| Concentrated Stream | Appendix: "Concentrated Steam" → chapter name used |
| Combat Insight / Prototype Medicine | Appendix plural → chapter singular used |
| Backseat Driver | Stays under Ace |
| Interchangeable Parts (Armsmith) | Both entries kept (general p.176 and melee p.182, different bonuses); a third, separate one exists under Automata |
| Arching Shot | Ends with a comma in the book that should be a period; nothing is missing |
| Gas Brewer | Aug +4, DIY +1, **HP +4** |
| Seize Your Suffering | The book's example (3 wounds → 3 AP) requires ≥24 Frenzy because of the 1-per-8-points cap |
| Metal Exoskeleton | Grants no armor; keeps the armor you wear active even when broken or destroyed |
| Nobotic, Skin-Papering | Book names (my earlier "Robotic"/"Skin-Tapering" were misreadings) |
| Gas augment Arm Mutation | Resist wording "resilience result" as printed |
| Clockwork Shadow-Me | Printed requirement "Go-There" kept as printed |
| Race wounds | No race changes the 12 base wounds |
| Racial traits & stories | Still summaries: their page layout (d12 number columns, split small-caps names) defeats clean extraction |
| Rules sections (§1, §2, gear definitions) | Structured summaries, not book text |

## Appendix A – Machine-readable specialty data (JSON Lines)
Fields: `n` name, `a` attribute, `s` skill, `g` group, `b` bonuses, `c` cost/type, `r` requirements, `t` tags. Effect text is in the tables above (book text after running `add_book_texts.py`).

```jsonl
{"n": "Block with a Grab", "a": "Brute", "s": "Brawl", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 10}, "c": "0 AP reflexive", "r": "", "t": "[REFLEX]"}
{"n": "Dirty Fighting", "a": "Brute", "s": "Brawl", "g": null, "b": {"Acc": 1, "Stk": 2, "HP": 9}, "c": "Stance", "r": "", "t": "[STANCE]"}
{"n": "Drunken Boxing", "a": "Brute", "s": "Brawl", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 9}, "c": "Called shot +1 AP", "r": "", "t": "[ATTACK+1] [SCALE:Brawl] Acc +Brawl"}
{"n": "Fisticuffs", "a": "Brute", "s": "Brawl", "g": null, "b": {"Stk": 2, "Pri": 1, "HP": 10}, "c": "Stance (needs a free hand)", "r": "", "t": "[STANCE] [GEAR] [SCALE:Brawl] unarmedDC += 1 + floor(Brawl/6)"}
{"n": "Fluid", "a": "Brute", "s": "Brawl", "g": null, "b": {"Eva": 2, "Stk": 1, "HP": 7}, "c": "1 AP reflexive", "r": "", "t": "[REFLEX]"}
{"n": "Grapple", "a": "Brute", "s": "Brawl", "g": null, "b": {"Acc": 2, "Stk": 1, "HP": 10}, "c": "Stance (must be grabbing)", "r": "", "t": "[STANCE] [SCALE:Brawl-tier]"}
{"n": "Heavy-Handed", "a": "Brute", "s": "Brawl", "g": null, "b": {"Stk": 2, "Pri": 2, "HP": 9}, "c": "Unarmed attack +1 AP", "r": "", "t": "[ATTACK+1] [SCALE:Brawl-tier]"}
{"n": "Hold Steady", "a": "Brute", "s": "Brawl", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 10}, "c": "Passive", "r": "", "t": "[COND] [SCALE:Brawl] ally Acc = 3 + floor(Brawl/4)"}
{"n": "Knock Aside", "a": "Brute", "s": "Brawl", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 9}, "c": "Deflect (1 AP reflexive)", "r": "", "t": "[REFLEX] [SCALE:Brawl] deflect Eva = 3 + floor(Brawl/8)"}
{"n": "Monkey Wrestler", "a": "Brute", "s": "Brawl", "g": null, "b": {"Acc": 1, "Stk": 1, "HP": 10}, "c": "Passive", "r": "5 Brawl", "t": "[PASSIVE] [SCALE:Brawl]"}
{"n": "Reversal", "a": "Brute", "s": "Brawl", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 10}, "c": "2 AP reflexive", "r": "", "t": "[REFLEX] [SCALE:Brawl]"}
{"n": "Shrug Away", "a": "Brute", "s": "Brawl", "g": null, "b": {"Eva": 1, "Pri": 2, "HP": 10}, "c": "Passive (free)", "r": "", "t": "[COND] [SCALE:Brawl]"}
{"n": "Throat Jab", "a": "Brute", "s": "Brawl", "g": null, "b": {"Stk": 2, "Pri": 2, "HP": 11}, "c": "Called shot to neck, reflexive; resist Brute (negates)", "r": "", "t": "[REFLEX]"}
{"n": "Bone-Breaker", "a": "Brute", "s": "Brawl", "g": "Bone-Breaking", "b": {"Stk": 2, "Pri": 1, "HP": 11}, "c": "Unarmed called shot +1 AP", "r": "", "t": "[ATTACK+1]"}
{"n": "Crippling Blow", "a": "Brute", "s": "Brawl", "g": "Bone-Breaking", "b": {"Stk": 3, "Pri": 1, "HP": 9}, "c": "Bone-breaking attack +1 AP per location", "r": "Bone-Breaker; 8 Brawl", "t": "[ATTACK+X] [REQ]"}
{"n": "Combo Flow", "a": "Brute", "s": "Brawl", "g": "Combo", "b": {"Acc": 1, "Stk": 2, "HP": 10}, "c": "Passive", "r": "4 Brawl", "t": "[COND] [SCALE:hits]"}
{"n": "Combo Opener", "a": "Brute", "s": "Brawl", "g": "Combo", "b": {"Acc": 1, "Stk": 2, "HP": 10}, "c": "Unarmed attack +1 AP", "r": "Combo Flow", "t": "[ATTACK+1] [REQ]"}
{"n": "Combo Breaker", "a": "Brute", "s": "Brawl", "g": "Combo", "b": {"Acc": 1, "Eva": 1, "HP": 9}, "c": "Free", "r": "—", "t": "[REFLEX] [SCALE:Brawl]"}
{"n": "Finisher", "a": "Brute", "s": "Brawl", "g": "Combo", "b": {"Stk": 3, "Pri": 1, "HP": 9}, "c": "Free", "r": "Heavy-Handed", "t": "[COND] [REQ]"}
{"n": "Crushing Grip", "a": "Brute", "s": "Brawl", "g": "Grip", "b": {"Stk": 3, "Pri": 1, "HP": 10}, "c": "Passive", "r": "+4 Strike", "t": "[PASSIVE] [REQ:Stk≥4]"}
{"n": "Twist", "a": "Brute", "s": "Brawl", "g": "Grip", "b": {"Acc": 1, "Stk": 2, "HP": 10}, "c": "1 AP", "r": "Crushing Grip", "t": "[ACTION] [REQ]"}
{"n": "Adrenaline Surge", "a": "Brute", "s": "Frenzy", "g": null, "b": {"Eva": 1, "Stk": 1, "HP": 14}, "c": "Passive", "r": "", "t": "[COND]"}
{"n": "Backlash", "a": "Brute", "s": "Frenzy", "g": null, "b": {"Acc": 1, "Stk": 2, "HP": 11}, "c": "1 AP reflexive", "r": "7 Frenzy", "t": "[REFLEX] [SCALE:Frenzy]"}
{"n": "Burning Revenge", "a": "Brute", "s": "Frenzy", "g": null, "b": {"Stk": 3, "Pri": 1, "HP": 11}, "c": "1 AP reflexive", "r": "", "t": "[REFLEX]"}
{"n": "Carry Through", "a": "Brute", "s": "Frenzy", "g": null, "b": {"Acc": 1, "Stk": 2, "HP": 10}, "c": "Melee attack +1 AP per extra foe", "r": "", "t": "[ATTACK+X]"}
{"n": "Crimson Weapon", "a": "Brute", "s": "Frenzy", "g": null, "b": {"Stk": 3, "Pri": 1, "HP": 10}, "c": "Melee attack +1 AP; resist Brute (tiers down)", "r": "", "t": "[ATTACK+1]"}
{"n": "Fray Fighter", "a": "Brute", "s": "Frenzy", "g": null, "b": {"Eva": 1, "Stk": 2, "HP": 10}, "c": "3 AP", "r": "", "t": "[ACTION]"}
{"n": "Hundred Strikes", "a": "Brute", "s": "Frenzy", "g": null, "b": {"Acc": 1, "Stk": 2, "HP": 10}, "c": "All AP of the turn (must be at max)", "r": "", "t": "[ACTION]"}
{"n": "Liberator", "a": "Brute", "s": "Frenzy", "g": null, "b": {"Eva": 2, "Stk": 2, "HP": 10}, "c": "1 AP reflexive", "r": "", "t": "[REFLEX]"}
{"n": "Merciless", "a": "Brute", "s": "Frenzy", "g": null, "b": {"Acc": 1, "Stk": 2, "HP": 8}, "c": "Stance (can't voluntarily exit)", "r": "", "t": "[STANCE] [SCALE:Frenzy]"}
{"n": "Neverending Bloodbath", "a": "Brute", "s": "Frenzy", "g": null, "b": {"Stk": 2, "Spd": 5, "HP": 11}, "c": "Passive", "r": "", "t": "[COND]"}
{"n": "No Escape", "a": "Brute", "s": "Frenzy", "g": null, "b": {"Stk": 2, "Spd": 5, "HP": 10}, "c": "As moving, reflexive", "r": "", "t": "[REFLEX]"}
{"n": "Raging", "a": "Brute", "s": "Frenzy", "g": null, "b": {"Stk": 2, "Pri": 2, "HP": 9}, "c": "Stance", "r": "", "t": "[STANCE] [STAT:Stk += Acc+Eva+Def; Acc/Eva/Def → 0]"}
{"n": "Straining Blow", "a": "Brute", "s": "Frenzy", "g": null, "b": {"Acc": 1, "Stk": 2, "HP": 13}, "c": "As melee attack", "r": "", "t": "[ATTACK+0]"}
{"n": "Soulless Blade", "a": "Brute", "s": "Frenzy", "g": null, "b": {"Acc": 1, "Stk": 2, "HP": 9}, "c": "2 AP reflexive", "r": "", "t": "[REFLEX]"}
{"n": "Walking Destruction", "a": "Brute", "s": "Frenzy", "g": null, "b": {"Stk": 3, "Spd": 5, "HP": 10}, "c": "Move + melee attack + 2 AP", "r": "15 Frenzy", "t": "[ACTION] [REQ]"}
{"n": "Berserker", "a": "Brute", "s": "Frenzy", "g": "Bloodlust", "b": {"Acc": 1, "Stk": 2, "HP": 12}, "c": "Stance", "r": "", "t": "[STANCE] [SCALE:Frenzy] DC += 1 + floor(Frenzy/6)"}
{"n": "Bloodlust", "a": "Brute", "s": "Frenzy", "g": "Bloodlust", "b": {"Acc": 1, "Stk": 2, "HP": 10}, "c": "+1 AP when entering Berserker", "r": "Berserker; 6 Frenzy", "t": "[STANCE] [REQ] [SCALE:enemies]"}
{"n": "Unquenchable Thirst", "a": "Brute", "s": "Frenzy", "g": "Bloodlust", "b": {"Acc": 1, "Stk": 3, "HP": 11}, "c": "+1 AP after Bloodlust", "r": "Berserker, Bloodlust; 12 Frenzy", "t": "[STANCE] [REQ] [GEAR] melee AP=1"}
{"n": "Laugh Like You're Crazy", "a": "Brute", "s": "Frenzy", "g": "Masochistic", "b": {"Stk": 2, "Pri": 2, "HP": 10}, "c": "Passive; resist Spirit (negates)", "r": "", "t": "[COND]"}
{"n": "Marriage to Suffering", "a": "Brute", "s": "Frenzy", "g": "Masochistic", "b": {"Stk": 2, "Wnd": 1, "HP": 11}, "c": "Passive", "r": "Laugh Like You're Crazy", "t": "[COND] [SCALE:wounds lost]"}
{"n": "Seize Your Suffering", "a": "Brute", "s": "Frenzy", "g": "Masochistic", "b": {"Stk": 2, "Wnd": 2, "HP": 11}, "c": "Passive", "r": "8 Frenzy; Laugh Like You're Crazy; Marriage to Suffering", "t": "[COND] [SCALE:Frenzy]"}
{"n": "Brickbreaker", "a": "Brute", "s": "Overpower", "g": null, "b": {"Stk": 3, "Pri": 1, "HP": 10}, "c": "As melee attack", "r": "", "t": "[ATTACK+0]"}
{"n": "Dragging", "a": "Brute", "s": "Overpower", "g": null, "b": {"Acc": 1, "Stk": 2, "HP": 11}, "c": "Stance", "r": "", "t": "[STANCE]"}
{"n": "Follow-Through", "a": "Brute", "s": "Overpower", "g": null, "b": {"Acc": 1, "Stk": 2, "HP": 10}, "c": "Passive", "r": "4 Overpower", "t": "[COND]"}
{"n": "Heavy Hitter", "a": "Brute", "s": "Overpower", "g": null, "b": {"Acc": 1, "Stk": 3, "HP": 9}, "c": "Stance", "r": "4 Overpower", "t": "[STANCE] [GEAR] [SCALE:Overpower] DC += floor(Overpower/4)"}
{"n": "Keep Them Down", "a": "Brute", "s": "Overpower", "g": null, "b": {"Acc": 1, "Stk": 2, "HP": 11}, "c": "Heavy+ melee attack", "r": "", "t": "[COND]"}
{"n": "Monstrous Attacks", "a": "Brute", "s": "Overpower", "g": null, "b": {"Stk": 3, "Def": 1, "HP": 10}, "c": "Super-heavy melee attack +1 AP", "r": "", "t": "[ATTACK+1] [SCALE:Overpower] DC += 2 + floor(Overpower/6)"}
{"n": "No Quarter", "a": "Brute", "s": "Overpower", "g": null, "b": {"Stk": 3, "Pri": 1, "HP": 11}, "c": "Heavy+ melee attack +1 AP; resist Dex (negates)", "r": "", "t": "[ATTACK+1]"}
{"n": "One-Handing It", "a": "Brute", "s": "Overpower", "g": null, "b": {"Acc": 1, "Stk": 2, "HP": 10}, "c": "Passive", "r": "", "t": "[PASSIVE] [GEAR]"}
{"n": "Robust Toss", "a": "Brute", "s": "Overpower", "g": null, "b": {"Acc": 1, "Stk": 2, "HP": 11}, "c": "Medium+ thrown attack", "r": "", "t": "[ATTACK+0]"}
{"n": "Shield Whack", "a": "Brute", "s": "Overpower", "g": null, "b": {"Acc": 1, "Stk": 3, "HP": 7}, "c": "Melee attack conversion", "r": "", "t": "[REFLEX]"}
{"n": "Solid Assault", "a": "Brute", "s": "Overpower", "g": null, "b": {"Stk": 3, "Pri": 1, "HP": 11}, "c": "Melee attack +1 AP", "r": "", "t": "[ATTACK+1]"}
{"n": "Stunning Blow", "a": "Brute", "s": "Overpower", "g": null, "b": {"Acc": 1, "Stk": 2, "HP": 9}, "c": "Melee attack +1 AP; resist Brute (tiers down)", "r": "", "t": "[ATTACK+1]"}
{"n": "Titanic Strength", "a": "Brute", "s": "Overpower", "g": null, "b": {"Acc": 1, "Stk": 3, "HP": 8}, "c": "Passive", "r": "3 Overpower", "t": "[PASSIVE] [GEAR]"}
{"n": "With Gusto", "a": "Brute", "s": "Overpower", "g": null, "b": {"Stk": 3, "Pri": 1, "HP": 10}, "c": "Passive; resist Brute (negates)", "r": "+13 Strike", "t": "[COND] [REQ:Stk≥13]"}
{"n": "Chipping Away", "a": "Brute", "s": "Overpower", "g": "Armor-Breaking", "b": {"Acc": 1, "Stk": 2, "HP": 10}, "c": "Heavy+ melee attack +1 AP; resist Dex (opposed, negates)", "r": "", "t": "[ATTACK+1]"}
{"n": "Armor Sunder", "a": "Brute", "s": "Overpower", "g": "Armor-Breaking", "b": {"Acc": 1, "Stk": 2, "HP": 9}, "c": "Heavy+ melee attack +1 AP; resist Dex (tiers down)", "r": "Chipping Away", "t": "[ATTACK+1] [REQ]"}
{"n": "Earthquaking Strike", "a": "Brute", "s": "Overpower", "g": "Earth-Shattering", "b": {"Acc": 1, "Stk": 2, "HP": 11}, "c": "As heavy+ melee attack; resist Cunning (negates)", "r": "", "t": "[ATTACK+0]"}
{"n": "Rampant Destruction", "a": "Brute", "s": "Overpower", "g": "Earth-Shattering", "b": {"Stk": 3, "Pri": 1, "HP": 11}, "c": "Earthquaking Strike +1 AP", "r": "Earthquaking Strike", "t": "[ATTACK+1] [REQ]"}
{"n": "Staggering Strike", "a": "Brute", "s": "Overpower", "g": "Push Away", "b": {"Acc": 1, "Stk": 2, "HP": 9}, "c": "Melee attack +1 AP; resist Brute (tiers down)", "r": "", "t": "[ATTACK+1]"}
{"n": "Bullrush", "a": "Brute", "s": "Overpower", "g": "Push Away", "b": {"Stk": 2, "Spd": 5, "HP": 11}, "c": "Move + melee attack", "r": "Staggering Strike", "t": "[ACTION] [REQ]"}
{"n": "Blast Proof", "a": "Brute", "s": "Resilience", "g": null, "b": {"Eva": 1, "Def": 2, "HP": 14}, "c": "Shield deflection +1 AP reflexive; resist Cunning (tiers down)", "r": "", "t": "[REFLEX]"}
{"n": "Body of Steel", "a": "Brute", "s": "Resilience", "g": null, "b": {"Def": 3, "Wnd": 1, "HP": 14}, "c": "Passive", "r": "", "t": "[COND] resist += Def"}
{"n": "Brace for Impact", "a": "Brute", "s": "Resilience", "g": null, "b": {"Acc": 1, "Def": 3, "HP": 15}, "c": "As a shield deflection", "r": "", "t": "[REFLEX]"}
{"n": "Bulwark", "a": "Brute", "s": "Resilience", "g": null, "b": {"Eva": 1, "Def": 2, "HP": 13}, "c": "Stance", "r": "", "t": "[STANCE]"}
{"n": "Interposition", "a": "Brute", "s": "Resilience", "g": null, "b": {"Def": 2, "Spd": 5, "HP": 13}, "c": "Move +1 AP reflexive; resist Dex (negates)", "r": "", "t": "[REFLEX]"}
{"n": "Metal Embrace", "a": "Brute", "s": "Resilience", "g": null, "b": {"Eva": 1, "Def": 3, "HP": 15}, "c": "1 AP reflexive", "r": "", "t": "[REFLEX]"}
{"n": "Never Off-Guard", "a": "Brute", "s": "Resilience", "g": null, "b": {"Eva": 1, "Pri": 3, "HP": 17}, "c": "Passive", "r": "", "t": "[PASSIVE] [SCALE:Resilience]"}
{"n": "Press", "a": "Brute", "s": "Resilience", "g": null, "b": {"Stk": 2, "Def": 2, "HP": 11}, "c": "Stance; resist Dex (negates)", "r": "", "t": "[STANCE]"}
{"n": "Protector", "a": "Brute", "s": "Resilience", "g": null, "b": {"Eva": 1, "Def": 3, "HP": 14}, "c": "As shield deflection", "r": "", "t": "[REFLEX]"}
{"n": "Resolute", "a": "Brute", "s": "Resilience", "g": null, "b": {"Def": 1, "Wnd": 1, "HP": 13}, "c": "Passive", "r": "2+ Resilience stances", "t": "[STANCE] [REQ]"}
{"n": "Second Skin", "a": "Brute", "s": "Resilience", "g": null, "b": {"Eva": 1, "Def": 2, "HP": 14}, "c": "1 AP reflexive", "r": "", "t": "[REFLEX]"}
{"n": "Solid Stances", "a": "Brute", "s": "Resilience", "g": null, "b": {"Eva": 1, "Def": 3, "HP": 13}, "c": "Passive", "r": "", "t": "[PASSIVE]"}
{"n": "Thick Skin", "a": "Brute", "s": "Resilience", "g": null, "b": {"Def": 3, "Wnd": 1, "HP": 11}, "c": "Passive", "r": "", "t": "[PASSIVE] [STAT:Soak += 1 + floor(Resilience/5)]"}
{"n": "Tough Stuff", "a": "Brute", "s": "Resilience", "g": null, "b": {"Def": 2, "Wnd": 1, "HP": 19}, "c": "Passive", "r": "", "t": "[PASSIVE] [STAT:HP += specialties × (1 + floor(Resilience/8))]"}
{"n": "Unassailable Mountain", "a": "Brute", "s": "Resilience", "g": null, "b": {"Acc": 1, "Def": 3, "HP": 12}, "c": "3 AP reflexive", "r": "heavy or heavier armor worn", "t": "[REFLEX] [REQ:armor≥heavy]"}
{"n": "Walking Fortress", "a": "Brute", "s": "Resilience", "g": null, "b": {"Def": 2, "Wnd": 1, "HP": 13}, "c": "Stance", "r": "3 Resilience", "t": "[STANCE] [SCALE:Resilience] Def += floor(Resilience/3)"}
{"n": "Ward", "a": "Brute", "s": "Resilience", "g": null, "b": {"Stk": 2, "Def": 2, "HP": 11}, "c": "Stance; 1 AP reflexive", "r": "", "t": "[STANCE] [REFLEX]"}
{"n": "Armored Ease", "a": "Brute", "s": "Resilience", "g": "Armored Movement", "b": {"Eva": 1, "Def": 3, "HP": 12}, "c": "Passive", "r": "", "t": "[PASSIVE] [GEAR] armor penalty degree −1"}
{"n": "Armored Freedom", "a": "Brute", "s": "Resilience", "g": "Armored Movement", "b": {"Def": 2, "Spd": 5, "HP": 14}, "c": "Passive", "r": "Armored Ease; 7 Resilience", "t": "[PASSIVE] [GEAR] [REQ] armor penalty degree −2 more"}
{"n": "Living Barrier", "a": "Brute", "s": "Resilience", "g": "Barrier", "b": {"Def": 3, "Pri": 1, "HP": 12}, "c": "Stance; resist Dex (negates)", "r": "", "t": "[STANCE]"}
{"n": "Living Wall", "a": "Brute", "s": "Resilience", "g": "Barrier", "b": {"Def": 2, "Wnd": 1, "HP": 14}, "c": "1 AP reflexive; resist Dex (negates)", "r": "Living Barrier", "t": "[REFLEX] [REQ]"}
{"n": "Living Stronghold", "a": "Brute", "s": "Resilience", "g": "Barrier", "b": {"Def": 2, "Wnd": 1, "HP": 15}, "c": "Passive; resist Dex", "r": "Living Barrier, Living Wall", "t": "[COND] [REQ]"}
{"n": "Destabilizing Strike", "a": "Cunning", "s": "Espionage", "g": null, "b": {"Acc": 1, "Stk": 2, "HP": 7}, "c": "Attack +1 AP", "r": "", "t": "[ATTACK+1] [COND]"}
{"n": "Feign Fatal Wounds", "a": "Cunning", "s": "Espionage", "g": null, "b": {"Acc": 1, "Eva": 2, "HP": 7}, "c": "1 AP reflexive; resist Cunning (opposed, negates)", "r": "", "t": "[REFLEX]"}
{"n": "First Strike", "a": "Cunning", "s": "Espionage", "g": null, "b": {"Acc": 1, "Pri": 4, "HP": 5}, "c": "Passive", "r": "", "t": "[COND] [SCALE:Espionage] Acc += Espionage"}
{"n": "Flowing Shadow", "a": "Cunning", "s": "Espionage", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 6}, "c": "Passive", "r": "4 Espionage", "t": "[COND] [SCALE:Espionage] Eva += floor(Esp/4)"}
{"n": "Heartseeker", "a": "Cunning", "s": "Espionage", "g": null, "b": {"Acc": 1, "Stk": 2, "HP": 6}, "c": "Light-weapon melee attack +1 AP", "r": "", "t": "[ATTACK+1] [REQ:light weapon]"}
{"n": "Invisible Blade", "a": "Cunning", "s": "Espionage", "g": null, "b": {"Acc": 1, "Stk": 1, "HP": 7}, "c": "Stance", "r": "", "t": "[STANCE] [GEAR] AP=1"}
{"n": "Master Lockpick", "a": "Cunning", "s": "Espionage", "g": null, "b": {"Eva": 1, "Pri": 3, "HP": 7}, "c": "Passive", "r": "", "t": "[COND]"}
{"n": "Pierce the Darkness", "a": "Cunning", "s": "Espionage", "g": null, "b": {"Acc": 2, "Pri": 1, "HP": 7}, "c": "Passive", "r": "4 Espionage", "t": "[COND] [SCALE:Espionage] Acc += floor(Esp/4)"}
{"n": "Silent Kill", "a": "Cunning", "s": "Espionage", "g": null, "b": {"Acc": 1, "Eva": 2, "HP": 6}, "c": "Melee attack +1 AP; resist Cunning", "r": "", "t": "[ATTACK+1]"}
{"n": "Sinister Strike", "a": "Cunning", "s": "Espionage", "g": null, "b": {"Acc": 1, "Stk": 3, "HP": 7}, "c": "Reflexive melee strike +3 AP", "r": "18 Espionage", "t": "[REFLEX] [REQ]"}
{"n": "Fighting Blind", "a": "Cunning", "s": "Espionage", "g": "Nightwalker", "b": {"Acc": 2, "Stk": 1, "HP": 6}, "c": "Passive", "r": "", "t": "[COND]"}
{"n": "Deep Blind Senses", "a": "Cunning", "s": "Espionage", "g": "Nightwalker", "b": {"Acc": 1, "Eva": 1, "HP": 6}, "c": "Passive", "r": "Fighting Blind; 5 Espionage", "t": "[COND] [REQ] [SCALE:Espionage]"}
{"n": "Cover Expert", "a": "Cunning", "s": "Espionage", "g": "Cover User", "b": {"Eva": 2, "Pri": 1, "HP": 5}, "c": "Stance", "r": "", "t": "[STANCE]"}
{"n": "Contort", "a": "Cunning", "s": "Espionage", "g": "Cover User", "b": {"Acc": 1, "Eva": 2, "HP": 6}, "c": "1 AP", "r": "Cover Expert", "t": "[ACTION] [REQ]"}
{"n": "Critical Hits", "a": "Cunning", "s": "Espionage", "g": "Critical", "b": {"Acc": 2, "Stk": 1, "HP": 5}, "c": "Passive", "r": "", "t": "[COND] [SCALE] DC += min(floor((Acc−Eva)/5), Espionage)"}
{"n": "Hairsplitter", "a": "Cunning", "s": "Espionage", "g": "Critical", "b": {"Acc": 2, "Stk": 1, "HP": 5}, "c": "Passive", "r": "Critical Hits; +6 Accuracy from specialties", "t": "[COND] [REQ:Acc≥6] DC += min(floor((Acc−Eva)/3), Espionage)"}
{"n": "Pinpoint Shot", "a": "Cunning", "s": "Espionage", "g": "Critical", "b": {"Acc": 2, "Pri": 1, "HP": 6}, "c": "Passive", "r": "Critical Hits or Heartseeker", "t": "[PASSIVE] [REQ]"}
{"n": "Dirt in the Eyes", "a": "Cunning", "s": "Espionage", "g": "Dirt In The Eyes", "b": {"Eva": 2, "Pri": 1, "HP": 7}, "c": "2 AP", "r": "", "t": "[ACTION] [SCALE:Espionage]"}
{"n": "Blind & Swing", "a": "Cunning", "s": "Espionage", "g": "Dirt In The Eyes", "b": {"Acc": 1, "Stk": 2, "HP": 6}, "c": "Melee attack +1 AP", "r": "Dirt in the Eyes", "t": "[ATTACK+1] [REQ]"}
{"n": "Distracting Attack", "a": "Cunning", "s": "Espionage", "g": "Disorienting", "b": {"Acc": 2, "Pri": 1, "HP": 7}, "c": "Melee attack +1 AP; resist Cunning (tiers down)", "r": "", "t": "[ATTACK+1]"}
{"n": "Taking Advantage", "a": "Cunning", "s": "Espionage", "g": "Disorienting", "b": {"Acc": 1, "Stk": 2, "HP": 8}, "c": "Passive", "r": "Distracting Attack", "t": "[COND] [REQ]"}
{"n": "Brain-Blowing Attack", "a": "Cunning", "s": "Espionage", "g": "Disorienting", "b": {"Acc": 1, "Stk": 2, "HP": 9}, "c": "Passive", "r": "12 Espionage; Distracting Attack", "t": "[PASSIVE] [REQ]"}
{"n": "Appraisal", "a": "Cunning", "s": "Expertise", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 9}, "c": "Once per downtime", "r": "", "t": "[NARR]"}
{"n": "Concentrated Focus", "a": "Cunning", "s": "Expertise", "g": null, "b": {"Eva": 1, "Def": 3, "HP": 10}, "c": "Passive", "r": "3 Expertise", "t": "[COND] [SCALE:Expertise]"}
{"n": "Deep Breath", "a": "Cunning", "s": "Expertise", "g": null, "b": {"Eva": 1, "Pri": 3, "HP": 8}, "c": "1 AP (once per turn)", "r": "5 Expertise", "t": "[ACTION] [REQ]"}
{"n": "Demoman", "a": "Cunning", "s": "Expertise", "g": null, "b": {"Acc": 1, "Stk": 3, "HP": 8}, "c": "Passive", "r": "3 Expertise", "t": "[COND] [SCALE:Expertise] DC += floor(Exp/3)"}
{"n": "Efficiency Expert", "a": "Cunning", "s": "Expertise", "g": null, "b": {"Pri": 3, "DIY": 3, "HP": 8}, "c": "Passive", "r": "3 Expertise", "t": "[COND] [DIY]"}
{"n": "Fire Fighter", "a": "Cunning", "s": "Expertise", "g": null, "b": {"Def": 2, "Pri": 2, "HP": 12}, "c": "Passive", "r": "", "t": "[COND]"}
{"n": "Hurl", "a": "Cunning", "s": "Expertise", "g": null, "b": {"Acc": 1, "Stk": 3, "HP": 9}, "c": "Passive", "r": "", "t": "[PASSIVE] [GEAR]"}
{"n": "Improv Fighter", "a": "Cunning", "s": "Expertise", "g": null, "b": {"Acc": 1, "Stk": 2, "HP": 10}, "c": "Passive", "r": "3 Expertise", "t": "[COND] [SCALE:Expertise] Acc += floor(Exp/3)"}
{"n": "Mechanic", "a": "Cunning", "s": "Expertise", "g": null, "b": {"Eva": 1, "Def": 2, "HP": 8}, "c": "3 AP", "r": "", "t": "[ACTION]"}
{"n": "Patch the Bleeding", "a": "Cunning", "s": "Expertise", "g": null, "b": {"Def": 2, "Pri": 2, "HP": 11}, "c": "1 AP", "r": "", "t": "[ACTION]"}
{"n": "Observance", "a": "Cunning", "s": "Expertise", "g": null, "b": {"Eva": 1, "Def": 2, "HP": 10}, "c": "2 AP; resist Cunning (negates)", "r": "", "t": "[ACTION]"}
{"n": "Weak Point", "a": "Cunning", "s": "Expertise", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 8}, "c": "2 AP", "r": "", "t": "[ACTION]"}
{"n": "Trick Counter", "a": "Cunning", "s": "Expertise", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 9}, "c": "1+ AP reflexive (= upgrade cost); resist Cunning (negates)", "r": "", "t": "[REFLEX]"}
{"n": "Poison Finder", "a": "Cunning", "s": "Expertise", "g": "Anti-Poison", "b": {"Acc": 1, "Eva": 1, "HP": 11}, "c": "Passive", "r": "", "t": "[COND] [SCALE:Expertise]"}
{"n": "Remove Poison", "a": "Cunning", "s": "Expertise", "g": "Anti-Poison", "b": {"Def": 3, "Pri": 2, "HP": 10}, "c": "2 AP", "r": "", "t": "[ACTION]"}
{"n": "Combat Insight", "a": "Cunning", "s": "Expertise", "g": "Combat Insights", "b": {"Eva": 1, "Pri": 2, "HP": 11}, "c": "Passive", "r": "", "t": "[PASSIVE]"}
{"n": "Combat Analytics", "a": "Cunning", "s": "Expertise", "g": "Combat Insights", "b": {"Acc": 1, "Eva": 1, "HP": 10}, "c": "1 AP reflexive", "r": "11 Expertise; Combat Insight", "t": "[REFLEX] [REQ]"}
{"n": "Weapon Appropriations", "a": "Cunning", "s": "Expertise", "g": "Item Appropriation", "b": {"Acc": 1, "Eva": 1, "HP": 9}, "c": "Passive (downtime in trade location)", "r": "", "t": "[GEAR] [AUG] [SCALE:Expertise]"}
{"n": "Quality Weapon", "a": "Cunning", "s": "Expertise", "g": "Item Appropriation", "b": {"Acc": 1, "Stk": 3, "HP": 7}, "c": "Passive", "r": "Weapon Appropriations", "t": "[GEAR] [REQ]"}
{"n": "Field Surgeon", "a": "Cunning", "s": "Expertise", "g": "Surgery", "b": {"Pri": 2, "Def": 2, "HP": 10}, "c": "3 AP (patient spends 3 AP reflexively)", "r": "4 Expertise", "t": "[ACTION] [REQ]"}
{"n": "First Aid", "a": "Cunning", "s": "Expertise", "g": "Surgery", "b": {"Def": 2, "Spd": 5, "HP": 9}, "c": "Move + Field Surgeon reflexive", "r": "Field Surgeon", "t": "[REFLEX] [REQ]"}
{"n": "Self-Surgery", "a": "Cunning", "s": "Expertise", "g": "Surgery", "b": {"Pri": 3, "Wnd": 1, "HP": 9}, "c": "Passive", "r": "Field Surgeon", "t": "[PASSIVE] [REQ]"}
{"n": "Blindside", "a": "Cunning", "s": "Showmanship", "g": null, "b": {"Eva": 1, "Pri": 3, "HP": 8}, "c": "2 AP to begin, 1 AP/turn to continue", "r": "", "t": "[ACTION]"}
{"n": "Captive Audience", "a": "Cunning", "s": "Showmanship", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 9}, "c": "Stance; resist Cunning (negates)", "r": "", "t": "[STANCE]"}
{"n": "Catchphrase", "a": "Cunning", "s": "Showmanship", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 8}, "c": "1 AP", "r": "", "t": "[ACTION] [SCALE:Showmanship]"}
{"n": "Chime In", "a": "Cunning", "s": "Showmanship", "g": null, "b": {"Eva": 1, "Pri": 3, "HP": 8}, "c": "Passive", "r": "2 Showmanship", "t": "[COND] [SCALE:Showmanship] floor(Show/2)"}
{"n": "Conveyor", "a": "Cunning", "s": "Showmanship", "g": null, "b": {"Eva": 1, "Pri": 2, "HP": 9}, "c": "1 AP reflexive", "r": "", "t": "[REFLEX]"}
{"n": "Deafening Roar", "a": "Cunning", "s": "Showmanship", "g": null, "b": {"Stk": 2, "Def": 2, "HP": 10}, "c": "1 AP; resist Brute (tiers down)", "r": "", "t": "[ACTION]"}
{"n": "Distract", "a": "Cunning", "s": "Showmanship", "g": null, "b": {"Eva": 1, "Pri": 3, "HP": 7}, "c": "2 AP reflexive; resist Cunning (negates)", "r": "", "t": "[REFLEX]"}
{"n": "Jester", "a": "Cunning", "s": "Showmanship", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 7}, "c": "2 AP; resist Cunning (tiers down)", "r": "", "t": "[ACTION]"}
{"n": "Marionette Strings", "a": "Cunning", "s": "Showmanship", "g": null, "b": {"Acc": 2, "Pri": 2, "HP": 6}, "c": "1 AP reflexive", "r": "", "t": "[REFLEX]"}
{"n": "Praise", "a": "Cunning", "s": "Showmanship", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 7}, "c": "1 AP reflexive", "r": "", "t": "[REFLEX]"}
{"n": "Sleight of Hand", "a": "Cunning", "s": "Showmanship", "g": null, "b": {"Eva": 2, "Pri": 2, "HP": 6}, "c": "Passive", "r": "", "t": "[PASSIVE]"}
{"n": "Smoke & Mirrors", "a": "Cunning", "s": "Showmanship", "g": null, "b": {"Eva": 1, "Pri": 3, "HP": 7}, "c": "3 AP reflexive; resist Dex (negates)", "r": "3 Showmanship", "t": "[REFLEX] [REQ]"}
{"n": "Throw Off Balance", "a": "Cunning", "s": "Showmanship", "g": null, "b": {"Eva": 1, "Pri": 2, "HP": 8}, "c": "1 AP reflexive; resist Cunning (tiers down)", "r": "", "t": "[REFLEX]"}
{"n": "Unmarred Perfection", "a": "Cunning", "s": "Showmanship", "g": null, "b": {"Eva": 1, "Pri": 2, "HP": 8}, "c": "Stance; resist Cunning or Spirit (negates)", "r": "", "t": "[STANCE] [SCALE:Showmanship]"}
{"n": "Epic Dance", "a": "Cunning", "s": "Showmanship", "g": "Choreographed", "b": {"Eva": 2, "Pri": 1, "HP": 6}, "c": "2 AP to begin, 1 AP/turn to continue", "r": "", "t": "[STANCE-like] [STAT:Eva += 3 + floor(Show/5)]"}
{"n": "Never Stop the Dance", "a": "Cunning", "s": "Showmanship", "g": "Choreographed", "b": {"Eva": 1, "Def": 2, "HP": 9}, "c": "Passive", "r": "Epic Dance", "t": "[COND] [REQ] [STAT:Def += 3 + floor(Show/5)]"}
{"n": "Battle Theme", "a": "Cunning", "s": "Showmanship", "g": "Epic Music", "b": {"Acc": 1, "Eva": 1, "HP": 7}, "c": "2 AP to begin, 1 AP/turn to continue", "r": "", "t": "[STANCE-like] [STAT:Acc += 3 + floor(Show/5)]"}
{"n": "Heavenly Serenade", "a": "Cunning", "s": "Showmanship", "g": "Epic Music", "b": {"Eva": 1, "Pri": 2, "HP": 8}, "c": "2 AP reflexive; resist Spirit (negates)", "r": "Battle Theme", "t": "[REFLEX] [REQ]"}
{"n": "Spotlight", "a": "Cunning", "s": "Showmanship", "g": "Epic Music", "b": {"Acc": 1, "Eva": 1, "HP": 9}, "c": "1 AP reflexive", "r": "Battle Theme", "t": "[REFLEX] [REQ]"}
{"n": "Unified Chorus", "a": "Cunning", "s": "Showmanship", "g": "Epic Music", "b": {"Acc": 1, "Stk": 3, "HP": 10}, "c": "Passive", "r": "Battle Theme; 16 Showmanship", "t": "[COND] [REQ]"}
{"n": "Victory Theme", "a": "Cunning", "s": "Showmanship", "g": "Epic Music", "b": {"Acc": 1, "Stk": 2, "HP": 9}, "c": "Passive", "r": "Battle Theme", "t": "[COND] [REQ] [STAT:Stk += BattleTheme]"}
{"n": "Smokescreen", "a": "Cunning", "s": "Showmanship", "g": "Smokescreen", "b": {"Eva": 1, "Pri": 3, "HP": 8}, "c": "1 AP", "r": "", "t": "[ACTION]"}
{"n": "Walking Darkness", "a": "Cunning", "s": "Showmanship", "g": "Smokescreen", "b": {"Eva": 1, "Spd": 5, "HP": 7}, "c": "Stance", "r": "Smokescreen", "t": "[STANCE] [REQ] [STAT:Eva +4]"}
{"n": "Ally of the Machine", "a": "Cunning", "s": "Tactical", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 9}, "c": "Passive", "r": "6 Automata", "t": "[PASSIVE] [REQ]"}
{"n": "Armistice", "a": "Cunning", "s": "Tactical", "g": null, "b": {"Eva": 2, "Pri": 1, "HP": 6}, "c": "Stance; resist Cunning (negates)", "r": "", "t": "[STANCE]"}
{"n": "Blitzkreig", "a": "Cunning", "s": "Tactical", "g": null, "b": {"Acc": 1, "Spd": 5, "HP": 8}, "c": "Stance", "r": "", "t": "[STANCE] [SCALE:Tactical] 10 + 5×floor(Tac/5)"}
{"n": "Call in a Favor", "a": "Cunning", "s": "Tactical", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 7}, "c": "Give 3 AP", "r": "4 Tactical", "t": "[ACTION] [REQ]"}
{"n": "Change Formation", "a": "Cunning", "s": "Tactical", "g": null, "b": {"Eva": 1, "Pri": 2, "HP": 7}, "c": "2 AP", "r": "", "t": "[ACTION]"}
{"n": "Change Places", "a": "Cunning", "s": "Tactical", "g": null, "b": {"Eva": 1, "Spd": 5, "HP": 6}, "c": "1 AP", "r": "", "t": "[ACTION]"}
{"n": "Crippling Formation", "a": "Cunning", "s": "Tactical", "g": null, "b": {"Acc": 1, "Stk": 2, "HP": 7}, "c": "Passive", "r": "3 Tactical", "t": "[COND] [SCALE:Tactical]"}
{"n": "Crossfire", "a": "Cunning", "s": "Tactical", "g": null, "b": {"Acc": 1, "Stk": 2, "HP": 8}, "c": "Stance", "r": "", "t": "[STANCE]"}
{"n": "Forewarned", "a": "Cunning", "s": "Tactical", "g": null, "b": {"Acc": 1, "Pri": 4, "HP": 6}, "c": "1 AP reflexive (from first turn)", "r": "", "t": "[REFLEX] [SCALE:Tactical]"}
{"n": "Focused Support", "a": "Cunning", "s": "Tactical", "g": null, "b": {"Acc": 1, "Stk": 2, "HP": 6}, "c": "2 AP to begin, 1 AP/turn", "r": "7 Tactical", "t": "[ACTION] [REQ]"}
{"n": "Lead the March", "a": "Cunning", "s": "Tactical", "g": null, "b": {"Spd": 5, "Pri": 2, "HP": 6}, "c": "1 AP", "r": "", "t": "[ACTION]"}
{"n": "Malleable Formation", "a": "Cunning", "s": "Tactical", "g": null, "b": {"Acc": 1, "Spd": 5, "HP": 7}, "c": "Passive", "r": "", "t": "[COND] aura"}
{"n": "Master Tactician", "a": "Cunning", "s": "Tactical", "g": null, "b": {"Acc": 1, "Pri": 3, "HP": 8}, "c": "Passive", "r": "15 Tactical", "t": "[PASSIVE] [REQ] AP +1 (reflex only)"}
{"n": "Stand-Off", "a": "Cunning", "s": "Tactical", "g": null, "b": {"Eva": 1, "Pri": 2, "HP": 6}, "c": "1 AP reflexive", "r": "", "t": "[REFLEX] [SCALE:Tactical]"}
{"n": "Encouragement", "a": "Cunning", "s": "Tactical", "g": "Encouraging", "b": {"Eva": 1, "Spd": 5, "HP": 6}, "c": "1 AP reflexive", "r": "", "t": "[REFLEX]"}
{"n": "Inspiring Words", "a": "Cunning", "s": "Tactical", "g": "Encouraging", "b": {"Eva": 1, "Pri": 2, "HP": 8}, "c": "Passive", "r": "5 Tactical; Encouragement", "t": "[COND] [REQ]"}
{"n": "Direct the Battle", "a": "Cunning", "s": "Tactical", "g": "Flow Of Battle", "b": {"Acc": 1, "Eva": 1, "HP": 8}, "c": "Stance", "r": "", "t": "[STANCE]"}
{"n": "Concentrated Barrage", "a": "Cunning", "s": "Tactical", "g": "Flow Of Battle", "b": {"Acc": 1, "Stk": 2, "HP": 7}, "c": "Passive", "r": "Direct the Battle", "t": "[COND] [REQ]"}
{"n": "Overwhelm", "a": "Cunning", "s": "Tactical", "g": "Flow Of Battle", "b": {"Acc": 1, "Eva": 1, "HP": 9}, "c": "1 AP reflexive", "r": "Direct the Battle", "t": "[REFLEX] [REQ]"}
{"n": "Issue Orders", "a": "Cunning", "s": "Tactical", "g": "Order", "b": {"Acc": 1, "Eva": 1, "HP": 7}, "c": "3 AP", "r": "", "t": "[ACTION]"}
{"n": "Complex Orders", "a": "Cunning", "s": "Tactical", "g": "Order", "b": {"Acc": 1, "Pri": 3, "HP": 8}, "c": "Extra AP = modifier cost", "r": "Issue Orders; 5 Tactical", "t": "[ACTION] [REQ]"}
{"n": "Improved Orders", "a": "Cunning", "s": "Tactical", "g": "Order", "b": {"Acc": 1, "Eva": 1, "HP": 8}, "c": "Passive", "r": "Issue Orders; Complex Orders; 8 Tactical", "t": "[PASSIVE] [REQ]"}
{"n": "Backseat Driver", "a": "Dexterity", "s": "Ace", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 9}, "c": "Stance", "r": "", "t": "[STANCE]"}
{"n": "Co-Pilot", "a": "Dexterity", "s": "Ace", "g": null, "b": {"Acc": 1, "Eva": 3, "HP": 8}, "c": "Reflexive", "r": "", "t": "[REFLEX]"}
{"n": "Crash Maneuver", "a": "Dexterity", "s": "Ace", "g": null, "b": {"Acc": 1, "Def": 3, "HP": 9}, "c": "3 AP reflexive", "r": "", "t": "[REFLEX]"}
{"n": "Denial Maneuver", "a": "Dexterity", "s": "Ace", "g": null, "b": {"Eva": 2, "Pri": 1, "HP": 7}, "c": "2 AP reflexive", "r": "", "t": "[REFLEX] [SCALE:Ace]"}
{"n": "Driving with Knees", "a": "Dexterity", "s": "Ace", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 8}, "c": "Stance", "r": "", "t": "[STANCE]"}
{"n": "Flying Fortress", "a": "Dexterity", "s": "Ace", "g": null, "b": {"Acc": 1, "Def": 3, "HP": 7}, "c": "2 AP to begin, 1 AP/turn", "r": "2 Ace", "t": "[ACTION] [REQ] [SCALE:Ace] vehicle Def += floor(Ace/2)"}
{"n": "Hold Together", "a": "Dexterity", "s": "Ace", "g": null, "b": {"Eva": 1, "Def": 3, "HP": 8}, "c": "Passive", "r": "7 Ace", "t": "[COND] [REQ]"}
{"n": "Horseman's Cut", "a": "Dexterity", "s": "Ace", "g": null, "b": {"Acc": 1, "Stk": 3, "HP": 7}, "c": "Mounted melee attack +1 AP", "r": "", "t": "[ATTACK+1]"}
{"n": "Hostile Maneuvers", "a": "Dexterity", "s": "Ace", "g": null, "b": {"Acc": 1, "Stk": 2, "HP": 9}, "c": "2 AP to begin, 1 AP/turn", "r": "5 Ace", "t": "[ACTION] [REQ] [SCALE:Ace]"}
{"n": "Level Flying", "a": "Dexterity", "s": "Ace", "g": null, "b": {"Acc": 1, "Pri": 3, "HP": 8}, "c": "Passive", "r": "", "t": "[COND]"}
{"n": "Quick-Mount", "a": "Dexterity", "s": "Ace", "g": null, "b": {"Acc": 2, "Pri": 1, "HP": 6}, "c": "Passive (once per turn)", "r": "", "t": "[PASSIVE]"}
{"n": "Vehicular Teamwork", "a": "Dexterity", "s": "Ace", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 10}, "c": "2 AP reflexive", "r": "", "t": "[REFLEX]"}
{"n": "Strafe", "a": "Dexterity", "s": "Ace", "g": "Auto Piloting", "b": {"Acc": 1, "Eva": 1, "HP": 9}, "c": "Free, once per turn", "r": "", "t": "[ACTION]"}
{"n": "Evasive Strafe", "a": "Dexterity", "s": "Ace", "g": "Auto Piloting", "b": {"Eva": 1, "Def": 2, "HP": 7}, "c": "Passive", "r": "Strafe", "t": "[COND] [REQ]"}
{"n": "Extension of Self", "a": "Dexterity", "s": "Ace", "g": "Clanker Piloting", "b": {"Acc": 1, "Eva": 1, "HP": 9}, "c": "Passive", "r": "", "t": "[PASSIVE]"}
{"n": "Piston-Spring", "a": "Dexterity", "s": "Ace", "g": "Clanker Piloting", "b": {"Eva": 1, "Def": 2, "HP": 10}, "c": "Jump", "r": "", "t": "[ACTION]"}
{"n": "Focused Flying", "a": "Dexterity", "s": "Ace", "g": "Focusing Flying", "b": {"Acc": 1, "Def": 3, "HP": 8}, "c": "Stance (both hands on controls, no other actions)", "r": "", "t": "[STANCE] [SCALE:Ace]"}
{"n": "Fine-Tuned Flying", "a": "Dexterity", "s": "Ace", "g": "Focusing Flying", "b": {"Def": 3, "Pri": 2, "HP": 7}, "c": "Passive", "r": "Focused Flying; 2 Ace", "t": "[COND] [REQ] [SCALE:Ace]"}
{"n": "Fully Focused Flying", "a": "Dexterity", "s": "Ace", "g": "Focusing Flying", "b": {"Acc": 1, "Eva": 1, "HP": 8}, "c": "Passive", "r": "Focused Flying; 3 Ace", "t": "[COND] [REQ] [SCALE:Ace]"}
{"n": "Fearless Mount", "a": "Dexterity", "s": "Ace", "g": "Mounted Cavalry", "b": {"Acc": 1, "Pri": 3, "HP": 8}, "c": "Passive", "r": "3 Ace", "t": "[PASSIVE] [REQ]"}
{"n": "One with the Beast", "a": "Dexterity", "s": "Ace", "g": "Mounted Cavalry", "b": {"Stk": 2, "Def": 2, "HP": 10}, "c": "Stance (mounted)", "r": "", "t": "[STANCE] [STAT:Stk,Def += mount's]"}
{"n": "Ram", "a": "Dexterity", "s": "Ace", "g": "Ramming", "b": {"Acc": 1, "Stk": 3, "HP": 7}, "c": "Move + 1 AP", "r": "", "t": "[ACTION]"}
{"n": "Puncture", "a": "Dexterity", "s": "Ace", "g": "Ramming", "b": {"Acc": 1, "Def": 3, "HP": 9}, "c": "Ram +1 AP", "r": "", "t": "[ATTACK+1] [REQ:Ram (book omits explicit req)]"}
{"n": "Battlefield Flow", "a": "Dexterity", "s": "Agility", "g": null, "b": {"Eva": 1, "Pri": 2, "HP": 7}, "c": "0 AP (once between your refreshes)", "r": "", "t": "[ACTION]"}
{"n": "Bounding Lunge", "a": "Dexterity", "s": "Agility", "g": null, "b": {"Acc": 1, "Spd": 5, "HP": 7}, "c": "Move + attack", "r": "", "t": "[ACTION]"}
{"n": "Charging Ram", "a": "Dexterity", "s": "Agility", "g": null, "b": {"Stk": 2, "Spd": 5, "HP": 6}, "c": "Move + melee attack", "r": "", "t": "[COND] [SCALE:distance]"}
{"n": "Free Movement", "a": "Dexterity", "s": "Agility", "g": null, "b": {"Pri": 2, "Spd": 5, "HP": 6}, "c": "Free, once per turn", "r": "medium or lighter armor", "t": "[ACTION] [REQ:armor≤medium]"}
{"n": "Groundfighting", "a": "Dexterity", "s": "Agility", "g": null, "b": {"Eva": 2, "Pri": 2, "HP": 7}, "c": "Passive", "r": "", "t": "[PASSIVE]"}
{"n": "Instant Draw", "a": "Dexterity", "s": "Agility", "g": null, "b": {"Acc": 1, "Pri": 3, "HP": 7}, "c": "Passive", "r": "", "t": "[PASSIVE]"}
{"n": "Slow Falling", "a": "Dexterity", "s": "Agility", "g": null, "b": {"Acc": 1, "Eva": 2, "HP": 6}, "c": "2 AP reflexive (must be next to a surface)", "r": "", "t": "[REFLEX]"}
{"n": "Side-Swipe", "a": "Dexterity", "s": "Agility", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 9}, "c": "As melee attack, reflexive", "r": "", "t": "[REFLEX] [SCALE:miss margin]"}
{"n": "Slipstreaming", "a": "Dexterity", "s": "Agility", "g": null, "b": {"Acc": 1, "Spd": 5, "HP": 8}, "c": "Move + 1 AP", "r": "4 Agility", "t": "[ACTION] [REQ]"}
{"n": "Snake Bite", "a": "Dexterity", "s": "Agility", "g": null, "b": {"Acc": 1, "Pri": 3, "HP": 7}, "c": "1 AP (first AP of your turn)", "r": "", "t": "[ACTION] [GEAR] AP=1"}
{"n": "Step Back", "a": "Dexterity", "s": "Agility", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 7}, "c": "1 AP reflexive", "r": "", "t": "[REFLEX]"}
{"n": "Terrain Mastery", "a": "Dexterity", "s": "Agility", "g": null, "b": {"Pri": 4, "Spd": 5, "HP": 9}, "c": "Passive", "r": "", "t": "[PASSIVE]"}
{"n": "Wall Runner", "a": "Dexterity", "s": "Agility", "g": null, "b": {"Acc": 1, "Spd": 5, "HP": 8}, "c": "Move +1 AP (1 AP with Free Movement)", "r": "6 Agility", "t": "[ACTION] [REQ]"}
{"n": "Walk Over", "a": "Dexterity", "s": "Agility", "g": null, "b": {"Eva": 1, "Spd": 5, "HP": 7}, "c": "Passive", "r": "", "t": "[PASSIVE]"}
{"n": "Blast Dodger", "a": "Dexterity", "s": "Agility", "g": "Explosion Dodging", "b": {"Eva": 1, "Spd": 5, "HP": 8}, "c": "0 AP, once per turn", "r": "", "t": "[REFLEX]"}
{"n": "Soaring Dodge", "a": "Dexterity", "s": "Agility", "g": "Explosion Dodging", "b": {"Eva": 1, "Pri": 3, "HP": 9}, "c": "1 AP reflexive per 5 Agility", "r": "5 Agility", "t": "[REFLEX] [REQ] [SCALE:Agility]"}
{"n": "Phase Step", "a": "Dexterity", "s": "Agility", "g": "Phasing", "b": {"Eva": 1, "Spd": 5, "HP": 7}, "c": "Move; resist Cunning (negates)", "r": "", "t": "[ACTION]"}
{"n": "Fleeting Shade", "a": "Dexterity", "s": "Agility", "g": "Phasing", "b": {"Eva": 1, "Spd": 5, "HP": 6}, "c": "Move", "r": "Phase Step", "t": "[ACTION] [REQ]"}
{"n": "Leave No Trace", "a": "Dexterity", "s": "Agility", "g": "Phasing", "b": {"Eva": 1, "Spd": 5, "HP": 6}, "c": "Move reflexive", "r": "Phase Step", "t": "[REFLEX] [REQ]"}
{"n": "Shifting", "a": "Dexterity", "s": "Agility", "g": "Stance-Shifting", "b": {"Acc": 1, "Eva": 1, "HP": 7}, "c": "1 AP reflexive", "r": "2 stances known", "t": "[REFLEX] [REQ]"}
{"n": "Freeform Shifting", "a": "Dexterity", "s": "Agility", "g": "Stance-Shifting", "b": {"Acc": 1, "Eva": 1, "HP": 8}, "c": "0 AP once per turn", "r": "12 Agility; Shifting; 3 stances known", "t": "[REFLEX] [REQ]"}
{"n": "Aim", "a": "Dexterity", "s": "Marksmanship", "g": null, "b": {"Acc": 2, "Eva": 1, "HP": 5}, "c": "1 AP per aim roll", "r": "4 Marksmanship", "t": "[ACTION] [REQ] [SCALE:Marksmanship cap]"}
{"n": "Cover Fire", "a": "Dexterity", "s": "Marksmanship", "g": null, "b": {"Acc": 1, "Eva": 2, "HP": 6}, "c": "As ranged attack", "r": "", "t": "[ATTACK+0] [SCALE:Marksmanship]"}
{"n": "Follow Up", "a": "Dexterity", "s": "Marksmanship", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 7}, "c": "Passive", "r": "", "t": "[COND]"}
{"n": "Head Popper", "a": "Dexterity", "s": "Marksmanship", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 7}, "c": "1 AP reflexive", "r": "", "t": "[REFLEX]"}
{"n": "Itchy Trigger Finger", "a": "Dexterity", "s": "Marksmanship", "g": null, "b": {"Eva": 2, "Pri": 3, "HP": 8}, "c": "Passive", "r": "", "t": "[COND]"}
{"n": "Knock-Off", "a": "Dexterity", "s": "Marksmanship", "g": null, "b": {"Acc": 2, "Pri": 2, "HP": 6}, "c": "Ranged attack +1 AP; resist Dex (negates)", "r": "", "t": "[ATTACK+1]"}
{"n": "Lockdown Gunner", "a": "Dexterity", "s": "Marksmanship", "g": null, "b": {"Acc": 1, "Pri": 3, "HP": 8}, "c": "Passive (reflexive)", "r": "", "t": "[REFLEX]"}
{"n": "Long Shot", "a": "Dexterity", "s": "Marksmanship", "g": null, "b": {"Acc": 2, "Pri": 1, "HP": 7}, "c": "Ranged attack +1 AP", "r": "", "t": "[ATTACK+1] [GEAR] range ×2"}
{"n": "Penetrating Shot", "a": "Dexterity", "s": "Marksmanship", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 8}, "c": "Ranged attack +1 AP", "r": "", "t": "[ATTACK+1]"}
{"n": "Point Blank", "a": "Dexterity", "s": "Marksmanship", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 7}, "c": "Ranged attack +1 AP", "r": "", "t": "[ATTACK+1]"}
{"n": "Seeker", "a": "Dexterity", "s": "Marksmanship", "g": null, "b": {"Acc": 2, "Pri": 1, "HP": 7}, "c": "Passive", "r": "", "t": "[COND] [SCALE:Marksmanship]"}
{"n": "Snap Reload", "a": "Dexterity", "s": "Marksmanship", "g": null, "b": {"Acc": 1, "Pri": 4, "HP": 6}, "c": "Passive", "r": "", "t": "[PASSIVE] [GEAR] AP to Ready −1"}
{"n": "Sneaky Seconds", "a": "Dexterity", "s": "Marksmanship", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 7}, "c": "Passive", "r": "4 AP per turn", "t": "[COND] [REQ:AP≥4] [SCALE:Marksmanship]"}
{"n": "Stable Shot", "a": "Dexterity", "s": "Marksmanship", "g": null, "b": {"Acc": 1, "Def": 2, "HP": 8}, "c": "Passive", "r": "3 Brute (book says \"3 points in Brute\")", "t": "[PASSIVE] [GEAR] [REQ]"}
{"n": "Turret", "a": "Dexterity", "s": "Marksmanship", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 5}, "c": "Stance (stationary, standing, not mounted)", "r": "", "t": "[STANCE]"}
{"n": "Warning Shot", "a": "Dexterity", "s": "Marksmanship", "g": null, "b": {"Acc": 2, "Pri": 1, "HP": 7}, "c": "As ranged attack", "r": "", "t": "[ACTION] [SCALE:Marksmanship]"}
{"n": "Wing Clipping", "a": "Dexterity", "s": "Marksmanship", "g": null, "b": {"Acc": 2, "Eva": 1, "HP": 6}, "c": "Ranged attack +1 AP; resist Brute (physical flight) or Sciences (mechanical)", "r": "", "t": "[ATTACK+1]"}
{"n": "Arching Shot", "a": "Dexterity", "s": "Marksmanship", "g": "Archery", "b": {"Acc": 1, "Stk": 3, "HP": 7}, "c": "Bow attack +1 AP", "r": "", "t": "[ATTACK+1] [GEAR] [SCALE:Marksmanship]"}
{"n": "Efficient Ranger", "a": "Dexterity", "s": "Marksmanship", "g": "Archery", "b": {"Acc": 1, "Stk": 2, "HP": 7}, "c": "Passive", "r": "3 Marksmanship", "t": "[PASSIVE] [GEAR] [REQ] bow AP=2"}
{"n": "Flight of Arrows", "a": "Dexterity", "s": "Marksmanship", "g": "Archery", "b": {"Acc": 1, "Stk": 3, "HP": 8}, "c": "Bow attack +1 AP", "r": "", "t": "[ATTACK+1]"}
{"n": "Flesh Biter", "a": "Dexterity", "s": "Marksmanship", "g": "Bleeding Arrow", "b": {"Acc": 1, "Stk": 2, "HP": 7}, "c": "Bow attack +1 AP", "r": "", "t": "[ATTACK+1]"}
{"n": "Flesh Piercing", "a": "Dexterity", "s": "Marksmanship", "g": "Bleeding Arrow", "b": {"Acc": 1, "Stk": 3, "HP": 6}, "c": "Passive", "r": "Flesh Biter", "t": "[PASSIVE] [REQ]"}
{"n": "Adaptable", "a": "Dexterity", "s": "Swashbuckling", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 7}, "c": "Passive", "r": "2 stances known", "t": "[STANCE] [REQ]"}
{"n": "Circle Attack", "a": "Dexterity", "s": "Swashbuckling", "g": null, "b": {"Acc": 1, "Stk": 2, "HP": 8}, "c": "1 AP reflexive per deflection", "r": "", "t": "[REFLEX]"}
{"n": "Counter-Stance", "a": "Dexterity", "s": "Swashbuckling", "g": null, "b": {"Acc": 2, "Stk": 1, "HP": 6}, "c": "Stance; 1 AP reflexive", "r": "", "t": "[STANCE] [REFLEX]"}
{"n": "Efficient Strike", "a": "Dexterity", "s": "Swashbuckling", "g": null, "b": {"Acc": 1, "Pri": 3, "HP": 8}, "c": "Melee attack +1 AP", "r": "", "t": "[ATTACK+1] [SCALE:margin]"}
{"n": "Fight Anywhere", "a": "Dexterity", "s": "Swashbuckling", "g": null, "b": {"Eva": 2, "Spd": 5, "HP": 6}, "c": "Passive", "r": "", "t": "[PASSIVE]"}
{"n": "Hilt Bash", "a": "Dexterity", "s": "Swashbuckling", "g": null, "b": {"Acc": 1, "Stk": 2, "HP": 8}, "c": "0 AP reflexive", "r": "", "t": "[REFLEX]"}
{"n": "Opening", "a": "Dexterity", "s": "Swashbuckling", "g": null, "b": {"Acc": 1, "Pri": 2, "HP": 6}, "c": "1 AP reflexive", "r": "", "t": "[REFLEX]"}
{"n": "Precise Attack", "a": "Dexterity", "s": "Swashbuckling", "g": null, "b": {"Acc": 1, "Stk": 2, "HP": 8}, "c": "Melee attack +1 AP", "r": "", "t": "[ATTACK+1]"}
{"n": "Saluted Opponent", "a": "Dexterity", "s": "Swashbuckling", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 6}, "c": "Stance", "r": "", "t": "[STANCE] [SCALE:Swashbuckling]"}
{"n": "Sword and Board", "a": "Dexterity", "s": "Swashbuckling", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 8}, "c": "Stance", "r": "", "t": "[STANCE]"}
{"n": "Wild Slash", "a": "Dexterity", "s": "Swashbuckling", "g": null, "b": {"Stk": 2, "Pri": 3, "HP": 8}, "c": "As melee attack", "r": "", "t": "[ATTACK+0]"}
{"n": "En-Garde", "a": "Dexterity", "s": "Swashbuckling", "g": "En-Garde", "b": {"Acc": 1, "Eva": 1, "HP": 8}, "c": "Stance (one-handed melee weapon, other hand empty)", "r": "", "t": "[STANCE] [COND] reflex Acc +4"}
{"n": "Find the Gap", "a": "Dexterity", "s": "Swashbuckling", "g": "En-Garde", "b": {"Acc": 1, "Stk": 2, "HP": 8}, "c": "Passive", "r": "En-Garde; 8 Swashbuckling", "t": "[COND] [REQ] [SCALE:Swashbuckling]"}
{"n": "Lightning Slash", "a": "Dexterity", "s": "Swashbuckling", "g": "En-Garde", "b": {"Acc": 2, "Pri": 2, "HP": 8}, "c": "1 AP", "r": "En-Garde; 16 Swashbuckling", "t": "[ACTION] [REQ] [SCALE:Swashbuckling]"}
{"n": "Flickering", "a": "Dexterity", "s": "Swashbuckling", "g": "Flickering", "b": {"Acc": 1, "Eva": 1, "HP": 7}, "c": "One-handed melee attack +1 AP", "r": "", "t": "[ATTACK+1]"}
{"n": "Torrent of Steel", "a": "Dexterity", "s": "Swashbuckling", "g": "Flickering", "b": {"Acc": 1, "Pri": 2, "HP": 7}, "c": "Flickering +2 AP", "r": "Flickering; 25 Swashbuckling", "t": "[ATTACK+2] [REQ]"}
{"n": "Footwork Training", "a": "Dexterity", "s": "Swashbuckling", "g": "Footwork", "b": {"Pri": 3, "Spd": 5, "HP": 8}, "c": "Passive", "r": "", "t": "[COND]"}
{"n": "Fancy Footwork", "a": "Dexterity", "s": "Swashbuckling", "g": "Footwork", "b": {"Eva": 1, "Spd": 5, "HP": 9}, "c": "Passive", "r": "Footwork Training", "t": "[COND] [REQ]"}
{"n": "Parry", "a": "Dexterity", "s": "Swashbuckling", "g": "Parry & Riposte", "b": {"Acc": 1, "Stk": 2, "HP": 9}, "c": "1 AP reflexive", "r": "", "t": "[REFLEX] [SCALE:Swashbuckling]"}
{"n": "Beat Parry", "a": "Dexterity", "s": "Swashbuckling", "g": "Parry & Riposte", "b": {"Acc": 1, "Stk": 3, "HP": 9}, "c": "Parry +1 AP; resist Dex (negates)", "r": "Parry", "t": "[REFLEX] [REQ]"}
{"n": "Distance Parry", "a": "Dexterity", "s": "Swashbuckling", "g": "Parry & Riposte", "b": {"Acc": 1, "Spd": 5, "HP": 8}, "c": "1 AP reflexive", "r": "Parry", "t": "[REFLEX] [REQ]"}
{"n": "Experienced Parries", "a": "Dexterity", "s": "Swashbuckling", "g": "Parry & Riposte", "b": {"Acc": 1, "Stk": 3, "HP": 8}, "c": "1 AP per damage tier", "r": "Parry; 9 Swashbuckling", "t": "[REFLEX] [REQ]"}
{"n": "Riposte", "a": "Dexterity", "s": "Swashbuckling", "g": "Parry & Riposte", "b": {"Acc": 1, "Stk": 2, "HP": 8}, "c": "Free after parry", "r": "Parry", "t": "[REFLEX] [REQ]"}
{"n": "Blind Faith", "a": "Spirit", "s": "Faith", "g": null, "b": {"Eva": 1, "Pri": 2, "HP": 8}, "c": "As an attack", "r": "6 Faith", "t": "[ATTACK+0] [REQ] [SCALE:Faith]"}
{"n": "Conviction", "a": "Spirit", "s": "Faith", "g": null, "b": {"Acc": 1, "Stk": 3, "HP": 8}, "c": "Attack +1 AP; resist Spirit (negates)", "r": "", "t": "[ATTACK+1] [COND]"}
{"n": "Divine Guidance", "a": "Spirit", "s": "Faith", "g": null, "b": {"Stk": 2, "Def": 2, "HP": 9}, "c": "2 AP reflexive", "r": "", "t": "[REFLEX]"}
{"n": "Flowing Vigor", "a": "Spirit", "s": "Faith", "g": null, "b": {"Eva": 1, "Def": 2, "HP": 9}, "c": "2 AP to begin, 1 AP to channel", "r": "", "t": "[ACTION]"}
{"n": "Grief & Hope", "a": "Spirit", "s": "Faith", "g": null, "b": {"Eva": 1, "Pri": 2, "HP": 8}, "c": "3 AP (allies may sacrifice 1 AP)", "r": "", "t": "[ACTION]"}
{"n": "Healing Halo", "a": "Spirit", "s": "Faith", "g": null, "b": {"Eva": 1, "Def": 2, "HP": 10}, "c": "Stance", "r": "", "t": "[STANCE] [SCALE:Faith]"}
{"n": "Infallible Faith", "a": "Spirit", "s": "Faith", "g": null, "b": {"Eva": 1, "Def": 2, "HP": 8}, "c": "1 AP reflexive (allies may sacrifice 1 AP)", "r": "", "t": "[REFLEX]"}
{"n": "Moral Support", "a": "Spirit", "s": "Faith", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 7}, "c": "2 AP reflexive", "r": "Spirit attribute 8", "t": "[REFLEX] [REQ:Spirit≥8]"}
{"n": "Prayer", "a": "Spirit", "s": "Faith", "g": null, "b": {"Acc": 1, "Def": 2, "HP": 9}, "c": "1 AP (allies may sacrifice 1 AP)", "r": "", "t": "[ACTION]"}
{"n": "Purify", "a": "Spirit", "s": "Faith", "g": null, "b": {"Eva": 1, "Pri": 2, "HP": 8}, "c": "2 AP", "r": "", "t": "[ACTION] [SCALE:Faith]"}
{"n": "Shock of Life", "a": "Spirit", "s": "Faith", "g": null, "b": {"Eva": 1, "Def": 3, "HP": 11}, "c": "2 AP", "r": "10 Faith", "t": "[ACTION] [REQ] [SCALE:Faith]"}
{"n": "Devoted Peers", "a": "Spirit", "s": "Faith", "g": "Ap Sacrifice Upgrade", "b": {"Eva": 1, "Def": 2, "HP": 10}, "c": "Passive", "r": "any AP-sacrifice specialty", "t": "[PASSIVE] [REQ]"}
{"n": "Self-Sacrifice", "a": "Spirit", "s": "Faith", "g": "Ap Sacrifice Upgrade", "b": {"Eva": 1, "Stk": 2, "HP": 8}, "c": "Passive", "r": "4 AP per turn; any AP-sacrifice specialty", "t": "[PASSIVE] [REQ]"}
{"n": "Silent Devotion", "a": "Spirit", "s": "Faith", "g": "Ap Sacrifice Upgrade", "b": {"Eva": 2, "Pri": 1, "HP": 7}, "c": "Passive", "r": "any AP-sacrifice specialty", "t": "[PASSIVE] [REQ]"}
{"n": "Appointed Champion", "a": "Spirit", "s": "Faith", "g": "Champion", "b": {"Eva": 1, "Def": 2, "HP": 9}, "c": "Stance", "r": "", "t": "[STANCE]"}
{"n": "Conduit of Faith", "a": "Spirit", "s": "Faith", "g": "Champion", "b": {"Acc": 1, "Eva": 1, "HP": 8}, "c": "Passive", "r": "Appointed Champion", "t": "[COND] [REQ]"}
{"n": "Proclaim the Heretic", "a": "Spirit", "s": "Faith", "g": "Inquisition", "b": {"Eva": 1, "Stk": 2, "HP": 8}, "c": "Stance; 1 AP reflexive", "r": "", "t": "[STANCE]"}
{"n": "Light in the Dark", "a": "Spirit", "s": "Faith", "g": "Inquisition", "b": {"Acc": 1, "Eva": 1, "HP": 8}, "c": "Passive", "r": "Proclaim the Heretic", "t": "[COND] [REQ]"}
{"n": "Smite", "a": "Spirit", "s": "Faith", "g": "Smiting", "b": {"Acc": 1, "Stk": 1, "HP": 8}, "c": "Melee attack +1 AP (allies within 25 ft sacrifice 1 AP)", "r": "", "t": "[ATTACK+1]"}
{"n": "Assured Success", "a": "Spirit", "s": "Faith", "g": "Smiting", "b": {"Acc": 2, "Pri": 1, "HP": 6}, "c": "Passive", "r": "Smite", "t": "[COND] [REQ]"}
{"n": "Impassioned Victory", "a": "Spirit", "s": "Faith", "g": "Smiting", "b": {"Acc": 1, "Stk": 3, "HP": 7}, "c": "Passive", "r": "17 Faith; Smite", "t": "[COND] [REQ]"}
{"n": "Smiting Shot", "a": "Spirit", "s": "Faith", "g": "Smiting", "b": {"Acc": 1, "Pri": 2, "HP": 8}, "c": "Passive", "r": "Smite", "t": "[PASSIVE] [REQ]"}
{"n": "Zealous Smite", "a": "Spirit", "s": "Faith", "g": "Smiting", "b": {"Acc": 1, "Stk": 2, "HP": 7}, "c": "Passive", "r": "Smite; 7 Faith", "t": "[COND] [REQ]"}
{"n": "Bloodsoak", "a": "Spirit", "s": "Grace", "g": null, "b": {"Eva": 1, "Def": 2, "HP": 9}, "c": "Passive", "r": "4 Grace", "t": "[PASSIVE] [REQ] [SCALE:Grace]"}
{"n": "Connection", "a": "Spirit", "s": "Grace", "g": null, "b": {"Acc": 2, "Pri": 1, "HP": 7}, "c": "Stance; resist Spirit (negates)", "r": "", "t": "[STANCE]"}
{"n": "Danger Sense", "a": "Spirit", "s": "Grace", "g": null, "b": {"Eva": 1, "Pri": 5, "HP": 9}, "c": "Passive; 1 AP reflexive to warn; resist Cunning (negates)", "r": "5 Grace", "t": "[COND] [REQ]"}
{"n": "Destabilize", "a": "Spirit", "s": "Grace", "g": null, "b": {"Acc": 1, "Stk": 2, "HP": 8}, "c": "Attack +1 AP; resist Dex or Spirit (tiers down)", "r": "", "t": "[ATTACK+1]"}
{"n": "Dispel Pain", "a": "Spirit", "s": "Grace", "g": null, "b": {"Eva": 1, "Def": 3, "HP": 9}, "c": "1 AP reflexive", "r": "", "t": "[REFLEX] [SCALE:Grace]"}
{"n": "Force of Self", "a": "Spirit", "s": "Grace", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 7}, "c": "Stance; resist Spirit (negates)", "r": "", "t": "[STANCE]"}
{"n": "Inner Calm", "a": "Spirit", "s": "Grace", "g": null, "b": {"Eva": 1, "Pri": 2, "HP": 10}, "c": "Stance", "r": "", "t": "[STANCE]"}
{"n": "Iron Palm", "a": "Spirit", "s": "Grace", "g": null, "b": {"Acc": 1, "Stk": 2, "HP": 10}, "c": "Unarmed called shot +1 AP", "r": "", "t": "[ATTACK+1]"}
{"n": "Master of Forms", "a": "Spirit", "s": "Grace", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 8}, "c": "Passive", "r": "6 Grace; 2 stances known", "t": "[STANCE] [REQ] [SCALE:Grace]"}
{"n": "Parting Waves", "a": "Spirit", "s": "Grace", "g": null, "b": {"Eva": 1, "Pri": 2, "HP": 8}, "c": "1 AP reflexive; resist Dex (negates)", "r": "", "t": "[REFLEX]"}
{"n": "Shocking Soul", "a": "Spirit", "s": "Grace", "g": null, "b": {"Acc": 1, "Stk": 2, "HP": 8}, "c": "2 AP reflexive", "r": "9 Grace", "t": "[REFLEX] [REQ] [SCALE:Grace]"}
{"n": "Spirit Break", "a": "Spirit", "s": "Grace", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 8}, "c": "1 AP reflexive", "r": "", "t": "[REFLEX] [SCALE:Grace]"}
{"n": "Spiritual Seal", "a": "Spirit", "s": "Grace", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 9}, "c": "Attack +1 AP", "r": "", "t": "[ATTACK+1]"}
{"n": "Void Strike", "a": "Spirit", "s": "Grace", "g": null, "b": {"Acc": 1, "Stk": 2, "HP": 10}, "c": "Melee attack +1 AP; target may use Spirit as evade", "r": "", "t": "[ATTACK+1] [GEAR] [SCALE:Grace] reach += 5×Grace"}
{"n": "Ki Flow", "a": "Spirit", "s": "Grace", "g": "Ki-Unleashing", "b": {"Eva": 1, "Stk": 1, "HP": 10}, "c": "2 AP; resist Brute or Spirit (negates)", "r": "", "t": "[ACTION]"}
{"n": "Ki Rage", "a": "Spirit", "s": "Grace", "g": "Ki-Unleashing", "b": {"Eva": 1, "Stk": 2, "HP": 8}, "c": "Ki Flow +1 AP (3 AP total)", "r": "Ki Flow", "t": "[ACTION] [REQ]"}
{"n": "Feather in the Wind", "a": "Spirit", "s": "Grace", "g": "Light-As-Air", "b": {"Eva": 1, "Spd": 5, "HP": 6}, "c": "1 AP (as a move)", "r": "", "t": "[ACTION]"}
{"n": "Weightless", "a": "Spirit", "s": "Grace", "g": "Light-As-Air", "b": {"Acc": 1, "Eva": 1, "HP": 8}, "c": "Stance (2 AP reflexive under duress)", "r": "Feather in the Wind", "t": "[STANCE] [REQ]"}
{"n": "Touch of Paralysis", "a": "Spirit", "s": "Grace", "g": "Paralyzing", "b": {"Acc": 1, "Stk": 2, "HP": 7}, "c": "Unarmed attack +2 AP; resist Brute (negates)", "r": "", "t": "[ATTACK+2]"}
{"n": "Blocked Ki", "a": "Spirit", "s": "Grace", "g": "Paralyzing", "b": {"Acc": 1, "Stk": 2, "HP": 8}, "c": "Unarmed attack +1 AP; resist Brute or Spirit (tiers down)", "r": "Touch of Paralysis", "t": "[ATTACK+1] [REQ]"}
{"n": "Confident in your Luck", "a": "Spirit", "s": "Luck", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 7}, "c": "1 AP reflexive", "r": "", "t": "[REFLEX] [SCALE:Luck]"}
{"n": "Don't Tell Me the Odds", "a": "Spirit", "s": "Luck", "g": null, "b": {"Eva": 2, "Pri": 2, "HP": 6}, "c": "1 AP reflexive", "r": "", "t": "[REFLEX] [SCALE:Luck] 1 + floor(Luck/10)"}
{"n": "Cheat Fate", "a": "Spirit", "s": "Luck", "g": null, "b": {"Acc": 2, "Eva": 1, "HP": 6}, "c": "Stance", "r": "", "t": "[STANCE]"}
{"n": "Equalizing Force", "a": "Spirit", "s": "Luck", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 6}, "c": "2 AP reflexive", "r": "", "t": "[REFLEX]"}
{"n": "Hex", "a": "Spirit", "s": "Luck", "g": null, "b": {"Eva": 1, "Pri": 3, "HP": 7}, "c": "2 AP reflexive; resist Dex or Spirit (negates)", "r": "", "t": "[REFLEX]"}
{"n": "Jackpot", "a": "Spirit", "s": "Luck", "g": null, "b": {"Acc": 1, "Stk": 3, "HP": 8}, "c": "Passive", "r": "4 Luck", "t": "[COND] [REQ]"}
{"n": "Jinx", "a": "Spirit", "s": "Luck", "g": null, "b": {"Acc": 1, "Stk": 2, "HP": 9}, "c": "Passive (when attacked)", "r": "", "t": "[REFLEX] [SCALE:Luck]"}
{"n": "Roll of the Dice", "a": "Spirit", "s": "Luck", "g": null, "b": {"Acc": 1, "Eva": 2, "HP": 8}, "c": "Free each turn start", "r": "any other Luck specialty", "t": "[PASSIVE] [REQ]"}
{"n": "Roulette", "a": "Spirit", "s": "Luck", "g": null, "b": {"Acc": 2, "Pri": 1, "HP": 6}, "c": "Attack +1 AP", "r": "", "t": "[ATTACK+1]"}
{"n": "Spot of Misfortune", "a": "Spirit", "s": "Luck", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 7}, "c": "2 AP to create, 1 AP reflexive to enact; resist Spirit (negates)", "r": "3 Luck", "t": "[ACTION] [REQ] [SCALE:Luck]"}
{"n": "Free from Failure", "a": "Spirit", "s": "Luck", "g": "Failure Avoidance", "b": {"Eva": 1, "Pri": 2, "HP": 7}, "c": "Stance", "r": "6 Luck", "t": "[STANCE] [REQ]"}
{"n": "Steady Friends", "a": "Spirit", "s": "Luck", "g": "Failure Avoidance", "b": {"Acc": 1, "Eva": 1, "HP": 8}, "c": "1 AP reflexive", "r": "10 Luck; Free from Failure", "t": "[REFLEX] [REQ]"}
{"n": "Curse", "a": "Spirit", "s": "Luck", "g": "Foul Luck", "b": {"Eva": 1, "Def": 2, "HP": 9}, "c": "1 AP to store, 1 AP reflexive to use; resist Spirit (negates)", "r": "", "t": "[REFLEX] [SCALE:Luck]"}
{"n": "Fumble", "a": "Spirit", "s": "Luck", "g": "Foul Luck", "b": {"Acc": 1, "Eva": 1, "HP": 8}, "c": "1 AP + one stored 1; resist Spirit (negates)", "r": "Curse", "t": "[ACTION] [REQ]"}
{"n": "Ace Up My Sleeve", "a": "Spirit", "s": "Luck", "g": "Luck Holder", "b": {"Eva": 1, "Pri": 2, "HP": 6}, "c": "1 AP reflexive to store, 1 AP to use", "r": "", "t": "[REFLEX] [SCALE:Luck]"}
{"n": "Leading the Lucky Life", "a": "Spirit", "s": "Luck", "g": "Luck Holder", "b": {"Acc": 1, "Eva": 1, "HP": 9}, "c": "1 AP", "r": "Ace Up My Sleeve", "t": "[ACTION] [REQ]"}
{"n": "Second Chance", "a": "Spirit", "s": "Luck", "g": "Luck Holder", "b": {"Eva": 1, "Wnd": 1, "HP": 10}, "c": "1 AP reflexive + stored 12; resist Spirit (negates)", "r": "Ace Up My Sleeve", "t": "[REFLEX] [REQ]"}
{"n": "Lucky Number 7", "a": "Spirit", "s": "Luck", "g": "Lucky #7", "b": {"Eva": 1, "Pri": 2, "HP": 6}, "c": "Stance", "r": "", "t": "[STANCE]"}
{"n": "Luckier Number 7", "a": "Spirit", "s": "Luck", "g": "Lucky #7", "b": {"Eva": 1, "Pri": 2, "HP": 7}, "c": "Passive", "r": "Lucky Number 7; 16 Luck", "t": "[STANCE] [REQ]"}
{"n": "Feeling Lucky", "a": "Spirit", "s": "Luck", "g": "Ranged Evading", "b": {"Eva": 2, "Pri": 1, "HP": 6}, "c": "1 AP reflexive; resist Spirit (tiers down)", "r": "", "t": "[REFLEX]"}
{"n": "Unfriendly Fire", "a": "Spirit", "s": "Luck", "g": "Ranged Evading", "b": {"Acc": 1, "Eva": 2, "HP": 5}, "c": "2 AP reflexive; resist Dex (tiers down)", "r": "Feeling Lucky", "t": "[REFLEX] [REQ]"}
{"n": "Unfriendly Artillery", "a": "Spirit", "s": "Luck", "g": "Ranged Evading", "b": {"Acc": 1, "Eva": 1, "HP": 7}, "c": "Passive", "r": "Feeling Lucky; Unfriendly Fire", "t": "[COND] [REQ]"}
{"n": "Control Beast", "a": "Spirit", "s": "Shamanism", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 8}, "c": "3 AP", "r": "", "t": "[ACTION]"}
{"n": "Druidic", "a": "Spirit", "s": "Shamanism", "g": null, "b": {"Acc": 1, "Stk": 2, "HP": 8}, "c": "Stance", "r": "", "t": "[STANCE] [GEAR] DC +2 (wood/organic)"}
{"n": "Fire Resistance", "a": "Spirit", "s": "Shamanism", "g": null, "b": {"Eva": 1, "Def": 3, "HP": 10}, "c": "Passive", "r": "", "t": "[COND]"}
{"n": "Geomancer", "a": "Spirit", "s": "Shamanism", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 7}, "c": "Passive", "r": "Topographer", "t": "[COND] [REQ]"}
{"n": "Hardened Trainer", "a": "Spirit", "s": "Shamanism", "g": null, "b": {"Acc": 1, "Def": 2, "HP": 10}, "c": "Passive", "r": "", "t": "[COND] [SCALE:Shamanism]"}
{"n": "Lion's Roar", "a": "Spirit", "s": "Shamanism", "g": null, "b": {"Stk": 2, "Pri": 2, "HP": 9}, "c": "2 AP; resist Spirit (negates)", "r": "", "t": "[ACTION]"}
{"n": "Naturalist", "a": "Spirit", "s": "Shamanism", "g": null, "b": {"Eva": 1, "Def": 2, "HP": 9}, "c": "Passive", "r": "5 Shamanism", "t": "[COND] [REQ] [STAT:Soak += floor(Sham/5)]"}
{"n": "Parasite", "a": "Spirit", "s": "Shamanism", "g": null, "b": {"Stk": 2, "Pri": 2, "HP": 7}, "c": "2 AP to begin, 1 AP/turn; resist Brute (tiers down)", "r": "", "t": "[ACTION]"}
{"n": "Still as Stone", "a": "Spirit", "s": "Shamanism", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 6}, "c": "Stance", "r": "", "t": "[STANCE] [SCALE:Shamanism]"}
{"n": "Tactics of the Wolf", "a": "Spirit", "s": "Shamanism", "g": null, "b": {"Acc": 1, "Stk": 3, "HP": 8}, "c": "Melee attack, reflexive", "r": "", "t": "[REFLEX]"}
{"n": "Topographer", "a": "Spirit", "s": "Shamanism", "g": null, "b": {"Eva": 1, "Pri": 2, "HP": 7}, "c": "Passive", "r": "", "t": "[PASSIVE]"}
{"n": "Avian Wrath", "a": "Spirit", "s": "Shamanism", "g": "Bird Calling", "b": {"Acc": 1, "Eva": 1, "HP": 7}, "c": "2 AP to begin, 1 AP/turn", "r": "", "t": "[ACTION]"}
{"n": "Blacken the Sky", "a": "Spirit", "s": "Shamanism", "g": "Bird Calling", "b": {"Acc": 1, "Eva": 1, "HP": 8}, "c": "Passive; resist Cunning (negates)", "r": "Avian Wrath", "t": "[COND] [REQ]"}
{"n": "Pitch Black", "a": "Spirit", "s": "Shamanism", "g": "Bird Calling", "b": {"Acc": 1, "Eva": 1, "HP": 8}, "c": "Passive", "r": "Avian Wrath; Blacken the Sky", "t": "[COND] [REQ]"}
{"n": "Venom Immunity", "a": "Spirit", "s": "Shamanism", "g": "Chemical Immunity", "b": {"Eva": 1, "Def": 2, "HP": 10}, "c": "Passive", "r": "", "t": "[COND] [SCALE:Shamanism]"}
{"n": "Alchemical Resistance", "a": "Spirit", "s": "Shamanism", "g": "Chemical Immunity", "b": {"Eva": 1, "Def": 3, "HP": 9}, "c": "Passive", "r": "Venom Immunity", "t": "[COND] [REQ] [SCALE:Shamanism]"}
{"n": "Protect the Monarch", "a": "Spirit", "s": "Shamanism", "g": "Protective Swarm", "b": {"Def": 2, "Pri": 1, "HP": 9}, "c": "2 AP to begin, 1 AP/turn", "r": "", "t": "[ACTION] [STAT:Soak +1..+4]"}
{"n": "Devoted Drones", "a": "Spirit", "s": "Shamanism", "g": "Protective Swarm", "b": {"Def": 3, "Pri": 1, "HP": 10}, "c": "Passive", "r": "Protect the Monarch", "t": "[PASSIVE] [REQ]"}
{"n": "Hive Exodus", "a": "Spirit", "s": "Shamanism", "g": "Protective Swarm", "b": {"Def": 2, "Spd": 5, "HP": 7}, "c": "Passive", "r": "Protect the Monarch", "t": "[COND] [REQ]"}
{"n": "Colony of One", "a": "Spirit", "s": "Shamanism", "g": "Swarming Insect", "b": {"Acc": 1, "Stk": 1, "HP": 8}, "c": "2 AP to begin, 1 AP/turn; resist Brute or Dex (negates, as grab)", "r": "", "t": "[ACTION]"}
{"n": "Drag Down", "a": "Spirit", "s": "Shamanism", "g": "Swarming Insect", "b": {"Acc": 1, "Stk": 1, "HP": 8}, "c": "Passive; resist Brute (negates)", "r": "Colony of One", "t": "[COND] [REQ]"}
{"n": "Hive Mind", "a": "Spirit", "s": "Shamanism", "g": "Swarming Insect", "b": {"Acc": 1, "Eva": 1, "HP": 9}, "c": "Passive", "r": "Colony of One", "t": "[PASSIVE] [REQ]"}
{"n": "Pressure Cooker", "a": "Spirit", "s": "Shamanism", "g": "Swarming Insect", "b": {"Acc": 1, "Stk": 2, "HP": 9}, "c": "Passive", "r": "Colony of One", "t": "[COND] [REQ]"}
{"n": "Learn Augments", "a": "Sciences", "s": "General (Sciences)", "g": null, "b": {"Aug": 4, "DIY": 1, "HP": 4}, "c": "Passive (repeatable)", "r": "", "t": "[AUG] [REPEATABLE]"}
{"n": "Nothing up my Sleeve", "a": "Sciences", "s": "General (Sciences)", "g": null, "b": {"Acc": 1, "Aug": 2, "HP": 4}, "c": "Once between downtimes", "r": "", "t": "[ACTION]"}
{"n": "Self-Made Immunity", "a": "Sciences", "s": "Alchemy", "g": "Immunity", "b": {"Def": 2, "Aug": 1, "HP": 8}, "c": "Passive", "r": "Acid Brewer, Gas Brewer or Poison Brewer", "t": "[PASSIVE] [REQ]"}
{"n": "Immunizations", "a": "Sciences", "s": "Alchemy", "g": "Immunity", "b": {"Def": 2, "Aug": 1, "HP": 6}, "c": "During a breather (15+ min)", "r": "Self-Made Immunity", "t": "[ACTION] [REQ]"}
{"n": "On-the-Fly Brewer", "a": "Sciences", "s": "Alchemy", "g": "On-The-Fly", "b": {"Eva": 1, "Aug": 2, "HP": 4}, "c": "3 AP per augment slot (0-slot augments 1 AP)", "r": "", "t": "[ACTION]"}
{"n": "Expiration", "a": "Sciences", "s": "Alchemy", "g": "On-The-Fly", "b": {"Eva": 1, "Aug": 2, "HP": 4}, "c": "Passive", "r": "On-the-Fly Brewer", "t": "[COND] [REQ]"}
{"n": "Herbalist", "a": "Sciences", "s": "Alchemy", "g": "On-The-Fly", "b": {"Aug": 2, "DIY": 1, "HP": 5}, "c": "Passive", "r": "On-the-Fly Brewer", "t": "[PASSIVE] [REQ]"}
{"n": "Rapid Mixer", "a": "Sciences", "s": "Alchemy", "g": "On-The-Fly", "b": {"Eva": 1, "Aug": 1, "HP": 5}, "c": "1 AP per augment slot (0-slot free)", "r": "On-the-Fly Brewer", "t": "[ACTION] [REQ]"}
{"n": "Walking Chemical Plant", "a": "Sciences", "s": "Alchemy", "g": "On-The-Fly", "b": {"Eva": 1, "Aug": 1, "HP": 5}, "c": "Passive", "r": "On-the-Fly Brewer; Expiration", "t": "[COND] [REQ]"}
{"n": "Acid Brewer", "a": "Sciences", "s": "Alchemy", "g": "Crafting Acids", "b": {"Aug": 2, "DIY": 1, "HP": 5}, "c": "Passive (crafting)", "r": "", "t": "[AUG] [DIY] [CRAFT:acid]"}
{"n": "Beta Acids", "a": "Sciences", "s": "Alchemy", "g": "Crafting Acids", "b": {"Aug": 2, "DIY": 1, "HP": 5}, "c": "Passive", "r": "4 Alchemy; Acid Brewer", "t": "[CRAFT] [REQ]"}
{"n": "Prototype Acids", "a": "Sciences", "s": "Alchemy", "g": "Crafting Acids", "b": {"Aug": 1, "DIY": 1, "HP": 6}, "c": "Passive", "r": "16 Alchemy; Acid Brewer; Beta Acids", "t": "[CRAFT] [REQ]"}
{"n": "Gas Brewer", "a": "Sciences", "s": "Alchemy", "g": "Crafting Gases", "b": {"Aug": 4, "DIY": 1, "HP": 4}, "c": "Passive (crafting)", "r": "", "t": "[AUG] [DIY] [CRAFT:gas]"}
{"n": "Beta Gases", "a": "Sciences", "s": "Alchemy", "g": "Crafting Gases", "b": {"Aug": 2, "DIY": 1, "HP": 4}, "c": "Passive", "r": "4 Alchemy; Gas Brewer", "t": "[CRAFT] [REQ]"}
{"n": "Prototype Gases", "a": "Sciences", "s": "Alchemy", "g": "Crafting Gases", "b": {"Aug": 1, "DIY": 1, "HP": 4}, "c": "Passive", "r": "16 Alchemy; Gas Brewer; Beta Gases", "t": "[CRAFT] [REQ]"}
{"n": "Medicine Brewer", "a": "Sciences", "s": "Alchemy", "g": "Crafting Medicines", "b": {"Aug": 2, "DIY": 1, "HP": 5}, "c": "Passive (crafting)", "r": "", "t": "[AUG] [DIY] [CRAFT:medicine]"}
{"n": "Beta Medicines", "a": "Sciences", "s": "Alchemy", "g": "Crafting Medicines", "b": {"Aug": 2, "DIY": 1, "HP": 6}, "c": "Passive", "r": "4 Alchemy; Medicine Brewer", "t": "[CRAFT] [REQ]"}
{"n": "Prototype Medicine", "a": "Sciences", "s": "Alchemy", "g": "Crafting Medicines", "b": {"Aug": 1, "DIY": 1, "HP": 7}, "c": "Passive", "r": "16 Alchemy; Medicine Brewer; Beta Medicines", "t": "[CRAFT] [REQ]"}
{"n": "Poison Brewer", "a": "Sciences", "s": "Alchemy", "g": "Crafting Poisons", "b": {"Aug": 2, "DIY": 1, "HP": 4}, "c": "Passive (crafting)", "r": "", "t": "[AUG] [DIY] [CRAFT:poison]"}
{"n": "Beta Poisons", "a": "Sciences", "s": "Alchemy", "g": "Crafting Poisons", "b": {"Aug": 2, "DIY": 1, "HP": 4}, "c": "Passive", "r": "4 Alchemy; Poison Brewer", "t": "[CRAFT] [REQ]"}
{"n": "Prototype Poisons", "a": "Sciences", "s": "Alchemy", "g": "Crafting Poisons", "b": {"Aug": 1, "DIY": 1, "HP": 5}, "c": "Passive", "r": "16 Alchemy; Poison Brewer; Beta Poisons", "t": "[CRAFT] [REQ]"}
{"n": "Belt Feeder", "a": "Sciences", "s": "Armsmith", "g": null, "b": {"Eva": 2, "Aug": 1, "HP": 7}, "c": "2 AP to begin, 1 AP/turn", "r": "", "t": "[ACTION]"}
{"n": "Interchangeable Parts", "a": "Sciences", "s": "Armsmith", "g": null, "b": {"Pri": 2, "Aug": 1, "HP": 5}, "c": "3 AP to swap (general version, p.176)", "r": "", "t": "[CRAFT] [SCALE:marque]"}
{"n": "Rapid Replacements", "a": "Sciences", "s": "Armsmith", "g": null, "b": {"Eva": 1, "DIY": 1, "HP": 6}, "c": "2 AP replace / 1 AP fix", "r": "", "t": "[ACTION]"}
{"n": "Temporary Attachments", "a": "Sciences", "s": "Armsmith", "g": null, "b": {"Aug": 2, "DIY": 1, "HP": 5}, "c": "1 AP per augment slot", "r": "", "t": "[ACTION] [GEAR]"}
{"n": "Weapon Support", "a": "Sciences", "s": "Armsmith", "g": null, "b": {"Acc": 1, "Aug": 1, "HP": 6}, "c": "Stance", "r": "", "t": "[STANCE] [SCALE:Armsmith] ally Acc = 1 + floor(Arm/4)"}
{"n": "Gunsmith", "a": "Sciences", "s": "Armsmith", "g": "Crafting Firearms & Crossbows", "b": {"Aug": 2, "DIY": 1, "HP": 4}, "c": "Passive (crafting)", "r": "", "t": "[AUG] [DIY] [CRAFT:firearm]"}
{"n": "Beta Firearms", "a": "Sciences", "s": "Armsmith", "g": "Crafting Firearms & Crossbows", "b": {"Aug": 2, "DIY": 1, "HP": 4}, "c": "Passive", "r": "4 Armsmith; Gunsmith", "t": "[CRAFT] [REQ]"}
{"n": "Prototype Firearms", "a": "Sciences", "s": "Armsmith", "g": "Crafting Firearms & Crossbows", "b": {"Aug": 1, "DIY": 1, "HP": 6}, "c": "Passive", "r": "16 Armsmith; Gunsmith; Beta Firearms", "t": "[CRAFT] [REQ]"}
{"n": "Crossbow Craftsman", "a": "Sciences", "s": "Armsmith", "g": "Crafting Firearms & Crossbows", "b": {"Aug": 2, "DIY": 1, "HP": 4}, "c": "Passive (crafting)", "r": "", "t": "[AUG] [DIY] [CRAFT:crossbow]"}
{"n": "Beta Crossbows", "a": "Sciences", "s": "Armsmith", "g": "Crafting Firearms & Crossbows", "b": {"Aug": 2, "DIY": 1, "HP": 4}, "c": "Passive", "r": "4 Armsmith; Crossbow Craftsman", "t": "[CRAFT] [REQ]"}
{"n": "Prototype Crossbows", "a": "Sciences", "s": "Armsmith", "g": "Crafting Firearms & Crossbows", "b": {"Aug": 1, "DIY": 1, "HP": 6}, "c": "Passive", "r": "16 Armsmith; Crossbow Craftsman; Beta Crossbows", "t": "[CRAFT] [REQ]"}
{"n": "Weapon Smith", "a": "Sciences", "s": "Armsmith", "g": "Crafting Melee Weapons & Throwing Weapons", "b": {"Aug": 2, "DIY": 1, "HP": 4}, "c": "Passive (crafting)", "r": "", "t": "[AUG] [DIY] [CRAFT:melee]"}
{"n": "Beta Weapons", "a": "Sciences", "s": "Armsmith", "g": "Crafting Melee Weapons & Throwing Weapons", "b": {"Aug": 2, "DIY": 1, "HP": 4}, "c": "Passive", "r": "4 Armsmith; Weapon Smith", "t": "[CRAFT] [REQ]"}
{"n": "Prototype Weapons", "a": "Sciences", "s": "Armsmith", "g": "Crafting Melee Weapons & Throwing Weapons", "b": {"Aug": 1, "DIY": 1, "HP": 5}, "c": "Passive", "r": "16 Armsmith; Weapon Smith; Beta Weapons", "t": "[CRAFT] [REQ]"}
{"n": "Interchangeable Parts", "a": "Sciences", "s": "Armsmith", "g": "Crafting Melee Weapons & Throwing Weapons", "b": {"Pri": 2, "Aug": 1, "HP": 5}, "c": "3 AP to swap (melee version, p.182)", "r": "Weapon Smith", "t": "[CRAFT] [REQ]"}
{"n": "Bowyer", "a": "Sciences", "s": "Armsmith", "g": "Crafting Bows", "b": {"Aug": 2, "DIY": 1, "HP": 4}, "c": "Passive (crafting)", "r": "", "t": "[AUG] [DIY] [CRAFT:bow]"}
{"n": "Beta Bows", "a": "Sciences", "s": "Armsmith", "g": "Crafting Bows", "b": {"Aug": 2, "DIY": 1, "HP": 4}, "c": "Passive", "r": "4 Armsmith; Bowyer", "t": "[CRAFT] [REQ]"}
{"n": "Prototype Bows", "a": "Sciences", "s": "Armsmith", "g": "Crafting Bows", "b": {"Aug": 1, "DIY": 1, "HP": 4}, "c": "Passive", "r": "16 Armsmith; Bowyer; Beta Bows", "t": "[CRAFT] [REQ]"}
{"n": "Armor Smith", "a": "Sciences", "s": "Armsmith", "g": "Crafting Armor", "b": {"Aug": 2, "DIY": 1, "HP": 5}, "c": "Passive (crafting)", "r": "", "t": "[AUG] [DIY] [CRAFT:armor]"}
{"n": "Beta Armor", "a": "Sciences", "s": "Armsmith", "g": "Crafting Armor", "b": {"Aug": 2, "DIY": 1, "HP": 5}, "c": "Passive", "r": "4 Armsmith; Armor Smith", "t": "[CRAFT] [REQ]"}
{"n": "Prototype Armor", "a": "Sciences", "s": "Armsmith", "g": "Crafting Armor", "b": {"Aug": 1, "DIY": 1, "HP": 6}, "c": "Passive", "r": "16 Armsmith; Armor Smith; Beta Armor", "t": "[CRAFT] [REQ]"}
{"n": "Automaton Repairs", "a": "Sciences", "s": "Automata", "g": null, "b": {"Def": 2, "Aug": 2, "HP": 7}, "c": "3 AP", "r": "", "t": "[ACTION]"}
{"n": "Interchangeable Parts", "a": "Sciences", "s": "Automata", "g": null, "b": {"Aug": 2, "DIY": 1, "HP": 6}, "c": "3 AP to swap", "r": "", "t": "[CRAFT] [SCALE:marque]"}
{"n": "Steam-Powered Crafter", "a": "Sciences", "s": "Automata", "g": "Crafting Steamers", "b": {"Aug": 2, "DIY": 1, "HP": 4}, "c": "Passive (crafting)", "r": "", "t": "[AUG] [DIY] [CRAFT:steamer]"}
{"n": "Beta Boilers", "a": "Sciences", "s": "Automata", "g": "Crafting Steamers", "b": {"Aug": 2, "DIY": 1, "HP": 4}, "c": "Passive", "r": "4 Automata; Steam-Powered Crafter", "t": "[CRAFT] [REQ]"}
{"n": "Prototype Boilers", "a": "Sciences", "s": "Automata", "g": "Crafting Steamers", "b": {"Aug": 1, "DIY": 1, "HP": 5}, "c": "Passive", "r": "16 Automata; Steam-Powered Crafter; Beta Boilers", "t": "[CRAFT] [REQ]"}
{"n": "Steamer Operator", "a": "Sciences", "s": "Automata", "g": "Steamer Operator", "b": {"Acc": 1, "Eva": 1, "HP": 6}, "c": "Passive", "r": "", "t": "[PASSIVE]"}
{"n": "Steam Poser", "a": "Sciences", "s": "Automata", "g": "Steamer Operator", "b": {"Eva": 1, "Aug": 1, "HP": 7}, "c": "Passive", "r": "Steamer Operator; ≥1 stance known", "t": "[PASSIVE] [REQ]"}
{"n": "Steam Specialist", "a": "Sciences", "s": "Automata", "g": "Steamer Operator", "b": {"Acc": 1, "Aug": 1, "HP": 6}, "c": "Passive", "r": "3 Automata; Steamer Operator", "t": "[PASSIVE] [REQ]"}
{"n": "Fuse Box Builder", "a": "Sciences", "s": "Automata", "g": "Crafting Fuse Boxes", "b": {"Aug": 2, "DIY": 1, "HP": 4}, "c": "Passive (crafting)", "r": "", "t": "[AUG] [DIY] [CRAFT:fusebox]"}
{"n": "Advanced Brainworks", "a": "Sciences", "s": "Automata", "g": "Crafting Fuse Boxes", "b": {"Aug": 2, "DIY": 1, "HP": 4}, "c": "Passive", "r": "4 Automata; Fuse Box Builder", "t": "[CRAFT] [REQ]"}
{"n": "Superior Brainworks", "a": "Sciences", "s": "Automata", "g": "Crafting Fuse Boxes", "b": {"Aug": 2, "DIY": 1, "HP": 6}, "c": "Passive", "r": "6 Automata; Fuse Box Builder", "t": "[CRAFT] [REQ]"}
{"n": "Heroic Brainworks", "a": "Sciences", "s": "Automata", "g": "Crafting Fuse Boxes", "b": {"Aug": 2, "DIY": 1, "HP": 5}, "c": "Passive", "r": "9 Automata; Fuse Box Builder; Superior Brainworks", "t": "[CRAFT] [REQ]"}
{"n": "Personality", "a": "Sciences", "s": "Automata", "g": "Crafting Fuse Boxes", "b": {"Aug": 2, "DIY": 1, "HP": 5}, "c": "Passive", "r": "Fuse Box Builder", "t": "[CRAFT] [REQ]"}
{"n": "Clockwork Crafter", "a": "Sciences", "s": "Automata", "g": "Crafting Clockworks", "b": {"Aug": 2, "DIY": 1, "HP": 4}, "c": "Passive (crafting)", "r": "", "t": "[AUG] [DIY] [CRAFT:clockwork]"}
{"n": "Advanced Analytics", "a": "Sciences", "s": "Automata", "g": "Crafting Clockworks", "b": {"Aug": 2, "DIY": 1, "HP": 5}, "c": "Passive", "r": "4 Automata; Clockwork Crafter", "t": "[CRAFT] [REQ]"}
{"n": "Prosthetician", "a": "Sciences", "s": "Automata", "g": "Crafting Prosthetics", "b": {"Aug": 2, "DIY": 1, "HP": 6}, "c": "Passive (crafting)", "r": "", "t": "[AUG] [DIY] [CRAFT:prosthetic]"}
{"n": "Beta Prosthetics", "a": "Sciences", "s": "Automata", "g": "Crafting Prosthetics", "b": {"Aug": 2, "DIY": 1, "HP": 6}, "c": "Passive", "r": "4 Automata; Prosthetician", "t": "[CRAFT] [REQ]"}
{"n": "Prototype Prosthetics", "a": "Sciences", "s": "Automata", "g": "Crafting Prosthetics", "b": {"Aug": 1, "DIY": 1, "HP": 7}, "c": "Passive", "r": "16 Automata; Prosthetician; Beta Prosthetics", "t": "[CRAFT] [REQ]"}
{"n": "Automata Tinkerer", "a": "Sciences", "s": "Automata", "g": "Crafting Prosthetics", "b": {"Aug": 2, "DIY": 1, "HP": 4}, "c": "Passive", "r": "3 Automata; Prosthetician", "t": "[AUG] [REQ]"}
{"n": "Automata Upgrader", "a": "Sciences", "s": "Automata", "g": "Crafting Prosthetics", "b": {"Aug": 2, "DIY": 1, "HP": 4}, "c": "Passive", "r": "3 Automata; Prosthetician", "t": "[CRAFT] [REQ]"}
{"n": "Nerve Crafting", "a": "Sciences", "s": "Automata", "g": "Crafting Prosthetics", "b": {"Aug": 1, "DIY": 1, "HP": 7}, "c": "Passive", "r": "7 Automata; Prosthetician", "t": "[CRAFT] [REQ] [STAT:Wnd −1 per extra limb]"}
{"n": "Sensory Builder", "a": "Sciences", "s": "Automata", "g": "Crafting Prosthetics", "b": {"Aug": 2, "DIY": 1, "HP": 7}, "c": "Passive", "r": "Prosthetician", "t": "[CRAFT] [REQ]"}
{"n": "Bio-Invigoration", "a": "Sciences", "s": "Bio-Flux", "g": "Invigoration", "b": {"Eva": 1, "Def": 3, "HP": 8}, "c": "3 AP", "r": "", "t": "[ACTION]"}
{"n": "Bio-Invigoration Expert", "a": "Sciences", "s": "Bio-Flux", "g": "Invigoration", "b": {"Eva": 1, "Pri": 3, "HP": 9}, "c": "Passive", "r": "Bio-Invigoration", "t": "[COND] [REQ]"}
{"n": "Quickshot Bio-Invigoration", "a": "Sciences", "s": "Bio-Flux", "g": "Invigoration", "b": {"Eva": 1, "Spd": 5, "HP": 8}, "c": "Passive", "r": "Bio-Invigoration", "t": "[PASSIVE] [REQ]"}
{"n": "Medical Marvel", "a": "Sciences", "s": "Bio-Flux", "g": "Invigoration", "b": {"Eva": 1, "Wnd": 1, "HP": 11}, "c": "Passive", "r": "Bio-Invigoration", "t": "[COND] [REQ]"}
{"n": "Self-Administer", "a": "Sciences", "s": "Bio-Flux", "g": "Invigoration", "b": {"Acc": 1, "Eva": 1, "HP": 11}, "c": "Passive", "r": "Bio-Invigoration", "t": "[PASSIVE] [REQ]"}
{"n": "Manipulate Essence", "a": "Sciences", "s": "Bio-Flux", "g": "Essence Manipulation", "b": {"Aug": 2, "DIY": 1, "HP": 6}, "c": "Passive (crafting, downtime)", "r": "", "t": "[AUG] [DIY] [CRAFT:essence]"}
{"n": "Beta Essence", "a": "Sciences", "s": "Bio-Flux", "g": "Essence Manipulation", "b": {"Aug": 2, "DIY": 1, "HP": 6}, "c": "Passive", "r": "4 Bio-Flux; Manipulate Essence", "t": "[CRAFT] [REQ] [STAT:own essence slots +2]"}
{"n": "Prototype Essence", "a": "Sciences", "s": "Bio-Flux", "g": "Essence Manipulation", "b": {"Aug": 2, "DIY": 1, "HP": 6}, "c": "Passive", "r": "16 Bio-Flux; Manipulate Essence; Beta Essence", "t": "[CRAFT] [REQ]"}
{"n": "Fast Manipulation", "a": "Sciences", "s": "Bio-Flux", "g": "Essence Manipulation", "b": {"Eva": 1, "Aug": 2, "HP": 7}, "c": "3 AP; resist Spirit (negates)", "r": "6 Bio-Flux; Manipulate Essence", "t": "[ACTION] [REQ]"}
{"n": "Body Renewal", "a": "Sciences", "s": "Bio-Flux", "g": "Essence Manipulation", "b": {"Def": 2, "Aug": 1, "HP": 9}, "c": "3 AP", "r": "Manipulate Essence", "t": "[ACTION] [REQ]"}
{"n": "Gene Therapy", "a": "Sciences", "s": "Bio-Flux", "g": "Essence Manipulation", "b": {"Aug": 2, "Wnd": 1, "HP": 9}, "c": "Once per downtime", "r": "16 Bio-Flux; Manipulate Essence; Body Renewal", "t": "[ACTION] [REQ]"}
{"n": "Bio-Zapper Developer", "a": "Sciences", "s": "Bio-Flux", "g": "Crafting Bio-Zappers", "b": {"Aug": 2, "DIY": 1, "HP": 4}, "c": "Passive (crafting)", "r": "", "t": "[AUG] [DIY] [CRAFT:biozapper]"}
{"n": "Beta Bio-Zappers", "a": "Sciences", "s": "Bio-Flux", "g": "Crafting Bio-Zappers", "b": {"Aug": 2, "DIY": 1, "HP": 4}, "c": "Passive", "r": "4 Bio-Flux; Bio-Zapper Developer", "t": "[CRAFT] [REQ]"}
{"n": "Prototype Bio-Zappers", "a": "Sciences", "s": "Bio-Flux", "g": "Crafting Bio-Zappers", "b": {"Aug": 1, "DIY": 1, "HP": 4}, "c": "Passive", "r": "16 Bio-Flux; Bio-Zapper Developer; Beta Bio-Zappers", "t": "[CRAFT] [REQ]"}
{"n": "Concentrated Stream", "a": "Sciences", "s": "Bio-Flux", "g": "Crafting Bio-Zappers", "b": {"Acc": 1, "Aug": 2, "HP": 6}, "c": "Bio-zapper attack, then 1 AP/turn", "r": "", "t": "[ACTION]"}
{"n": "Extra Settings", "a": "Sciences", "s": "Bio-Flux", "g": "Crafting Bio-Zappers", "b": {"Aug": 2, "DIY": 1, "HP": 4}, "c": "Passive", "r": "", "t": "[CRAFT] [SCALE:marque]"}
{"n": "Multi-Ray", "a": "Sciences", "s": "Bio-Flux", "g": "Crafting Bio-Zappers", "b": {"Acc": 1, "Aug": 1, "HP": 6}, "c": "Bio-zapper attack +1 AP", "r": "", "t": "[ATTACK+1]"}
{"n": "Splicer", "a": "Sciences", "s": "Bio-Flux", "g": "Crafting Bio-Zappers", "b": {"Acc": 1, "Aug": 1, "HP": 6}, "c": "Passive", "r": "", "t": "[PASSIVE]"}
{"n": "Tracing", "a": "Sciences", "s": "Bio-Flux", "g": "Crafting Bio-Zappers", "b": {"Acc": 1, "Aug": 1, "HP": 7}, "c": "Bio-zapper attack +1 AP", "r": "", "t": "[ATTACK+1]"}
{"n": "Maintenance", "a": "Sciences", "s": "Engineer", "g": null, "b": {"Aug": 2, "DIY": 1, "HP": 6}, "c": "Stance", "r": "2 Engineer", "t": "[STANCE] [REQ] [SCALE:Engineer]"}
{"n": "Power Surge", "a": "Sciences", "s": "Engineer", "g": null, "b": {"Aug": 1, "Pri": 3, "HP": 6}, "c": "1 AP (not the pilot)", "r": "", "t": "[ACTION]"}
{"n": "Quick Upgrades", "a": "Sciences", "s": "Engineer", "g": null, "b": {"Aug": 2, "DIY": 1, "HP": 5}, "c": "Engineer roll per slot swapped", "r": "", "t": "[ACTION]"}
{"n": "Vehicle Repairs", "a": "Sciences", "s": "Engineer", "g": null, "b": {"Def": 2, "Aug": 1, "HP": 7}, "c": "3 AP", "r": "Auto-Wright or Manual-Wright", "t": "[ACTION] [REQ]"}
{"n": "Gearhead", "a": "Sciences", "s": "Engineer", "g": "Grease Monkey", "b": {"Aug": 1, "DIY": 1, "HP": 5}, "c": "Stance (in/adjacent to vehicle)", "r": "2 Engineer", "t": "[STANCE] [REQ] [SCALE:Engineer]"}
{"n": "Gearjunkie", "a": "Sciences", "s": "Engineer", "g": "Grease Monkey", "b": {"Aug": 1, "Eva": 1, "HP": 6}, "c": "Passive", "r": "5 Engineer; Gearhead", "t": "[COND] [REQ] [SCALE:Engineer]"}
{"n": "Auto-Wright", "a": "Sciences", "s": "Engineer", "g": "Crafting Vehicles", "b": {"Aug": 2, "DIY": 1, "HP": 4}, "c": "Passive (crafting)", "r": "", "t": "[AUG] [DIY] [CRAFT:auto]"}
{"n": "Beta Autos", "a": "Sciences", "s": "Engineer", "g": "Crafting Vehicles", "b": {"Aug": 2, "DIY": 1, "HP": 5}, "c": "Passive", "r": "4 Engineer; Auto-Wright", "t": "[CRAFT] [REQ]"}
{"n": "Prototype Autos", "a": "Sciences", "s": "Engineer", "g": "Crafting Vehicles", "b": {"Aug": 1, "DIY": 1, "HP": 6}, "c": "Passive", "r": "16 Engineer; Auto-Wright; Beta Autos", "t": "[CRAFT] [REQ]"}
{"n": "Manual-Wright", "a": "Sciences", "s": "Engineer", "g": "Crafting Vehicles", "b": {"Aug": 2, "DIY": 1, "HP": 4}, "c": "Passive (crafting)", "r": "", "t": "[AUG] [DIY] [CRAFT:clanker]"}
{"n": "Beta Clankers", "a": "Sciences", "s": "Engineer", "g": "Crafting Vehicles", "b": {"Aug": 2, "DIY": 1, "HP": 5}, "c": "Passive", "r": "4 Engineer; Manual-Wright", "t": "[CRAFT] [REQ]"}
{"n": "Prototype Clankers", "a": "Sciences", "s": "Engineer", "g": "Crafting Vehicles", "b": {"Aug": 1, "DIY": 1, "HP": 5}, "c": "Passive", "r": "16 Engineer; Manual-Wright; Beta Clankers", "t": "[CRAFT] [REQ]"}
{"n": "Vehicle Armorer", "a": "Sciences", "s": "Engineer", "g": "Armoring Vehicles", "b": {"Aug": 2, "DIY": 1, "HP": 6}, "c": "Passive (crafting)", "r": "", "t": "[AUG] [DIY] [CRAFT:vehicle armor]"}
{"n": "Beta Armoring", "a": "Sciences", "s": "Engineer", "g": "Armoring Vehicles", "b": {"Aug": 2, "DIY": 1, "HP": 6}, "c": "Passive", "r": "4 Engineer; Vehicle Armorer", "t": "[CRAFT] [REQ]"}
{"n": "Prototype Armoring", "a": "Sciences", "s": "Engineer", "g": "Armoring Vehicles", "b": {"Aug": 1, "DIY": 1, "HP": 7}, "c": "Passive", "r": "16 Engineer; Vehicle Armorer; Beta Armoring", "t": "[CRAFT] [REQ]"}
{"n": "Beta Hacker", "a": "Sciences", "s": "Gadgetry", "g": null, "b": {"Eva": 1, "Aug": 1, "HP": 8}, "c": "Passive", "r": "", "t": "[COND] [SCALE:Gadgetry]"}
{"n": "Dud", "a": "Sciences", "s": "Gadgetry", "g": null, "b": {"Acc": 1, "Eva": 1, "HP": 7}, "c": "1 AP reflexive; resist Cunning (negates)", "r": "", "t": "[REFLEX]"}
{"n": "Item Breaker", "a": "Sciences", "s": "Gadgetry", "g": null, "b": {"Acc": 1, "Stk": 3, "HP": 9}, "c": "As a sunder", "r": "Saboteur", "t": "[ATTACK+0] [REQ]"}
{"n": "Reverse Engineer", "a": "Sciences", "s": "Gadgetry", "g": null, "b": {"Aug": 2, "DIY": 1, "HP": 5}, "c": "During a breather", "r": "", "t": "[ACTION]"}
{"n": "Saboteur", "a": "Sciences", "s": "Gadgetry", "g": null, "b": {"Acc": 1, "Pri": 3, "HP": 8}, "c": "1 AP; resist Dex (negates)", "r": "", "t": "[ACTION]"}
{"n": "Improvised Improvements", "a": "Sciences", "s": "Gadgetry", "g": null, "b": {"Eva": 1, "Aug": 1, "HP": 7}, "c": "Stance", "r": "4 Gadgetry", "t": "[STANCE] [REQ] [SCALE:Gadgetry]"}
{"n": "Pyrotechnician", "a": "Sciences", "s": "Gadgetry", "g": "Crafting Explosives", "b": {"Aug": 2, "DIY": 1, "HP": 4}, "c": "Passive (crafting)", "r": "", "t": "[AUG] [DIY] [CRAFT:explosive]"}
{"n": "Beta Explosives", "a": "Sciences", "s": "Gadgetry", "g": "Crafting Explosives", "b": {"Aug": 2, "DIY": 1, "HP": 5}, "c": "Passive", "r": "4 Gadgetry; Pyrotechnician", "t": "[CRAFT] [REQ]"}
{"n": "Prototype Explosives", "a": "Sciences", "s": "Gadgetry", "g": "Crafting Explosives", "b": {"Aug": 2, "DIY": 1, "HP": 6}, "c": "Passive", "r": "16 Gadgetry; Pyrotechnician; Beta Explosives", "t": "[CRAFT] [REQ]"}
{"n": "Major Explosion", "a": "Sciences", "s": "Gadgetry", "g": "Crafting Explosives", "b": {"Aug": 2, "DIY": 1, "HP": 4}, "c": "Activating fuse +1 AP", "r": "", "t": "[ACTION]"}
{"n": "Optician", "a": "Sciences", "s": "Gadgetry", "g": "Crafting Eyewear", "b": {"Aug": 2, "DIY": 1, "HP": 4}, "c": "Passive (crafting)", "r": "", "t": "[AUG] [DIY] [CRAFT:eyewear]"}
{"n": "Beta Eyewear", "a": "Sciences", "s": "Gadgetry", "g": "Crafting Eyewear", "b": {"Aug": 2, "DIY": 1, "HP": 4}, "c": "Passive", "r": "4 Gadgetry; Optician", "t": "[CRAFT] [REQ]"}
{"n": "Prototype Eyewear", "a": "Sciences", "s": "Gadgetry", "g": "Crafting Eyewear", "b": {"Aug": 2, "DIY": 1, "HP": 5}, "c": "Passive", "r": "16 Gadgetry; Optician; Beta Eyewear", "t": "[CRAFT] [REQ]"}
{"n": "Trinket Crafter", "a": "Sciences", "s": "Gadgetry", "g": "Crafting Trinkets", "b": {"Aug": 2, "DIY": 1, "HP": 4}, "c": "Passive (crafting)", "r": "", "t": "[AUG] [DIY] [CRAFT:trinket]"}
```
