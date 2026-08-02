# Reviewer Handoff

## Gate
`gfix` — Fix `feature_schema_version` override breaking the sampled-runtime backtest

## What Was Implemented
In `src/evo_predictor/module_adapters/_common.py`, `_config_with_overrides()` now pops `feature_schema_version` from the overrides dict before `dataclasses.replace(default_config, **override_dict)` (and short-circuits to `default_config` if the dict is then empty). This is the single chokepoint all non-quali adapter closures route through; the quali recent-history closures consume `feature_schema_version` directly from `config_overrides` earlier, so they're unaffected. New regression test file added.

## How to Inspect the Diff
```bash
cd C:/Programs/f1Brainz
git diff -- src/evo_predictor/module_adapters/_common.py
git status --porcelain   # new: tests/unit/evo_predictor/test_feature_schema_version_override_regression.py
```
Working tree uncommitted (commander commits at integrate).

## Task Statement
Root-cause fix for the #369 regression: `feature_schema_version` must keep driving the runtime consistency check (`module_runtime._check_feature_schema_consistency`) and the quali v1/v2 encoding selection, but must NOT be passed into adapter `Config` constructors that don't declare it. One principled fix covering all affected recent-history/race-weekend module families. Promoted runtime path → TDD.

## Close Criteria
- Fix is at the single chokepoint (`_config_with_overrides`), not a per-config band-aid; verify it covers ALL non-quali modules that route through it (race, race_start, constructor variants).
- Regression test genuinely reproduces the pre-fix `TypeError` (confirm it FAILS on the pre-fix code — e.g. `git stash` the src change, run the test, see red, restore) and PASSES after.
- Quali v1/v2 selection + consistency check NOT regressed: `test_module_runtime.py::test_run_module_field_raises_on_schema_version_mismatch`, `::test_run_module_field_no_check_when_manifest_has_no_schema_version`, `::test_driver_quali_recent_history_v1_schema_via_config_overrides`, `::test_driver_quali_recent_history_v2_schema_via_config_overrides` pass.
- Full evo unit region green: `py -m pytest tests/unit/evo_predictor -q`.
- `py -m src.utils.simplification_limits` clean on touched paths.
- Smoke Arm A sampled-backtest completes with no `TypeError` (independently re-run it).

## Allowed Scope
`src/evo_predictor/module_adapters/_common.py` + `tests/unit/evo_predictor/`. No promoted artifacts, no config, no quali/anchor semantics, no retraining.

## Specific Exclusions
Flag if the diff touches quali/anchor logic, `params/gold/`, configs, or anything beyond `_common.py` + tests.

## Constraints the Implementation Must Respect
- One canonical path (single chokepoint fix).
- No silent behavior change to the quali encoding paths or the consistency check.
- Promoted runtime path: focused region green, no implementation-only logic commit.

## Evidence Produced
- Fix: ~6-line addition in `_config_with_overrides`.
- Regression test: 11 tests, 9 failed before fix / all pass after.
- `py -m pytest tests/unit/evo_predictor -q` → 1615 passed, 19 skipped, 0 failures.
- Named quali consistency/encoding tests pass.
- `simplification_limits` → PASS (2 files).
- Smoke Arm A sampled-backtest: 2024 (2 races) + 2023 (1 race) complete, 0 skipped, no TypeError.

## Suggested Model Tier
sonnet — bounded verification of a contained fix; the judgment is confirming the chokepoint truly covers all affected modules and the quali path is genuinely untouched.

## Stop Conditions
BLOCK if: the fix is a narrow band-aid leaving sibling configs broken, the regression test doesn't actually fail pre-fix, any quali/consistency test regresses, the evo region isn't green, or the diff exceeds the allowed scope.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE/BLOCK), per-criterion findings with the exact commands you re-ran (including your independent pre-fix red check), confirmation the quali path is untouched, blockers, out-of-scope observations.
