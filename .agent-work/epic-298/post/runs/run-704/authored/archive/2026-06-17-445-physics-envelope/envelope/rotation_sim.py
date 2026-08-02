"""Simple rotation model: yaw-rate-limited idealized lap (epic #445).

Quasi-static lets the car snap between full-lateral and full-longitudinal. Add a
rotation constraint: yaw rate psi_dot = v*kappa can't change faster than psi_dd_max
(tyres generate finite yaw moment vs the car's rotational inertia). Forward pass:
yaw rate can't RISE too fast (entry turn-in); backward: can't FALL too fast (exit
unwind -> delayed deploy). Estimate psi_dd_max from the actual car. Does the ideal
slow toward the real lap (higher utilization)?
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "C:/Programs/f1Brainz")

import harvest_envelope as H  # noqa: E402

G, RHO, MASS = 9.81, 1.2, 808.0
OUT = Path("C:/Programs/f1Brainz/.agent-work/445/envelope")
A, B, GSAT, P_ENG, CC, CO = 1.90, 0.00177, 4.95, 525e3, 1.53, 0.97
LEN = 5807
VER_QUALI = 88.88


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def Gv(v):
    return min(A + B * v * v, GSAT)


def drag(v, k):
    return 0.5 * RHO * (CO if (abs(k) < 8e-4 and v > 200 / 3.6) else CC) * v * v / MASS


def estimate_psidd_max():
    """From VER's actual lap: yaw rate v*kappa, its rate of change, high pct."""
    session = H.load_session(2023, "Japan", "Q")
    laps = session.laps.pick_drivers("VER"); laps = laps[laps["LapTime"].notna()]
    fl = laps.loc[laps["LapTime"].idxmin()]
    ls, le = fl["LapStartTime"].total_seconds(), fl["Time"].total_seconds()
    runs = H.driver_runs(session, "VER")
    run = next((r for r in runs if r["t0"] <= ls and r["t1"] >= le),
               max(runs, key=lambda r: r["t1"] - r["t0"]))
    ss = H.StintSmoother(2.0, 100.0, 0.3, 0.06, iters=2)
    ss.fit(run["tp"], run["X"], run["Y"], run["tc"], run["V"])
    mask = (ss.kind == 1) & (ss.ts >= ls) & (ss.ts <= le)
    t = ss.ts[mask]; o = np.argsort(t); t = t[o]
    keep = np.concatenate([[True], np.diff(t) > 1e-9]); t = t[keep]
    Xd, Yd = ss.vel_at(t)
    psi = np.unwrap(np.arctan2(Yd, Xd))                # heading from velocity (clean)
    psidot = np.gradient(psi, t)                       # yaw rate
    psidot = np.convolve(psidot, np.ones(5) / 5, mode="same")
    psidd = np.gradient(psidot, t)
    return float(np.percentile(np.abs(psidd), 92))


def simulate(s, kappa, psidd_max=None):
    kappa = np.abs(kappa); n = len(s); ds = np.diff(s)
    vg = np.sqrt(GSAT * G / np.maximum(kappa, 1e-6))
    for _ in range(10):
        vg = np.minimum(np.sqrt(np.array([Gv(x) for x in vg]) * G / np.maximum(kappa, 1e-6)), 100.0)
    v = vg.copy()
    for _ in range(5):
        for i in range(n - 1):
            al = v[i] ** 2 * kappa[i] / G
            tr = np.sqrt(max(Gv(v[i]) ** 2 - al ** 2, 0)) * G
            a = min(tr, P_ENG / (MASS * max(v[i], 1.0))) - drag(v[i], kappa[i])
            vn = np.sqrt(max(v[i] ** 2 + 2 * a * ds[i], 1.0))
            if psidd_max is not None and kappa[i + 1] > 1e-4:
                dt = ds[i] / max(v[i], 1.0)
                vyaw = (v[i] * kappa[i] + psidd_max * dt) / kappa[i + 1]   # yaw can't rise too fast
                vn = min(vn, vyaw)
            v[i + 1] = min(v[i + 1], vn, vg[i + 1])
        for i in range(n - 2, -1, -1):
            al = v[i + 1] ** 2 * kappa[i + 1] / G
            tr = np.sqrt(max(Gv(v[i + 1]) ** 2 - al ** 2, 0)) * G
            vp = np.sqrt(max(v[i + 1] ** 2 + 2 * (tr + drag(v[i + 1], kappa[i + 1])) * ds[i], 1.0))
            if psidd_max is not None and kappa[i] > 1e-4:
                dt = ds[i] / max(v[i + 1], 1.0)
                vyaw = (v[i + 1] * kappa[i + 1] + psidd_max * dt) / kappa[i]  # yaw can't fall too fast
                vp = min(vp, vyaw)
            v[i] = min(v[i], vp, vg[i])
    t = float(np.sum(ds / ((v[:-1] + v[1:]) / 2))) * LEN / s[-1]
    return t, v


def main():
    log("estimating yaw-acceleration capability from VER's actual lap ...")
    psidd_max = estimate_psidd_max()
    log(f"  psi_dd_max ~ {psidd_max:.1f} rad/s^2")
    d = np.load(OUT / "ribbon_suzuka.npz"); s, kappa = d["s"], np.abs(d["kappa"])
    t_qs, _ = simulate(s, kappa, None)
    t_rot, vr = simulate(s, kappa, psidd_max)
    log(f"\nquasi-static ideal:       {t_qs:.2f}s  (util {100*t_qs/VER_QUALI:.1f}%)")
    log(f"rotation-limited ideal:   {t_rot:.2f}s  (util {100*t_rot/VER_QUALI:.1f}%)")
    log(f"VER actual:               {VER_QUALI:.2f}s")
    log(f"  rotation limit cost {t_rot - t_qs:+.2f}s; remaining gap to actual "
        f"{VER_QUALI - t_rot:.2f}s")
    # sweep to see sensitivity
    print("\n  psi_dd_max sweep:")
    for pdd in [psidd_max * 0.6, psidd_max, psidd_max * 1.6, 1e9]:
        tt, _ = simulate(s, kappa, pdd if pdd < 1e8 else None)
        lab = f"{pdd:.0f}" if pdd < 1e8 else "inf (quasi-static)"
        print(f"    psi_dd_max={lab:>20}: ideal {tt:.2f}s, util {100*tt/VER_QUALI:.1f}%")


if __name__ == "__main__":
    main()
