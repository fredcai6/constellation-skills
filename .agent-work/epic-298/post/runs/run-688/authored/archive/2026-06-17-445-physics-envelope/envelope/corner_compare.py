"""Multi-car corner comparison by apex speed at matched track location (#445).

Cleanest cornering observable: at each corner (fixed track location), each car's
APEX SPEED (local speed minimum near that X-Y point). Purely measured (sensor
speed + smoothed position), line-preserved, no per-car corner-detection matching
needed. Corners self-classify slow/fast by apex speed. Answers 'who is better in
slow vs fast corners' at the SAME corner.

Reference corner LOCATIONS from VER; every car (incl. VER) read at those points.
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
from corner_segment import adaptive_radius  # noqa: E402

G = 9.81
DRIVERS = ["VER", "PER", "HAM", "RUS", "ALB"]
TEAM = {"VER": "RBR", "PER": "RBR", "HAM": "MERC", "RUS": "MERC", "ALB": "WIL"}
MATCH_M = 55.0   # X-Y radius to associate a car's nodes with a reference corner


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def driver_fast_lap_geo(session, abbr):
    laps = session.laps.pick_drivers(abbr)
    laps = laps[laps["LapTime"].notna()]
    if len(laps) == 0:
        return None
    fl = laps.loc[laps["LapTime"].idxmin()]
    lap_start, lap_end = fl["LapStartTime"].total_seconds(), fl["Time"].total_seconds()
    runs = H.driver_runs(session, abbr)
    run = next((r for r in runs if r["t0"] <= lap_start and r["t1"] >= lap_end), None)
    if run is None:
        return None
    ss = H.StintSmoother(2.0, 100.0, 0.3, 0.06, iters=2)
    ss.fit(run["tp"], run["X"], run["Y"], run["tc"], run["V"])
    mask = (ss.kind == 1) & (ss.ts >= lap_start) & (ss.ts <= lap_end)
    t = ss.ts[mask]
    order = np.argsort(t)
    t = t[order]
    keep = np.concatenate([[True], np.diff(t) > 1e-9])
    t = t[keep]
    X, Y = ss.pos_at(t)
    v = np.interp(t, run["tc"], run["V"])
    s = np.concatenate([[0.0], np.cumsum(0.5 * (v[1:] + v[:-1]) * np.diff(t))])
    R = adaptive_radius(X, Y, N=5)
    return dict(abbr=abbr, X=X, Y=Y, v=v, s=s, R=R, lap=fl["LapTime"].total_seconds())


def reference_corners(geo):
    """VER corner locations: a_lat peaks, deduped, physical only."""
    alat = np.nan_to_num(geo["v"] ** 2 / geo["R"], nan=0.0)
    idx, _ = find_peaks(alat, height=5.0, prominence=4.0, distance=4)
    idx = [i for i in idx if geo["v"][i] * 3.6 > 45 and 1.0 < alat[i] / G < 7.0]
    # dedupe within 60 m arc, keep higher a_lat
    idx = sorted(idx, key=lambda i: geo["s"][i])
    keep = []
    for i in idx:
        if keep and geo["s"][i] - geo["s"][keep[-1]] < 60:
            if alat[i] > alat[keep[-1]]:
                keep[-1] = i
        else:
            keep.append(i)
    return keep


def apex_speed_at(geo, Xr, Yr):
    """Car's apex speed near a reference X-Y: min speed within MATCH_M."""
    d = np.hypot(geo["X"] - Xr, geo["Y"] - Yr)
    near = d < MATCH_M
    if near.sum() < 2:
        return None
    j = np.where(near)[0][np.argmin(geo["v"][near])]
    return geo["v"][j] * 3.6   # km/h


def main():
    log("loading 2023 Japan Q ...")
    session = H.load_session(2023, "Japan", "Q")
    geos = {}
    for abbr in DRIVERS:
        g = driver_fast_lap_geo(session, abbr)
        if g is not None:
            geos[abbr] = g
            log(f"{abbr}: fastest lap {g['lap']:.3f}s, {len(g['X'])} nodes")
    ref = reference_corners(geos["VER"])
    log(f"{len(ref)} reference corners from VER")

    # per-corner apex speeds
    rows = []
    for i in ref:
        Xr, Yr = geos["VER"]["X"][i], geos["VER"]["Y"][i]
        sp = {a: apex_speed_at(g, Xr, Yr) for a, g in geos.items()}
        rows.append(dict(s=geos["VER"]["s"][i], vref=geos["VER"]["v"][i] * 3.6, sp=sp))

    print(f"\n{'s(m)':>6} {'class':>6} | " + " ".join(f"{a:>6}" for a in DRIVERS)
          + "   apex speed (km/h)")
    print("-" * 70)
    for r in rows:
        vref = r["vref"]
        cls = "slow" if vref < 130 else ("fast" if vref > 210 else "med")
        cells = " ".join(
            (f"{r['sp'][a]:6.0f}" if r["sp"].get(a) is not None else f"{'--':>6}")
            for a in DRIVERS
        )
        print(f"{r['s']:6.0f} {cls:>6} | {cells}")

    # regime summary: each car's mean apex-speed gap to field, by corner class
    print("\n--- mean apex-speed gap to field median (km/h), by corner class ---")
    print(f"{'class':>6} {'n':>3} | " + " ".join(f"{a:>6}" for a in DRIVERS))
    for cls, lo, hi in [("slow", 0, 130), ("med", 130, 210), ("fast", 210, 999)]:
        sub = [r for r in rows if lo <= r["vref"] < hi]
        if not sub:
            continue
        gaps = {a: [] for a in DRIVERS}
        for r in sub:
            vals = {a: r["sp"][a] for a in DRIVERS if r["sp"].get(a) is not None}
            if len(vals) < 3:
                continue
            med = np.median(list(vals.values()))
            for a, vv in vals.items():
                gaps[a].append(vv - med)
        cells = " ".join(
            (f"{np.mean(gaps[a]):+6.1f}" if gaps[a] else f"{'--':>6}") for a in DRIVERS
        )
        print(f"{cls:>6} {len(sub):3d} | {cells}")
    print("\n(+ = carries more apex speed than field at that corner class; "
          "teammates should track together if it's a car signature)")


if __name__ == "__main__":
    main()
