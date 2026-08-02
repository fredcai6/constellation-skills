# Implementer Handoff

## Gate
`gfix` — Fix the `feature_schema_version` override regression that breaks the sampled-runtime backtest

## Task
Fix a pre-existing #369 regression so the sampled-runtime backtest stops crashing on freshly-trained bundles. This is on the **promoted runtime path** → test-led.

**Root cause (verified):** `src/evo_predictor/sampled_runtime.py` `_run_stage` (≈ lines 446-449) reads each loaded module's per-bundle manifest `feature_schema_version` and, when present, injects it into `stage_overrides`, which then flow into the module's adapter `Config` constructor via `build_pair_batch_for_module`. The quali recent-history adapter consumes it (translates v1/v2 → `form_encoding`), but the other recent-history configs do **not** declare a `feature_schema_version` field. `RaceStartRecentHistoryConfig` (`race_start_recent_history_adapter.py:70`) is a frozen dataclass with no such field → `TypeError: ...__init__() got an unexpected keyword argument 'feature_schema_version'`, which aborts the **entire** sampled-runtime backtest (both `sampled_state` and `oracle_all_states`). Every fresh bundle stamps `feature_schema_version`, so this breaks all new runs (the current promoted 260603 manifest predates the stamping, so production is unaffected).

**Required fix (root-cause, not a band-aid):** `feature_schema_version` must keep driving (1) the runtime consistency CHECK (`module_runtime._check_feature_schema_consistency`) and (2) the quali recent-history v1/v2 encoding selection — but it must **not** be passed as a generic kwarg into adapter `Config` constructors that don't declare it. Fix at the injection/closure boundary so it's handled once for all modules. Do NOT just add a dead `feature_schema_version` field to `RaceStartRecentHistoryConfig` — confirm the full set of affected recent-history module families (race, race_start, constructor variants) and fix them all with one principled change.

## Protected Intent
The fused-output sampled backtest must run to completion for all 12 production modules (it's the source of the A/B decision metric for this regen). The #369 runtime consistency guarantee and the quali v1/v2 encoding selection must be preserved exactly — no behavior change to the quali encoding paths.

## Test Mode
TDD required (promoted runtime path, logic change). Write a failing regression test first, then fix.

## Close Criteria
- A regression test exercises the `_run_stage` / sampled-backtest path with a `race_start_recent_history` (and ideally another non-quali recent-history) module bundle carrying `feature_schema_version`; it FAILS before the fix (repro) and PASSES after.
- The full evo unit region is green: `py -m pytest tests/unit/evo_predictor -q`.
- The #369 consistency check and quali v1/v2 selection still work (existing tests stay green; call out which ones cover them).
- The smoke Arm A sampled-backtest now completes with NO `TypeError` (re-run it and capture proof).
- `py -m src.utils.simplification_limits` clean on touched paths.

## Allowed Scope
- `src/evo_predictor/sampled_runtime.py`, `src/evo_predictor/module_adapters/` (closure/config-resolution), `src/evo_predictor/module_runtime.py`, and the affected adapter/config files — whatever the principled fix needs.
- New/updated tests under `tests/unit/evo_predictor/`.
- Re-running the smoke Arm A sampled-backtest (manifest at `outputs/evo_runs/smoke_armA_335/sampled_runtime_manifest.json`) for proof.

## Specific Exclusions
- Do NOT change the quali encoding semantics or the anchor logic.
- Do NOT touch `params/gold/`, the promoted manifest, `configs/evo/gold_defaults.toml`, or the Arm B config.
- Do NOT retrain any module (the bug is at backtest-time config construction; bundles/manifests are fine).

## Constraints
- One canonical path — prefer the single injection-site fix over per-config band-aids.
- Promoted runtime path: focused region green, no implementation-only logic commit.
- DB is the only data source; missingness explicit.

## Required Evidence
- The failing-then-passing regression test (name it, show before/after).
- `py -m pytest tests/unit/evo_predictor -q` output (green).
- simplification_limits output on touched paths.
- Proof the smoke Arm A sampled-backtest completes (the log lines that previously showed the TypeError now show success / scored races).
- A one-paragraph note on which recent-history module families were affected and how the fix covers them all.

## Verification Commands
```bash
py -m pytest tests/unit/evo_predictor -q
py -m src.utils.simplification_limits <touched paths>
# Re-prove the backtest end to end on the existing smoke Arm A manifest:
py -m src.evo_predictor.run sampled-backtest --manifest outputs/evo_runs/smoke_armA_335/sampled_runtime_manifest.json --year 2025 --max-races 1   # adjust flags to the real CLI; goal: completes w/o TypeError
```

## Suggested Model Tier
sonnet — contained bug with a clear root cause; the judgment is choosing the single clean fix location and covering all affected modules.

## Authority
The decision to fix this in-run was made by the user. You own the fix design. You may NOT expand scope to unrelated refactors, change quali/anchor semantics, or touch promoted artifacts. If the clean fix turns out to require a cross-module/boundary change beyond `evo_predictor`, STOP and report.

## Stop Conditions
Stop and return if: the fix needs to cross a region boundary or touch `latent_power`; the regression cannot be reproduced in a test; the quali consistency/encoding tests would have to change to make it pass; or scope beyond the listed files is required.

## Return Format
Return IMPLEMENTER_RESULT: root cause, the fix (file + approach), the regression test (failing→passing proof), affected-module-family note, evo region test output, simplification_limits output, smoke sampled-backtest proof, assumptions, stop conditions hit, out-of-scope observations. Do NOT commit — leave changes in the working tree for the commander to commit at integrate.
