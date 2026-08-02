"""Cubic-Hermite curvature vs windowed heading-regression (epic #445).

The windowed theta-vs-s regression has a free window W (the 'new ell'). A cubic
Hermite interpolant constrained by the solved (position, velocity) at each node
is PARAMETER-FREE: each segment's cubic is fixed by p_i,v_i,p_{i+1},v_{i+1}, and
curvature is read analytically:

    a_lat = |P' x P''| / |P'|,  P = CubicHermite(t; pos, vel)

Hermite is the W->0 endpoint. Compare its ceiling envelope to the windowed one
(W=2,4,8) and across ell. Agreement => W not biasing, both validated, and the
W-sensitivity question is closed.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
from scipy.interpolate import CubicHermiteSpline

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

import harvest_envelope as H  # noqa: E402


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def hermite_lat(ss):
    """a_lat from a cubic-Hermite interpolant on the solved (pos, vel). Param-free."""
    mask = ss.kind == 1
    t = ss.ts[mask]
    order = np.argsort(t)
    t = t[order]
    keep = np.concatenate([[True], np.diff(t) > 1e-9])
    t = t[keep]
    if len(t) < 4:
        return None
    X, Y = ss.pos_at(t)
    Xd, Yd = ss.vel_at(t)
    hx = CubicHermiteSpline(t, X, Xd)
    hy = CubicHermiteSpline(t, Y, Yd)
    x1, y1 = hx(t, 1), hy(t, 1)          # = Xd, Yd at nodes (by construction)
    x2, y2 = hx(t, 2), hy(t, 2)          # cubic-implied acceleration
    v = np.maximum(np.hypot(x1, y1), 1e-3)
    latm = np.abs(x1 * y2 - y1 * x2) / v
    return dict(v=v, latm=latm, latm_sd=np.ones_like(latm))


def env_ceil(runs, ell, sf, sig_pos, delta, method, W=4):
    chunks = []
    for r in runs:
        try:
            ss = H.StintSmoother(ell, sf, sig_pos, delta, iters=2)
            ss.fit(r["tp"], r["X"], r["Y"], r["tc"], r["V"])
        except Exception:
            continue
        if method == "hermite":
            c = hermite_lat(ss)
        else:
            g = H.geom_kinematics(ss, W=W)
            c = dict(v=g["v"], latm=g["latm"], latm_sd=g["latm_sd"])
        if c is not None:
            chunks.append(c)
    if not chunks:
        return None
    out = {k: np.concatenate([c[k] for c in chunks]) for k in chunks[0]}
    env = H.build_envelope(out["v"], out["latm"], out["latm_sd"])
    if not env:
        return None
    return H._interp_ceil(env, 45), H._interp_ceil(env, 70)


def main():
    log("loading 2023 Japan Q ...")
    session = H.load_session(2023, "Japan", "Q")
    runs = H.driver_runs(session, "VER")
    log(f"VER: {len(runs)} runs")
    delta, sf = 0.06, 100.0

    def fmt(r):
        if r is None:
            return f"{'--':>7} {'--':>7}"
        a, b = r
        sa = f"{a:7.1f}" if a is not None else f"{'--':>7}"
        sb = f"{b:7.1f}" if b is not None else f"{'--':>7}"
        return f"{sa} {sb}"

    print("\n--- ell-stability: HERMITE (param-free) vs WINDOWED W=4 ---")
    print(f"{'ell':>5} | {'HERMITE 45/70':>15} | {'WINDOWED 45/70':>15}")
    for ell in [1.2, 2.0, 3.0, 5.0]:
        h = env_ceil(runs, ell, sf, 0.3, delta, "hermite")
        w = env_ceil(runs, ell, sf, 0.3, delta, "windowed", W=4)
        print(f"{ell:5.2f} | {fmt(h)} | {fmt(w)}")

    print("\n--- W-sensitivity at ell=2.0 (windowed) + Hermite endpoint ---")
    print(f"{'W':>6} | {'ceil 45/70':>15}")
    for W in [2, 4, 8, 16]:
        w = env_ceil(runs, 2.0, sf, 0.3, delta, "windowed", W=W)
        print(f"{W:6d} | {fmt(w)}")
    h = env_ceil(runs, 2.0, sf, 0.3, delta, "hermite")
    print(f"{'herm':>6} | {fmt(h)}")
    print("\n(ceil = 0.92 envelope of |a_lat| at 45 and 70 m/s; m/s^2)")


if __name__ == "__main__":
    main()
