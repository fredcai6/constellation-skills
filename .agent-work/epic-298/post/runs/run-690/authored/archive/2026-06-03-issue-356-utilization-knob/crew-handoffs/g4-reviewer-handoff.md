# Reviewer Handoff

## Gate
g4 — Sampled-backtest per-race refactor + parallelization

## What Was Implemented
`backtest_sampled_runtime`'s per-race loop body extracted into a pure `_score_one_race` (in a NEW sibling module
`sampled_backtest_scoring.py`); the function is now a thin driver: default in-process (live objects), opt-in parallel
via run_jobs when given a multi-worker plan + reconstruction paths, fail-fast ValueError when a multi-worker plan
lacks paths. `_run_sampled_backtest_phase` threads the resolved plan + manifest/db/compound paths in.

## How to Inspect the Diff
- `git status --porcelain` (expect: modified sampled_backtest.py, runner.py, test_sampled_backtest.py; NEW
  sampled_backtest_scoring.py; ignore `.agent-work/`).
- `git diff -- src/evo_predictor/sampled_backtest.py src/evo_predictor/gold_cycle/runner.py tests/unit/evo_predictor/test_sampled_backtest.py`
- Read the NEW `src/evo_predictor/sampled_backtest_scoring.py` in full.
- Compare `_score_one_race` against the ORIGINAL loop body (use `git show HEAD:src/evo_predictor/sampled_backtest.py` to see the pre-G4 loop, lines ~474-618).
Implementer result: `.agent-work/issue-356-utilization-knob/crew-handoffs/g4-implementer-result.md`.

## Task Statement
Behavior-preserving extraction + opt-in parallelization of the sampled backtest. Full handoff:
`.agent-work/issue-356-utilization-knob/crew-handoffs/g4-implementer-handoff.md`.

## SANCTIONED SCOPE EXPANSION (do not block on this)
The handoff's Allowed Scope listed only sampled_backtest.py, but the implementer created a NEW sibling module
`src/evo_predictor/sampled_backtest_scoring.py` because keeping the new code in sampled_backtest.py would push it
>1000 lines (a NEW file-size violation). The Commander CONFIRMED this expansion. VERIFY: the new module contains
ONLY code authored this gate (the extracted per-race scorer + parallel helpers), no pre-existing logic was altered
in the move, and there is no import cycle. Do NOT block on the existence of the new module.

## Close Criteria (each a review check)
- **`_score_one_race` is PURE and EQUIVALENT** to the original loop body: same actual/quali/race_start lookups,
  same oracle-state handling, same `runtime.predict`, same `_compute_entrant_restriction`, same
  `sampled_order_metrics`, same per-stage metrics, same SampledBacktestRaceResult construction. Diff it against
  `HEAD:` line-by-line.
- **All 6 skip reasons preserved EXACTLY** (missing_actual_race_classification, missing_oracle_state,
  missing_predicted_scored_entrants, ScoringContractError skip, unscorable_prediction, and any other) with the
  same diagnostics keys.
- **Ordering:** per_race and skipped partitioned in calendar (INPUT) order on BOTH the in-process and parallel
  paths (run_jobs returns input-ordered results).
- **Default unchanged:** with no `plan` (or n_workers==1), the function uses the LIVE runtime/db/normalizer
  in-process — every existing caller (tests, cmd_sampled_backtest) is unaffected.
- **Parallel contract:** n_workers>1 WITH paths → per-race jobs via run_jobs + module-level `_score_one_race_job`
  worker that rebuilds runtime (sampled_runtime_from_manifest), db (DatabaseManager(db_path)), normalizer
  (load_time_safe_compound_prior→CompoundNormalizer); n_workers>1 WITHOUT paths → clear ValueError (no silent fallback).
- **target_lap equivalence:** the parallel worker derives target_lap from the rebuilt runtime (via
  `_runtime_race_start_target_lap`) exactly as the in-process path does — confirm no divergence.
- Worker module-level + spawn-safe; `_ScoreOneRaceJob` picklable; jobs carry only paths/primitives (no DB handle, no tensors).
- No shared RNG; no module-level mutable cache of runtime/db.
- diagnostics + aggregate (`_mean_metrics`) computation unchanged.

## Allowed Scope (actual)
sampled_backtest.py, sampled_backtest_scoring.py (NEW, sanctioned), gold_cycle/runner.py
(_run_sampled_backtest_phase + run_cycle call site), tests/unit/evo_predictor/test_sampled_backtest.py.

## Specific Exclusions (flag if touched)
No training loops (G3), no scripts (G5), no report-schema/run_config change, no scoring/skip/diagnostics numeric change.

## Constraints (each a review check)
- DB-only; logging not print; module-level spawn-safe worker; input-order assembly.
- **Simplification (Commander standard):** NO NEW violation. Re-run `--paths` on all touched files incl. the new
  module → expect PASS. Confirm backtest_sampled_runtime is now under limits (was pre-existing CC=32/225). BLOCK on any new violation.

## Evidence Produced
- `py -m pytest tests/unit/evo_predictor/test_sampled_backtest.py tests/unit/evo_predictor/test_sampled_backtest_cli.py -q` → 47 passed (re-run).
- `py -m src.utils.simplification_limits --paths src/evo_predictor/sampled_backtest.py src/evo_predictor/sampled_backtest_scoring.py src/evo_predictor/gold_cycle/runner.py` → expect PASS.

## Suggested Model Tier
stronger — reason: line-by-line behavior-equivalence of a long branch-heavy loop + a reconstruct-from-paths worker;
a silent skip-semantics or ordering change corrupts gold backtest output.

## Stop Conditions
Return BLOCK if: _score_one_race diverges from the original body, a skip reason/diagnostic key changed, ordering is
not input-order, the default path changed for existing callers, a NEW simplification violation appears, or jobs carry
non-picklable data.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers (file:line + issue), out-of-scope observations.
