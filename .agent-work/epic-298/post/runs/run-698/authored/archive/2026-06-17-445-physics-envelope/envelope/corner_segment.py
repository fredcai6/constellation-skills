"""Curvature-based corner segmentation, validated on VER's Suzuka 2023 lap.

Detect corners as PEAKS in a_lat(s) (catches flowing corners + 130R, which is
near-flat so has no speed dip). Radius from an ADAPTIVE node-count circle window
(auto-scales: ~110m arc at 330 km/h for 130R, ~30m at the hairpin). Each apex:
(track location X,Y, arc s, apex speed, radius, a_lat). Track location is the
cross-car matching key for the multi-car step.

Validate against known Suzuka corners before scaling up:
  T1/2 fast esses entry | S-curves T3-7 | Degner T8-9 | hairpin T11 (slowest) |
  Spoon T13-14 (~50-70m) | 130R T15 (fast, ~85-130m) | chicane T16-17 (slow).
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
OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def circle_fit(x, y):
    A = np.column_stack([x, y, np.ones_like(x)])
    b = -(x**2 + y**2)
    sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    a, bb, c = sol
    cx, cy = -a / 2, -bb / 2
    r2 = cx**2 + cy**2 - c
    return float(np.sqrt(r2)) if r2 > 0 else np.nan


def adaptive_radius(X, Y, N=5):
    """Circle fit over +-N nodes (constant point count -> arc auto-scales)."""
    n = len(X)
    R = np.full(n, np.nan)
    for i in range(n):
        a, b = max(0, i - N), min(n, i + N + 1)
        if b - a >= 5:
            r = circle_fit(X[a:b], Y[a:b])
            if np.isfinite(r) and 3 < r < 5000:
                R[i] = r
    return R


def lap_geometry(ss, run, lap_start, lap_end):
    mask = (ss.kind == 1) & (ss.ts >= lap_start) & (ss.ts <= lap_end)
    t = ss.ts[mask]
    order = np.argsort(t)
    t = t[order]
    keep = np.concatenate([[True], np.diff(t) > 1e-9])
    t = t[keep]
    X, Y = ss.pos_at(t)
    v = np.interp(t, run["tc"], run["V"])          # sensor speed (clean)
    s = np.concatenate([[0.0], np.cumsum(0.5 * (v[1:] + v[:-1]) * np.diff(t))])
    R = adaptive_radius(X, Y, N=5)
    alat = v**2 / R
    return dict(t=t, X=X, Y=Y, v=v, s=s, R=R, alat=alat)


def detect_corners(geo, a_thr=5.0, prom=4.0, vmin_kmh=40.0):
    """Corner apexes = prominent peaks in a_lat(s)."""
    alat = np.nan_to_num(geo["alat"], nan=0.0)
    idx, _ = find_peaks(alat, height=a_thr, prominence=prom, distance=4)
    idx = [i for i in idx if geo["v"][i] * 3.6 > vmin_kmh and np.isfinite(geo["R"][i])]
    return idx


def main():
    log("loading 2023 Japan Q ...")
    session = H.load_session(2023, "Japan", "Q")
    laps = session.laps.pick_drivers("VER")
    laps = laps[laps["LapTime"].notna()]
    fl = laps.loc[laps["LapTime"].idxmin()]
    lap_start, lap_end = fl["LapStartTime"].total_seconds(), fl["Time"].total_seconds()
    runs = H.driver_runs(session, "VER")
    run = next((r for r in runs if r["t0"] <= lap_start and r["t1"] >= lap_end),
               max(runs, key=lambda r: r["t1"] - r["t0"]))
    ss = H.StintSmoother(2.0, 100.0, 0.3, 0.06, iters=2)
    ss.fit(run["tp"], run["X"], run["Y"], run["tc"], run["V"])
    geo = lap_geometry(ss, run, lap_start, lap_end)
    log(f"lap: {len(geo['t'])} nodes, {geo['s'][-1]:.0f} m, "
        f"vmax {geo['v'].max()*3.6:.0f} vmin {geo['v'].min()*3.6:.0f} km/h")

    idx = detect_corners(geo)
    log(f"detected {len(idx)} corners")
    print(f"\n{'#':>2} {'s(m)':>6} {'v(km/h)':>8} {'R(m)':>6} {'a_lat(g)':>9}")
    for k, i in enumerate(idx, 1):
        print(f"{k:2d} {geo['s'][i]:6.0f} {geo['v'][i]*3.6:8.0f} "
              f"{geo['R'][i]:6.0f} {geo['alat'][i]/G:9.2f}")

    # named-corner checks
    print("\n--- named-corner validation ---")
    _check(geo, idx, "hairpin T11 (slowest, ~60-70km/h, tight)", lambda i: True, by="vmin")
    _check(geo, idx, "130R T15 (fastest cornering, ~290-310km/h, R~85-130m)",
           lambda i: geo["v"][i] * 3.6 > 230, by="vmax")
    _check(geo, idx, "Spoon T13-14 (~120-150km/h, R~50-70m)",
           lambda i: 110 < geo["v"][i] * 3.6 < 170, by="amax")
    _plot(geo, idx)


def _check(geo, idx, label, cond, by):
    cand = [i for i in idx if cond(i)]
    if not cand:
        print(f"  {label}: NONE found")
        return
    if by == "vmin":
        i = min(cand, key=lambda i: geo["v"][i])
    elif by == "vmax":
        i = max(cand, key=lambda i: geo["v"][i])
    else:
        i = max(cand, key=lambda i: geo["alat"][i])
    print(f"  {label}:\n      v={geo['v'][i]*3.6:.0f} km/h, R={geo['R'][i]:.0f} m, "
          f"a_lat={geo['alat'][i]/G:.2f}g  @ s={geo['s'][i]:.0f}m")


def _plot(geo, idx):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    ax1.scatter(geo["X"], geo["Y"], c=geo["v"] * 3.6, s=8, cmap="viridis")
    ax1.scatter(geo["X"][idx], geo["Y"][idx], c="red", s=45, zorder=5)
    for k, i in enumerate(idx, 1):
        ax1.annotate(f"{k}:R{geo['R'][i]:.0f}", (geo["X"][i], geo["Y"][i]),
                     fontsize=7, color="darkred")
    ax1.set_aspect("equal")
    ax1.set_title("VER lap — corners (label = radius m)")
    ax2.plot(geo["s"], geo["v"] * 3.6, "b-", label="speed km/h")
    ax2.plot(geo["s"], np.nan_to_num(geo["alat"]) / G * 30, "r-", alpha=0.5,
             label="a_lat (g x30)")
    ax2.scatter(geo["s"][idx], geo["v"][idx] * 3.6, c="red", zorder=5)
    ax2.set_xlabel("arc length (m)")
    ax2.legend(fontsize=8)
    fig.tight_layout()
    png = OUT / "suzuka_ver_corners.png"
    fig.savefig(png, dpi=110)
    log(f"wrote {png}")


if __name__ == "__main__":
    main()
