"""Independent reviewer probe of the aphysical-ideal-lap diagnosis (g4 / #518).

Reuses the SAME canonical helpers the dashboard uses (no second sim implementation):
  EstimateStore -> car_prior.build_car_ceiling -> simulate_lap -> regime masks.
Reports the ideal-lap top speed, real-lap top speed, and the braking-mask
v_ideal vs v_real, plus per-point ratio stats. Italy/VER on the WIRED store.
"""
import numpy as np

from src.physics.layer2.estimate_store import EstimateStore
from src.physics.physics_simulator import PhysicsSimulator
from src.physics.session_fit import load_quali_session
from src.physics.sim_evaluator import resample_by_progress
from src.physics.utilization.characterize import (
    _build_ceiling, _load_lap_and_ribbon, _resolve_round_idx, _lookup_constructor,
)
from src.physics.utilization.regime_utilization import _build_regime_masks

YEAR, GP, DRIVER = 2023, "Italy", "VER"
WIRED = "data/physics_estimates_g3wired.db"
CACHE = "data/telemetry"


def main():
    store_df = EstimateStore(WIRED).load(year=YEAR, status="ok")
    constructor = _lookup_constructor(store_df, YEAR, GP, DRIVER)
    rd = _resolve_round_idx(store_df, YEAR, GP, constructor)
    print(f"constructor={constructor!r} round_idx={rd}")

    ceiling = _build_ceiling(store_df, YEAR, constructor, rd)
    print(f"ceiling.n_sessions={ceiling.n_sessions}")

    full, track_df = _load_lap_and_ribbon(YEAR, GP, DRIVER, CACHE, load_quali_session)

    sim = PhysicsSimulator()
    grid_dist = track_df["distance_m"].to_numpy(dtype=float)
    grid_curv = track_df["curvature"].to_numpy(dtype=float)

    # Canonical ideal lap (the exact call estimate_driver_utilization makes).
    nominal = sim.simulate_lap(track_df, ceiling.params, sample=False)
    v_ideal = np.interp(grid_dist, nominal.distance_profile, nominal.speed_profile)
    v_real = resample_by_progress(grid_dist, full.best_distance, full.best_speed_real)

    print("\n=== TOP-SPEED PROBE ===")
    print(f"ideal-lap speed profile:  min={nominal.speed_profile.min():.1f}  "
          f"max={nominal.speed_profile.max():.1f} m/s  "
          f"({nominal.speed_profile.max()*3.6:.0f} km/h)")
    print(f"ideal on grid:            min={v_ideal.min():.1f}  max={v_ideal.max():.1f} m/s")
    print(f"real lap (full.best_speed_real): min={full.best_speed_real.min():.1f}  "
          f"max={full.best_speed_real.max():.1f} m/s  "
          f"({full.best_speed_real.max()*3.6:.0f} km/h)")
    print(f"real on grid:             min={v_real.min():.1f}  max={v_real.max():.1f} m/s")

    # Regime masks + braking-mask comparison.
    m_brk, m_slow, m_fast, m_str = _build_regime_masks(grid_dist, grid_curv, v_real)
    safe = np.where(np.abs(v_ideal) > 1e-6, v_ideal, 1e-6)
    ratio = v_real / safe

    for name, mask in (("braking", m_brk), ("fast_corner", m_fast),
                       ("slow_corner", m_slow), ("straight", m_str)):
        n = int(mask.sum())
        if n == 0:
            print(f"\n[{name}] EMPTY")
            continue
        vi = v_ideal[mask].mean()
        vr = v_real[mask].mean()
        r = ratio[mask]
        frac_ge2 = float(np.mean(r >= 2.0))
        u = float(np.clip(np.mean(r), 0.0, 2.0))
        print(f"\n[{name}] n={n}  mean v_ideal={vi:.1f}  mean v_real={vr:.1f}  "
              f"ratio[min/mean/max]={r.min():.2f}/{r.mean():.2f}/{r.max():.2f}  "
              f"frac(ratio>=2.0)={frac_ge2:.2f}  U=clip(mean)={u:.3f}")


if __name__ == "__main__":
    main()
