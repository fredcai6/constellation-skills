"""Corner-level apex curvature via circle-fit, vs scale (epic #445).

The POINTWISE a_lat ceiling is scale-dependent (Hermite/ell/W swing 15x). But a
CORNER is a physical unit: apex = speed minimum (measured, robust); fit a circle
to the position points in the apex region -> radius R (pools ~20-30 pts, the
'scale' is the corner extent, not an arbitrary window). a_lat_apex = v_apex^2 / R.

TEST: is per-corner apex a_lat stable across ell and across the fit window,
where the pointwise ceiling was not? If yes, the corner-level geometry is
recoverable and the broad 'scale-dependent dead end' claim was too broad.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
from scipy.signal import find_peaks

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

import harvest_envelope as H  # noqa: E402

G = 9.81


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def circle_fit(x, y):
    """Kasa algebraic circle fit. Returns radius R (m)."""
    A = np.column_stack([x, y, np.ones_like(x)])
    b = -(x**2 + y**2)
    try:
        sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    except Exception:
        return np.nan
    a, bb, c = sol
    cx, cy = -a / 2, -bb / 2
    r2 = cx**2 + cy**2 - c
    return float(np.sqrt(r2)) if r2 > 0 else np.nan


def corner_apexes(ss, v_corner=78.0, prom=8.0):
    """Smoothed nodes -> (t, X, Y, v, s) and apex indices (speed minima)."""
    mask = ss.kind == 1
    t = ss.ts[mask]
    order = np.argsort(t)
    t = t[order]
    keep = np.concatenate([[True], np.diff(t) > 1e-9])
    t = t[keep]
    X, Y = ss.pos_at(t)
    v = ss.speed_at(t)[0]
    s = np.concatenate([[0.0], np.cumsum(0.5 * (v[1:] + v[:-1]) * np.diff(t))])
    # apex = local speed minimum, prominence in m/s, only genuine corners (v low)
    idx, _ = find_peaks(-v, prominence=prom, distance=6)
    idx = idx[v[idx] < v_corner]
    return t, X, Y, v, s, idx


def apex_alat(ss, win_m=20.0):
    """Per-corner apex a_lat (=v^2/R) from a circle fit over +-win_m of arc."""
    t, X, Y, v, s, idx = corner_apexes(ss)
    out = []
    for i in idx:
        sel = np.abs(s - s[i]) <= win_m
        if sel.sum() < 6:
            continue
        R = circle_fit(X[sel], Y[sel])
        if not np.isfinite(R) or R < 5 or R > 2000:
            continue
        out.append((float(v[i]), R, float(v[i] ** 2 / R)))
    return out


def collect(runs, ell, sf, sig_pos, delta, win_m=20.0):
    rows = []
    for r in runs:
        try:
            ss = H.StintSmoother(ell, sf, sig_pos, delta, iters=2)
            ss.fit(r["tp"], r["X"], r["Y"], r["tc"], r["V"])
        except Exception:
            continue
        rows += apex_alat(ss, win_m=win_m)
    return rows


def summ(rows):
    if not rows:
        return None
    al = np.array([r[2] for r in rows])
    return dict(n=len(rows), med=float(np.median(al)), p90=float(np.percentile(al, 90)))


def main():
    log("loading 2023 Japan Q ...")
    session = H.load_session(2023, "Japan", "Q")
    runs = H.driver_runs(session, "VER")
    log(f"VER: {len(runs)} runs")
    delta, sf = 0.06, 100.0

    print("\n--- apex a_lat (=v_apex^2/R) stability across ell (win=20m) ---")
    print(f"{'ell':>5} | {'n':>4} {'median':>8} {'p90':>8}  (m/s^2 ; /9.81=g)")
    for ell in [1.2, 2.0, 3.0, 5.0]:
        sm = summ(collect(runs, ell, sf, 0.3, delta, 20.0))
        if sm:
            print(f"{ell:5.2f} | {sm['n']:4d} {sm['med']:8.1f} {sm['p90']:8.1f}  "
                  f"({sm['med']/G:.1f}g / {sm['p90']/G:.1f}g)")

    print("\n--- apex a_lat stability across fit window (ell=2.0) ---")
    print(f"{'win_m':>6} | {'n':>4} {'median':>8} {'p90':>8}")
    for w in [12.0, 20.0, 30.0, 45.0]:
        sm = summ(collect(runs, 2.0, sf, 0.3, delta, w))
        if sm:
            print(f"{w:6.0f} | {sm['n']:4d} {sm['med']:8.1f} {sm['p90']:8.1f}")

    print("\n--- per-corner detail (ell=2.0, win=20m): apex speed / R / a_lat ---")
    rows = sorted(collect(runs, 2.0, sf, 0.3, delta, 20.0), key=lambda r: r[0])
    print(f"{'v_apex(km/h)':>12} {'R(m)':>7} {'a_lat(g)':>9}")
    seen = set()
    for vmax, R, al in rows:
        key = round(vmax * 3.6 / 5) * 5
        if key in seen:
            continue
        seen.add(key)
        print(f"{vmax*3.6:12.0f} {R:7.0f} {al/G:9.2f}")


if __name__ == "__main__":
    main()
