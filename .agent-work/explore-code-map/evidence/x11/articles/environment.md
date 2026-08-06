# `src.utils.environment`

> Shared environment utilities.

`src/utils/environment.py` · 91 lines [s] · 2 top-level, 2 entities total · 2 documented, 0 **holes**

## Dependencies

**Imports (stdlib)**: `__future__.annotations`, `math`

**Imported by** (9 modules in the extraction window): `src.compound_prior.gamma_modifier`, `src.evo_predictor.practice_preprocessor`, `src.evo_predictor.practice_preprocessor._compound_helpers`, `src.evo_predictor.practice_preprocessor._compute`, `src.evo_predictor.practice_preprocessor._lap_pipeline`, `src.evo_predictor.practice_preprocessor._types`, `src.physics.layer2.session_race`, `src.physics.session_fit`, `src.physics.weekend_state.layer1_physics`

## Module-level constants

| name | annotation [s] | value [s] | line | in store? |
| --- | --- | --- | --- | --- |
| `ISA_SEA_LEVEL_PRESSURE_PA` | — | `101325.0` | 7 | name only |
| `ISA_SEA_LEVEL_TEMP_K` | — | `288.15` | 8 | name only |
| `ISA_TEMPERATURE_LAPSE_RATE` | — | `0.0065` | 9 | name only |
| `GRAVITATIONAL_ACCEL` | — | `9.80665` | 10 | name only |
| `MOLAR_MASS_DRY_AIR` | — | `0.0289644` | 11 | name only |
| `UNIVERSAL_GAS_CONSTANT` | — | `8.31447` | 12 | name only |
| `SPECIFIC_GAS_CONSTANT_DRY_AIR` | — | `287.05` | 13 | name only |
| `SPECIFIC_GAS_CONSTANT_WATER_VAPOR` | — | `461.5` | 14 | name only |

## Contents

- [`moist_air_density_from_pressure`](#moist-air-density-from-pressure) — *function* — Compute moist-air density from a MEASURED barometric pressure.
- [`estimate_air_density_kg_m3`](#estimate-air-density-kg-m3) — *function* — Estimate moist-air density from altitude, air temperature, and relative humidity.

---

## `moist_air_density_from_pressure`
*function* [s] · [`src/utils/environment.py:17`](C:/Programs/f1Brainz/src/utils/environment.py#L17) · 46 lines [s]

**Signature** [s]

```python
def moist_air_density_from_pressure(pressure_pa: float, air_temp_c: float, humidity_pct: float) -> float
```

> Compute moist-air density from a MEASURED barometric pressure.
>
> Uses the same moist-air physics as ``estimate_air_density_kg_m3`` but
> takes the barometric pressure directly instead of deriving it from
> altitude via the ISA standard atmosphere.  Prefer this function when a
> measured ``Pressure`` field is available from FastF1 weather data.
>
> **Unit warning:** ``pressure_pa`` must be in **Pascals**.  FastF1
> ``weather_data['Pressure']`` is in **mbar (hPa)**; multiply by 100.0
> before passing here (e.g. ``pressure_mbar * 100.0``).  Passing mbar
> directly (e.g. 1013 instead of 101300) underestimates density ~100×.
>
> Args:
>     pressure_pa: Absolute barometric pressure in **Pascals** (Pa).
>         Realistic sea-level values are approximately 80 000–110 000 Pa.
>         Values below 10 000 Pa are almost certainly mbar passed by
>         mistake — this function raises ``ValueError`` in that case.
>     air_temp_c: Air temperature in degrees Celsius.
>     humidity_pct: Relative humidity as a percentage (0–100).
>
> Returns:
>     Moist-air density in kg/m³.
>
> Raises:
>     ValueError: If ``pressure_pa < 10000``, which almost certainly
>         indicates that the caller passed mbar (e.g. FastF1 ``Pressure``)
>         instead of Pa.

*(everything after the first line above is [s] — the store keeps only the summary line.)*

**Parameters**

- `pressure_pa` — pressure_pa: Absolute barometric pressure in **Pascals** (Pa). [a]
- `air_temp_c` — air_temp_c: Air temperature in degrees Celsius. [a]
- `humidity_pct` — humidity_pct: Relative humidity as a percentage (0–100). [a]

**Uses**

| relation | scope | targets |
| --- | --- | --- |
| calls | stdlib | `builtins.ValueError`, `math.exp` |
| reads | internal | `SPECIFIC_GAS_CONSTANT_DRY_AIR`, `SPECIFIC_GAS_CONSTANT_WATER_VAPOR` |
| reads | stdlib | `math (module)` |

*Not shown: 6 local-variable reads, 4 local-variable writes; 7 reads of its own parameters.*

**Referenced by**: 2 site(s) across 2 module(s) — src.physics.weekend_state.layer1_physics


## `estimate_air_density_kg_m3`
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

**Provenance**: unmarked facts come from `evidence/x7b/statements.jsonl`; `[a]` from `evidence/x7a/statements.jsonl`; `[s]` had to be fetched from source by `evidence/x11/supplement.py` and is a logged statement-vocabulary gap. No sentence on this page was written by a model.

Line numbers in source links are the store's `q.line` **+ 1**: x7b records 0-based lines for all 87 entities and the schema does not say so (defect D1).
