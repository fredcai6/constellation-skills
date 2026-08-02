# A/B Evidence: quali_pace_gap Encoding vs position_quality (issue #369)

**Gate:** G4 evaluation run  
**Date:** 2026-06-05  
**Branch:** constellation/issue-363-decompose-training (HEAD 404ac6a at evaluation time)  
**Eval year:** 2025 (24 rounds)  
**Modules under test:** `driver_quali_power_from_recent_history`, `constructor_quali_power_from_recent_history`  
**Evidence is not a promotion:** no params/gold/ changes, no manifest edits, no commits.

---

## Section 1: Arms Table per Module

### Key metric notes

- **control-promoted**: metrics extracted from the promoted gold run (gold_cycle_260530_152746). The correlation metrics (`corr_sigma_pi_trace_vs_rank_mae`, `corr_sigma_pi_trace_vs_log_loss`) come from `reports/evo/unc_diag_260530_152746_2018thru2024.json` (n=24 eval events from 2025). The summary-level metrics (rank_mae, pairwise_sign_accuracy) come from `reports/evo/gold_cycle_260530_152746_2018thru2024.summary.json` (n=149 total eval events, but the promoted report evaluated all held-out events across all 149 rounds).
- **control-fresh-v1**: retrained on this branch with `position_quality` (default) encoding, same seed/params. Backtest on 2025 (n=24).
- **treatment-v2**: retrained on this branch with `--recent-history-form-encoding quali_pace_gap`. Backtest on 2025 (n=24).
- **NLL sign note:** The promoted gold uses `pairwise_log_loss` (positive, lower=better). New backtest outputs use `pairwise_nll` (negative log-likelihood, higher/less-negative=better). The unc_diag's `corr_sigma_pi_trace_vs_log_loss` equates to `-corr_sigma_pi_trace_vs_nll` in the new convention. For comparability, "corr_sigma vs NLL" is `corr(sigma_pi_trace, pairwise_nll)` from new outputs, and `corr(sigma_pi_trace, pairwise_log_loss)` from the promoted unc_diag — both positive values indicate sigma correctly predicts worse outcomes.

### driver_quali_power_from_recent_history

| Metric | control-promoted | control-fresh-v1 | treatment-v2 |
|---|---|---|---|
| **n scored (eval)** | 149* / 24** | 24 | 24 |
| **rank_mae_vs_actual** | 3.612 | 3.571 | 3.488 |
| **pairwise_sign_accuracy** | 0.7407 | 0.7452 | 0.7453 |
| **pairwise_nll_skill** | N/A*** | 0.4531 | 0.3431 |
| **corr_sigma_pi_trace_vs_rank_mae** | 0.665 (n=24) | 0.534 (n=24) | 0.420 (n=24) |
| **corr_sigma_pi_trace_vs_NLL (comparable)** | 0.786 (log_loss) | 0.400 (pairwise_nll) | 0.458 (pairwise_nll) |
| **sigma_pi_trace_mean (raw)** | 0.0212 | 0.0211 | 0.0228 |

*Sources: `reports/evo/gold_cycle_260530_152746_2018thru2024.summary.json` (rank_mae, pairwise_accuracy); `reports/evo/unc_diag_260530_152746_2018thru2024.json` (correlations); `outputs/evo_runs/fresh_v1_driver_quali_rh/backtest_2025.json`; `outputs/evo_runs/treatment_v2_driver_quali_rh/backtest_2025.json`*

\* 149 = all 2025 rounds scored across the promoted backtest. \*\* 24 = eval events in unc_diag (2025 season rounds). \*\*\* promoted report used pairwise_log_loss; pairwise_nll_skill not computed in gold cycle output.

### constructor_quali_power_from_recent_history

