"""Field utilization backtest across drivers and races (epic #445).

Per track: pooled ribbon + reference top-car ideal -> each driver's best lap vs
the ideal = how close car+driver got to the physics ideal. Common reference, so
it BLENDS car and driver (pure-driver needs per-car params). Shows the field
spread and how it differs by race.
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
from src.preprocessing.trajectory.loaders import driver_num, driver_streams, stint_span  # noqa: E402

G, RHO, MASS, P_ENG = 9.81, 1.2, 808.0, 525e3
A, B, GSAT = 1.85, 0.0018, 5.0
OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
NGRID = 1500
RIB_CARS = ["VER", "HAM"]
TRACKS = {
    "Suzuka": dict(gp="Japan", length=5807, cda_c=1.53, cda_o=0.97, ribbon="ribbon_suzuka.npz"),
    "Spain":  dict(gp="Spain", length=4675, cda_c=1.45, cda_o=0.95, ribbon="ribbon_spain.npz"),
}


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def Gv(v):
    return np.minimum(A + B * v * v, GSAT)


def lap_path(ss, ls, le):
    mask = (ss.kind == 1) & (ss.ts >= ls) & (ss.ts <= le)
    t = ss.ts[mask]; o = np.argsort(t); t = t[o]
    keep = np.concatenate([[True], np.diff(t) > 1e-9]); t = t[keep]
    if len(t) < 80:
        return None
    X, Y = ss.pos_at(t)
    s = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(X), np.diff(Y)))])
    if s[-1] < 3500 or s[-1] > 7000:
        return None
    ug = np.linspace(0, 1, NGRID)
    return np.interp(ug, s / s[-1], X), np.interp(ug, s / s[-1], Y)


def build_ribbon(gp, path_out):
    paths = []
    for car in RIB_CARS:
        q = H.load_session(2023, gp, "Q")
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
        rc = H.load_session(2023, gp, "R")
        num = driver_num(rc, car); pos_d, spd_d = driver_streams(rc, num)
        laps = rc.laps.pick_drivers(car); laps = laps[laps["LapTime"].notna()].copy()
        for st in sorted(int(s) for s in laps["Stint"].dropna().unique()):
            try:
                t0, t1, _ = stint_span(rc, car, st)
            except Exception:
                continue
            mp = (pos_d["t"] >= t0) & (pos_d["t"] <= t1); mc = (spd_d["t"] >= t0) & (spd_d["t"] <= t1)
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
        log(f"    {gp} {car}: {len(paths)} paths")
    mean = np.array(paths).mean(axis=0)
    X, Y = mean[0], mean[1]
    s = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(X), np.diff(Y)))])
    th = np.unwrap(np.arctan2(np.gradient(Y, s), np.gradient(X, s)))
    kappa = np.convolve(np.gradient(th, s), np.ones(9) / 9, mode="same")
    np.savez(path_out, s=s, kappa=kappa, nlaps=len(paths))
    return s, kappa


def ideal_time(s, kappa, cda_c, cda_o, length):
    kappa = np.abs(kappa); n = len(s); ds = np.diff(s)

    def drag(v, k):
        cda = cda_o if (abs(k) < 8e-4 and v > 200 / 3.6) else cda_c
        return 0.5 * RHO * cda * v * v / MASS
    vg = np.sqrt(GSAT * G / np.maximum(kappa, 1e-6))
    for _ in range(10):
        vg = np.sqrt(Gv(vg) * G / np.maximum(kappa, 1e-6))
    vg = np.minimum(vg, 100.0)
    v = vg.copy()
    for _ in range(4):
        for i in range(n - 1):
            al = v[i] ** 2 * kappa[i] / G
            tr = np.sqrt(max(Gv(np.array([v[i]]))[0] ** 2 - al ** 2, 0)) * G
            a = min(tr, P_ENG / (MASS * max(v[i], 1.0))) - drag(v[i], kappa[i])
            v[i + 1] = min(v[i + 1], np.sqrt(max(v[i] ** 2 + 2 * a * ds[i], 1.0)), vg[i + 1])
        for i in range(n - 2, -1, -1):
            al = v[i + 1] ** 2 * kappa[i + 1] / G
            tr = np.sqrt(max(Gv(np.array([v[i + 1]]))[0] ** 2 - al ** 2, 0)) * G
            a = tr + drag(v[i + 1], kappa[i + 1])
            v[i] = min(v[i], np.sqrt(max(v[i + 1] ** 2 + 2 * a * ds[i], 1.0)), vg[i])
    t_id = float(np.sum(ds / ((v[:-1] + v[1:]) / 2)))
    return t_id * length / s[-1]


def main():
    results = {}
    for name, cfg in TRACKS.items():
        rib = OUT / cfg["ribbon"]
        if rib.exists():
            d = np.load(rib); s, kappa = d["s"], d["kappa"]
            log(f"{name}: ribbon loaded ({int(d['nlaps'])} laps)")
        else:
            log(f"{name}: building ribbon ...")
            s, kappa = build_ribbon(cfg["gp"], rib)
        t_id = ideal_time(s, kappa, cfg["cda_c"], cfg["cda_o"], cfg["length"])
        log(f"{name}: idealized lap {t_id:.2f}s")
        q = H.load_session(2023, cfg["gp"], "Q")
        util = {}
        for drv in q.laps["Driver"].dropna().unique():
            cl = q.laps.pick_drivers(drv); cl = cl[cl["LapTime"].notna()]
            if len(cl):
                best = cl["LapTime"].min().total_seconds()
                if best > 60:
                    util[drv] = t_id / best
        results[name] = (t_id, util)

    print("\n=== field utilization vs reference physics ideal ===")
    for name, (t_id, util) in results.items():
        order = sorted(util.items(), key=lambda kv: -kv[1])
        print(f"\n{name} (ideal {t_id:.2f}s):")
        for drv, u in order:
            print(f"   {drv:>4} {100*u:5.1f}%")
    print("\n(util = ideal/best-lap; BLENDS car+driver. Top cars approach the ideal; "
          "spread ~ the competitive order. Pure-driver needs per-car params.)")


if __name__ == "__main__":
    main()
