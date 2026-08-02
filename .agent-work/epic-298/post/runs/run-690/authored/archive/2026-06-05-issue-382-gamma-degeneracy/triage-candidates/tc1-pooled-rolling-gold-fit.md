# Triage Recommendation: Adopt a pooled/rolling multi-season gold compound_prior fit (the β fix)

## Classification
feature | unresolved decision

## Source checklist/artifact
- `.agent-work/issue-382-gamma-degeneracy/evidence/beta_degeneracy.json` (G1 measured root-cause)
- review finding (G1 r5), §7.7 of `docs/evo/prediction_ceiling_and_priorities.md`

## Structural anchor
`path:src/compound_prior/` (fit path); `path:scripts/build_rolling_compound_priors.py`

## Problem
The gold per-season `compound_prior` fits cannot identify the fresh-pace β ladder: #382 measured 8/8 seasons non-monotone even at ridge=0 on a clean fixed-effects design; the ordered ~0.7%/step β ladder only emerges when all eight seasons are pooled. So the gold β anchor used for `qs_*` normalization is under-pooled, not mis-solved.

## Current truth
- Gold artifacts (`params/gold/compound_prior/{2022..2025}`) are per-season (one fit/year), selected time-safely (prior-season) by `runtime_normalization.py`.
- `scripts/build_rolling_compound_priors.py` already pools historical + target-year-to-date observations with sigmoid downweighting — i.e. the pooling mechanism largely exists but is not what gold currently ships for the β anchor.
- Sibling #380 is injecting the gate-recovered (pooled) β at the existing normalizer interface.

## Desired/future concern
Decide whether to make the gold/runtime compound β come from a pooled/rolling multi-season fit (so β is identified) instead of (or in addition to) the per-season fit, while preserving time-safety. Co-validate with #380 since they share the β artifact.

## Evidence
- 8/8 seasons non-monotone at ridge=0; pooled spread 0.00726 monotone (beta_degeneracy.json).
- Ridge refuted (0.2% effect) — the fix is pooling, not the solver.
- architecture packet `compound_prior.md` Known-Limits already flags "regen from unified solver path planned."

## Impact
β is the Piece-1 quali normalization correctness fix (≤13% of feature pairs per §7.5). Getting an *identified* β requires pooling; otherwise #380 injects a hand-fit β rather than a reproducible gold artifact.

## Suggested scope
- Prototype a pooled (or rolling) multi-season gold compound β fit; confirm the β ladder is identified and time-safe; compare to the gate's pooled ladder.
- Decide the artifact/selection change with #380; keep the emitted schema unchanged (no normalizer change).

## Non-goals
- Any γ-ladder / Piece-3 work (γ is confounded — separate, see tc2).
- Changing the `CompoundNormalizer` interface or artifact schema.

## Acceptance criteria
- [ ] A pooled/rolling gold β fit that produces a monotone, time-safe β ladder, with numbers vs the per-season gold and the gate pooled fit.
- [ ] An explicit decision (with #380) on whether to adopt it for the runtime β anchor.
- [ ] Brier/region evidence if it changes promoted prediction behavior.

## Recommended priority
medium

**Reason:** It is the actionable "fix" half of #382's β finding and directly supports #380's Piece-1 correctness fix, but it is off the dominant quali lever (§7.6 says the big gap is same-compound model-side) so not urgent.

## Related artifacts
- `docs/evo/prediction_ceiling_and_priorities.md` §7.5/§7.7
- `scripts/build_rolling_compound_priors.py`, `src/compound_prior/runtime_normalization.py`
- #380 (qs_* β injection)

## Issue creation authority
issue-ready only (Admiral approves filing; touches the #380 seam decision)
