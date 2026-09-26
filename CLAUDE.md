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
```

Deployment mirrors TheLog: `bin/start.sh` (collectstatic → migrate → seed_catalog → gunicorn) under supervisord; see README.

## Architecture

Django 6 + server-rendered templates + HTMX + Alpine (vendored in `static/js`, no build step). Three apps:

- **`rules`**: game rules. It has no DB models.
  - `data/source/Tephra_Reference_full.md` is the rules summary of the Playing Guide. Its Appendix A holds the 462 specialties as JSONL.
  - `management/commands/build_rules_data.py` parses the markdown (`mdparse.py`) and merges it with `curated.py` into the committed JSON files `data/specialties|races|stories|nationalities|augments|catalog.json`. Curated data always wins. After editing `curated.py`, run `build_rules_data` again, or the JSON (and the tests) won't see the change.
  - `registry.py` loads that JSON once (`get_registry()`). Characters reference rule entries **by slug**. Trait keys are `"<race>/<trait-slug>"`.
  - `engine/` is pure Python with no Django imports. `stats.compute(CharacterState) -> Sheet` computes every sheet value as a `modifiers.Value` (total plus labelled parts). Those parts feed the hover/tap breakdown popovers (`{% stat %}` tag → `data-bd` JSON → `static/js/app.js`). `weapons.py` builds the weapon blocks (firearms and crossbows use Accuracy for damage). `requirements.py` checks specialty and augment prerequisites. `creation.py` and `leveling.py` hold the validation and random generators.
- **Modifier schema** (see the docstring in `curated.py`): `stat`, `value|formula|by_marque`, `op` (add/base/transfer), `when` (always/stance/toggle/note), `scope` (character/weapon/melee/unarmed/ranged).
  - Formulas are evaluated by the safe AST evaluator `engine/formula.py`. Variables are lowercased skill names (`bioflux`), `level`, `specialties`, attribute names and `*_total`.
  - Toggle keys are the source keys (`spec:<slug>`, `trait:<key>`, `story:<slug>`, `custom:<pk>`), stored in `Character.toggles`.
  - The sheet's "Misc" values live in `Character.misc` (`acc`…, `attr:X`, `skill:X`) and show up as "Misc (admin)" in the breakdowns.
- **`characters`**: the `Character` model stores rule choices as JSON (skills = allocated points only; racial and story skill bonuses come from modifiers), plus `InventoryItem`, `EffectEntry`, `CustomModifier`, `LevelLog` and the singleton `NarratorSettings`. `Character.to_state()` converts a character into an engine `CharacterState`.
  - `services.py` holds every rule-aware mutation: wizard steps, `revalidate`, `random_all`, `apply_levelup`.
  - The views live in `characters/views/`. `wizard.py` has the 10 creation steps (a `STEP_CONTEXT`/`STEP_SAVE` dispatch; per-item buttons post `action=add:<slug>`). `sheet.py` has the sheet and `play_action` (HTMX actions re-render `partials/sheet_body.html`). The other modules are `levelup.py`, `admin_mode.py` and `general.py`.
  - `access.py`: characters are unlocked per session with the character password (hashed, throttled). Staff users (the narrator) bypass this. Admin mode is a per-session flag.
- **`catalog`**: `ItemTemplate` (shared catalog) and the abstract `ItemFields`, also used by `InventoryItem`. Empty numeric fields mean "use the size tables" in `rules/engine/tables.py`. The object creator (`forms.ItemForm` + Alpine in `item_form.html`) and the CSV/TSV/markdown bulk import (`importer.py`) live here too.

The sheet UI (`templates/characters/partials/page1.html`, `page2.html`, `static/css/sheet.css`) recreates the PDF on a fixed 952×1232 design canvas. Elements are placed with `--x/--y/--w/--h` (or `--cx/--cy/--r` for gears) in design units, scaled by `--u = 100cqw/952`. Landscape screens show both pages side by side; portrait (tablet) screens show one page per tab.
