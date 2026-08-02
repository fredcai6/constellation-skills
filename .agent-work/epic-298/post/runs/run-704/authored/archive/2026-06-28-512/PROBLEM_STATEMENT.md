# #512 — Regime-capability vector readiness (C3) — Problem Statement

## The ask
Characterize the per-car **regime-capability vector** — the fitted physics parameters
describing a car's cornering / straight-line capability — **as a prediction input**, and
land a **GO / CONTEXTUAL / NO-GO** readiness verdict per component to the spec §4 done-done
bar. Measured, **not wired** (no feature plumbing into evo this issue).

## Components (from the 2023-Q five-view estimate store, `physics_estimates_g3wired.db`)
| Component | Store column(s) |
|---|---|
| Slow-corner grip (μ·g, mechanical) | `lateral_mech_grip_g` |
| Fast-corner grip (k_df, aero) | `lateral_aero_grip_g` |
| Straight-line (deployed power − drag) | `max_power_w`, `power_drag_area_m2` (+ `drag_area_closed_m2`) |
| Braking | `brake_decel_ms2`, `brake_aero_decel_per_m` |
| Traction (corner-exit) | `traction_accel_ms2`, `traction_aero_accel_per_m` |

(Coast is honestly-diagnostic only; carried as a minor 6th readout, not a headline component.)

## The 4 readiness tests per component
1. **Separability** — (a) *car-vs-car*: between-car variance vs within-car noise (two-way
   team×circuit decomposition, `frac_team`) — are cars actually distinguishable on this axis?
   (b) *param-vs-param*: σ inflation from collinearity with a sibling param (joint covariance
   blob correlations — mech↔aero grip, power↔drag).
2. **Per-car×regime coverage** — per constructor, how many of 22 rounds yield a valid
   (ok, finite, SNR-passed) estimate; where coverage is thin (regimes a circuit doesn't
   exercise, e.g. Monaco ⇒ no high-speed for fast-corner / power-drag).
3. **Cross-session stability** — does the component reproduce across a car's sessions
   (random-effects τ² between-session vs within-σ); a car axis should be stable modulo real
   development, a setup axis (CdA) should not.
4. **Covariance honesty** — are reported σ calibrated? Cross-session reproducibility:
   do residuals about the pooled (drift-aware) mean fall within stated σ (z / χ²)? Over-claim
   = σ too small.

## Going-in priors
- **Traction → CONTEXTUAL, pre-derived** (#557: not cross-session-stable as one stationary
  frontier; recoverable corner-indexed). **Set-aside protocol**: characterize + verdict here,
  do NOT rebuild; #557 is the upgrade path.
- **CdA / drag is a setup axis (drifts)** → expect weak cross-session stability.
- **"constructors not separable, frac_team ≤ 3%"** (prior #492 finding) — headline risk that
  the whole vector is weakly car-separating; #512 is exactly the test of it. A broad NO-GO/
  CONTEXTUAL here is a legitimate, valuable terminal result (bounds the bet).

## Scope boundary with #511 (race-state)
#512 = the **static** vector (steady-state fit). Grip-evolution STATE (tyre decay `k_tire`,
track multiplier `g_track`) is **#511's job** → explicitly **out of scope / deferred**.

## Method
Mostly **run existing machinery**: the populated 2023-Q `estimate_store` + `pool_driver`
(random-effects τ + two-way team×circuit decomposition) + the covariance blobs. New code is
the **readiness readout layer** (coverage / param-pair separability / covariance-honesty
calibration / the GO-CONTEXTUAL-NO-GO rubric) + a **traceable dashboard** + tests — composing
`pool_driver`/`pooling`/`fit_evidence`, not reimplementing estimation.

## Done-done (spec §4)
Full test coverage · honest covariance (first-class) · single canonical execution path ·
traceable data→dashboard · GO/CONTEXTUAL/NO-GO verdict per component.
