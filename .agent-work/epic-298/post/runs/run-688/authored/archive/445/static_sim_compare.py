"""STATIC sim-engine comparison: exploration `ideal_time` vs production
`PhysicsSimulator.simulate_lap`, on IDENTICAL geometry + IDENTICAL physics params.

We reproduce the exploration's EXACT params by calling ribbon_reeval's own
functions (Hungary Q is cached), so the exploration leg reproduces its recorded
74.79 s.  Then we feed those identical (A, B, GS, P, CdA) numbers to the
production simulator on the SAME cached ribbon and diff.  Any difference is pure
sim-engine code.

Baseline: RBR (VER) @ Hungary 2023 — the only "best-behaved" track in the notes.

Run:  py .agent-work/445/static_sim_compare.py
"""
from __future__ import annotations

import logging
import sys
import warnings
from pathlib import Path

import numpy as np

sys.path.insert(0, "C:/Programs/f1Brainz/.agent-work/445/envelope")
sys.path.insert(0, "C:/Programs/f1Brainz")
warnings.filterwarnings("ignore")
logging.getLogger("fastf1").setLevel(logging.ERROR)
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import ribbon_reeval as RR  # noqa: E402
from src.physics.physics_config import PhysicsEstimatorConfig          # noqa: E402
from src.physics.physics_data_models import (                          # noqa: E402
    LateralParameters, LongitudinalParameters, PhysicsParameterSet,
)
from src.physics.physics_simulator import PhysicsSimulator             # noqa: E402

G, RHO, MASS = RR.G_CONST, RR.RHO, RR.MASS          # 9.81, 1.2, 808
GP, HP_KEY, LENGTH = "Hungary", "Hungarian", 4381.0
TEAM, CARS = "RBR", ["VER", "PER"]
RIBBON = Path("C:/Programs/f1Brainz/.agent-work/445/envelope/ribbon_clean_hungary.npz")


def expl_ideal_profile(s, kappa, A, B, GS, P, cc, co, length, drs_open=True, gsat_on=True):
    """ribbon_reeval.ideal_time, instrumented to also return the speed profile."""
    kappa = np.abs(kappa)
    n = len(s)
    ds = np.diff(s)
    gs_eff = GS if gsat_on else 1e9

    def Gv(v):
        return min(A + B * v * v, gs_eff)

    def drag(v, k):
        cda = co if (drs_open and abs(k) < 8e-4 and v > 200 / 3.6) else cc
        return 0.5 * RHO * cda * v * v / MASS

    vg = np.sqrt(gs_eff * G / np.maximum(kappa, 1e-6))
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
            a_b = tr + drag(v[i + 1], kappa[i + 1])
            v[i] = min(v[i], np.sqrt(max(v[i + 1] ** 2 + 2 * a_b * ds[i], 1.0)), vg[i])
    t_sim = float(np.sum(ds / ((v[:-1] + v[1:]) / 2)))
    return t_sim * length / s[-1], v


def make_prod_params(A, B, P, cda_closed):
    longi = LongitudinalParameters(
        theta_D=cda_closed / (2.0 * MASS), theta_R=0.0, theta_D_std=0.0, theta_R_std=0.0,
        theta_P_times=np.array([0.0]), theta_P_values=np.array([P / MASS]),
        theta_P_covariance=None, drag_rolling_covariance=np.diag([1e-12, 1e-12]),
    )
    lat = LateralParameters(A0=A * G, A2=B * G / RHO, k_tire=0.0, g_track=1.0,
                            covariance=np.diag([1e-12, 1e-12]))
    return PhysicsParameterSet(
        driver_id="VER", session_id=0, longitudinal=longi, lateral=lat,
        n_samples_used=0, fit_quality_metrics={}, fit_air_density=RHO, braking=None,
    )


