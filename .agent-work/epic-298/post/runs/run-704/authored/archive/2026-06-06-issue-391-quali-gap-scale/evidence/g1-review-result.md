# REVIEW_RESULT — g1 (Gap-scale module)

## Verdict
APPROVE

## Scope inspected
- `src/evo_predictor/quali_gap_scale.py` (NEW, in the worktree on branch constellation/issue-391-quali-gap-scale)
- `tests/unit/evo_predictor/test_quali_gap_scale.py` (NEW)
- Re-ran all verification from the WORKTREE root (see process note below).

## Close-criteria findings
1. Formula correctness: `expected_gap_ij` = `float(s)*(float(pi_i)-float(pi_j))` = s*(pi_i-pi_j). PASS.
2. Positive-s order invariance: algebraic + tests `test_positive_scale_preserves_order_sign`, `test_scale_changes_magnitude_not_order`. sign(gap)==sign(pi_i-pi_j) for s>0. PASS.
3. Reference handling: median/mean/numeric; reference cancels in pairwise diff (`test_pairwise_difference_recovered_from_field_gaps`). PASS.
4. Input validation with named messages: every public fn names field/expectation/actual. PASS.
5. Default-preserving: only the two NEW files; no existing `-pi` consumer touched; main repo working tree clean. PASS.
6. CF1 (`carry_forward_scale`), CF2 (`same_circuit_prior_year_scale`), baseline (`global_constant_scale`) all present; vacuous "persistence" dropped per Admiral. PASS.
7. Tests meaningful and green: 36 behavioral tests. PASS.
8. pyright + simplification_limits clean. PASS.

## Evidence (re-run from worktree)
- `py -m pytest tests/unit/evo_predictor/test_quali_gap_scale.py -q` -> 36 passed in 0.13s
- `py -m pyright src/evo_predictor/quali_gap_scale.py tests/unit/evo_predictor/test_quali_gap_scale.py` -> 0 errors, 0 warnings
- `py -m src.utils.simplification_limits --paths ...` -> PASS (2 files checked)

## Process note (corrected, non-blocking)
The implementer initially created the two files in the MAIN repo working tree (cwd slip:
`cd C:\Programs\f1Brainz` instead of the worktree). Detected at review (git showed no diff in
the worktree). Files moved into the worktree on the correct branch; main repo working tree
restored to clean; all verification re-run from the worktree and green. Content was correct;
this was a workspace-location slip, now fixed. All subsequent commands must run from the
worktree root.

## Observations (non-blocking)
- `same_circuit_prior_year_scale` / `carry_forward_scale` are thin wrappers over
  `_optional_scale_value`; the distinct named functions are intentional (they ARE the
  two-variant contract g2/g3 reference and carry the as-of semantics in their names). Fine.

## Out-of-scope finds
None.
