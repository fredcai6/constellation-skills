[map index](../INDEX.md) / [`src.utils.environment`](INDEX.md)

# `moist_air_density_from_pressure`
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


---
*Generated from the statement store by `evidence/x11/render_fn.py`. Unmarked facts = `x7b` statements; `[a]` = `x7a`; `[s]` = fetched from source (a logged vocabulary gap). Source-link lines are the store's `q.line` + 1 (defect D1: the store is 0-based and does not say so).*
