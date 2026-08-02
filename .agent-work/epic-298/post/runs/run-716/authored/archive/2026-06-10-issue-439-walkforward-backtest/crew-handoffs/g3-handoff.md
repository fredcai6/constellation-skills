# Implementer Handoff

## Gate
`g3` — Walk-forward orchestrator + gold-cycle runner cutoff wiring + leakage attestation

## Task
Two phases. Deliver Phase 1 first (it unblocks Phase 2). NO heavy training in this gate — tests mock the
multi-hour calls; the real heavy run is a later gate (G4).

### Phase 1 — Wire the as-of cutoff through the gold-cycle runner (the missing primitive→pipeline link)
G2 added the cutoff params to `prepare_module_training_data` and the gold-cycle config schema, but the
RUNNER does not pass them. Today `build_main_train_backtest_jobs` → `_module_train_args`
(`src/evo_predictor/gold_cycle/runner.py:111-156`) threads `max_rounds_per_year` but NOT
`config.data.eval_year_train_through_round` / `eval_round_range`. Wire them so a single
`gold-cycle --config <cutoff>.toml` run actually:
  - trains with eval_year rounds `<= N` included in the train pool (thread cutoff → `_module_train_args`
    → `train_module` → `prepare_module_training_data`),
  - runs its eval/backtest over `eval_round_range` only (thread into the backtest template / sampled phase),
  - uses the eval-year compound prior in as-of-N mode when the cutoff is set: point at the per-period
    as-of-N prior root and load via `allow_same_season_research=True` (the config's
    `runtime.allow_same_season_compound_prior`, already wired at runner_support.py:173). Do NOT loosen the
    gold-mode guard.
Phase-1 test: prove on REAL code (mock only the actual NN training/solve) that a cutoff config causes the
training-data prep to receive `eval_year_train_through_round=N` / `eval_round_range=(lo,hi)` and the eval
phase to target the range. (A spy/mock on `prepare_module_training_data` asserting the forwarded kwargs is
sufficient — no full cycle.)

