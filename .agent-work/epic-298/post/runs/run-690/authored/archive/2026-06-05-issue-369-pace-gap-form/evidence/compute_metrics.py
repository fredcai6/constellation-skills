"""
Compute variance-channel correlation metrics for all A/B arms.
Imports existing functions from src/ -- does NOT reimplement math.
Writes metric JSON artifacts to .agent-work/issue-369-pace-gap-form/evidence/
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Use the existing _corr, _mean from task_calibration
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.evo_predictor.gold_cycle.task_calibration import _corr, _mean  # noqa: E402

REPO_ROOT = Path(__file__).parent.parent.parent.parent
EVIDENCE_DIR = REPO_ROOT / ".agent-work/issue-369-pace-gap-form/evidence"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------------
# Promoted control numbers from gold_cycle_260530_152746 summary.json
# -------------------------------------------------------------------
PROMOTED_CONTROL = {
    "driver_quali_power_from_recent_history": {
        "arm": "control-promoted",
        "source": "reports/evo/gold_cycle_260530_152746_2018thru2024.summary.json",
        "scored_event_count": 149,
        "rank_mae_vs_actual": 3.6124999999999994,
        "pairwise_sign_accuracy": 0.7406798265874386,
        "pairwise_nll_skill": None,  # not in summary (computed from pairwise_log_loss)
        "pairwise_log_loss": 0.6297541831930479,
        "calibrated_sigma_pi_trace_mean": 2.0212010464941463,
        # From unc_diag_260530_152746_2018thru2024.json module 'driver_quali_power_from_recent_history'
        "corr_sigma_pi_trace_vs_rank_mae": 0.6459749635008385,  # NOT from summary—from unc_diag
        "corr_sigma_pi_trace_vs_nll": None,  # not separately listed in unc_diag; field is corr_sigma_pi_trace_vs_brier/log_loss
        "corr_sigma_pi_trace_vs_log_loss": 0.594291731985638,  # from unc_diag correlations
    },
    "constructor_quali_power_from_recent_history": {
        "arm": "control-promoted",
        "source": "reports/evo/gold_cycle_260530_152746_2018thru2024.summary.json",
        "scored_event_count": 149,
        "rank_mae_vs_actual": 1.7287878787878785,
        "pairwise_sign_accuracy": 0.7703282882769903,
        "pairwise_log_loss": 0.6215303515394529,
        "calibrated_sigma_pi_trace_mean": 1.019562808951984,
        # From unc_diag_260530_152746_2018thru2024.json module 'constructor_quali_power_from_recent_history'
        "corr_sigma_pi_trace_vs_rank_mae": 0.6459749635008385,  # placeholder - will read actual below
        "corr_sigma_pi_trace_vs_log_loss": 0.594291731985638,  # placeholder - will read actual below
    },
}

# Read actual unc_diag correlations for each module
unc_diag_path = REPO_ROOT / "reports/evo/unc_diag_260530_152746_2018thru2024.json"
unc_diag = json.loads(unc_diag_path.read_text(encoding="utf-8"))

for module_entry in unc_diag["modules"]:
    mname = module_entry["module_name"]
    if mname in PROMOTED_CONTROL:
        PROMOTED_CONTROL[mname]["corr_sigma_pi_trace_vs_rank_mae"] = module_entry["correlations"]["corr_sigma_pi_trace_vs_rank_mae"]
        PROMOTED_CONTROL[mname]["corr_sigma_pi_trace_vs_log_loss"] = module_entry["correlations"]["corr_sigma_pi_trace_vs_log_loss"]
        PROMOTED_CONTROL[mname]["corr_sigma_pi_trace_vs_brier"] = module_entry["correlations"]["corr_sigma_pi_trace_vs_brier"]
        PROMOTED_CONTROL[mname]["unc_diag_source"] = "reports/evo/unc_diag_260530_152746_2018thru2024.json"
        PROMOTED_CONTROL[mname]["unc_diag_event_count"] = module_entry["event_count"]


def extract_metrics_from_backtest(backtest_path: Path, arm_name: str) -> dict:
    """Extract all required metrics from a backtest JSON file."""
    data = json.loads(backtest_path.read_text(encoding="utf-8"))
    module_name = data["module_name"]
    event_count = data["event_count"]

    # Build flat per-event rows for correlation computation
    per_event_rows = []
    availability_count = 0
    total_event_count = event_count

    for ev in data["per_event"]:
        m = ev["metrics"]
        # Only include events that were scored (have pairwise_nll)
        if m.get("pairwise_nll") is not None:
            per_event_rows.append(m)
            availability_count += 1

    # Use existing _corr, _mean from task_calibration
    corr_sigma_vs_rank_mae = _corr(per_event_rows, "sigma_pi_trace", "rank_mae_vs_retro_bt")
    corr_sigma_vs_nll = _corr(per_event_rows, "sigma_pi_trace", "pairwise_nll")

    agg = data["aggregate_metrics"]

    return {
        "arm": arm_name,
        "module_name": module_name,
        "source": str(backtest_path.relative_to(REPO_ROOT)),
        "scored_event_count": availability_count,
        "total_event_count": total_event_count,
        "rank_mae_vs_actual": agg.get("rank_mae_vs_actual"),
        "rank_mae_chance": agg.get("rank_mae_chance"),
        "rank_mae_vs_actual_skill": agg.get("rank_mae_vs_actual_skill"),
        "pairwise_sign_accuracy": agg.get("pairwise_sign_accuracy"),
        "pairwise_nll": agg.get("pairwise_nll"),
        "pairwise_nll_chance": agg.get("pairwise_nll_chance"),
        "pairwise_nll_skill": agg.get("pairwise_nll_skill"),
        "sigma_pi_trace_mean": agg.get("sigma_pi_trace"),
        "field_std_mean": agg.get("field_std"),
        "spearman": agg.get("spearman"),
        # Variance channel correlations: computed using existing _corr function from task_calibration.py
        "corr_sigma_pi_trace_vs_rank_mae": corr_sigma_vs_rank_mae,
        "corr_sigma_pi_trace_vs_nll": corr_sigma_vs_nll,
        "n_events_for_corr": len(per_event_rows),
    }


# -------------------------------------------------------------------
# Compute metrics for all arms
# -------------------------------------------------------------------
RUNS = {
    "driver_quali_power_from_recent_history": {
        "treatment_v2": REPO_ROOT / "outputs/evo_runs/treatment_v2_driver_quali_rh/backtest_2025.json",
        "fresh_v1":     REPO_ROOT / "outputs/evo_runs/fresh_v1_driver_quali_rh/backtest_2025.json",
    },
    "constructor_quali_power_from_recent_history": {
        "treatment_v2": REPO_ROOT / "outputs/evo_runs/treatment_v2_constructor_quali_rh/backtest_2025.json",
        "fresh_v1":     REPO_ROOT / "outputs/evo_runs/fresh_v1_constructor_quali_rh/backtest_2025.json",
    },
}

results = {}
for module_name, arms in RUNS.items():
    results[module_name] = {
        "control_promoted": PROMOTED_CONTROL[module_name],
    }
    for arm_name, path in arms.items():
        results[module_name][arm_name] = extract_metrics_from_backtest(path, arm_name)

# Write out metrics
output_path = EVIDENCE_DIR / "metrics_all_arms.json"
output_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
print(f"Metrics written to: {output_path}")

# Print summary
for module_name, arms in results.items():
    print(f"\n--- {module_name} ---")
    for arm_name, arm_data in arms.items():
        print(f"  {arm_name}:")
        print(f"    rank_mae_vs_actual: {arm_data.get('rank_mae_vs_actual')}")
        print(f"    pairwise_sign_accuracy: {arm_data.get('pairwise_sign_accuracy')}")
        print(f"    pairwise_nll_skill: {arm_data.get('pairwise_nll_skill')}")
        print(f"    sigma_pi_trace_mean: {arm_data.get('sigma_pi_trace_mean', arm_data.get('calibrated_sigma_pi_trace_mean'))}")
        print(f"    corr_sigma_pi_trace_vs_rank_mae: {arm_data.get('corr_sigma_pi_trace_vs_rank_mae')}")
        print(f"    corr_sigma_pi_trace_vs_nll: {arm_data.get('corr_sigma_pi_trace_vs_nll')}")
        print(f"    n (events for corr): {arm_data.get('n_events_for_corr', arm_data.get('unc_diag_event_count', 'N/A'))}")
