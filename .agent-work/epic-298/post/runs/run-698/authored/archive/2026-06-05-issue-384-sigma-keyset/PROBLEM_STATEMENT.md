# Problem Statement — Issue #384 (σ/error-correlation diagnostic key-set mismatch)

## The bug
`src/evo_predictor/module_uncertainty_diagnostics.py` defines the consumer constant:

```python
_SIGMA_ERROR_CORR_KEYS = (
    "corr_sigma_pi_trace_vs_log_loss",   # never emitted by producer
    "corr_sigma_pi_trace_vs_brier",      # never emitted by producer
    "corr_sigma_pi_trace_vs_rank_mae",   # emitted
)
```

The producer — `src/evo_predictor/gold_module_cycle.py::uncertainty_calibration()` — emits exactly:
- `corr_sigma_pi_trace_vs_nll`   (σ channel, emitted, IGNORED by consumer)
- `corr_sigma_pi_trace_vs_rank_mae` (σ channel, emitted, consumed)
- `corr_field_std_vs_nll`, `corr_field_std_vs_rank_mae` (field-spread channels, out of σ-gate scope)

Result: of the consumer's three keys, only `rank_mae` matches an emitted key. `log_loss`/`brier` are silently absent (always `None` → dropped by `finite_float`), and the emitted `nll` channel is never read. So the (n-aware, PR #366) wrong-sign / insignificant σ gate in `_module_diagnostic_flags` runs on **`rank_mae` alone**, not the multi-channel set the code implies.

## Resolved decisions (interrogation)

1. **Alignment direction — CONSUMER → PRODUCER** (`corr_sigma_pi_trace_vs_nll` + `corr_sigma_pi_trace_vs_rank_mae`). PRE-RULING R2 default; the R2 exception does NOT apply. Three independent confirmations that log_loss/brier were never intended:
   - `git grep`: the `..._vs_log_loss`/`..._vs_brier` strings exist ONLY in the consumer file (+ stale test fixtures); no `src/` producer ever emitted them.
   - `git log -S`: producer side never had a log_loss/brier σ-trace correlation; consumer constant was wrong from its inception in #225.
   - Committed report schema `gold_report_schema.py` (lines 356-357, slice_metrics descriptions) documents the emitted σ keys as `nll` + `rank_mae`, never log_loss/brier.

2. **field_std correlations OUT of scope.** `_SIGMA_ERROR_CORR_KEYS` stays the two `sigma_pi_trace_*` channels only. field_std is a distinct signal; the gate name + issue scope are about σ.

3. **Structural pin test (heart of the fix).** Import the consumer constant `_SIGMA_ERROR_CORR_KEYS` AND derive the producer's emitted σ keys live from `gold_module_cycle.uncertainty_calibration()` output (filter `correlations` to `sigma_pi_trace_*`); assert set-equality. Both sides bound to live code → cannot drift. A hardcoded expected-list is rejected.

4. **Sibling boundary.** Touch ONLY the σ-keyset consumer + its tests (+ a doc note). Producer `gold_module_cycle` already emits correct keys → no producer edit. Do NOT touch `entity_count`/`event_level_metrics`/dof term — sibling #383 owns F1.

5. **Existing tests are part of the drift — rework in scope.** `test_module_uncertainty_diagnostics.py` fixtures fabricate log_loss/brier keys and assert the gate fires on them (passing only because consumer matched the fabricated keys). Rework fixtures to emit producer-real keys (nll + rank_mae) and repoint the log_loss/brier wrong-sign tests to nll. Also update the stale `test_pipeline_validation.py::_gold_module_observability` correlation fixture (lines 37-42) to producer-real keys for fixture honesty (does not assert the σ gate; low-risk).

6. **Doc note — append-shaped.** Append a minimal resolution note under design-doc §6.2 (F2) recording the fix + structural pin, ref #384. Honors the Admiral append-only constraint.

## No schema change
Summary report keys (`modules_with_*_uncertainty_error_correlation`) are FLAG-derived, not key-name-derived. Aligning `_SIGMA_ERROR_CORR_KEYS` renames no emitted report field. The producer output is unchanged. So this is NOT a committed-report-schema change (the report-schema atomic-update rule does not bind).

## Acceptance (from issue + Admiral)
- Consumer key set ≡ producer σ key set (`nll` + `rank_mae`).
- The σ wrong-sign / insignificant gate evaluates the channels it claims (both σ channels), not rank_mae alone.
- A STRUCTURAL test pinning producer ≡ consumer so they cannot drift again.
- Targeted tests green; pyright-clean on touched src.