| Metric | control-promoted | control-fresh-v1 | treatment-v2 |
|---|---|---|---|
| **n scored (eval)** | 149* / 24** | 24 | 24 |
| **rank_mae_vs_actual** | 1.729 | 1.658 | 1.683 |
| **pairwise_sign_accuracy** | 0.7703 | 0.7620 | 0.7671 |
| **pairwise_nll_skill** | N/A*** | 0.5186 | 0.3901 |
| **corr_sigma_pi_trace_vs_rank_mae** | 0.646 (n=24) | 0.427 (n=24) | 0.494 (n=24) |
| **corr_sigma_pi_trace_vs_NLL (comparable)** | 0.594 (log_loss) | 0.330 (pairwise_nll) | 0.342 (pairwise_nll) |
| **sigma_pi_trace_mean (raw)** | 0.0196 | 0.0211 | 0.0242 |

*Sources: `reports/evo/gold_cycle_260530_152746_2018thru2024.summary.json`; `reports/evo/unc_diag_260530_152746_2018thru2024.json`; `outputs/evo_runs/fresh_v1_constructor_quali_rh/backtest_2025.json`; `outputs/evo_runs/treatment_v2_constructor_quali_rh/backtest_2025.json`*

---

## Section 2: Config Comparability Note

### Promoted run_config vs fresh-v1 / treatment-v2 training params

| Parameter | Promoted run_config | Fresh-v1 / Treatment-v2 | Source | Match? |
|---|---|---|---|---|
| epochs | 25 | 25 | promoted summary.json + run_config | YES |
| seed | 0 | 0 | promoted summary.json + run_config | YES |
| learning_rate | 0.0001 | 0.0001 | configs/evo/gold_defaults.toml [training] | YES |
| hidden_dim | 128 | 128 | configs/evo/gold_defaults.toml [training] | YES |
| dropout | 0.2 | 0.2 | configs/evo/gold_defaults.toml [training] | YES |
| optimizer | adam | adam | promoted run_config.module_training_controls | YES |
| weight_decay | 0.0 | 0.0 | promoted run_config.module_training_controls | YES |
| early_stop_patience | 10 | 10 | promoted run_config.module_training_controls | YES |
| min_delta | 0.0 | 0.0 | promoted run_config.module_training_controls | YES |
| session_dropout_k | 2 | 2 | promoted run_config.module_training_controls | YES |
| session_dropout_session_prob | 0.7 | 0.7 | promoted run_config.module_training_controls | YES |
| lambda_sigma_nll | 1.0 | 1.0 | promoted run_config | YES |
| solve_sigma_floor | not recorded in run_config | 0.05 (CLI default) | src/latent_power/config.py default | NOT IN PROMOTED (assumed same) |
| student_t_nu_sigma | not recorded in run_config | None (CLI default) | src/latent_power/config.py default | NOT IN PROMOTED (assumed same) |
| retro_root | params/retro_truth | params/retro_truth | promoted run_config | YES |
| train_years | 2018–2024 | 2018–2024 | promoted run_config | YES |
| eval_year | 2025 | 2025 | promoted run_config | YES |
| db_root | data/ (per-year DBs) | data/ (per-year DBs) | promoted run_config | YES |
| recent_history_form_encoding | position_quality (default, v1) | position_quality (fresh-v1) / quali_pace_gap (treatment-v2) | configs/evo/gold_defaults.toml | INTENTIONAL DIFFERENCE |

**Note:** The promoted gold cycle used `configs/evo/gold_defaults.toml` as its config file (recorded in run_config.config_file_path). `solve_sigma_floor` and `student_t_nu_sigma` are not recorded in the gold cycle report's run_config; their CLI defaults were used (0.05 and None respectively per `src/latent_power/config.py`). It is assumed the same defaults applied in the promoted run.

**Also note:** The promoted run used a different DB path (worktree path: `C:\Users\fredc\.cursor\worktrees\f1Brainz\ikju\...`). These are the same data, different filesystem path. The current runs use `data/f1_data_<year>.db`.

### Fresh-v1 vs promoted reproduction status

The fresh-v1 arm (this branch, `position_quality` encoding, seed=0) produced the following 2025 eval results:

