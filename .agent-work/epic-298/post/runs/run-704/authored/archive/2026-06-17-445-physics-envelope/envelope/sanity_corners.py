"""Corner-geometry sanity check on VER's fastest Suzuka 2023 lap (epic #445).

Reconstruct one clean flying lap, compute rolling radius R(s), and check named
corners against known values before scaling up:
  - hairpin (T11): slowest, ~60-70 km/h, tight R
  - Spoon (T13/14): medium, ~120-150 km/h
  - 130R (T15): fast left, ~290-310 km/h, nominal R ~85-130 m
Also renders the track map (should look like Suzuka's figure-8) colored by speed.
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


def rolling_radius(X, Y, s, win_m=20.0):
    R = np.full(len(s), np.nan)
    for i in range(len(s)):
        sel = np.abs(s - s[i]) <= win_m
        if sel.sum() >= 6:
            r = circle_fit(X[sel], Y[sel])
            if np.isfinite(r) and 3 < r < 5000:
                R[i] = r
    return R


def main():
    log("loading 2023 Japan Q ...")
    session = H.load_session(2023, "Japan", "Q")
    laps = session.laps.pick_drivers("VER")
    laps = laps[laps["LapTime"].notna()]
    fl = laps.loc[laps["LapTime"].idxmin()]
    lap_start = fl["LapStartTime"].total_seconds()
    lap_end = fl["Time"].total_seconds()
    log(f"VER fastest lap: {fl['LapTime'].total_seconds():.3f}s "
        f"window [{lap_start:.1f}, {lap_end:.1f}]")

    runs = H.driver_runs(session, "VER")
    run = next((r for r in runs if r["t0"] <= lap_start and r["t1"] >= lap_end), None)
    if run is None:
        log("no run contains the fastest lap; using widest run")
        run = max(runs, key=lambda r: r["t1"] - r["t0"])
    ss = H.StintSmoother(2.0, 100.0, 0.3, 0.06, iters=2)
    ss.fit(run["tp"], run["X"], run["Y"], run["tc"], run["V"])

    mask = (ss.kind == 1) & (ss.ts >= lap_start) & (ss.ts <= lap_end)
    t = ss.ts[mask]
    order = np.argsort(t)
    t = t[order]
    keep = np.concatenate([[True], np.diff(t) > 1e-9])
    t = t[keep]
    X, Y = ss.pos_at(t)
    # Speed from the SENSOR (clean), not the smoothed |velocity| (isolated spikes).
    # Geometry (radius) comes from the smoothed position; speed from the measurement.
    v = np.interp(t, run["tc"], run["V"])
    s = np.concatenate([[0.0], np.cumsum(0.5 * (v[1:] + v[:-1]) * np.diff(t))])
    log(f"lap reconstructed: {len(t)} nodes, length {s[-1]:.0f} m, "
        f"vmax {v.max()*3.6:.0f} km/h, vmin {v.min()*3.6:.0f} km/h")

    R = rolling_radius(X, Y, s, 20.0)

    # corners = speed minima
    idx, _ = find_peaks(-v, prominence=8, distance=6)
    print("\n--- detected corners along the lap (apex speed / R / a_lat) ---")
    print(f"{'s(m)':>6} {'v(km/h)':>8} {'R(m)':>7} {'a_lat(g)':>9}")
    for i in idx:
        if not np.isfinite(R[i]):
            continue
        al = v[i] ** 2 / R[i] / G
        print(f"{s[i]:6.0f} {v[i]*3.6:8.0f} {R[i]:7.0f} {al:9.2f}")

    # 130R candidate: tightest radius among high-speed nodes
    hs = (v * 3.6 > 250) & np.isfinite(R)
    if hs.any():
        j = np.where(hs)[0][np.argmin(R[hs])]
        print(f"\n130R candidate (fast corner): v={v[j]*3.6:.0f} km/h, "
              f"R={R[j]:.0f} m, a_lat={v[j]**2/R[j]/G:.2f}g  (known: ~290-310 km/h, R~85-130m)")
    print(f"\nhairpin candidate (slowest): v={v[np.argmin(v)]*3.6:.0f} km/h, "
          f"R={R[np.argmin(v)]:.0f} m  (known: ~60-70 km/h)")

    _plot(X, Y, v, s, R, idx)


def _plot(X, Y, v, s, R, idx):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:
        log(f"plot skipped ({exc})")
        return
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    sc = ax1.scatter(X, Y, c=v * 3.6, s=8, cmap="viridis")
    ax1.scatter(X[idx], Y[idx], c="red", s=40, marker="o", label="apex (speed min)")
    ax1.set_aspect("equal")
    ax1.set_title("VER fastest lap — track map (color = speed km/h)")
    ax1.legend(fontsize=8)
    fig.colorbar(sc, ax=ax1, label="km/h")
    ax2.plot(s, v * 3.6, "b-", label="speed (km/h)")
    ax2.set_xlabel("arc length (m)")
    ax2.set_ylabel("speed (km/h)", color="b")
    axb = ax2.twinx()
    axb.plot(s, np.clip(R, 0, 300), "g-", alpha=0.6, label="radius (m, clip 300)")
    axb.set_ylabel("radius (m)", color="g")
    ax2.set_title("speed and radius vs arc length")
    fig.tight_layout()
    png = OUT / "suzuka_ver_lap_geometry.png"
    fig.savefig(png, dpi=110)
    log(f"wrote {png}")


if __name__ == "__main__":
    main()
