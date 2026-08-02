# x7 — Current Basis Map & Dropped Correlations (READ-ONLY, code-truth as of 2026-07-17)

Scope: map current truth only. No new design proposed.

## (a) Basis map — every parameter each view estimates

All five views are session-level, per-constructor (pooled across both cars) capability-frontier
fits over `frontier_fit.fit_frontier` (kernel local-upper-quantile ridge → one-sided envelope
cantilever), except Coast (parametric quantile regression, not a frontier). Each view returns a
mean vector + an (at most) 2×2 sampling covariance.

| View | Parameters (physical meaning) | Units | Fit method | σ source |
|---|---|---|---|---|
| **BrakingView** (`braking_view.py:176-262`) | `brake_decel_ms2` (a_b — mechanical braking-grip floor at v→0); `brake_aero_decel_per_m` (b_b — downforce-added braking grip, ≥0) | m/s²; 1/m | `fit_frontier` on de-conflated `y = -a_long - drag(CdA) - theta_R - g·sinθ` | 2×2 = bootstrap sampling cov (`ff.covariance`, `frontier_fit.py`) **+** `[[theta_R.sigma², 0],[0,0]]` (θ_R systematic, additive on intercept only) **+** `outer(J,J)·cda.sigma²` (CdA systematic, via `cda_frontier_jacobian`, `braking_view.py:125-173`) |
| **LateralView** (`lateral_view.py:94-181`) | `lateral_mech_grip_g` (mechanical lateral-grip coefficient, dimensionless g-units, ~3.2); `lateral_aero_grip_g` (aero grip slope, 1/(m/s)², ≥0) | g-units (dimensionless); (m/s)⁻² | `fit_frontier` on `mu_obs = |a_lat|/(g·cosθ)` (flat) or the exact banked-corner inverse (#497) | 2×2 = bootstrap sampling cov **only** — "no uncertain drag/rolling supporting term" (`lateral_view.py:118-119`); mass cancels, no CdA/θ_R coupling |
| **TractionView** (`traction_view.py:67-171`) | `traction_accel_ms2` (a_t — mechanical traction floor, driven-axle grip at v→0); `traction_aero_accel_per_m` (b_t — downforce-added traction, ≥0) | m/s²; 1/m | `fit_frontier` on the **ascent only** (v ≤ v_crossover) of de-conflated `y = a_long + drag(CdA) + theta_R + g·sinθ` | 2×2 = bootstrap sampling cov **+** `[[theta_R.sigma², 0],[0,0]]` **+** `outer(J,J)·cda.sigma²` (same Jacobian mechanism as braking, `drag_sign=+1`) |
| **PowerDragView** (`power_drag_view.py:100-252`) | `max_power_w` (P_max — engine power ceiling, W); `drag_area_closed_m2` (CdA, DRS-closed, m²); `drag_area_open_m2` (CdA, DRS-open, optional, quantile-only no cov) | W; m² | `fit_frontier` on the **descent only** (v ≥ v_crossover) of `y = a_long + theta_R + g·sinθ` (drag left IN); design `[1/(mv), -ρv²/2m]` | 2×2 = **either** a diagonal `[[p_max_prior.sigma², 0],[0, cda_var]]` when P_max is pinned (residual-based `cda_var`), **or** the conditioning-aware analytic design covariance `s²·(XᵀX)⁻¹` over the ridge when jointly solved (bootstrap explicitly rejected here as overconfident on degenerate/short spans, `power_drag_view.py:139-149`); degenerate fits (CdA<0.3 m²) get a hardcoded floor (`_CDA_UNKNOWN_SIGMA=0.4`, `_PMAX_UNKNOWN_FRAC=0.15`) |
| **CoastView** (`coast_view.py:75-139`) | `coast_rolling_decel_ms2` (θ_R — rolling/standing-drag decel, freely fit, no injectable prior slot); `coast_drag_area_m2` (CdA, cross-check only) | m/s²; m² | Pinball-loss (τ=0.20) quantile regression of the **lower envelope** `decel = θ_R + CdA·ρv²/2m` (not a kernel frontier — every coast sample IS on the physics curve, contaminated above by MGU-K regen) | 2×2 = bootstrap (resample+refit, `n_boot=40`) covariance of the two-parameter Nelder-Mead fit |

Shared **inputs** (not themselves per-view estimated parameters, but injected/threaded identically):
`mass_kg` = `quali_mass(year)` (one value/session, `session_estimator.py:125`); `rho` = one
per-session air density threaded to every view; `theta` (grade) from the #497 z-map (fallback
FLAT); `g=9.81` (`GRAVITY_MS2`, `constants.py`).

