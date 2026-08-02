# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g2` — Layer 1: explained physics (density from measured pressure + mass/fuel) with σ + falsifiable Mexico-vs-Monaco density check.

## Completed slice
Built `src/physics/weekend_state/layer1_physics.py`: per car-weekend x axis `explained` (density + mass/fuel component), `residual` (`axis - explained`), and honest propagated `layer1_sigma`, for all 11 axes in the g1 frame. Added `mexico_monaco_residual_consistency()` (the F6 falsifiable check's reusable core) and `tests/unit/physics/weekend_state/test_layer1_physics.py` (18 tests, all real-data-grounded except one synthetic mechanism test).

## Scope
**Files changed (all new):**
- `src/physics/weekend_state/layer1_physics.py`
- `tests/unit/physics/weekend_state/test_layer1_physics.py`
- `.agent-work/wave4-626/g2-implementer-plan.json` (own working plan, engine-driven)

**Specific exclusions touched:** no. Did not build Layers 2/3/4, did not modify `frame.py`/`floor.py`/the estimator/evo/config, did not commit/modify any `data/*.db`.

## Behavior changed
Yes — new module, no prior behavior existed.

## Map Impact
- **Structural anchors touched:** NEW `src/physics/weekend_state/layer1_physics.py` — consumes the g1 `frame.load_frame()` output (11 axes + `_sigma` + `rho`/`rho_is_fallback`/`mass_kg_assumed`) read-only; reads no DB itself (all DB access stays in `frame.py`/`TelemetryStore`, both pre-existing).
- **Capabilities added:** (1) `fit_density_betas(df, axes)` — within-car-season (fixed-effects) OLS slope of each axis on `ln(rho)`, with standard error, applied only to the axes physically justified below. (2) `apply_layer1(df, axes)` — adds `{axis}_explained` / `{axis}_residual` / `{axis}_layer1_sigma` columns. (3) `mexico_monaco_residual_consistency(layer1_df, axis)` — per shared (year, constructor) raw vs Layer-1-corrected gap + z-scores.
- **Constraints/assumptions touched:** `constraint:physics_region_no_evo_import` — honored (verified, see Evidence). `RHO_REF_KG_M3` derived from ISA constants via the real measured-pressure formula, not a hardcoded `1.2` (verified by test). No `data/*.db` staged/modified — honored.
- **Decision candidates / resolved decisions:** (1) **Axis grouping (mine, grounded not guessed):** `DENSITY_SENSITIVE_AXES` = the 3 CdA axes + `max_power_w` + the 3 aero-slope companions (`brake_aero_decel_per_m`, `traction_aero_accel_per_m`, `lateral_aero_grip_g`); `MASS_SENSITIVE_AXES` = the 3 CdA axes + `max_power_w` only. This extends — does not contradict — `src/physics/layer2/estimate_store.py`'s existing `SYSTEMATIC_FLOOR` (cda/p_max/A0 get a 4% mass+rho systematic; A0's own comment says "mass/rho cancel in the de-conflation," which corroborates leaving `lateral_mech_grip_g` density-null). (2) **Rho source correction (data-quality finding, see Workflow Feedback):** the handoff's cited `f1_data_<year>.db` weather table has NO Pressure column; the real measured-pressure source is `src/data/telemetry_store.py`'s `tele_weather.pressure_hpa`, confirmed bit-identical to the stored `rho` (see rho validation below).
- **Claims/evidence produced:** claim — `rho` in the g1 frame is bit-identically `moist_air_density_from_pressure` applied to the raw telemetry store's measured pressure/temp/humidity (3/3 sessions, diff = 0.00e+00). claim — the drag/power channel (`drag_area_closed_m2`, `max_power_w`) carries a statistically significant residual density leakage (t = 5.29, 7.84) even after the estimator's own rho-normalization, matching `estimate_store.py`'s own ~4% "mass + rho" systematic-floor citation in order of magnitude. claim — Layer 1's density correction reduces the Mexico<->Monaco normalized gap for both axes (drag: mean |z| 2.51 → 1.63, 90% of car-seasons improved; power: mean |z| 1.66 → 0.85, 95% improved) but does NOT close it to <1σ on every car-season (see honest magnitude note below) — a genuine, falsifiable, partially-positive result, not full closure.
- **Trust limitations / drift found:** the handoff's `f1_data_<year>.db` claim for rho validation was WRONG for this store's actual schema (no Pressure column there); redirected to `telemetry_store.db`, itself an existing, already-DB-only-compliant source (used in production by `session_fit._density_from_session`), so no new data-access violation was introduced.
- **Triage candidates:** the pooled density beta is empirically identified almost entirely by the Mexico-vs-everything-else contrast (Mexico is the only very-low-ρ circuit on the calendar; nearly everywhere else clusters ρ~1.15-1.23) — see honest magnitude note. A future gate wanting a cleaner density-only estimate (decorrelated from Mexico-specific setup/turbo/cooling effects) would need either more low-ρ circuits in the pooled fit or an explicit Mexico-dummy control; flagging for g3-g5/Commander, not fixed here (would require inventing evidence this store doesn't cleanly provide).

## Test mode
**Required:** `test-after` (per handoff: "the load-bearing test is the falsifiable density check")
**Satisfied:** yes — the module was implemented, then the 18-test file (including the falsifiable check) was written against real data and passed on the full run below.

## Evidence

```bash
cd C:/Programs/f1-626
py -m pytest tests/unit/physics/weekend_state/test_layer1_physics.py -q
```
```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Programs\f1-626
configfile: pyproject.toml
plugins: anyio-4.13.0, hypothesis-6.152.9, cov-7.1.0, mock-3.15.1
collected 18 items

tests\unit\physics\weekend_state\test_layer1_physics.py .................. [100%]

============================= 18 passed in 3.33s ==============================
```
**Result:** pass — 18/18, run 3 times consecutively with identical outcomes.

```bash
grep -n '^import\|^from' src/physics/weekend_state/layer1_physics.py | grep -i evo   # exit 1 = no import matches
git status --short | grep -i "\.db"                                                  # exit 1 = no db files touched
py -m src.utils.simplification_limits --paths src/physics/weekend_state/layer1_physics.py tests/unit/physics/weekend_state/test_layer1_physics.py
```
All three: no evo import, no db files touched, simplification-limits `PASS (2 files checked)`.

## Rho validation (measured-pressure grounding)

Corrected source: `src/data/telemetry_store.py` (`tele_weather.pressure_hpa`/`air_temp_c`/`humidity_pct`) — NOT `f1_data_<year>.db` (its `weather` table has no Pressure column; verified by schema inspection). This is the exact source `session_fit._density_from_session` reads in production.

| year | gp | computed (moist_air_density_from_pressure) | stored `rho` | diff |
|---|---|---|---|---|
| 2021 | Mexico | 0.9240329142 | 0.9240329142 | 0.00e+00 |
| 2021 | Monaco | 1.2021190699 | 1.2021190699 | 0.00e+00 |
| 2023 | Mexico | 0.9052291730 | 0.9052291730 | 0.00e+00 |

Bit-identical on all 3 sessions — the g1 frame's `rho` column is confirmed to be the measured-pressure moist-air density, not a fixed/altitude-derived value.

`RHO_REF_KG_M3` (Layer 1's reference density) = `moist_air_density_from_pressure(101325.0, 15.0, 0.0)` = **1.2250122659906946** kg/m³ — the ISA standard atmosphere run through the same measured-pressure formula, not a hardcoded `1.2` (tested).

## Density beta fits (all 11 axes, within-car-season fixed-effects OLS on ln(rho))

| axis | applied | beta | se | t = beta/se | n | n_car_seasons |
|---|---|---|---|---|---|---|
| drag_area_closed_m2 | **True** | 0.5257 | 0.0993 | **5.29** | 1481 | 81 |
| power_drag_area_m2 | **True** | 0.5257 | 0.0993 | **5.29** | 1481 | 81 |
| coast_drag_area_m2 | **True** | 0.4892 | 0.0972 | **5.04** | 1559 | 81 |
| max_power_w | **True** | 134,908 | 17,201 | **7.84** | 1481 | 81 |
| brake_aero_decel_per_m | **True** | -0.00585 | 0.00078 | **-7.49** | 1562 | 81 |
| traction_aero_accel_per_m | **True** | 0.00729 | 0.00123 | **5.91** | 1562 | 81 |
| lateral_aero_grip_g | **True** | -0.00852 | 0.01011 | -0.84 (n.s.) | 1562 | 81 |
| brake_decel_ms2 | False (null) | 14.52 (diagnostic only) | 3.50 | 4.15 | 1562 | 81 |
| traction_accel_ms2 | False (null) | -6.64 (diagnostic only) | 1.21 | -5.49 | 1562 | 81 |
| lateral_mech_grip_g | False (null) | 2.16 (diagnostic only) | 0.34 | 6.31 | 1562 | 81 |
| coast_rolling_decel_ms2 | False (null) | -0.354 (diagnostic only) | 0.11 | -3.25 | 1559 | 81 |

The "False (null)" rows are still fitted (as an audit diagnostic) but their beta is NOT applied — see honest magnitude note below for why.

## Mexico<->Monaco falsifiable residual-consistency check (all shared car-seasons, 2018-2026)

| axis | n pairs | mean \|z\| raw (density ignored) | mean \|z\| resid (Layer 1) | % car-seasons improved | % resid within 1σ |
|---|---|---|---|---|---|
| drag_area_closed_m2 | 59 | 2.512 | 1.632 | 89.8% | 37.3% |
| max_power_w | 59 | 1.665 | 0.849 | 94.9% | 66.1% |

2023 headline (raw pre-density gap for contrast, `drag_area_closed_m2`, m²):

| constructor | raw_gap | resid_gap | σ | z_raw | z_resid |
|---|---|---|---|---|---|
| Red Bull Racing | -0.4925 | -0.3535 | 0.1086 | 4.54 | 3.26 |
| Ferrari | -0.4313 | -0.2923 | 0.1284 | 3.36 | 2.28 |
| McLaren | -0.3848 | -0.2457 | 0.1038 | 3.71 | 2.37 |
| Mercedes | -0.2657 | -0.1267 | 0.1209 | 2.20 | 1.05 |
| AlphaTauri | -0.5325 | -0.3934 | 0.1386 | 3.84 | 2.84 |

2023 headline (`max_power_w`, W):

| constructor | raw_gap | resid_gap | σ | z_raw | z_resid |
|---|---|---|---|---|---|
| Red Bull Racing | -93,648 | -57,959 | 37,456 | 2.50 | 1.55 |
| Ferrari | -71,915 | -36,226 | 38,676 | 1.86 | 0.94 |
| McLaren | -95,022 | -59,333 | 37,343 | 2.54 | 1.59 |
| Mercedes | -61,836 | -26,147 | 37,942 | 1.63 | 0.69 |
| Alfa Romeo | -3,191 | 32,498 | 39,022 | 0.08 | 0.83 |

The test (`TestMexicoMonacoResidualConsistency`) asserts, per axis: (1) the raw gap is real (mean |z| raw > 1.0 — not a vacuous test), (2) the Layer-1-corrected mean |z| is < 85% of the raw mean |z| (a mishandled/ignored-density scenario — which is literally the `raw_gap`/`z_raw` column — would fail this), (3) the corrected mean |z| stays bounded (< 2.2 for drag, < 1.2 for power). All pass with real margin. A contrast test (`test_mexico_monaco_density_null_axis_shows_no_correction`) proves a density-null axis's residual gap equals its raw gap exactly (no explained component silently applied where none was justified).

## Honest note on the layer's magnitude

This is **not** a no-op, but it is **not full closure** either, and the two axes where it's strongest (drag CdA, max power) are also the two the pre-existing `estimate_store.SYSTEMATIC_FLOOR` already flagged as mass+rho-sensitive — Layer 1 is putting a real, fitted number on a leakage the codebase already knew was there, not discovering a new large effect from nothing.

- **7 of 11 axes get a real, nonzero density-explained component**, all with the sign and rough (per-axis) magnitude expected from the underlying dynamics (drag/power channel most sensitive, aero-slope companions next, matching the SYSTEMATIC_FLOOR precedent's own ordering).
- **4 of 11 axes are an exact, code-enforced no-op** (`brake_decel_ms2`, `traction_accel_ms2`, `lateral_mech_grip_g`, `coast_rolling_decel_ms2`): these are already mass-normalized accelerations with no direct 0.5·ρ·v² term, so a density/mass explained component would not be physically real — reported honestly rather than manufactured (tested exactly: `explained == 0`, `residual == raw`, `layer1_sigma == stored sigma` when rho is trusted).
- **The mass/fuel component nets to exactly zero for any same-year comparison** (including the falsifiable check above): `mass_kg_assumed` is constant WITHIN a season (tracks the year's regulation minimum weight, not per-race fuel load — verified: every year has exactly one distinct value in the store). The `MASS_ELASTICITY`/`MASS_SENSITIVE_AXES` machinery is real (F=m·a reasoning: force/power-derived axes carry ~unit elasticity to an assumed-mass error; already-per-unit-mass axes carry none) but is only OBSERVABLE cross-year, where it would be hopelessly confounded with genuine regulation-era performance shifts (e.g. the 2022 ground-effect reset) — so it is assigned from physical units reasoning, not fit from this store, and documented as such rather than dressed up as a data-driven measurement it isn't.
- **The density correction does not close the Mexico/Monaco gap to <1σ on every car-season** (37-66% within 1σ post-correction, not 100%). This is the honest, falsifiable output, not a failure to hit an arbitrary bar: Mexico's pooled density beta is empirically identified almost entirely by the Mexico-vs-everywhere-else contrast (Mexico is nearly the only sub-1.0 ρ circuit on the calendar), so it is plausibly entangled with genuine Mexico-specific effects (turbo/cooling derate at altitude, unique aero trim) that are real physics but NOT density-normalization leakage in the sense Layer 1 targets. The falsifiable test is written to reflect exactly this: "meaningfully more consistent than raw," not "fully consistent."

## Docs/contracts touched
- None.

## Assumptions
- **Axis grouping** (density-sensitive / mass-sensitive / null) is mine, grounded in `estimate_store.SYSTEMATIC_FLOOR`'s existing split + F=m·a units reasoning (see Map Impact/decision notes), not fit or tuned against the Mexico/Monaco result.
- **`RHO_REF_KG_M3`**: ISA standard atmosphere (15°C, 0% humidity, 101325 Pa) via `moist_air_density_from_pressure` — a defensible, documented physical reference, not the only possible choice (e.g. the store's own mean rho would also be defensible); chosen because it's traceable to a named physical standard rather than a data-dependent constant that would shift if the store grows.
- **`MASS_REF`**: the calling `df`'s own mean `mass_kg_assumed` (computed inside `apply_layer1`, not a module-level constant, per the project's no-module-level-mutable-state rule) — reasonable for a same-store comparison; would need reconsideration if this layer is ever called on a partial/filtered df where the mean shifts.
- **`MASS_ELASTICITY_SIGMA = 0.3`** and **`RHO_FALLBACK_INFLATION = 0.05`** (the latter reused verbatim from `estimate_store._RHO_INFLATION` for continuity, but applied to Layer 1's OWN density/mass-split uncertainty, not a duplicate of the floor already baked into the stored axis `_sigma`): both are honest, documented, conservative constants, not fit.
- **`MIN_WEEKENDS_FOR_BETA = 4`**: reused from `floor.MIN_WEEKENDS` for a trusted car-season, consistent with g1's own convention.
- Density-beta fitting pools ALL trusted car-seasons (no held-out split) — this is a within-sample consistency check per the handoff's framing ("residual-consistency test," not a g5-style held-out prediction gate), not a claim of out-of-sample generalization.

## Stop conditions hit
None outright, but the second stop condition's spirit was partially triggered and reported rather than silently smoothed over: **the Mexico/Monaco residual gap is NOT brought fully within 1σ for every car-season even with correct density handling** (37-66% within 1σ post-correction). Per the handoff, this is reported as a real finding (see honest magnitude note) rather than treated as a blocking failure, because the test itself is framed as a consistency-IMPROVEMENT check (which passes with real margin), not an exact-closure claim — the handoff explicitly anticipated and pre-authorized this outcome ("Mexico differs from Monaco in aero trim + track too... a residual gap is not naively blamed on density").

## Out-of-scope observations
- **Rho-validation source correction**: the handoff's `f1_data_<year>.db` citation for measured weather does not hold for this store's actual schema (no Pressure column). Flagging for whoever owns the handoff template/map anchors: the correct citation is `src/data/telemetry_store.py` (`tele_weather.pressure_hpa`), an existing, already-DB-only-compliant, absolute-main-checkout-path source.
- **Mexico-contrast confound**: the pooled density beta is effectively a "Mexico dummy" more than a smooth density-response estimate, because Mexico is nearly the only very-low-ρ circuit in the F1 calendar. A future gate wanting a cleaner, less Mexico-confounded density estimate would need either more low-density circuits in the training pool or an explicit per-circuit control — flagged as a triage candidate above, not fixed here.
- **`lateral_aero_grip_g`'s density beta is not statistically significant** (t = -0.84) despite being in `DENSITY_SENSITIVE_AXES` on physical-units grounds — its typical magnitude (~0.0004 g) is tiny relative to its noise floor, so the density correction is essentially harmless-but-uninformative there (not tested for significance in the required-evidence test, which only requires it for `drag_area_closed_m2`/`max_power_w`; worth a note for whoever reviews axis-by-axis behavior in g5's ablation).

## Workflow Feedback

- **Handoff gaps:** the handoff's "measured weather from `f1_data_<year>.db`" claim (Key data facts bullet 2, and Verification's implicit assumption) does not match this store's actual schema — its `weather` table carries no Pressure column. This cost one grounding detour (schema inspection -> trace `_density_from_session` -> find `telemetry_store.py`) but resolved cleanly to an equally DB-only-compliant, already-existing, absolute-path source; no design compromise resulted. Worth correcting the map anchor for future gates that also need measured weather (g3/g4 might hit the same trap).
- **Context rediscovered:** `estimate_store.py`'s `SYSTEMATIC_FLOOR`/`_RHO_INFLATION` constants (the existing production density/mass-sensitivity grounding) were not named in the handoff's Map Anchors but turned out to be the single most load-bearing piece of context for deciding the axis grouping honestly rather than guessing uniformly. A future g2-style handoff could point directly at this file.
- **Instructions improvised around:** none beyond the above. The plan's own `m2-core` postcondition command used a `-k` filter (`'rho_matches or fallback_inflat or ...'`) that didn't substring-match my actual test names exactly (`fallback_inflat` vs `test_fallback_row_gets_larger_sigma...`); rather than leaving a loosely-matching check, I renamed the two `m3` Mexico/Monaco test functions to literally contain `mexico_monaco` (an improvement to test naming anyway) so the `m3` postcondition's `-k mexico_monaco` command was a genuine, non-vacuous check rather than accidentally-passing-via-0-selected.
- **What would have made this easier:** a one-line pointer in the handoff to `estimate_store.SYSTEMATIC_FLOOR` (the existing production precedent for exactly this layer's physical reasoning) would have saved the discovery step; otherwise the handoff was unusually well-scoped (explicit stop conditions that correctly anticipated the actual outcome).

## Return status
`complete`
