"""G4-A: Student-t nu sensitivity on two driver weekend modules (smoke budget)."""

from __future__ import annotations

import json
from pathlib import Path

from g4_common import (
    EPOCHS,
    EVAL_YEAR,
    TRAIN_YEARS,
    prepare_smoke_batches,
    train_smoke_module,
    write_evidence,
)

NU_VALUES = [2, 3, 4, 6, 8]
BASELINE_NU = 4.0
MODULES = (
    "driver_race_start_power_from_race_weekend",
    "driver_quali_power_from_race_weekend",
)


def _verdict(module_rows: dict[str, list[dict]], baseline: dict) -> dict[str, object]:
    """Pick recommendation from sweep deltas vs nu=4."""
    keep_shared = True
    rationale: list[str] = []
    best_alt: float | None = None

    for module_name, runs in module_rows.items():
        base = next((r for r in runs if r.get("nu") == BASELINE_NU and r.get("status") == "ok"), None)
        if base is None:
            rationale.append(f"{module_name}: missing nu=4 baseline run")
            continue
        base_p95 = base["uncertainty_diagnostics"].get("r_over_sigma_p95")
        base_sigma_std = base["pairwise_arrays"].get("sigma_std")
        base_supervised = base["pairwise_metrics"].get("supervised_nll")
        for run in runs:
            if run.get("status") != "ok" or run.get("nu") == BASELINE_NU:
                continue
            nu = float(run["nu"])
            p95 = run["uncertainty_diagnostics"].get("r_over_sigma_p95")
            sigma_std = run["pairwise_arrays"].get("sigma_std")
            supervised = run["pairwise_metrics"].get("supervised_nll")
            if base_supervised is not None and supervised is not None:
                delta_sup = float(supervised) - float(base_supervised)
                if abs(delta_sup) > 0.02:
                    rationale.append(
                        f"{module_name} nu={nu}: supervised_nll delta vs nu=4 = {delta_sup:+.4f} "
                        "(nu changes dropped Student-t constants — interpret shape metrics first)"
                    )
            if base_p95 is not None and p95 is not None and abs(float(p95) - float(base_p95)) > 0.15:
                rationale.append(
                    f"{module_name} nu={nu}: |r/sigma| p95 {p95:.3f} vs baseline {base_p95:.3f}"
                )
            if (
                base_sigma_std is not None
                and sigma_std is not None
                and float(sigma_std) > float(base_sigma_std) * 1.25
            ):
                rationale.append(
                    f"{module_name} nu={nu}: per-pair sigma_std {sigma_std:.4f} "
                    f"vs baseline {base_sigma_std:.4f}"
                )

    # Recommend change only if one non-4 nu clearly wins on BOTH modules' tail + sigma spread
    candidates: dict[float, int] = {}
    for module_name, runs in module_rows.items():
        base = next((r for r in runs if r.get("nu") == BASELINE_NU and r.get("status") == "ok"), None)
        if base is None:
            continue
        base_p99 = base["uncertainty_diagnostics"].get("r_over_sigma_p99")
        base_std = base["pairwise_arrays"].get("sigma_std")
        for run in runs:
            if run.get("status") != "ok":
                continue
            nu = float(run["nu"])
            if nu == BASELINE_NU:
                continue
            p99 = run["uncertainty_diagnostics"].get("r_over_sigma_p99")
            std = run["pairwise_arrays"].get("sigma_std")
            if base_p99 is None or p99 is None or base_std is None or std is None:
                continue
            if float(std) >= float(base_std) and float(p99) <= float(base_p99) * 1.05:
                candidates[nu] = candidates.get(nu, 0) + 1

    # Require meaningful tail improvement (>3% p99 drop) on BOTH modules to override ν=4.
    strong: dict[float, int] = {}
    for module_name, runs in module_rows.items():
        base = next((r for r in runs if r.get("nu") == BASELINE_NU and r.get("status") == "ok"), None)
        if base is None:
            continue
        base_p99 = base["uncertainty_diagnostics"].get("r_over_sigma_p99")
        if base_p99 is None:
            continue
        for run in runs:
            if run.get("status") != "ok":
                continue
            nu = float(run["nu"])
            if nu == BASELINE_NU:
                continue
            p99 = run["uncertainty_diagnostics"].get("r_over_sigma_p99")
            if p99 is None:
                continue
            if float(p99) <= float(base_p99) * 0.97:
                strong[nu] = strong.get(nu, 0) + 1
    if strong:
        best_alt = max(strong.items(), key=lambda item: item[1])[0]
        if strong[best_alt] >= 2:
            keep_shared = False
            candidates = strong

    if keep_shared:
        verdict = "keep_shared_nu_4"
        g5 = {
            "student_t_nu": 4.0,
            "student_t_nu_sigma": None,
            "note": "No smoke sweep showed consistent improvement on both modules; keep G3 defaults.",
        }
    else:
        verdict = "recommend_single_bounded_nu"
        g5 = {
            "student_t_nu": best_alt,
            "student_t_nu_sigma": None,
            "note": f"Smoke favored nu={best_alt} on both modules (tail+sigma_std); confirm on G5 gold.",
        }

    return {
        "verdict": verdict,
        "keep_shared_nu_4": keep_shared,
        "recommended_student_t_nu": g5["student_t_nu"],
        "recommended_student_t_nu_sigma": g5["student_t_nu_sigma"],
        "g5_recommendation": g5,
        "rationale": rationale,
        "triage_followup": (
            "per_phase_scope_nu_tuning"
            if any(
                module_rows[m][0].get("status") == "ok"
                and len({r["nu"] for r in module_rows[m] if r.get("status") == "ok"}) >= 3
                for m in MODULES
            )
            else None
        ),
        "adr_note": (
            "Student-t NLL drops nu-only constants; supervised_nll deltas across nu are not "
            "directly comparable — use |r/sigma| percentiles and per-pair sigma_std."
        ),
    }


