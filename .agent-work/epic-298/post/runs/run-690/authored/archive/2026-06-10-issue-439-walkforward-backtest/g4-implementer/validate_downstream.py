"""Real cheap end-to-end validation of the FIXED _run_downstream (#439, g4).

No training. Reuses the EXISTING promoted-gold gold-cycle artifacts in reports/evo/ as a
stand-in "period": copies the gold summary/details/sampled_runtime_manifest into a temp
period report dir and the unc_cal into its calibration dir, then drives the real
SubprocessPipeline._run_downstream for a 2-race synthetic period (rounds 1-2). This runs the
real fusion-training, assemble-trained-manifest, and sampled-runtime-comparison subprocesses
(cheap vs the multi-hour gold cycle) and proves:

  1. the comparison produces a *.trained.json with per_race position_distribution for the
     requested rounds, and
  2. the comparison summary's run_config records the EXPLICIT PERIOD trained/default
     manifest paths (under the temp period dir) — NOT the promoted-gold global discovery.

Everything is written under a temp dir; no committed reports/evo or params/gold writes.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

from src.evo_predictor.walkforward.periods import WALKFORWARD_TRAIN_YEARS
from src.evo_predictor.walkforward.pipeline import PeriodPaths, SubprocessPipeline
from src.evo_predictor.walkforward.periods import Period

REPO = Path(__file__).resolve().parents[3]
GOLD_SLUG = "gold_cycle_260608_043414_2018thru2024"
UNC_CAL = "unc_cal_260608_043414_2018thru2024.json"


def _two_race_period() -> Period:
    """A synthetic period that predicts only rounds 1-2 (cheap) but is otherwise real.

    cutoff/train_max/prior_through are not exercised by _run_downstream (it reads
    eval_round_range + train_years only); set to safe values.
    """
    return Period(
        index=1, label="PVAL", cutoff=0, eval_round_range=(1, 2),
        reuse_promoted_gold=False, train_max_round=0, prior_through_round=0,
        train_years=list(WALKFORWARD_TRAIN_YEARS),
    )


def _seed_period_with_promoted_gold(paths: PeriodPaths) -> None:
    src_reports = REPO / "reports" / "evo"
    paths.report_dir.mkdir(parents=True, exist_ok=True)
    paths.calibration_dir.mkdir(parents=True, exist_ok=True)
    for suffix in ("summary.json", "details.json", "sampled_runtime_manifest.json"):
        shutil.copy2(
            src_reports / f"{GOLD_SLUG}.{suffix}",
            paths.report_dir / f"{GOLD_SLUG}.{suffix}",
        )
    shutil.copy2(
        REPO / "params" / "gold" / "uncertainty_calibration" / UNC_CAL,
        paths.calibration_dir / UNC_CAL,
    )


def main() -> int:
    period = _two_race_period()
    work_root = Path(tempfile.mkdtemp(prefix="wf_g4_val_"))
    print(f"[validate] temp work_root = {work_root}")
    paths = PeriodPaths.for_period(period, work_root=work_root)
    _seed_period_with_promoted_gold(paths)

    # Point the period prior root at the committed gold compound priors (read-only). The
    # comparison needs train-year + eval-year (2025) priors; promoted gold has all of them.
    object.__setattr__(paths, "prior_root", REPO / "params" / "gold" / "compound_prior")

    pipe = SubprocessPipeline(db_root=REPO / "data")
    trained_path = pipe._run_downstream(period, paths, utilization="background")
    print(f"[validate] trained result = {trained_path}")

    trained = json.loads(Path(trained_path).read_text(encoding="utf-8"))
    per_race = trained.get("per_race") or []
    rounds = sorted(r.get("round_num") for r in per_race if isinstance(r, dict))
    print(f"[validate] per_race rounds = {rounds}")
    has_dist = {
        r["round_num"]: bool(
            isinstance(r.get("prediction"), dict)
            and isinstance(r["prediction"].get("position_distribution"), dict)
            and r["prediction"]["position_distribution"]
        )
        for r in per_race
        if isinstance(r, dict)
    }
    print(f"[validate] round -> has position_distribution = {has_dist}")

    # The comparison summary records which manifests it actually consumed. run_comparison
    # appends reports/evo under --output-dir unless the dir's name is literally "evo"; here
    # --output-dir is the period report dir (name "reports"), so it lands one level deeper.
    summary = json.loads(
        SubprocessPipeline._only(
            paths.report_dir / "reports" / "evo", "rt_comparison_*.summary.json"
        ).read_text(encoding="utf-8")
    )
    run_config = summary["run_config"]
    default_manifest = run_config["default_manifest"]
    trained_manifest = run_config["trained_manifest"]
    print(f"[validate] run_config.default_manifest = {default_manifest}")
    print(f"[validate] run_config.trained_manifest = {trained_manifest}")

    period_dir_posix = paths.report_dir.resolve().as_posix()
    checks = {
        "both_rounds_present": rounds == [1, 2],
        "both_rounds_have_distribution": all(has_dist.get(r) for r in (1, 2)),
        "default_manifest_is_period_local": period_dir_posix in Path(default_manifest).resolve().as_posix(),
        "trained_manifest_is_period_local": period_dir_posix in Path(trained_manifest).resolve().as_posix(),
        "trained_manifest_is_fusion": Path(trained_manifest).name.startswith("fusion_"),
        "not_promoted_gold_global": "reports/evo/gold_cycle_260608_043414" not in Path(trained_manifest).as_posix(),
    }
    print("[validate] CHECKS:")
    for name, ok in checks.items():
        print(f"   {'PASS' if ok else 'FAIL'}  {name}")

    all_ok = all(checks.values())
    print(f"[validate] RESULT = {'ALL PASS' if all_ok else 'FAILURES PRESENT'}")
    # Leave the temp dir for inspection; print path so the caller can clean up.
    print(f"[validate] (temp dir retained: {work_root})")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
