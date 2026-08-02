#!/usr/bin/env python3
"""Compare G5 gold cycle metrics vs baseline and extract sigma diagnostics."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE_SUMMARY = ROOT / "reports/evo/gold_cycle_260526_004033_2018thru2024.summary.json"
NEW_SUMMARY = ROOT / "reports/evo/gold_cycle_260530_042533_2018thru2024.summary.json"
BASELINE_UNC = ROOT / "reports/evo/unc_diag_260526_004033_2018thru2024.json"
NEW_UNC = ROOT / "reports/evo/unc_diag_260530_042533_2018thru2024.json"
OUT = ROOT / ".agent-work/issue-142-sigma-calibration/evidence/g5-metrics-comparison.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    baseline = load(BASELINE_SUMMARY)
    new = load(NEW_SUMMARY)
    baseline_unc = load(BASELINE_UNC) if BASELINE_UNC.exists() else {}
    new_unc = load(NEW_UNC) if NEW_UNC.exists() else {}

    module_rows = []
    regressions = []
    for nm in sorted({m["module_name"] for m in baseline["modules"]}):
        b = next(m for m in baseline["modules"] if m["module_name"] == nm)
        n = next(m for m in new["modules"] if m["module_name"] == nm)
        bp = b["performance"]
        np_ = n["performance"]
        bu = b.get("uncertainty", {})
        nu = n.get("uncertainty", {})
        row = {
            "module_name": nm,
            "baseline": {
                "pairwise_log_loss": bp["pairwise_log_loss"],
                "pairwise_accuracy": bp["pairwise_accuracy"],
                "spearman": bp["spearman"],
                "rank_mae": bp["rank_mae"],
                "raw_sigma_pi_trace_mean": bu.get("raw_sigma_pi_trace_mean"),
                "calibrated_sigma_pi_trace_mean": bu.get("calibrated_sigma_pi_trace_mean"),
            },
            "new": {
                "pairwise_log_loss": np_["pairwise_log_loss"],
                "pairwise_accuracy": np_["pairwise_accuracy"],
                "spearman": np_["spearman"],
                "rank_mae": np_["rank_mae"],
                "raw_sigma_pi_trace_mean": nu.get("raw_sigma_pi_trace_mean"),
                "calibrated_sigma_pi_trace_mean": nu.get("calibrated_sigma_pi_trace_mean"),
            },
            "delta_pairwise_log_loss": np_["pairwise_log_loss"] - bp["pairwise_log_loss"],
            "delta_pairwise_accuracy": np_["pairwise_accuracy"] - bp["pairwise_accuracy"],
        }
        if row["delta_pairwise_log_loss"] > 1e-6:
            regressions.append(nm)
        module_rows.append(row)

    def unc_module_map(payload: dict) -> dict[str, dict]:
        mods = payload.get("modules") or []
        return {m["module_name"]: m for m in mods if isinstance(m, dict) and "module_name" in m}

    b_unc_map = unc_module_map(baseline_unc)
    n_unc_map = unc_module_map(new_unc)
    sigma_rows = []
    for nm in sorted(set(b_unc_map) | set(n_unc_map)):
        bmod = b_unc_map.get(nm, {})
        nmod = n_unc_map.get(nm, {})
        btrace = bmod.get("sigma_pi_trace_dynamic_range") or {}
        ntrace = nmod.get("sigma_pi_trace_dynamic_range") or {}
        bc = (bmod.get("correlations") or {})
        nc = (nmod.get("correlations") or {})
        sigma_rows.append(
            {
                "module_name": nm,
                "baseline_sigma_pi_trace_range": btrace,
                "new_sigma_pi_trace_range": ntrace,
                "baseline_corr_sigma_pi_trace_vs_log_loss": bc.get("corr_sigma_pi_trace_vs_log_loss"),
                "new_corr_sigma_pi_trace_vs_log_loss": nc.get("corr_sigma_pi_trace_vs_log_loss"),
                "baseline_corr_sigma_pi_trace_vs_brier": bc.get("corr_sigma_pi_trace_vs_brier"),
                "new_corr_sigma_pi_trace_vs_brier": nc.get("corr_sigma_pi_trace_vs_brier"),
            }
        )

    payload = {
        "baseline_summary": str(BASELINE_SUMMARY.relative_to(ROOT)),
        "new_summary": str(NEW_SUMMARY.relative_to(ROOT)),
        "baseline_lambda_sigma_nll": baseline["run_config"].get("lambda_sigma_nll"),
        "new_lambda_sigma_nll": new["run_config"].get("lambda_sigma_nll"),
        "new_pairwise_sigma_nll_enabled": new["run_config"].get("pairwise_sigma_nll_enabled"),
        "pairwise_log_loss_regressions": regressions,
        "module_comparison": module_rows,
        "sigma_diagnostics": sigma_rows,
        "baseline_unc_summary": baseline_unc.get("summary"),
        "new_unc_summary": new_unc.get("summary"),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {OUT}")
    print(f"Regressions (higher log loss): {regressions or 'none'}")
    improved = sum(1 for r in module_rows if r["delta_pairwise_log_loss"] < -1e-6)
    print(f"Improved modules: {improved}/12")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
