# Mission Frame — #627 (+#506) Phase 3 unified-basis + σ-honesty

## Intent
Persist REAL cross-view covariance so multi-view redundancy tightens shared-parameter σ; replace the static
systematic floor with data-driven per-session Jacobian propagation whose SHARED component floors the pooled σ_μ
(#506); and give every basis axis an explicit resolved/unresolved status with a reserved "unknown" slot. All
within `struct:physics.layer2`, backward-compatible with the Phase-2 `weekend_state` consumers.

## Affected Capabilities
- **Per-session five-view estimate → store** (`struct:physics.layer2`): today emits within-view 2×2 covariance +
  a static `SYSTEMATIC_FLOOR`. This run adds cross-view terms, data-driven systematic, and status.
- **Layer-A cross-session pooling** (`pooling.py`/`pool_driver.py`): today `pool_random_effects` shrinks σ_μ→0
  with n as if sessions were independent. This run floors σ_μ by the correlated-shared systematic.

## Structural Anchors
- `struct:physics.layer2` — `src/physics/layer2/` — component.
- `estimate_store.py` — `EstimateRecord`, `record_from_estimate`, `SYSTEMATIC_FLOOR`, `_migrate_missing_columns`
  (the additive-migration path — file, level).
- `pooling.py::pool_random_effects` / `pool_driver.py::pool_store` — the pooled-σ_μ site (function).
- `braking_view.py::cda_frontier_jacobian` + `BrakingView.fit` (lines 242-249) / `traction_view.py` — the
  already-computed-then-discarded `J = d(coef)/d(CdA)`; `cov(CdA,[a,b]) = σ_CdA²·J` is the recoverable cross-view term.
- `power_drag_view.py::PowerDragResult` (CdA, P_max, joint_prior) + `coast_view.py::CoastViewResult` (coast CdA) —
  the two independent CdA measurements whose fusion is the redundancy-tightening demonstration.
- `scripts/nuisance_sensitivity.py` — the perturbation-Jacobian probe to promote into a per-session budget module.
- `src/physics/weekend_state/*` (`layer1_physics.py`, `gate_spec.py`, `gate_f6.py`, `floor.py`) — Phase-2
  consumers reading value/`{axis}_sigma` columns by name (backward-compat surface — must stay green).

## Governing Constraints / Assumptions
- `constraint:physics_region_no_evo_import` — new code must not import evo.
- Store must stay backward-readable (additive columns; `_migrate_missing_columns` ALTER-adds nullable).
- No production-default / gold / circuits.yaml / `data/*.db` changes (LAUNCH_ORDER pre-ruling #5).
- Honest wide σ over optimistic tight σ (pre-ruling #3).

## Decision Anchors & Decision Pressure
- `decision:decoupled_1d_longitudinal` (+ #523/#546 HONEST-NULL) — GOVERNS the a_long fracture: braking uses the
  decoupled Kalman-RTS filter, throttle/coast use `clean_longitudinal_from_raw`; re-merge is a documented
  structural failure. → a_long reconciliation = **bounded-defer with a σ-impact number** (pre-ruling #2), NOT a re-merge.
- **Decision pressure (candidate for reconcile):** the cross-view covariance representation (targeted sparse
  cross-terms vs a dense full-basis covariance) and the pooled-σ_μ shared-floor mechanism are new load-bearing
  interfaces — surface as decision candidates.

## Claims / Evidence Surfaces
- NON-DEFERRABLE gate claim: fused-CdA σ (PowerDrag ⊕ Coast) < PowerDrag-only σ on ≥1 real 2023 Q session
  (before/after number). Cross-view `cov(CdA,b_b)` persisted non-trivially and reloads.
- #506 claim: pooled σ_μ for CdA/P_max no longer shrinks below the shared-systematic floor (before/after number);
  matches nuisance_sensitivity budget (~4.3% CdA, ~3.7% P_max) on Monza RBR 2023.
- Explicit-unknown claim: a genuinely-unmeasured axis (θ_R / degenerate / absent view) reads `unresolved` with
  reserved wide σ; a measured axis reads `resolved` — a testable property.

## Map Confidence / Staleness / Disputes
- Map is current for `struct:physics.layer2` (physics.md packet, verified against source this run). No stale area
  gates the plan. The x7 fracture map (`.agent-work/archive/.../x7-basis-map-RESULT.md`) is code-truth 2026-07-17,
  cross-checked against source this run — trusted.

## Out of Scope
- Re-merging a_long across views (documented HONEST-NULL — bounded-defer only).
- Changing the production pinning CdA / gold bundle / evo path / circuits.yaml.
- Building the 2026 two-state aero joint fit (Tier-3 — bounded-defer with recommendation).
- The `kind=3` Matérn outer-loop feedback (#496 remainder — not this issue).
