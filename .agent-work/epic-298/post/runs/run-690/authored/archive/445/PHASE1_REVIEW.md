# Phase 1 Review — Per-session air density consistency (epic #445)

**Verdict: APPROVE-WITH-NITS**

Tests: 176 passed, 13 skipped, 4 warnings — all green.

---

## Summary

The primary bug (simulator used hardcoded `reference_density_kg_m3=1.225` while the fit could use a
different ρ, making `theta_D * rho_sim ≠ theta_D * rho_fit`) is correctly fixed. The fix is minimal
and well-targeted: one field added to `PhysicsParameterSet`, one resolution in `simulate_lap`, and
consistent propagation through `_sample_parameters`. All density uses in `simulate_lap`
(`_compute_speed_caps`, `_forward_pass`, `_backward_pass`) receive the same resolved `air_density`
local variable, so the invariant truly holds across every evaluation path.

The `estimate_air_density_kg_m3` refactor (delegating to the new function) is numerically identical
to the old code — verified across 1000 random inputs with zero difference. Physics of
`moist_air_density_from_pressure` is correct: returns 1.22501 at ISA conditions and ~0.923 at 78 kPa
Mexico conditions, matching expected values.

The consistency property test is genuine (not tautological): `test_lap_time_invariant_when_fit_and_sim_density_agree`
would fail on the pre-fix code because the sim would apply the wrong ρ to the differently-scaled
`theta_D` values, producing different lap times. `test_lap_time_changes_when_sim_density_differs_from_fit`
correctly documents the pre-fix bug by using `fit_air_density=None` to let the config density be used.

One finding is worth attention before the next phase caller lands.

---

## Findings

### 1. [NIT] `moist_air_density_from_pressure` docstring does not warn about FastF1 mbar units
**Severity:** Low (latent, no production caller yet)
**File:** `src/utils/environment.py:27`
**What:** The docstring says "Prefer this function when a measured `Pressure` field is available from
FastF1 weather data." FastF1 `weather_data['Pressure']` is in **mbar**, not Pa. The parameter is
`pressure_pa`. Passing mbar directly (e.g. `1013.25` instead of `101325.0`) produces a density
~100x too low (≈0.012 kg/m³ instead of 1.225 kg/m³). There is no validation guard.
**Why it matters:** This function is not yet called in production code; it's only called from
`estimate_air_density_kg_m3` (which derives Pa from the ISA model) and tests. But the docstring
exists precisely to guide the next person wiring FastF1 Pressure into this path, and it's a silent
factor-of-100 trap.
**Suggested fix:** Add one line to the docstring: "Note: FastF1 `weather_data['Pressure']` is in
mbar; multiply by 100.0 to convert to Pa before passing here." Alternatively add an assertion
`assert pressure_pa > 10000, "pressure_pa must be in Pa, not mbar"` (any realistic atmospheric
pressure in Pa is above 50000).

---

### 2. [NIT] `simulate_lap(sample=True)` parameter is now dead code with stale documentation
**Severity:** Low (no behavior impact, purely cosmetic)
**File:** `src/physics/physics_simulator.py:35, 49`
**What:** The class docstring says "The stochastic path (`sample=True`), used by `monte_carlo_laps`"
but `monte_carlo_laps` now calls `_sample_parameters` + `simulate_lap(sample=False)` exclusively.
The `sample` parameter is declared but never referenced in the function body. Calling
`simulate_lap(sample=True)` is identical to `simulate_lap(sample=False)`.
**Why it matters:** Anyone reading the class docstring will think `simulate_lap(sample=True)` does
something. It does nothing. No production callers use `sample=True` (verified by grep).
**Suggested fix:** Either (a) remove the `sample` parameter and update the docstring, or (b) add a
`# noqa` comment and update the docstring to say the `sample` parameter is deprecated/reserved.
Option (a) is cleaner but is a breaking API change if any external callers pass it.

---

### 3. [INFO — no action] `_get_air_density` does not call `moist_air_density_from_pressure`
**Severity:** Informational (by design, not a bug)
**File:** `src/physics/parameter_estimator.py:282`
**What:** The estimator accepts a pre-computed density via `weather.air_density` (or similar
attribute). It does not internally call `moist_air_density_from_pressure(weather['Pressure'], ...)`.
This means the caller must supply an already-computed density, not raw FastF1 weather fields.
**Why it matters:** The MEMORY notes (density-cda-fix.md) say "use real per-session density
(measured FastF1 Pressure)". The new function exists to enable this, but wiring it through
`_get_air_density` is deferred. This is a known gap (Phase 1 scope was fit/sim consistency, not
the data-collection wiring), not a Phase 1 defect. Note it for whoever wires the collection path.

---

### 4. [INFO — no action] No input validation on `moist_air_density_from_pressure`
**Severity:** Very low (silent on unphysical inputs, but all realistic inputs are fine)
**File:** `src/utils/environment.py:17`
**What:** Zero pressure returns 0.0 (fine). Negative pressure returns negative density (silently
wrong). NaN propagates through (returns NaN). Near-absolute-zero temperature returns a spuriously
large density. 100% humidity at realistic conditions is safe (vapor pressure stays well below
atmospheric).
**Why it matters:** These edge cases don't arise from real FastF1 data. FastF1 Pressure values are
always in the 600–1050 mbar range (and would be passed in Pa after conversion). Not worth guarding
against given the function's expected use domain.

---

## Test result

```
py -m pytest tests/unit/physics tests/unit/utils/test_environment.py tests/regression/test_physics_regression.py -q
176 passed, 13 skipped, 4 warnings in 11.02s
```

Warnings:
- One `RuntimeWarning: covariance is not symmetric positive-semidefinite` from `test_monte_carlo.py`
  — this is pre-existing, in the Monte Carlo test fixture, not introduced by Phase 1.
- Three regression `UserWarning` for large lap-time errors on fallback fits — also pre-existing
  (Monaco/Monza/Spain fixture with fallback parameters), not introduced by Phase 1.

---

## Physics correctness summary

| Check | Result |
|---|---|
| `moist_air_density_from_pressure` formula | Correct (Dalton's law of partial pressures) |
| ISA sea level (15°C, 0% RH, 101325 Pa) | 1.22501 kg/m³ ✓ |
| Mexico-like (78 kPa, 20°C, 40% RH) | 0.9227 kg/m³ ✓ |
| `estimate_air_density_kg_m3` drift after refactor | 0.0 (exact bitwise match) |
| Simulator uses same ρ in all drag evaluations | Yes — `air_density` local resolved once at top of `simulate_lap`, passed through `_forward_pass`, `_backward_pass`, `_compute_speed_caps`, `_compute_drive_accel`, `_compute_braking_decel` |
| `_sample_parameters` propagates `fit_air_density` | Yes — line 318 copies it to perturbed set |
| Invariant test is genuine (not tautological) | Yes — would fail pre-fix |
| Bug-documentation test exercises the actual fix | Yes |
| `fit_air_density=None` backward-compat path | Preserved correctly |
| Existing fixtures (no `fit_air_density` field) | Unaffected — dataclass default is None |