## (b) Duplication / correlation table — same physics, different names

| Physical quantity | Where it's measured | Coupled in code? | Cross-view correlation captured? |
|---|---|---|---|
| **Mechanical tyre-road grip ceiling** (car's fundamental friction limit) | `lateral_mech_grip_g` (LateralView, g-units, cornering); `brake_decel_ms2` (BrakingView, m/s², longitudinal-decel); `traction_accel_ms2` (TractionView, m/s², longitudinal-accel) | **No.** Three fully independent fits, different regimes (corner vs straight-brake vs straight-throttle), different units (g-units vs m/s², requiring `car_prior._assemble_lateral` as the "ONE sanctioned conversion seam" — `lateral_view.py:65-67`). No shared solve, no joint prior, no cross-term. | **Not captured — dropped.** No JSON blob or code path relates lateral grip to braking/traction grip. (Physically these needn't be identical — braking/traction grip is combined-slip/longitudinal-limited, cornering is lateral-limited — so the correlation, if any, is a friction-circle relationship, not identity; but the current code makes zero attempt to even test whether they co-vary car-to-car.) |
| **CdA (drag area)** | **Solved** independently twice: `drag_area_closed_m2` (PowerDragView, from throttle-on descent shape) and `coast_drag_area_m2` (CoastView, from coast lower envelope — explicit "cross-check", `coast_view.py:15-16`). **Injected as a point prior** (not solved) into BrakingView's `cda_closed` and TractionView's `cda` — both PINNED from PowerDragView's posterior each outer-loop round (`session_estimator.py:154,156,158`). | **Partially coupled** for Braking/Traction: `cda_frontier_jacobian` (`braking_view.py:125-173`, shared/imported by `traction_view.py:34`) propagates PowerDragView's CdA uncertainty into the pinned view's OWN 2×2 covariance via `outer(J,J)·σ_CdA²` — a real (if one-directional, point-estimate) coupling. **NOT coupled** for Coast: `coast_view.py` fits CdA independently with **no** shared prior, no Jacobian, pure cross-check by eyeballing agreement. | **Dropped for storage.** The propagated uncertainty is baked additively into braking_covariance/traction_covariance's own diagonal+off-diagonal terms (Jacobian outer product is 2×2, so it does inject a within-view a_b↔b_b or a_t↔b_t correlation term) — but the actual cross-view `cov(CdA, b_b)` or `cov(CdA, b_t)` is never itself persisted; only its downstream shadow inside the pinned view's blob. `power_drag_covariance` and `coast_covariance` are two entirely separate, uncorrelated blobs — the coast/power-drag CdA agreement is never quantified as a joint covariance, only visually cross-checked. **Recoverable in principle** — `cda_frontier_jacobian` is deterministic and re-derivable offline from stored (v,y) samples + bandwidth if someone wanted `cov(CdA, b_b)` explicitly; the coast-vs-power_drag correlation is NOT recoverable from stored data at all (independent samples, independent fits, no shared randomness to reconstruct a copula from). |
| **θ_R (rolling resistance)** | **Solved** once, by CoastView (`coast_rolling_decel_ms2`), freely estimated, no injectable prior slot (`coast_view.py:100-104` — a `prior_theta_R` param existed and was removed as dead). **Used** as a hardcoded COLD constant (`_THETA_R0=0.15, sigma=0.30`, `session_estimator.py:41,126`) in Braking/Traction/PowerDrag's de-conflation — the SAME literal value passed to all three every round, never updated from CoastView's own posterior. | **Explicitly NOT coupled by design** — `session_estimator.py:12-15` states Coast's θ_R "is powertrain-contaminated in the modern era, so it is NOT fed back into the de-conflations (it would corrupt them)". This is a deliberate, documented decision, not an oversight. | **Dropped, and irrecoverable as a real correlation** — since θ_R is never actually measured-and-injected (only a cold literal is used everywhere except Coast itself), there is no correlation to recover; Coast's θ_R measurement and the other three views' θ_R constant are causally disconnected by design. |
| **Underlying raw kinematic trajectory** (v, a_long, θ per sample) | BrakingView, TractionView, LateralView **share** the exact same per-driver smoothed/classified trajectory via `sample_cache` threaded through `session_estimator.estimate_session` (`session_estimator.py:119-124`) → `session_braking._driver_samples` (cached) → reused by `session_traction.py:79,90` and `session_lateral.py:44,54`. CoastView does **not** participate in this cache (`session_coast.py` has no `sample_cache` param) — it loads from out/in-laps (non-flying), a genuinely different sample set (`coast_view.py:18-19`). | **Coupled at the raw-observation level** (same trajectory fit, same per-sample σ_kin from the same Matérn/decoupled-longitudinal posterior) for Braking/Traction/Lateral. Coast is observationally independent. | This is the **opposite** direction of "dropped correlation" — it's a correlation the code creates but never propagates forward: because Braking/Traction/Lateral draw noise realizations from the same underlying smoothed trajectory, their per-session fit errors are NOT independent (shared trajectory-estimation error), yet each view's bootstrap covariance is computed as if its samples were an independent draw. No cross-view term accounts for this shared upstream uncertainty. |
| **Longitudinal a_long ITSELF** (the base observable feeding Braking vs Traction/PowerDrag/Coast) | BrakingView's `a_long` comes from `decoupled_longitudinal.py`'s 1D Kalman-RTS `[E_total, F_vehicle]` filter (WIRED via `decoupled_braking_input.py`, per `decision:decoupled_1d_longitudinal`). Traction/PowerDrag/Coast still use `clean_longitudinal_from_raw` (`braking_view.py:85-122`) — the #523/#546 HONEST-NULL means the decoupled filter was **measured and explicitly held back** from throttle/coast (`decoupled-1d-longitudinal.md:102-137`). | **Not coupled — actively split.** Braking and {Traction, PowerDrag, Coast} use two DIFFERENT longitudinal-acceleration estimators on the same underlying telemetry. | This is the starkest current basis fracture: the "same" physical quantity (`a_long`) is two different numbers depending on which view reads it, with two different noise models, and no attempt to reconcile/correlate them. |

