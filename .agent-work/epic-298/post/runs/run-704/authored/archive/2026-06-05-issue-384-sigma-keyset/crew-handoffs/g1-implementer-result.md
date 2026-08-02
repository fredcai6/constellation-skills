# Implementation Result — g1

## Assigned gate
`g1` — Reconcile σ/error-correlation diagnostic key sets + structural pin (issue #384)

## Completed slice
Aligned the consumer σ-correlation key set to what the gold-cycle producer actually emits, added a structural producer≡consumer pin test, reworked the test fixtures/cases that encoded the same drift, fixed a stale pipeline-validation fixture, and appended a resolution note to the design doc.

## Scope
**Files changed (4, vs branch point fa9e48b):**
- `src/evo_predictor/module_uncertainty_diagnostics.py` — `_SIGMA_ERROR_CORR_KEYS` now `("corr_sigma_pi_trace_vs_nll", "corr_sigma_pi_trace_vs_rank_mae")`; honest explanatory comment added.
- `tests/unit/evo_predictor/test_module_uncertainty_diagnostics.py` — added structural pin test + producer-emits guard; reworked `_make_module_result`/`_make_result_with_correlations` and all wrong-sign/insignificant/markdown/missing-metric tests to producer-real keys; added `test_report_wrong_sign_gate_evaluates_nll_not_rank_mae_alone` regression guard.
- `tests/unit/evo_predictor/test_pipeline_validation.py` — `_gold_module_observability` correlation fixture updated to producer-real keys.
- `docs/evo/prediction_ceiling_and_priorities.md` — appended a *Resolved (#384)* sub-note under §6.2 F2 (append-shaped; existing prose untouched).

**Specific exclusions touched:** no. Producer `gold_module_cycle.py` untouched; `gold_report_schema.py` untouched; no `entity_count`/`event_level_metrics`/dof term (sibling #383); no field_std widening; no brier/log_loss emitted; no summary-key rename.

## Behavior changed
Yes — the σ wrong-sign / insignificant gate now evaluates BOTH emitted σ channels (`nll` + `rank_mae`) instead of `rank_mae` alone. The previously-ignored `nll` channel is now consumed; the never-emitted `log_loss`/`brier` keys are removed. No emitted-report shape change (summary keys are flag-derived).

## Test mode
**Required:** TDD for the pin test (red→green); test-after acceptable for the constant.
**Satisfied:** yes.
- Pin test RED against the wrong constant: `AssertionError` — left set extra `{corr_sigma_pi_trace_vs_brier, corr_sigma_pi_trace_vs_log_loss}`, right set extra `{corr_sigma_pi_trace_vs_nll}`.
- After aligning the constant: pin test GREEN.

## Evidence

```bash
py -m pytest tests/unit/evo_predictor/test_module_uncertainty_diagnostics.py tests/unit/evo_predictor/test_pipeline_validation.py -q
# => 79 passed in 0.66s

py -m pyright src/evo_predictor/module_uncertainty_diagnostics.py
# => 0 errors, 0 warnings, 0 informations

py -m src.utils.simplification_limits --baseline
# => FAIL (2 violations, 519 files checked):
#    src/evo_predictor/models/_param_dataclasses.py: file_lines=1122
#    src/reporting/html_reports/__init__.py: file_lines=1627
#    (both pre-existing, both in files I did NOT touch)
```

**Result:** pass. Targeted suites green; pyright clean; canonical baseline simplification check FAILs only on 2 pre-existing, unrelated files (not introduced by this change).

## The structural pin (heart of the fix)
```python
def _producer_sigma_correlation_keys() -> set[str]:
    rows = [ {"sigma_pi_trace": 4.0+i, "field_std": 0.5+0.1*i,
              "pairwise_nll": 0.50+0.02*i, "rank_mae_vs_retro_bt": 2.0+0.3*i}
             for i in range(6) ]
    correlations = uncertainty_calibration(rows)["correlations"]
    return {k for k in correlations if k.startswith("corr_sigma_pi_trace_")}

def test_consumer_sigma_keys_equal_producer_sigma_keys():
    assert set(_SIGMA_ERROR_CORR_KEYS) == _producer_sigma_correlation_keys()
```
Both sides derived from live code: consumer constant imported; producer keys computed by actually calling `gold_module_cycle.uncertainty_calibration()`. Fails on any add/drop/rename on either side. No hardcoded expected list.

## Final constant
```python
_SIGMA_ERROR_CORR_KEYS = (
    "corr_sigma_pi_trace_vs_nll",
    "corr_sigma_pi_trace_vs_rank_mae",
)
```

## Docs/contracts touched
- `docs/evo/prediction_ceiling_and_priorities.md` §6.2 F2 — append-shaped resolution note.
- No committed report-schema change (producer output unchanged; summary keys flag-derived). The report-schema atomic-update rule does not bind.

## Assumptions
- The `nll` producer channel maps to the metric the issue calls "nll" (confirmed: `_corr(scored, "sigma_pi_trace", "pairwise_nll")`).
- `_SIGMA_ERROR_CORR_KEYS` is acceptable to import in tests despite the leading underscore — its whole purpose is the internal pin; documented in the test comment.

## Stop conditions hit
- None.

## Out-of-scope observations (for Commander → triage)
1. **Pre-existing simplification-limit debt in a touched file:** `render_module_uncertainty_diagnostics_markdown` in `module_uncertainty_diagnostics.py` is complexity 26 / 149 lines (limits <20 / <100). Pre-existing, untouched by this change, tolerated by `--baseline`. Flagged only by strict `--paths` mode because the file was touched elsewhere. Candidate for a future render-splitting refactor; NOT fixed here (out of scope, sized-small issue).
2. **Branch point lag:** this branch was cut from `fa9e48b`; `origin/main` has since advanced ~10 commits via sibling merges. Verified the producer/consumer on current `origin/main` are still compatible with this fix (producer emits nll+rank_mae; consumer still buggy — no sibling touched it). Commander should rebase/merge current main before/at PR.

## Return status
`complete`
