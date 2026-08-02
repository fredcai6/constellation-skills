# Implementer Handoff

## Gate
g5 (RE-PLANNED) — Diagnose + fix the ideal-lap simulator over-acceleration. The G4 NO-GO traced
to an aphysical ideal lap; this gate fixes the real blocker so G6 can re-run C1 honestly.

## Task
**Diagnose (systematic-debugging discipline) then fix** the bug that makes the canonical ideal-lap
simulator accelerate the RBR ideal lap to **~206.9 m/s (745 km/h)** when the measured straight-line
capability implies a physical drag-limited terminal velocity of **~99 m/s (356 km/h)** — a **2.09×**
over-shoot. The capability MEASUREMENT is physical (P_max=629 kW, CdA=1.130 → terminal ≈99 m/s,
identical OLD vs WIRED). The bug is in the **ideal-lap machinery**: `CapabilityEnvelope._power_accel`
(the straight-line `power/v − drag − rolling` model) and/or `PhysicsSimulator.simulate_lap` /
`_forward_pass` / `speed_caps`. Fix it so the simulated ideal-lap top speed respects the drag-limited
terminal velocity, then add a truth-anchored invariant test.

## Protected Intent
This is a SIM/ENVELOPE-machinery fix, NOT a re-calibration. Do NOT change the capability MEASUREMENT
(the store params, the braking/traction/power-drag/lateral fits) — they are physical. The fix must make
the ideal lap top out near the envelope's own terminal velocity WITHOUT breaking braking/cornering
behaviour (the forward-backward sweep, the friction ellipse, the braking capability).

## Test Mode
TDD-leaning: write the failing invariant first (L1/L2). Truth-anchored physics evidence required at the
highest applicable level — e.g. **L1 analytical:** at the speed where `_power_accel(v)=0` (terminal
velocity from `power/v = drag(v)+rolling`), the simulated straight-line top speed must match within
tolerance; **L2 invariant:** the ideal-lap `max_speed_ms` ≤ ~1.05× the analytic terminal velocity for a
representative RBR ceiling. Keep the existing physics_simulator/capability_envelope tests green.

## Close Criteria
- Root cause identified and stated (the exact line/formula/units producing the 2.09× over-shoot).
- Fix applied in the ideal-lap machinery (envelope `_power_accel` and/or simulator integration); the
  simulated ideal-lap top speed for the RBR ceiling drops from ~206.9 m/s to ≈ the analytic terminal
  velocity (~99 m/s, ≤~5% over).
- A truth-anchored invariant test encodes it (top-speed-vs-terminal-velocity / `_power_accel` zero-crossing).
- Braking + cornering sim behaviour preserved (forward-backward sweep still produces sane laps; spot-check
  a real case lap time is still plausible).
- `py -m pytest tests/unit/physics/ -q` green; `py -m src.utils.simplification_limits` clean on touched paths.
- A short DIAGNOSIS note (what the bug was, why 2.09×) in the result.

## Allowed Scope
- `src/physics/capability_envelope.py` (`_power_accel` and the straight-line/power-limit path).
- `src/physics/physics_simulator.py` (`simulate_lap` / `_forward_pass` / `speed_caps` longitudinal integration).
- `src/physics/physics_data_models.py` ONLY if a units bug lives in `LongitudinalParameters.max_power` /
  `drag_acceleration` (verify units there — `power/(speed)` is consumed as an ACCELERATION, so `max_power`
  must be specific power; a W-vs-W/kg units mismatch is a prime suspect).
- `tests/unit/physics/` (invariant tests), `reports/physics/` (gitignored probe output if any).

## Specific Exclusions
- Do NOT change the capability measurement / fits (braking_fit, traction_fit, power_drag_view,
  lateral_envelope, the store, car_prior). The measured params are physical.
