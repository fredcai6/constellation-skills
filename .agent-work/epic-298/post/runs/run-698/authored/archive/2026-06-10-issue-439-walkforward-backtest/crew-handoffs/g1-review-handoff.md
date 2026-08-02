# Reviewer Handoff

## Gate
`g1` — Season fantasy aggregation + 2025 no-in-season-retrain baseline

## What Was Implemented
A source-agnostic season fantasy aggregator (`src/fantasy_scoring/season.py`), a baseline script
(`scripts/run_walkforward_baseline.py`) computing the 2025 no-in-season-retrain season fantasy score
from the promoted-gold per-race predictions vs DB actuals, 14 unit tests, and a committed baseline
artifact under `reports/walkforward/`. Reported **baseline season total = 707.0** (lower=better).

## How to Inspect the Diff
```bash
cd /c/Programs/f1Brainz
git status --short
git diff --stat
git diff -- src/fantasy_scoring/season.py scripts/run_walkforward_baseline.py tests/unit/fantasy_scoring/test_season_aggregation.py
```
New files (untracked) — inspect directly:
`src/fantasy_scoring/season.py`, `scripts/run_walkforward_baseline.py`,
`tests/unit/fantasy_scoring/test_season_aggregation.py`,
`reports/walkforward/walkforward_2025_baseline.json` + `.md`.

## Task Statement
Build a reusable season aggregator that scores each 2025 race via the EXISTING
`ScoringCalculator.fantasy_score_from_predictions` and sums to a season total with per-race breakdown +
provenance; plus a script that computes the baseline from `params/gold/per_race_predictions/round*.json`
vs `data/f1_data_2025.db` actuals. Full spec: `.agent-work/issue-439-walkforward-backtest/crew-handoffs/g1-handoff.md`.

## Close Criteria (each a review check)
- Scoring uses `fantasy_score_from_predictions` — scoring is NOT re-implemented.
- Top-10 extraction = items with `rank` 1..10 as `(driver_id, rank)`.
- Actuals come from the DB only (via `DatabaseManager.get_session_classification`), no FastF1, no ad-hoc SQL if a helper exists.
- DNF path (predicted driver absent from actuals → `DNF_POSITION`) is exercised by a test.
- Aggregator is source-agnostic (no hardcoded promoted-gold path) and reusable by a future orchestrator.
- `scripts/run_walkforward_baseline.py` reproduces the season total. **Re-run it and confirm 707.0.**
- Tests are real (assert on known synthetic totals, not trivially-true), use small fixtures (not the 27MB files).

## Allowed Scope
New files only: `src/fantasy_scoring/season.py`, `scripts/run_walkforward_baseline.py`,
`tests/unit/fantasy_scoring/test_season_aggregation.py`, `reports/walkforward/`. Read-only reference to
scoring_rules, database, constants, per_race_predictions.

## Specific Exclusions (flag if touched)
- No changes to the gold cycle, training, promoted gold artifacts, or any prediction-producing code.
- No walk-forward orchestrator / cutoff / retrain logic.

## Constraints the Implementation Must Respect (each a review check)
- DB-only for actuals; `py` not `python`; one canonical path; reuse existing scoring.
- `py -m src.utils.simplification_limits` passes on touched paths.

## Evidence Produced
- pytest: `14 passed in 0.10s`.
- baseline script printed season total `707.0` with a 24-row per-race table (all source = promoted-gold).
- simplification_limits: `PASS (2 files checked)`.
- Full IMPLEMENTER_RESULT: `.agent-work/issue-439-walkforward-backtest/evidence/g1-implementer-result.md`.

## Suggested Model Tier
`simple bounded` — reuses existing scoring; verify schema/DB correctness and that the baseline reproduces.

## Stop Conditions
BLOCK if: scoring is re-implemented, actuals not DB-sourced, baseline does not reproduce, tests are
hollow, or excluded code was touched.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations.
