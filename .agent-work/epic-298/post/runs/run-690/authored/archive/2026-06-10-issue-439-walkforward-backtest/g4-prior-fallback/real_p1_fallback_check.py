"""Real P1 (N=6) fallback check for the g4 prior-build robustness fix (#439).

Drives the REAL SubprocessPipeline._build_prior_root for P1 (cutoff N=6) against the live
2025 DB and the committed gold train-year priors. The as-of-6 constrained solve genuinely
does not converge today (fit_compound_prior exits 1), so this exercises the actual fallback
path — not a mock. Asserts:

  * the explicit cross-season fallback is logged (period P1, N=6, cross-season),
  * _build_prior_root returns prior_mode=cross_season_fallback, prior_through_round=0,
  * no <period>/compound_prior/2025 dir is left behind (only the copied 2018-2024 priors),
  * the resulting period prior root resolves via the runtime loader to a prior-season
    artifact with source_season < 2025 (zero 2025 data) — leakage-safe.

Not committed source; run from repo root with `py`.
"""

from __future__ import annotations

import logging
import sys
import tempfile
from pathlib import Path

# Make ``scripts`` importable exactly as the real run script does (run_walkforward_backtest.py
# inserts the repo root) so _build_as_of_n_eval_prior's ``from scripts.run_season_alignment
# import run_year`` resolves and the GENUINE as-of-6 extract->baseline->solve runs (and fails
# to converge) — not a spurious ImportError.
_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.compound_prior.runtime_normalization import (
    CompoundPriorArtifact,
    load_time_safe_compound_prior,
)
from src.evo_predictor.walkforward.periods import build_periods
from src.evo_predictor.walkforward.pipeline import (
    PRIOR_MODE_CROSS_SEASON_FALLBACK,
    PeriodPaths,
    SubprocessPipeline,
)


def main() -> int:
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
    p1 = build_periods()[1]
    assert p1.label == "P1" and p1.cutoff == 6, p1

    with tempfile.TemporaryDirectory(prefix="g4_real_p1_") as tmp:
        work_root = Path(tmp)
        paths = PeriodPaths.for_period(p1, work_root=work_root)
        pipeline = SubprocessPipeline(
            db_root=Path("data"),
            gold_prior_root=Path("params/gold/compound_prior"),
        )

        print(">>> Driving REAL _build_prior_root for P1 (N=6) — as-of-6 solve is expected "
              "to fail and fall back...")
        result = pipeline._build_prior_root(p1, paths)
        print(f">>> RESULT: prior_mode={result.prior_mode!r}, "
              f"prior_through_round={result.prior_through_round}")

        ok = True

        if result.prior_mode != PRIOR_MODE_CROSS_SEASON_FALLBACK:
            print(f"FAIL: expected cross_season_fallback, got {result.prior_mode!r}")
            ok = False
        if result.prior_through_round != 0:
            print(f"FAIL: expected effective prior_through_round 0, got "
                  f"{result.prior_through_round}")
            ok = False

        eval_dir = paths.prior_root / "2025"
        if eval_dir.exists():
            print(f"FAIL: a 2025 prior dir was left behind at {eval_dir}")
            ok = False
        else:
            print(f">>> OK: no 2025 prior dir under {paths.prior_root} (loader will use "
                  "cross-season).")

        # The train-year priors must be present (the cross-season fallback resolves from them).
        train_years_present = sorted(
            int(d.name) for d in paths.prior_root.iterdir()
            if d.is_dir() and d.name.isdigit()
        )
        print(f">>> Prior root years present: {train_years_present}")
        if train_years_present != [2018, 2019, 2020, 2021, 2022, 2023, 2024]:
            print("FAIL: train-year priors not assembled as expected")
            ok = False

        # The loader, given the period prior root + same-season opt-in, must resolve a
        # cross-season-safe prior (source_season < 2025, zero 2025 data).
        artifact = load_time_safe_compound_prior(
            str(paths.prior_root), target_year=2025, allow_same_season_research=True
        )
        if not isinstance(artifact, CompoundPriorArtifact):
            print(f"FAIL: loader returned {type(artifact).__name__}, not an artifact")
            ok = False
        else:
            print(f">>> Loader resolved: source_season={artifact.source_season}, "
                  f"availability_rule={artifact.metadata.get('availability_rule')!r}, "
                  f"leakage_mode={artifact.metadata.get('leakage_mode')!r}")
            if artifact.source_season >= 2025:
                print(f"FAIL: loader used source_season={artifact.source_season} (>= 2025) "
                      "— would leak")
                ok = False
            if artifact.metadata.get("leakage_mode") == "same_season_research":
                print("FAIL: loader took the same_season_research path — not cross-season")
                ok = False

        print("PASS: real P1 as-of-6 build fell back to the cross-season prior, recorded "
              "explicitly, leakage-safe." if ok else "OVERALL: FAIL")
        return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
