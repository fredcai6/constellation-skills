"""Assemble the committed multi-season leakage-free pre-quali fantasy report.

Reuses score_season.build_race_results (which enforces the sampled_state/oracle
leakage guard) + SeasonAggregator. Writes reports/walkforward/multiseason_fantasy.{json,md}.
"""
from __future__ import annotations
import importlib.util, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("score_season", Path(__file__).with_name("score_season.py"))
score_season = importlib.util.module_from_spec(spec); spec.loader.exec_module(score_season)
from src.data.database.manager import DatabaseManager
from src.fantasy_scoring.season import SeasonAggregator

WD = Path(__file__).parent
SOURCES = {
    2022: WD / "backtests/heldout_2022_sampled.json",
    2023: WD / "backtests/heldout_2023_sampled.json",
    2024: WD / "backtests/heldout_2024_sampled.json",
    2025: ROOT / "reports/evo/sampled_runtime_backtests/sampled_runtime_comparison_2018-2019-2020-2021-2022-2023-2024_eval_2025.trained.json",
}
MODEL_SRC = {
    2022: "LOSO heldout_2022 (trained on 2018-21,23,24 — excludes 2022)",
    2023: "LOSO heldout_2023 (trained on 2018-22,24 — excludes 2023)",
    2024: "LOSO heldout_2024 (trained on 2018-23 — excludes 2024)",
    2025: "gold 2018-2024 (excludes 2025)",
}
HUMAN = {2022: 739, 2023: 632, 2024: 615, 2025: 711}

rows = []
for yr in (2022, 2023, 2024, 2025):
    trained = json.loads(SOURCES[yr].read_text(encoding="utf-8"))
    db = DatabaseManager(db_path=str(ROOT / f"data/f1_data_{yr}.db"))
    races = score_season.build_race_results(trained, year=yr, db=db, provenance=f"prequali-{yr}")
    res = SeasonAggregator().aggregate(races)
    rows.append({
        "season": yr, "model_fantasy": res.season_total, "human_fantasy": HUMAN[yr],
        "gap_model_minus_human": res.season_total - HUMAN[yr], "races": len(races),
        "model_per_race": round(res.season_total / len(races), 2),
        "human_per_race": round(HUMAN[yr] / len(races), 2),
        "model_source": MODEL_SRC[yr],
    })

report = {
    "title": "Leakage-free, pre-quali fantasy: model vs human, 2022-2025",
    "metric": "F1 fantasy season score (sum of |pred_pos-actual| over top-10 picks + bingo bonuses); LOWER is better",
    "evidence_model": "pre-quali / practice-only (sampled_state; verified in STEP1_EVIDENCE_MODEL.md, oracle modes excluded)",
    "verdict": "The leakage-free model LOSES to the human in all four seasons (by 92-331 pts).",
    "seasons": rows,
    "totals": {
        "model": sum(r["model_fantasy"] for r in rows),
        "human": sum(HUMAN[y] for y in HUMAN),
    },
    "leakage_controls": [
        "2025 model = gold cycle trained on 2018-2024 only (eval 2025 held out); pipeline_validation green.",
        "2022-2024 models = leave-one-season-out folds, each EXCLUDES its eval season from training (manifest provenance verified).",
        "Predictions are pre-quali (sampled_state): practice-only ordering; oracle/actual-grid modes refused by the scorer.",
        "Compound prior is time-safe (season < eval year).",
        "The prior '707 beats human 711' figure was LEAKED (a March train-evo-pipeline trained on 2025) and is retracted.",
    ],
    "caveats": [
        "LOSO folds train on seasons AFTER the eval season too (e.g. heldout_2022 saw 2023-24) — a mild edge the human lacked; the model still loses, so the gap is conservative.",
        "Gold static fusion was trained on LOSO OOF spanning all years and structurally saw each held-out year's OOF metrics; follow-up: strict per-season-holdout fusion.",
        "sampled_state uses the actual-Q roster (who started, not their order) — the project's established pre-quali design, not positional leakage.",
    ],
}
out_json = ROOT / "reports/walkforward/multiseason_fantasy.json"
out_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

md = ["# Leakage-free, pre-quali fantasy — model vs human (2022-2025)", "",
      f"**{report['verdict']}**", "", report["metric"], "",
      "| Season | Model | Human | Gap (model-human) | Model/race | Human/race |",
      "|---|--:|--:|--:|--:|--:|"]
for r in rows:
    md.append(f"| {r['season']} | {r['model_fantasy']:.0f} | {r['human_fantasy']} | "
              f"**+{r['gap_model_minus_human']:.0f}** | {r['model_per_race']} | {r['human_per_race']} |")
md += ["", f"Totals — model **{report['totals']['model']:.0f}** vs human **{report['totals']['human']}** "
       f"(lower is better).", "", "## Leakage controls", ""]
md += [f"- {c}" for c in report["leakage_controls"]]
md += ["", "## Caveats", ""] + [f"- {c}" for c in report["caveats"]]
(ROOT / "reports/walkforward/multiseason_fantasy.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print(json.dumps({"seasons": rows, "totals": report["totals"]}, indent=2))
