"""Re-extract quali cornering nodes keeping a_lat and a_long SEPARATE (#445 anisotropy).

emit_nodes() already computes alat (from circle-fit radius) and along (from dv/dt) then
hypots them into g_tot and discards the split. This vendors emit_nodes/collect_nodes
verbatim EXCEPT it keeps the two components, so we can test an anisotropic frontier
(pure-lateral grip vs the combined magnitude) without touching the shared module.

Cache aniso_nodes_full.npz: per round per car -> v, alat, along, w (float32).
NOTE the cloud is CORNERING nodes (alat>0.6, v<VMAX); 'along' is the entry/exit
longitudinal component DURING the corner (trail-brake / on-power), not straight-line
braking. So this supports lateral-vs-combined, not a clean straight-line longitudinal
axis (that needs separate braking-zone extraction, sensor-capped).
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
CACHE = OUT / "aniso_nodes_full.npz"
ROUNDS = list(range(1, 23))
CARS = ["VER", "PER", "HAM", "RUS", "LEC", "SAI", "NOR", "PIA", "ALO", "STR",
        "GAS", "OCO", "ALB", "SAR", "TSU", "DEV", "RIC", "LAW", "BOT", "ZHO",
        "MAG", "HUL"]
MIN_NODES = 25
G = GI.G
VMAX = GI.VMAX


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def emit_nodes_aniso(t, X, Y, v, base_w=1.0):
    """Verbatim grip_iter.emit_nodes but returns (v, alat, along, w) per node."""
    n = len(v); pts = []
    for i in range(n):
        a, b = max(0, i - 5), min(n, i + 6)
        if b - a < 5:
            continue
        xx, yy = X[a:b], Y[a:b]
        M = np.column_stack([xx, yy, np.ones_like(xx)])
        sol, *_ = np.linalg.lstsq(M, -(xx**2 + yy**2), rcond=None)
        cx, cy = -sol[0] / 2, -sol[1] / 2
        r2 = cx**2 + cy**2 - sol[2]
        if r2 <= 9:
            continue
        R = np.sqrt(r2)
        resid = np.sqrt(np.mean((np.hypot(xx - cx, yy - cy) - R) ** 2))
        q = resid / R
        if q > 0.03 or v[i] * 3.6 > VMAX:
            continue
        alat = v[i] ** 2 / R / G
        if alat < 0.6:
            continue
        c, dd = max(0, i - 1), min(n, i + 2)
        dt = t[dd - 1] - t[c]
        along = (v[dd - 1] - v[c]) / dt / G if dt > 0 else 0.0
        w = base_w / (q + 0.005) ** 2
        pts.append((v[i], alat, along, w))
    return pts


def collect_nodes_aniso(session, car):
    """Verbatim grip_iter.collect_nodes but using emit_nodes_aniso."""
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
        pts += emit_nodes_aniso(t, X, Y, v, base_w=1.0)
    return pts


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    store = {}; rnames = []; t_start = time.time()
    for r in ROUNDS:
        t0 = time.time()
        try:
            q = GI.H.load_session(2023, r, "Q")
        except Exception as e:
            log(f"round {r}: LOAD FAILED {e}")
            continue
        ev = getattr(q, "event", None)
        nm = str(ev["EventName"]).replace(" Grand Prix", "") if ev is not None else str(r)
        rnames.append(nm); n_ok = 0
        for c in CARS:
            try:
                pts = collect_nodes_aniso(q, c)
            except Exception:
                continue
            if len(pts) < MIN_NODES:
                continue
            p = np.array(pts)
            store[f"v__{nm}__{c}"] = p[:, 0].astype(np.float32)
            store[f"alat__{nm}__{c}"] = p[:, 1].astype(np.float32)
            store[f"along__{nm}__{c}"] = p[:, 2].astype(np.float32)
            store[f"w__{nm}__{c}"] = p[:, 3].astype(np.float32)
            n_ok += 1
        log(f"round {r:>2} {nm:16s} {time.time()-t0:5.1f}s  {n_ok} cars")
    store["rounds"] = np.array(rnames); store["cars"] = np.array(CARS)
    np.savez_compressed(CACHE, **store)
    log(f"wrote {CACHE}  ({(len(store)-2)//4} clouds)  elapsed {time.time()-t_start:.0f}s")


if __name__ == "__main__":
    main()
