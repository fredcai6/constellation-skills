#!/usr/bin/env python3
"""Compare G5 gold cycle vs baseline (Brier-primary + pairwise log-loss)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BASELINE = "gold_cycle_260530_042533_2018thru2024"
OUT = ROOT / ".agent-work/sigma-calibration-followups/evidence/g5-metrics-comparison.json"
# Task-pooled Brier deltas below this are treated as retrain noise (G5 gate).
BRIER_MATERIAL_THRESHOLD = 0.001


def load_summary(slug: str) -> dict:
    path = ROOT / "reports/evo" / f"{slug}.summary.json"
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def load_unc(slug_prefix: str) -> dict:
    report_dir = ROOT / "reports/evo"
    matches = sorted(report_dir.glob(f"unc_diag_*{slug_prefix.split('_', 2)[-1]}*.json"))
    if not matches:
        # try exact slug from gold_cycle timestamp portion
        for p in sorted(report_dir.glob("unc_diag_*.json"), reverse=True):
            if slug_prefix.replace("gold_cycle_", "") in p.name:
                return json.loads(p.read_text(encoding="utf-8"))
        return {}
    return json.loads(matches[-1].read_text(encoding="utf-8"))


def task_brier_rows(summary: dict) -> dict[str, dict]:
    diag = summary.get("task_calibration_diagnostics") or {}
    out: dict[str, dict] = {}
    for task in ("quali", "race_start", "race"):
        sm = (diag.get(task) or {}).get("slice_metrics") or {}
        out[task] = {
            "mean_brier_score": sm.get("mean_brier_score"),
            "mean_pairwise_log_loss": sm.get("mean_pairwise_log_loss"),
            "corr_sigma_pi_trace_vs_brier": sm.get("corr_sigma_pi_trace_vs_brier"),
        }
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", default=DEFAULT_BASELINE)
    parser.add_argument("--new", required=True, help="New gold_cycle slug (no extension)")
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()

    baseline = load_summary(args.baseline)
    new = load_summary(args.new)
    baseline_unc = load_unc(args.baseline)
    new_unc = load_unc(args.new)

    module_rows = []
    regressions_ll = []
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
            regressions_ll.append(nm)
        module_rows.append(row)

    b_tasks = task_brier_rows(baseline)
    n_tasks = task_brier_rows(new)
    brier_regressions = []
    brier_rows = []
    for task in ("quali", "race_start", "race"):
        bb = b_tasks.get(task, {}).get("mean_brier_score")
        nb = n_tasks.get(task, {}).get("mean_brier_score")
        delta = None
        if bb is not None and nb is not None:
            delta = nb - bb
            if delta is not None and delta > BRIER_MATERIAL_THRESHOLD:
                brier_regressions.append(task)
        brier_rows.append(
            {
                "task": task,
                "baseline": b_tasks.get(task),
                "new": n_tasks.get(task),
                "delta_mean_brier_score": delta,
            }
        )

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
        bc = bmod.get("correlations") or {}
        nc = nmod.get("correlations") or {}
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

    race_start_unc = sigma_rows
    rs = next((r for r in race_start_unc if r["module_name"] == "driver_race_start_power_from_race_weekend"), {})

    payload = {
        "baseline_slug": args.baseline,
        "new_slug": args.new,
        "baseline_summary": f"reports/evo/{args.baseline}.summary.json",
        "new_summary": f"reports/evo/{args.new}.summary.json",
        "baseline_schema_version": baseline.get("schema_version"),
        "new_schema_version": new.get("schema_version"),
        "baseline_lambda_sigma_nll": baseline["run_config"].get("lambda_sigma_nll"),
        "new_lambda_sigma_nll": new["run_config"].get("lambda_sigma_nll"),
        "new_pairwise_sigma_nll_enabled": new["run_config"].get("pairwise_sigma_nll_enabled"),
        "pairwise_log_loss_regressions": regressions_ll,
        "brier_primary": {
            "task_comparison": brier_rows,
            "brier_regressions": brier_regressions,
            "verdict": "pass" if not brier_regressions else "fail",
        },
        "race_start_driver_weekend": rs,
        "module_comparison": module_rows,
        "sigma_diagnostics": sigma_rows,
        "baseline_unc_summary": baseline_unc.get("summary"),
        "new_unc_summary": new_unc.get("summary"),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {args.out}")
    print(f"Brier regressions: {brier_regressions or 'none'}")
    print(f"Log-loss regressions: {regressions_ll or 'none'}")
    return 1 if brier_regressions else 0


if __name__ == "__main__":
    raise SystemExit(main())