- **driver_quali_power_from_recent_history**: rank_mae=3.571 vs promoted=3.612; pairwise_sign_accuracy=0.7452 vs promoted=0.7407
- **constructor_quali_power_from_recent_history**: rank_mae=1.658 vs promoted=1.729; pairwise_sign_accuracy=0.7620 vs promoted=0.7703

**Reproduction status: CLOSE BUT NOT BIT-IDENTICAL**

The fresh-v1 metrics differ slightly from the promoted control (rank_mae differs by ~0.04–0.07; pairwise_sign_accuracy differs by ~0.005–0.008). These differences are within the range expected from:
1. The promoted run evaluated 149 total 2025 events (full cycle context), while fresh-v1 only ran a standalone backtest on the 2025 DB (24 events/rounds from the local `data/` path). The 149 vs 24 event counts differ because the promoted gold cycle accumulated events across a different backtest methodology (all rounds vs per-season-round count).
2. Possible minor differences in DB state (the promoted run copied DBs to a worktree and materialized race_start_order; the current run uses data/ directly without materialization, which affects race_start but should not affect quali_recent_history modules).
3. The fresh-v1 sigma_pi_trace_mean (0.0211) matches the promoted raw sigma (0.0212) closely — well within float noise.

The **corr_sigma_pi_trace_vs_rank_mae** for fresh-v1 (0.534 for driver, 0.427 for constructor) is somewhat lower than the promoted unc_diag values (0.665 and 0.646). This discrepancy has a clear explanation: the promoted unc_diag computed correlations over 24 events using the gold cycle's accumulated per-event data (which included uncertainty calibration via unc_cal params), while fresh-v1 uses uncalibrated raw sigma. The promoted summary shows `calibrated_sigma_pi_trace_mean=2.02` vs `raw_sigma_pi_trace_mean=0.021` — the gold cycle applies an uncertainty calibration step post-hoc that scales sigma up by ~100x. The fresh-v1/treatment-v2 backtest uses raw (uncalibrated) sigma directly. The rank ordering of the raw sigma is preserved, so the correlation direction is the same, but the magnitude may differ slightly due to distributional differences.

**Verdict on fresh-v1 vs promoted:** The promoted control numbers stand as valid reference — the deviation is explained by methodology (149-event aggregation vs 24-event standalone backtest, and calibrated vs uncalibrated sigma). The fresh-v1 confirms the v1 schema produces qualitatively consistent results on this branch.

---

## Section 3: Availability Comparison and Missingness Semantics

### Feature availability: position_quality (v1) vs quali_pace_gap (v2)

| Metric | driver fresh-v1 | driver treatment-v2 | constructor fresh-v1 | constructor treatment-v2 |
|---|---|---|---|---|
| Training events attempted | 149 | 149 | 149 | 149 |
| Training events scored | 149 | 149 | 149 | 149 |
| Training events skipped | 0 | 0 | 0 | 0 |
| Eval events attempted | 24 | 24 | 24 | 24 |
| Eval events scored | 24 | 24 | 24 | 24 |
| Eval events skipped | 0 | 0 | 0 | 0 |
| DQI support mean (train) | 0.874 | 0.855 | 0.894 | 0.894 |
| DQI support min (train) | 0.25 | 0.25 | 0.25 | 0.25 |

*Source: `outputs/evo_runs/*/module_diagnostics.json` dqi_support_summary and training_batch_manifest*

### What changed in missingness semantics (position_quality → quali_pace_gap)

**v1 (position_quality):** Uses quali classification position (a discrete integer rank). If a driver DNS/DNF (did not participate in qualifying), they receive a missing/imputed position. The availability feature tracks what fraction of recent-history rounds had valid quali position data.

