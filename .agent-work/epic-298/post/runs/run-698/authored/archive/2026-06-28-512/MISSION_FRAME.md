# Mission Frame — #512 Regime-capability vector readiness (C3)

## Intent
Characterize the per-car regime-capability vector as a prediction input; land GO/CONTEXTUAL/
NO-GO per component to spec §4. Measured, not wired. Mostly readout over existing machinery.

## Affected capabilities
- `struct:physics.layer2` capability measurement — read-only consumption of the populated
  2023-Q five-view `estimate_store` + `pool_driver` (random-effects τ, two-way team×circuit).
- New: a **readiness readout** capability (coverage / separability / stability / covariance
  honesty + verdict rubric) composing the above. No evo-region touch (Phase P is later #450).

## Structural anchors
- `struct:physics.layer2`: `estimate_store.py` (EstimateRecord/EstimateStore — the component
  columns + covariance blobs), `pool_driver.py` (`pool_store`, `render_markdown` — per-car
  cards + two-way variance), `pooling.py` (`pool_random_effects` DL-τ², `fit_two_way`,
  `fit_drift`), `fit_evidence.py` (`axis_identifiability`, `pooling_feasibility` — precedent;
  note it targets the OLD Layer-1 fit_store, not the five-view store — reuse the *idea*, point
  at the new store).
- `struct:physics.utilization`: regime definitions (slow `a_lat<25`, fast `a_lat≥25`) for
  consistent component naming.
- New module lands under `src/physics/layer2/` (composes pool_driver) — name e.g.
  `regime_readiness.py`; dashboard `scripts/regime_capability_dashboard.py`.

## Governing constraints / assumptions
- `constraint:physics_region_no_evo_import` — no evo-region import (verify).
- Honest covariance is first-class (§4). The covariance blobs are the param-pair separability
  source — must use the real 2×2 blobs, not the diagonal σ alone.
- Tests must not depend on `data/` (gitignored, lives in MAIN checkout) — use synthetic
  fixtures; the real 2023-Q run reads the absolute main-checkout DB at G2 only.

## Decision anchors + decision pressure
- `decision:traction_own_measured_frontier`, `decision:c1_driver_utilization_design`,
  `decision:ideal_lap_sim_two_sided_evaluator` — frame the components' meaning.
- **Decision pressure (candidate):** the GO/CONTEXTUAL/NO-GO **rubric thresholds**
  (frac_team / σ-calibration z / coverage) — a durable choice future runs could rediscover;
  surface to reconcile as a decision-anchor candidate.

## Claims / evidence surfaces to re-confirm (NOT trust silently)
- `claim`: "constructors not separable, frac_team ≤ 3%" (#492-era). **Map confidence: this is
  a prior finding; #512 RE-MEASURES it on the current g3wired store.** A broad NO-GO is a
  legitimate terminal result.
- `#557`: traction not cross-session-stable as one stationary frontier → traction component is
  pre-derived CONTEXTUAL (set-aside; do not rebuild here).

## Out of scope
- Grip-evolution STATE (tyre decay, track mult) → **#511**.
- Traction corner-indexed rebuild → **#557**.
- Any feature wiring into evo (`race_weekend`) → Phase P **#450**.
- Re-running the season fit / changing estimation — we consume the existing store.

## Map confidence
`packets/physics.md` high-confidence and current (reconciled through #525/#527). The only
stale element is the #492-era separability *number*, which this issue re-measures by design.
