import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for label, name in [
    ("baseline", "gold_cycle_260526_004033_2018thru2024.summary.json"),
    ("new", "gold_cycle_260530_042533_2018thru2024.summary.json"),
]:
    s = json.loads((ROOT / "reports/evo" / name).read_text())
    t = s.get("task_calibration_diagnostics", {})
    print(label)
    for task in ("quali", "race_start", "race"):
        sm = t.get(task, {}).get("slice_metrics", {})
        print(
            f"  {task}: brier={sm.get('mean_brier_score')} "
            f"ll={sm.get('mean_pairwise_log_loss')} "
            f"corr={sm.get('corr_sigma_pi_trace_vs_brier')}"
        )