def main():
    # ---- exploration's EXACT params (its own functions, cached Hungary Q) ----
    cal_nodes = RR.load_cal_nodes()
    v_kmh, g_g = RR.get_apex_nodes(cal_nodes, GP, CARS)
    A, B, GS = RR.fit_grip_clean(v_kmh, g_g)
    q = RR.load_session(2023, GP, "Q")
    from air_density import air_density
    P, cc, co = RR.full_q_pd(q, CARS, air_density(2023, GP, "Q"))
    print(f"Exploration RBR @ Hungary params (its own fit):")
    print(f"  A={A:.3f}g  B={B:.5f}  GS={GS:.2f}g  P={P/1e3:.0f}kW  CdA_c={cc:.3f}  CdA_o={co:.3f}")
    print(f"  ({len(v_kmh)} apex nodes)\n")

    d = np.load(RIBBON)
    s, kappa = d["s"], d["kappa"]

    cfg = PhysicsEstimatorConfig.from_config()
    print("Production sim config:")
    print(f"  max_braking_ms2={cfg.max_braking_ms2}  apply_braking_friction={cfg.apply_braking_friction}"
          f"  start_speed={cfg.simulator_start_speed_ms}  merge_passes={cfg.simulator_merge_passes}\n")

    # ---- exploration: native + isolation toggles ----
    t_e0, v_e0 = expl_ideal_profile(s, kappa, A, B, GS, P, cc, co, LENGTH)
    t_e1, v_e1 = expl_ideal_profile(s, kappa, A, B, GS, P, cc, co, LENGTH, drs_open=False)
    t_e2, _ = expl_ideal_profile(s, kappa, A, B, GS, P, cc, co, LENGTH, gsat_on=False)

    # ---- production: same params, same ribbon ----
    params = make_prod_params(A, B, P, cc)
    sim = PhysicsSimulator(cfg)
    lap = sim.simulate_lap({"distance_m": s, "curvature": np.abs(kappa)}, params, sample=False)
    t_p = lap.lap_time_s * LENGTH / s[-1]
    v_p = np.interp(s, lap.distance_profile, lap.speed_profile)

    print("=" * 72)
    print("IDEAL LAP TIME (RBR/VER @ Hungary, identical ribbon + params)")
    print("=" * 72)
    print(f"  exploration native (DRS on, Gsat on)  : {t_e0:7.3f} s   [recorded 74.79]")
    print(f"  exploration  DRS-open OFF             : {t_e1:7.3f} s   ({t_e1-t_e0:+.3f}s = DRS-straight effect)")
    print(f"  exploration  Gsat OFF                 : {t_e2:7.3f} s   ({t_e2-t_e0:+.3f}s = saturation effect)")
    print(f"  PRODUCTION (closed CdA, const brake)  : {t_p:7.3f} s   ({t_p-t_e0:+.3f}s vs expl native)")

    print("\n" + "=" * 72)
    print("SPEED PROFILE (km/h)")
    print("=" * 72)
    print(f"  {'metric':<20}{'expl native':>13}{'expl DRSoff':>13}{'production':>13}")
    print(f"  {'top speed':<20}{v_e0.max()*3.6:>13.1f}{v_e1.max()*3.6:>13.1f}{v_p.max()*3.6:>13.1f}")
    print(f"  {'min speed (apex)':<20}{v_e0.min()*3.6:>13.1f}{v_e1.min()*3.6:>13.1f}{v_p.min()*3.6:>13.1f}")
    print(f"  {'mean speed':<20}{v_e0.mean()*3.6:>13.1f}{v_e1.mean()*3.6:>13.1f}{v_p.mean()*3.6:>13.1f}")
    # exclude index 0 from prod min (start-at-rest)
    print(f"  {'prod min excl. start':<20}{'':>13}{'':>13}{v_p[1:].min()*3.6:>13.1f}")

    diff = (v_p - v_e0) * 3.6
    order = np.sort(np.argsort(-np.abs(diff))[:8])
    print("\n  largest local speed gaps (production - expl native):")
    print(f"  {'s(m)':>7}{'R(m)':>8}{'expl':>9}{'prod':>9}{'d_kmh':>8}")
    for i in order:
        k = abs(kappa[i]); R = 1.0 / k if k > 1e-6 else np.inf
        Rs = f"{R:.0f}" if np.isfinite(R) else "straight"
        print(f"  {s[i]:>7.0f}{Rs:>8}{v_e0[i]*3.6:>9.1f}{v_p[i]*3.6:>9.1f}{diff[i]:>8.1f}")


if __name__ == "__main__":
    main()
