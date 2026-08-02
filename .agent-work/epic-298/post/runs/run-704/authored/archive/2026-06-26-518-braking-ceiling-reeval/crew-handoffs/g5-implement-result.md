# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g5 (RE-PLANNED) — Diagnose + fix the ideal-lap simulator over-acceleration.`

## DIAGNOSIS (root cause + why the over-shoot)

**Root cause: a watts-vs-W/kg units mismatch at the param-assembly boundary.** The
`theta_P` power channel on `LongitudinalParameters` is consumed by the simulator and
envelope as **specific power** (W/kg = m²/s³): the drive acceleration is
`theta_P / v` and `drag`/`rolling` are accelerations (m/s²), so `theta_P` must already
carry the `1/mass` factor. Three independent witnesses confirm this is the canonical
convention:
- `LongitudinalFit.fit_power_trajectory` (`longitudinal_fit.py:316`) produces
  `power_est = (a_long + theta_R + drag) * v` — an accel×speed = **W/kg**.
- `config.default_theta_P = 300.0` — sensible only as W/kg (300 W/kg ÷ 50 m/s = 6 m/s²;
  as watts it is 0.0074 m/s²).
- `test_physics_simulator.py:218` computes terminal velocity as
  `(theta_P/(theta_D·rho))**(1/3)` with **no** mass division.

The **store path** breaks the convention. `car_prior._build_longitudinal`
(`car_prior.py:341`) wrote `theta_P_values=[p_max]` where the store's `p_max` is
`DragThrottleFit.power` in **total watts** (~629 kW for RBR; the fit's design matrix at
`longitudinal_fit.py:256` uses a `1/(MASS_KG·v)` power column, so the fitted power comes
out in watts with mass baked into the model). No watts→W/kg conversion was applied, so
the simulator divided ~629000 by `v` and got an acceleration ~mass× too large.

**Why the over-shoot factor.** The straight-line terminal velocity solves
`power/v = drag(v) + rolling`. Drag is cubic-ish in `v`, so a mass× error on the LHS
shifts the balance by ~mass^(1/3) ≈ 808^(1/3) ≈ 9.3×. The unbounded-straight top speed
went from a physical ~95 m/s to ~909 m/s (the analytic `_power_accel` zero-crossing
moves identically). The handoff's headline **206.9 m/s / 2.09×** is the *same* bug
measured on the **real ribbon**, where corners and `speed_caps` clip the straight before
it reaches the unbounded ~909 m/s asymptote; on a pure straight the unclamped
over-acceleration runs to ~909 m/s / 9.57×. Both are the identical root cause.

This bug has been present since `car_prior` was built (#510), so it **confounded #510's
original C1 diagnosis** (the "ceiling under-call" reading) — the ideal-lap ceiling was
aphysically high, not the measured capability being too low. (Flagged for
Cartographer/Triage.)

## Completed slice
Converted the store's total-watts `p_max` to the simulator's specific-power (W/kg)
convention at the param-assembly boundary in `car_prior._build_longitudinal`, with a
clear units docstring, and added a truth-anchored L1/L2 invariant test. The capability
**measurement is unchanged** (the 629 kW value is identical; only its unit representation
is corrected).

## Scope
**Files changed:**
- `src/physics/utilization/car_prior.py` — `_build_longitudinal`: `theta_P_values =
  [p_max / MASS_KG]` and `theta_P_covariance = _build_1x1_cov(p_max_sigma / MASS_KG)`
  (variance scales by `1/MASS_KG²`); units docstring + bridge-table rows updated.
- `tests/unit/physics/test_ideal_lap_top_speed_invariant.py` — **NEW** truth-anchored
  invariant test (the regression guard).
- `tests/unit/physics/test_car_prior.py` — updated `test_p_max_single_point` and
  `test_p_max_covariance_1x1` to expect the W/kg conversion (they previously pinned the
  buggy watts passthrough with an unrealistically small `p_max=350` fixture).

**Specific exclusions touched:** `yes — car_prior.py, ruled IN-SCOPE by the Commander`
(team-lead message, 2026-06-25). car_prior was named in the exclusions to forbid
re-CALIBRATING the measurement (fits / p_max / CdA values); a watts→W/kg **units
conversion** changes none of those — it is exactly the "param-assembly boundary / ideal-lap
machinery" the gate targets, and it is the only producer emitting wrong units (a blanket
`/MASS_KG` in `max_power` was correctly rejected — it would double-divide the already-W/kg
`fit_power_trajectory` path). No other excluded surface touched (no utilization/dashboard,
no `regime_utilization` thresholds, no `U_CLIP_MAX`, no docs/architecture, no other fits).