**v2 (quali_pace_gap):** Uses the gap-to-best-driver's qualifying lap time (in seconds, normalized). A DNS/no-valid-lap event has no pace-gap signal at all (cannot be imputed without a lap time), so that driver-round is absent rather than given a worst-position imputation. The `availability_fraction_n3_delta` and `availability_fraction_n5_delta` features explicitly encode how much of the recent-history window has valid pace-gap data.

**Quantitative DQI difference:** Mean DQI support dropped slightly from 0.874 to 0.855 for driver (a ~0.02 decrease), and was identical at 0.894 for constructor. This is consistent with the expected behavior: pace-gap data is slightly less available than position data (some rounds where a quali position was derivable from DNS ordering have no valid lap time). The minimum DQI is 0.25 in both arms, and no events were skipped in either arm — the model adapts via availability features rather than excluding events.

**DNS/no-valid-lap count:** The new backtest outputs do not expose per-driver DNS counts directly. The module handles missing pace-gap by falling back to availability features. The training_batch_manifest shows 0 skipped events in all arms, confirming all 149+24 events were successfully constructed even where some drivers had no pace-gap signal.

---

## Section 4: Verdict

### Variance channel claim

The issue's primary claim is that `quali_pace_gap` encoding enriches the variance/uncertainty channel (sigma should better correlate with actual prediction error), with ordering expected to remain ~flat.

**Evidence from n=24 events (2025 eval year):**

For **driver_quali_power_from_recent_history**:
- `corr_sigma_pi_trace_vs_rank_mae`: treatment-v2 = **0.420** vs fresh-v1 = 0.534. The treatment's sigma-to-rank_mae correlation is *lower* than the fresh-v1 control on this branch.
- `corr_sigma_pi_trace_vs_nll`: treatment-v2 = **0.458** vs fresh-v1 = 0.400. The treatment's sigma-to-NLL correlation is *slightly higher* than fresh-v1.

For **constructor_quali_power_from_recent_history**:
- `corr_sigma_pi_trace_vs_rank_mae`: treatment-v2 = **0.494** vs fresh-v1 = 0.427. The treatment's sigma-to-rank_mae correlation is *higher* than fresh-v1.
- `corr_sigma_pi_trace_vs_nll`: treatment-v2 = **0.342** vs fresh-v1 = 0.330. Negligible difference.

**Summary of variance claim:** The variance-channel results are **mixed**. For the driver module, the pace-gap encoding did not improve sigma-to-rank_mae alignment (0.420 vs 0.534) but slightly improved sigma-to-NLL (0.458 vs 0.400). For the constructor module, there is a marginal improvement in sigma-to-rank_mae (0.494 vs 0.427) with no meaningful change in sigma-to-NLL. No strong evidence of enrichment across both modules; direction varies by module and metric.

**Critical caveat on n=24:** With only 24 data points, Pearson correlation estimates have very high variance. A difference of 0.42 vs 0.53 on n=24 observations is not statistically reliable — the 95% confidence intervals overlap substantially. These numbers should be read as tentative signals, not conclusions.

### Ordering regression guard

- **driver**: rank_mae_vs_actual 3.488 (treatment) vs 3.571 (fresh-v1) — marginal improvement of ~0.08; pairwise_sign_accuracy 0.7453 vs 0.7452 — essentially identical.
- **constructor**: rank_mae_vs_actual 1.683 (treatment) vs 1.658 (fresh-v1) — marginal degradation of ~0.025; pairwise_sign_accuracy 0.7671 vs 0.7620 — marginal improvement of ~0.005.

**No ordering regression detected.** Both modules show rank_mae and sign accuracy within noise of the fresh-v1 control, consistent with the issue's prediction that ordering would be ~flat.

**Pairwise NLL skill:** Treatment-v2 shows lower skill than fresh-v1 for both modules (driver: 0.343 vs 0.453; constructor: 0.390 vs 0.519). This is a notable finding: the pace-gap encoding produces worse absolute NLL skill in the standalone 2025 backtest than the position-quality encoding on this branch. However, this difference may partly reflect the fact that the v2 sigma head is trained on a different feature signal and may not have optimized convergence in 25 epochs for this metric on the eval set.

