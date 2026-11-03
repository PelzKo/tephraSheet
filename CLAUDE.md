# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands run from `tephra/` (the Django project root) with the repo-level venv:

```bash
../.venv/bin/python manage.py runserver          # dev server (needs tephra/.env with LOCAL=True, DEBUG=True)
../.venv/bin/pytest                              # all tests (settings: tephra.settings_test)
../.venv/bin/pytest tests/test_engine.py::test_stance_and_toggle   # single test
../.venv/bin/python manage.py build_rules_data   # regenerate rules/data/*.json from the reference markdown
../.venv/bin/python manage.py seed_catalog       # load book items into the catalog DB (idempotent)
../.venv/bin/python manage.py create_random_character [--level N] [--if-empty]   # finished random character, password "demo"
../.venv/bin/python manage.py i18n_check [--lang de]   # UI texts ({% t %}, _()) without a translation
```

Deployment mirrors TheLog: `bin/start.sh` (collectstatic → migrate → seed_catalog → `create_random_character --if-empty` → gunicorn) under supervisord; see README.

## Architecture

Django 6 + server-rendered templates + HTMX + Alpine (vendored in `static/js`, no build step). Four apps (rules, characters, catalog, wiki).

**Languages** (no gettext tooling): `rules/lang.py` holds the current language (a contextvar set by `characters.middleware.LanguageMiddleware` from session/cookie `tephra_lang` or Accept-Language; switcher in `base.html` posts to `set_language`). UI texts are keyed by their English wording: templates use the builtin `{% t "Text {n}" n=x %}` and `{{ value|t }}` (for English values from Python such as choice labels and skill names), Python uses `from rules.lang import gettext as _` with `{placeholders}` (never f-strings, never at import time). Translations: `locale/<code>/*.json` (merged; `_meta.json` = language name). Rule content is translated per language in `rules/data/i18n/<code>/<kind>*.json` ({slug: {field: text}}, glossary `rules/data/i18n/GLOSSARY_de.md`); `get_registry()` returns the registry of the current language, every entry keeps `name_en` and rules logic that matches by name must use `name_en` (or `specialties_by_name`, which is keyed by English name). `effects.get()`/`location_label()` localize the effect texts. Augment `req. X` qualifiers are checked on `qualifiers_en`. A new language = both folders, nothing else.

**Extensions** (plan and decisions: `Downloads/TephraExtra/00_Overview.md`): rule entries with `"extension": "<key>"` (+ `also_in`) belong to an extension, no key = core. `rules/extensions.py` holds `EXTENSIONS` (key → name) and a contextvar set per request from `NarratorSettings.enabled_extensions`/`disabled_races` (in `LanguageMiddleware`; commands call `set_offer` themselves). Every place that *offers* choices (wizard, level-up, planner, admin mode, random generators, catalog augment pickers, wiki search) filters with `offer(entries, keep=<owned slugs>)`/`offer_races`; lookups by slug never filter, so existing characters keep everything.

- **`rules`**: game rules. It has no DB models.
  - `data/source/Tephra_Reference_full.md` is the rules summary of the Playing Guide. Its Appendix A holds the 462 specialties as JSONL.
  - `management/commands/build_rules_data.py` parses the markdown (`mdparse.py`) and merges it with `curated.py` into the committed JSON files `data/specialties|races|stories|nationalities|augments|catalog.json`. Curated data always wins. After editing `curated.py`, run `build_rules_data` again, or the JSON (and the tests) won't see the change.
  - `registry.py` loads that JSON once (`get_registry()`). Characters reference rule entries **by slug**. Trait keys are `"<race>/<trait-slug>"`.
  - `engine/` is pure Python with no Django imports. `stats.compute(CharacterState) -> Sheet` computes every sheet value as a `modifiers.Value` (total plus labelled parts). Those parts feed the hover/tap breakdown popovers (`{% stat %}` tag → `data-bd` JSON → `static/js/app.js`); every Value with at least one part gets one, so derived values should inherit their sources (`Value.inherited`, used for weapon Accuracy/Strike) instead of copying a bare total. `weapons.py` builds the weapon blocks (firearms and crossbows use Accuracy for damage) and `hand_layout` (weapon1 = left hand, weapon2 = right hand, `wings` = extra one-handed slot for Wings as Arms; a two-handed item shows left and blocks the right, so does a shield/parrying dagger in the deflection slot; `tables.item_hands` = item `hands` (0 = worn, e.g. cloak) or the size table, with Rotating Barrels and One-Handing It applied). `requirements.py` checks specialty and augment prerequisites. Clauses marked `"soft": true` never block learning; `specialty_warnings`/`character_warnings` report them while the equipment doesn't fit (picker "Can be learned, but …" + yellow sheet banner). They come from the armor requirements in the book text and from `curated.USAGE_CONDITIONS` (weapon kind/size/material/hands/concealable, free hand, both hands empty, shield or deflection item, armor worn/material). Unchecked conditions go into `curated.USAGE_NOTES` (highlighted in the specialty details); choices made when learning (Battle Theme: singing/instrument) into `curated.SPECIALTY_OPTIONS` → `Character.specialty_choices`. "Any AP-sacrifice specialty" is a hard requirement (`curated.AP_SACRIFICE_SPECIALTIES`). `effects.py` holds the status effects and the called-shot chart (Normal/Wounded/Fatal effect per location) with their modifiers; a Normal hand hit drops the held item. `creation.py` and `leveling.py` hold the validation and random generators.
