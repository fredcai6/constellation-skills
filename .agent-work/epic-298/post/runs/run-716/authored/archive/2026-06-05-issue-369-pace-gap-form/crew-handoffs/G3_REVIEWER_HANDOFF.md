# Reviewer Handoff

## Gate
g3 — end-to-end plumbing (issue #369, work area `.agent-work/issue-369-pace-gap-form/`)

## What Was Implemented
`form_encoding` wired end to end (training, runtime, CLI, gold config, docs), mirroring the pace_normalization pattern:
- `module_adapters/_common.py`: `_build_recent_history_race_features` takes `recent_history_form_encoding`; pace-gap fetch/lookup extracted into `_fetch_pace_gap_map` / `_driver_pace_gap_list` helpers (no-op/None when off or task≠quali).
- `module_adapters/_training_builders.py`: all 12 training closures accept the kwarg; ONLY the two quali RH closures use it (forward to builder + construct `RecentHistoryFeatureConfig(form_encoding=...)`); others accept-and-ignore.
- `module_training_orchestration.py`: `prepare_module_training_data` / `build_labeled_batches_for_module` carry + forward the kwarg.
- `data_adapter/_build.py`: three builders accept the kwarg; `_inject_quali_pace_gap_history(features, db, year, round_num, encoding)` no-ops unless `quali_pace_gap`.
- `run.py`: `--recent-history-form-encoding` on `train-latent-power-module` + `backtest-latent-power-module`.
- `gold_cycle/config.py`: `VALID_FORM_ENCODINGS`, `GoldCycleDataConfig.recent_history_form_encoding`, validation, `_config_to_raw`/`_apply_overrides_to_raw`; `runner_support._module_train_args` forwards; knob added to `configs/evo/gold_defaults.toml` AND `configs/evo/smoke_defaults.toml`.
- **Runtime consistency seam**: `sampled_runtime.py::_run_stage` merges each bundle manifest's `feature_schema_version` into `config_overrides`; the two quali RH runtime closures (`_runtime_builders.py`) derive encoding via `_form_encoding_from_schema_version` (`.v2` suffix → pace_gap) and lazily inject gap history via `_inject_pace_gap_history_runtime` (skips if pre-populated); `module_runtime.py::run_module_field` calls `_check_feature_schema_consistency` — RuntimeError naming module + expected/actual on mismatch; manifests WITHOUT the key skip the check (old-bundle compatibility).
- Docs: both `docs/evo/modules/recent_history_{driver,constructor}.md` updated.
- Tests: new cases in `test_module_adapters.py`, `test_module_training_orchestration.py`, `test_data_adapter/test_build_all_race_features.py`, `test_run_cli_defaults.py`, `test_gold_cycle_config.py`, `test_module_runtime.py`.

## How to Inspect the Diff
Uncommitted working tree on branch `constellation/issue-369-pace-gap-form` (HEAD 0148958 = G2):
```bash
git -C C:\Programs\f1Brainz status
git -C C:\Programs\f1Brainz diff
```
Pattern reference the wiring must mirror: `git diff main...origin/claude/compound-regime-feasibility -- src/evo_predictor/module_training_orchestration.py src/evo_predictor/run.py src/evo_predictor/data_adapter/_build.py src/evo_predictor/gold_cycle/runner_support.py configs/evo/gold_defaults.toml`

## Task Statement
Full implementer handoff: `.agent-work/issue-369-pace-gap-form/crew-handoffs/G3_IMPLEMENTER_HANDOFF.md` (8 sub-items a–h; the (f) seam was the implementer's documented design decision within stated bounds).

## Close Criteria
**Primary — default-path inertness:**
- Flag off ⇒ ZERO extra DB reads on every path (training builder, data_adapter builders, runtime closures): trace each call site in the diff and confirm the provider/`lap_times` access is unreachable when encoding is `position_quality`/key absent.
- No behavior change for any of the 12 modules when off: closure-contract change is accept-and-ignore default kwargs only; region suite green (1258) is the executable proof — re-run it.

**Runtime/training consistency mechanism (review hard):**
- A v2 bundle gets pace-gap features; v1 bundle position-quality — trace the path: manifest `feature_schema_version` → `config_overrides` → `_form_encoding_from_schema_version` → adapter config; verify the produced batch schema then hits `_check_feature_schema_consistency` and a mismatch RAISES naming module + both schemas. Verify there is genuinely NO silent-fallback branch (e.g. catch-and-default, or injection failure silently producing v1).
- Old-bundle compatibility: manifest without the key → no check, no injection, default config — confirm this cannot mask a real v2 mismatch (a v2-trained bundle would have the key; reason about whether any path writes bundles lacking it while training v2 — check what `train-latent-power-module` records into the bundle manifest).
- `.v2`-suffix → encoding inference: assess robustness (it keys off the shared schema constants; is any other module's schema ending `.v2` reachable through these two closures? They are module-specific closures, so scope is bounded — confirm).
- Lazy runtime injection `_inject_pace_gap_history_runtime`: confirm "skips if pre-populated" can't half-populate (mixed None/non-None across drivers) and that injected data honors the as-of contract (prior rounds only) by delegating to the G1 provider.

**Config/CLI:**
- `gold_cycle/config.py` validation rejects invalid values loudly; round-trips through `_config_to_raw`/`_apply_overrides_to_raw`; `_module_train_args` forwards; toml defaults are `position_quality` in BOTH defaults files.
- `run.py` flag: choices constrained, default right, forwarded into both command paths.

**Docs accuracy:** both module docs match the code as implemented (schema strings, names, missingness, consistency story, default unchanged).

**Tests:** new tests pin builder populate/omit, closure encoding selection, runtime mismatch raise, config validation, CLI flow — check they assert behavior, not implementation trivia.

**Limits:** commander has already baseline-verified: current violations are all pre-existing except `_common.py` cc=22 (at its baseline) and +3 irreducible threading lines in `build_labeled_batches_for_module` (cc unchanged 36). Re-run limits if you wish; do NOT block on these known pre-existing items (tracked as triage tc3). Any OTHER new violation → BLOCK.

## Allowed Scope
The files listed in "What Was Implemented" + the named test files. Frozen (BLOCK if diffed): `quali_pace_gap_history.py`, `quali_recent_history_adapter.py`, `constructor_quali_recent_history_adapter.py`, `recent_history_adapter.py`, DB layer, `src/latent_power/`, `params/gold/`, committed `reports/`.

## Constraints the Implementation Must Respect
- Mirror the pace_normalization pattern (no parallel mechanism invented) — compare against the pattern diff.
- All defaults `position_quality`; no default flip anywhere (check toml, dataclass defaults, CLI default, closure fallbacks).
- As-of contract preserved; no "latest" fallback added.
- `py` not `python`; pyright-clean on changed files.

## Evidence Produced
From IMPLEMENTER_RESULT (+ rework): TDD red→green observed per sub-item; full region `py -m pytest tests/unit/evo_predictor -q` → 1258 passed; targeted suites green (85 passed); limits at baseline (9 pre-existing violations, commander-verified vs clean HEAD worktree). Re-run the region suite and any targeted command yourself; do not take the transcript on faith.

## Suggested Model Tier
stronger-leaning bounded — the consistency seam and inertness proof are the crux; wiring breadth is mechanical.

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed, evidence is absent or unverifiable, or a policy decision is required before a verdict is possible.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations.
