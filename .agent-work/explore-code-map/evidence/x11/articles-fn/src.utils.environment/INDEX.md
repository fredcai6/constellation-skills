# src.utils.environment
src/utils/environment.py, 91 lines

Shared environment utilities.

imports stdlib: __future__.annotations, math
imported by: src.compound_prior.gamma_modifier, src.evo_predictor.practice_preprocessor, src.evo_predictor.practice_preprocessor._compound_helpers, src.evo_predictor.practice_preprocessor._compute, src.evo_predictor.practice_preprocessor._lap_pipeline, src.evo_predictor.practice_preprocessor._types, src.physics.layer2.session_race, src.physics.session_fit, src.physics.weekend_state.layer1_physics

```python
ISA_SEA_LEVEL_PRESSURE_PA = 101325.0
ISA_SEA_LEVEL_TEMP_K = 288.15
ISA_TEMPERATURE_LAPSE_RATE = 0.0065
GRAVITATIONAL_ACCEL = 9.80665
MOLAR_MASS_DRY_AIR = 0.0289644
UNIVERSAL_GAS_CONSTANT = 8.31447
SPECIFIC_GAS_CONSTANT_DRY_AIR = 287.05
SPECIFIC_GAS_CONSTANT_WATER_VAPOR = 461.5
```

- [moist_air_density_from_pressure](moist_air_density_from_pressure.md) function: Compute moist-air density from a MEASURED barometric pressure.
- [estimate_air_density_kg_m3](estimate_air_density_kg_m3.md) function: Estimate moist-air density from altitude, air temperature, and relative humidity.