- **Modifier schema** (see the docstring in `curated.py`): `stat`, `value|formula|by_marque`, `op` (add/base/transfer/set), `when` (always/stance/toggle/note), `scope` (character/weapon/melee/unarmed/ranged). `toggle_key` makes a toggle modifier follow another source's toggle (Victory Theme → `spec:showmanship-battle-theme`, no own button). Specialties/traits with an `ongoing` cost dict (`curated.ONGOING`/`ONGOING_TRAITS`: `start`/`upkeep`/`stop` AP, `requires_stance`/`requires_toggle`, `body_race`) are not stances: toggles under "Other" (`Sheet.ongoing`, with `available`). Only `Stance …` costs are stances (1 AP to enter, `views/sheet.STANCE_AP`); one at a time. In fight mode `pay_ap` takes start/stop costs from the round's AP (refuses if too few; outside fight mode only an info bar), "My turn" pays upkeep or asks which to keep (`fight.upkeep_choice` dialog), `end_unavailable` switches off what lost its precondition. Growth Intensity (gnome) makes `stats.body_race` the elf (fixed traits, speeds, unarmed DC).
  - Formulas are evaluated by the safe AST evaluator `engine/formula.py`. Variables are lowercased skill names (`bioflux`), `level`, `specialties`, attribute names and `*_total`.
  - Toggle keys are the source keys (`spec:<slug>`, `trait:<key>`, `story:<slug>`, `custom:<pk>`), stored in `Character.toggles`.
  - `roll:<Attribute>` modifiers (e.g. Elf Big Boned +2 Brute) go into the attribute's Misc bubble (`Sheet.attr_misc`) and its total, which requirement checks use too. With `when: note` they are conditional and only listed below the circle (`Sheet.roll_notes`).
  - Manual "Misc" values live in `Character.misc` (`acc`…, `attr:X`, `skill:X`, changed in admin mode) and show up as "Manual Misc Change" in the breakdowns.
- **`characters`**: the `Character` model stores rule choices as JSON (skills = allocated points only; racial and story skill bonuses come from modifiers), plus `InventoryItem`, `EffectEntry` (kind normal/wound/fatal/status, `key` into `engine/effects.py`, silhouette `location` 1–12; custom status text has no key), `CustomModifier`, `LevelLog` and the singleton `NarratorSettings`. `Character.to_state()` converts a character into an engine `CharacterState`. **Wounds count up**: `Character.wounds_taken` (0 = unhurt, at max wounds every hit is fatal). `Character.fight` is the fight-mode state (`{active, ap, my_turn, round}`, `sheet.fight_action`), `story_notes` the journal (`characters/journal.py`: `#` headings start collapsible blocks, rendered in the Story tab), `plan` the level-up planner (`views/planner.py`: one entry per future level with skills/specialty/augments/note; preview via `planned_state`, preselected on the level-up page).
  - `services.py` holds every rule-aware mutation: wizard steps, `revalidate`, `random_all`, `apply_levelup`, and `equip` (always use it to put items into slots: it enforces the hand rules, moves displaced items to "carried", raises `EquipError` and returns a pop-up notice, e.g. for firing position). `normalize_hands` repairs old data when a sheet opens.
  - The views live in `characters/views/`. `wizard.py` has the 10 creation steps (a `STEP_CONTEXT`/`STEP_SAVE` dispatch; per-item buttons post `action=add:<slug>`). `sheet.py` has the sheet and `play_action` (HTMX actions re-render `partials/sheet_body.html`; URL slugs use hyphens, `effect-add` → `effect_add`). The other modules are `levelup.py`, `admin_mode.py` and `general.py`.
  - `views/feedback.py` + `Feedback` model: the speech bubble in `base.html` (every page) posts bug/feature/feedback messages with page, character and browser details in `meta` (session-throttled). The narrator reviews them (status, delete) in the Feedback section of `/gm/`.
  - `access.py`: characters are unlocked per session with the character password (hashed, throttled). Staff users (the narrator) bypass this. Admin mode is a per-session flag.
