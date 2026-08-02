# G5 Full Gold Retrain — Sigma Calibration Follow-ups (#303–#306)

**Gate:** G5 | **Date:** 2026-05-30 | **Branch:** `codex/sigma-calibration-followups`

## Settings

| Parameter | Value |
|-----------|-------|
| `student_t_nu` | 4.0 |
| `student_t_nu_sigma` | null (term B uses same ν) |
| `lambda_sigma_nll` | 1.0 |
| `solve_sigma_floor` | 0.05 |
| Report schema | v5 (no `target_mode` in `run_config`) |

Config: `configs/evo/gold_defaults.toml`

## Commands

```bash
py -m src.evo_predictor gold-cycle --config configs/evo/gold_defaults.toml
# exit 0, ~76 min (4554645 ms)

py -m pytest tests/unit/latent_power tests/unit/evo_predictor/test_gold_cycle_config.py -q
# 247 passed

py .agent-work/sigma-calibration-followups/g5_promote_artifacts.py \
  --slug gold_cycle_260530_152746_2018thru2024 \
  --unc-cal-slug unc_cal_260530_152746_2018thru2024

py .agent-work/sigma-calibration-followups/g5_compare_metrics.py \
  --new gold_cycle_260530_152746_2018thru2024
```

Log: `.agent-work/sigma-calibration-followups/evidence/g5-gold-cycle.log`

## New artifacts (promoted)

| Artifact | Path |
|----------|------|
| Gold summary | `reports/evo/gold_cycle_260530_152746_2018thru2024.summary.json` |
| Gold details | `reports/evo/gold_cycle_260530_152746_2018thru2024.details.json` |
| Unc calibration | `params/gold/uncertainty_calibration/unc_cal_260530_152746_2018thru2024.json` |
| Unc diagnostics | `reports/evo/unc_diag_260530_152746_2018thru2024.json` |
| Runtime bundle | `params/gold/runtime_bundles/gold_cycle_260530_152746_2018thru2024/` |
| Sampled manifest | `reports/evo/gold_cycle_260530_152746_2018thru2024.sampled_runtime_manifest.json` |

**Baseline for comparison:** `gold_cycle_260530_042533_2018thru2024` (issue #142 G5, schema v4, same λ=1.0).

## Brier-primary vs baseline (task-pooled)

| Task | Baseline Brier | New Brier | Δ Brier | Verdict |
|------|----------------|-----------|---------|---------|
| quali | 0.22376 | 0.22377 | +1.1e-05 | noise |
| race_start | 0.19457 | 0.19461 | +4.9e-05 | noise |
| race | 0.21295 | 0.21305 | +1.0e-04 | noise |

Material threshold: 0.001. **No Brier regression.**

## Pairwise log-loss (module-level)

Max Δ log-loss ≈ **+0.0012** (`driver_race_power_from_race_weekend`). Seven modules show strictly higher log-loss vs baseline at 1e-6 tolerance; all deltas &lt; 0.0013. Four modules improved. Assessment: **retrain noise**, consistent with issue #142 G5.

## Race-start re-check (#306)

`driver_race_start_power_from_race_weekend` event-level corr(σ_π trace, log_loss):

| Run | Pearson |
|-----|---------|
| Baseline `260530_042533` | −0.397 |
| G5 follow-ups `260530_152746` | −0.055 |

Task-pooled race_start Brier unchanged within noise; corr sign still weak/unstable vs G4 smoke conclusion (**flat_signal_artifact**). **No repo-wide λ change.** Keep `lambda_sigma_nll=1.0`.

Promoted bundle train-time `|r/σ|` percentiles (`driver_race_start_power_from_race_weekend`): p50=0.61, p90=1.76, p95=2.35, p99=4.25, σ_mean=0.12.

## Uncertainty diagnostics summary

| Metric | Baseline unc_diag | New unc_diag |
|--------|-------------------|--------------|
| wrong_sign_uncertainty_error_correlation | 4 | 5 |
| near_zero_uncertainty_error_correlation | 1 | 1 |

## Docs updated

- `docs/adr/0008-retro-delta-supervision.md` — follow-ups #303–#306, schema v5, promoted slug, `student_t_nu_sigma`, `|r/σ|` diagnostics
- `docs/architecture/packets/latent_power.md` — same
- `src/evo_predictor/gold_report_schema.py` — already documents `r_over_sigma_*` (issue #304); no edit required

## Close criteria

- [x] Full gold exit 0
- [x] Brier-primary comparison captured (pass)
- [x] Artifacts promoted
- [x] Docs updated
- [x] Unit tests green
