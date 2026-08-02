"""Re-bless the physics regression fixtures after the #488 simulator rewire.

Mirrors the regression test's current-dict construction exactly, then writes it
as the new blessed snapshot.  Prints a per-key diff so the change is auditable —
only the sim-derived keys (simulated_lap_time_s, max_speed_ms) should move; the
fitted-parameter keys must be identical (the estimator is unchanged).
"""
import sys, json, warnings
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))
warnings.filterwarnings("ignore")

from tests.regression.test_physics_regression import (
    _available_fixtures, _load_fixture, _load_blessed, _save_blessed, _extract_param_dict,
)
from src.physics.parameter_estimator import ParameterEstimator
from src.physics.physics_simulator import PhysicsSimulator


def _changed(old, new, key):
    a, b = old.get(key), new.get(key)
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(float(a) - float(b)) > 1e-6
    return a != b


for fx in _available_fixtures():
    processed, controls, metadata, track_profile = _load_fixture(fx)
    params = ParameterEstimator().estimate_parameters(
        processed, controls,
        weather={"air_density": metadata.get("weather", {}).get("air_density_kg_m3", 1.225)},
    )
    sim_result = PhysicsSimulator().simulate_lap(track_profile, params, sample=False) if track_profile is not None else None
    current = _extract_param_dict(params, sim_result, fixture_dir=fx, processed=processed)
    old = _load_blessed(fx) or {}

    diffs = [k for k in current if _changed(old, current, k)]
    print(f"\n=== {fx.name} ===")
    for k in diffs:
        print(f"  {k}: {old.get(k)} -> {current.get(k)}")
    non_sim = [k for k in diffs if k not in ("simulated_lap_time_s", "max_speed_ms")]
    if non_sim:
        print(f"  !! NON-SIM KEYS CHANGED (investigate before blessing): {non_sim}")
    else:
        _save_blessed(fx, current)
        print("  blessed updated (only sim keys changed).")
