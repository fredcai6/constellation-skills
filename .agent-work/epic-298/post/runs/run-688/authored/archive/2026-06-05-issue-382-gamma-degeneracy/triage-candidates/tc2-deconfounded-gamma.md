# Triage Recommendation: De-confounded γ identification — the gated reopen condition for Piece 3

## Classification
research hardening | unresolved decision

## Source checklist/artifact
- `.agent-work/issue-382-gamma-degeneracy/evidence/gamma_identifiability.json` (G2 measured verdict)
- §7.7 of `docs/evo/prediction_ceiling_and_priorities.md`

## Structural anchor
`path:src/compound_prior/` ; `none` (research)

## Problem
The race-side γ-up degradation ladder is **not identifiable** from race-lap data with the current design — and #382 measured the limit is **confounding, not poor identifiability** (VIF only 2.5, γ statistically well-resolved, but every resolved adjacent pair points DOWN = wrong sign). A better fit of the same data cannot recover it. Piece 3 (structured vector latent, #336) is gated on whether the β-down/γ-up trade identifies; it is now effectively closed on physics grounds **unless a de-confounding lever appears**.

## Current truth
- γ recovered from pooled race laps is monotone-DOWN in softness (C1 4.2e-4 → C6 1.3e-4), opposite the physics expectation. Confounded with the absorbed fuel/track-evolution + stint-phase structure (§7.1).
- §7.7 sets the reopen condition: a design that breaks the confound.

## Desired/future concern
If Piece 3 is ever to be revisited, it requires a γ identification that *de-confounds*, e.g.: per-compound φ (not one global slope), explicit non-linear fuel/track-evolution nuisance terms (vs an absorbed linear lump), stint-phase / traffic controls, or an exogenous degradation measurement (telemetry-derived deg, tyre-temp). Only such a lever — not more pooling or a fancier estimator — can move the gate.

## Evidence
- max VIF 2.5 (moderate), 4/5 pairs separable >2 SE, C6 profile CI [8.4e-5,1.7e-4] excludes zero → well-resolved.
- 0 of 4 resolved adjacent pairs go UP → wrong sign → confounding, not noise.
- Gate findings (`compound_crossover_gate_findings.md`): per-race φ and single-season both degrade γ.

## Impact
This is the load-bearing gate for the #336 structured-latent dream. Without de-confounding, building a latent that *assumes* the conserved γ trade is unjustified by the one problem with ground-truth physics.

## Suggested scope
- A research spike: re-fit γ with at least one de-confounding design (per-compound φ + non-linear evolution, or stint-phase controls), measure whether the γ-up ladder emerges with the confound removed.
- If it does → reopen Piece 3 with evidence; if not → close Piece 3 definitively.

## Non-goals
- Building Piece 3 / the vector latent itself.
- Any β / Piece 1 work (β is identified via pooling, see tc1).

## Acceptance criteria
- [ ] At least one de-confounded γ fit with a measured verdict (γ-up recovered or still confounded), with the confound-removal made explicit.
- [ ] An updated §7.7 / §7.4 gate line: Piece 3 reopen or definitive close.

## Recommended priority
low

**Reason:** Exploratory, off the critical path; Piece 3 is already gated off and #382 strengthened the case for keeping it off. Only worth doing if someone wants to definitively close (or surprise-reopen) the #336 direction.

## Related artifacts
- `docs/evo/prediction_ceiling_and_priorities.md` §7.1/§7.4/§7.7, `compound_crossover_gate_findings.md`
- #336 (structured-latent dream), #382 (this work)

## Issue creation authority
issue-ready only (Admiral approves filing)
