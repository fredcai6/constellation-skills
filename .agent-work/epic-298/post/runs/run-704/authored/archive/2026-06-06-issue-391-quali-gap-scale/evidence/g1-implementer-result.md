# IMPLEMENTER_RESULT — g1 (Gap-scale module)

## Completed slice
Created the pure module `src/evo_predictor/quali_gap_scale.py` and its unit test
`tests/unit/evo_predictor/test_quali_gap_scale.py`. Implements the quali mean-head gap
MAGNITUDE expression via the per-event exchange rate, plus three prediction-time scale
providers.

## Files changed
- `src/evo_predictor/quali_gap_scale.py` (NEW)
- `tests/unit/evo_predictor/test_quali_gap_scale.py` (NEW)

## Public API delivered (matches plan + Admiral correction)
- `expected_gap_ij(pi_i, pi_j, s) -> float` = `s*(pi_i - pi_j)` — the phase-agnostic #386 contract function.
- `expected_gaps(pi, s, *, reference='median') -> Dict[str,float]` — field-level gap-to-reference (median/mean/numeric reference).
- `carry_forward_scale(history) -> Optional[float]` — CF1: last-known prior-event quali s_e; None on empty/all-non-finite.
- `same_circuit_prior_year_scale(prior_year_record) -> Optional[float]` — CF2 (Admiral): same-circuit prior-year s_e; None when absent/non-finite.
- `global_constant_scale(records, *, aggregate='median') -> float` — the status-quo-ante baseline both CF variants must beat.
- The vacuous "persistence" provider was DROPPED (it was identical to CF1 — Admiral).

## Test mode satisfied
Test-after (pure functions). 36 tests: formula/sign/antisymmetry, positive-s order-sign
preservation, scale-changes-magnitude-not-order (monotone invariance), reference handling
(median/mean/numeric), single-driver-is-own-reference, pairwise-diff recovered from field
gaps, input validation (empty field, non-finite scale/power, unknown reference/aggregate),
CF1 last-known + record extraction + trailing-non-finite skip + None on empty/all-non-finite,
CF2 value/record/None/non-finite, global-constant median/mean + record skip + empty/all-non-finite rejection.

## Evidence produced
- `py -m pytest tests/unit/evo_predictor/test_quali_gap_scale.py -q` -> 36 passed in 0.12s
- `py -m pyright src/evo_predictor/quali_gap_scale.py tests/unit/evo_predictor/test_quali_gap_scale.py` -> 0 errors, 0 warnings
- `py -m src.utils.simplification_limits --paths src/evo_predictor/quali_gap_scale.py tests/unit/evo_predictor/test_quali_gap_scale.py` -> PASS (2 files checked)

## Assumptions used
- Providers accept `SpreadTargetRecord | float` via duck-typed `.s_e` (no import-time dep on spread_target; TYPE_CHECKING-only import).
- `_optional_scale_value` returns None for absent/non-finite (the "no usable scale, fall back to baseline" signal); core gap functions raise on non-finite (strict public inputs per project rule).
- Same-circuit prior-year resolution (circuit->round) is the harness's job (kept this module DB-free); the provider takes an already-looked-up record/value.

## Stop conditions hit
None.

## Out-of-scope observations
None. No existing file touched; `-pi` ordering output untouched (default-preserving).
