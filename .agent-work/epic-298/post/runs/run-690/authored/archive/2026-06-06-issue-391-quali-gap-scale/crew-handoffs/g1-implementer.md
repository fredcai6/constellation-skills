# Implementer Handoff

## Gate
g1 — Gap-scale module

## Task
Create the pure module `src/evo_predictor/quali_gap_scale.py` expressing the quali mean head's gap MAGNITUDE via the per-event exchange rate, plus prediction-time scale providers. Write its unit test.

## Protected Intent
The existing quali ordering output (`-pi`, lower=better) must remain byte-identical. This gate ADDS a gap expression the head did not have; it must not alter any existing `-pi` consumer. `pi` stays dimensionless; gap is expressed ONLY through `s * (pi_i - pi_j)`.

## Test Mode
Test-after allowed (pure functions; small surface). Tests must be meaningful (formula, sign, monotone-invariance of order, reference handling, edge cases, provider None-on-empty, aggregation).

## Close Criteria
- `expected_gap_ij(pi_i, pi_j, s) -> float == s*(pi_i - pi_j)` (the #386 contract function; fraction-of-median units).
- `expected_gaps(pi: Mapping[str,float], s, *, reference='median') -> Dict[str,float]` returns per-driver gap-to-reference `s*(pi_d - ref(pi))`; field-level expression.
- `carry_forward_scale(history) -> Optional[float]` = last-known prior-event quali s_e (None if empty). [CF1]
- `same_circuit_prior_year_scale(prior_year_record_or_value) -> Optional[float]` = same-circuit prior-year quali s_e (None if absent). [CF2 — Admiral correction]
- `global_constant_scale(records) -> float` = mean/median s_e over a fitting pool (the baseline both CF variants must beat).
- Input validation with messages naming field/expectation/actual.
- Positive-s order-invariance: sign(expected_gap_ij) == sign(pi_i - pi_j) for s>0.
- pytest green; pyright clean on touched; simplification_limits clean on touched.

## Allowed Scope
- NEW file `src/evo_predictor/quali_gap_scale.py`
- NEW file `tests/unit/evo_predictor/test_quali_gap_scale.py`

## Specific Exclusions
- No change to `spread_target.py` (label estimator/IO stays untouched).
- No retro re-solve; no pi-semantics change; no sigma / disagreement_rate logic.
- No DB access in the pure module (circuit→round resolution via get_calendar lives in the g2 harness; the pure provider takes an already-looked-up prior-year record/value).
- Do NOT alter any existing `-pi` consumer.

## Constraints
- pi dimensionless; gap via exchange rate only.
- Default-preserving: new file only.
- py not python; targeted pytest only; pyright-clean on touched; simplification_limits on touched.
- Validate public inputs (field/expectation/actual).

## Required Evidence
- `py -m pytest tests/unit/evo_predictor/test_quali_gap_scale.py -q` green.
- pyright on the two touched files clean.
- `py -m src.utils.simplification_limits` on the two touched paths clean.

## Verification Commands
```
py -m pytest tests/unit/evo_predictor/test_quali_gap_scale.py -q
py -m src.utils.simplification_limits src/evo_predictor/quali_gap_scale.py tests/unit/evo_predictor/test_quali_gap_scale.py
```

## Authority
Mechanism + API fixed by the approved plan + Admiral correction (CF1+CF2, drop persistence). Implementer must not change the API shape or scope.

## Stop Conditions
Stop and return if scope must be exceeded, an exclusion must be touched, or evidence cannot be produced.
