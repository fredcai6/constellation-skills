# Reviewer Handoff — G3 Re-run + Verdict review (#522)

## Gate
g3-review (verify the C1 re-run + verdict are honestly grounded; verify the doc edits match the result)

## What Was Implemented
The C1 driver-utilization dashboard was re-run on the RBR 2023-Q subset (Monaco/Italy/GB/Singapore, VER) with the G2 lateral-units-corrected ceiling (committed 33c56214). The corner regimes un-pinned from the 2.0 clip. Verdict authored as overall CONTEXTUAL. Docs updated. Artifacts: `.agent-work/522-phase-align-utilization/VERDICT.md`, `crew-handoffs/g3-implement-result.md`; doc edits to `docs/architecture/packets/physics.md` and `docs/architecture/decisions/ideal-lap-sim-two-sided-evaluator.md`.

## How to Inspect
- `VERDICT.md` + `g3-implement-result.md` for the numbers/verdict.
- `git --no-pager diff -- docs/` for the doc edits.
- Re-run the dashboard to confirm the numbers: `py scripts/driver_utilization_dashboard.py --db data/physics_estimates.db --cases "Monaco:VER,Italy:VER,Great Britain:VER,Singapore:VER"` (adjust GP names to the store if needed).

## Close Criteria (each a review check)
1. **Numbers reproduce:** the per-regime U + σ in VERDICT.md match a fresh dashboard run (spot-check at least Monaco + one other case). The reported un-pinning (braking 0.89–1.02, fast_corner 0.92–0.97, slow_corner 0.89–0.96, straight 0.90–1.01) is real, not asserted.
2. **Verdict honestly grounded:** the per-regime GO/CONTEXTUAL/NO-GO calls follow from the numbers + covariance (not inflated). "CONTEXTUAL" for the corner regimes (U≈1, circuit-differentiated, σ small) is defensible; confirm no regime is over-claimed as GO without support, and that the straight under-call (Italy/Singapore slight) is honestly recorded as a persisting finding (lateral fix doesn't touch power-drag).
3. **Root-cause statement correct:** VERDICT explicitly states #518's "phase misalignment binding constraint" was superseded by the lateral units bug — consistent with the G1 diagnosis (true-distance registration changes U <1%).
4. **Doc edits accurate:** the packet characterization-finding + the decision-anchor characterization-finding/review-trigger now describe the units fix + the new CONTEXTUAL verdict, and do NOT leave stale "NO-GO / phase misalignment / clipped at 2.0" claims as current truth. Factual, minimal.
5. **Tests green:** `py -m pytest tests/unit/physics/test_regime_utilization.py tests/unit/physics/test_driver_utilization_dashboard.py -q` passes; confirm no old clipped expectation was left wrong (the implementer reports none existed).

## Allowed Scope (of the change under review)
`.agent-work/.../VERDICT.md`, `docs/architecture/packets/physics.md`, `docs/architecture/decisions/ideal-lap-sim-two-sided-evaluator.md`, and any test edits. `car_prior.py`/consumer must be UNCHANGED by g3 (G2 is committed; verify g3 added no src change).

## Constraints
`py` launcher; store/cache read-only via absolute main-checkout paths; verdict grounded in actual numbers.

## Map Anchors (inbound)
`scripts/driver_utilization_dashboard.py`, `struct:physics.utilization`, `decision:ideal_lap_sim_two_sided_evaluator` (review-trigger fires on this fix), `decision:c1_driver_utilization_design`.

## Evidence Produced
Dashboard 4/4 OK (264s); per-regime un-pinning table; VERDICT.md; doc diffs; 35/35 physics utilization tests pass.

## Suggested Model Tier
Sonnet — verification of reproducible numbers + verdict grounding + doc accuracy; bounded.

## Stop Conditions
BLOCK if: the numbers don't reproduce; a verdict is over-claimed vs the numbers/σ; the doc edits leave stale NO-GO/phase-misalignment claims as current truth; or g3 changed production code.

## Return Format
REVIEW_RESULT to exactly `.agent-work/522-phase-align-utilization/crew-handoffs/g3-review-result.md`: verdict (APPROVE/BLOCK), per-check findings (incl. the reproduced numbers), blockers, out-of-scope observations, workflow feedback.