## Behavior changed
`yes — the RBR ideal-lap straight-line top speed drops from ~908.8 m/s (3272 km/h) to
94.80 m/s (341 km/h), exactly matching the analytic drag-limited terminal velocity
(ratio 1.0000). Braking and cornering behaviour is unchanged.`

## Map Impact
- **Structural anchors touched:** `struct:physics — src/physics/utilization/car_prior.py
  (_build_longitudinal), level: param-assembly boundary — watts→W/kg conversion for the
  theta_P power channel.`
- **Capabilities affected:** `ideal-lap simulation from the capability envelope — the
  ideal lap now respects the drag-limited terminal velocity; the straight-line ceiling is
  physical.`
- **Constraints/assumptions touched:** `assumption: theta_P is SPECIFIC power (W/kg) — now
  explicitly enforced and documented at the car_prior producer (previously violated
  silently). constraint:physics_region_no_evo_import honored. One canonical path (no second
  sim) honored.`
- **Decision candidates / resolved decisions:** `decision:ideal_lap_sim_two_sided_evaluator
  — this fix restores the ideal-lap-as-ceiling contract (an aphysical ideal lap was not a
  valid ceiling). Note for reconcile.`
- **Claims/evidence produced:** `claim: ideal-lap top speed ≈ analytic terminal velocity
  (95 m/s for RBR), encoded by the new invariant test. C1 (G6) can now test the real
  premise on a physical ceiling.`
- **Trust limitations / drift found:** `#510's C1 diagnosis ("ceiling under-call") is
  confounded by this bug and is now low-confidence — the ideal ceiling was aphysically high,
  not the measurement low. Triage/reconcile candidate.`
- **Triage candidates:** `(1) #510 C1 diagnosis re-evaluation given the corrected ideal lap.
  (2) The deprecated FrictionCoupling._compute_longitudinal_max (friction_coupling.py:70)
  and fit_power_trajectory share the same theta_P convention but there is no single typed
  "specific power" accessor — a future consolidation could make the W/kg convention explicit
  in the type (e.g. a named property) to prevent recurrence.`

## Test mode
**Required:** `test-first (TDD-leaning) — failing invariant first (L1/L2), truth-anchored.`
**Satisfied:** `yes — RED observed before the fix (top speed 921.5 m/s >> terminal 96.3 m/s),
GREEN after.`

## Evidence

Before/after ideal-lap top speed (real store, RBR 2023 rd14 ceiling, pure straight):
```
BEFORE-FIX: theta_P_values[0] = 634231.9 (watts)  | straight sim top speed = 908.8 m/s (3272 km/h) | _power_accel zero-crossing = 908.8 m/s | over-shoot 9.57×
AFTER-FIX : theta_P_values[0] = 784.94  (W/kg)    | straight sim top speed =  94.8 m/s ( 341 km/h) | _power_accel zero-crossing =  94.8 m/s | ratio 1.0000
```

New invariant test:
```bash
py -m pytest tests/unit/physics/test_ideal_lap_top_speed_invariant.py -q
# 2 passed in 0.17s
```

Full physics suite:
```bash
py -m pytest tests/unit/physics/ -q
# 604 passed, 6 skipped in 274.16s
```

Simplification limits (touched paths):
```bash
py -m src.utils.simplification_limits --paths src/physics/utilization/car_prior.py tests/unit/physics/test_ideal_lap_top_speed_invariant.py tests/unit/physics/test_car_prior.py
# PASS (3 files checked)
```

Braking/cornering preservation spot-check (synthetic 4 km mixed track, RBR rd14):
```
lap_time_s = 81.30 | max_speed = 94.8 m/s (341 km/h) | min_speed = 9.0 m/s (32 km/h)
hairpin apex = 9.0 m/s | fast sweep = 93.4 m/s | braking into hairpin: 59.9 → 9.0 m/s (present)
SPOT-CHECK PASS: finite lap, braking into corner, physical speeds
```

