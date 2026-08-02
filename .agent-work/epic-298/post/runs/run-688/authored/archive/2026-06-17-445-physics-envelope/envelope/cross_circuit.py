"""Cross-circuit constructor ideals: does the model DISCRIMINATE? (epic #445).

Suzuka gave nearly-equal constructor ideals despite very different car characters
(Williams low-grip/low-drag, Merc draggy, RBR efficient). Two readings:
  (a) genuine balanced-track cancellation (grip vs drag trade-offs net out), or
  (b) the model can't tell the cars apart (differences below the noise floor).

Test: re-fit each constructor's params PER TRACK (wings reconfigured per circuit,
so CdA/grip differ) and recompute the ideal at two circuits with OPPOSITE demands:
  - Monza  = low-downforce, drag-dominated (long straights, few corners)
  - Hungary= high-downforce, grip-dominated (slow/twisty, almost no straights)
If discriminating: the low-drag cars (Williams/RBR) should pull RELATIVELY ahead
at Monza, and the grip swing should reorder at Hungary. If the ideals stay packed
the same everywhere, the model can't discriminate (reading b).

Heavy: rebuilds the ribbon (pool VER+HAM Q+R) and re-fits 4 constructors x 2
drivers (apex grip + full-throttle power/drag) per track. Run in background.
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
from constructor_ideal import apex_q, apex_r, full_q, fit_grip, fit_pd  # noqa: E402
from ribbon import lap_path  # noqa: E402
from src.preprocessing.trajectory.loaders import (  # noqa: E402
    driver_num, driver_streams, stint_span,
)

G, RHO, MASS = 9.81, 1.2, 808.0
OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")

# (gp, official length m). Suzuka reuses the cached ribbon if present.
TRACKS = {
    "Monza":   dict(gp="Italy",   length=5793),   # low downforce
    "Hungary": dict(gp="Hungary", length=4381),   # high downforce
    "Suzuka":  dict(gp="Japan",   length=5807),   # balanced (baseline)
}
TEAMS = {
    "RBR": ["VER", "PER"], "MERC": ["HAM", "RUS"],
    "FER": ["LEC", "SAI"], "WIL": ["ALB", "SAR"],
}


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


# --------------------------------------------------------------------------
# ribbon (pooled mean line -> clean kappa(s)) -- generalized, per circuit
# --------------------------------------------------------------------------
def build_ribbon(q, rc, cars=("VER", "HAM")):
    paths = []
    for car in cars:
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
    paths = np.array(paths)
    mean = paths.mean(axis=0); X, Y = mean[0], mean[1]
    s = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(X), np.diff(Y)))])
    th = np.unwrap(np.arctan2(np.gradient(Y, s), np.gradient(X, s)))
    kappa = np.convolve(np.gradient(th, s), np.ones(9) / 9, mode="same")
    return s, X, Y, kappa, len(paths)


# --------------------------------------------------------------------------
# quasi-static ideal lap on the ribbon (length passed per track)
# --------------------------------------------------------------------------
def ideal_time(s, kappa, A, B, GS, P, cc, co, length):
    kappa = np.abs(kappa); n = len(s); ds = np.diff(s)

    def Gv(v):
        return min(A + B * v * v, GS)

    def drag(v, k):
        return 0.5 * RHO * (co if (abs(k) < 8e-4 and v > 200 / 3.6) else cc) * v * v / MASS
    vg = np.sqrt(GS * G / np.maximum(kappa, 1e-6))
    for _ in range(10):
        vg = np.minimum(np.sqrt(np.array([Gv(x) for x in vg]) * G / np.maximum(kappa, 1e-6)), 100.0)
    v = vg.copy()
    for _ in range(4):
        for i in range(n - 1):
            al = v[i] ** 2 * kappa[i] / G
            tr = np.sqrt(max(Gv(v[i]) ** 2 - al ** 2, 0)) * G
            a = min(tr, P / (MASS * max(v[i], 1.0))) - drag(v[i], kappa[i])
            v[i + 1] = min(v[i + 1], np.sqrt(max(v[i] ** 2 + 2 * a * ds[i], 1.0)), vg[i + 1])
        for i in range(n - 2, -1, -1):
            al = v[i + 1] ** 2 * kappa[i + 1] / G
            tr = np.sqrt(max(Gv(v[i + 1]) ** 2 - al ** 2, 0)) * G
            v[i] = min(v[i], np.sqrt(max(v[i + 1] ** 2 + 2 * (tr + drag(v[i + 1], kappa[i + 1])) * ds[i], 1.0)), vg[i])
    return float(np.sum(ds / ((v[:-1] + v[1:]) / 2))) * length / s[-1]


def best_quali_lap(q, drvs):
    best = np.inf
    for car in drvs:
        laps = q.laps.pick_drivers(car); laps = laps[laps["LapTime"].notna()]
        if len(laps):
            best = min(best, float(laps["LapTime"].dt.total_seconds().min()))
    return best


def run_track(name, gp, length):
    log(f"==== {name} ({gp}, {length} m) ====")
    q = H.load_session(2023, gp, "Q")
    rc = H.load_session(2023, gp, "R")

    cache = OUT / f"ribbon_{name.lower()}.npz"
    if cache.exists():
        d = np.load(cache); s, kappa, nrib = d["s"], d["kappa"], int(d.get("nlaps", 0))
        log(f"  ribbon: loaded cached {cache.name} ({nrib} laps, {s[-1]:.0f} m)")
    else:
        log("  building ribbon (pool VER+HAM Q+R) ...")
        s, X, Y, kappa, nrib = build_ribbon(q, rc)
        np.savez(cache, s=s, X=X, Y=Y, kappa=kappa, nlaps=nrib)
        log(f"  ribbon: {nrib} laps, mean line {s[-1]:.0f} m, "
            f"tightest R={1/np.abs(kappa).max():.0f} m")

    res = {}
    for team, drvs in TEAMS.items():
        apex, full = [], []
        for car in drvs:
            try:
                apex += apex_q(q, car) + apex_r(rc, car)
                full += full_q(q, car)
            except Exception as e:
                log(f"    {team}/{car}: {e}")
        if len(apex) < 60 or len(full) < 30:
            log(f"  {team}: thin data ({len(apex)} apex, {len(full)} full), skip")
            continue
        A, B, GS = fit_grip(apex)
        P, cc, co = fit_pd(full)
        t_id = ideal_time(s, kappa, A, B, GS, P, cc, co, length)
        res[team] = dict(A=A, B=B, GS=GS, P=P, cc=cc, co=co, t=t_id,
                         n_apex=len(apex), n_full=len(full))
        log(f"  {team}: A={A:.2f} B={B:.5f} CdA_c={cc:.2f} CdA_o={co:.2f} "
            f"P={P/1e3:.0f}kW -> ideal {t_id:.2f}s ({len(apex)} apex/{len(full)} full)")

    pole = best_quali_lap(q, sum(TEAMS.values(), []))
    return dict(length=length, ideals=res, pole=pole)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    out = {}
    for name, cfg in TRACKS.items():
        try:
            out[name] = run_track(name, cfg["gp"], cfg["length"])
        except Exception as e:
            log(f"  {name} FAILED: {e}")

    # ---- comparison: relative position of each constructor by track ----
    print("\n" + "=" * 70)
    print("CROSS-CIRCUIT constructor ideals (s) and delta-from-field-mean (ms)")
    print("=" * 70)
    for name, r in out.items():
        ids = r["ideals"]
        if not ids:
            continue
        mean = np.mean([p["t"] for p in ids.values()])
        spread = max(p["t"] for p in ids.values()) - min(p["t"] for p in ids.values())
        print(f"\n--- {name} ({r['length']} m, field-mean ideal {mean:.2f}s, "
              f"spread {spread*1000:.0f} ms, pole {r['pole']:.2f}s) ---")
        print(f"{'team':>5} {'ideal(s)':>9} {'d_mean(ms)':>11} {'util%':>7} "
              f"{'CdA_c':>6} {'A(g)':>5}")
        for team, p in sorted(ids.items(), key=lambda kv: kv[1]["t"]):
            dms = (p["t"] - mean) * 1000
            util = 100 * p["t"] / r["pole"]
            print(f"{team:>5} {p['t']:9.2f} {dms:+11.0f} {util:7.1f} "
                  f"{p['cc']:6.2f} {p['A']:5.2f}")

    # ---- did the ORDER shift in the physically-sensible direction? ----
    print("\n" + "=" * 70)
    print("DISCRIMINATION CHECK: constructor delta-from-mean (ms) across tracks")
    print("low-drag cars (WIL/RBR) should go relatively FASTER at Monza (low-DF);")
    print("grip should swing it at Hungary (high-DF). If columns barely move,")
    print("the model can't discriminate (Suzuka similarity = no resolution, not a")
    print("genuine balanced-track cancellation).")
    print("=" * 70)
    teams = sorted({t for r in out.values() for t in r["ideals"]})
    cols = [n for n in out if out[n]["ideals"]]
    print(f"{'team':>5} | " + " ".join(f"{c:>9}" for c in cols))
    for team in teams:
        row = []
        for c in cols:
            ids = out[c]["ideals"]
            if team in ids:
                mean = np.mean([p["t"] for p in ids.values()])
                row.append(f"{(ids[team]['t']-mean)*1000:+9.0f}")
            else:
                row.append(f"{'--':>9}")
        print(f"{team:>5} | " + " ".join(row))
    print("\n(ms vs field mean; negative = faster than the field at that track.)")


if __name__ == "__main__":
    main()
