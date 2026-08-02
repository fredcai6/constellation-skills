# Triage Recommendation: Bisect the iterative production fit's secondary per-season β distortions

## Classification
research hardening | cleanup

## Source checklist/artifact
- G1 implementer-result + review (g1) out-of-scope note
- `.agent-work/issue-382-gamma-degeneracy/evidence/beta_degeneracy.json`

## Structural anchor
`path:src/compound_prior/solver/` ; `path:src/compound_prior/baseline.py`

## Problem
#382 established the PRIMARY β degeneracy cause (per-season vs pooled identification). But the production fit is an iterative baseline+compound solve (`fit_tire_wear_model`) carrying several additional constraints not in the clean pooled-FE comparison: baseline residualization, a `--beta-upper-bound` default of −1e-6 (β constrained ≤ −1e-6), `race_delta_gamma_mode=additive`, `sparse_prior_strength=1.0`, and the monotone-γ isotonic projection. Their *secondary* contribution to the per-season jaggedness was timeboxed out (off critical path).

## Current truth
- Gold per-season β is jagged/wrong-signed; the dominant lever is pooling (measured). The iterative-fit components add further per-season distortion of unquantified size.
- The β-upper-bound (≤ −1e-6) in particular forces every compound β negative, which interacts oddly with the weighted-mean-zero centering — worth a closer look.

## Desired/future concern
A component-by-component attribution of the iterative production fit's per-season β distortion (toggle each: β-upper-bound, race-delta-gamma, sparse-prior, baseline residualization) — only if a pooled fit (tc1) is pursued and the residual per-fit distortion matters.

## Evidence
- `fit_tire_wear_model` / `scripts/fit_tire_wear_model.py` arg defaults (β-upper-bound −1e-6, sparse-prior 1.0, additive race-delta).
- G1 ridge sweep + per-season analysis isolate pooling as primary but do not attribute the iterative-fit residual.

## Impact
Lower-value than tc1/tc2; mostly relevant if the team wants a fully-understood production fit before changing the β anchor. Could surface a real secondary bug (e.g. the β-upper-bound sign interaction).

## Suggested scope
- Ablate the iterative production fit components on one season; quantify each's β-spread/sign effect beyond pooling.

## Non-goals
- Changing production defaults (that needs gold-cycle Brier evidence — separate).
- γ work (tc2).

## Acceptance criteria
- [ ] A per-component attribution table for the iterative fit's per-season β distortion.

## Recommended priority
low

**Reason:** Diagnostic completeness; the actionable fix (pooling, tc1) and the gate decision (tc2) don't depend on it.

## Related artifacts
- `src/compound_prior/solver/`, `scripts/fit_tire_wear_model.py`
- #382 (this work)

## Issue creation authority
issue-ready only (Admiral approves filing)
