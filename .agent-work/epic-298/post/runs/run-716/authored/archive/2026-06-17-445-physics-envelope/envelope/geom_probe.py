"""Geometric lateral channel: kappa = d(theta)/ds from solved p/v states.

Instead of reading a_lat off the smoother's ell-regularized ACCELERATION state
(2nd time-derivative; shown to be prior-dominated, ceiling swings 135g->2.3g
with ell), build curvature from the WELL-CONSTRAINED velocity heading:

    theta = atan2(vy, vx)            (1st-order, speed measured, dir pinned by pos)
    s     = integral v dt             (measured speed)
    kappa = local slope of theta(s)   (regression over a node window, noise averages)
    a_lat = v^2 * kappa               (v measured)

Per-car (line preserved, no track pooling). Uncertainty carried from the
velocity covariance through theta and the weighted-LS slope.

DECISIVE TEST: rerun the ell sweep on this geometric a_lat. If it is FLAT across
ell while the time-domain a_lat swung 135g->2.3g, the channel is data-determined.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

import harvest_envelope as H  # noqa: E402


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def geom_lateral(ss, W=4):
    """a_lat from kappa=d(theta)/ds via local weighted regression of heading."""
    mask = ss.kind == 1
    m = ss.m_s[mask]
    P = ss.P_s[mask]
    t = ss.ts[mask]
    vx = m[:, 1] + ss._vtrend_x
    vy = m[:, 4] + ss._vtrend_y
    v = np.maximum(np.hypot(vx, vy), 1e-3)
    svx2 = np.clip(P[:, 1, 1], 0, None)
    svy2 = np.clip(P[:, 4, 4], 0, None)
    cvxy = P[:, 1, 4]
    theta = np.unwrap(np.arctan2(vy, vx))
    sth2 = np.clip((vy**2 * svx2 + vx**2 * svy2 - 2 * vx * vy * cvxy) / v**4, 1e-10, None)
    s = np.concatenate([[0.0], np.cumsum(0.5 * (v[1:] + v[:-1]) * np.diff(t))])
    n = len(v)
    kappa = np.full(n, np.nan)
    skap = np.full(n, np.nan)
    w_all = 1.0 / sth2
    for i in range(n):
        a, b = max(0, i - W), min(n, i + W + 1)
        if b - a < 3:
            continue
        ssl, th, w = s[a:b], theta[a:b], w_all[a:b]
        wsum = w.sum()
        sbar = (w * ssl).sum() / wsum
        tbar = (w * th).sum() / wsum
        dsx = ssl - sbar
        denom = (w * dsx * dsx).sum()
        if denom <= 1e-9:
            continue
        kappa[i] = (w * dsx * (th - tbar)).sum() / denom
        skap[i] = np.sqrt(1.0 / denom)
    sv2 = (vx / v) ** 2 * svx2 + (vy / v) ** 2 * svy2 + 2 * (vx * vy / v**2) * cvxy
    sv2 = np.clip(sv2, 0, None)
    latm = np.abs(v**2 * kappa)
    slat = np.sqrt((2 * v * np.abs(kappa)) ** 2 * sv2 + v**4 * skap**2)
    good = np.isfinite(latm) & np.isfinite(slat)
    return dict(v=v[good], latm=latm[good], latm_sd=np.clip(slat[good], 1e-6, None))


def premise_check(ss):
    """Median per-node sigma of velocity, heading, and acceleration state."""
    mask = ss.kind == 1
    m, P = ss.m_s[mask], ss.P_s[mask]
    vx = m[:, 1] + ss._vtrend_x
    vy = m[:, 4] + ss._vtrend_y
    v = np.maximum(np.hypot(vx, vy), 1e-3)
    sv = np.sqrt(np.clip((vx**2 * P[:, 1, 1] + vy**2 * P[:, 4, 4]) / v**2, 0, None))
    sth = np.sqrt(np.clip((vy**2 * P[:, 1, 1] + vx**2 * P[:, 4, 4]) / v**4, 0, None))
    sa = np.sqrt(np.clip(P[:, 2, 2] + P[:, 5, 5], 0, None))
    return float(np.median(sv)), float(np.degrees(np.median(sth))), float(np.median(sa))


def collect(runs, ell, sf, sig_pos, delta, which):
    chunks = []
    for r in runs:
        try:
            ss = H.StintSmoother(ell, sf, sig_pos, delta, iters=2)
            ss.fit(r["tp"], r["X"], r["Y"], r["tc"], r["V"])
        except Exception:
            continue
        chunks.append(geom_lateral(ss) if which == "geom" else H._propagate_nodes(ss))
    if not chunks:
        return None
    out = {k: np.concatenate([c[k] for c in chunks]) for k in chunks[0]}
    env = H.build_envelope(out["v"], out["latm"], out["latm_sd"])
    if not env:
        return None
    return dict(
        c45=H._interp_ceil(env, 45),
        peak=max(e["ceil"] for e in env),
        sig=float(np.median(out["latm_sd"])),
    )


def main():
    log("loading 2023 Japan Q ...")
    session = H.load_session(2023, "Japan", "Q")
    runs = H.driver_runs(session, "VER")
    log(f"VER: {len(runs)} runs")
    delta, sf = 0.06, 100.0

    # premise check at ell=3
    ss0 = H.StintSmoother(3.0, sf, 0.3, delta, iters=2)
    ss0.fit(runs[0]["tp"], runs[0]["X"], runs[0]["Y"], runs[0]["tc"], runs[0]["V"])
    sv, sth, sa = premise_check(ss0)
    log(f"premise @ell=3: median sigma_v={sv:.3f} m/s, sigma_heading={sth:.2f} deg, "
        f"sigma_acc_state={sa:.2f} m/s^2")

    ells = [0.5, 0.8, 1.2, 2.0, 3.0, 5.0]
    print(f"\n{'ell':>5} | {'TIME a_lat':>22} | {'GEOM a_lat':>22}")
    print(f"{'':>5} | {'c45':>7} {'peak':>7} {'sig':>6} | {'c45':>7} {'peak':>7} {'sig':>6}   (m/s^2)")
    print("-" * 56)
    for ell in ells:
        rt = collect(runs, ell, sf, 0.3, delta, "time")
        rg = collect(runs, ell, sf, 0.3, delta, "geom")

        def f(r, k):
            if r is None or r[k] is None:
                return f"{'--':>7}"
            return f"{r[k]:7.1f}"
        def fs(r):
            return f"{r['sig']:6.1f}" if r else f"{'--':>6}"
        print(f"{ell:5.2f} | {f(rt,'c45')} {f(rt,'peak')} {fs(rt)} | "
              f"{f(rg,'c45')} {f(rg,'peak')} {fs(rg)}")
    print("\n(time = a_lat from acceleration state; geom = v^2 * d(theta)/ds)")


if __name__ == "__main__":
    main()
