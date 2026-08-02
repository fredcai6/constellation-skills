# Crew Handoff

## Role
implementer

## Assigned Gate
G2 — surface `|r/σ|` percentile instrumentation (issue #304, phase 1)

## Suggested Model Tier
stronger broad — touches latent_power eval + the persisted diagnostics dict + the gold report producer + schema doc + tests, with an ADR-0001 boundary constraint

## Test Mode
TDD-leaning / test-after acceptable, but the new percentile fields MUST have unit tests asserting presence, finiteness, and monotonicity.

## Task
Today `latent_power/training.py` computes `r_over_sigma_p95/p99` + `sigma_mean` only on the LAST TRAINING BATCH and writes them only to the optional per-epoch JSONL diagnostics stream (`_diagnostics_handle`). They never reach the returned `diagnostics` dict, `module_diagnostics.json`, or the gold report.

Make `|r/σ|` a first-class, persisted uncertainty diagnostic:

1. **Compute over the full eval set, full percentile set.** In `latent_power/training.py`'s `_evaluate_module(...)` (the function that already produces `pairwise_metrics`/`field_metrics`/`calibration_metrics` over the full `validation_list`), compute `|r/σ| = |target_mu - mu| / sigma` across ALL validation pairwise predictions (concatenate over events, not last-batch) and derive percentiles `{p50, p90, p95, p99}` plus `sigma_mean`. Put them in a new diagnostics group, e.g. `uncertainty_diagnostics` (preferred — keeps it separate), returned alongside the existing metric groups. Guard the empty/None `target_mu` case (return nulls, never raise).
2. **Persist into the module diagnostics dict.** Add the new group to the `diagnostics` dict assembled at the end of `train_latent_power_module` (near `eval_pairwise_metrics`/`field_metrics`/`calibration_metrics`, ~lines 249-277) so it lands in `module_diagnostics.json`.
3. **Keep the existing per-epoch JSONL block** but you MAY refactor it to reuse the shared percentile helper. Extend it to the full {p50,p90,p95,p99} set for consistency. (Per-epoch can stay last-batch; the persisted/eval one MUST be full-eval — make the distinction explicit in field names or a comment.)
4. **Surface into the gold report (v5 fields).** In `src/evo_predictor/gold_cycle/reports.py`, include the per-module `uncertainty_diagnostics` percentiles in the per-module report entry (the same place module `field_metrics`/`calibration_metrics`/`uncertainty_calibration` are assembled). Register the new fields in `src/evo_predictor/gold_report_schema.py` (DETAILS or per-module section) and regenerate the schema markdown doc (`docs/evo/gold_module_training_cycle_report_schema.md`) via its generator — do NOT hand-edit it. These are the `|r/σ|` fields the v5 contract (G1) reserved; no further `REPORT_SCHEMA_VERSION` bump.
5. **Domain independence (ADR 0001).** `latent_power` must stay F1-agnostic: NO phase/scope strings (`quali`/`race_start`/`driver`/`constructor`) in `latent_power`. Percentiles are generic numbers keyed by module. Phase/scope is recoverable report-side from existing module names — no new tagging code needed in latent_power.
6. **Tests:**
   - `tests/unit/latent_power/test_training.py` (or test_modules): percentiles present + finite + monotonic `p50<=p90<=p95<=p99`; computed over the full validation set (construct a 2+ event validation set where last-batch vs full-set percentiles differ, assert the persisted value matches the full-set value); None/empty `target_mu` → null fields, no raise.
   - gold report test (`tests/unit/evo_predictor/test_gold_cycle_runner.py` or test_gold_report_schema): the per-module report entry carries the percentile fields and the schema doc validates.

## Baseline capture (required evidence)
Capture a baseline `|r/σ|` readout for the current promoted bundle `gold_cycle_260530_042533_2018thru2024` into `.agent-work/sigma-calibration-followups/evidence/g2-rsigma-baseline.md`. Source preference: recompute from the committed `params/gold/runtime_bundles/gold_cycle_260530_042533_2018thru2024/modules/*/module_diagnostics.json` if `|r/σ|` is derivable there, OR a no-train recompute pass over those bundles. If neither is feasible without a retrain, record that and capture the baseline numbers from the first smoke instead (note the limitation). Per-module p50/p90/p95/p99 table.

## Intent Protected
- Student-t heavy-tail robustness + the trained sigma signal (this only OBSERVES sigma; no loss/training-math change).
- `latent_power` must not import `evo_predictor` and must carry no F1 vocabulary (ADR 0001).
- Report producer + consumers + schema doc move together.

## Close Criteria
- `py -m pytest tests/unit/latent_power tests/unit/evo_predictor/test_gold_cycle_config.py tests/unit/evo_predictor/test_gold_cycle_runner.py -q` → exit 0.
- New percentile fields present in the persisted module diagnostics AND the gold report, with passing monotonicity/full-eval tests.
- `evidence/g2-rsigma-baseline.md` written with a per-module percentile table.

## Authority
User-approved plan, gate G2.

## Allowed Scope
`src/latent_power/training.py` (+ a small shared percentile helper if useful), `src/evo_predictor/gold_cycle/reports.py`, `src/evo_predictor/gold_report_schema.py`, the generated schema doc (via generator), and the named tests. The evidence file.

## Specific Exclusions
- Do NOT change any loss/training math, sigma computation, or numeric default.
- Do NOT add F1 phase/scope strings into `latent_power`.
- Do NOT add the term-B nu knob (G3).
- Do NOT bump `REPORT_SCHEMA_VERSION` again (G1 already set 5).
- Do NOT retrain or regenerate committed gold bundles.
- Do NOT commit (Pilot commits after review).

## Relevant Project Rules For This Gate
- Use `py`.
- Evidence is machine-checkable captured numbers.
- Generated artifacts regenerated from source, not hand-edited.
- Validate/guard the empty/missing `target_mu` case explicitly (no silent crash).

## Required Context
- `src/latent_power/training.py` (esp. `_evaluate_module`, the per-epoch diagnostics block ~152-174, and the final `diagnostics` dict ~249-277)
- `src/evo_predictor/gold_cycle/reports.py` (per-module entry assembly)
- `src/evo_predictor/gold_report_schema.py` (field registry + markdown generator)
- A committed `module_diagnostics.json` under `params/gold/runtime_bundles/gold_cycle_260530_042533_2018thru2024/modules/`

## Project Mechanics For This Gate
Do not commit. Return diff + evidence.

## Required Evidence
- Close-criteria pytest output (exit 0).
- The new field names + an example value block from a test or a small recompute.
- `evidence/g2-rsigma-baseline.md` content summary.

## Required Verification Commands
```bash
py -m pytest tests/unit/latent_power tests/unit/evo_predictor/test_gold_cycle_config.py tests/unit/evo_predictor/test_gold_cycle_runner.py -q
```

## Stop Conditions
Stop and return if: surfacing the percentiles forces a loss/training-math change; the only way to compute full-eval percentiles requires importing evo into latent_power; or the baseline cannot be recomputed without a full retrain (record the limitation and proceed with a smoke-derived baseline rather than blocking).

## Return Format
`IMPLEMENTER_RESULT`: diff summary, new field names + schema doc regen confirmation, the pytest output, the baseline evidence summary, blockers, scope concerns, assumptions.
