# Gate 6 Evidence: Gold Training Run

## Artifact
`gold_cycle_260526_004033_2018thru2024`  
PR: #287  
Commit: 87db2ff

## Module Metrics (2025 eval)
| Module | log_loss | spearman | events |
|--------|----------|----------|--------|
| constructor_quali_power_from_race_weekend | 0.654 | 0.531 | 447 |
| constructor_quali_power_from_recent_history | 0.623 | 0.700 | 149 |
| constructor_race_power_from_race_weekend | 0.597 | 0.788 | 447 |
| constructor_race_power_from_recent_history | 0.629 | 0.638 | 149 |
| constructor_race_start_power_from_race_weekend | 0.575 | 0.920 | 447 |
| constructor_race_start_power_from_recent_history | 0.579 | 0.916 | 149 |
| driver_quali_power_from_race_weekend | 0.651 | 0.578 | 447 |
| driver_quali_power_from_recent_history | 0.629 | 0.672 | 149 |
| driver_race_power_from_race_weekend | 0.622 | 0.710 | 447 |
| driver_race_power_from_recent_history | 0.621 | 0.717 | 149 |
| driver_race_start_power_from_race_weekend | 0.582 | 0.920 | 447 |
| driver_race_start_power_from_recent_history | 0.585 | 0.918 | 149 |

All log_loss < 0.7 ✓  All spearman > 0.5 ✓  No NaN metrics ✓

## Holdout Mode Coverage (details JSON)
- `same_season_recent`: 6 modules × 5 events (rounds 1-5)
- `short_gap_holdout`: 6 modules × 11 events (≤8 day gap rounds)
- `season_boundary_holdout`: 6 modules × 3 events (rounds 1-3)
- `round_01` through `round_24`: 6 modules each (per-round breakdown)

## Tests: 937 passed, 0 failures

## Committed artifacts
- `params/gold/runtime_bundles/gold_cycle_260526_004033_2018thru2024/` (12 module bundles)
- `params/gold/uncertainty_calibration/unc_cal_260526_004033_2018thru2024.json`
