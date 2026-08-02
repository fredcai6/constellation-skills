# Pre-registration — correlation screen primary axis

**Registered:** 2026-07-18T01:39:24Z, before writing or running any correlation-computing code this run (no `g1_correlation_screen.py` or equivalent exists on disk yet at this timestamp — verify via `git log`/file mtimes at review time).

## Primary axis (pre-registered)

`lateral_total_grip_g := lateral_mech_grip_g + lateral_aero_grip_g` (from `data/physics_estimates.db` table `session_estimates`, `session_type='Q'`).

Sign convention: higher = more total lateral-g capability = faster cornering = expected to correlate NEGATIVELY with quali pace-gap-to-median (higher grip → smaller/more-negative gap) and NEGATIVELY with `quali_error` as defined in `PROBLEM_STATEMENT.md` (`actual_pace_gap - recent_history_baseline`), i.e. we expect `corr(lateral_total_grip_g, quali_error) < 0` if physics carries usable signal.

## Rationale (physical, not data-driven)

F1Brainz's own prior #445 axis-consolidation work (cited before this run: `src/physics/capability.py:110-112` "the validated −0.89 signal used the 90th pct"; `docs/architecture/packets/physics.md:246-249` Capability API) found cornering/apex-speed capability dominates pace (−0.89) over drag CdA (−0.50, secondary, +0.31 complementary). That work used a different computation (`ApexPace` over raw `ApexObservation` sequences, not the `session_estimates` table), so it cannot be reused directly here — but it is the basis for choosing THIS run's primary axis: `lateral_mech_grip_g + lateral_aero_grip_g` is the `session_estimates` table's closest analog to that validated cornering-capability concept (total peak lateral-g ceiling, mechanical + aero components, additive in the same units).

## Secondary/exploratory axes (reported separately, clearly labeled, never as headline)

All other raw `session_estimates` columns: `drag_area_closed_m2`, `brake_decel_ms2`, `brake_aero_decel_per_m`, `traction_accel_ms2`, `traction_aero_accel_per_m`, `max_power_w`, `power_drag_area_m2`, `coast_rolling_decel_ms2`, `coast_drag_area_m2`. A secondary composite `power_to_drag := max_power_w / drag_area_closed_m2` (straight-line pace proxy, the complementary −0.50 axis from the same prior finding) is also reported as exploratory, not primary.

## Discipline

No axis or composite is added to, or removed from, this list after seeing any correlation number. If the primary axis is later judged a poor physical proxy, that is a finding for the NEXT run's pre-registration, not a mid-run substitution.
