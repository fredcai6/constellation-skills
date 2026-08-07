[map index](../INDEX.md)

# `src.utils.environment`

> Shared environment utilities.

`src/utils/environment.py` · 91 lines [s] · 2 entities · 2 documented, 0 **holes**

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

- [`moist_air_density_from_pressure`](moist_air_density_from_pressure.md) — *function* [s] — Compute moist-air density from a MEASURED barometric pressure.
- [`estimate_air_density_kg_m3`](estimate_air_density_kg_m3.md) — *function* [s] — Estimate moist-air density from altitude, air temperature, and relative humidity.
---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
