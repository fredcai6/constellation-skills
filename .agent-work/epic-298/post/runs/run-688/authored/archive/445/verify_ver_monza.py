"""Step-by-step verification of VER @ Monza 2023 via the EXPLORATION tools.

Re-establishes the ground truth one layer at a time so we have a trusted baseline.
Run a single step:  py .agent-work/445/verify_ver_monza.py --step 1
"""
from __future__ import annotations

import argparse
import logging
import sys
import warnings

import numpy as np

sys.path.insert(0, "C:/Programs/f1Brainz/.agent-work/445/envelope")
sys.path.insert(0, "C:/Programs/f1Brainz")
warnings.filterwarnings("ignore")
logging.getLogger("fastf1").setLevel(logging.ERROR)
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from ribbon_reeval import load_session, driver_num  # noqa: E402
from src.preprocessing.trajectory.loaders import driver_streams  # noqa: E402
from src.preprocessing.trajectory.calibration import session_offset, fit_stint_hp  # noqa: E402
from src.preprocessing.trajectory.smoother import StintSmoother  # noqa: E402

YEAR, GP, DRV = 2023, "Italy", "VER"   # Monza = Italian GP
PAD = 2.0


def fastest_lap_window(q, drv):
    laps = q.laps.pick_drivers(drv)
    valid = laps[laps["LapTime"].notna()]
    fast = valid.loc[valid["LapTime"].dt.total_seconds().idxmin()]
    return (float(fast["LapStartTime"].total_seconds()),
            float(fast["Time"].total_seconds()),
            int(fast["LapNumber"]),
            float(fast["LapTime"].total_seconds()))


def step1_trajectory():
    print("=" * 64)
    print("STEP 1 — first-order trajectory (calibrated smoother), VER @ Monza '23 Q")
    print("=" * 64)
    q = load_session(YEAR, GP, "Q")
    t0, t1, lapnum, laptime = fastest_lap_window(q, DRV)
    print(f"VER fastest Q lap: {laptime:.3f}s (lap {lapnum}); window {t0:.1f}–{t1:.1f}s "
          f"(dur {t1 - t0:.2f}s).  [Monza '23 pole VER 1:20.294]")

    num = driver_num(q, DRV)
    pos_d, spd_d = driver_streams(q, num)
    tp, X, Y = pos_d["t"], pos_d["X"], pos_d["Y"]
    tc, V = spd_d["t"], spd_d["V"]

    mp = (tp >= t0 - PAD) & (tp <= t1 + PAD)
    mc = (tc >= t0 - PAD) & (tc <= t1 + PAD)
    tp_l, X_l, Y_l = tp[mp], X[mp], Y[mp]
    tc_l, V_l = tc[mc], V[mc]
    dt_med = float(np.median(np.diff(tp_l)))
    print(f"raw streams (in lap window): {mp.sum()} position pts (dt_med {dt_med:.3f}s), "
          f"{mc.sum()} speed pts; raw speed top {V_l.max() * 3.6:.0f} km/h")

    delta, _ = session_offset([(tp_l, X_l, Y_l, tc_l, V_l)])
    hp = fit_stint_hp(tp_l, X_l, Y_l, tc_l, V_l, delta=delta, iters=3)
    print(f"calibrated smoother HP: ell={hp['ell']:.2f}s  sf={hp['sf']:.0f}  "
          f"sig_pos={hp['sig_pos']:.2f}m  delta={hp['delta']:.3f}s")
    print(f"  HELD-OUT honesty:  chi2_pos={hp['chi2_pos']:.2f}  chi2_spd={hp['chi2_spd']:.2f}   "
          f"(target ≈ 1.0 — over-trust shows as >>1)")

    ss = StintSmoother(hp["ell"], hp["sf"], hp["sig_pos"], hp["delta"], iters=3)
    ss.fit(tp_l, X_l, Y_l, tc_l, V_l)

    # Sample the smoothed PATH over the flying lap only
    qm = (tp >= t0) & (tp <= t1)
    tq = tp[qm]
    Xs, Ys = ss.pos_at(tq)
    s = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(Xs), np.diff(Ys)))])
    Vq = np.interp(tq, tc_l, V_l)   # speed channel sampled on the lap

    # Geometry: curvature -> tightest radius
    th = np.unwrap(np.arctan2(np.gradient(Ys, s), np.gradient(Xs, s)))
    kappa = np.convolve(np.gradient(th, s), np.ones(9) / 9, mode="same")
    kmax = float(np.abs(kappa).max())
    Rmin = 1.0 / kmax if kmax > 1e-6 else float("inf")

    print(f"smoothed path length: {s[-1]:.0f} m            [Monza lap ≈ 5793 m]")
    print(f"speed on lap:         top {Vq.max() * 3.6:.0f} km/h, min {Vq.min() * 3.6:.0f} km/h   "
          f"[Monza top ≈ 355 km/h, 1st chicane ≈ 80 km/h]")
    print(f"tightest radius:      {Rmin:.0f} m")
    print("\nLayer-1 verdict cues: chi2 ≈ 1 (honest fit, no noise-tracking), top speed ~355 km/h,")
    print("path length ~5.8 km, a tight (~25–40 m) chicane radius — all physical = trajectory OK.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", type=int, default=1)
    args = ap.parse_args()
    if args.step == 1:
        step1_trajectory()
    else:
        print(f"step {args.step} not implemented yet")
