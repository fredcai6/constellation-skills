"""G4-B: Race-start corr flip investigation (driver_race_start_power_from_race_weekend)."""

from __future__ import annotations

import json

from g4_common import (
    EPOCHS,
    EVAL_YEAR,
    TRAIN_YEARS,
    eval_frozen_module,
    prepare_smoke_batches,
    train_smoke_module,
    try_load_promoted_module,
    write_evidence,
)

MODULE = "driver_race_start_power_from_race_weekend"
LAMBDA_VALUES = [0.0, 0.5, 1.0, 2.0]
ARCHIVE_G5_CORR = {
    "baseline_lambda_0": 0.1049386099458957,
    "promoted_lambda_1": -0.39739394214592483,
}


def _lambda_verdict(lambda_runs: list[dict], promoted_eval: dict | None) -> dict[str, object]:
    ok_runs = [r for r in lambda_runs if r.get("status") == "ok"]
    by_lambda = {float(r["lambda_sigma_nll"]): r for r in ok_runs}

    def corr_for(lam: float) -> float | None:
        row = by_lambda.get(lam)
        if row is None:
            return None
        return row.get("event_level", {}).get("correlations", {}).get("pearson")

    corr_0 = corr_for(0.0)
    corr_05 = corr_for(0.5)
    corr_1 = corr_for(1.0)
    corr_2 = corr_for(2.0)

    # Prefer positive corr with minimal supervised_nll penalty vs lambda=0 smoke
    best_lam = 1.0
    verdict = "flat_signal_artifact"
    rationale: list[str] = []

    if promoted_eval is None:
        rationale.append(
            "Promoted bundle weights not present locally; used archive G5 corr (+0.10 → −0.40) "
            "and smoke retrains for λ sweep."
        )
    else:
        pe = promoted_eval.get("event_level", {}).get("correlations", {})
        rationale.append(
            f"Promoted bundle event-level corr(σ_π,log_loss) pearson={pe.get('pearson')} "
            f"spearman={pe.get('spearman')}"
        )

    sigma_spread = []
    for lam, row in by_lambda.items():
        ev = row.get("event_level", {})
        events = ev.get("events") or []
        if events:
            traces = [float(e["sigma_pi_trace"]) for e in events]
            import numpy as np

            sigma_spread.append((lam, float(np.std(traces)), float(np.max(traces) - np.min(traces))))

    if sigma_spread:
        lam0_std = next((s for l, s, _ in sigma_spread if l == 0.0), None)
        rationale.append(
            f"σ_π trace spread across events (std): "
            + ", ".join(f"λ={l}:{s:.6f}" for l, s, _ in sigma_spread)
        )
        if lam0_std is not None and lam0_std < 5e-4:
            rationale.append("σ_π trace dynamic range is sub-mill — event-level Pearson is unstable.")

    # Verdict logic
    if corr_05 is not None and corr_0 is not None:
        if corr_05 > 0 and (corr_0 <= 0 or corr_05 > corr_0 + 0.15):
            verdict = "needs_lambda_tuning"
            best_lam = 0.5
            rationale.append(f"λ=0.5 restores positive corr ({corr_05:.3f}) vs λ=0 ({corr_0:.3f}).")
        elif corr_1 is not None and corr_1 < -0.25 and (corr_0 is None or abs(corr_0) < 0.2):
            verdict = "flat_signal_artifact"
            rationale.append(
                "λ=1 smoke reproduces strong negative corr on tiny σ_π spread — consistent with "
                "G5 #306 flat-signal / aggregation artifact, not pairwise miscalibration."
            )
    if corr_2 is not None and corr_1 is not None and corr_2 < corr_1 - 0.1:
        rationale.append(f"λ=2 further degrades corr ({corr_2:.3f} vs λ=1 {corr_1:.3f}).")

    promoted_pearson = None
    if promoted_eval:
        promoted_pearson = promoted_eval.get("event_level", {}).get("correlations", {}).get("pearson")
    if promoted_pearson is not None and promoted_pearson < -0.3:
        loo = promoted_eval.get("event_level", {}).get("correlations", {})
        if loo.get("loo_spearman_mean") is not None and abs(loo["loo_spearman_mean"]) < 0.35:
            rationale.append(
                "LOO/Spearman on promoted eval are weaker than full-sample Pearson — outlier-driven flip."
            )

    if verdict == "needs_lambda_tuning":
        g5_lambda = best_lam
    else:
        g5_lambda = 1.0 if verdict == "flat_signal_artifact" else 1.0

    g5 = {
        "lambda_sigma_nll": g5_lambda,
        "student_t_nu": 4.0,
        "student_t_nu_sigma": None,
        "note": (
            "Keep repo-wide λ=1 unless human overrides after G5; race-start event-corr is misleading."
            if verdict == "flat_signal_artifact"
            else f"Consider λ={g5_lambda} for race-start only — needs scoped G5/human decision."
        ),
    }

    return {
        "verdict": verdict,
        "recommended_lambda_sigma_nll": g5_lambda,
        "g5_recommendation": g5,
        "rationale": rationale,
        "lambda_correlations": {
            str(lam): {
                "pearson": by_lambda[lam]["event_level"]["correlations"].get("pearson"),
                "spearman": by_lambda[lam]["event_level"]["correlations"].get("spearman"),
                "loo_pearson_mean": by_lambda[lam]["event_level"]["correlations"].get("loo_pearson_mean"),
            }
            for lam in by_lambda
        },
        "archive_g5_reference": ARCHIVE_G5_CORR,
    }


