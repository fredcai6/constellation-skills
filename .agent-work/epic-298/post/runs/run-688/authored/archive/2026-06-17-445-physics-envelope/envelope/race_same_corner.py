"""Same-corner lap-to-lap grip consistency (epic #445).

Is the ~10% race scatter REAL lap-to-lap variation, or an artifact of averaging
DIFFERENT corners? Match corners by track location and track each specific
corner's apex grip lap-by-lap. Compare within-corner scatter (same corner,
successive laps -> should be small for a consistent driver) to the cross-corner
spread (different corners -> genuinely different grip).
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
from corner_segment import circle_fit  # noqa: E402
from src.preprocessing.trajectory.loaders import driver_num, driver_streams, stint_span  # noqa: E402

G = 9.81
OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
DRIVER = "VER"
MATCH_M = 45.0


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def lap_geom(ss, run, ls, le, N=5):
    la = lap_arrays(ss, run, ls, le)
    if la is None:
        return None
    t, X, Y, v = la
    n = len(v)
    R = np.full(n, np.nan)
    for i in range(n):
        a, b = max(0, i - N), min(n, i + N + 1)
        if b - a >= 5:
            r = circle_fit(X[a:b], Y[a:b])
            if np.isfinite(r) and 3 < r < 5000:
                R[i] = r
    return X, Y, v, R


def corner_grip_at(X, Y, v, R, Xr, Yr):
    """Apex grip at the matched corner: min-speed node in the neighborhood."""
    d = np.hypot(X - Xr, Y - Yr)
    near = d < MATCH_M
    if near.sum() < 2:
        return np.nan, np.nan
    idx = np.where(near)[0]
    j = idx[np.argmin(v[idx])]
    if not np.isfinite(R[j]):
        return np.nan, np.nan
    return v[j] ** 2 / R[j] / G, v[j] * 3.6   # grip (g), apex speed (km/h)


def main():
    log("loading 2023 Japan R ...")
    session = H.load_session(2023, "Japan", "R")
    num = driver_num(session, DRIVER)
    pos_d, spd_d = driver_streams(session, num)
    laps = session.laps.pick_drivers(DRIVER)
    laps = laps[laps["LapTime"].notna()].copy()
    stints = sorted(int(s) for s in laps["Stint"].dropna().unique())

    # fit a smoother per stint, gather lap geometries
    lapgeos = []   # (lapnum, stint, compound, age, X,Y,v,R)
    smoothers = {}
    for st in stints:
        try:
            t0, t1, _ = stint_span(session, DRIVER, st)
        except Exception:
            continue
        mp = (pos_d["t"] >= t0) & (pos_d["t"] <= t1)
        mc = (spd_d["t"] >= t0) & (spd_d["t"] <= t1)
        if mp.sum() < 100 or mc.sum() < 100:
            continue
        ss = H.StintSmoother(2.0, 100.0, 0.3, 0.06, iters=2)
        ss.fit(pos_d["t"][mp], pos_d["X"][mp], pos_d["Y"][mp],
               spd_d["t"][mc], spd_d["V"][mc])
        smoothers[st] = ss
        run = dict(tc=spd_d["t"][mc], V=spd_d["V"][mc])
        for _, r in laps[laps["Stint"] == st].iterrows():
            if pd.notna(r.get("PitInTime")) or pd.notna(r.get("PitOutTime")):
                continue
            if int(r["LapNumber"]) <= 1:
                continue
            g = lap_geom(ss, run, r["LapStartTime"].total_seconds(),
                         r["Time"].total_seconds())
            if g is None:
                continue
            lapgeos.append((int(r["LapNumber"]), st, str(r["Compound"]),
                            float(r["TyreLife"]) if pd.notna(r["TyreLife"]) else np.nan, *g))
    log(f"{len(lapgeos)} racing-lap geometries")

    # reference corners from the lap with the most detected apexes
    best = max(lapgeos, key=lambda L: len(corner_apexes(
        np.arange(len(L[4])) * 0.24, L[4], L[5], L[6])) if True else 0)
    # detect on a representative lap via its arrays
    Xr_, Yr_, vr_, Rr_ = best[4], best[5], best[6], best[7]
    # build (X,Y) reference apex locations from min-speed corner detection
    from scipy.signal import find_peaks
    alat = np.nan_to_num(vr_**2 / Rr_, nan=0.0)
    idx, _ = find_peaks(alat, height=5.0, prominence=4.0, distance=4)
    idx = [i for i in idx if vr_[i] * 3.6 > 45 and np.isfinite(Rr_[i]) and alat[i] / G < 6.0]
    refs = [(Xr_[i], Yr_[i], vr_[i] * 3.6) for i in idx]
    log(f"{len(refs)} reference corners")

    # grip per reference corner per lap
    data = {k: [] for k in range(len(refs))}
    for (lapn, st, comp, age, X, Y, v, R) in lapgeos:
        for k, (Xr, Yr, vref) in enumerate(refs):
            g, vk = corner_grip_at(X, Y, v, R, Xr, Yr)
            data[k].append((lapn, st, age, g, vk))

    # per-corner: within-stint scatter + degradation
    print(f"\n{'corner':>6} {'refkmh':>7} {'mean_g':>7} {'within-stint sd':>16} "
          f"{'wear(g/lap)':>12} {'n':>3}")
    within_sds = []
    rows_for_plot = {}
    for k, (Xr, Yr, vref) in enumerate(refs):
        arr = np.array([(a, g) for (lapn, st, a, g, vk) in data[k] if np.isfinite(g)])
        if len(arr) < 6:
            continue
        rows_for_plot[k] = (vref, np.array(data[k], dtype=object))
        # within-stint sd: detrend per stint then std
        sds = []
        wears = []
        for st in stints:
            sub = np.array([(a, g) for (lapn, s2, a, g, vk) in data[k]
                            if s2 == st and np.isfinite(g)])
            if len(sub) >= 4:
                sl, intc = np.polyfit(sub[:, 0], sub[:, 1], 1)
                resid = sub[:, 1] - (sl * sub[:, 0] + intc)
                sds.append(np.std(resid))
                wears.append(sl)
        if sds:
            wsd = float(np.mean(sds))
            within_sds.append(wsd)
            print(f"{k:6d} {vref:7.0f} {np.mean(arr[:,1]):7.2f} {wsd:16.3f} "
                  f"{np.mean(wears):+12.4f} {len(arr):3d}")
    print(f"\nmedian WITHIN-corner lap-to-lap sd (detrended): "
          f"{np.median(within_sds):.3f} g")
    # cross-corner spread (different corners, same lap-ish)
    cc = [np.mean(np.array([(g) for (lapn, st, a, g, vk) in data[k] if np.isfinite(g)]))
          for k in rows_for_plot]
    print(f"cross-corner spread (sd of per-corner mean grip): {np.std(cc):.3f} g")
    print("\n-> if within-corner sd << cross-corner spread, the '10%' was mixing "
          "corners, not real lap-to-lap variation.")
    _plot(rows_for_plot, stints)


def _plot(rows_for_plot, stints):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    # pick up to 5 corners spanning speed
    items = sorted(rows_for_plot.items(), key=lambda kv: kv[1][0])
    pick = items[:: max(1, len(items) // 5)][:5]
    fig, ax = plt.subplots(figsize=(12, 6))
    cmap = plt.cm.viridis(np.linspace(0, 1, len(pick)))
    for (k, (vref, arr)), col in zip(pick, cmap):
        laps = np.array([row[0] for row in arr])
        grips = np.array([row[3] if np.isfinite(row[3]) else np.nan for row in arr])
        ax.plot(laps, grips, "o-", ms=4, color=col, label=f"corner@{vref:.0f}km/h")
    for st in stints[1:]:
        ax.axvline(0, color="k", ls=":", lw=0.6)
    ax.set_xlabel("lap number")
    ax.set_ylabel("apex grip (g)")
    ax.set_title(f"{DRIVER} Suzuka race — SAME-corner grip lap-by-lap")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    png = OUT / "race_same_corner.png"
    fig.savefig(png, dpi=110)
    log(f"wrote {png}")


if __name__ == "__main__":
    main()
