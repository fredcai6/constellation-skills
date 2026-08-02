# Mission Frame — #664 reference laps first-class + class-grain utilization observables

## Intent
Land two quali-side products in `src/physics/`: (D1) the physics-simulated reference lap as
a FIRST-CLASS STORED product — scalar ideal lap time + a per-segment-class TIME-share circuit
fingerprint from a field-reference car's simulated lap; (D2) a per-driver, per-segment-class
utilization observables store (absolute transit-time / speed deficits + dual energy channels
+ a one-sided G uncertainty band), persisted with `map_version`, in its OWN db. Build the
pipeline season-CAPABLE; validate on a BOUNDED slice; gate on jackknife attribution
robustness. Map adds real context here (this lands squarely in `struct:physics.utilization`
and consumes `segment_map`), so the frame is full.

## Affected Capabilities
- per-regime driver utilization / driver-utility latent (#628/#510) — today tiles a lap into
  4 REGIME masks (braking/slow/fast/straight) and reports absolute deficits per axis; this
  run adds a SIBLING that tiles by SEGMENT CLASS from the persisted `SegmentMap` and persists
  per-class, with map_version + energy + G-band. Descriptive; prediction-isolated.
- ideal-lap simulation (`struct:physics.utilization.car_prior` → `PhysicsSimulator`) — today
  the scalar `lap_time_s` is computed and discarded; this run persists it + its class
  time-share fingerprint.
- circuit fingerprint (retires #625 `regime_rollup` DISTANCE-share) — replaced by simulated-
  lap TIME-share.

## Structural Anchors
- `struct:physics.utilization` — `src/physics/utilization/` (component). New modules land here.
  - `car_prior.build_car_ceiling(strictly_pre=True)` → `CarCeilingResult(params, ...)` [car_prior.py].
  - `driver_utility_observable.compute_regime_deficits(...)` — the #628 absolute-deficit core
    (reuse its regime-mask + resample discipline; the new class-grain core is a sibling).
- `struct:physics.segment_map` — `src/physics/segment_map/` (consume AS-IS):
  - `runtime.SegmentMap` — `segment_of(distance)`, `seg_type_code` {STRAIGHT=0,BRAKING_ZONE=1,
    CORNER=2}, `severity_membership (n,k)`, `class_ids`, `map_version`, `boundaries_m`, `length_m`.
  - `derivation.derive.derive_segment_map(year,gp,session) -> (SegmentMap,VocabularyRef,MapVersion)`.
  - `store.SegmentMapStore` — `get_current`/`get_by_version`.
  - `derivation.reference_lap.build_reference_lap(...)` / `reference_lap_from_store(...)` →
    `ReferenceLap` (pooled field OBSERVATIONAL backbone; distinct from the simulated ideal lap).
- `struct:physics.physics_simulator` — `PhysicsSimulator.simulate_lap(track, params) ->
  SimulatedLap(lap_time_s, max_speed_ms, distance_profile, speed_profile)` [physics_simulator.py:50-128].
- `struct:physics.layer2` — `estimate_store.EstimateStore` (car prior source, read-only);
  `grip_baseline`/`grip_store` (module G, #663): `get_grip_at(store,year,gp,session,cum_laps)->float`,
  `GripEstimateRecord{session_offset,curve_asymptote,curve_rate,*_sigma,fit_status}`,
  evolution `offset+asymptote*(1-exp(-rate*x))`; `frozen_constants` (#660, F12 set).

## Governing Constraints / Assumptions
- constraint:db-canonical — analysis reads the SQLite/telemetry stores, never live FastF1.
- constraint:anti-circularity (#628) — `v_ideal` from `strictly_pre=True`; deficit is ABSOLUTE
  (`mean(v_ideal - v_real)`), NEVER a ratio.
- constraint:pre-quali — predictions before quali; no race-outcome leakage into any observable.
- constraint:frozen-constants (F12) — consume `frozen_constants.py`; mint NO new literal
  thresholds. A needed-but-unfrozen threshold is a FLOAT (new named set + re-run), not a literal.
- constraint:own-db (#632) — utilization/reference-lap stores write to their OWN db, off the
  f1_data DBs.
- constraint:tests-clean-real-dbs (#656) — tests must not dirty real DBs (temp/scratch only).
- constraint:no-normality — Student-t / heavy-tailed wherever a distributional form is chosen.
- constraint:region-boundary — stays inside physics region; no evo import, no physics→evo coupling.

## Decision Anchors & Decision Pressure
- decision:c1_driver_utilization_design — split impure, covariance-owned; single canonical
  ideal-lap path EstimateStore→car_prior→CapabilityEnvelope→PhysicsSimulator; `strictly_pre`
  load-bearing for held-out falsifiability.
  @grade: settled/human · leans g1-fingerprint,g2-refstore,g3-utilstore
- decision:corner-gate-is-curvature (#660) — corner/straight gate is CURVATURE not lateral-g.
  @grade: settled/human
- decision pressure (surface as candidate): **class-attribution grain** — how a lap tiles into
  "classes": seg_type {straight, braking_zone} as hard classes + corner rows distributed by
  SOFT `severity_membership` over k corner classes → a (2 + k)-way class vocabulary whose
  per-class time-shares sum to the lap. Load-bearing interface → design-it-twice.
- decision pressure (candidate): **field-reference car** for the fingerprint — pooled/median
  car ceiling across the field vs a nominated constructor. Each car's OWN reference still
  baselines its own utilization.
- decision pressure (candidate): **G one-sided wrap** contract shape (μ=0, σ⁺, half-Student-t)
  at the consumer boundary — binding per launch-order pre-ruling; record as settled/inherited.
- decision pressure (candidate): **energy channel** needs total-mechanical-energy (½v²+g·h)
  on elevation circuits, or does deployment-relative suffice? Launch order asks me to state a
  finding.

## Claims / Evidence Surfaces
- claim:deficits-sum-to-lap — per-class transit times sum to the simulated lap time
  (CONSTRUCTION check; cannot catch misattribution). Re-confirmed in G1 unit tests.
- claim:attribution-robust — per-class deficits stable under boundary jitter within the frozen
  quantile's uncertainty (JACKKNIFE over derivation laps on the bounded slice). GATING; G4.
- claim:anti-circular — no `v_real/v_ideal` ratio anywhere; ceiling is `strictly_pre=True`.
  Re-confirmed by grep + unit test in G1/G3.
- claim:G-band-one-sided — G moves only the one-sided σ, never the point deficit. G3 unit test.

## Map Confidence / Staleness / Disputes
- `segment_map` packet coverage is #625-era (distance-share `regime_rollup`); the #661/#662
  runtime+derivation are NEWER than the physics.md utilization section — I verified them by
  direct source read (high confidence), not the packet. Map fence: I do not edit the packet;
  map impact recorded as prose for the epic closeout cartographer.
- STALE FORWARD-REFS: `store.py`/`identity.py`/`derive.py` label #664 as "Build 3 seeded/
  supersede write path" — a different deliverable than this launch order. Floated to Admiral;
  triage-note to re-point them. Does NOT alter D1/D2 gates.

## Out of Scope
Race-side observables (Build 2); absolute ERS/SOC/kW; ANY fingerprint FITTING (#666); moving
G's μ off zero (#678); the FULL season-scale run (#670); the SegmentMap seeded/supersede write
path (stays NotImplementedError); re-opening k (#642 downstream); re-fitting grip G (#687/#688).
