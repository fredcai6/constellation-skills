# Mission frame — #628 Phase 3b driver utility (produced, not consumed)

## Intent
Produce a **driver-utility latent** on the pooled physics car-capability basis: per-driver, per-axis
**access** of the car envelope, as a race-history prior with a weekend update. Bank it (round-1 artifact) for
round-2 driver-affinity consumption. Gate it with an un-gameable **held-out** replication test built to be
falsifiable (no `observed÷capability`).

## Affected capabilities
- `struct:physics.utilization` — per-regime driver utilization (existing DESCRIPTIVE #510 layer) gains a NEW
  falsifiable driver-utility LATENT sibling. The descriptive ratio layer is untouched.
- Pooled car capability (`car_prior.build_car_ceiling`) — CONSUMED read-only as the causal denominator; not
  re-fit.

## Structural anchors
- `src/physics/utilization/car_prior.py::build_car_ceiling` (causal one-sided kernel; `strictly_pre` mode).
- `src/physics/utilization/regime_utilization.py::_build_regime_masks` (4-regime tiling: braking / slow_corner
  / fast_corner / straight — the axis set) and `regime_utilization` core (v_ideal via `PhysicsSimulator`).
- `src/physics/session_fit.py::fit_best_lap_trace` (LEAN realized-trace extractor; skips the MAP fit).
- `src/physics/layer2/estimate_store.py` — `UNRESOLVED_AXIS_SIGMA_FRAC` + per-axis `*_status` machinery
  (REUSE for the explicit-unknown contract).
- `src/physics/layer2/pool_driver.py` — pooling primitives (`pool_random_effects` shrinkage) prior art.

## Governing constraints / assumptions
- DB-only analysis (no FastF1 from analysis; `fit_best_lap_trace` reads the telemetry_store mirror first).
- NEVER commit `data/*.db`; scratch observable DB is untracked.
- Headless compute via `Start-Process -WindowStyle Hidden`; poll artifacts, never idle a watcher.
- `py` launcher, not `python`. `py -m pytest tests/unit/physics/...`.

## Decision anchors + decision pressure
- `decision:c1_driver_utilization_design` (2026-06-24): (pt2) measured driver contaminates the through-W
  frontier; (pt3) `split_is_impure=True`. **Decision pressure / candidate:** the falsifiable gate REQUIRES a
  `strictly_pre=True` causal ceiling for held-out sessions to break that contamination — a NEW decision the
  Cartographer should anchor (extends, does not overturn, #510: the descriptive layer keeps its through-W
  frontier; the gate uses the strictly-pre one). Surface at reconcile.
- New decision candidate: the driver-utility latent is **additive absolute-deficit**, not a ratio (F4).

## Claims / evidence surfaces
- The held-out gate result (recomposition RMSE vs δ=0 baseline out-of-sample; per-axis cross-driver variance
  out-of-sample). Honest-null admissible.
- Explicit-unknown status per axis (reserved slots). Reputational smell-test (non-gating).

## Map confidence
- HIGH: car_prior, regime_utilization, estimate_store status machinery, fit_best_lap_trace all read from
  source this run; timings measured empirically. No stale/disputed area the plan depends on.

## Out of scope
Round-2 driver-affinity consumption, evo-feature consumption, delta-basis evolution, re-fitting the Phase-3
car basis, full multi-season production table (bounded 2023 slice suffices for the gate).
