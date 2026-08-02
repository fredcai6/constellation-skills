"""Pooled lateral-accel ceiling from corner APEXES only (epic #445).

The single-lap ceiling looked like a median because it was fit from ALL reliable
nodes (straights at a_lat~0 dragged the quantile down) and extrapolated to v=0.
Fix: fit the ceiling from CORNER APEXES only (cornering nodes), pooled across many
laps so a genuine high quantile is trustworthy. Monaco adds slow corners to anchor
the low-speed (mechanical) end. The ceiling should now BOUND the cloud and sit at
physical values (~3g mech rising to ~4.5g), with a bootstrap band = real certainty.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

import harvest_envelope as H  # noqa: E402
from envelopes_1d import corner_apexes, lap_arrays  # noqa: E402
from corner_compare_v2 import flying_windows  # noqa: E402
from src.preprocessing.trajectory.loaders import driver_num, driver_streams, stint_span  # noqa: E402

G = 9.81
OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
CAR = "VER"
VMAX = 185.0
RNG = np.random.default_rng(5)


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def apexes_quali(session):
    runs = H.driver_runs(session, CAR)
    fits = {}
    pts = []
    for ls, le in flying_windows(session, CAR):
        run = next((r for r in runs if r["t0"] <= ls and r["t1"] >= le), None)
        if run is None:
            continue
        key = (round(run["t0"], 1), round(run["t1"], 1))
        ss = fits.get(key)
        if ss is None:
            ss = H.StintSmoother(2.0, 100.0, 0.3, 0.06, iters=2)
            ss.fit(run["tp"], run["X"], run["Y"], run["tc"], run["V"])
            fits[key] = ss
        la = lap_arrays(ss, run, ls, le)
        if la:
            t, X, Y, v = la
            for va, al in corner_apexes(t, X, Y, v):
                if va * 3.6 < VMAX:
                    pts.append((va * 3.6, al / G))
    return pts


def apexes_race(session):
    num = driver_num(session, CAR)
    pos_d, spd_d = driver_streams(session, num)
    laps = session.laps.pick_drivers(CAR)
    laps = laps[laps["LapTime"].notna()].copy()
    pts = []
    for st in sorted(int(s) for s in laps["Stint"].dropna().unique()):
        try:
            t0, t1, _ = stint_span(session, CAR, st)
        except Exception:
            continue
        mp = (pos_d["t"] >= t0) & (pos_d["t"] <= t1)
        mc = (spd_d["t"] >= t0) & (spd_d["t"] <= t1)
        if mp.sum() < 100 or mc.sum() < 100:
            continue
        ss = H.StintSmoother(2.0, 100.0, 0.3, 0.06, iters=2)
        ss.fit(pos_d["t"][mp], pos_d["X"][mp], pos_d["Y"][mp], spd_d["t"][mc], spd_d["V"][mc])
        run = dict(tc=spd_d["t"][mc], V=spd_d["V"][mc])
        for _, r in laps[laps["Stint"] == st].iterrows():
            if pd.notna(r.get("PitInTime")) or pd.notna(r.get("PitOutTime")) or int(r["LapNumber"]) <= 1:
                continue
            la = lap_arrays(ss, run, r["LapStartTime"].total_seconds(), r["Time"].total_seconds())
            if la:
                t, X, Y, v = la
                for va, al in corner_apexes(t, X, Y, v):
                    if va * 3.6 < VMAX:
                        pts.append((va * 3.6, al / G))
    return pts


def main():
    pts = {}
    sources = [("Suzuka Q", "Japan", "Q", apexes_quali),
               ("Suzuka R", "Japan", "R", apexes_race),
               ("Monaco Q", "Monaco", "Q", apexes_quali),
               ("Monaco R", "Monaco", "R", apexes_race)]
    for label, gp, ses, fn in sources:
        log(f"loading {label} ...")
        s = H.load_session(2023, gp, ses)
        p = fn(s)
        pts[label] = np.array(p)
        log(f"  {len(p)} apexes")

    allp = np.vstack([v for v in pts.values() if len(v)])
    v, a = allp[:, 0], allp[:, 1]
    log(f"pooled {len(v)} corner apexes, speed {v.min():.0f}-{v.max():.0f} km/h")

    # ceiling = high quantile per speed bin (apexes only -> no straight contamination)
    edges = np.arange(40, VMAX + 1, 12)
    print(f"\n{'speed':>7} {'n':>4} {'median':>7} {'90th':>7} {'ceiling[16,84]':>18}")
    vb, cb = [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        b = (v >= lo) & (v < hi)
        if b.sum() < 8:
            continue
        aa = a[b]
        ceil = np.quantile(aa, 0.90)
        boots = [np.quantile(RNG.choice(aa, len(aa), replace=True), 0.90) for _ in range(300)]
        lo_, hi_ = np.percentile(boots, [16, 84])
        vb.append(0.5 * (lo + hi)); cb.append(ceil)
        print(f"{0.5*(lo+hi):7.0f} {int(b.sum()):4d} {np.median(aa):7.2f} "
              f"{ceil:7.2f}  [{lo_:.2f},{hi_:.2f}]")
    vb, cb = np.array(vb), np.array(cb)
    coef = np.polyfit((vb / 3.6) ** 2, cb, 1)
    Bc, Ac = coef
    log(f"\npooled grip ceiling: mechanical {Ac:.2f}g, downforce@250km/h "
        f"{Bc*(250/3.6)**2:.2f}g  (single-lap was 1.81g / 1.20g)")
    _plot(pts, vb, cb, Ac, Bc)


def _plot(pts, vb, cb, Ac, Bc):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    fig, ax = plt.subplots(figsize=(10, 6))
    cols = {"Suzuka Q": "navy", "Suzuka R": "skyblue", "Monaco Q": "darkred", "Monaco R": "salmon"}
    for label, p in pts.items():
        if len(p):
            ax.scatter(p[:, 0], p[:, 1], s=8, alpha=0.35, color=cols.get(label), label=label)
    ax.plot(vb, cb, "ko", ms=6, label="90th-pct ceiling (binned)")
    vv = np.linspace(40, 320, 60)
    ax.plot(vv, Ac + Bc * (vv / 3.6) ** 2, "k-", lw=2,
            label=f"ceiling = {Ac:.2f}g + downforce·v²")
    ax.set_xlabel("corner apex speed (km/h)"); ax.set_ylabel("a_lat (g)")
    ax.set_title(f"{CAR} pooled corner-apex lateral accel — ceiling bounds the cloud")
    ax.grid(alpha=0.3); ax.legend(fontsize=8)
    png = OUT / "pool_lateral_ver.png"
    fig.tight_layout(); fig.savefig(png, dpi=110)
    log(f"wrote {png}")


if __name__ == "__main__":
    main()