- **`catalog`**: `ItemTemplate` (shared catalog) and the abstract `ItemFields`, also used by `InventoryItem`. Empty numeric fields mean "use the size tables" in `rules/engine/tables.py`. The object creator (`forms.ItemForm` + Alpine in `item_form.html`), the CSV/TSV/markdown bulk import (`importer.py`) and the augment reference page (`/catalog/augments/`) live here too. `build_rules_data.expand_marques` turns the book's shorthand mQ II–IV values ("+4") into full text ("+4 Stk"), and `fix_smallcaps` repairs the book's small-caps OCR ("reQuires:" → "Requires:"). Every item made in the object creator is also saved to the catalog (unless name+kind exists). Kind `general` = found/looted things (quick-add form in the inventory). Weapons have optional `acc_bonus`/`stk_bonus`. Armor penalties are stored positive and shown/applied negative. Money: 1 king = 10 princes = 100 dukes (`tables.format_money`).
- **`wiki`**: `WikiPage` (anyone can edit; `WikiRevision` keeps the previous version, restore in the Django admin), app help pages from `docs/<lang>/NN-name.md`, the rules reference (chapters 1–5 of the reference markdown; German in `rules/data/source/reference_rules_de.md`) and search across pages, help, rules, specialties, augments and traits (`wiki/views.search`). User markdown goes through `wiki.content.render` (HTML escaped, unsafe links removed).

The sheet UI (`templates/characters/partials/page1.html`, `page2.html`, `static/css/sheet.css`) recreates the PDF on a fixed 952×1232 design canvas. Elements are placed with `--x/--y/--w/--h` (or `--cx/--cy/--r` for gears) in design units, scaled by `--u = 100cqw/952`. Landscape screens show both pages side by side; portrait (tablet) screens show one page per tab. Characters with Wings as Arms get a small extra page (`.page-wings`, 300 units wide, same scale via `--pw`) with the Weapon (Wings) box: level with Weapon (Left) in landscape, above page 1 in portrait. Messages tagged `popup` render as a modal. Every `table.data` is click-to-sort (`static/js/app.js`): a cell's `data-sort` overrides its text (`size_rank` filter, price in dukes), `data-nosort` on a `th`/`tr` opts out, empty values sort last. The inventory list has a client-side toolbar (search, kind filter, sort) that works on the rows' `data-*` attributes and remembers its state per character in localStorage. Specialty effects ending in four tier results are shown with numbered tier gears (`rules/engine/text.split_tiers`, `effect_html` filter). Print targets A4 (`@media print` in `sheet.css`). Everything with a hover `title`/`data-tip` also opens on click/tap (`static/js/app.js`), so the sheet works on tablets.

<!-- code-review-graph MCP tools -->
## MCP Tools: code-review-graph

**This project has a knowledge graph. Start with the code-review-graph
MCP tools to narrow scope, then read the source.** The graph is cheaper than scanning files and
gives you structural context (callers, dependents, test coverage) that file search cannot.

### When to use graph tools FIRST

- **Exploring code**: `semantic_search_nodes_tool` or `query_graph_tool` instead of Grep
- **Understanding impact**: `get_impact_radius_tool` instead of manually tracing imports
- **Code review**: `detect_changes_tool` + `get_review_context_tool` instead of reading entire files
- **Finding relationships**: `query_graph_tool` with callers_of/callees_of/imports_of/tests_for
- **Architecture questions**: `get_architecture_overview_tool` + `list_communities_tool`

### Verify in the source

- Narrow scope with the graph, then read the source. Do not change code from graph output alone.
- For any non-trivial change, read the implementation and the relevant tests before concluding.
- Verify the exact source when touching behavior, database logic, migrations, retries, fallbacks,
  recovery, or compatibility code.
- When the graph and the source disagree, the source wins. The graph may be stale or may not
  model that relationship.
- An empty graph result can mean "not indexed" or "not statically visible", not "does not exist".

### Key Tools

| Tool | Use when |
| ------ | ---------- |
| `detect_changes_tool` | Reviewing code changes — gives risk-scored analysis |
| `get_review_context_tool` | Need source snippets for review — token-efficient |
| `get_impact_radius_tool` | Understanding blast radius of a change |
| `get_affected_flows_tool` | Finding which execution paths are impacted |
| `query_graph_tool` | Tracing callers, callees, imports, tests, dependencies |
| `semantic_search_nodes_tool` | Finding functions/classes by name or keyword |
| `get_architecture_overview_tool` | Understanding high-level codebase structure |
| `refactor_tool` | Planning renames, finding dead code |

### Workflow

1. The graph auto-updates on file changes (via hooks).
2. Use `detect_changes_tool` for code review.
3. Use `get_affected_flows_tool` to understand impact.
4. Use `query_graph_tool` pattern="tests_for" to check coverage.
<!-- /code-review-graph MCP tools -->
