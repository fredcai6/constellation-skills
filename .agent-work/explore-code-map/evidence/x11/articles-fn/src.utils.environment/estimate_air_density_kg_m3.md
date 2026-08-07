[map index](../INDEX.md) / [`src.utils.environment`](INDEX.md)

# `estimate_air_density_kg_m3`
*function* [s] · [`src/utils/environment.py:65`](C:/Programs/f1Brainz/src/utils/environment.py#L65) · 27 lines [s]

**Signature** [s]

```python
def estimate_air_density_kg_m3(altitude_m: float, air_temp_c: float, humidity_pct: float) -> float
```

> Estimate moist-air density from altitude, air temperature, and relative humidity.
>
> Derives barometric pressure from the ISA standard atmosphere model, then
> applies the moist-air equation.  Use ``moist_air_density_from_pressure``
> instead when a measured barometric pressure is available.
>
> Args:
>     altitude_m: Altitude above mean sea level in metres.
>     air_temp_c: Air temperature in degrees Celsius.
>     humidity_pct: Relative humidity as a percentage (0–100).
>
> Returns:
>     Moist-air density in kg/m³.

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `altitude_m` — altitude_m: Altitude above mean sea level in metres. [a]
- `air_temp_c` — air_temp_c: Air temperature in degrees Celsius. [a]
- `humidity_pct` — humidity_pct: Relative humidity as a percentage (0–100). [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | internal | `moist_air_density_from_pressure` |
| reads | internal | `ISA_SEA_LEVEL_PRESSURE_PA` x2, `ISA_TEMPERATURE_LAPSE_RATE` x2, `GRAVITATIONAL_ACCEL`, `ISA_SEA_LEVEL_TEMP_K`, `MOLAR_MASS_DRY_AIR`, `UNIVERSAL_GAS_CONSTANT` |

*Not shown: 1 local-variable reads, 2 local-variable writes; 4 reads of its own parameters.*

**Referenced by**: 1 site(s) across 1 module(s) — src.evo_predictor.practice_preprocessor._compute


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
