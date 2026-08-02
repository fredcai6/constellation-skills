"""Constructor ideals: pool both teammates per car (epic #445).

Per-driver params were under-resolved (~2sigma) and ranked the cars wrong (Merc
ideal > RBR). Pool BOTH drivers per constructor -> more data + the better driver
reveals more of the car -> tighter params. Test: does the constructor ideal now
rank correctly (Red Bull fastest, Williams slowest)?
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

G, RHO, MASS = 9.81, 1.2, 808.0
OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
VMAX = 185.0
VMIN_PD = 160 / 3.6
LEN = 5807
TEAMS = {
    "RBR": ["VER", "PER"], "MERC": ["HAM", "RUS"],
    "FER": ["LEC", "SAI"], "WIL": ["ALB", "SAR"],
}


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def gmodel(v, A, B, Gs):
    return np.minimum(A + B * v**2, Gs)


def apex_q(session, car):
    runs = H.driver_runs(session, car)
    fits, pts = {}, []
    for ls, le in flying_windows(session, car):
        run = next((r for r in runs if r["t0"] <= ls and r["t1"] >= le), None)
        if run is None:
            continue
        key = (round(run["t0"], 1), round(run["t1"], 1))
        ss = fits.get(key)
        if ss is None:
            ss = H.StintSmoother(2.0, 100.0, 0.3, 0.06, iters=2)
            ss.fit(run["tp"], run["X"], run["Y"], run["tc"], run["V"]); fits[key] = ss
        la = lap_arrays(ss, run, ls, le)
        if la:
            for va, al in corner_apexes(*la):
                if va * 3.6 < VMAX:
                    pts.append((va * 3.6, al / G))
    return pts


def apex_r(session, car):
    num = driver_num(session, car); pos_d, spd_d = driver_streams(session, num)
    laps = session.laps.pick_drivers(car); laps = laps[laps["LapTime"].notna()].copy()
    pts = []
    for st in sorted(int(s) for s in laps["Stint"].dropna().unique()):
        try:
            t0, t1, _ = stint_span(session, car, st)
        except Exception:
            continue
        mp = (pos_d["t"] >= t0) & (pos_d["t"] <= t1); mc = (spd_d["t"] >= t0) & (spd_d["t"] <= t1)
        if mp.sum() < 100:
            continue
        ss = H.StintSmoother(2.0, 100.0, 0.3, 0.06, iters=2)
        ss.fit(pos_d["t"][mp], pos_d["X"][mp], pos_d["Y"][mp], spd_d["t"][mc], spd_d["V"][mc])
        run = dict(tc=spd_d["t"][mc], V=spd_d["V"][mc])
        for _, r in laps[laps["Stint"] == st].iterrows():
            if pd.notna(r.get("PitInTime")) or pd.notna(r.get("PitOutTime")) or int(r["LapNumber"]) <= 1:
                continue
            la = lap_arrays(ss, run, r["LapStartTime"].total_seconds(), r["Time"].total_seconds())
            if la:
                for va, al in corner_apexes(*la):
                    if va * 3.6 < VMAX:
                        pts.append((va * 3.6, al / G))
    return pts


def full_q(session, car):
    num = driver_num(session, car); cd = session.car_data[num]
    tc = cd["SessionTime"].dt.total_seconds().to_numpy()
    spd = cd["Speed"].to_numpy(float) / 3.6
    thr = cd["Throttle"].to_numpy(float); brk = cd["Brake"].to_numpy(float); drs = cd["DRS"].to_numpy(float)
    rows = []
    for ls, le in flying_windows(session, car):
        m = (tc >= ls) & (tc <= le)
        t, v, th, bk, dr = tc[m], spd[m], thr[m], brk[m], drs[m]
        o = np.argsort(t); t, v, th, bk, dr = t[o], v[o], th[o], bk[o], dr[o]
        keep = np.concatenate([[True], np.diff(t) > 1e-9]); t, v, th, bk, dr = t[keep], v[keep], th[keep], bk[keep], dr[keep]
        for i in range(1, len(t) - 1):
            dt = t[i + 1] - t[i - 1]
            if dt > 0 and th[i] > 95 and bk[i] < 1 and v[i] > VMIN_PD:
                rows.append((v[i], (v[i + 1] - v[i - 1]) / dt, dr[i]))
    return rows


def fit_grip(apex, gsat=5.2):
    """Car differences from the RELIABLE slow/medium regime only; saturation
    fixed COMMON (high-speed car differences are below the v^2/R noise floor)."""
    a = np.array(apex); v, g = a[:, 0], a[:, 1]
    edges = np.arange(40, 156, 12); vb, cb, sb = [], [], []   # reliable regime only
    for lo, hi in zip(edges[:-1], edges[1:]):
        b = (v >= lo) & (v < hi)
        if b.sum() >= 6:
            vb.append(v[b].mean()); cb.append(np.quantile(g[b], 0.90)); sb.append(0.06)

    def m2(vv, A, B):
        return np.minimum(A + B * vv**2, gsat)
    popt, _ = curve_fit(m2, np.array(vb) / 3.6, cb, p0=[1.8, 0.0018],
                        sigma=sb, bounds=([1.0, 0.0005], [3.0, 0.005]), maxfev=20000)
    return popt[0], popt[1], gsat   # A, B, common Gsat


def fit_pd(full):
    d = np.array(full); v, a, drs = d[:, 0], d[:, 1], d[:, 2]
    op = drs >= 10
    X = np.column_stack([1 / (MASS * v), -0.5 * RHO * v**2 / MASS * (~op), -0.5 * RHO * v**2 / MASS * op])
    coef, *_ = np.linalg.lstsq(X, a, rcond=None)
    return coef   # P, CdA_c, CdA_o


def ideal_time(s, kappa, A, B, GS, P, cc, co):
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
    return float(np.sum(ds / ((v[:-1] + v[1:]) / 2))) * LEN / s[-1]


def main():
    q = H.load_session(2023, "Japan", "Q")
    r = H.load_session(2023, "Japan", "R")
    d = np.load(OUT / "ribbon_suzuka.npz"); s, kappa = d["s"], d["kappa"]
    res = {}
    for team, drvs in TEAMS.items():
        apex, full = [], []
        for car in drvs:
            try:
                apex += apex_q(q, car) + apex_r(r, car)
                full += full_q(q, car)
            except Exception as e:
                log(f"  {team}/{car}: {e}")
        if len(apex) < 100 or len(full) < 40:
            log(f"{team}: thin data ({len(apex)} apex, {len(full)} full), skip")
            continue
        A, B, GS = fit_grip(apex)
        P, cc, co = fit_pd(full)
        t_id = ideal_time(s, kappa, A, B, GS, P, cc, co)
        res[team] = dict(A=A, B=B, GS=GS, P=P, cc=cc, co=co, t=t_id, n=len(apex))
        log(f"{team}: Gsat={GS:.2f} CdA={cc:.2f} P={P/1e3:.0f}kW -> ideal {t_id:.2f}s ({len(apex)} apex)")

    print("\n=== constructor ideals (pooled teammates) ===")
    print(f"{'team':>5} {'Gsat':>5} {'CdA':>5} {'P(kW)':>6} {'ideal(s)':>9}")
    for team, p in sorted(res.items(), key=lambda kv: kv[1]["t"]):
        print(f"{team:>5} {p['GS']:5.2f} {p['cc']:5.2f} {p['P']/1e3:6.0f} {p['t']:9.2f}")
    print("\n(2023 Suzuka quali reality: RBR pole, McLaren P3/P5, Ferrari/Merc mid, Williams back.\n"
          " correct ranking would put RBR fastest ideal.)")


if __name__ == "__main__":
    main()