### Phase 2 — Walk-forward orchestrator
Create `src/evo_predictor/walkforward/` encoding the 4 periods and the per-period pipeline. Periods (2025,
24 rounds): P0 train 2018-2024 → predict R1-6; P1 +R1-6 → R7-12; P2 +R1-12 → R13-18; P3 +R1-18 → R19-24.
- **P0 reuse:** do NOT retrain. Use the promoted-gold per-race predictions
  `params/gold/per_race_predictions/round01..06_*.json` for R1-6 (same source G1's baseline used). Verify
  the promoted gold config matches P0 intent (train 2018-2024, eval 2025, anchor on, quali_pace_gap).
- **P1-P3 per-period pipeline** (automate the `docs/evo/analysis_refresh.md` recipe with cutoff params):
  1. Build the as-of-N 2025 compound prior via `run_season_alignment ... --through-round N --skip-collection`
     into a per-period prior root (do NOT overwrite `params/gold/compound_prior/2025`).
  2. Write a per-period gold-cycle TOML: `mode="research"` (so cutoff overrides are allowed),
     `data.eval_year_train_through_round=N`, `data.eval_round_range=[N+1, N+6]`,
     `data.compound_prior_root=<period prior root>`, `runtime.allow_same_season_compound_prior=true`,
     anchor on + quali_pace_gap to match promoted gold, isolated `outputs`/`report_dir`/
     `uncertainty_calibration_dir` under a per-period work area, `runtime.utilization` from a passthrough.
  3. Run the gold cycle, then static fusion + materialize bundles + the trained sampled-runtime predictions
     for the eval rounds (the runbook Steps 3/3b/4 scripts). Collect the per-race top-10 predicted order for
     each eval round.
- **Aggregate** all 24 races (P0 R1-6 + P1 R7-12 + P2 R13-18 + P3 R19-24) via the G1 aggregator
  (`src/fantasy_scoring/season.py`) against DB actuals → season fantasy total + per-race breakdown +
  per-race period provenance.
- **Leakage attestation** (the orchestrator ENFORCES this, hard): for every scored race R, assert
  `max training round used for R's period < R` and `the compound prior used for R was built through a round < R`.
  Emit a per-race attestation table; the run FAILS if any race violates it.
- **Output contract** `reports/walkforward/walkforward_2025.summary.json`: `season_total`,
  `baseline_total` (from G1 baseline, for comparison), `per_race[]` each with
  `{round, gp_name, period, train_max_round, compound_prior_through_round, predicted_top10, actual_top, fantasy_score, leakage_ok}`,
  and `attestation_all_pass: bool`. Plus a `.md`.
- **Scripts:** `scripts/run_walkforward_backtest.py` (full run entrypoint; `--utilization` passthrough;
  `--dry-run` that prints the per-period execution plan WITHOUT running anything) and
  `scripts/verify_walkforward_run.py` (exit 0 iff the summary has 24 races, each period-attributed, and
  `attestation_all_pass` is true; nonzero otherwise).

## Protected Intent
A correct, leakage-free walk-forward season fantasy score. The attestation must be real and enforced — a
silent leak or a missing race silently invalidates #439. P0 reuse must be the genuine promoted-gold model.

## Test Mode
`TDD required` for the orchestration logic and attestation; heavy training/fusion/materialize calls are
MOCKED in tests. Phase-1 wiring proven via spy/mock as described.

## Close Criteria
- Phase 1: a cutoff gold-cycle config provably forwards the cutoff into training + eval range (test, real code path, training solve mocked).
- Orchestrator defines the 4 periods exactly per the table; P0 reuses promoted gold; P1-3 use the cutoff pipeline.
- Leakage attestation logic correct and enforced (unit test: a synthetic race with train round >= race round FAILS the run).
- Aggregation reuses G1; output summary matches the contract above; `verify_walkforward_run.py` is a real gate.
- `--dry-run` prints a per-period plan (periods, cutoff N, eval range, prior root, configs) without executing.
- Unit tests at `tests/unit/evo_predictor/walkforward/test_orchestrator.py` green with heavy calls mocked.
- `py -m src.utils.simplification_limits` passes on touched paths.

## Allowed Scope
- New: `src/evo_predictor/walkforward/` (package), `scripts/run_walkforward_backtest.py`,
  `scripts/verify_walkforward_run.py`, tests under `tests/unit/evo_predictor/walkforward/`.
- Modify (Phase 1 wiring): `src/evo_predictor/gold_cycle/runner.py`, `runner_support.py` as needed to thread
  the cutoff; keep gold defaults unchanged.
- Read-only: `docs/evo/analysis_refresh.md` (the per-period recipe), the runbook scripts
  (`run_static_hierarchical_fusion_training.py`, `materialize_runtime_bundles.py`,
  `assemble_trained_sampled_runtime_manifest.py`, `run_sampled_runtime_comparison.py`),
  `src/fantasy_scoring/season.py`, `params/gold/`.

## Specific Exclusions
- Do NOT run heavy training / a real gold cycle here (that is G4). Do NOT change scoring (`scoring_rules.py`),
  the G2 leakage primitives' semantics, or gold-default behavior. Do NOT overwrite promoted `params/gold/`
  artifacts (period work goes to isolated per-period dirs).

## Constraints
- As-of cutoff explicit; DB-only; `py` not `python`; run from repo root; repo-relative manifest paths.
- One canonical path; validate inputs with clear messages; tunables in config/constants.
- Reuse the runbook scripts rather than reimplementing fusion/materialize/comparison.

## Required Evidence
- `py -m pytest tests/unit/evo_predictor/walkforward/test_orchestrator.py -q` (green) — paste output.
- `py scripts/run_walkforward_backtest.py --dry-run` output (the per-period plan).
- Phase-1 wiring test output.
- Regression: `py -m pytest tests/unit/evo_predictor/test_gold_cycle_runner.py -q` (or the runner suite) green.
- `py -m src.utils.simplification_limits` on touched paths.
- A short design note: the per-period config/prior layout and how predictions for eval rounds are collected,
  so the Commander can drive the real run in G4.

## Verification Commands
```bash
py -m pytest tests/unit/evo_predictor/walkforward/test_orchestrator.py -q
py scripts/run_walkforward_backtest.py --dry-run
py -m pytest tests/unit/evo_predictor/test_gold_cycle_runner.py -q
py -m src.utils.simplification_limits
```

## Suggested Model Tier
`stronger` — large, intricate orchestration spanning runner wiring, the per-period pipeline, attestation,
and the run/verify scripts; correctness gates the multi-hour G4 run.

## Authority
Decided (Commander): 4 periods per the table; P0 reuses promoted gold; full pipeline per period
(gold+fusion+calibration+materialize); per-period priors isolated (never overwrite params/gold); output
under reports/walkforward/. You choose module/function layout, the per-period config mechanism, and how to
collect eval-round predictions — record them in the design note. You must NOT loosen gold guards, change
scoring, or run heavy training in this gate.

## Stop Conditions
Stop and return if: Phase-1 wiring requires changing gold-default behavior or broad refactors; the
per-period prediction-collection path cannot be determined from the runbook/scripts without running a real
cycle (return a design question); or the promoted-gold config does NOT match P0 intent (surface it).

## Return Format
Return IMPLEMENTER_RESULT: completed slice (Phase 1 + Phase 2 status), files changed, test mode satisfied,
evidence (paste test output + dry-run plan + simplification), the design note (per-period layout +
prediction collection), assumptions, stop conditions hit, out-of-scope observations.