- Do NOT touch the utilization layer / dashboard (that's G6).
- Do NOT edit `docs/architecture/**` (reconcile owns the map).
- Do NOT change `regime_utilization` thresholds or `U_CLIP_MAX`.

## Constraints
- `py` not `python`. Physics model change → highest-applicable L1-L4 evidence with units/bounds explicit.
- `constraint:physics_region_no_evo_import`.
- One canonical path (no second sim).
- If the diagnosis shows this is NOT a contained bug but a deep modeling gap (e.g. the envelope has no
  coherent terminal-velocity concept), STOP and surface to the Commander before forcing a fix.

## Map Anchors (inbound)
- **Structural:** `struct:physics` — `capability_envelope.py` (`_power_accel`, `traction_capability`,
  `from_parameters`), `physics_simulator.py` (`simulate_lap`, `_forward_pass`), `physics_data_models.py`
  (`LongitudinalParameters.max_power`, `drag_acceleration`).
- **Capability:** ideal-lap simulation from the capability envelope.
- **Decision anchors:** `decision:ideal_lap_sim_two_sided_evaluator` — the ideal-lap-as-ceiling contract;
  this bug directly undermines it (an aphysical ideal lap is not a valid ceiling). Note for reconcile.
- **Evidence:** ideal-lap top speed ≈ analytic terminal velocity; C1 (G6) can then test the real premise.

## Exact seams (verified from source)
- `capability_envelope._power_accel(self, speed)` → `power/(speed+eps) − drag − rolling`, where
  `power = self.params.longitudinal.max_power`, `drag = longitudinal.drag_acceleration(speed, air_density)`,
  `rolling = longitudinal.theta_R`. **`power/(speed)` is consumed as an ACCELERATION** (drag/rolling are
  m/s²) → confirm `max_power`'s units make that dimensionally correct (specific power m²/s³, i.e. P_max/mass).
  A missing `/mass` (treating total watts as specific power) would make `power/v` ~mass× too large → top
  speed too high. **CHECK THIS FIRST.**
- `physics_simulator.simulate_lap(...)`: `power_scale = mean(theta_P_values)`; runs `_forward_pass` +
  backward + `speed_caps`; `speeds = min(forward, backward, speed_caps)`; returns `max_speed_ms = max(speeds)`.
- The analytic terminal velocity for a probe: solve `_power_accel(v)=0`, i.e. `power/v = drag(v)+rolling`.
  For RBR (P_max=629 kW, CdA=1.130, rho=1.148, MASS=808): ≈99 m/s. Reproduce the 206.9 m/s first, then
  show your fix brings it to ≈99.
- Reproduce the ideal lap: `car_prior.build_car_ceiling(store_df, 2023, "Red Bull Racing", target_round=14)`
  on `data/physics_estimates_g3wired.db` → `.envelope` / `.params`; `PhysicsSimulator().simulate_lap(track_df,
  params, sample=False)` → `.speed_profile.max()`. Ribbon via `ribbon.build_session_ribbon` (see the dashboard / characterize.py).

## Data Locations (absolute; main checkout)
- Store `C:/Programs/f1Brainz/data/physics_estimates_g3wired.db`; cache `C:/Programs/f1Brainz/data/telemetry` (offline).

## Required Evidence
- The DIAGNOSIS (root-cause line + the 2.09× explanation).
- Before/after ideal-lap top speed for RBR (≈206.9 → ≈99 m/s).
- `py -m pytest tests/unit/physics/ -q` (green) + simplification clean + the new invariant test output.
- A spot-check that a real case still produces a plausible lap (sweep not broken).

## Suggested Model Tier
Stronger (Opus) — systematic-debugging of a physics/units bug feeding the headline re-eval; correctness critical.

## Authority
- The redirect to fix the sim is the user's decision (made). You diagnose + fix within scope.
- Do NOT change the capability measurement. If it's a deep modeling gap not a contained bug, STOP + surface.

## Stop Conditions
Stop and return if: it is not a contained bug (deep modeling gap); the fix would require changing the
capability measurement; braking/cornering sim regresses and can't be preserved; scope must be exceeded.

## Return Format
Return IMPLEMENTER_RESULT to `.agent-work/518-braking-ceiling-reeval/crew-handoffs/g5-implement-result.md`:
the DIAGNOSIS (root cause + why 2.09×), the fix (files/lines), before/after ideal-lap top speed, the
invariant test, test+simplification output, the braking/cornering-preserved spot check, assumptions,
stop conditions, out-of-scope observations, and **Workflow Feedback**.