def main() -> None:
    prepared, train_batches, eval_batches = prepare_smoke_batches(MODULE)

    promoted_module, promoted_path = try_load_promoted_module(MODULE)
    promoted_eval = None
    if promoted_module is not None:
        promoted_eval = eval_frozen_module(
            promoted_module, eval_batches, label="promoted_bundle", nu=4.0
        )
        promoted_eval["manifest_path"] = promoted_path

    lambda_runs: list[dict] = []
    for lam in LAMBDA_VALUES:
        row = {"lambda_sigma_nll": lam}
        try:
            result = train_smoke_module(
                prepared,
                train_batches,
                eval_batches,
                student_t_nu=4.0,
                lambda_sigma_nll=float(lam),
            )
            row["status"] = "ok"
            row.update(result)
        except Exception as exc:  # noqa: BLE001
            row["status"] = "error"
            row["error"] = str(exc)
        lambda_runs.append(row)

    # Fresh smoke λ=1 for per-pair comparison (same as lam=1 run if ok)
    smoke_l1 = next((r for r in lambda_runs if r.get("lambda_sigma_nll") == 1.0 and r.get("status") == "ok"), None)

    verdict_block = _lambda_verdict(lambda_runs, promoted_eval)
    payload = {
        "gate": "G4-B",
        "issue": "#306",
        "module": MODULE,
        "train_years": TRAIN_YEARS,
        "eval_year": EVAL_YEAR,
        "epochs": EPOCHS,
        "lambda_values": LAMBDA_VALUES,
        "promoted_bundle_available": promoted_module is not None,
        "promoted_eval": promoted_eval,
        "lambda_sweep": lambda_runs,
        "smoke_lambda_1_pairwise": smoke_l1.get("pairwise_arrays") if smoke_l1 else None,
        **verdict_block,
    }

    md = [
        "# G4-B — Race-start σ correlation investigation",
        "",
        f"**Module:** `{MODULE}`",
        f"**Smoke:** {TRAIN_YEARS} → {EVAL_YEAR}, epochs={EPOCHS}",
        "",
        f"**Verdict:** `{verdict_block['verdict']}`",
        "",
        "**Archive G5 reference (full gold, not re-run):** "
        f"λ=0 corr={ARCHIVE_G5_CORR['baseline_lambda_0']:.3f}, "
        f"λ=1 corr={ARCHIVE_G5_CORR['promoted_lambda_1']:.3f}",
        "",
        f"**G5 recommendation:** λ_sigma_nll={verdict_block['g5_recommendation']['lambda_sigma_nll']}, "
        f"student_t_nu={verdict_block['g5_recommendation']['student_t_nu']}",
        "",
        verdict_block["g5_recommendation"]["note"],
        "",
    ]
    if verdict_block["rationale"]:
        md.append("## Findings")
        for line in verdict_block["rationale"]:
            md.append(f"- {line}")
        md.append("")

    md.append("## λ sweep (smoke retrain)")
    md.append("| λ | pearson | spearman | LOO pearson μ | σ_pair std (median event) |")
    md.append("|---:|---:|---:|---:|---:|")
    for run in lambda_runs:
        lam = run.get("lambda_sigma_nll")
        if run.get("status") != "ok":
            md.append(f"| {lam} | {run.get('status')} | — | — | — |")
            continue
        c = run["event_level"]["correlations"]
        events = run["event_level"]["events"]
        med_sigma_std = None
        if events:
            import numpy as np

            med_sigma_std = float(np.median([e["sigma_pair_std"] for e in events]))
        md.append(
            f"| {lam} | {c.get('pearson', '—')} | {c.get('spearman', '—')} | "
            f"{c.get('loo_pearson_mean', '—')} | {med_sigma_std if med_sigma_std is not None else '—'} |"
        )
    md.append("")

    if promoted_eval:
        c = promoted_eval["event_level"]["correlations"]
        pa = promoted_eval["pairwise_arrays"]
        md.append("## Promoted bundle (no-train eval)")
        md.append(
            f"- corr(σ_π, log_loss): pearson={c.get('pearson')}, spearman={c.get('spearman')}"
        )
        md.append(
            f"- per-pair: σ_std={pa.get('sigma_std')}, |r| median={pa.get('abs_r_median')}, "
            f"p95 |r/σ|={pa.get('r_over_sigma_p95')}"
        )
        md.append("")
    else:
        md.append("## Promoted bundle")
        md.append("- Not available in worktree; smoke λ=0 vs λ=1 used as proxy.")
        md.append("")

    write_evidence("g4-racestart", payload, "\n".join(md))
    print(
        json.dumps(
            {"verdict": verdict_block["verdict"], "g5": verdict_block["g5_recommendation"]},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
