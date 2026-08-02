# #627 (+#506) Problem Statement — Stage-1 Phase 3 unified-basis refit + σ-honesty

Delegated run. Principal = frozen Admiral LAUNCH_ORDER (`ShipF-627`). No reachable human.

## The ask (reconciled against code truth 2026-07-18)

Turn the five per-view physics fits (`src/physics/layer2/{braking,traction,lateral,power_drag,coast}_view.py`)
into ONE physical basis solved across the lap, with honest cross-view-aware uncertainty, so multi-view
redundancy REDUCES σ instead of being ignored. Absorbs #506 (data-driven systematic floors).

## Baseline reconciliation (delegated understand: is the headline already shipped? NO)

Verified against source, not the order's framing:
- **Store holds within-view covariance ONLY.** `estimate_store.py` `_JSON_COLUMNS` = the five per-view 2×2
  blobs (`braking_covariance` … `coast_covariance`); `regime_readiness._compute_param_pair_corr` reads one
  view's own 2×2. No cross-view `cov(CdA,b_b)` / `cov(CdA,b_t)` / grip-triplet term persisted anywhere. → Tier-1 #1 is a real gap.
- **σ is a static table.** `SYSTEMATIC_FLOOR = {cda:0.04, p_max:0.04, A0:0.04}` (`estimate_store.py:53`) applied
  as a flat relative floor; `pool_random_effects` (`pooling.py`) shrinks `sigma_mu = sqrt(1/Σwr)` toward 0 with
  n, treating every session as independent → pooling claims sub-% season knowledge that the shared systematic
  (mass ±2.5%, ρ) forbids. → Tier-1 #2 / #506 is a real gap.
- **No explicit-unknown status.** No axis carries resolved/unresolved; a cold-constant θ_R (used in the
  de-conflations) and a degenerate/absent view are emitted the same way a measured ≈0 would be. → Tier-1 #3 gap.

The genuine in-scope gaps match the launch order. Headline is NOT already-done.

## Scope (frozen by the order)

TIER 1 (MUST): (1) cross-view covariance persistence — NON-DEFERRABLE, must demonstrably tighten a shared
param's σ; (2) σ-honesty #506 — per-session Jacobian propagation + correlated-vs-independent split flooring the
pooled σ_μ; (3) explicit-unknown contract — testable resolved/unresolved status + reserved unknown slot.

TIER 2 (SHOULD; close-with-number OR bounded-defer-with-number): grip-triplet cross-coupling; dual-CdA
(PowerDrag vs Coast) reconciliation; a_long reconciliation; shared-trajectory-noise propagation.

TIER 3 (DEFERRABLE): 2026 two-state (Z/X) aero — bounded-defer w/ recommendation unless Tier 1+2 solid.

## Pre-settled decisions (from the order; cited at each checkpoint)

- **a_long reconciliation = bounded-defer** (pre-ruling #2): `decision:decoupled_1d_longitudinal` + #523/#546
  are a documented structural HONEST-NULL (Kalman-RTS LOOSE coupling at throttle-on diverges circuit-topology-
  dependently; coast 21-26% structural sample loss). Do NOT re-merge. Quantify the σ-impact bound instead.
- **cda_frontier_jacobian** (shared by braking/traction views) already computes the CdA→{b_b,b_t} coupling and
  bakes it into the within-view diagonal — the cross-view `cov(CdA,b_b/b_t)` is deterministically RECOVERABLE
  and is the cheapest real cross-view term to persist + demonstrate.
- **Honest wide σ over optimistic tight σ** (pre-ruling #3). Correlated-shared systematic MUST floor pooled σ_μ.
- **Backward-readable store** (pre-ruling #4): additive columns only; `_migrate_missing_columns` already
  ALTER-adds nullable columns. Phase-2 weekend_state consumers read value/`_sigma` columns by name — must stay green.
- **No production-default / gold / circuits.yaml / data/*.db changes** (pre-ruling #5).

## Gate (how judged)

Cross-view covariance persisted+real (NON-DEFERRABLE); #506 delivered w/ pooled-σ_μ floor; explicit-unknown
testable; each Tier-2 fracture CLOSED-with-number or DEFERRED-with-quantified-bound (undecided/unbounded = fail).

## Float triggers (up to Admiral, via verdict)

Cross-view covariance persistence infeasible; abandoning unified-basis architecture; a store change breaking a
consumer I cannot migrate; any production-default/gold change; a scope cut.