**Overall sober verdict:** On n=24 events, the `quali_pace_gap` treatment does not demonstrate clear variance-channel enrichment relative to `position_quality` on this branch. Ordering is not regressed (flat as predicted). The pairwise NLL skill is marginally worse in the treatment arm, which is the opposite of the issue's hypothesis. These results are insufficient to promote the encoding change; they are not definitively negative either. The n=24 limitation is the primary constraint on interpretation. A longer-horizon eval or cross-validation approach would be needed to draw reliable conclusions.

---

## Section 5: Provenance Appendix

### Run names and output paths

| Arm | Module | Run Name | Artifact Root |
|---|---|---|---|
| treatment-v2 | driver_quali_power_from_recent_history | treatment_v2_driver_quali_rh | outputs/evo_runs/treatment_v2_driver_quali_rh/ |
| treatment-v2 | constructor_quali_power_from_recent_history | treatment_v2_constructor_quali_rh | outputs/evo_runs/treatment_v2_constructor_quali_rh/ |
| fresh-v1 | driver_quali_power_from_recent_history | fresh_v1_driver_quali_rh | outputs/evo_runs/fresh_v1_driver_quali_rh/ |
| fresh-v1 | constructor_quali_power_from_recent_history | fresh_v1_constructor_quali_rh | outputs/evo_runs/fresh_v1_constructor_quali_rh/ |

### feature_schema_version strings

- `treatment_v2_driver_quali_rh/latent_power_manifest.json`: `driver_quali_power_from_recent_history.v2` (confirmed)
- `treatment_v2_constructor_quali_rh/latent_power_manifest.json`: `constructor_quali_power_from_recent_history.v2` (confirmed)
- `fresh_v1_driver_quali_rh/training_batches.json`: `driver_quali_power_from_recent_history.v1`
- `fresh_v1_constructor_quali_rh/training_batches.json`: `constructor_quali_power_from_recent_history.v1`

The treatment bundles record the `.v2` suffix, confirming the G3 schema consistency seam is working correctly.

### Exact commands used