## (c) What the covariance JSON blobs capture

Confirmed from `estimate_store.py:26-30,166-171` and `regime_readiness.py:243-268`: the five stored
blobs (`braking_covariance`, `traction_covariance`, `power_drag_covariance`, `lateral_covariance`,
`coast_covariance`) are **each a single view's own 2×2 covariance, WITHIN-view only** — e.g.
`braking_covariance` is `Cov(brake_decel_ms2, brake_aero_decel_per_m)`. There is **no** blob, column,
or code path anywhere in `estimate_store.py`/`race_stint_store.py` that stores a cross-view
covariance (e.g. `Cov(CdA, brake_decel_ms2)` or `Cov(lateral_mech_grip_g, traction_accel_ms2)`).
`regime_readiness._compute_param_pair_corr` (`regime_readiness.py:243-268`) only ever reads ONE
component's own 2×2 blob to get its within-component off-diagonal correlation (e.g. mech-grip vs
aero-grip collinearity, flagged `param_aliased` at |corr|≥0.9) — it is explicitly a
within-view-parameter-pair diagnostic, never cross-view.

`PowerDragResult.joint_prior()` (`power_drag_view.py:82-97`) is the one place that explicitly names
and preserves a 2×2 joint covariance as a first-class artifact "the marginal drops" — but that pair
is `(P_max, CdA)`, both PowerDragView's OWN parameters. It is a within-view joint (vs the marginal
`cda_prior_closed`), not a cross-view one, and it is not itself persisted to `estimate_store` as a
separate blob (only `power_drag_covariance` is stored, which already is this 2×2).

