"""Fantasy-score a pre-quali sampled_state backtest result against DB actuals.

INFERENCE/REPORTING glue (lives in .agent-work, not src/): it does not train, does
not touch FastF1, and reuses the project's canonical building blocks:

  - per-race top-10 from prediction.position_distribution via the established
    "ascending mean position" rule:
      src.evo_predictor.walkforward.periods.predicted_top10_from_position_distribution
  - DB actuals from session_classifications session_type 'R':
      DatabaseManager(db_path).get_session_classification(year, round, "R")
  - season aggregation + scoring:
      src.fantasy_scoring.season.SeasonAggregator / RaceResult
      (-> src.fantasy_scoring.scoring_rules.ScoringCalculator)

Usage:
    py .agent-work/multiseason-fantasy/score_season.py \
        --trained-json <sampled_runtime_comparison_*.trained.json> \
        --year <YYYY> --db data/f1_data_<YYYY>.db [--provenance <label>]

Emits one JSON line (the season summary) to stdout.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.data.database.manager import DatabaseManager
from src.evo_predictor.walkforward.periods import (
    predicted_top10_from_position_distribution,
)
from src.fantasy_scoring.season import RaceResult, SeasonAggregator


def build_race_results(trained_json: dict, *, year: int, db: DatabaseManager, provenance: str):
    per_race = trained_json.get("per_race")
    if not isinstance(per_race, list) or not per_race:
        raise ValueError("trained_json missing a non-empty 'per_race' list")
    # Leakage/mode guard: the comparison MUST have been produced in sampled_state
    # (pre-quali). Refuse to score an oracle (actual-grid) result.
    mode = (trained_json.get("diagnostics", {}) or {}).get("mode")
    if mode != "sampled_state":
        raise ValueError(
            f"refusing to score: diagnostics.mode={mode!r}, expected 'sampled_state' "
            "(pre-quali). Oracle modes inject actual qualifying and are leaky."
        )
    races = []
    for race in per_race:
        round_num = int(race["round_num"])
        gp_name = str(race.get("gp_name", f"round{round_num}"))
        prediction = race.get("prediction") or {}
        # Per-race runtime cross-check: no oracle grid/lap-N may have been used.
        rt = (prediction.get("stage_diagnostics", {}) or {}).get("runtime", {}) or {}
        if rt.get("oracle_grid_used") or rt.get("oracle_lap_n_used"):
            raise ValueError(
                f"round {round_num}: oracle state used "
                f"(grid={rt.get('oracle_grid_used')}, lap_n={rt.get('oracle_lap_n_used')}); "
                "not pre-quali."
            )
        dist = prediction.get("position_distribution")
        if not isinstance(dist, dict):
            raise ValueError(f"round {round_num}: missing prediction.position_distribution")
        top10 = predicted_top10_from_position_distribution(dist)
        actual_results = db.get_session_classification(int(year), round_num, "R")
        if not actual_results:
            raise ValueError(
                f"round {round_num}: no DB actuals (session_classifications R) for {year}"
            )
        races.append(RaceResult(
            round_num=round_num,
            gp_name=gp_name,
            top10_picks=top10,
            actual_results=actual_results,
            provenance=provenance,
        ))
    return races


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trained-json", required=True)
    ap.add_argument("--year", type=int, required=True)
    ap.add_argument("--db", required=True)
    ap.add_argument("--provenance", default="")
    args = ap.parse_args()

    trained = json.loads(Path(args.trained_json).read_text(encoding="utf-8"))
    db = DatabaseManager(db_path=args.db)
    provenance = args.provenance or f"sampled_state-pre-quali-{args.year}"
    races = build_race_results(trained, year=args.year, db=db, provenance=provenance)
    result = SeasonAggregator().aggregate(races)

    summary = {
        "year": args.year,
        "mode": "sampled_state",
        "evidence_model": "pre-quali (practice-only)",
        "trained_json": str(args.trained_json),
        "db_path": args.db,
        "race_count": len(races),
        "season_total": result.season_total,
        "per_race": result.per_race,
    }
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
