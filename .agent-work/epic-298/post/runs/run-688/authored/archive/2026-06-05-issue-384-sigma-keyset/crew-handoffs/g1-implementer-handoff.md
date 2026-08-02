# Implementer Handoff

## Gate
`g1`

## Task
Reconcile the σ/error-correlation diagnostic key sets in the evo gold-cycle diagnostics, and pin them with a structural test so producer and consumer key sets cannot drift apart again. This is issue #384 (F2 in `docs/evo/prediction_ceiling_and_priorities.md` §6.2).

The **bug**: `src/evo_predictor/module_uncertainty_diagnostics.py::_SIGMA_ERROR_CORR_KEYS` lists `corr_sigma_pi_trace_vs_{log_loss, brier, rank_mae}`, but the producer `src/evo_predictor/gold_module_cycle.py::uncertainty_calibration()` only emits `corr_sigma_pi_trace_vs_nll` and `corr_sigma_pi_trace_vs_rank_mae` (plus two `corr_field_std_*` keys that are a different signal). So the n-aware σ wrong-sign / insignificant gate in `_module_diagnostic_flags` runs on `rank_mae` alone — `log_loss`/`brier` are silently absent and the emitted `nll` channel is ignored.

The **direction is DECIDED and frozen** (do not re-litigate): align the CONSUMER to the producer's two σ channels (`nll` + `rank_mae`). Evidence: the `..._vs_log_loss`/`..._vs_brier` strings exist only in the consumer + stale test fixtures, never in any `src/` producer; the committed report schema `gold_report_schema.py` documents the emitted σ keys as `nll`+`rank_mae`; the consumer constant was wrong from its introduction in #225.

## Subtasks (all required)
1. **Consumer constant.** In `src/evo_predictor/module_uncertainty_diagnostics.py`, change `_SIGMA_ERROR_CORR_KEYS` to exactly the two emitted σ channels:
   ```python
   _SIGMA_ERROR_CORR_KEYS = (
       "corr_sigma_pi_trace_vs_nll",
       "corr_sigma_pi_trace_vs_rank_mae",
   )
   ```
   Update the surrounding comment to explain these are the σ (sigma_pi_trace) channels the producer `gold_module_cycle.uncertainty_calibration()` actually emits, and that the field_std channels are deliberately excluded (a different signal). Keep it concise and honest.

2. **Structural pin test (the heart of the fix).** Add a test (in `tests/unit/evo_predictor/test_module_uncertainty_diagnostics.py`) that:
   - imports the consumer constant `_SIGMA_ERROR_CORR_KEYS` from `module_uncertainty_diagnostics`;
   - imports and CALLS the producer `gold_module_cycle.uncertainty_calibration()` on a small fixture of scored rows (rows need at least `pairwise_nll`, `sigma_pi_trace`, `field_std`, `rank_mae_vs_retro_bt`), takes the returned `["correlations"]` dict, and filters its keys to the σ ones (those starting `corr_sigma_pi_trace_`);
   - asserts `set(consumer_keys) == set(producer_sigma_keys)`.
   It must derive BOTH sides from live code (no hardcoded expected list) so it FAILS if either the producer or consumer key set drifts. Note: `_SIGMA_ERROR_CORR_KEYS` is private — import it explicitly (`from src.evo_predictor.module_uncertainty_diagnostics import _SIGMA_ERROR_CORR_KEYS`); that is acceptable for a pin test whose whole job is to bind the two internal key sets.

3. **Rework drifted unit tests.** In `tests/unit/evo_predictor/test_module_uncertainty_diagnostics.py`, the fixtures `_make_module_result` and `_make_result_with_correlations` inject `corr_sigma_pi_trace_vs_log_loss`/`_vs_brier` keys and several tests assert the wrong-sign gate fires on them (e.g. `test_report_flags_significant_wrong_sign_sigma_log_loss_correlation`, `..._brier_correlation`). These pass today only because the consumer matched the FABRICATED keys. After subtask 1 they will be testing absent keys. Rework them so the fixtures emit the producer's REAL σ keys (`corr_sigma_pi_trace_vs_nll`, `corr_sigma_pi_trace_vs_rank_mae`) and the wrong-sign/insignificant tests exercise those real channels (repoint the log_loss/brier-specific cases to `nll`). Preserve the n-aware significance coverage (the existing tests around `correlation_is_significant`, insignificant-vs-wrong-sign, summary counts) — just point them at real keys. Do not delete coverage; convert it.

4. **Fix stale pipeline-validation fixture.** In `tests/unit/evo_predictor/test_pipeline_validation.py`, `_gold_module_observability` builds an `uncertainty_calibration.correlations` block (around lines 36-43) with the fabricated `corr_sigma_pi_trace_vs_log_loss`/`_vs_brier`/`corr_field_std_vs_log_loss`/`_vs_brier` keys. Update it to the producer's real key set (`corr_sigma_pi_trace_vs_nll`, `corr_sigma_pi_trace_vs_rank_mae`, `corr_field_std_vs_nll`, `corr_field_std_vs_rank_mae`) so the validation fixture reflects the true producer contract. This test does not assert the σ gate; it should still pass — confirm it does.

