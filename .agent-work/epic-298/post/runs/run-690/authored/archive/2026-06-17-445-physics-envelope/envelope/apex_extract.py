"""Apex-speed / corner-time extraction on CLEAN calibrated kinematics (#445).

For every (round, car), on every flying quali lap, segment corners as a_lat peaks
and record per-corner geometry:
  - v_apex   : minimum speed in the corner window (m/s)  -- THE pace-relevant observable
  - R_apex   : adaptive circle-fit radius at the apex (m) -- corner geometry (track, not car)
  - alat_apex: lateral g at the apex
  - s_in/s_out, t_in/t_out: corner extent in arc / time, for corner-traversal time
  - v_in, v_out : entry/exit speed (for braking-in / traction-out decomposition)

Uses the SAME per-session calibrated smoother as calibrated_extract.py (chi2~=1),
so kinematics are clean. Pools corners across all flying laps for stability.

Cache: apex_corners.npz  (flat columns; one row per detected corner per lap)
Run:  py apex_extract.py sanity   (round 1, VER+MAG, prints corners)
      py apex_extract.py          (full 22 rounds, all cars -> npz)
"""
from __future__ import annotations

import json
import logging
import sys
import time
import warnings
from pathlib import Path

import numpy as np
from scipy.signal import find_peaks

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")
warnings.filterwarnings("ignore")
logging.getLogger("fastf1").setLevel(logging.ERROR)

import grip_iter as GI  # noqa: E402
from src.preprocessing.trajectory.smoother import StintSmoother  # noqa: E402
from src.preprocessing.trajectory.calibration import session_offset, fit_stint_hp  # noqa: E402

G = 9.81
OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
NPZ = OUT / "apex_corners.npz"
ROUNDS = list(range(1, 23))
CARS = ["VER", "PER", "HAM", "RUS", "LEC", "SAI", "NOR", "PIA", "ALO", "STR",
        "GAS", "OCO", "ALB", "SAR", "TSU", "DEV", "RIC", "LAW", "BOT", "ZHO",
        "MAG", "HUL"]
CAL_CARS = ["VER", "HAM", "LEC", "NOR", "RUS"]

# corner detection params (validated on Suzuka in corner_segment.py)
A_THR = 5.0       # min apex lateral accel (m/s^2)
PROM = 4.0        # peak prominence in a_lat(s)
VMIN_KMH = 40.0   # ignore pit/slow
DIST = 4          # min nodes between peaks


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def _stream(run):
    return (np.asarray(run["tp"], float), np.asarray(run["X"], float),
            np.asarray(run["Y"], float), np.asarray(run["tc"], float),
            np.asarray(run["V"], float))


def calibrate(q):
    streams = []
    for c in CAL_CARS:
        runs = GI.H.driver_runs(q, c)
        if runs:
            streams.append(_stream(max(runs, key=lambda r: len(r["X"]))))
    if not streams:
        return None
    delta, _ = session_offset(streams)
    s = max(streams, key=lambda S: len(S[0]))
    hp = fit_stint_hp(s[0], s[1], s[2], s[3], s[4], delta=delta, iters=3)
    if hp is None:
        return None
    hp["delta"] = float(delta)
    return hp


def circle_fit(x, y):
    A = np.column_stack([x, y, np.ones_like(x)])
    b = -(x**2 + y**2)
    sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    a, bb, c = sol
    cx, cy = -a / 2, -bb / 2
    r2 = cx**2 + cy**2 - c
    return float(np.sqrt(r2)) if r2 > 0 else np.nan


def adaptive_radius(X, Y, N=5):
    n = len(X)
    R = np.full(n, np.nan)
    for i in range(n):
        a, b = max(0, i - N), min(n, i + N + 1)
        if b - a >= 5:
            r = circle_fit(X[a:b], Y[a:b])
            if np.isfinite(r) and 3 < r < 5000:
                R[i] = r
    return R


def lap_geometry(ss, run, ls, le):
    mask = (ss.kind == 1) & (ss.ts >= ls) & (ss.ts <= le)
    t = ss.ts[mask]
    order = np.argsort(t)
    t = t[order]
    keep = np.concatenate([[True], np.diff(t) > 1e-9])
    t = t[keep]
    if len(t) < 50:
        return None
    X, Y = ss.pos_at(t)
    v = np.interp(t, run["tc"], run["V"])
    s = np.concatenate([[0.0], np.cumsum(0.5 * (v[1:] + v[:-1]) * np.diff(t))])
    R = adaptive_radius(X, Y, N=5)
    alat = v**2 / R
    return dict(t=t, X=X, Y=Y, v=v, s=s, R=R, alat=alat)


def detect_corners(geo):
    alat = np.nan_to_num(geo["alat"], nan=0.0)
    idx, _ = find_peaks(alat, height=A_THR, prominence=PROM, distance=DIST)
    idx = [i for i in idx if geo["v"][i] * 3.6 > VMIN_KMH and np.isfinite(geo["R"][i])]
    return idx


