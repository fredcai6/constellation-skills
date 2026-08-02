"""Lap curve definition -- the track 'ribbon' (epic #445).

Pool many laps, parametrize each by progress from the start/finish line, average
the PATH -> a generalized track centerline whose curvature is clean (position
noise averages down ~sqrt(N_laps)). Deliberately not any individual driver's line
-- the idealized pace lives on a generalized curve. Output: kappa(s) for the lap
sim, validated against known Suzuka radii.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

import harvest_envelope as H  # noqa: E402
from corner_compare_v2 import flying_windows  # noqa: E402
from src.preprocessing.trajectory.loaders import driver_num, driver_streams, stint_span  # noqa: E402

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
CARS = ["VER", "HAM"]
NGRID = 1500
import pandas as pd  # noqa: E402


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def lap_path(ss, ls, le):
    mask = (ss.kind == 1) & (ss.ts >= ls) & (ss.ts <= le)
    t = ss.ts[mask]
    o = np.argsort(t); t = t[o]
    keep = np.concatenate([[True], np.diff(t) > 1e-9]); t = t[keep]
    if len(t) < 80:
        return None
    X, Y = ss.pos_at(t)
    s = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(X), np.diff(Y)))])
    if s[-1] < 4000 or s[-1] > 7000:
        return None
    u = s / s[-1]
    ug = np.linspace(0, 1, NGRID)
    return np.interp(ug, u, X), np.interp(ug, u, Y)


def collect():
    paths = []
    for car in CARS:
        # quali
        q = H.load_session(2023, "Japan", "Q")
        runs = H.driver_runs(q, car)
        laps = q.laps.pick_drivers(car); laps = laps[laps["LapTime"].notna()]
        for _, r in laps.iterrows():
            ls, le = r["LapStartTime"].total_seconds(), r["Time"].total_seconds()
            run = next((rr for rr in runs if rr["t0"] <= ls and rr["t1"] >= le), None)
            if run is None:
                continue
            ss = H.StintSmoother(2.0, 100.0, 0.3, 0.06, iters=2)
            ss.fit(run["tp"], run["X"], run["Y"], run["tc"], run["V"])
            p = lap_path(ss, ls, le)
            if p:
                paths.append(p)
        # race
        rc = H.load_session(2023, "Japan", "R")
        num = driver_num(rc, car)
        pos_d, spd_d = driver_streams(rc, num)
        laps = rc.laps.pick_drivers(car); laps = laps[laps["LapTime"].notna()].copy()
        for st in sorted(int(s) for s in laps["Stint"].dropna().unique()):
            try:
                t0, t1, _ = stint_span(rc, car, st)
            except Exception:
                continue
            mp = (pos_d["t"] >= t0) & (pos_d["t"] <= t1)
            mc = (spd_d["t"] >= t0) & (spd_d["t"] <= t1)
            if mp.sum() < 100:
                continue
            ss = H.StintSmoother(2.0, 100.0, 0.3, 0.06, iters=2)
            ss.fit(pos_d["t"][mp], pos_d["X"][mp], pos_d["Y"][mp], spd_d["t"][mc], spd_d["V"][mc])
            for _, r in laps[laps["Stint"] == st].iterrows():
                if pd.notna(r.get("PitInTime")) or pd.notna(r.get("PitOutTime")) or int(r["LapNumber"]) <= 1:
                    continue
                p = lap_path(ss, r["LapStartTime"].total_seconds(), r["Time"].total_seconds())
                if p:
                    paths.append(p)
        log(f"  {car} done, {len(paths)} paths so far")
    return np.array(paths)   # (nlaps, 2, NGRID)


def main():
    log("collecting lap paths ...")
    paths = collect()
    log(f"{len(paths)} laps pooled")
    mean = paths.mean(axis=0)        # (2, NGRID)
    X, Y = mean[0], mean[1]
    # arc length of the mean line, curvature = d(theta)/ds (smooth mean line)
    s = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(X), np.diff(Y)))])
    th = np.unwrap(np.arctan2(np.gradient(Y, s), np.gradient(X, s)))
    kappa = np.gradient(th, s)
    # light smoothing
    k = np.ones(9) / 9
    kappa = np.convolve(kappa, k, mode="same")
    R = 1.0 / np.maximum(np.abs(kappa), 1e-5)
    log(f"mean line length {s[-1]:.0f} m")
    log(f"tightest corner R = {R.min():.0f} m (Suzuka hairpin ~25-30m)")
    # report a few corner radii at known locations (by min-R clusters)
    from scipy.signal import find_peaks
    pk, _ = find_peaks(np.abs(kappa), height=1/200, distance=20)
    pk = sorted(pk, key=lambda i: -np.abs(kappa[i]))[:8]
    print(f"\n{'s(m)':>6} {'R(m)':>7}  (corners, tightest first)")
    for i in sorted(pk, key=lambda j: s[j]):
        print(f"{s[i]:6.0f} {1/abs(kappa[i]):7.0f}")
    np.savez(OUT / "ribbon_suzuka.npz", s=s, X=X, Y=Y, kappa=kappa, nlaps=len(paths))
    log("saved ribbon_suzuka.npz")
    _plot(X, Y, s, kappa, R)


def _plot(X, Y, s, kappa, R):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    sc = ax1.scatter(X, Y, c=np.clip(R, 0, 300), s=8, cmap="viridis_r")
    ax1.set_aspect("equal"); ax1.set_title("Generalized track ribbon (color = radius m)")
    fig.colorbar(sc, ax=ax1, label="radius (m)")
    ax2.plot(s, np.clip(R, 0, 400), "b-")
    ax2.set_xlabel("arc length (m)"); ax2.set_ylabel("corner radius (m, clip 400)")
    ax2.set_title("Curvature profile (low R = tight corner)")
    ax2.grid(alpha=0.3)
    fig.tight_layout()
    png = OUT / "ribbon_suzuka.png"
    fig.savefig(png, dpi=110)
    log(f"wrote {png}")


if __name__ == "__main__":
    main()