def main() -> None:
    module_rows: dict[str, list[dict]] = {}
    for module_name in MODULES:
        prepared, train_batches, eval_batches = prepare_smoke_batches(module_name)
        runs: list[dict] = []
        for nu in NU_VALUES:
            row: dict = {"module_name": module_name, "nu": nu}
            if nu <= 2.0:
                row["status"] = "skipped"
                row["error"] = "LatentPowerConfig requires student_t_nu > 2"
                runs.append(row)
                continue
            try:
                result = train_smoke_module(
                    prepared,
                    train_batches,
                    eval_batches,
                    student_t_nu=float(nu),
                    lambda_sigma_nll=1.0,
                )
                row["status"] = "ok"
                row.update(result)
                if nu != BASELINE_NU:
                    base = next((r for r in runs if r.get("nu") == BASELINE_NU and r.get("status") == "ok"), None)
                    if base is not None:
                        sup = row["pairwise_metrics"].get("supervised_nll")
                        base_sup = base["pairwise_metrics"].get("supervised_nll")
                        if sup is not None and base_sup is not None:
                            row["delta_supervised_nll_vs_nu4"] = float(sup) - float(base_sup)
                runs.append(row)
            except Exception as exc:  # noqa: BLE001 — evidence script
                row["status"] = "error"
                row["error"] = str(exc)
                runs.append(row)
        module_rows[module_name] = runs

    verdict = _verdict(module_rows, {})
    payload = {
        "gate": "G4-A",
        "issue": "#304",
        "train_years": TRAIN_YEARS,
        "eval_year": EVAL_YEAR,
        "epochs": EPOCHS,
        "nu_values_requested": NU_VALUES,
        "nu_values_ran": [n for n in NU_VALUES if n > 2.0],
        "modules": list(MODULES),
        "module_runs": module_rows,
        **verdict,
    }

    md_lines = [
        "# G4-A — Student-t ν sensitivity (smoke)",
        "",
        f"**Train/eval:** {TRAIN_YEARS} → {EVAL_YEAR}, **epochs:** {EPOCHS}, **λ_sigma_nll:** 1.0",
        "",
        f"**Verdict:** `{verdict['verdict']}`",
        "",
        f"**G5 recommendation:** `student_t_nu={verdict['g5_recommendation']['student_t_nu']}`, "
        f"`student_t_nu_sigma={verdict['g5_recommendation']['student_t_nu_sigma']}`",
        "",
        verdict["g5_recommendation"]["note"],
        "",
    ]
    if verdict["rationale"]:
        md_lines.append("## Observations")
        for line in verdict["rationale"]:
            md_lines.append(f"- {line}")
        md_lines.append("")

    md_lines.append("## Per-module sweep")
    for module_name, runs in module_rows.items():
        md_lines.append(f"### {module_name}")
        md_lines.append("| ν | status | p50 | p95 | p99 | σ_std | corr(σ,nll) | Δ sup vs ν=4 |")
        md_lines.append("|---:|---|---:|---:|---:|---:|---:|---:|")
        for run in runs:
            nu = run.get("nu")
            status = run.get("status")
            if status != "ok":
                md_lines.append(f"| {nu} | {status} | — | — | — | — | — | — |")
                continue
            ud = run["uncertainty_diagnostics"]
            pa = run["pairwise_arrays"]
            delta = run.get("delta_supervised_nll_vs_nu4")
            md_lines.append(
                f"| {nu} | ok | {ud.get('r_over_sigma_p50', '—'):.3f} | "
                f"{ud.get('r_over_sigma_p95', '—'):.3f} | {ud.get('r_over_sigma_p99', '—'):.3f} | "
                f"{pa.get('sigma_std', 0):.4f} | {pa.get('corr_sigma_per_pair_nll_pearson', '—')} | "
                f"{delta if delta is not None else '—'} |"
            )
        md_lines.append("")

    if verdict.get("triage_followup"):
        md_lines.append(
            f"**Triage:** deeper per-(phase,scope) ν tuning flagged as `{verdict['triage_followup']}`."
        )

    write_evidence("g4-nu-sweep", payload, "\n".join(md_lines))
    print(json.dumps({"verdict": verdict["verdict"], "g5": verdict["g5_recommendation"]}, indent=2))


if __name__ == "__main__":
    main()
