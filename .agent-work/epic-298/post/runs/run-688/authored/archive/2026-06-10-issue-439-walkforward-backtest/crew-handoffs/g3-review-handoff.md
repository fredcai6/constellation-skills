# Reviewer Handoff

## Gate
`g3` — Walk-forward orchestrator + gold-cycle runner cutoff wiring + leakage attestation.
Correctness here gates the multi-hour G4 run — review carefully.

## What Was Implemented
Phase 1: gold-cycle runner now threads `eval_year_train_through_round`/`eval_round_range` into MAIN training
+ eval phase + as-of-N eval-year compound prior (LOSO/calibration jobs excluded; gold defaults unchanged).
Phase 2: `src/evo_predictor/walkforward/` (periods, attestation, orchestrator, pipeline), `scripts/run_walkforward_backtest.py`
(`--dry-run`, `--utilization`), `scripts/verify_walkforward_run.py`, output contract `reports/walkforward/walkforward_2025.summary.json`.
Reported: walkforward suite 79 passed; runner regression 24 passed; run.py regression 157 passed; simplification PASS (16 files).

## How to Inspect the Diff
```bash
cd /c/Programs/f1Brainz
git status --short
git diff --stat
git diff -- src/evo_predictor/gold_cycle/runner.py src/evo_predictor/gold_cycle/runner_support.py src/evo_predictor/run.py
```
New (untracked): `src/evo_predictor/walkforward/`, `scripts/run_walkforward_backtest.py`,
`scripts/verify_walkforward_run.py`, `tests/unit/evo_predictor/walkforward/test_{runner_cutoff_wiring,orchestrator,pipeline,run_scripts}.py`.
Design note: `.agent-work/issue-439-walkforward-backtest/evidence/g3-design-note.md`. Full spec: `crew-handoffs/g3-handoff.md`.

## Close Criteria (verify INDEPENDENTLY)
- **Phase-1 wiring:** read the runner diff — a cutoff config forwards `eval_year_train_through_round`/`eval_round_range`
  into `prepare_module_training_data` for the MAIN train job, restricts the eval/backtest to `eval_round_range`,
  and uses the as-of-N same-season eval-year prior. Confirm **LOSO/calibration jobs do NOT receive the cutoff**
  and that with no cutoff the runner behavior is unchanged. Re-run `py -m pytest tests/unit/evo_predictor/walkforward/test_runner_cutoff_wiring.py tests/unit/evo_predictor/test_gold_cycle_runner.py -q`.
- **Period definitions** match the issue table exactly (P0 R1-6, P1 R7-12, P2 R13-18, P3 R19-24; cutoffs 0/6/12/18). Read `periods.py`.
- **Attestation enforced:** read `attestation.py` — for each race, `train_max_round < race_round` AND
  `compound_prior_through_round < race_round`; a violation FAILS the run. Confirm a test injects a leaking
  synthetic race and asserts failure.
- **P0 reuse valid:** uses promoted-gold `params/gold/per_race_predictions/round01..06` and the promoted config matches P0 intent.
- **Prediction-collection rule:** P1-3 rank `per_race[].prediction.position_distribution` by ascending mean.
  Verify the claim that this reproduces the promoted `predictions[].rank` ordering (spot-check the logic/test);
  a wrong ordering rule would silently corrupt every walk-forward fantasy score.
- **verify_walkforward_run.py** is a real gate (exit 0 only on 24 races + period-attributed + attestation_all_pass).
  Re-run it against the committed sample/fixture if present.
- **Tests genuine:** mocks isolate the multi-hour pipeline (PipelinePort/SubprocessPipeline) but the
  orchestration/attestation/aggregation logic runs on real code. Re-run `py -m pytest tests/unit/evo_predictor/walkforward -q`.
- **simplification_limits** passes on touched paths.

## Allowed Scope
Phase-1 modifies runner.py/runner_support.py/run.py (cutoff threading only). Phase-2 is new walkforward
package + scripts + tests. No changes to scoring, G2 leakage semantics, gold defaults, or promoted params/gold.

## Specific Exclusions (BLOCK if violated)
- No heavy training/real gold cycle run in this gate. No overwrite of promoted `params/gold/`.
- `src/fantasy_scoring/scoring_rules.py` and G2 primitives' semantics unchanged.

## Constraints (each a check)
- As-of cutoff explicit; DB-only; repo-relative paths; one canonical path; reuse runbook scripts; G1 reused for aggregation.

## Evidence Produced
- walkforward suite 79 passed; runner regression 24; run.py regression 157; simplification PASS (16).
- `--dry-run` plan correct (P0 reuse; P1 N=6→7-12; P2 N=12→13-18; P3 N=18→19-24).
- Implementer result + design note in `.agent-work/issue-439-walkforward-backtest/evidence/`.

## Suggested Model Tier
`stronger` — wiring + attestation + prediction-ordering correctness gate the multi-hour run.

## Stop Conditions
BLOCK if: cutoff reaches LOSO/calibration; gold defaults changed; attestation not enforced; the
prediction-ordering rule does not reproduce promoted ordering; verify script is not a real gate; tests hollow.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations.
