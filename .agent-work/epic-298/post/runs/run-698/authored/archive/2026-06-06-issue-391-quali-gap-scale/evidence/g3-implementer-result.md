# IMPLEMENTER_RESULT — g3 (Doc note + #386 contract recording)

## Completed slice
Appended §9.6 "Quali mean gap scale — expression + OOS measurement (#391)" to
`docs/evo/prediction_ceiling_and_priorities.md` (after §9.5, append-shaped) and added the
`quali_gap_scale.py` module entry to `docs/architecture/packets/evo_predictor.md` (after the
spread_target.py entry). All numbers cite the g2 evidence JSON exactly.

## Files changed
- `docs/evo/prediction_ceiling_and_priorities.md` (append §9.6)
- `docs/architecture/packets/evo_predictor.md` (add module entry)

## §9.6 contents
1. **Monotone-invariance finding**: `expected_gap_ij = s·(π_i−π_j)`; positive `s` is monotone in
   π-differences so it cannot move ordering KPIs (algebraic) — hence "meaningful" reconciled to
   gap-MAGNITUDE error (Admiral Q1), not ordering (ordering = #375).
2. **Mechanism**: pure `src/evo_predictor/quali_gap_scale.py` (`expected_gap_ij` + `expected_gaps`);
   additive, opt-in, default-preserving; `spread_target.py` untouched. Learned feature→s_e head
   deferred (#375-shaped, triage candidate).
3. **Two CF variants + shipped default**: CF1 (last-prior-event) and CF2 (same-circuit prior-year)
   vs the global-constant baseline; vacuous persistence dropped. Default = measured winner.
4. **Measured numbers (OOS 2025 midfield gap-MAE, table)**: event 0.001949, cf1 0.003258, cf2
   0.003825, global_const 0.003255, with calibration slope/r². HONEST NULL — neither CF beats the
   baseline; shipped default ŝ_e = global_const. ~40% ceiling headroom noted.
5. **Flat-ordering confirmation**: sign-accuracy identical 0.938776 across all scales, spread 0.0.
6. **#386 contract**: phase-agnostic `expected_gap_ij` in `quali_gap_scale.py`, evaluated with the
   LABEL `s_e` (committed `params/spread_target/<y>/<r>/<phase>.json`) as the reference gap;
   quali-vs-race ownership note (this module owns the quali expression + ŝ_e providers; race-phase
   s_e consumption belongs to Thrust B #386/#388/#389).

## Architecture packet entry
One paragraph for `quali_gap_scale.py`: role, the #386 contract function, the three ŝ_e providers,
purity (no DB/FastF1/torch; spread_target untouched), the honest-null OOS result + shipped default,
flat-ordering, deferred head, and a §9.6 cross-reference.

## Verification
- Doc numbers cross-checked against the JSON: event/cf1/cf2/global_const all present and exact;
  sign-acc 0.938776 present; "honest null" present.
- `py -m pytest tests/unit/evo_predictor/test_quali_gap_scale.py tests/unit/evo_predictor/test_quali_gap_scale_harness.py -q` -> 54 passed.
- Only the two intended doc files changed (git status); edits append/additive, no prior §9 text rewritten.

## Stop conditions hit
None.

## Out-of-scope observations
None beyond the already-flagged deferred feature→s_e head triage candidate (tc1).
