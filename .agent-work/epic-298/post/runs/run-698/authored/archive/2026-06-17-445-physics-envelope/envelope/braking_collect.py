"""Longitudinal (braking) grip-node extractor — the 'consider along in its own axis' path (#445).

Cornering nodes gate alat>0.6 (mid-corner); braking lives in the OPPOSITE regime:
high speed, near-straight (low alat), strong deceleration (along<<0). Build a separate
cloud (v, |decel| in g, w) and fit a longitudinal frontier G_long(v)=A+B v^2.

Physics: a_brake ~ mu*g + (mu*downforce + drag)*v^2/m  => B_long mixes DOWNFORCE+DRAG
(lateral B was downforce only). along is dv/dt from the ~4.2Hz speed channel => peak
decel is sub-sample, so this is a consistent LOWER BOUND, not absolute. Accel (along>0)
is POWER-limited not grip-limited => excluded.

Run:  py braking_collect.py sanity   -> 1 round diagnostics (counts, decel/speed ranges)
      py braking_collect.py          -> full 22-round extraction -> braking_nodes_full.npz
"""
from __future__ import annotations

import logging
import sys
import time
import warnings
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")
warnings.filterwarnings("ignore")
logging.getLogger("fastf1").setLevel(logging.ERROR)

import grip_iter as GI  # noqa: E402

OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
CACHE = OUT / "braking_nodes_full.npz"
ROUNDS = list(range(1, 23))
CARS = ["VER", "PER", "HAM", "RUS", "LEC", "SAI", "NOR", "PIA", "ALO", "STR",
        "GAS", "OCO", "ALB", "SAR", "TSU", "DEV", "RIC", "LAW", "BOT", "ZHO",
        "MAG", "HUL"]
G = GI.G
BRAKE_MIN = 1.2      # g, firm-ish braking (keep combined trail-brake points)
W = 3                # half-window for the decel slope fit
MIN_NODES = 25
# Pure straight-line braking ~doesn't exist (diagnostic: 2 pts/driver). Keep ALL
# firm-braking points WITH their lateral load so the fit can ellipse-project the
# combined trail-braking cloud onto the longitudinal axis. No lat gate, no speed cap.


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def _alat(X, Y, vi, i, n):
    a, b = max(0, i - 5), min(n, i + 6)
    if b - a < 5:
        return 0.0
    xx, yy = X[a:b], Y[a:b]
    M = np.column_stack([xx, yy, np.ones_like(xx)])
    try:
        sol, *_ = np.linalg.lstsq(M, -(xx**2 + yy**2), rcond=None)
    except Exception:
        return 0.0
    cx, cy = -sol[0] / 2, -sol[1] / 2
    r2 = cx**2 + cy**2 - sol[2]
    if r2 <= 25:                       # nearly straight -> alat ~ 0
        return 0.0
    return vi ** 2 / np.sqrt(r2) / G


def emit_braking(t, X, Y, v, base_w=1.0):
    """Keep firm-braking points with their lateral load: (v, alat, decel>0, w)."""
    n = len(v); pts = []
    for i in range(n):
        c, d = i - W, i + W + 1
        if c < 0 or d > n:
            continue
        tt = t[c:d] - t[c]; vv = v[c:d]
        if tt[-1] - tt[0] <= 0:
            continue
        slope = np.polyfit(tt, vv, 1)[0] / G        # g (negative under braking)
        if slope > -BRAKE_MIN:                      # need firm braking; exclude accel
            continue
        alat = _alat(X, Y, v[i], i, n)
        pts.append((v[i], alat, -slope, base_w))    # decel as +g
    return pts


def collect_braking(session, car):
    runs = GI.H.driver_runs(session, car)
    fits, pts = {}, []
    for ls, le in GI.flying_windows(session, car):
        run = next((r for r in runs if r["t0"] <= ls and r["t1"] >= le), None)
        if run is None:
            continue
        key = (round(run["t0"], 1), round(run["t1"], 1))
        ss = fits.get(key)
        if ss is None:
            ss = GI.H.StintSmoother(2.0, 100.0, 0.3, 0.06, iters=2)
            ss.fit(run["tp"], run["X"], run["Y"], run["tc"], run["V"]); fits[key] = ss
        mask = (ss.kind == 1) & (ss.ts >= ls) & (ss.ts <= le)
        t = ss.ts[mask]; o = np.argsort(t); t = t[o]
        keep = np.concatenate([[True], np.diff(t) > 1e-9]); t = t[keep]
        X, Y = ss.pos_at(t); v = np.interp(t, run["tc"], run["V"])
        pts += emit_braking(t, X, Y, v, base_w=1.0)
    return pts


def sanity():
    q = GI.H.load_session(2023, 1, "Q")
    print("BAHRAIN braking-node sanity (decel in g, speed in km/h):")
    for c in ["VER", "PER", "HAM", "RUS", "LEC", "SAI"]:
        try:
            pts = collect_braking(q, c)
        except Exception as e:
            print(f"  {c}: ERR {e}"); continue
        if not pts:
            print(f"  {c}: 0 nodes"); continue
        p = np.array(pts)   # v, alat, decel, w
        print(f"  {c}: {len(pts):4d} nodes | decel g med {np.median(p[:,2]):.2f} "
              f"max {p[:,2].max():.2f} | alat g med {np.median(p[:,1]):.2f} | "
              f"speed km/h {p[:,0].min()*3.6:.0f}-{p[:,0].max()*3.6:.0f}")


def full():
    OUT.mkdir(parents=True, exist_ok=True)
    store = {}; rnames = []; t_start = time.time()
    for r in ROUNDS:
        t0 = time.time()
        try:
            q = GI.H.load_session(2023, r, "Q")
        except Exception as e:
            log(f"round {r}: LOAD FAILED {e}"); continue
        ev = getattr(q, "event", None)
        nm = str(ev["EventName"]).replace(" Grand Prix", "") if ev is not None else str(r)
        rnames.append(nm); n_ok = 0
        for c in CARS:
            try:
                pts = collect_braking(q, c)
            except Exception:
                continue
            if len(pts) < MIN_NODES:
                continue
            p = np.array(pts)   # v, alat, decel, w
            store[f"v__{nm}__{c}"] = p[:, 0].astype(np.float32)
            store[f"alat__{nm}__{c}"] = p[:, 1].astype(np.float32)
            store[f"d__{nm}__{c}"] = p[:, 2].astype(np.float32)
            store[f"w__{nm}__{c}"] = p[:, 3].astype(np.float32)
            n_ok += 1
        log(f"round {r:>2} {nm:16s} {time.time()-t0:5.1f}s  {n_ok} cars")
    store["rounds"] = np.array(rnames); store["cars"] = np.array(CARS)
    np.savez_compressed(CACHE, **store)
    log(f"wrote {CACHE}  ({(len(store)-2)//4} clouds)  elapsed {time.time()-t_start:.0f}s")


if __name__ == "__main__":
    (sanity if len(sys.argv) > 1 and sys.argv[1] == "sanity" else full)()
