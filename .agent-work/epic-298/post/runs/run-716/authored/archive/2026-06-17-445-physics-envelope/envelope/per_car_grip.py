"""Per-car grip channel G(v), derived saturation, compound/age frontier (#445).

(1) Per car: fit G(v)=min(A+B v^2, G_sat) with G_sat DERIVED (free param).
(2) Compound/age frontier: apexes are on mixed compounds/ages, mostly NOT at the
    grip frontier. The Suzuka(C1-3)/Monaco(C3-5) overlap (~80-150 km/h) gives the
    same speeds on different compounds -> measure whether softer rubber / fresher
    tyres lift the ceiling, and correct toward the true frontier.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

import harvest_envelope as H  # noqa: E402
from envelopes_1d import corner_apexes, lap_arrays  # noqa: E402
from corner_compare_v2 import flying_windows  # noqa: E402
from src.preprocessing.trajectory.loaders import driver_num, driver_streams, stint_span  # noqa: E402

G = 9.81
OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
CARS = ["VER", "HAM", "ALB"]
TEAM = {"VER": "RBR", "HAM": "MERC", "ALB": "WIL"}
VMAX = 185.0
# 2023 allocations: Suzuka [1,2,3], Monaco [3,4,5]
COMP = {"Japan": {"SOFT": 3, "MEDIUM": 2, "HARD": 1},
        "Monaco": {"SOFT": 5, "MEDIUM": 4, "HARD": 3}}


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def gmodel(v, A, B, Gs):
    return np.minimum(A + B * v**2, Gs)


def collect(year, gp, ses, car, mode):
    session = H.load_session(year, gp, ses)
    cmap = COMP[gp]
    rows = []
    if mode == "Q":
        runs = H.driver_runs(session, car)
        fits = {}
        laps = session.laps.pick_drivers(car)
        laps = laps[laps["LapTime"].notna()]
        for ls, le in flying_windows(session, car):
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
            if not la:
                continue
            lr = laps[(laps["LapStartTime"].dt.total_seconds() <= ls + 1) &
                      (laps["Time"].dt.total_seconds() >= le - 1)]
            comp = str(lr["Compound"].iloc[0]) if len(lr) else "SOFT"
            age = float(lr["TyreLife"].iloc[0]) if len(lr) and pd.notna(lr["TyreLife"].iloc[0]) else 3.0
            C = cmap.get(comp, 3)
            for va, al in corner_apexes(*la):
                if va * 3.6 < VMAX:
                    rows.append((va * 3.6, al / G, C, age))
    else:
        num = driver_num(session, car)
        pos_d, spd_d = driver_streams(session, num)
        laps = session.laps.pick_drivers(car)
        laps = laps[laps["LapTime"].notna()].copy()
        for st in sorted(int(s) for s in laps["Stint"].dropna().unique()):
            try:
                t0, t1, _ = stint_span(session, car, st)
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
                comp = str(r["Compound"])
                if comp not in cmap:
                    continue
                la = lap_arrays(ss, run, r["LapStartTime"].total_seconds(), r["Time"].total_seconds())
                if not la:
                    continue
                C = cmap[comp]
                age = float(r["TyreLife"]) if pd.notna(r["TyreLife"]) else 5.0
                for va, al in corner_apexes(*la):
                    if va * 3.6 < VMAX:
                        rows.append((va * 3.6, al / G, C, age))
    return rows


def ceiling_pts(df, q=0.90):
    edges = np.arange(40, VMAX + 1, 12)
    vb, cb, sb = [], [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        b = (df["v"] >= lo) & (df["v"] < hi)
        if b.sum() >= 8:
            vb.append(df["v"][b].mean()); cb.append(np.quantile(df["a"][b], q))
            sb.append(np.std(df["a"][b]) / np.sqrt(b.sum()) + 0.05)
    return np.array(vb), np.array(cb), np.array(sb)


def main():
    data = {}
    for car in CARS:
        rows = []
        for gp, ses, mode in [("Japan", "Q", "Q"), ("Japan", "R", "R"),
                              ("Monaco", "Q", "Q"), ("Monaco", "R", "R")]:
            log(f"{car} {gp} {ses} ...")
            rows += collect(2023, gp, ses, car, mode)
        data[car] = pd.DataFrame(rows, columns=["v", "a", "C", "age"])
        log(f"  {car}: {len(rows)} apexes")
    pd.concat({k: v for k, v in data.items()}).to_csv(OUT / "per_car_apex.csv")

    print("\n=== per-car grip channel (derived saturation) ===")
    print(f"{'car':>4} {'team':>5} {'mech A(g)':>10} {'downforce B':>12} {'G_sat(g)':>10} {'n':>6}")
    fits = {}
    for car in CARS:
        df = data[car]
        vb, cb, sb = ceiling_pts(df)
        try:
            popt, pcov = curve_fit(gmodel, vb / 3.6, cb, p0=[1.8, 0.0018, 5.0],
                                   sigma=sb, absolute_sigma=True, maxfev=20000,
                                   bounds=([1.0, 0.0005, 3.5], [3.0, 0.005, 6.5]))
            s = np.sqrt(np.diag(pcov))
            fits[car] = (popt, vb, cb, sb)
            print(f"{car:>4} {TEAM[car]:>5} {popt[0]:6.2f}±{s[0]:.2f} "
                  f"{popt[1]:.5f}±{s[1]:.5f} {popt[2]:6.2f}±{s[2]:.2f} {len(df):6d}")
        except Exception as e:
            log(f"  {car} fit failed: {e}")

    # compound/age frontier in the overlap (same speeds, different compounds)
    allp = pd.concat(data.values())
    ov = allp[(allp["v"] >= 80) & (allp["v"] <= 150)].copy()
    print("\n=== compound/age effect on grip in the 80-150 km/h overlap ===")
    # within-speed-bin regression of a on C and age
    import numpy.linalg as la
    ov["vbin"] = (ov["v"] // 12).astype(int)
    X, y = [], []
    binmap = {b: i for i, b in enumerate(sorted(ov["vbin"].unique()))}
    nb = len(binmap)
    for _, r in ov.iterrows():
        row = np.zeros(nb + 2)
        row[binmap[r["vbin"]]] = 1.0
        row[nb] = r["C"]
        row[nb + 1] = r["age"]
        X.append(row); y.append(r["a"])
    X = np.array(X); y = np.array(y)
    coef, *_ = la.lstsq(X, y, rcond=None)
    resid = y - X @ coef
    se = np.sqrt(np.sum(resid**2) / (len(y) - X.shape[1]) * np.diag(la.inv(X.T @ X)))
    bC, bage = coef[nb], coef[nb + 1]
    print(f"  compound slope (per C-number, softer=+): {bC:+.4f} ± {se[nb]:.4f} g/C  "
          f"({abs(bC)/se[nb]:.1f} sigma)")
    print(f"  tyre-age slope (per lap):                {bage:+.4f} ± {se[nb+1]:.4f} g/lap  "
          f"({abs(bage)/se[nb+1]:.1f} sigma)")
    print("  -> if compound slope ~0, peak grip is compound-independent (ceiling already "
          "~frontier). if >0, softer lifts the frontier.")
    _plot(fits)


def _plot(fits):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    cols = {"RBR": "navy", "MERC": "teal", "WIL": "darkorange"}
    fig, ax = plt.subplots(figsize=(9, 6))
    vv = np.linspace(40, 200, 80)
    for car, (popt, vb, cb, sb) in fits.items():
        c = cols[TEAM[car]]
        ax.errorbar(vb, cb, yerr=sb, fmt="o", color=c, alpha=0.6)
        ax.plot(vv, gmodel(vv / 3.6, *popt), color=c, lw=2,
                label=f"{car} ({TEAM[car]}): mech {popt[0]:.1f}g, sat {popt[2]:.1f}g")
    ax.set_xlabel("corner speed (km/h)"); ax.set_ylabel("grip ceiling G (g)")
    ax.set_title("Per-car grip channel with derived saturation")
    ax.grid(alpha=0.3); ax.legend(fontsize=8)
    png = OUT / "per_car_grip.png"
    fig.tight_layout(); fig.savefig(png, dpi=110)
    log(f"wrote {png}")


if __name__ == "__main__":
    main()