5. **Doc note (append-shaped).** Append a SHORT resolution note under `docs/evo/prediction_ceiling_and_priorities.md` §6.2 (the F2 bullet). New note appended — do NOT rewrite the existing F2 bullet. Record: F2 resolved by aligning the consumer `_SIGMA_ERROR_CORR_KEYS` to the producer's emitted σ channels (`nll`+`rank_mae`), with a structural producer≡consumer pin test; reference #384.

## Protected Intent
The σ wrong-sign / insignificant gate must evaluate the σ channels it claims (BOTH `nll` and `rank_mae`), not `rank_mae` alone. The emitted report shape and the summary key names (`modules_with_*_uncertainty_error_correlation`) must NOT change — they are flag-derived, not key-name-derived.

## Test Mode
test-after acceptable for subtask 1 (trivial constant change), but the structural pin test (subtask 2) and the reworked tests (subtask 3) ARE the verification — write/adjust them in the same change and prove them green. The pin test should be demonstrably able to fail (you may sanity-check by temporarily reverting the constant locally, observing the failure, then restoring — report if you did).

## Close Criteria
- `_SIGMA_ERROR_CORR_KEYS == ("corr_sigma_pi_trace_vs_nll", "corr_sigma_pi_trace_vs_rank_mae")`.
- A structural pin test exists that derives both key sets from live code and asserts equality; it passes; it would fail on drift.
- The σ gate (`_module_diagnostic_flags`) now reads both σ channels (verify via a test that the gate fires on a significantly-negative `nll` correlation, not only `rank_mae`).
- Reworked diagnostics tests + pipeline-validation fixture use producer-real keys; all green.
- Doc note appended under §6.2 F2 (append-shaped), references #384.
- `py -m pytest tests/unit/evo_predictor/test_module_uncertainty_diagnostics.py tests/unit/evo_predictor/test_pipeline_validation.py -q` passes.
- `py -m src.utils.simplification_limits` clean on touched src/tests paths.
- Pyright clean on touched src (if pyright available: `py -m pyright src/evo_predictor/module_uncertainty_diagnostics.py`).

## Allowed Scope
- `src/evo_predictor/module_uncertainty_diagnostics.py` (the `_SIGMA_ERROR_CORR_KEYS` constant + its comment ONLY).
- `tests/unit/evo_predictor/test_module_uncertainty_diagnostics.py` (fixtures + σ-correlation tests + new pin test).
- `tests/unit/evo_predictor/test_pipeline_validation.py` (`_gold_module_observability` correlation fixture only).
- `docs/evo/prediction_ceiling_and_priorities.md` (append a note under §6.2 F2 only).

## Specific Exclusions
- Do NOT edit the producer `src/evo_predictor/gold_module_cycle.py` (it already emits the correct keys).
- Do NOT add `brier`/`log_loss` correlations anywhere.
- Do NOT widen the σ gate to `field_std` channels.
- Do NOT touch `entity_count`, `event_level_metrics`, or the calibration dof term (sibling #383 owns that — F1).
- Do NOT change `gold_report_schema.py` or any emitted-report field/summary-key name.
- Do NOT rewrite existing prose in `prediction_ceiling_and_priorities.md` — append only.

## Constraints
- Use `py` (not `python`) for Python.
- Prefer one canonical execution path; no compatibility shims or dual key sets.
- The doc edit must be append-shaped.
- Keep the change minimal and bounded — this is sized small.

## Required Evidence
- `git diff --stat` of the change.
- Output of `py -m pytest tests/unit/evo_predictor/test_module_uncertainty_diagnostics.py tests/unit/evo_predictor/test_pipeline_validation.py -q`.
- Output of `py -m src.utils.simplification_limits <touched paths>`.
- Pyright output on the touched src module (or note if pyright unavailable).
- The final `_SIGMA_ERROR_CORR_KEYS` value and the body of the new pin test (paste).

## Verification Commands
```bash
cd C:/Programs/f1Brainz/.claude/worktrees/agent-a43c9994cf94e812c
py -m pytest tests/unit/evo_predictor/test_module_uncertainty_diagnostics.py tests/unit/evo_predictor/test_pipeline_validation.py -q
py -m src.utils.simplification_limits src/evo_predictor/module_uncertainty_diagnostics.py tests/unit/evo_predictor/test_module_uncertainty_diagnostics.py tests/unit/evo_predictor/test_pipeline_validation.py
py -m pyright src/evo_predictor/module_uncertainty_diagnostics.py
```

## Suggested Model Tier
`simple bounded` — dispatch with model: sonnet. Scope is small and the direction is fully decided; the only craft is making the pin test genuinely structural.

## Authority
Direction (consumer→producer; nll+rank_mae) is DECIDED by the Admiral's PRE-RULING R2 + code/schema/git evidence — do not change it. Test-rework approach is decided (convert, don't delete coverage). You may NOT: change the alignment direction, emit brier/log_loss, widen to field_std, edit the producer or schema, or touch #383's territory. If any close criterion cannot be met without violating an exclusion, STOP and return.

## Stop Conditions
Stop and return if: allowed scope must be exceeded, a specific exclusion must be touched, the pin test cannot be made to derive both sides from live code, required evidence cannot be produced, or a decision outside the given authority is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced (paste the test + simplification_limits + pyright output), assumptions used, stop conditions hit, out-of-scope observations.
