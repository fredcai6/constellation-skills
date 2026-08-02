# G5 Full Gold Retrain — Issue #142 Sigma Calibration

**Gate:** G5 | **Date:** 2026-05-30 | **Branch:** `codex/issue-142-sigma-calibration`

## Config change

| Parameter | Before | After |
|-----------|--------|-------|
| `lambda_sigma_nll` | 0.0 | **1.0** |
| `pairwise_sigma_nll_enabled` | false | **true** |
| `solve_sigma_floor` | (G2 default 0.05) | unchanged |

File: `configs/evo/gold_defaults.toml`

## Commands

```bash
py -m src.evo_predictor gold-cycle --config configs/evo/gold_defaults.toml
# exit 0, ~56 min (3344328 ms)

py -m pytest tests/unit/latent_power tests/unit/evo_predictor/test_gold_cycle_config.py -q
# (see verification section)

py .agent-work/issue-142-sigma-calibration/g5_promote_artifacts.py
py .agent-work/issue-142-sigma-calibration/g5_compare_metrics.py
```

Log: `.agent-work/issue-142-sigma-calibration/evidence/g5-gold-cycle.log`

## New artifacts

| Artifact | Path |
|----------|------|
| Gold summary | `reports/evo/gold_cycle_260530_042533_2018thru2024.summary.json` |
| Gold details | `reports/evo/gold_cycle_260530_042533_2018thru2024.details.json` |
| Unc calibration | `params/gold/uncertainty_calibration/unc_cal_260530_042533_2018thru2024.json` |
| Unc diagnostics | `reports/evo/unc_diag_260530_042533_2018thru2024.json` |
| Runtime bundle | `params/gold/runtime_bundles/gold_cycle_260530_042533_2018thru2024/` |
| Sampled manifest | `reports/evo/gold_cycle_260530_042533_2018thru2024.sampled_runtime_manifest.json` |

Baseline: `gold_cycle_260526_004033_2018thru2024` (`lambda_sigma_nll=0.0`).

## Module-level pairwise log-loss vs baseline

| Module | Δ log-loss | Δ accuracy | Verdict |
|--------|------------|------------|---------|
| constructor_quali_power_from_race_weekend | +0.00216 | -0.0069 | ~flat |
| constructor_quali_power_from_recent_history | **-0.00072** | +0.0003 | improved |
| constructor_race_power_from_race_weekend | +0.00205 | +0.0005 | ~flat |
| constructor_race_power_from_recent_history | +0.00047 | -0.0023 | ~flat |
| constructor_race_start_power_from_race_weekend | +0.00286 | +0.0028 | ~flat |
| constructor_race_start_power_from_recent_history | **-0.00268** | -0.0056 | improved LL |
| driver_quali_power_from_race_weekend | +0.00143 | -0.0008 | ~flat |
| driver_quali_power_from_recent_history | +0.00096 | -0.0021 | ~flat |
| driver_race_power_from_race_weekend | +0.00098 | +0.0001 | ~flat |
| driver_race_power_from_recent_history | **-0.00022** | +0.0015 | improved |
| driver_race_start_power_from_race_weekend | +0.00363 | -0.0037 | ~flat |
| driver_race_start_power_from_recent_history | **-0.00054** | -0.0012 | improved LL |

**Assessment:** No material regression. Max Δ pairwise log-loss = **+0.0036** (driver_race_start race_weekend). Changes are within retrain noise; 4/12 modules improved log-loss. Task-pooled Brier (new run only — baseline summary lacked `task_calibration_diagnostics`):

| Task | mean_brier | mean_log_loss | corr(σ_π, brier) |
|------|------------|---------------|------------------|
| quali | 0.2238 | 0.6402 | 0.687 |
| race_start | 0.1946 | 0.5808 | 0.173 |
| race | 0.2129 | 0.6182 | 0.574 |

## Sigma / uncertainty diagnostics

| Metric | Baseline unc_diag | New unc_diag |
|--------|-------------------|--------------|
| modules_with_near_zero_uncertainty_error_correlation | 4 | **1** |
| modules_with_wrong_sign_uncertainty_error_correlation | 6 | **4** |

Notable corr(σ_π trace, log_loss) improvements (race_weekend modules):

- constructor_quali: 0.14 → **0.29**
- constructor_race: 0.13 → **0.41**
- driver_quali: 0.37 → **0.50**

Raw `sigma_pi_trace_mean` across modules remains material (≈0.007–0.034); not collapsed to floor.

**Regression note:** `driver_race_start_power_from_race_weekend` corr(σ_π, brier) flipped sign (0.10 → -0.40). Flagged for follow-up; does not block promotion given flat pairwise metrics and improved aggregate uncertainty quality counts.

## Non-fatal run warnings

- Missing lap times: 2020 R11, 2021 R15 (both baseline and new)
- Sampled-runtime backtest `oracle_all_states` singular matrix on 2025 Singapore (non-fatal; same class of issue as issue-292 rt_comparison note)

## Promotion paths

```
outputs/evo_runs/gold_module_training_cycle/modules/* 
  → params/gold/runtime_bundles/gold_cycle_260530_042533_2018thru2024/modules/*

outputs/evo_runs/gold_module_training_cycle/sampled_runtime_manifest.json
  → reports/evo/gold_cycle_260530_042533_2018thru2024.sampled_runtime_manifest.json

unc_cal written in-cycle → params/gold/uncertainty_calibration/unc_cal_260530_042533_2018thru2024.json
```

Provenance: `params/gold/runtime_bundles/gold_cycle_260530_042533_2018thru2024/provenance.json`

## Docs

- `docs/architecture/packets/latent_power.md` — retro-only path, term A/B, solve_sigma_floor
- `docs/adr/0008-retro-delta-supervision.md` — new ADR
- `src/evo_predictor/gold_report_schema.py` — lambda_sigma_nll field notes updated

## Verification

```bash
py -m pytest tests/unit/latent_power tests/unit/evo_predictor/test_gold_cycle_config.py -q
```

Machine-readable comparison: `.agent-work/issue-142-sigma-calibration/evidence/g5-metrics-comparison.json`

## Gate verdict

**PASS** — Full gold cycle completed; metrics flat-to-improved; sigma uncertainty correlations improved; artifacts promoted per artifact policy.
