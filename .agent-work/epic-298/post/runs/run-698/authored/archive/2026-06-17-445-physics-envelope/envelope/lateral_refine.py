"""Refine lateral acceleration + grip unification (epic #445, Stage 2).

Stage 1 lateral wrongly required v<185, discarding high-speed STRAIGHTS where the
fit is great and a_lat~0 is known tightly. Fix the gate to 'trust where the local
path is genuinely circular' (low fit residual), any speed. What's left poorly fit
is genuine high-speed CORNERS -> there the car is at the limit, so a_lat ~ the
GRIP CEILING g_ceil(v)=A+B v^2 (mechanical + downforce), fit from the reliable
points. a_lat and grip are the SAME object: the upper envelope of a_lat(v) IS the
grip model. Append as Stage 2 in the ledger.

Demonstrator: VER Suzuka 2023 quali fastest lap.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

import harvest_envelope as H  # noqa: E402
import truth_ledger as TL  # noqa: E402

G = 9.81
OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def circle_fit_resid(x, y):
    A = np.column_stack([x, y, np.ones_like(x)])
    sol, *_ = np.linalg.lstsq(A, -(x**2 + y**2), rcond=None)
    cx, cy = -sol[0] / 2, -sol[1] / 2
    r2 = cx**2 + cy**2 - sol[2]
    if r2 <= 0:
        return np.nan, np.nan
    R = np.sqrt(r2)
    resid = np.sqrt(np.mean((np.hypot(x - cx, y - cy) - R) ** 2))
    return float(R), float(resid)


def fit_ceiling(v, a, qhi=0.85):
    """g_ceil(v) = A + B v^2 from the upper envelope of reliable a_lat(v)."""
    edges = np.arange(15, 92, 9)
    vb, ab = [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        b = (v >= lo) & (v < hi)
        if b.sum() >= 4:
            vb.append(v[b].mean())
            ab.append(np.quantile(a[b], qhi))
    if len(vb) < 3:
        return None
    coef = np.polyfit(np.array(vb) ** 2, ab, 1)
    return coef[1], coef[0], np.array(vb), np.array(ab)   # A, B


def main():
    log("loading 2023 Japan Q ...")
    session = H.load_session(2023, "Japan", "Q")
    laps = session.laps.pick_drivers("VER")
    laps = laps[laps["LapTime"].notna()]
    fl = laps.loc[laps["LapTime"].idxmin()]
    ls, le = fl["LapStartTime"].total_seconds(), fl["Time"].total_seconds()
    runs = H.driver_runs(session, "VER")
    run = next((r for r in runs if r["t0"] <= ls and r["t1"] >= le),
               max(runs, key=lambda r: r["t1"] - r["t0"]))
    ss = H.StintSmoother(2.0, 100.0, 0.3, 0.06, iters=2)
    ss.fit(run["tp"], run["X"], run["Y"], run["tc"], run["V"])
    mask = (ss.kind == 1) & (ss.ts >= ls) & (ss.ts <= le)
    t = ss.ts[mask]
    o = np.argsort(t)
    t = t[o]
    keep = np.concatenate([[True], np.diff(t) > 1e-9])
    t = t[keep]
    X, Y = ss.pos_at(t)
    v = np.interp(t, run["tc"], run["V"])
    s = np.concatenate([[0.0], np.cumsum(0.5 * (v[1:] + v[:-1]) * np.diff(t))])
    n = len(v)

    # per-node circle fit
    a_meas = np.full(n, np.nan)
    s_meas = np.full(n, np.nan)
    reliable = np.zeros(n, bool)
    N = 5
    for i in range(n):
        a, b = max(0, i - N), min(n, i + N + 1)
        if b - a >= 5:
            R, resid = circle_fit_resid(X[a:b], Y[a:b])
            if np.isfinite(R) and 3 < R < 1e5:
                a_meas[i] = v[i] ** 2 / R
                s_meas[i] = v[i] ** 2 / R**2 * max(resid, 0.15)
                if resid / R < 0.03:           # genuinely circular -> trust, ANY speed
                    reliable[i] = True

    # grip ceiling from reliable points (this is the grip model)
    rv, ra = v[reliable], a_meas[reliable]
    fit = fit_ceiling(rv, ra)
    A, B, vb, ab = fit
    log(f"grip ceiling (this lap): mechanical {A/G:.2f}g, "
        f"downforce@250km/h {B*(250/3.6)**2/G:.2f}g")

    # Stage 2 a_lat: reliable -> measured; unreliable -> grip ceiling (at-limit)
    g_ceil = A + B * v**2
    a2 = np.where(reliable, a_meas, g_ceil)
    s2 = np.where(reliable, s_meas, 0.30 * g_ceil)   # ceiling-fill: ~30% honest sigma
    # but on straights (low curvature even if 'unreliable') a_lat ~ 0, not ceiling:
    straight = (~reliable) & (np.nan_to_num(a_meas) / G < 0.5)
    a2[straight] = np.nan_to_num(a_meas[straight])
    s2[straight] = 0.2 * G

    # ledger: append Stage 2
    path = TL.ledger_path(2023, "Japan", "Q", "VER", int(fl["LapNumber"]))
    try:
        TL.save_stage(path, "s2_lateral_grip",
                      {"a_lat": a2, "a_lat_sigma": s2},
                      "lateral: circular-fit where reliable (any speed), grip-ceiling "
                      "fill at high-speed corners, ~0 on straights")
        log("Stage 2 appended to ledger")
    except ValueError as e:
        log(f"ledger: {e}")

    # report sigma reduction
    _, s1 = TL.best_field(path, "a_lat", ["s0_smoother", "s1_geometry"])
    log(f"lateral median sigma: Stage<=1 {np.nanmedian(s1)/G:.2f}g -> "
        f"Stage 2 {np.nanmedian(s2)/G:.2f}g  ({reliable.sum()}/{n} nodes directly measured)")
    _plot(s, v, a_meas, reliable, a2, s2, rv, ra, A, B, vb, ab)


def _plot(s, v, a_meas, reliable, a2, s2, rv, ra, A, B, vb, ab):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    # lateral along the lap
    ax1.plot(s, a2 / G, color="navy", lw=1.0, label="Stage 2 a_lat")
    ax1.fill_between(s, (a2 - s2) / G, (a2 + s2) / G, color="navy", alpha=0.2)
    ax1.scatter(s[reliable], a_meas[reliable] / G, s=8, color="seagreen",
                label="directly measured (reliable)")
    ax1.set_xlabel("arc length (m)"); ax1.set_ylabel("a_lat (g)")
    ax1.set_title("Refined lateral acceleration along the lap")
    ax1.legend(fontsize=8); ax1.grid(alpha=0.3)
    # grip unification: a_lat vs speed, upper envelope = grip model
    ax2.scatter(rv * 3.6, ra / G, s=10, color="slateblue", alpha=0.5,
                label="measured a_lat (reliable)")
    vv = np.linspace(60, 320, 60) / 3.6
    ax2.plot(vv * 3.6, (A + B * vv**2) / G, "r-", lw=2,
             label=f"grip ceiling = {A/G:.2f} + downforce·v²")
    ax2.scatter(vb * 3.6, ab / G, color="red", s=25, zorder=5)
    ax2.set_xlabel("speed (km/h)"); ax2.set_ylabel("a_lat (g)")
    ax2.set_title("Grip unification: a_lat vs speed; upper envelope = grip model")
    ax2.legend(fontsize=8); ax2.grid(alpha=0.3)
    fig.tight_layout()
    png = OUT / "lateral_refine_ver.png"
    fig.savefig(png, dpi=110)
    log(f"wrote {png}")


if __name__ == "__main__":
    main()
