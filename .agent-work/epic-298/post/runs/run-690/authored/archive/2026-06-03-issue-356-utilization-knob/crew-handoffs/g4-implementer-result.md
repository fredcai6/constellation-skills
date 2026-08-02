# IMPLEMENTER_RESULT — g4 (sampled-backtest per-race refactor + parallelize)

Status: complete. Behavior-preserving. Commander CONFIRMED the sibling-module scope expansion (see below).

## Files changed
- `src/evo_predictor/sampled_backtest.py` — driver refactor; optional params plan/manifest_path/db_path/
  compound_prior_root; default in-process / opt-in parallel / fail-fast ValueError when multi-worker plan lacks paths;
  _RaceOutcome + _assemble_backtest_result; lazy-imports the two _score_races_* drivers.
- `src/evo_predictor/sampled_backtest_scoring.py` (NEW sibling module) — pure `_score_one_race` + sub-helpers
  (_predict_with_oracle_state, _per_stage_metrics, _restrict_and_score); `_ScoreOneRaceJob`; module-level
  `_score_one_race_job` worker (rebuilds runtime/db/normalizer from paths); _score_races_sequential/_parallel;
  on_complete helper.
- `src/evo_predictor/gold_cycle/runner.py` — `_run_sampled_backtest_phase` gains plan; resolves backtest db_path
  once; passes plan + manifest_path + db_path + compound_prior_root into backtest_sampled_runtime; run_cycle passes plan.
- `tests/unit/evo_predictor/test_sampled_backtest.py` — characterization (incl. previously-uncovered
  unscorable_prediction skip), calendar-order partition guard, fail-fast contract, single-worker==default
  equivalence, parallel-vs-sequential partition equivalence (n_workers=1 + patched worker, no real pool).

## COMMANDER-CONFIRMED scope expansion
- New sibling module `sampled_backtest_scoring.py` was required: keeping all new code in sampled_backtest.py would
  push it >1000 lines = a NEW file-size violation. The split relocates ONLY code authored this gate (no pre-existing
  logic, no excluded areas), breaks the import cycle via lazy import, and leaves both files passing simplification.
  CONFIRMED correct — honors the no-new-violation standard and isolation; reviewer to verify only G4 code moved.

## Test mode: TDD/characterization satisfied
- Baseline GREEN before refactor (42 passed) -> after (47 passed). fail-fast test RED until implemented, then green.

## Evidence
- `py -m pytest tests/unit/evo_predictor/test_sampled_backtest.py tests/unit/evo_predictor/test_sampled_backtest_cli.py -q` -> 47 passed.
- Broader: test_gold_cycle_runner.py 21 passed; full tests/unit/evo_predictor/ 1171 passed.
- `--paths sampled_backtest.py runner.py` -> PASS (2 files). With new module + tests -> PASS (5 files).
- Simplification: backtest_sampled_runtime was PRE-EXISTING over-limit (CC=32, 225 lines); extraction brought it
  UNDER. NO NEW violations.
- Picklable _ScoreOneRaceJob; module-level worker (spawn-safe); no import cycle.

## Behavior preservation (for reviewer)
- Scoring numerics, all 6 skip reasons + diagnostics keys, aggregate: byte-identical; only iteration changed.
- per_race/skipped partitioned in calendar (input) order on BOTH paths (run_jobs returns input order).
- target_lap omitted from job by design — derived from rebuilt runtime via _runtime_race_start_target_lap,
  identical to in-process. Reviewer: confirm equivalence.
- Worker rebuilds normalizer and fails fast if load_time_safe_compound_prior doesn't return a CompoundPriorArtifact
  (mirrors in-process guard; phase only enters parallel with a real compound_prior_root).

## Out-of-scope observations
- A worker-local cache of rebuilt runtime/db (perf) was intentionally NOT built (would be module-level mutable state);
  noted as a possible future perf follow-up.
