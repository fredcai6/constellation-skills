# cmdr-413 Findings: qs_compound_beta_regime manifest plumbing

**Date:** 2026-06-11  
**Issue:** #413  
**Branch:** issue-413-beta-regime-manifest  
**Verdict:** Shipped — PR pending

---

## Problem Confirmed

The `qs_compound_beta_regime` flag was fully plumbed through the TRAINING path but absent from the SERVING path. At runtime, prediction-time features always used `"race"` regime normalization regardless of how the gold cycle was trained.

**Gap trace:**
- `GoldCycleDataConfig.qs_compound_beta_regime` → training path: fully connected through `runner_support.py` → `module_training_orchestration.py` → `data_adapter/_build.py._resolve_quali_sim_normalizer`
- `SampledRuntimeConfig` in `pipeline_manifest_v4.py`: NO `qs_compound_beta_regime` field
- `assemble_sampled_runtime_manifest`: did not emit the field to JSON
- `_run_sampled_backtest_phase` in `runner.py`: did not pass the field when calling `cmd_assemble`
- `build_sampled_runtime_features` in `data_adapter/_helpers.py`: did not pass `qs_compound_beta_regime` to `build_race_features`
- `SampledEvoRuntime.predict`: no awareness of the flag

No current skew exists (default is `"race"` everywhere today), confirmed by the architecture map note from #380.

---

## Changes Made

### 1. `src/evo_predictor/pipeline_manifest_v4.py`
- Added `DEFAULT_QS_COMPOUND_BETA_REGIME = "race"` named constant
- Added `_VALID_QS_COMPOUND_BETA_REGIMES = ("race", "push")` private sentinel
- Added `qs_compound_beta_regime: str = DEFAULT_QS_COMPOUND_BETA_REGIME` field to `SampledRuntimeConfig` with `__post_init__` validation
- `sampled_runtime_config_from_dict` reads from `runtime_payload` with fallback to `DEFAULT_QS_COMPOUND_BETA_REGIME` (named constant, not inline `"race"` string)
- Exported `DEFAULT_QS_COMPOUND_BETA_REGIME` in `__all__`

### 2. `src/evo_predictor/sampled_runtime_manifest_assembly.py`
- Added `qs_compound_beta_regime: str = DEFAULT_QS_COMPOUND_BETA_REGIME` parameter
- Emits `"qs_compound_beta_regime": str(qs_compound_beta_regime)` to `runtime` block in JSON

### 3. `src/evo_predictor/gold_cycle/runner.py`
- `_run_sampled_backtest_phase` passes `qs_compound_beta_regime=config.data.qs_compound_beta_regime` to `cmd_assemble`

### 4. `src/evo_predictor/data_adapter/_helpers.py`
- `build_sampled_runtime_features` adds `qs_compound_beta_regime: str = "race"` parameter
- Forwards it to `build_race_features` (which already accepted it)

### 5. `src/evo_predictor/sampled_runtime.py`
- `SampledEvoRuntime` adds `qs_compound_beta_regime: str = DEFAULT_QS_COMPOUND_BETA_REGIME` field
- `predict()` passes `qs_compound_beta_regime=self.qs_compound_beta_regime` to `build_sampled_runtime_features`
- `sampled_runtime_from_config` threads `config.qs_compound_beta_regime` into `SampledEvoRuntime`

### 6. `src/evo_predictor/run.py`
- CLI `assemble-sampled-runtime-manifest` subcommand gains `--qs-compound-beta-regime` argparse arg
- `cmd_assemble_sampled_runtime_manifest` passes it through with `getattr` fallback

### 7. `tests/unit/evo_predictor/test_beta_regime_manifest.py` (NEW)
Five tests proving the guard behavior:
1. push→push flow through manifest into `build_race_features` (monkeypatched capture)
2. Absent manifest key → `DEFAULT_QS_COMPOUND_BETA_REGIME` (asserted against constant, not string)
3. `assemble_sampled_runtime_manifest` with push writes push to JSON + round-trips
4. `SampledEvoRuntime.predict` passes push to `build_sampled_runtime_features` (short-circuit + capture)
5. Invalid regime value rejected on parse with `ValueError`

---

## Evidence

- `py -m pytest tests/unit/evo_predictor/test_pipeline_manifest_v4.py tests/unit/evo_predictor/test_sampled_runtime_manifest_assembly.py tests/unit/evo_predictor/test_sampled_runtime_data_adapter.py tests/unit/evo_predictor/test_beta_regime_manifest.py -x -q` → **38 passed**
- `py -m pytest tests/unit/evo_predictor/ -x -q` → **1739 passed, 0 failures**
- `py -m src.utils.simplification_limits --paths src/... (6 files)` → **PASS**

---

## Guard Behavior

| Scenario | Behavior |
|---|---|
| Manifest has `qs_compound_beta_regime: "push"` | `SampledRuntimeConfig.qs_compound_beta_regime == "push"` → runtime uses push normalizer |
| Manifest absent / no key | Resolves to `DEFAULT_QS_COMPOUND_BETA_REGIME` (`"race"`), named constant |
| Gold cycle trained with push | Manifest assembly emits `"push"`, runtime reads it |
| Legacy manifest (no field) | Falls back to named default, backward compatible |
| Invalid value in manifest | `ValueError` on parse, explicit error message |

---

## Collision Check with #410 (sibling Wave-1 issue)

Issue #410 is changing the gold β fit to pooled multi-season in `compound_push_regime.py` — it changes emitted β VALUES, not schema or plumbing. This issue (#413) changes manifest schema and serving plumbing, not the β constants. No collision in the files touched:
- #413 touches: `pipeline_manifest_v4.py`, `sampled_runtime_manifest_assembly.py`, `sampled_runtime.py`, `data_adapter/_helpers.py`, `gold_cycle/runner.py`, `run.py`
- #410 touches: `compound_push_regime.py` (and possibly `compound_prior/` solver files)

No shared lines in the same files. Admiral can merge independently.

---

## Triage Candidates

- **`run.py` CLI default uses inline `"race"` string literal** in `--qs-compound-beta-regime` default arg (minor style inconsistency vs named constant) — cosmetic, not a constraint violation. Low priority.
- **Schema documentation update**: The manifest schema is documented in `docs/report_schemas/` and packet prose. The `runtime` block's new `qs_compound_beta_regime` field could be added there. Not done in this PR (it was not in the explicit scope); route as a follow-up doc touch if needed.

---

## Workflow Feedback

The issue was well-specified with clear prior verdicts and a precise honest-null clause. The "four plumbing points" framing made the scope immediately clear. The only improvisation: `run.py` wasn't in the original allowed scope but was a necessary link in the CLI chain; added transparently with `getattr` fallback pattern consistent with the existing `quali_pace_anchor_*` args pattern.
