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
```

Deployment mirrors TheLog: `bin/start.sh` (collectstatic → migrate → seed_catalog → `create_random_character --if-empty` → gunicorn) under supervisord; see README.

## Architecture

Django 6 + server-rendered templates + HTMX + Alpine (vendored in `static/js`, no build step). Three apps:

- **`rules`**: game rules. It has no DB models.
  - `data/source/Tephra_Reference_full.md` is the rules summary of the Playing Guide. Its Appendix A holds the 462 specialties as JSONL.
  - `management/commands/build_rules_data.py` parses the markdown (`mdparse.py`) and merges it with `curated.py` into the committed JSON files `data/specialties|races|stories|nationalities|augments|catalog.json`. Curated data always wins. After editing `curated.py`, run `build_rules_data` again, or the JSON (and the tests) won't see the change.
  - `registry.py` loads that JSON once (`get_registry()`). Characters reference rule entries **by slug**. Trait keys are `"<race>/<trait-slug>"`.
  - `engine/` is pure Python with no Django imports. `stats.compute(CharacterState) -> Sheet` computes every sheet value as a `modifiers.Value` (total plus labelled parts). Those parts feed the hover/tap breakdown popovers (`{% stat %}` tag → `data-bd` JSON → `static/js/app.js`); every Value with at least one part gets one, so derived values should inherit their sources (`Value.inherited`, used for weapon Accuracy/Strike) instead of copying a bare total. `weapons.py` builds the weapon blocks (firearms and crossbows use Accuracy for damage) and `hand_layout` (weapon1 = left hand, weapon2 = right hand, `wings` = extra one-handed slot for Wings as Arms; a two-handed item shows left and blocks the right, so does a shield/parrying dagger in the deflection slot; `tables.item_hands` = item `hands` (0 = worn, e.g. cloak) or the size table, with Rotating Barrels and One-Handing It applied). `requirements.py` checks specialty and augment prerequisites. Clauses marked `"soft": true` never block learning; `specialty_warnings`/`character_warnings` report them while the equipment doesn't fit (picker "Can be learned, but …" + yellow sheet banner). They come from the armor requirements in the book text and from `curated.USAGE_CONDITIONS` (weapon kind/size/material/hands/concealable, free hand, both hands empty, shield or deflection item, armor worn/material). Unchecked conditions go into `curated.USAGE_NOTES` (highlighted in the specialty details); choices made when learning (Battle Theme: singing/instrument) into `curated.SPECIALTY_OPTIONS` → `Character.specialty_choices`. "Any AP-sacrifice specialty" is a hard requirement (`curated.AP_SACRIFICE_SPECIALTIES`). `effects.py` holds the status effects and the called-shot chart (Normal/Wounded/Fatal effect per location) with their modifiers; a Normal hand hit drops the held item. `creation.py` and `leveling.py` hold the validation and random generators.
- **Modifier schema** (see the docstring in `curated.py`): `stat`, `value|formula|by_marque`, `op` (add/base/transfer/set), `when` (always/stance/toggle/note), `scope` (character/weapon/melee/unarmed/ranged).
  - Formulas are evaluated by the safe AST evaluator `engine/formula.py`. Variables are lowercased skill names (`bioflux`), `level`, `specialties`, attribute names and `*_total`.
  - Toggle keys are the source keys (`spec:<slug>`, `trait:<key>`, `story:<slug>`, `custom:<pk>`), stored in `Character.toggles`.
  - `roll:<Attribute>` modifiers (e.g. Elf Big Boned +2 Brute) go into the attribute's Misc bubble (`Sheet.attr_misc`) and its total, which requirement checks use too. With `when: note` they are conditional and only listed below the circle (`Sheet.roll_notes`).
  - Manual "Misc" values live in `Character.misc` (`acc`…, `attr:X`, `skill:X`, changed in admin mode) and show up as "Manual Misc Change" in the breakdowns.
- **`characters`**: the `Character` model stores rule choices as JSON (skills = allocated points only; racial and story skill bonuses come from modifiers), plus `InventoryItem`, `EffectEntry` (kind normal/wound/fatal/status, `key` into `engine/effects.py`, silhouette `location` 1–12; custom status text has no key), `CustomModifier`, `LevelLog` and the singleton `NarratorSettings`. `Character.to_state()` converts a character into an engine `CharacterState`.
  - `services.py` holds every rule-aware mutation: wizard steps, `revalidate`, `random_all`, `apply_levelup`, and `equip` (always use it to put items into slots: it enforces the hand rules, moves displaced items to "carried", raises `EquipError` and returns a pop-up notice, e.g. for firing position). `normalize_hands` repairs old data when a sheet opens.
  - The views live in `characters/views/`. `wizard.py` has the 10 creation steps (a `STEP_CONTEXT`/`STEP_SAVE` dispatch; per-item buttons post `action=add:<slug>`). `sheet.py` has the sheet and `play_action` (HTMX actions re-render `partials/sheet_body.html`; URL slugs use hyphens, `effect-add` → `effect_add`). The other modules are `levelup.py`, `admin_mode.py` and `general.py`.
  - `access.py`: characters are unlocked per session with the character password (hashed, throttled). Staff users (the narrator) bypass this. Admin mode is a per-session flag.
- **`catalog`**: `ItemTemplate` (shared catalog) and the abstract `ItemFields`, also used by `InventoryItem`. Empty numeric fields mean "use the size tables" in `rules/engine/tables.py`. The object creator (`forms.ItemForm` + Alpine in `item_form.html`) and the CSV/TSV/markdown bulk import (`importer.py`) live here too.

The sheet UI (`templates/characters/partials/page1.html`, `page2.html`, `static/css/sheet.css`) recreates the PDF on a fixed 952×1232 design canvas. Elements are placed with `--x/--y/--w/--h` (or `--cx/--cy/--r` for gears) in design units, scaled by `--u = 100cqw/952`. Landscape screens show both pages side by side; portrait (tablet) screens show one page per tab. Characters with Wings as Arms get a small extra page (`.page-wings`, 300 units wide, same scale via `--pw`) with the Weapon (Wings) box: level with Weapon (Left) in landscape, above page 1 in portrait. Messages tagged `popup` render as a modal. Print targets A4 (`@media print` in `sheet.css`). Everything with a hover `title`/`data-tip` also opens on click/tap (`static/js/app.js`), so the sheet works on tablets.

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
