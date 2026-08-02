"""STATIC grip-envelope fit comparison: exploration `fit_grip_clean` vs
production `LateralEnvelopeFit.fit_envelope`, on the SAME cached apex-node cloud.

No session load — the apex nodes come from calibrated_aniso_nodes.npz.
Baseline: RBR (VER+PER) @ Hungary 2023.

Run:  py .agent-work/445/static_gripfit_compare.py
"""
from __future__ import annotations

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

import ribbon_reeval as RR  # noqa: E402
from src.physics.physics_config import PhysicsEstimatorConfig          # noqa: E402
from src.physics.physics_data_models import ControlState, KinematicSample  # noqa: E402
from src.physics.lateral_envelope import LateralEnvelopeFit            # noqa: E402

G, RHO = 9.81, 1.2


def mk_sample(v_ms, alat_ms2):
    """Minimal valid KinematicSample carrying speed + a_lateral (the fit inputs)."""
    z3 = np.zeros(3); z9 = np.zeros((9, 9))
    ctrl = ControlState(timestamp_ms=0, throttle_confidence=1.0,
                        throttle_value=0.0, brake_probability=0.0)
    return KinematicSample(
        timestamp_ms=0, position=z3, velocity=z3, acceleration=z3, covariance=z9,
        speed=float(v_ms), a_longitudinal=0.0, a_lateral=float(alat_ms2),
        curvature=0.0, control=ctrl, regime="corner",
    )


def main():
    cal_nodes = RR.load_cal_nodes()
    v_kmh, g_g = RR.get_apex_nodes(cal_nodes, "Hungary", ["VER", "PER"])
    v_ms = v_kmh / 3.6
    alat_ms2 = g_g * G
    print(f"RBR @ Hungary apex node cloud: {len(v_kmh)} nodes, "
          f"v {v_kmh.min():.0f}-{v_kmh.max():.0f} km/h, "
          f"a_lat {g_g.min():.2f}-{g_g.max():.2f} g\n")

    # ---- exploration grip fit (per-speed-bin p90, saturated, bounded) ----
    A, B, GS = RR.fit_grip_clean(v_kmh, g_g)
    # exploration a_lat(v) in m/s^2 = min(A + B v^2, GS) * G
    def expl_alat(v):  # v in m/s
        return min(A + B * v * v, GS) * G

    # ---- production grip fit (global-quantile linear lstsq, no sat/bounds) ----
    cfg = PhysicsEstimatorConfig.from_config()
    samples = [mk_sample(v, a) for v, a in zip(v_ms, alat_ms2)]
    lat = LateralEnvelopeFit(cfg).fit_envelope(samples, RHO)
    # production a_lat(v) = A0*g_track + A2*rho*v^2 (g_track=1)
    def prod_alat(v):
        return lat.A0 * lat.g_track + lat.A2 * RHO * v * v

    print(f"envelope_quantile (prod mask) = {cfg.envelope_quantile}\n")
    print("FIT PARAMETERS")
    print(f"  exploration:  A={A:.3f}g  B={B:.5f}  Gsat={GS:.2f}g  (bounds A[1,3] B[5e-4,5e-3])")
    print(f"                -> A0_equiv={A*G:.2f} m/s^2   A2_equiv={B*G/RHO:.5f}")
    print(f"  production :  A0={lat.A0:.2f} m/s^2 ({lat.A0/G:.2f}g)   A2={lat.A2:.5f}   (no sat, no bounds, no binning)")

    print("\nIMPLIED LATERAL GRIP a_lat(v)  [m/s^2 and g]")
    print(f"  {'v (km/h)':>9}{'expl m/s2':>11}{'expl g':>8}{'prod m/s2':>11}{'prod g':>8}{'prod/expl':>10}")
    for vk in (60, 100, 140, 180, 220, 260, 300):
        v = vk / 3.6
        e = expl_alat(v); p = prod_alat(v)
        print(f"  {vk:>9}{e:>11.1f}{e/G:>8.2f}{p:>11.1f}{p/G:>8.2f}{p/e:>10.2f}")

    print("\nNote: exploration saturates at Gsat; production grows unbounded as A2·ρ·v².")
    print(f"At 300 km/h production implies {prod_alat(300/3.6)/G:.1f}g vs exploration's capped {GS:.1f}g.")


if __name__ == "__main__":
    main()
