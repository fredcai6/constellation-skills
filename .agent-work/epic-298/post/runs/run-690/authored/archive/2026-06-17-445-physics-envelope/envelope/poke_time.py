"""Consolidate per-car grip channel + first poke at TIME (epic #445).

Consolidate: per-car G(v)=min(A+B v^2, G_sat), frontier-corrected for compound
(+0.036 g/C lifts to the soft-tyre frontier; common to all cars so it shifts the
absolute level, not the car-to-car differences). Saved as per-car artifacts.

Time: at a corner of radius R the grip ceiling sets apex speed v=sqrt(G g R), so
a fractional grip change shifts corner time by ~ -1/2 dG/G. Sum over the grip-
limited part of a reference lap -> grip-attributable lap-time difference. Compare
to the ACTUAL qualifying gaps: how much of the gap does grip explain?
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

import harvest_envelope as H  # noqa: E402

G = 9.81
OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
CARS = {
    "VER": dict(team="RBR", A=1.90, B=0.00177, Gsat=4.95),
    "HAM": dict(team="MERC", A=1.84, B=0.00186, Gsat=5.10),
    "ALB": dict(team="WIL", A=1.74, B=0.00192, Gsat=4.84),
}
COMP_FRONTIER = 0.036 * 2.5   # +0.036 g/C, ~2.5 C-numbers to soft frontier (common)


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def Gv(v_ms, p, frontier=False):
    base = np.minimum(p["A"] + p["B"] * v_ms**2, p["Gsat"])
    return base + (COMP_FRONTIER if frontier else 0.0)


def consolidate():
    for car, p in CARS.items():
        art = {
            "car": car, "team": p["team"],
            "form": "G(v)=min(A+B v^2, G_sat) [g], v in m/s; +frontier to soft tyre",
            "A_mechanical_g": p["A"], "B_downforce": p["B"], "G_sat_g": p["Gsat"],
            "compound_frontier_lift_g": round(COMP_FRONTIER, 3),
            "valid_kmh": [46, 185], "above": "capped at G_sat (physical, unmeasured)",
            "provenance": "pooled apexes Suzuka+Monaco quali+race, derived saturation",
        }
        (OUT / f"grip_channel_{car}.json").write_text(json.dumps(art, indent=2))
    log("saved per-car grip channels (frontier-corrected)")


def reference_corner_profile():
    """VER Suzuka quali lap: per-node (v, dt, reliable a_lat)."""
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
    o = np.argsort(t); t = t[o]
    keep = np.concatenate([[True], np.diff(t) > 1e-9]); t = t[keep]
    X, Y = ss.pos_at(t)
    v = np.interp(t, run["tc"], run["V"])
    n = len(v)
    alat = np.zeros(n)
    for i in range(n):
        a, b = max(0, i - 5), min(n, i + 6)
        if b - a >= 5:
            xx, yy = X[a:b], Y[a:b]
            A = np.column_stack([xx, yy, np.ones_like(xx)])
            sol, *_ = np.linalg.lstsq(A, -(xx**2 + yy**2), rcond=None)
            cx, cy = -sol[0] / 2, -sol[1] / 2
            r2 = cx**2 + cy**2 - sol[2]
            if r2 > 9:
                R = np.sqrt(r2)
                resid = np.sqrt(np.mean((np.hypot(xx - cx, yy - cy) - R) ** 2))
                if resid / R < 0.03 and R < 5000:
                    alat[i] = v[i] ** 2 / R / G
    dt = np.gradient(t)
    return v, dt, alat, fl["LapTime"].total_seconds(), session


def main():
    consolidate()
    log("loading reference lap ...")
    v, dt, alat, ver_lap, session = reference_corner_profile()
    pV = CARS["VER"]
    GV_all = Gv(v, pV)
    util = np.clip(alat / np.maximum(GV_all, 1e-6), 0, 1)   # fraction of grip used
    T_grip = float((dt * util).sum())
    log(f"VER lap {ver_lap:.2f}s; grip-limited time (util-weighted) {T_grip:.1f}s "
        f"({100*T_grip/ver_lap:.0f}% of lap)")

    print("\n=== grip-attributable lap-time difference (corners) ===")
    print(f"{'car':>4} {'team':>5} {'grip dt vs VER':>15}")
    times = {}
    for car, p in CARS.items():
        Gc = Gv(v, p)
        d = -0.5 * dt * util * (Gc - GV_all) / np.maximum(GV_all, 1e-6)
        times[car] = float(d.sum())
        print(f"{car:>4} {p['team']:>5} {times[car]:+14.3f}s")

    print("\n=== vs ACTUAL Suzuka 2023 quali gaps ===")
    print(f"{'car':>4} {'best lap':>9} {'actual d vs VER':>16} {'grip explains':>14}")
    for car, p in CARS.items():
        cl = session.laps.pick_drivers(car)
        cl = cl[cl["LapTime"].notna()]
        best = cl["LapTime"].min().total_seconds() if len(cl) else np.nan
        d_act = best - ver_lap
        frac = (times[car] / d_act * 100) if abs(d_act) > 0.05 else np.nan
        fs = f"{frac:5.0f}%" if np.isfinite(frac) else "  n/a"
        print(f"{car:>4} {best:8.2f}s {d_act:+15.2f}s {fs:>14}")
    print("\n(grip dt = corner time from the per-car grip ceiling; the REST of the gap "
          "is power/drag/efficiency + driver -- other channels not built yet.)")


if __name__ == "__main__":
    main()
