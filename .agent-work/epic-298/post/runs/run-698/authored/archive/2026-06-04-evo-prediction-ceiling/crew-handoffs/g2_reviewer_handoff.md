# Reviewer Handoff

Concise fragments. Omit filler.

## Gate
`g2` — honest, n-aware `sigma_corr` diagnostic.

## What Was Implemented
A named significance helper (`correlation_is_significant(r, n, alpha)`, exact t-based
critical-r via scipy; `SIGNIFICANCE_ALPHA=0.05`) in `gold_module_cycle.py`, re-exported
and used by `module_uncertainty_diagnostics.py`. `sigma_error_correlation_wrong_sign`
now fires only for a SIGNIFICANTLY negative correlation at the scored event count `n`;
insignificant correlations get a new informational `sigma_error_correlation_insignificant`
flag. The duplicate hard `abs(corr)<0.05` near_zero loop in
`gold_module_cycle.uncertainty_calibration()` was routed through the same helper. The
summary key `modules_with_near_zero_uncertainty_error_correlation` was KEPT (name) but
its meaning REDEFINED to count insignificant correlations (consumer:
`scripts/run_pipeline_validation.py`).

## How to Inspect the Diff
- `git status --porcelain` — src/tests changes plus untracked `.agent-work/`.
- `git diff -- src/evo_predictor/module_uncertainty_diagnostics.py src/evo_predictor/gold_module_cycle.py tests/unit/evo_predictor/test_module_uncertainty_diagnostics.py`

## Task Statement
Make the sigma/error-correlation diagnostic statistically honest: gate `wrong_sign` on
significance at the event count (a correlation indistinguishable from 0 at n must not
read as a defect), while a genuinely significant wrong-sign correlation still flags.
Consolidate the duplicate near_zero magic threshold into one n-aware gate. No runtime
sigma/calibration change; no new dependency.

## Close Criteria (each a review check)
- Both test files re-run GREEN:
  `py -m pytest tests/unit/evo_predictor/test_module_uncertainty_diagnostics.py tests/unit/evo_predictor/test_gold_module_cycle.py -q`.
- Significance correctness: independently confirm the t-based `r_crit(n=24,alpha=0.05)≈0.4044`
  (matches G1). `wrong_sign` fires for a significant negative (e.g. r≈−0.7 @ n=24) and
  NOT for n=24 |r|≈0.1. On the current bundle the two race-start recent_history modules
  (−0.119, −0.092) are no longer wrong_sign-flagged (was 3 wrong_sign → 0).
- Single honest path: no second magic `0.05` remains (only the named `SIGNIFICANCE_ALPHA`);
  the retained `{key}_near_zero` flag (gold_module_cycle) is now n-aware via the helper,
  not a leftover dishonest/parallel threshold.
- **SCHEMA CONTRACT (scrutinize hardest):** the summary key kept its name but changed
  meaning. Verify (i) the consumer `scripts/run_pipeline_validation.py` still behaves
  correctly under the new semantics; (ii) whether `src/evo_predictor/gold_report_schema.py`
  and/or `docs/report_schemas/` describe this key or the sigma-corr flags and are now
  STALE. Per project rule, a report-schema meaning change must move producer + committed
  consumer + docs together. If a description/consumer is now inconsistent and was not
  updated, that is a BLOCK (or must be explicitly routed). Make the call.
- Honesty of framing: `insignificant` is presented as benign/advisory (markdown +
  summary), not as a defect.
- Diagnostics-only: no change to runtime sigma values, `gold_cycle/calibration.py`,
  fusion, `latent_power/`, or any artifact; no new third-party dependency (confirm scipy
  was already declared in `pyproject.toml`).
- `py -m src.utils.simplification_limits` canonical gate passes on touched paths; confirm
  NO new violation was introduced (implementer claims the 5 strict-positional hits are
  pre-existing grandfathered megafile debt — verify via the baseline gate, and that the
  one expanded function is net-neutral-or-better).

## Allowed Scope
`src/evo_predictor/module_uncertainty_diagnostics.py`,
`src/evo_predictor/gold_module_cycle.py` (duplicate-flag logic only),
`tests/unit/evo_predictor/test_module_uncertainty_diagnostics.py`.

## Specific Exclusions (flag if touched)
Runtime sigma production, calibration fit, fusion, latent_power/, any artifact, new deps.

## Constraints the Implementation Must Respect (each a review check)
- `py` for python; test-led.
- One canonical flag path; named constant for alpha; no inline magic numbers.
- `simplification_limits` (canonical/baseline gate) on touched paths.
- Diagnostics-only.

## Evidence Produced
67 passed (both target files); downstream contract tests (pipeline_validation,
gold_report_schema, gold_cycle_runner) 58 passed; t-based method reproduces G1
r_crit=0.4044; bundle wrong_sign 3→0; simplification baseline gate PASS, renderer
refactored 33→26 CC / 161→149 lines; scipy>=1.9.0 already in pyproject (no new dep).

## Suggested Model Tier
stronger — reason: report-schema-contract judgment (redefined key) + statistical
correctness + a consolidation that must not break the gold cycle.

## Stop Conditions
Return BLOCK if: tests don't re-run green, the significance gate is wrong (over/under
fires), a second magic threshold remains, the redefined summary key leaves the consumer
or schema docs inconsistent without update, any excluded surface was touched, a new dep
was added, or simplification_limits regressed.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings (with your
independent r_crit recompute, the bundle before/after, and an explicit ruling on the
schema-contract question), blockers, out-of-scope observations.
