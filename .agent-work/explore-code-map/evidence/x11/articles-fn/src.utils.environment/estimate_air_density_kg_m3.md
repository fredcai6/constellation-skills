# src.utils.environment:estimate_air_density_kg_m3
function, src/utils/environment.py:65, 27 lines

```python
def estimate_air_density_kg_m3(altitude_m: float, air_temp_c: float, humidity_pct: float) -> float
```

Estimate moist-air density from altitude, air temperature, and relative humidity.

Derives barometric pressure from the ISA standard atmosphere model, then
applies the moist-air equation.  Use ``moist_air_density_from_pressure``
instead when a measured barometric pressure is available.

Args:
    altitude_m: Altitude above mean sea level in metres.
    air_temp_c: Air temperature in degrees Celsius.
    humidity_pct: Relative humidity as a percentage (0–100).

Returns:
    Moist-air density in kg/m³.

calls internal: moist_air_density_from_pressure
reads internal: ISA_SEA_LEVEL_PRESSURE_PA x2, ISA_TEMPERATURE_LAPSE_RATE x2, GRAVITATIONAL_ACCEL, ISA_SEA_LEVEL_TEMP_K, MOLAR_MASS_DRY_AIR, UNIVERSAL_GAS_CONSTANT

referenced by: 1 sites in 1 modules (src.evo_predictor.practice_preprocessor._compute)