def corner_records(geo, idx):
    """For each detected apex, locate the local speed MINIMUM (true apex speed) and
    the corner window (between bracketing a_lat troughs), record geometry+timing."""
    v = geo["v"]; s = geo["s"]; t = geo["t"]; R = geo["R"]; alat = geo["alat"]
    n = len(v)
    alat_f = np.nan_to_num(alat, nan=0.0)
    recs = []
    for i in idx:
        # search a small window around the a_lat peak for the true min-speed apex
        a, b = max(0, i - 4), min(n, i + 5)
        j = a + int(np.argmin(v[a:b]))     # min-speed node (apex)
        Rj = R[j] if np.isfinite(R[j]) else R[i]
        if not np.isfinite(Rj):
            continue
        # corner window: walk out from the peak until a_lat drops below half-apex
        thr = 0.5 * alat_f[i]
        lo = i
        while lo > 0 and alat_f[lo] > thr:
            lo -= 1
        hi = i
        while hi < n - 1 and alat_f[hi] > thr:
            hi += 1
        v_in = v[lo]; v_out = v[hi]
        dt = t[hi] - t[lo]
        ds = s[hi] - s[lo]
        recs.append(dict(
            v_apex=float(v[j]), R_apex=float(Rj), alat_apex=float(alat_f[i] / G),
            v_in=float(v_in), v_out=float(v_out),
            corner_dt=float(dt), corner_ds=float(ds),
            s_apex=float(s[j]),
        ))
    return recs


def collect_car(session, car, hp):
    runs = GI.H.driver_runs(session, car)
    fits = {}
    allrecs = []
    for ls, le in GI.flying_windows(session, car):
        run = next((r for r in runs if r["t0"] <= ls and r["t1"] >= le), None)
        if run is None:
            continue
        key = (round(run["t0"], 1), round(run["t1"], 1))
        ss = fits.get(key)
        if ss is None:
            ss = StintSmoother(hp["ell"], hp["sf"], hp["sig_pos"], hp["delta"], iters=2)
            ss.fit(run["tp"], run["X"], run["Y"], run["tc"], run["V"])
            fits[key] = ss
        geo = lap_geometry(ss, run, ls, le)
        if geo is None:
            continue
        idx = detect_corners(geo)
        allrecs += corner_records(geo, idx)
    return allrecs


def sanity():
    q = GI.H.load_session(2023, 1, "Q")
    hp = calibrate(q)
    print(f"Bahrain HP: ell={hp['ell']:.2f} sig_pos={hp['sig_pos']:.2f} "
          f"delta={hp['delta']:.3f} chi2_pos={hp['chi2_pos']:.2f}")
    for c in ["VER", "MAG"]:
        recs = collect_car(q, c, hp)
        if not recs:
            print(f"  {c}: no corners"); continue
        va = np.array([r["v_apex"] for r in recs]) * 3.6
        Ra = np.array([r["R_apex"] for r in recs])
        print(f"  {c}: {len(recs)} corner-records  "
              f"v_apex {va.min():.0f}-{va.max():.0f} km/h (med {np.median(va):.0f}), "
              f"R {Ra.min():.0f}-{Ra.max():.0f} m")


def full():
    OUT.mkdir(parents=True, exist_ok=True)
    cols = {k: [] for k in ["round", "car", "v_apex", "R_apex", "alat_apex",
                            "v_in", "v_out", "corner_dt", "corner_ds", "s_apex"]}
    rnames = []
    t_start = time.time()
    for r in ROUNDS:
        t0 = time.time()
        try:
            q = GI.H.load_session(2023, r, "Q")
        except Exception as e:
            log(f"round {r}: LOAD FAILED {e}"); continue
        ev = getattr(q, "event", None)
        nm = str(ev["EventName"]).replace(" Grand Prix", "") if ev is not None else str(r)
        rnames.append(nm)
        hp = calibrate(q)
        if hp is None:
            log(f"round {r:>2} {nm}: CAL FAILED, skip"); continue
        ncars = 0; ncorn = 0
        for c in CARS:
            try:
                recs = collect_car(q, c, hp)
            except Exception:
                continue
            if not recs:
                continue
            ncars += 1; ncorn += len(recs)
            for rec in recs:
                cols["round"].append(nm)
                cols["car"].append(c)
                for k in ["v_apex", "R_apex", "alat_apex", "v_in", "v_out",
                          "corner_dt", "corner_ds", "s_apex"]:
                    cols[k].append(rec[k])
        log(f"round {r:>2} {nm:16s} {time.time()-t0:5.0f}s  {ncars} cars  "
            f"{ncorn} corners  ell={hp['ell']:.1f} d={hp['delta']:.2f} "
            f"X2p={hp['chi2_pos']:.1f}")
    store = {k: np.array(v) for k, v in cols.items()}
    store["round"] = np.array(cols["round"])
    store["car"] = np.array(cols["car"])
    store["rounds"] = np.array(rnames)
    np.savez_compressed(NPZ, **store)
    log(f"wrote {NPZ.name}  ({len(cols['v_apex'])} corner-records, "
        f"{len(set(zip(cols['round'], cols['car'])))} car-weekends)  "
        f"elapsed {time.time()-t_start:.0f}s")


if __name__ == "__main__":
    (sanity if len(sys.argv) > 1 and sys.argv[1] == "sanity" else full)()
