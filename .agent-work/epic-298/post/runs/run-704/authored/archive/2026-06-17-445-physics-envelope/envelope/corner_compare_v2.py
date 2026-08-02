"""Multi-LAP corner apex-speed comparison with per-corner uncertainty (#445).

Upgrade of corner_compare: use ALL flying laps per driver (LapTime <= 1.07*best),
so each (driver, corner) gets a mean +/- sd apex speed over laps. Lets us judge
which cross-car differences exceed within-driver scatter. Apex speed only (sensor
speed + smoothed position) -> no radius, no a_lat over-read.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

import harvest_envelope as H  # noqa: E402
from corner_compare import apex_speed_at, reference_corners  # noqa: E402

DRIVERS = ["VER", "PER", "HAM", "RUS", "ALB"]
TEAM = {"VER": "RBR", "PER": "RBR", "HAM": "MERC", "RUS": "MERC", "ALB": "WIL"}


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def flying_windows(session, abbr, frac=1.07):
    laps = session.laps.pick_drivers(abbr)
    laps = laps[laps["LapTime"].notna()]
    if len(laps) == 0:
        return []
    best = laps["LapTime"].min()
    fly = laps[laps["LapTime"] <= best * frac]
    out = []
    for _, r in fly.iterrows():
        out.append((r["LapStartTime"].total_seconds(), r["Time"].total_seconds()))
    return out


def lap_geo(ss, run, lap_start, lap_end):
    mask = (ss.kind == 1) & (ss.ts >= lap_start) & (ss.ts <= lap_end)
    t = ss.ts[mask]
    order = np.argsort(t)
    t = t[order]
    keep = np.concatenate([[True], np.diff(t) > 1e-9])
    t = t[keep]
    if len(t) < 50:
        return None
    X, Y = ss.pos_at(t)
    v = np.interp(t, run["tc"], run["V"])
    return dict(X=X, Y=Y, v=v)


def driver_lap_geos(session, abbr):
    """All flying-lap geometries for a driver (smoother fit once per run)."""
    runs = H.driver_runs(session, abbr)
    fits = {}
    geos = []
    for ls, le in flying_windows(session, abbr):
        run = next((r for r in runs if r["t0"] <= ls and r["t1"] >= le), None)
        if run is None:
            continue
        key = (round(run["t0"], 1), round(run["t1"], 1))
        ss = fits.get(key)
        if ss is None:
            ss = H.StintSmoother(2.0, 100.0, 0.3, 0.06, iters=2)
            ss.fit(run["tp"], run["X"], run["Y"], run["tc"], run["V"])
            fits[key] = ss
        g = lap_geo(ss, run, ls, le)
        if g is not None:
            geos.append(g)
    return geos


def main():
    log("loading 2023 Japan Q ...")
    session = H.load_session(2023, "Japan", "Q")

    # reference corners from VER fastest lap
    from corner_compare import driver_fast_lap_geo
    refgeo = driver_fast_lap_geo(session, "VER")
    ref = reference_corners(refgeo)
    refpts = [(refgeo["X"][i], refgeo["Y"][i], refgeo["s"][i], refgeo["v"][i] * 3.6)
              for i in ref]
    log(f"{len(refpts)} reference corners")

    # per driver: all flying-lap apex speeds at each ref corner
    apex = {a: [[] for _ in refpts] for a in DRIVERS}
    for a in DRIVERS:
        geos = driver_lap_geos(session, a)
        log(f"{a}: {len(geos)} flying laps")
        for g in geos:
            for ci, (Xr, Yr, _, _) in enumerate(refpts):
                sp = apex_speed_at(g, Xr, Yr)
                if sp is not None:
                    apex[a][ci].append(sp)

    # per-corner table: mean +/- sd (n)
    print(f"\n{'s(m)':>6} {'cls':>4} | " + " ".join(f"{a:>11}" for a in DRIVERS))
    print("-" * 78)
    stats = {a: [] for a in DRIVERS}   # (corner_class, mean) per corner
    for ci, (_, _, s, vref) in enumerate(refpts):
        cls = "slow" if vref < 130 else ("fast" if vref > 210 else "med")
        cells = []
        for a in DRIVERS:
            xs = apex[a][ci]
            if len(xs) >= 1:
                m, sd = float(np.mean(xs)), float(np.std(xs))
                cells.append(f"{m:5.0f}±{sd:3.0f}({len(xs)})")
                stats[a].append((cls, m, ci))
            else:
                cells.append(f"{'--':>11}")
        print(f"{s:6.0f} {cls:>4} | " + " ".join(f"{c:>11}" for c in cells))

    # regime summary with field-relative gap + SE across corners
    print("\n--- mean apex-speed gap to field median by class (km/h), +/- SE over corners ---")
    print(f"{'cls':>5} {'n':>3} | " + " ".join(f"{a:>11}" for a in DRIVERS))
    # build per-corner field medians
    for cls in ["slow", "med", "fast"]:
        cis = [ci for ci, (_, _, _, vref) in enumerate(refpts)
               if (vref < 130 if cls == "slow" else vref > 210 if cls == "fast"
                   else 130 <= vref <= 210)]
        if not cis:
            continue
        gaps = {a: [] for a in DRIVERS}
        for ci in cis:
            vals = {a: np.mean(apex[a][ci]) for a in DRIVERS if apex[a][ci]}
            if len(vals) < 3:
                continue
            med = np.median(list(vals.values()))
            for a, vv in vals.items():
                gaps[a].append(vv - med)
        cells = []
        for a in DRIVERS:
            if gaps[a]:
                m = np.mean(gaps[a])
                se = np.std(gaps[a]) / np.sqrt(len(gaps[a]))
                flag = "*" if abs(m) > 2 * se and se > 0 else " "
                cells.append(f"{m:+5.1f}±{se:3.1f}{flag}")
            else:
                cells.append(f"{'--':>11}")
        print(f"{cls:>5} {len(cis):3d} | " + " ".join(f"{c:>11}" for c in cells))
    print("\n(* = |gap| > 2*SE across corners; teammates tracking => car signature)")


if __name__ == "__main__":
    main()
