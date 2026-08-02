# Review Result — g1

## Assigned Gate
`g1` — Reconcile σ/error-correlation diagnostic key sets + structural pin (issue #384)

## Result
`APPROVE`

## Handoff compliance
All asks met. `_SIGMA_ERROR_CORR_KEYS = ("corr_sigma_pi_trace_vs_nll", "corr_sigma_pi_trace_vs_rank_mae")`. Structural producer≡consumer pin test added. Drifted diagnostics tests reworked to producer-real keys. Stale pipeline-validation fixture corrected. Append-shaped resolution note added under §6.2 F2 referencing #384.

## Scope drift
None. Exactly the 4 allowed files changed (verified via `git diff --name-only HEAD`). Producer `gold_module_cycle.py` untouched (independently verified it still emits `nll`+`rank_mae`). `gold_report_schema.py` untouched. No `entity_count`/`event_level_metrics`/dof term touched (sibling #383). No `brier`/`log_loss` emitted. σ gate not widened to `field_std`. Doc note is append-only.

## Evidence verdict
Verified independently (not trusting the result doc):
- `py -m pytest tests/unit/evo_predictor/test_module_uncertainty_diagnostics.py tests/unit/evo_predictor/test_pipeline_validation.py -q` → **79 passed**.
- `py -m pyright src/evo_predictor/module_uncertainty_diagnostics.py` → **0 errors, 0 warnings**.
- TDD evidence credible: original RED (extra brier+log_loss / missing nll) and post-fix GREEN.
- Added regression guard `test_report_wrong_sign_gate_evaluates_nll_not_rank_mae_alone` directly proves the #384 symptom is fixed (gate fires on wrong-signed nll while rank_mae benign).

## Pin test is genuinely structural (critical check)
CONFIRMED. `_producer_sigma_correlation_keys()` calls the real `gold_module_cycle.uncertainty_calibration()` and filters `corr_sigma_pi_trace_*`; the consumer constant is imported. Neither side is a hardcoded list. Proved drift-detection: temporarily added `corr_sigma_pi_trace_vs_BOGUS` to the consumer → `test_consumer_sigma_keys_equal_producer_sigma_keys` FAILED with a precise set diff; restored. The pin will catch any future add/drop/rename on either side.

## Code/doc quality
Minimal, canonical (single key set, no shim/dual/alias). Comment on the constant is accurate and explains both the bug and why `field_std` is excluded. Diff introduces ZERO new simplification violations (canonical `--baseline` check FAILs only on 2 pre-existing unrelated files). Doc note honest and append-shaped.

## Reconciliation check
No emitted-report-schema change (summary keys are flag-derived; producer output unchanged). No architecture/boundary divergence — change stays within evo diagnostics. Nothing for the cartographer beyond a one-line note that the σ gate is now multi-channel and pinned.

## Blockers
- None.

## Out-of-scope observations
- (triage tc1) Pre-existing simplification-limit debt: `render_module_uncertainty_diagnostics_markdown` is complexity 26 / 149 lines (limits <20/<100). Untouched by #384, tolerated by `--baseline`. Candidate for a future render-splitting refactor.

## Note for Commander
During the structural drift-check, a `git checkout` to restore the temporarily-mutated source briefly reverted the (uncommitted) source fix; it was immediately re-applied and re-verified (79 passed, diff back to the correct 4-file state). Final working tree is correct.

## Return status
`complete`
