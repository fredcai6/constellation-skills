# Mission Frame — #511 W3 tyre-age grip-evolution + supplant (CAPSTONE)

## Intent
Phase-C **MEASURED-not-wired** characterization: populate per-stint race decay
fits across the 2023 fleet, then separate `f_tyre(compound, age)` (per-axis:
lateral_mech / lateral_aero / traction) from track-evolution `g_track`, run the
ratified supplant test against the lap-time incumbents, and land a per-axis
GO/CONTEXTUAL/NO-GO verdict on a traceable dashboard. Lands entirely inside
`struct:physics.layer2` + region-neutral scripts; no evo wiring (Phase-P #450).

## Affected Capabilities
- `purpose:physics_estimation` / `purpose:physics_utilization` — the physics
  measurement layer. This run ADDS a race-stint cross-session decay
  characterization on top of the W2 per-stint fit path; consumes the quali
  envelope (`session_estimates`) as the car-baseline anchor, does not change it.

## Structural Anchors
- `struct:physics.layer2` (component, `src/physics/layer2/`) — the W3 modules land
  here: `race_stint_batch.py` (new, G1), `tyre_separation.py` (new, G3),
  `tyre_supplant.py` (new, G4). W2 seams consumed: `session_race.py`,
  `stint_estimator.py`, `race_stint_store.py`, `pooling.py`.
- `struct:common` (`src/common/pairwise_ordering.py`) — neutral supplant metric.
- `struct:physics` (`mass_model.py`) — race_mass (used inside W2 loader).
- scripts/ (non-map nodes): `populate_race_stint_estimates.py` (G1 CLI),
  `tyre_age_dashboard.py` (G5) — the region-neutral boundary that wires evo
  incumbents into the supplant comparison.
- `struct:cp.empirical_sensor` (`src/compound_prior/empirical_sensor.py`) — #443
  cross-check, read by the dashboard script ONLY (comparator, not incumbent).

## Governing Constraints / Assumptions
- `constraint:physics_region_no_evo_import` — `src/physics/` must import no
  evo-region package. The separation (G3) and supplant scoring (G4) stay
  evo-free; incumbent predictions (C# floor, compound_prior γ, #443) are
  **injected as arrays** by the region-neutral dashboard script (G5). This is
  the sanctioned "comparator via a neutral boundary."
- Anti-circular: physics fit uses STRUCTURAL priors only (monotone-up compound
  ordering, k≥0, plausible ranges) — NO #443 empirical magnitudes. Supplant
  truth (lap-time degradation slope) is an independent channel from the physics
  feature (telemetry grip decay).
- `lesson:loo-residual-diagnostic-over-self-weighted-predictor` — every
  residual/calibration/stability/covariance-honesty diagnostic over the pooled
  (self-weighted) fit MUST use leave-one-out / out-of-sample.
- DB/telemetry-store is the ONLY data source; `py` not `python`.
- 2σ = reference NOT a gate (fine-margin); honest-null is a complete deliverable.

## Decision Anchors & Decision Pressure
- `decision:regime_readiness_rubric` (#512) — the per-axis readiness-verdict +
  dashboard pattern this capstone mirrors (coverage / separability / LOO
  stability / LOO covariance-honesty; per-axis GO/CONTEXTUAL/NO-GO; 2σ reference).
- `decision:c1_driver_utilization_design` (#510) — car-envelope-from-quali anchor
  lineage.
- **Decision pressure (candidate for reconcile):** the W3 separation model
  (crossed log-grip `car_envelope + f_tyre(compound,age) + g_track + noise`) and
  the **net-new `g_track`** within-weekend track-evolution term (pooling.py has
  no within-weekend time term) — a new measured axis + a new pooling structure.
- **Decision pressure (candidate):** the neutral-boundary INJECTION pattern for
  the supplant comparators (physics module evo-free, takes injected incumbent
  arrays; script reads evo) — a reusable physics↔evo comparison boundary.

## Claims / Evidence Surfaces
- W2 inherited (verify on current data, do not trust blind): 889 clean 2023
  stints; track_status 100% populated 2023; absolute `tyre_life` (some stints
  start ~4 = warm-up); `cumulative_track_laps` stored. G2 coverage diagnosis
  re-confirms on the actual populated store.
- #443: empirical sensor LOO P=0.8032, monotone-up ladder, perm z=5.22σ — the
  cross-check bar at the supplant gate.
- Supplant: physics μ_tyre(age) P via neutral `pairwise_ordering_accuracy` vs
  {absolute-C# floor, compound_prior γ}; magnitude R²; honest covariance overlap;
  LOO for any self-fit diagnostic.

## Map Confidence / Staleness / Disputes
- Map is fresh (W1 #562, W2 #563, #443 all reconciled 2026-06-28; `struct:cp.
  empirical_sensor` + `src/common/pairwise_ordering` newly added). High
  confidence. No scout gate needed. The one open area is empirical (does coverage
  hold, does separation identify) — handled by the G2 diagnose-first checkpoint
  and LOO diagnostics, not a map-trust risk.

## Out of Scope
- Quali five-view path (session_estimator/EstimateStore/session_estimates) —
  untouched (read-only anchor). Evo wiring / Phase-P #450 race-weekend
  composition. Multi-season (structure for it; fit 2023 only). Modifying W2
  modules (consume, not change — float if a defect surfaces). #557 traction
  param-aliasing, #502 coast, #506 σ over-claim, #546/#549 follow-ons.