**Result:** `pass — all evidence green; over-acceleration fixed; braking/cornering preserved.`

## TDD evidence, if required
- Failing test observed: `py -m pytest tests/unit/physics/test_ideal_lap_top_speed_invariant.py -q`
  → `AssertionError: ideal-lap straight top speed 921.5 m/s exceeds 1.05x the analytic
  terminal velocity 96.3 m/s — power channel is not specific power` (and the `_power_accel`
  zero-crossing assert failed at 921.5 vs 96.3).
- Passing test observed: same command after the fix → `2 passed in 0.17s`.
- Refactor while green: `no — the fix is a 1-line units conversion; no further refactor needed.`

## Docs/contracts touched
- `src/physics/utilization/car_prior.py` module docstring bridge table (the scalar →
  PhysicsParameterSet mapping) — updated `p_max` / `p_max_sigma` scaling rows to reflect the
  `/MASS_KG` conversion. No `docs/architecture/**` touched (reconcile owns the map).

## Assumptions
- `MASS_KG = 808.0` (the reference mass from `longitudinal_fit.py`, already imported into
  `car_prior.py` and used for `theta_D`) is the correct mass for the watts→W/kg conversion —
  it is the same mass baked into the power fit's design column, so it cancels exactly.
- The 6 skipped physics tests are pre-existing skips (telemetry/optional-dep gated), unrelated
  to this change.

## Stop conditions hit
- `none — surfaced the scope/diagnosis conflict to the Commander before fixing (per the stop
  condition "the fix would require changing the capability measurement" — it does NOT; only the
  unit representation), received the ruling to proceed with car_prior in-scope, then proceeded.`

## Out-of-scope observations
- `#510's original C1 "ceiling under-call" diagnosis is confounded by this units bug (the
  ideal-lap ceiling was aphysically high). The G4 NO-GO root cause (aphysical 206.9 m/s ideal
  lap) is now fixed; G6 can re-run C1 on a physical ceiling.`
- `The deprecated FrictionCoupling._compute_longitudinal_max (friction_coupling.py:70) consumes
  max_power the same way; it inherits the now-corrected W/kg value automatically and needs no
  change (slated for #491 removal). No second sim path was introduced.`

## Workflow Feedback
- **Handoff gaps:** The handoff's prime-suspect framing ("`max_power` must be specific power;
  a missing `/mass`") pointed at the **consumer** (`physics_data_models.LongitudinalParameters.max_power`
  / `_power_accel`) and explicitly allowed editing `physics_data_models.py`. But the consumers
  are already correct for the W/kg convention; the actual producer of wrong units is
  `car_prior._build_longitudinal`, which the **Specific Exclusions** named ("Do NOT change …
  the store, car_prior"). So the handoff's allowed-scope and its prime suspect pointed at a
  fix locus (`physics_data_models.max_power`) that would have been **wrong** (a blanket `/mass`
  there double-divides the `fit_power_trajectory` path), while the correct locus was excluded.
  This is the single biggest friction — it forced a Commander ruling mid-run.
- **Context rediscovered:** That `theta_P` has **two producers with different units**
  (`fit_power_trajectory` = W/kg vs the store `p_max` = watts) feeding the same field was not
  in the handoff or anchors; I had to derive it from `longitudinal_fit.py:256` vs `:316` and
  `default_theta_P`. Carrying "theta_P convention = W/kg; store p_max = watts" in the handoff
  would have pointed straight at car_prior.
- **Instructions improvised around:** My own plan template put a green-`command` postcondition
  on the RED (test-first) gate; the engine correctly refuses to attest an engine-checked
  postcondition while the command fails. I refined that gate's postcondition to a qualitative
  "RED observed" attestation (with the failing numbers captured as evidence) and kept the
  green-command check on the GREEN gate where it belongs. Minor; the IMPLEMENTER_PLAN template
  could note that RED steps should use a non-command postcondition.
- **What would have made this easier:** One line in the handoff's "Exact seams" — "NB: theta_P
  is consumed as specific power (W/kg); confirm every PRODUCER (fit_power_trajectory AND the
  car_prior store-injection) emits W/kg" — would have located the bug immediately and pre-empted
  the scope conflict.

## Return status
`complete`