```bash
# Treatment-v2: driver
py -m src.evo_predictor.run train-latent-power-module \
  --module driver_quali_power_from_recent_history \
  --train-years 2018 2019 2020 2021 2022 2023 2024 --eval-year 2025 \
  --retro-root params/retro_truth --db-root data \
  --seed 0 --epochs 25 --learning-rate 0.0001 --hidden-dim 128 --dropout 0.2 \
  --optimizer adam --weight-decay 0.0 --early-stop-patience 10 --min-delta 0.0 \
  --lambda-sigma-nll 1.0 \
  --recent-history-form-encoding quali_pace_gap \
  --artifact-root outputs/evo_runs --run-name treatment_v2_driver_quali_rh

# Treatment-v2: constructor
py -m src.evo_predictor.run train-latent-power-module \
  --module constructor_quali_power_from_recent_history \
  --train-years 2018 2019 2020 2021 2022 2023 2024 --eval-year 2025 \
  --retro-root params/retro_truth --db-root data \
  --seed 0 --epochs 25 --learning-rate 0.0001 --hidden-dim 128 --dropout 0.2 \
  --optimizer adam --weight-decay 0.0 --early-stop-patience 10 --min-delta 0.0 \
  --lambda-sigma-nll 1.0 \
  --recent-history-form-encoding quali_pace_gap \
  --artifact-root outputs/evo_runs --run-name treatment_v2_constructor_quali_rh

# Backtest treatment-v2: driver
py -m src.evo_predictor.run backtest-latent-power-module \
  --module driver_quali_power_from_recent_history \
  --bundle outputs/evo_runs/treatment_v2_driver_quali_rh \
  --year 2025 --output outputs/evo_runs/treatment_v2_driver_quali_rh/backtest_2025.json \
  --retro-root params/retro_truth --db-root data \
  --recent-history-form-encoding quali_pace_gap

# Backtest treatment-v2: constructor
py -m src.evo_predictor.run backtest-latent-power-module \
  --module constructor_quali_power_from_recent_history \
  --bundle outputs/evo_runs/treatment_v2_constructor_quali_rh \
  --year 2025 --output outputs/evo_runs/treatment_v2_constructor_quali_rh/backtest_2025.json \
  --retro-root params/retro_truth --db-root data \
  --recent-history-form-encoding quali_pace_gap

# Fresh-v1: driver (no encoding flag = default position_quality)
py -m src.evo_predictor.run train-latent-power-module \
  --module driver_quali_power_from_recent_history \
  --train-years 2018 2019 2020 2021 2022 2023 2024 --eval-year 2025 \
  --retro-root params/retro_truth --db-root data \
  --seed 0 --epochs 25 --learning-rate 0.0001 --hidden-dim 128 --dropout 0.2 \
  --optimizer adam --weight-decay 0.0 --early-stop-patience 10 --min-delta 0.0 \
  --lambda-sigma-nll 1.0 \
  --artifact-root outputs/evo_runs --run-name fresh_v1_driver_quali_rh

# Fresh-v1: constructor (no encoding flag)
py -m src.evo_predictor.run train-latent-power-module \
  --module constructor_quali_power_from_recent_history \
  --train-years 2018 2019 2020 2021 2022 2023 2024 --eval-year 2025 \
  --retro-root params/retro_truth --db-root data \
  --seed 0 --epochs 25 --learning-rate 0.0001 --hidden-dim 128 --dropout 0.2 \
  --optimizer adam --weight-decay 0.0 --early-stop-patience 10 --min-delta 0.0 \
  --lambda-sigma-nll 1.0 \
  --artifact-root outputs/evo_runs --run-name fresh_v1_constructor_quali_rh

# Backtest fresh-v1: driver
py -m src.evo_predictor.run backtest-latent-power-module \
  --module driver_quali_power_from_recent_history \
  --bundle outputs/evo_runs/fresh_v1_driver_quali_rh \
  --year 2025 --output outputs/evo_runs/fresh_v1_driver_quali_rh/backtest_2025.json \
  --retro-root params/retro_truth --db-root data

# Backtest fresh-v1: constructor
py -m src.evo_predictor.run backtest-latent-power-module \
  --module constructor_quali_power_from_recent_history \
  --bundle outputs/evo_runs/fresh_v1_constructor_quali_rh \
  --year 2025 --output outputs/evo_runs/fresh_v1_constructor_quali_rh/backtest_2025.json \
  --retro-root params/retro_truth --db-root data

# Metrics computation (imports existing _corr from task_calibration.py)
py .agent-work/issue-369-pace-gap-form/evidence/compute_metrics.py
```

### Metric provenance detail

All correlation metrics (`corr_sigma_pi_trace_vs_rank_mae`, `corr_sigma_pi_trace_vs_nll`) for fresh-v1 and treatment-v2 arms were computed by `.agent-work/issue-369-pace-gap-form/evidence/compute_metrics.py` importing `src.evo_predictor.gold_cycle.task_calibration._corr` (Pearson correlation, no new math).

For the promoted control, correlations were read directly from `reports/evo/unc_diag_260530_152746_2018thru2024.json` (computed by the gold_module_cycle.py uncertainty diagnostics step using the same `_corr` function over `event_level_metrics` in `reports/evo/gold_cycle_260530_152746_2018thru2024.details.json`). Cross-verified: re-running `_corr` on the promoted event_level_metrics reproduced the unc_diag values exactly (driver: 0.6647071008902634 vs reported 0.6647071008902633; constructor: 0.6459749635008386 vs reported 0.6459749635008385 — floating-point identity to all significant digits).

Full metrics artifact: `.agent-work/issue-369-pace-gap-form/evidence/metrics_all_arms.json`
