# notes-664 — Reference laps first-class + class-grain utilization observables

Commander: cmdr-664 (delegated). Epic #659 Wave 2, manifest E. Worktree
`C:/Programs/f1brainz-wt/epic659-664` @ base main `0deea80f`.
Interpreter PIN: `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`.

## Problem statement (reconciled against actual code at `understand`)

Two deliverables, both quali-side (pre-quali constraint, no race-outcome leakage):

**D1 — Reference lap as a first-class STORED product.** The physics-simulated ideal
lap (`car_prior.build_car_ceiling(strictly_pre=True)` → `PhysicsSimulator.simulate_lap`)
already computes a scalar lap time (`SimulatedLap.lap_time_s`), but nothing persists it —
the #628 build script (`scripts/build_driver_utility_observables.py:283-285`) uses only
`nominal_lap.speed_profile`/`distance_profile` and DISCARDS `lap_time_s`. Promote it to a
stored product. Alongside the scalar time, store the CIRCUIT FINGERPRINT = **per-class
TIME-shares** computed from the FIELD-REFERENCE car's simulated lap (retires the #625
`regime_rollup` DISTANCE-share proxy, which is only a lower bound on true corner
time-share). "Per-class" = the #662 SegmentMap classes (seg_type straight/braking_zone/
corner + k=4 corner-severity vocabulary), persisted against `map_version`.

**D2 — Class-grain utilization observables store.** Mirror the existing
`driver_utility_observables` scratch schema (`build_driver_utility_observables.py:65-84`)
but at **per-driver, per-SEGMENT-CLASS** grain (not the 4 regime masks the #628
`compute_regime_deficits` currently tiles into), persisted with `map_version`. Time-ledger
native: **transit-time deficits** (absolute deficit, m/s — NEVER a ratio, #628
anti-circularity). Energy tracked in BOTH channels (§7 pre-registered comparison). G
carried as a one-sided directed uncertainty (see pre-ruling). Speed profiles stay
diagnostic. Its own DB, OFF the f1_data DBs (#632 debt).

## Protected intent (binding — from launch order)
- Anti-circularity: `v_ideal` from `build_car_ceiling(..., strictly_pre=True)`; absolute
  deficit `g = mean(v_ideal - v_real)`, never a ratio.
- Pre-quali: predictions BEFORE quali; quali anchor = post-facto calibration only.
- Frozen constants (F12): consume `layer2/frozen_constants.py`; mint NO new literals. If a
  threshold I need is absent from the frozen set, that is a FLOAT (new named set + re-run),
  never a silent literal.
- Lowest dimensionality; escalation layers dormant in schema from day one.
- No baked-in normality: Student-t / heavy-tailed wherever a form is chosen.

## ⚠️ CRITICAL pre-ruling — G = directed uncertainty (NOT point subtraction)
G consumed as μ=0, one-sided σ⁺, half/truncated Student-t on the "grip only improves"
side; evolution = linear ramp to plateau; circuit-agnostic. Carry as a ONE-SIDED σ band
on the utilization observable; the point value is UNCHANGED. "G barely moves utilization"
is the honest first-pass outcome, not a failure. #663 `grip_baseline.py` exposes a POINT
estimate + Student-t σ (`get_grip_at(...) -> float`; `GripEstimateRecord`; evolution
`offset + asymptote*(1-exp(-rate*x))`) → WRAP to the (μ=0, σ⁺) contract at the consumer
boundary; do NOT re-fit G (sharpening μ off zero is #678, out of scope).

## ⚠️ Scope boundary — build season-CAPABLE, run BOUNDED
Deliver: (1) reference-lap product, (2) utilization store schema + runnable season-capable
pipeline, (3) a VALIDATION run on a bounded, representative slice. NOT the full-season run
(that's #670/Wave 6, HITL). GATING = attribution robustness via JACKKNIFE over derivation
laps on the bounded slice; deficits-sum-to-lap is a CONSTRUCTION check only. A measured-null
/ weak-attribution result is a COMPLETE deliverable (no-frame-kill).

## Baseline reconciliation (order's assumed baseline vs actual code)
- `SimulatedLap.lap_time_s` ALREADY computed+returned (`physics_simulator.py:115-128`);
  "discarded" = never persisted. ✓
- SegmentMap FULLY built: `segment_map/runtime.py` (`SegmentMap`, `segment_of()`,
  `seg_type_code` {STRAIGHT,BRAKING_ZONE,CORNER}, `severity_membership (n,k)`, `class_ids`,
  `map_version`); `derivation/derive.py::derive_segment_map(year,gp,session) -> (SegmentMap,
  VocabularyRef, MapVersion)`; `store.py::SegmentMapStore` persists/loads. CONSUME as-is.
- Field-reference observational lap: `derivation/reference_lap.py::ReferenceLap`
  (`v_ref`=median field speed, `brake_active_frac`) — this is the map-DERIVATION backbone,
  a DIFFERENT object from the physics-SIMULATED ideal lap D1 promotes. Don't conflate.
- #628 absolute-deficit observable: `utilization/driver_utility_observable.py::
  compute_regime_deficits` over 4 regime masks; `build_driver_utility_observables.py`
  persists per-AXIS to scratch `driver_utility_observables`. D2 = per-CLASS + map_version.
- Frozen constants (`layer2/frozen_constants.py`): CORNER_CURVATURE_THRESHOLD,
  BRAKING_ONSET_QUANTILE, MIN_SEGMENT_LENGTH_M, MAP_STABILITY_DRIFT_M, SECTOR_CALIB_*.
  NONE directly cover utilization-deficit / energy thresholds → watch for a needed-but-
  unfrozen threshold (would be a float, not a literal).

## OPEN FLOAT (to Admiral, sent at understand)
#661/#662 forward-ref "#664 = Build 3 SegmentMap seeded/supersede write path"
(`store.py:24,148-163`, `identity.py:33-34`, `derive.py:234`) — DIFFERENT deliverable than
my launch order. My read: stale issue-numbering; seeded/supersede `write` stays
NotImplementedError, out of my scope; log as triage/map-note. Awaiting confirm before plan
freeze.

## Key design questions for `plan`
1. "Per-class" grain definition: exactly which classes tile the lap? seg_type {straight,
   braking_zone} + k=4 corner-severity classes = 6-way? Or corner rows carry SOFT
   membership (deficit distributed by `severity_membership` weight)? Time-shares must sum
   to the lap; deficits per class.
2. Field-reference car for the fingerprint: pooled/median car ceiling across the field vs a
   nominated reference. Each car's OWN reference still baselines its own utilization.
3. Energy channel: relative deployment vs the car's own rolling baseline + phase + derate
   flags; NEVER absolute SOC/kW. Confirm whether the deployment channel needs the total-
   mechanical-energy (½v²+g·h) elevation convention at all — state finding.
4. Store DB path + schema (own DB, #632); escalation columns dormant from day one.
5. Bounded validation slice choice + jackknife-over-derivation-laps design.
