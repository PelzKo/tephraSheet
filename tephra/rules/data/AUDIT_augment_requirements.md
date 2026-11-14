# Audit: augment requirements and restrictions

Package F (2026-11-14). Every augment of the core book and of all extensions (`rules/data/augments.json`, built from
`rules/data/source/Tephra_Reference_full.md` and `rules/data/ext/*/augments.json`) was scanned by script for
qualifiers (`req. X`, `light only`, …) and for requirement wording in the text ("Requires:", "only be placed", "light
weapon", "throwing", "cannot be applied" …); every hit was read against the book text. Dependencies were resolved per
list section: the required augment must share a list with the dependent one (same-named augments on other lists are
different augments, e.g. melee Custom ≠ firearm/crossbow Custom ≠ bow Custom).

Classes:

- **(a) character learning prerequisite**: a specialty, skill points, an augment the character must know, a marque.
  Checked by `rules/engine/requirements.check_augment`.
- **(b) item prerequisite**: another augment on the same item ("placed on weapon with Custom"), AND/OR preserved.
  Data: `curated.AUGMENT_ITEM_RULES[slug]["needs"]`; checked by `rules/engine/item_requirements.py` when augments are
  put on an item. Its `"from"` qualifiers are no longer learning requirements.
- **(c) item restriction**: kind, size, material, variant (throwing, flexible), reload time, exclusions.
- **(d) prose only / unclear**: not checkable or ambiguous; listed below.

Where the predicates live: `rules/curated.py` `AUGMENT_ITEM_RULES` (item: `needs`, `needs_waived_by`, `sizes`,
`materials`, `variants`, `max_ready`, `excludes`, `from`) and `AUGMENT_LEARN` (special learning rules). The augment
`size` field was NOT read as an installation restriction (trinket sizes describe the constructed object).

## Decisions

- **Aerodynamic counts as throwing** for Propelled/Returning ("you may throw it like a weapon designed for throwing";
  `item_requirements.GRANTS_VARIANT`).
- **Aether-shaped weapons** take Signature Weapon without Custom (Aether p.5: "Signature Weapon (no Custom needed)");
  aether-synced does not.
- **Rotating Barrels**: "firearms that use ammunition and have a reload time of 2 AP or less" → base AP to ready (the
  item's own value, else the size table) ≤ 2. "Use ammunition" is not checked (every firearm in the app does).
- **Split Shot**: "cannot be applied to rounds containing a substance (Syringed, Inkshot, Flash-Bangs, …)" → excludes
  those three (the "…" can't be enumerated).
- **Extended Blast** "req. mQ II explosives" → learning: marque II in the augment's skill. Before, it could never be met.
- **Explosive "req. X"** (extension) = X on the same bomb (they modify that bomb's fire/knock back/fuse). Shockwave's
  "Knock Back" is the core explosive augment "Knockback" (`gadgetry-explosive-knockback`); the squib Knock Back is on
  another list.
- **Resonator "req. X"** = X on the same resonator (Aether notes).
- **Living liquids** Defensive / Lifting Liquid: "Requires: X augment" read as the same liquid (Lifting Liquid "moves
  using its lighter-than-air speed").
- **Mementos**: Master of Fortune / Lost & Stolen say "on the memento" → (b). Fumble says only "Requires: Hand Slip
  augment" while the same section words others as "on the memento" and "specialty known" → kept as (a) learning.
- **Turrets** "Automated turret" / "Automated augment" → Automated on the same turret.
- Ambiguous bare "Requires: X augment" on non-item lists (acid Thick Rust, essence Metal Exoskeleton/Osmote, animal
  traits) stay (a) learning requirements as before (conservative: no change).
- Specialty conditions worded as the item ("weapon made with Interchangeable Parts", "Brainworks built with
  Personality") stay (a): the crafter needs the specialty. Bow Easily Altered gets the same qualifier as the melee and
  firearm ones (the bow table lacked it).
- Prosthetics, automata (clockwork, fusebox, steamer), vehicles and vehicle armor have no catalog item; their (b)/(c)
  conditions are classified and no longer block learning, but nothing checks them on the automaton/body.

## (d) prose only / unclear

- `automata-clockwork-shadow-me-subdirective`: qualifier "text says req. Go-There"; the Hedge-/Mark-/Secure-Your-Area,
  Sprint-to-Me, March-/Run-There, Protect-Us/-Yourself, Shield-Yourself subdirectives require their Directive in the
  text but have no qualifier. All are analytics (clockwork) conditions = (b) on a non-item; not checked.
- `bio-flux-essence-specialized-animal`: "needs a known animal special trait" (the animal's traits, pets validator).
- `armsmith-turret-automated`: "Requires: 1 skill point in Automata & turret has a 0 AP readying cost" – neither part
  is checked (the readying cost can depend on other augments such as Automatic Reload).
- `gadgetry-explosive-target-processing`: "for use with mines" (no mine flag on items).
- `luck-memento-eau-de-bile`: "can only be placed on an object after a successful called shot to the groin" (event).
- Aether-shaped weapons allow only 15 named melee augments, max 3 (5 with Beta Weapons), unless Aetherform Modules:
  depends on the crafter's specialties, not checked.
- `automata-prosthetic-furnace` "cannot apply to a wooden prosthetic", `automata-prosthetic-arm-grasper` "no two-handed
  items": target restrictions on prosthetics (no item).

## Inconsistent source entries (reported, not rewritten)

- `armsmith-bow-burn-trail-everburning`: the parser merged the bow Burn Trail and Everburning texts into one entry with
  no text and no qualifier; the book has two augments, both "placed on bow with the Combustion augment". Classified as
  needing bow Combustion on the same bow.
- Living liquid Defensive: book typo "Interior Platements" (data already says Interior Platelets).
- Shockwave: "Knock Back" vs the augment name "Knockback".

## Table

Augments audited: 714 (core 427, extensions 287); with a requirement/restriction clause: 90

| Class | Clauses |
|---|---|
| (a) character learning prerequisite | 22 |
| (b) item prerequisite (augment on the same item) | 57 |
| (c) item restriction | 21 |
| (d) prose only / unclear (qualifier clauses; more in the (d) list) | 2 |

| Augment (slug) | Source | Book qualifier | Class | Check |
|---|---|---|---|---|
| `alchemy-acid-thick-rust` | core | req. Rusting | a | learning: specialty/augment known (checked by check_augment) |
| `alchemy-medicine-improved-push` | core | req. Push | a | learning: specialty/augment known (checked by check_augment) |
| `armsmith-firearm-crank-free` | core | req. Rotating Barrels | b | same item: armsmith-firearm-rotating-barrels |
| `armsmith-firearm-crossbow-easily-altered` | core | req. Interchangeable Parts | a | learning: specialty/augment known (checked by check_augment) |
| `armsmith-firearm-crossbow-gnome-sized` | core | light only | c | size one of light |
| `armsmith-firearm-rotating-barrels` | core | (text) | c | base AP to ready ≤ 2 |
| `armsmith-firearm-crossbow-signature-weapon` | core | req. Custom | b | same item: armsmith-firearm-crossbow-custom |
| `armsmith-melee-chainsaw` | core | melee | c | kind melee: enforced by the augment list (melee augments only fit melee items) |
| `armsmith-melee-burn-trail` | core | req. Combustion | b | same item: armsmith-melee-combustion |
| `armsmith-melee-everburning` | core | req. Combustion | b | same item: armsmith-melee-combustion |
| `armsmith-melee-easily-altered` | core | req. Interchangeable Parts | a | learning: specialty/augment known (checked by check_augment) |
| `armsmith-melee-electrical-archs` | core | req. Electrical | b | same item: armsmith-melee-electrical |
| `armsmith-melee-long-archs` | core | req. Electrical Archs | b | same item: armsmith-melee-electrical-archs |
| `armsmith-melee-gnome-sized` | core | light | c | size one of light |
| `armsmith-melee-propelled` | core | throwing | c | variant one of throwing |
| `armsmith-melee-returning` | core | throwing | c | variant one of throwing |
| `armsmith-melee-signature-weapon` | core | req. Custom | b | same item: armsmith-melee-custom (waived by variant aether) |
| `armsmith-melee-specialized` | core | req. Custom | b | same item: armsmith-melee-custom |
| `armsmith-melee-streamlined` | core | light/medium | c | size one of light, medium |
| `armsmith-melee-tangling` | core | flexible | c | variant one of flexible |
| `armsmith-bow-easily-altered` | core | req. Interchangeable Parts | a | learning: specialty/augment known (checked by check_augment) |
| `armsmith-bow-burn-trail-everburning` | core | (text) | b | same item: armsmith-bow-combustion |
| `automata-fusebox-master-fuse-box` | core | req. Specialist | b | same item/body, NOT enforced: the app has no item for list fusebox |
| `automata-fusebox-spiritual-connection` | core | req. Personality | a | learning: specialty/augment known (checked by check_augment) |
| `automata-clockwork-hit-them-subdirective` | core | req. Avenge-Me | b | same item/body, NOT enforced: the app has no item for list clockwork |
| `automata-clockwork-hurt-them-subdirective` | core | req. Avenge-Me | b | same item/body, NOT enforced: the app has no item for list clockwork |
| `automata-clockwork-shadow-me-subdirective` | core | text says req. Go-There | d | display only, see (d) list |
| `automata-prosthetic-air-conditioner` | core | req. Air Blaster | b | same item/body, NOT enforced: the app has no item for list prosthetic |
| `automata-prosthetic-air-tunnel` | core | req. Air Blaster | b | same item/body, NOT enforced: the app has no item for list prosthetic |
| `automata-prosthetic-cold-iron` | core | metal | c | restriction on the target, NOT enforced: the app has no item for list prosthetic |
| `automata-prosthetic-cold-iron` | core | req. Freezer | b | same item/body, NOT enforced: the app has no item for list prosthetic |
| `automata-prosthetic-flame-exhausts` | core | req. Furnace | b | same item/body, NOT enforced: the app has no item for list prosthetic |
| `automata-prosthetic-freeze-exhausts` | core | req. Freezer | b | same item/body, NOT enforced: the app has no item for list prosthetic |
| `automata-prosthetic-hidden-blade` | core | req. Weapon Mounting | b | same item/body, NOT enforced: the app has no item for list prosthetic |
| `automata-prosthetic-hidden-claymore` | core | req. Hidden Blade | b | same item/body, NOT enforced: the app has no item for list prosthetic |
| `automata-prosthetic-hot-iron` | core | metal | c | restriction on the target, NOT enforced: the app has no item for list prosthetic |
| `automata-prosthetic-hot-iron` | core | req. Furnace | b | same item/body, NOT enforced: the app has no item for list prosthetic |
| `automata-prosthetic-overglow` | core | req. Glowing | b | same item/body, NOT enforced: the app has no item for list prosthetic |
| `automata-prosthetic-smokestack` | core | req. Furnace or Freezer | b | same item/body, NOT enforced: the app has no item for list prosthetic |
| `bio-flux-essence-metal-exoskeleton` | core | req. Exoskeleton | a | learning: specialty/augment known (checked by check_augment) |
| `bio-flux-essence-osmote` | core | req. Jellyskin | a | learning: specialty/augment known (checked by check_augment) |
| `engineer-auto-blazing-speed` | core | req. Improved Speed | b | same item/body, NOT enforced: the app has no item for list auto |
| `engineer-auto-clanker-extra-passengers` | core | req. Passenger | b | same item/body, NOT enforced: the app has no item for list auto/clanker |
| `engineer-vehicle-armor-exceptional-structure` | core | req. Structural Integrity | b | same item/body, NOT enforced: the app has no item for list vehicle armor |
| `gadgetry-explosive-extended-blast` | core | req. mQ II explosives | a | learning: marque ≥ 2 (check_augment) |
| `automata-prosthetic-arm-extendable-hand` | core | arm with a hand | c | restriction on the target, NOT enforced: the app has no item for list prosthetic |
| `automata-prosthetic-hand-flame-pores` | core | req. Furnace | b | same item/body, NOT enforced: the app has no item for list prosthetic |
| `automata-prosthetic-hand-freezing-pores` | core | req. Freezer | b | same item/body, NOT enforced: the app has no item for list prosthetic |
| `automata-prosthetic-hand-retractable` | core | req. Hand-Launcher | b | same item/body, NOT enforced: the app has no item for list prosthetic |
| `automata-prosthetic-head-sensory-transmission` | core | automaton only | c | restriction on the target, NOT enforced: the app has no item for list prosthetic |
| `automata-prosthetic-head-sensory-transmission` | core | req. Automata Tinkerer | a | learning: specialty/augment known (checked by check_augment) |
| `automata-prosthetic-torso-back-pack` | core | automaton only | c | restriction on the target, NOT enforced: the app has no item for list prosthetic |
| `automata-prosthetic-torso-back-pack` | core | req. Automata Tinkerer | a | learning: specialty/augment known (checked by check_augment) |
| `automata-prosthetic-torso-mass-propulsion` | core | automaton only | c | restriction on the target, NOT enforced: the app has no item for list prosthetic |
| `automata-prosthetic-torso-mass-propulsion` | core | req. Automata Tinkerer | a | learning: specialty/augment known (checked by check_augment) |
| `automata-prosthetic-torso-poison-gas-epicenter` | core | automaton only | c | restriction on the target, NOT enforced: the app has no item for list prosthetic |
| `automata-prosthetic-torso-poison-gas-epicenter` | core | req. Automata Tinkerer | a | learning: specialty/augment known (checked by check_augment) |
| `automata-prosthetic-torso-poison-gas-receptor` | core | automaton only | c | restriction on the target, NOT enforced: the app has no item for list prosthetic |
| `automata-prosthetic-torso-poison-gas-receptor` | core | req. Automata Tinkerer | a | learning: specialty/augment known (checked by check_augment) |
| `automata-prosthetic-torso-poison-gas-receptor` | core | req. Poison Gas Epicenter | b | same item/body, NOT enforced: the app has no item for list prosthetic |
| `automata-prosthetic-torso-sensor-array` | core | automaton only | c | restriction on the target, NOT enforced: the app has no item for list prosthetic |
| `automata-prosthetic-torso-sensor-array` | core | req. Automata Tinkerer | a | learning: specialty/augment known (checked by check_augment) |
| `gadgetry-resonator-fast-black-trap` | aether | req. Black Trap | b | same item: gadgetry-resonator-black-trap |
| `gadgetry-resonator-focused-black-trap` | aether | req. Black Trap | b | same item: gadgetry-resonator-black-trap |
| `gadgetry-resonator-highly-irradiated` | aether | req. Irradiated | b | same item: gadgetry-resonator-irradiated |
| `gadgetry-resonator-widespread-darkness` | aether | req. Light-Absorbing | b | same item: gadgetry-resonator-light-absorbing |
| `armsmith-munition-split-shot` | armsmith-extra | (text) | c | not with armsmith-munition-syringed, armsmith-munition-inkshot, armsmith-munition-flash-bangs |
| `armsmith-turret-body-part-seeker` | armsmith-extra | req. Automated | b | same item: armsmith-turret-automated |
| `armsmith-turret-deadly-accurate` | armsmith-extra | req. Automated | b | same item: armsmith-turret-automated |
| `armsmith-turret-devastatingly-accurate` | armsmith-extra | req. Automated / req. Deadly Accurate | b | same item: armsmith-turret-automated |
| `armsmith-turret-devastatingly-accurate` | armsmith-extra | req. Automated / req. Deadly Accurate | b | same item: armsmith-turret-deadly-accurate |
| `armsmith-turret-seek-destroy-system` | armsmith-extra | req. Automated | b | same item: armsmith-turret-automated |
| `armsmith-turret-spray-shots` | armsmith-extra | req. Automated | b | same item: armsmith-turret-automated |
| `armsmith-turret-targeting-system` | armsmith-extra | req. Automated | b | same item: armsmith-turret-automated |
| `gadgetry-explosive-anti-handling-fuse` | explosives | req. Delay | b | same item: gadgetry-explosive-delay |
| `gadgetry-explosive-clinging` | explosives | req. Jumping or Roaming | b | same item: gadgetry-explosive-jumping OR gadgetry-explosive-roaming |
| `gadgetry-explosive-high-incendiary` | explosives | req. Incendiary | b | same item: gadgetry-explosive-incendiary |
| `gadgetry-explosive-lingering-fires` | explosives | req. Incendiary | b | same item: gadgetry-explosive-incendiary |
| `gadgetry-explosive-miniscule` | explosives | req. Concealable | b | same item: gadgetry-explosive-concealable |
| `gadgetry-explosive-proximity-leap` | explosives | req. Jumping / req. Proximity Fuse | b | same item: gadgetry-explosive-jumping |
| `gadgetry-explosive-proximity-leap` | explosives | req. Jumping / req. Proximity Fuse | b | same item: gadgetry-explosive-proximity-fuse |
| `gadgetry-explosive-shockwave` | explosives | req. Knock Back | b | same item: gadgetry-explosive-knockback |
| `gadgetry-explosive-super-heated-shrapnel` | explosives | req. Shrapnel | b | same item: gadgetry-explosive-shrapnel |
| `gadgetry-explosive-target-processing` | explosives | req. Fuse Box Builder | a | learning: specialty/augment known (checked by check_augment) |
| `gadgetry-explosive-vast-crater` | explosives | req. Sinking Crater | b | same item: gadgetry-explosive-sinking-crater |
| `gadgetry-firebomb-battlefield-scorcher` | explosives | req. Extended Blast | b | same item: gadgetry-firebomb-extended-blast |
| `gadgetry-firebomb-magnetic-pulsing` | explosives | req. Sparks in the Air | b | same item: gadgetry-firebomb-sparks-in-the-air |
| `alchemy-living-liquid-defensive` | living-liquids | req. Interior Platelets | b | same item: alchemy-living-liquid-interior-platelets |
| `alchemy-living-liquid-lifting-liquid` | living-liquids | req. Lighter-than-Air Liquid | b | same item: alchemy-living-liquid-lighter-than-air-liquid |
| `luck-memento-master-of-fortune` | mementos | req. Moneymaker | b | same item: luck-memento-moneymaker |
| `luck-memento-fumble` | mementos | req. Hand Slip | a | learning: specialty/augment known (checked by check_augment) |
| `luck-memento-hand-slip` | mementos | req. Feeling Lucky | a | learning: specialty/augment known (checked by check_augment) |
| `luck-memento-lost-and-stolen` | mementos | req. Lost Wallet | b | same item: luck-memento-lost-wallet |
| `alchemy-medicine-antivenom-plus` | pets-and-predators | req. Antivenom | b | same item: alchemy-medicine-antivenom |
| `bio-flux-essence-mobile-animal` | pets-and-predators | animal only | c | restriction on the target, NOT enforced: the app has no item for list essence |
| `bio-flux-essence-prehensile` | pets-and-predators | animal only | c | restriction on the target, NOT enforced: the app has no item for list essence |
| `bio-flux-essence-specialized-animal` | pets-and-predators | animal only | c | restriction on the target, NOT enforced: the app has no item for list essence |
| `bio-flux-essence-specialized-animal` | pets-and-predators | needs a known animal special trait | d | display only, see (d) list |
| `bio-flux-animal-trait-flesh-tearing` | pets-and-predators | req. Piercing Attacks | a | learning: specialty/augment known (checked by check_augment) |
| `bio-flux-animal-trait-extra-hardy` | pets-and-predators | req. Hardy | a | learning: specialty/augment known (checked by check_augment) |
| `bio-flux-animal-trait-hurl` | pets-and-predators | req. Prehensile Limbs | a | learning: specialty/augment known (checked by check_augment) |
| `bio-flux-animal-trait-tool-user` | pets-and-predators | req. Prehensile Limbs | a | learning: specialty/augment known (checked by check_augment) |
