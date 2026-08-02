# Plan-alternatives (design-it-twice) — #627 load-bearing interfaces

The LAUNCH_ORDER froze the tier/gate structure (Tier 1 MUST, Tier 2 close-or-defer, Tier 3 defer), so
whole-gate-plan alternatives are constrained. The genuine design choices are the TWO new load-bearing
interfaces. Bias-to-yes: two candidates each, converging to one recommendation. Untaken roads named.

## Interface A — cross-view covariance representation

- **A1 (constraint: minimal blast radius) — targeted sparse cross-terms.** Persist only the cross-view terms
  that are real and recoverable: `cov(CdA,{a_b,b_b})`, `cov(CdA,{a_t,b_t})` (deterministic via the existing
  `cda_frontier_jacobian`), plus the fused-CdA (PowerDrag⊕Coast) slot. One JSON blob column
  `cross_view_covariance`. Locality: one column, one populate site in `record_from_estimate`.
- **A2 (constraint: maximal generality) — dense full-basis covariance matrix.** Assemble one N×N covariance
  over the whole parameter vector [CdA,P_max,a_b,b_b,a_t,b_t,A0,A2,...] with all cross-terms, most of which are
  structurally zero or unrecoverable (Coast↔PowerDrag CdA has NO shared latent to reconstruct — x7 scoped null;
  grip-triplet cross-terms were never built). Deep interface, but most entries are fabricated zeros or unknowns.

- **CONVERGENCE → A1.** The recoverable cross-view structure is exactly the Jacobian-coupled CdA↔{braking,
  traction} terms + the fusible dual-CdA; everything else in a dense matrix is a structural zero or an
  unrecoverable term (x7 map scoped nulls). A dense matrix would emit fabricated-zero cross-terms as if
  measured — the exact confident-zero-vs-unknown confusion the explicit-unknown contract exists to prevent.
  A1 persists what is real; the explicit-unknown status carries the rest as `unresolved`. The grip-triplet
  cross-term (a genuine open question) is QUANTIFIED in G5, not fabricated into the matrix.
- **Untaken road:** a dense full-basis matrix — deferred; revisit only if a future joint solve actually
  produces non-zero grip-triplet cross-terms (G5 measures whether they co-vary at all first).

## Interface B — pooled-σ_μ shared-systematic floor

- **B1 (constraint: simplest honest mechanism) — additive quadrature floor after shrinkage.** After
  `pool_random_effects` computes `sigma_mu`, floor it: `sigma_mu = sqrt(sigma_mu² + shared_floor²)` where
  `shared_floor` is the per-param SHARED systematic (mass-model bias + θ_R literal — common-mode across a
  year's sessions). Minimal change to `pool_random_effects` (one optional arg) + `pool_store` threads it.
- **B2 (constraint: most principled model) — two-level variance component.** Model the shared systematic as a
  third variance component (σ_shared²) inside the random-effects likelihood alongside τ² and σ_i², re-deriving
  the DerSimonian–Laird estimator. Principled but re-opens a validated estimator (`pooling.py` is consumed by
  Phase-2), risks regressing `test_pooling`, and the shared bias is common-mode (rank-1) — it does NOT enter
  the within-session weighting, only the final σ_μ, so the likelihood re-derivation reduces to exactly B1's
  additive floor in the common-mode limit.

- **CONVERGENCE → B1.** B2 collapses to B1 for a common-mode (fully-correlated) shared bias, which is precisely
  the #506 case (every session uses the same `quali_mass(year)` and the same θ_R literal → correlation 1). B1
  is the honest minimal mechanism and keeps the validated pooling estimator's weighting untouched (backward
  compat, pre-ruling #4). Honest-wide (pre-ruling #3): the floor only ever WIDENS σ_μ.
- **Untaken road:** the full three-component likelihood — deferred; only needed if a shared bias were
  PARTIALLY correlated (not common-mode), which the #506 nuisances are not.

## Panel-vs-single (surfaced choice)
Single cold critic (not a 3-lens panel): this run touches an established component (`struct:physics.layer2`)
with a frozen launch-order scope, not new architecture — one cold critic is proportional. Recorded as the
surfaced choice.
