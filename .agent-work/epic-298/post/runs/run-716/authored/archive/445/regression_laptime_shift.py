"""Quantify the #488 lap-time shift per regression fixture (new sim vs blessed)."""
import sys, json, warnings
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))
warnings.filterwarnings("ignore")

import numpy as np
from tests.regression.test_physics_regression import (
    _available_fixtures, _load_fixture, FIXTURES_DIR,
)
from src.physics.parameter_estimator import ParameterEstimator
from src.physics.physics_simulator import PhysicsSimulator

print(f"{'fixture':32s} {'blessed':>9s} {'new':>9s} {'shift':>8s}  flags")
for fx in _available_fixtures():
    processed, controls, metadata, track_profile = _load_fixture(fx)
    rho = metadata.get("weather", {}).get("air_density_kg_m3", 1.225)
    params = ParameterEstimator().estimate_parameters(processed, controls, weather={"air_density": rho})
    lap = PhysicsSimulator().simulate_lap(track_profile, params, sample=False)
    blessed = json.loads((fx / "blessed_params.json").read_text()).get("simulated_lap_time_s", float("nan"))
    new = lap.lap_time_s
    shift = (new - blessed) / blessed * 100 if blessed else float("nan")
    fqm = params.fit_quality_metrics
    flags = []
    if fqm.get("fallback_longitudinal"): flags.append("fb_long")
    if fqm.get("fallback_lateral"): flags.append("fb_lat")
    if params.lateral.ceiling is not None: flags.append(f"ceil={params.lateral.ceiling/9.81:.1f}g")
    from src.physics.capability_envelope import CapabilityEnvelope
    env = CapabilityEnvelope.from_parameters(params, rho)
    flags.append(f"brk={env.braking_source[:4]}")
    print(f"{fx.name:32s} {blessed:9.2f} {new:9.2f} {shift:+7.1f}%  {' '.join(flags)}")
