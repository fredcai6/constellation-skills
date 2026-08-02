"""HAA tell: WHY does Haas read high cornering frontier-g but go slow? (#445)

Three diagnostics on the clean calibrated cornering nodes:

(1) WHERE in speed does HAA's grip live? Compare the per-car lateral-apex frontier
    G_lat(v) = A + B*v^2 across the speed range. If HAA's edge is only at HIGH speed
    (where grip doesn't set corner time the way low-speed mechanical grip + traction
    do), the frontier number overstates pace relevance.

(2) APEX-SPEED node distribution: at matched corner SPEED bins, does HAA actually
    reach the same lateral g as RBR — or does HAA's "high B" come from a steeper v^2
    slope fit that is dominated by a few high-speed nodes? Look at the low-speed
    (mechanical-grip) regime specifically.

(3) Friction-circle USE: peak lateral g is grip CEILING. Lap time needs that grip
    converted to SPEED. v_apex = sqrt(a_lat * R). For the SAME corner radius, the
    car with higher usable a_lat AT THAT SPEED is faster. Check whether HAA's grip
    advantage is at radii/speeds that matter.

Compares HAA (MAG/HUL) vs RBR (VER/PER) pooled across the season on clean nodes.
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
DRV2TEAM = aniso_fit.DRV2TEAM


def pool_lateral_nodes(cars):
    """Pool near-apex pure-lateral nodes across all rounds for a set of cars."""
    per = aniso_fit.load()
    v_all, g_all = [], []
    for rname, cl in per:
        cl_ = aniso_fit.clouds_lat(cl)
        for c in cars:
            if c in cl_:
                v, g, w = cl_[c]
                v_all.append(v); g_all.append(g)
    return np.concatenate(v_all), np.concatenate(g_all)


def upper_quantile_curve(v, g, edges, q=0.90):
    """Upper-q lateral-g per speed bin = the achieved-grip frontier shape."""
    mids, ceil, n = [], [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (v >= lo) & (v < hi)
        if m.sum() < 15:
            continue
        mids.append(0.5 * (lo + hi))
        ceil.append(np.quantile(g[m], q))
        n.append(int(m.sum()))
    return np.array(mids), np.array(ceil), np.array(n)


def main():
    print("=" * 74)
    print("HAA TELL — where Haas's cornering grip lives (clean calibrated nodes)")
    print("=" * 74)

    teams = {"HAA": ["MAG", "HUL"], "RBR": ["VER", "PER"],
             "FER": ["LEC", "SAI"], "MERC": ["HAM", "RUS"]}
    pools = {t: pool_lateral_nodes(cars) for t, cars in teams.items()}

    # (1) achieved lateral-g frontier curve by speed bin
    edges = np.array([15, 22, 30, 38, 47, 58, 70, 85, 110, 160]) / 1.0  # m/s
    print("\n(1) ACHIEVED lateral-g frontier (90th pct) by APEX SPEED bin:")
    print(f"  speed bin (km/h):  " +
          " ".join(f"{(0.5*(edges[i]+edges[i+1]))*3.6:5.0f}" for i in range(len(edges)-1)))
    curves = {}
    for t in ["RBR", "HAA", "FER", "MERC"]:
        v, g = pools[t]
        mids, ceil, n = upper_quantile_curve(v, g, edges)
        curves[t] = (mids, ceil)
        # align to all bins
        row = []
        bmids = np.array([0.5 * (edges[i] + edges[i+1]) for i in range(len(edges)-1)])
        for bm in bmids:
            k = np.argmin(np.abs(mids - bm)) if len(mids) else None
            if k is not None and abs(mids[k] - bm) < 1e-6:
                row.append(f"{ceil[k]:5.2f}")
            else:
                row.append("   --")
        print(f"  {t:>4} g_lat ceil:    " + " ".join(row))

    # HAA vs RBR delta by speed
    print("\n  HAA - RBR achieved g_lat by speed (positive = HAA grippier):")
    mR, cR = curves["RBR"]; mH, cH = curves["HAA"]
    common = np.intersect1d(np.round(mR, 3), np.round(mH, 3))
    for cm in common:
        iR = np.argmin(np.abs(mR - cm)); iH = np.argmin(np.abs(mH - cm))
        d = cH[iH] - cR[iR]
        flag = "HAA grippier" if d > 0.03 else ("RBR grippier" if d < -0.03 else "~tie")
        print(f"    {cm*3.6:5.0f} km/h:  HAA {cH[iH]:.2f}  RBR {cR[iR]:.2f}  "
              f"Δ {d:+.2f}  [{flag}]")

    # (2) frontier fit slope/intercept: is HAA's edge in B (high-speed v^2) or A (low-speed)?
    print("\n(2) Per-team fitted frontier  G_lat(v) = A + B*v^2  (season-pooled):")
    print(f"  {'team':>4} {'A(g)':>7} {'B(1e-3)':>9} {'G@80kmh':>9} {'G@200kmh':>9}")
    for t in ["RBR", "HAA", "FER", "MERC"]:
        v, g = pools[t]
        A, Bd = fit_weekend({t: (v, g, np.ones_like(v))})
        B = Bd[t]
        g80 = min(A + B * (80/3.6)**2, GSAT)
        g200 = min(A + B * (200/3.6)**2, GSAT)
        print(f"  {t:>4} {A:7.2f} {B*1e3:9.3f} {g80:9.2f} {g200:9.2f}")
    print("  (A = LOW-SPEED mechanical grip intercept; B = high-speed downforce slope.")
    print("   If HAA's lead is all in B at 200km/h but it ties/loses at 80km/h, its")
    print("   'grip' is high-speed downforce that doesn't rescue slow corners.)")

    # (3) apex-speed-relevant view: a_lat at LOW speed (mechanical/traction-limited)
    print("\n(3) LOW-SPEED regime (<=130 km/h apex — mechanical/traction limited corners):")
    for t in ["RBR", "HAA"]:
        v, g = pools[t]
        m = v * 3.6 <= 130
        print(f"  {t}: {m.sum()} low-speed nodes, median g_lat {np.median(g[m]):.2f}, "
              f"90th {np.quantile(g[m], 0.9):.2f}")
    print("\n  HIGH-SPEED regime (>=180 km/h apex — downforce limited):")
    for t in ["RBR", "HAA"]:
        v, g = pools[t]
        m = v * 3.6 >= 180
        if m.sum() < 5:
            print(f"  {t}: {m.sum()} high-speed nodes (thin)")
            continue
        print(f"  {t}: {m.sum()} high-speed nodes, median g_lat {np.median(g[m]):.2f}, "
              f"90th {np.quantile(g[m], 0.9):.2f}")


if __name__ == "__main__":
    main()
