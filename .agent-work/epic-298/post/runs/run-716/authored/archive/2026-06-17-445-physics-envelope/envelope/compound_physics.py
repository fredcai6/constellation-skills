"""Physics-based compound degradation vs the lap-time prior (epic #445).

The gold lap-time compound prior is DEGENERATE on wear: gamma = +0.00022/lap for
C1=C2=C3=C4 (prior-pegged), can't tell compounds apart. Reason: within a stint
lap time mixes fuel burn-off (faster) and tyre wear (slower) -> they cancel.

Slow-corner GRIP is fuel-immune (mechanical mu*g), so its decline with tyre age
is ~pure degradation. Pool several cars over a race, fixed effects for
(car,corner,stint), extract the age slope per compound WITH uncertainty. Compare
to the lap-time-vs-age slope on the same data, and to the gold prior. Does
physics distinguish C2 (medium) from C1 (hard) where lap time cannot?

2023 Suzuka allocation [1,2,3]: HARD=C1, MEDIUM=C2, SOFT=C3.
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
from envelopes_1d import lap_arrays  # noqa: E402
from corner_segment import circle_fit  # noqa: E402
from src.preprocessing.trajectory.loaders import driver_num, driver_streams, stint_span  # noqa: E402
from scipy.signal import find_peaks  # noqa: E402

G = 9.81
OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
CARS = ["VER", "PER", "HAM", "RUS", "LEC", "NOR"]
COMP_C = {"SOFT": 3, "MEDIUM": 2, "HARD": 1}   # Japan 2023
MATCH_M = 45.0
VMAX_RELIABLE = 185.0  # km/h — only slow/medium corners (grip = v^2/R reliable)


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


def reference_corners(X, Y, v, R):
    alat = np.nan_to_num(v**2 / R, nan=0.0)
    idx, _ = find_peaks(alat, height=5.0, prominence=4.0, distance=4)
    refs = []
    for i in idx:
        vk = v[i] * 3.6
        if 50 < vk < VMAX_RELIABLE and np.isfinite(R[i]) and alat[i] / G < 6.0:
            refs.append((X[i], Y[i], vk))
    return refs


def grip_at(X, Y, v, R, Xr, Yr):
    d = np.hypot(X - Xr, Y - Yr)
    near = d < MATCH_M
    if near.sum() < 2:
        return np.nan
    idx = np.where(near)[0]
    j = idx[np.argmin(v[idx])]
    if not np.isfinite(R[j]):
        return np.nan
    return v[j] ** 2 / R[j] / G


def collect(session):
    rows = []   # car, corner, stint, C, age, grip, laptime
    refs = None
    for car in CARS:
        try:
            num = driver_num(session, car)
            pos_d, spd_d = driver_streams(session, num)
            laps = session.laps.pick_drivers(car)
            laps = laps[laps["LapTime"].notna()].copy()
            stints = sorted(int(s) for s in laps["Stint"].dropna().unique())
        except Exception as exc:
            log(f"  {car}: {exc}")
            continue
        ncar = 0
        for st in stints:
            try:
                t0, t1, _ = stint_span(session, car, st)
            except Exception:
                continue
            mp = (pos_d["t"] >= t0) & (pos_d["t"] <= t1)
            mc = (spd_d["t"] >= t0) & (spd_d["t"] <= t1)
            if mp.sum() < 100 or mc.sum() < 100:
                continue
            try:
                ss = H.StintSmoother(2.0, 100.0, 0.3, 0.06, iters=2)
                ss.fit(pos_d["t"][mp], pos_d["X"][mp], pos_d["Y"][mp],
                       spd_d["t"][mc], spd_d["V"][mc])
            except Exception:
                continue
            run = dict(tc=spd_d["t"][mc], V=spd_d["V"][mc])
            for _, r in laps[laps["Stint"] == st].iterrows():
                if pd.notna(r.get("PitInTime")) or pd.notna(r.get("PitOutTime")):
                    continue
                if int(r["LapNumber"]) <= 1:
                    continue
                comp = str(r["Compound"])
                if comp not in COMP_C:
                    continue
                g = lap_geom(ss, run, r["LapStartTime"].total_seconds(),
                             r["Time"].total_seconds())
                if g is None:
                    continue
                X, Y, v, R = g
                if refs is None:
                    refs = reference_corners(X, Y, v, R)
                    log(f"  {len(refs)} reference slow/med corners")
                age = float(r["TyreLife"]) if pd.notna(r["TyreLife"]) else np.nan
                lt = r["LapTime"].total_seconds()
                for ci, (Xr, Yr, vk) in enumerate(refs):
                    gv = grip_at(X, Y, v, R, Xr, Yr)
                    if np.isfinite(gv):
                        rows.append((car, ci, st, COMP_C[comp], age, gv, lt))
                ncar += 1
        log(f"  {car}: {ncar} racing laps")
    return pd.DataFrame(rows, columns=["car", "corner", "stint", "C", "age", "grip", "lt"])


def fe_slope(df, yc, groupcols):
    """Within-group-centered slope of y vs age (fixed effects), with SE."""
    x, y = [], []
    for _, sub in df.groupby(groupcols):
        if len(sub) < 3:
            continue
        a = sub["age"].to_numpy()
        yy = sub[yc].to_numpy()
        x.append(a - a.mean())
        y.append(yy - yy.mean())
    if not x:
        return np.nan, np.nan, 0
    x = np.concatenate(x)
    y = np.concatenate(y)
    Sxx = (x * x).sum()
    if Sxx < 1e-9:
        return np.nan, np.nan, 0
    slope = (x * y).sum() / Sxx
    resid = y - slope * x
    dof = max(len(x) - 1, 1)
    se = np.sqrt((resid * resid).sum() / dof / Sxx)
    return slope, se, len(x)


def main():
    log("loading 2023 Japan R ...")
    session = H.load_session(2023, "Japan", "R")
    df = collect(session)
    df.to_csv(OUT / "compound_physics.csv", index=False)
    log(f"{len(df)} (car,corner,lap) grip observations")

    print("\n=== compound degradation: PHYSICS (slow-corner grip) vs LAP TIME ===")
    print("gold lap-time prior gamma (fractional/lap): C1=C2=C3=+0.00022 (degenerate)\n")
    print(f"{'C':>3} {'comp':>7} | {'grip slope(g/lap)':>18} {'frac/lap':>10} "
          f"| {'laptime slope(s/lap)':>20} {'frac/lap':>10}")
    for C, name in [(1, "HARD"), (2, "MEDIUM"), (3, "SOFT")]:
        sub = df[df["C"] == C]
        if len(sub) < 20:
            continue
        gs, gse, ng = fe_slope(sub, "grip", ["car", "corner", "stint"])
        meang = sub["grip"].mean()
        ls, lse, nl = fe_slope(sub, "lt", ["car", "stint"])
        meanlt = sub["lt"].mean()
        gfrac = gs / meang
        gfrac_se = gse / meang
        lfrac = ls / meanlt
        lfrac_se = lse / meanlt
        print(f"{C:>3} {name:>7} | {gs:+9.4f}±{gse:.4f}  {gfrac:+.5f} "
              f"| {ls:+11.4f}±{lse:.4f}  {lfrac:+.5f}")
    print("\n(grip slope negative = degradation; want PHYSICS to separate HARD vs "
          "MEDIUM where lap time / prior cannot. frac = slope/mean.)")

    # is physics resolving HARD vs MEDIUM?
    sH = df[df["C"] == 1]
    sM = df[df["C"] == 2]
    if len(sH) > 20 and len(sM) > 20:
        gH, seH, _ = fe_slope(sH, "grip", ["car", "corner", "stint"])
        gM, seM, _ = fe_slope(sM, "grip", ["car", "corner", "stint"])
        diff = gM - gH
        sed = np.sqrt(seH**2 + seM**2)
        print(f"\nPHYSICS HARD vs MEDIUM grip-slope difference: {diff:+.4f} "
              f"± {sed:.4f} g/lap  ({abs(diff)/sed:.1f} sigma)")
        lH, lseH, _ = fe_slope(sH, "lt", ["car", "stint"])
        lM, lseM, _ = fe_slope(sM, "lt", ["car", "stint"])
        diffl = lM - lH
        sedl = np.sqrt(lseH**2 + lseM**2)
        print(f"LAPTIME HARD vs MEDIUM slope difference:      {diffl:+.4f} "
              f"± {sedl:.4f} s/lap  ({abs(diffl)/sedl:.1f} sigma)")


if __name__ == "__main__":
    main()
