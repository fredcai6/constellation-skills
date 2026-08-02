# Implementer Handoff

## Gate
`g1` — Season fantasy aggregation + baseline 2025 estimate

## Task
Build a reusable **season fantasy aggregator** and a script that computes the
**no-in-season-retrain baseline** 2025 season fantasy score from the *already-on-disk*
promoted-gold per-race predictions. This is the first deliverable of issue #439 (walk-forward
backtest); the aggregator will be reused by the walk-forward orchestrator (a later gate).

Two artifacts:
1. `src/fantasy_scoring/season.py` — a season aggregator that, given a set of per-race inputs
   (round, gp_name, top-10 predicted order, actual results, provenance), computes each race's
   fantasy score via the EXISTING `ScoringCalculator.fantasy_score_from_predictions` and returns
   a season total (lower = better) with a per-race breakdown and per-race provenance (which
   prediction source / which period produced it). Keep it source-agnostic — it must NOT hardcode
   the promoted-gold path; the walk-forward will feed it per-period predictions later.
   Include small helpers: extract top-10 `(driver_id, predicted_position)` from a per-race
   prediction JSON, and load actual finishing results from the DB.
2. `scripts/run_walkforward_baseline.py` — computes the BASELINE: for 2025 rounds 1..24, read the
   promoted-gold predictions `params/gold/per_race_predictions/round*.json`, load actual R results
   from `data/f1_data_2025.db`, aggregate, print the season total + per-race table, and write a
   small committed artifact `reports/walkforward/walkforward_2025_baseline.json` (+ a short `.md`).
   Label it clearly as the *no-in-season-retrain baseline* (promoted gold applied to all 24 races).

## Protected Intent
A correct, reproducible 2025 season fantasy score (delta-based, lower-is-better) that exactly
matches the project's scoring semantics, with actuals sourced ONLY from the DB. This number is a
real performance estimate the user is waiting on — it must be trustworthy, not approximate.

## Test Mode
`TDD required` — scoring correctness is the whole point; write tests first on synthetic fixtures.

## Close Criteria
- `src/fantasy_scoring/season.py` aggregates per-race scores into a season total using
  `ScoringCalculator.fantasy_score_from_predictions` (do NOT re-implement scoring).
- Top-10 extraction: from `predictions` list, take the 10 items with `rank` 1..10 as
  `(driver_id, rank)`. (Schema: each item is `{rank, driver_id, driver_name, team, score, ...}`.)
- Actuals come from the DB via `DatabaseManager` (e.g. `get_session_classification(2025, round, 'R')
  -> {driver_id: position}`); NO FastF1, NO raw cross-module SQL if a DB helper exists.
- Drivers predicted in the top-10 but absent from actuals are scored as DNF (the scorer already
  applies `DNF_POSITION`); confirm this path is exercised by a test.
- `scripts/run_walkforward_baseline.py` runs end-to-end and prints the 2025 baseline season total +
  per-race breakdown, and writes `reports/walkforward/walkforward_2025_baseline.json`.
- Unit tests at `tests/unit/fantasy_scoring/test_season_aggregation.py` pass and cover: a known
  synthetic season total, top-10 extraction, the DNF path, and provenance carry-through. Tests must
  use small synthetic fixtures — do NOT load the 27MB sampled_runtime backtest files.

## Allowed Scope
- New: `src/fantasy_scoring/season.py`, `scripts/run_walkforward_baseline.py`,
  `tests/unit/fantasy_scoring/test_season_aggregation.py`, `reports/walkforward/` (new dir).
- Read-only reference: `src/fantasy_scoring/scoring_rules.py`, `src/data/database.py` (DB helpers),
  `params/gold/per_race_predictions/round*.json`, `src/utils/constants.py`.

## Specific Exclusions
- Do NOT touch the gold cycle, training, the promoted gold artifacts, or any prediction-producing
  code. This gate only *consumes* existing predictions + DB actuals and aggregates.
- Do NOT build the walk-forward orchestrator or any cutoff/retrain logic (later gates).

## Constraints
- DB-only for actual results; `py` not `python`; run from repo root.
- Reuse existing scoring; one canonical path; validate inputs with clear messages.
- Run `py -m src.utils.simplification_limits` on touched `src/` and `tests/` paths (must pass).

## Required Evidence
- `py -m pytest tests/unit/fantasy_scoring/test_season_aggregation.py -q` output (green).
- Output of `py scripts/run_walkforward_baseline.py` showing the 2025 baseline season total +
  per-race table (paste the printed summary).
- `py -m src.utils.simplification_limits` result on touched paths.

## Verification Commands
```bash
py -m pytest tests/unit/fantasy_scoring/test_season_aggregation.py -q
py scripts/run_walkforward_baseline.py
py -m src.utils.simplification_limits  # on touched src/ and tests/ paths
```

## Suggested Model Tier
`simple bounded` — well-scoped, reuses existing scoring; main care is schema correctness.

## Authority
Decided already (Commander): report dir = `reports/walkforward/`; baseline source =
`params/gold/per_race_predictions/`; scoring via existing `fantasy_score_from_predictions`.
You may choose internal function/dataclass shapes for `season.py`, but keep it source-agnostic and
reusable by a future orchestrator. Do not change scoring semantics or the report location.

## Stop Conditions
Stop and return if: the per-race prediction schema differs from the above, a DB helper for R
results does not exist (report what does), scope must expand into training/prediction code, or the
baseline number looks implausible (e.g., all-DNF) — surface it rather than papering over.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced
(including the printed baseline season total), assumptions used, stop conditions hit, out-of-scope
observations.