## (d) Existing seams already pointing toward a shared basis

- **`decision:decoupled_1d_longitudinal`** (`docs/architecture/decisions/decoupled-1d-longitudinal.md`)
  is the closest thing to a "unified longitudinal state" attempt: state `[E_total, F_vehicle]` in
  gravity-free vehicle-force coordinates, designed as ONE estimator that all longitudinal views
  (braking, traction, power/drag, coast) could in principle read `a_long` from. It is WIRED for
  braking only (#518 G3); the #523/#546 characterization runs (same file, lines 102-206) are
  explicit **measured attempts to extend the shared basis to throttle/coast and an HONEST-NULL
  verdict** — root cause is structural (Kalman-RTS LOOSE coupling at throttle-on diverges from
  per-sample FD in a circuit-topology-dependent way; coast has structural 21-26% sample loss on
  short segments). This is the strongest evidence in the repo that someone already tried to build
  the shared-basis stage-1 the brief hints at, and it partially failed — the failure mode (why a
  single kinematic-state estimator doesn't trivially serve all five views) is directly relevant
  design input.
- **`session_estimator.py`'s outer loop** (Plan 7, `session_estimator.py:1-19`) is explicitly framed
  as "the general framework for cyclic coupling once a view feeds back" — currently a one-round DAG
  (PowerDrag → {Braking, Traction}; Lateral and Coast standalone) but architected to generalize.
- **`cda_frontier_jacobian`** (shared by `braking_view.py` and `traction_view.py`) is a working,
  reusable pattern for propagating one view's parameter uncertainty into another's covariance via a
  numerical Jacobian — the mechanical building block a real joint-basis solve would need, already
  proven at 2-view scale.
- **The `sample_cache` sharing** (`session_estimator.py:119`, threaded into braking/traction/lateral)
  already unifies the RAW kinematic observation layer for 3 of 5 views — the gap is that this shared
  upstream uncertainty is never propagated into the per-view fit covariances (see table (b), row 4).
- **#496/#498 refinement-into-views path** (`accel_obs.py`, `trajectory_refine.py`,
  `scripts/pool_physics_estimates.py`): the two-cycle external-anchor design explicitly treats the
  RAW `a_long` sensor value (never a smoothed re-derivation) as the one non-negotiable shared
  physical anchor across cycles — an "anchor-source invariant" that is philosophically the same
  discipline a shared-basis parameterization would need (one raw truth, multiple derived views), but
  currently implemented only as a trajectory-level refinement loop, not a parameter-level joint basis.

## Scoped nulls (explicit)

- "CdA cross-view correlation is dropped in code" ≠ "not recoverable" — for the Braking/Traction
  pin path it IS reconstructable post-hoc via `cda_frontier_jacobian` (deterministic, given stored
  (v,y) samples + bandwidth); for the Coast-vs-PowerDrag CdA agreement it is NOT recoverable (fully
  independent samples/fits, no shared latent variable to reconstruct).
- "θ_R correlation is dropped" is not really a dropped correlation at all — by design, no correlation
  was ever created (CoastView's θ_R measurement is deliberately walled off as
  powertrain-contaminated); recovering it would require a NEW model, not an archive dig.
- "Mechanical grip (lateral/braking/traction) correlation is dropped" — genuinely unknown whether
  recoverable, since no joint data structure was ever built; would need a new cross-view fit over
  the existing per-view point estimates + within-view covariances (data exists in `estimate_store`
  rows to attempt this retroactively — e.g. per-session-pair Pearson correlation of the three
  point estimates across the season — but no code currently does this).
