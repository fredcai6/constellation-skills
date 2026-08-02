"""Multi-event car-capability hierarchy: stable basis + per-event drift (#445).

One race resolves tiers (paired same-corner). Pool across events to find the
STABLE hierarchy (the ordering holds week to week) and the DRIFT (absolute level
moves with setup/track). Fixed field of cars; paired field-relative capability
index per event; pool into stable mean + per-event deviation, with uncertainty.

Suzuka reused from compound_physics.csv; Spain + Britain extracted fresh.
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
from scipy.signal import find_peaks  # noqa: E402

G = 9.81
OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
CARS = ["VER", "HAM", "RUS", "LEC", "NOR"]
TEAM = {"VER": "RBR", "HAM": "MERC", "RUS": "MERC", "LEC": "FER", "NOR": "MCL"}
VMAX = 185.0


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


def ref_corners(X, Y, v, R):
    alat = np.nan_to_num(v**2 / R, nan=0.0)
    idx, _ = find_peaks(alat, height=5.0, prominence=4.0, distance=4)
    return [(X[i], Y[i]) for i in idx
            if 50 < v[i] * 3.6 < VMAX and np.isfinite(R[i]) and alat[i] / G < 6.0]


def grip_at(X, Y, v, R, Xr, Yr, m=45.0):
    d = np.hypot(X - Xr, Y - Yr)
    near = d < m
    if near.sum() < 2:
        return np.nan
    j = np.where(near)[0][np.argmin(v[near])]
    return v[j] ** 2 / R[j] / G if np.isfinite(R[j]) else np.nan


def extract_race(year, gp):
    session = H.load_session(year, gp, "R")
    refs = None
    rows = []
    for car in CARS:
        try:
            num = driver_num(session, car)
            pos_d, spd_d = driver_streams(session, num)
            laps = session.laps.pick_drivers(car)
            laps = laps[laps["LapTime"].notna()].copy()
            stints = sorted(int(s) for s in laps["Stint"].dropna().unique())
        except Exception:
            continue
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
                g = lap_geom(ss, run, r["LapStartTime"].total_seconds(),
                             r["Time"].total_seconds())
                if g is None:
                    continue
                X, Y, v, R = g
                if refs is None:
                    refs = ref_corners(X, Y, v, R)
                    log(f"    {len(refs)} ref corners")
                for ci, (Xr, Yr) in enumerate(refs):
                    gv = grip_at(X, Y, v, R, Xr, Yr)
                    if np.isfinite(gv):
                        rows.append((car, ci, gv))
        log(f"    {car} done")
    return pd.DataFrame(rows, columns=["car", "corner", "grip"])


def paired_index(df, qceil=0.80, min_laps=8):
    ceil = {}
    for (car, corner), g in df.groupby(["car", "corner"]):
        if len(g) >= min_laps:
            ceil[(car, corner)] = np.quantile(g["grip"], qceil)
    corners = sorted(df["corner"].unique())
    field = {}
    for c in corners:
        vals = [ceil[(car, c)] for car in CARS if (car, c) in ceil]
        if len(vals) >= 3:
            field[c] = np.mean(vals)
    out = {}
    for car in CARS:
        deltas = [ceil[(car, c)] - field[c] for c in corners
                  if (car, c) in ceil and c in field]
        if len(deltas) >= 4:
            out[car] = (float(np.mean(deltas)),
                        float(np.std(deltas, ddof=1) / np.sqrt(len(deltas))))
    return out


def main():
    events = {}
    # Suzuka from existing CSV
    suz = pd.read_csv(OUT / "compound_physics.csv").dropna(subset=["grip"])
    suz = suz[suz["car"].isin(CARS)][["car", "corner", "grip"]]
    events["Suzuka"] = paired_index(suz)
    log("Suzuka index from CSV")
    for label, gp in [("Spain", "Spain"), ("Britain", "Great Britain")]:
        log(f"extracting {label} race ...")
        df = extract_race(2023, gp)
        events[label] = paired_index(df)
        df.to_csv(OUT / f"capindex_{label}.csv", index=False)

    print("\n=== paired capability index per event (field-relative g) ===")
    print(f"{'car':>4} {'team':>5} | " + " ".join(f"{e:>14}" for e in events))
    table = {}
    for car in CARS:
        cells = []
        vals = []
        for e in events:
            if car in events[e]:
                cap, se = events[e][car]
                cells.append(f"{cap:+.3f}±{se:.3f}")
                vals.append(cap)
            else:
                cells.append(f"{'--':>14}")
        table[car] = vals
        print(f"{car:>4} {TEAM[car]:>5} | " + " ".join(f"{c:>14}" for c in cells))

    print("\n=== pooled STABLE hierarchy + DRIFT across events ===")
    print(f"{'car':>4} {'team':>5} {'stable cap':>11} {'drift(sd)':>10} {'n_events':>9}")
    rows = []
    for car in CARS:
        vals = table[car]
        if len(vals) >= 2:
            stable = np.mean(vals)
            drift = np.std(vals, ddof=1)
            se = drift / np.sqrt(len(vals))
            rows.append((car, stable, drift, se, len(vals)))
    rows.sort(key=lambda r: -r[1])
    for car, stable, drift, se, n in rows:
        print(f"{car:>4} {TEAM[car]:>5} {stable:+8.3f}±{se:.3f} {drift:10.3f} {n:9d}")
    print("\n(stable cap = mean across events [the basis]; drift = sd across events "
          "[weekend-to-weekend movement]. Is the ORDER stable while levels drift?)")


if __name__ == "__main__":
    main()
