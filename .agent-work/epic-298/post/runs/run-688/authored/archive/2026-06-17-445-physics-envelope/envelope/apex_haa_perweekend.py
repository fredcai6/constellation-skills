"""HAA tell, part 2: dissect the per-weekend frontier fit that makes HAA read #1.

The season feature averages PER-WEEKEND B*vref^2. The pooled-season fit instead
shows HAA with the LOWEST v^2 slope. So HAA's #1 ranking is created by the
per-weekend shared-A fit. Diagnose:
  - HAA's B*vref^2 per weekend vs RBR's  (is it a few outlier weekends?)
  - the fitted intercept A per weekend (shared) and HAA's node coverage:
    does HAA lack high-speed nodes, so its B is set by extrapolating a steep slope
    from a short low-speed lever arm? -> high B that doesn't reflect achieved grip.
  - apex-speed RANGE per car per weekend: HAA may corner only at low speed (few
    fast corners reached), inflating the per-weekend slope estimate.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

import aniso_fit  # noqa: E402
from season_prior_filter import fit_weekend, VREF, GSAT  # noqa: E402

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
aniso_fit.CACHE = OUT / "calibrated_aniso_nodes.npz"


def main():
    per = aniso_fit.load()
    print("Per-weekend lateral-apex frontier: HAA vs RBR")
    print(f"{'round':>14} | {'HAA B*vref2':>11} {'HAA vmax':>9} {'HAA n':>6} | "
          f"{'RBR B*vref2':>11} {'RBR vmax':>9} {'RBR n':>6} | {'A_shared':>8}")
    haa_b, rbr_b, haa_vmax, rbr_vmax = [], [], [], []
    for rname, cl in per:
        cl_ = aniso_fit.clouds_lat(cl)
        cl_ = {c: v for c, v in cl_.items() if len(v[0]) >= 24}
        if len(cl_) < 4:
            continue
        A, B = fit_weekend(cl_)
        # team B = mean of drivers
        def teamB(drvs):
            vals = [B[c] * VREF * VREF for c in drvs if c in B]
            return np.mean(vals) if vals else np.nan
        def teamvmax(drvs):
            vs = [cl_[c][0].max() * 3.6 for c in drvs if c in cl_]
            return np.max(vs) if vs else np.nan
        def teamn(drvs):
            return sum(len(cl_[c][0]) for c in drvs if c in cl_)
        hb = teamB(["MAG", "HUL"]); rb = teamB(["VER", "PER"])
        hv = teamvmax(["MAG", "HUL"]); rv = teamvmax(["VER", "PER"])
        hn = teamn(["MAG", "HUL"]); rn = teamn(["VER", "PER"])
        if np.isfinite(hb) and np.isfinite(rb):
            haa_b.append(hb); rbr_b.append(rb)
            haa_vmax.append(hv); rbr_vmax.append(rv)
        print(f"{rname:>14} | {hb:11.3f} {hv:9.0f} {hn:6d} | "
              f"{rb:11.3f} {rv:9.0f} {rn:6d} | {A:8.2f}")

    print(f"\n  season-mean HAA B*vref2 = {np.nanmean(haa_b):.3f}  "
          f"(median {np.nanmedian(haa_b):.3f})")
    print(f"  season-mean RBR B*vref2 = {np.nanmean(rbr_b):.3f}  "
          f"(median {np.nanmedian(rbr_b):.3f})")
    print(f"\n  HAA highest-apex-speed reached (season max): {np.nanmax(haa_vmax):.0f} km/h")
    print(f"  RBR highest-apex-speed reached (season max): {np.nanmax(rbr_vmax):.0f} km/h")
    print(f"  HAA mean per-weekend vmax: {np.nanmean(haa_vmax):.0f} km/h")
    print(f"  RBR mean per-weekend vmax: {np.nanmean(rbr_vmax):.0f} km/h")

    # The mechanism: where on the v^2 axis is each car's lever arm?
    print("\n  KEY: B is the slope of g vs v^2. A short, low-speed lever arm makes")
    print("  the slope estimate noisy/inflated. Compare each car's apex-speed span:")
    haa_v, rbr_v = [], []
    for rname, cl in per:
        cl_ = aniso_fit.clouds_lat(cl)
        for c in ["MAG", "HUL"]:
            if c in cl_:
                haa_v.append(cl_[c][0] * 3.6)
        for c in ["VER", "PER"]:
            if c in cl_:
                rbr_v.append(cl_[c][0] * 3.6)
    haa_v = np.concatenate(haa_v); rbr_v = np.concatenate(rbr_v)
    print(f"    HAA apex-speed dist: p10 {np.percentile(haa_v,10):.0f}  "
          f"p50 {np.percentile(haa_v,50):.0f}  p90 {np.percentile(haa_v,90):.0f}  "
          f"p99 {np.percentile(haa_v,99):.0f} km/h")
    print(f"    RBR apex-speed dist: p10 {np.percentile(rbr_v,10):.0f}  "
          f"p50 {np.percentile(rbr_v,50):.0f}  p90 {np.percentile(rbr_v,90):.0f}  "
          f"p99 {np.percentile(rbr_v,99):.0f} km/h")


if __name__ == "__main__":
    main()
