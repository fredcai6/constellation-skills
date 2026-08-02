# Implementer Handoff

Concise fragments. Omit filler.

## Gate
`g2` — honest, n-aware `sigma_corr` diagnostic.

## Task
Make the sigma/error correlation diagnostic statistically honest by gating it on
significance at the event count, instead of a hard sign/magnitude threshold.

1. **Significance helper (named, tested).** Add a named significance level constant
   and a small function that, given the scored event count `n` and a correlation
   `r`, decides significance. Method may be either the exact t-based critical-r
   (`r_crit = t_crit/sqrt(n-2+t_crit^2)`, matching G1's `r_crit(n=24)=0.4044`) IF
   scipy is already a declared project dependency, OR a dependency-free Fisher-z
   normal-approx test (`|atanh(r)|*sqrt(n-3) > Z_CRIT`, `Z_CRIT≈1.959964` for
   alpha=0.05) using only `math`. Pick ONE; do not add a new dependency. The level
   (alpha=0.05) and any critical value are NAMED CONSTANTS, not inline magic.

2. **Honest flags** in `src/evo_predictor/module_uncertainty_diagnostics.py`
   (currently lines ~73-86, `_module_diagnostic_flags`):
   - `sigma_error_correlation_wrong_sign` fires ONLY when a sigma/error correlation
     is **significantly negative** (`r < 0` AND significant at `n`). An insignificant
     negative `r` (e.g. race-start −0.119 at n=24) MUST NOT fire it.
   - `sigma_error_correlation_near_zero`: reframe honestly. Insignificance is the
     EXPECTED, benign state at low n / deterministic phases — it is not a defect.
     Either drop this warning or demote it to clearly-informational; do not let an
     insignificant correlation read as a problem. Use your judgment; the reviewer
     will check the framing is honest.
   - Thread the scored event count `n` into `_module_diagnostic_flags` (available as
     `len(scored_rows)` in `_module_entry`).

3. **Consolidate the duplicate.** `src/evo_predictor/gold_module_cycle.py`
   `uncertainty_calibration()` (~lines 143-146) independently appends
   `{key}_near_zero` via a separate hard `abs(value) < 0.05`. Remove the duplicate
   magic threshold and route ALL sigma/error-correlation flagging through the single
   n-aware helper so there is ONE honest gate. (The flag is merged into diagnostics
   via the `existing_flags` path — keep that working, or move the logic; just no
   second magic 0.05 left behind.)

## Protected Intent
Diagnostics honesty only. The runtime sigma VALUES and the calibration artifact must
not change in this gate. The point: a correlation indistinguishable from 0 at the
event count stops being reported as a defect, while a genuinely significant wrong-sign
correlation still flags.

## Test Mode
TDD preferred (the behavior is precise and testable). Extend
`tests/unit/evo_predictor/test_module_uncertainty_diagnostics.py`.

## Close Criteria
- A genuinely significant negative correlation (e.g. r≈−0.7 at n=24, or the helper's
  own significant region) STILL raises `sigma_error_correlation_wrong_sign`.
- An n=24, |r|≈0.1 correlation does NOT raise `wrong_sign` (nor read as a defect).
- Recompute/derive on the persisted bundle: the two race-start recent_history modules
  (`driver_race_start_power_from_recent_history` r=−0.119,
  `constructor_race_start_power_from_recent_history` r=−0.092) are NO LONGER
  wrong_sign-flagged; any genuinely significant module (if present) still flags.
- The threshold/alpha is a named constant; the significance decision is a named,
  unit-tested function; no second magic 0.05 remains.
- `py -m pytest tests/unit/evo_predictor/test_module_uncertainty_diagnostics.py -q`
  green, AND `py -m pytest tests/unit/evo_predictor/test_gold_module_cycle.py -q`
  still green (consolidation must not break it).
- `py -m src.utils.simplification_limits` passes on every touched src/ and tests/ path.

## Allowed Scope
- `src/evo_predictor/module_uncertainty_diagnostics.py`
- `src/evo_predictor/gold_module_cycle.py` (only the duplicate near_zero flag logic)
- `tests/unit/evo_predictor/test_module_uncertainty_diagnostics.py` (and
  `test_gold_module_cycle.py` if a test there asserts the old behavior)
- A named constant may live in the most local sensible module (diagnostics module is
  fine); do not invent a new config file.

## Specific Exclusions
- Do NOT change runtime sigma production, the calibration fit (`gold_cycle/calibration.py`),
  fusion, or `latent_power/`.
- Do NOT add a new third-party dependency.
- Do NOT regenerate or edit any gold bundle / report artifact.

## Constraints
- `py` for python.
- Test-led; run the focused evo tests before and after.
- One canonical flag path — no duplicate magic thresholds.
- Named constants for alpha/critical value; no inline magic numbers.
- `py -m src.utils.simplification_limits` (strict) on touched paths.

## Required Evidence
Paste into IMPLEMENTER_RESULT: the new test names + `pytest -q` output for both test
files; the simplification_limits output; and a short before/after of which modules
carry `sigma_error_correlation_wrong_sign` on the current bundle (expect the 2
race-start recent_history modules to drop).

## Verification Commands
```bash
py -m pytest tests/unit/evo_predictor/test_module_uncertainty_diagnostics.py tests/unit/evo_predictor/test_gold_module_cycle.py -q
py -m src.utils.simplification_limits src/evo_predictor/module_uncertainty_diagnostics.py src/evo_predictor/gold_module_cycle.py
```

## Suggested Model Tier
stronger — reason: probability-adjacent diagnostics, a statistical gate, and a
de-duplication that must not break the gold cycle.

## Authority
Decided (human): Path 1, honest flag. You decide the significance method (t-based vs
Fisher-z) and the near_zero framing, within the constraints. You must NOT change
runtime sigma values, add deps, or touch artifacts.

## Stop Conditions
Stop and return if: making the gate honest requires touching runtime sigma/calibration
(out of scope), a new dependency seems necessary, or the consolidation can't preserve
`test_gold_module_cycle.py` without a scope expansion.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied,
evidence (pytest + simplification_limits output, before/after flag set), assumptions,
stop conditions hit, out-of-scope observations.
