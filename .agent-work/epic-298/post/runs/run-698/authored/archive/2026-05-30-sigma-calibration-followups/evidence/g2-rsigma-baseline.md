# G2 baseline: |r/σ| percentiles (promoted bundle)

**Bundle:** `params/gold/runtime_bundles/gold_cycle_260530_042533_2018thru2024`  
**Method:** No-train recompute — load committed checkpoints, rebuild 2024 eval `PairBatch`es from DB + compound priors + `params/retro_truth`, run `_evaluate_module` (full validation pairwise set).  
**Limitation:** Committed `module_diagnostics.json` files predate G2 and do not contain `uncertainty_diagnostics`; baseline is not read from those files. Loader strips removed config key `target_mode` from bundle checkpoints (G1).

| module_name | eval_events | p50 | p90 | p95 | p99 | sigma_mean |
|-------------|------------:|----:|----:|----:|----:|-----------:|
| constructor_quali_power_from_race_weekend | 24 | 0.7551 | 1.7118 | 2.0188 | 2.5250 | 0.2728 |
| constructor_quali_power_from_recent_history | 24 | 0.8037 | 1.9186 | 2.2608 | 3.0837 | 0.1991 |
| constructor_race_power_from_race_weekend | 24 | 0.6504 | 1.7537 | 2.2482 | 3.5256 | 0.1710 |
| constructor_race_power_from_recent_history | 24 | 0.6908 | 1.7514 | 2.1690 | 3.3715 | 0.1996 |
| constructor_race_start_power_from_race_weekend | 24 | 0.6289 | 1.7744 | 2.3232 | 3.4821 | 0.1266 |
| constructor_race_start_power_from_recent_history | 24 | 0.6195 | 1.6995 | 2.1616 | 3.3033 | 0.1352 |
| driver_quali_power_from_race_weekend | 24 | 0.7540 | 1.7906 | 2.1639 | 2.9933 | 0.2501 |
| driver_quali_power_from_recent_history | 24 | 0.7759 | 2.0338 | 2.5397 | 3.3526 | 0.2040 |
| driver_race_power_from_race_weekend | 24 | 0.6460 | 1.8556 | 2.4342 | 3.8773 | 0.1906 |
| driver_race_power_from_recent_history | 24 | 0.6259 | 1.8828 | 2.5159 | 4.0928 | 0.1870 |
| driver_race_start_power_from_race_weekend | 24 | 0.6271 | 1.9559 | 2.8392 | 4.6303 | 0.1196 |
| driver_race_start_power_from_recent_history | 24 | 0.5474 | 1.7261 | 2.4188 | 4.0960 | 0.1351 |

**Notes:** `|r/σ| = |target_mu - mu| / sigma` over all eval pairs (concatenated events). Highest p99 tails: `driver_race_start_power_from_race_weekend` (4.63), `driver_race_power_from_recent_history` (4.09). Script: `.agent-work/sigma-calibration-followups/g2_rsigma_baseline.py`.
