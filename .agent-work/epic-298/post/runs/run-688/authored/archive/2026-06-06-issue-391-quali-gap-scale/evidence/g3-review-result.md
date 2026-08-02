# REVIEW_RESULT — g3 (Doc note + #386 contract recording)

## Verdict
APPROVE

## Scope inspected
`git diff` of `docs/evo/prediction_ceiling_and_priorities.md` (§9.6) and
`docs/architecture/packets/evo_predictor.md` (quali_gap_scale.py entry). Numbers cross-checked
against `.agent-work/.../evidence/quali_gap_scale_numbers.json`.

## Close-criteria findings
1. Monotone-invariance argument stated correctly: `expected_gap = s·(π_i−π_j)`, positive `s`
   monotone -> sign preserved -> cannot move ordering KPIs; "algebraic, not empirical". PASS.
2. Numbers match the g2 JSON exactly: table event 0.001949, cf1 0.003258, cf2 0.003825,
   global_const 0.003255; calibration slopes (0.999/0.623/0.497/0.761); flat sign-acc 0.938776,
   spread 0.0. Programmatic cross-check passed. PASS.
3. Shipped default = measured winner with rationale: "shipped default ŝ_e source is therefore
   the global constant (it wins by measurement)"; honest-null rationale (CF1 essentially tied,
   CF2 worse). PASS.
4. #386 contract accurate: phase-agnostic `expected_gap_ij` in `quali_gap_scale.py`, evaluated
   with the LABEL `s_e` (committed `params/spread_target/<y>/<r>/<phase>.json`) as the reference
   gap; "same function, two s sources." Matches the shipped module. PASS.
5. Quali-vs-race ownership note present and correct (this module owns the quali expression +
   ŝ_e providers; functions phase-agnostic/reusable; race-phase s_e consumption -> #386/#388/#389).
   PASS.
6. Append-shaped, no contradiction: §9.6 after §9.5 (cites §9.5's CV≈0.80, does not rewrite it);
   packet entry after spread_target's, does not alter it. PASS.
7. Architecture packet entry accurate: role, contract function, three providers, purity,
   honest-null result, flat-ordering, deferred head, §9.6 cross-ref — all match. PASS.

## Verification
- `py -m pytest tests/unit/evo_predictor/test_quali_gap_scale.py tests/unit/evo_predictor/test_quali_gap_scale_harness.py -q` -> 54 passed.
- Only the two intended doc files changed (git status).

## Out-of-scope finds
None beyond the already-flagged deferred feature->s_e head (tc1).
