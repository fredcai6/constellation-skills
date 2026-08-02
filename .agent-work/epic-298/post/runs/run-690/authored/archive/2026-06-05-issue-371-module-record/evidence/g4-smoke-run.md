# G4 Smoke Run Evidence

## Command

```
py -m src.evo_predictor.run gold-cycle \
  --config .agent-work/issue-371-module-record/evidence/g4_smoke_config.toml \
  --max-rounds-per-year 1
```

Run from repo root: `C:\Programs\f1Brainz\.claude\worktrees\issue-371-module-record`

Stdout/stderr redirected to: `.agent-work/issue-371-module-record/evidence/g4_smoke_run.log`

## Wall-clock Duration

Start: 16:40:06 (from first log timestamp)
End: ~16:41:43 (Python process exit, last log line at 16:41:37)
Duration: approximately **97 seconds** (~1 min 37 s)

## Grouped .record.* Listing

All three output dir families are populated. Counts: 12 modules per dir family
(24 pairs of .record.npz + .record.json).

### backtests/ (mains — 12 modules)

```
smoke_output/backtests/constructor_quali_power_from_race_weekend.record.json
smoke_output/backtests/constructor_quali_power_from_race_weekend.record.npz
smoke_output/backtests/constructor_quali_power_from_recent_history.record.json
smoke_output/backtests/constructor_quali_power_from_recent_history.record.npz
smoke_output/backtests/constructor_race_power_from_race_weekend.record.json
smoke_output/backtests/constructor_race_power_from_race_weekend.record.npz
smoke_output/backtests/constructor_race_power_from_recent_history.record.json
smoke_output/backtests/constructor_race_power_from_recent_history.record.npz
smoke_output/backtests/constructor_race_start_power_from_race_weekend.record.json
smoke_output/backtests/constructor_race_start_power_from_race_weekend.record.npz
smoke_output/backtests/constructor_race_start_power_from_recent_history.record.json
smoke_output/backtests/constructor_race_start_power_from_recent_history.record.npz
smoke_output/backtests/driver_quali_power_from_race_weekend.record.json
smoke_output/backtests/driver_quali_power_from_race_weekend.record.npz
smoke_output/backtests/driver_quali_power_from_recent_history.record.json
smoke_output/backtests/driver_quali_power_from_recent_history.record.npz
smoke_output/backtests/driver_race_power_from_race_weekend.record.json
smoke_output/backtests/driver_race_power_from_race_weekend.record.npz
smoke_output/backtests/driver_race_power_from_recent_history.record.json
smoke_output/backtests/driver_race_power_from_recent_history.record.npz
smoke_output/backtests/driver_race_start_power_from_race_weekend.record.json
smoke_output/backtests/driver_race_start_power_from_race_weekend.record.npz
smoke_output/backtests/driver_race_start_power_from_recent_history.record.json
smoke_output/backtests/driver_race_start_power_from_recent_history.record.npz
```

### loso_folds/heldout_2022/backtests/ (12 modules)

```
smoke_output/loso_folds/heldout_2022/backtests/constructor_quali_power_from_race_weekend.record.json
smoke_output/loso_folds/heldout_2022/backtests/constructor_quali_power_from_race_weekend.record.npz
smoke_output/loso_folds/heldout_2022/backtests/constructor_quali_power_from_recent_history.record.json
smoke_output/loso_folds/heldout_2022/backtests/constructor_quali_power_from_recent_history.record.npz
smoke_output/loso_folds/heldout_2022/backtests/constructor_race_power_from_race_weekend.record.json
smoke_output/loso_folds/heldout_2022/backtests/constructor_race_power_from_race_weekend.record.npz
smoke_output/loso_folds/heldout_2022/backtests/constructor_race_power_from_recent_history.record.json
smoke_output/loso_folds/heldout_2022/backtests/constructor_race_power_from_recent_history.record.npz
smoke_output/loso_folds/heldout_2022/backtests/constructor_race_start_power_from_race_weekend.record.json
smoke_output/loso_folds/heldout_2022/backtests/constructor_race_start_power_from_race_weekend.record.npz
smoke_output/loso_folds/heldout_2022/backtests/constructor_race_start_power_from_recent_history.record.json
smoke_output/loso_folds/heldout_2022/backtests/constructor_race_start_power_from_recent_history.record.npz
smoke_output/loso_folds/heldout_2022/backtests/driver_quali_power_from_race_weekend.record.json
smoke_output/loso_folds/heldout_2022/backtests/driver_quali_power_from_race_weekend.record.npz
smoke_output/loso_folds/heldout_2022/backtests/driver_quali_power_from_recent_history.record.json
smoke_output/loso_folds/heldout_2022/backtests/driver_quali_power_from_recent_history.record.npz
smoke_output/loso_folds/heldout_2022/backtests/driver_race_power_from_race_weekend.record.json
smoke_output/loso_folds/heldout_2022/backtests/driver_race_power_from_race_weekend.record.npz
smoke_output/loso_folds/heldout_2022/backtests/driver_race_power_from_recent_history.record.json
smoke_output/loso_folds/heldout_2022/backtests/driver_race_power_from_recent_history.record.npz
smoke_output/loso_folds/heldout_2022/backtests/driver_race_start_power_from_race_weekend.record.json
smoke_output/loso_folds/heldout_2022/backtests/driver_race_start_power_from_race_weekend.record.npz
smoke_output/loso_folds/heldout_2022/backtests/driver_race_start_power_from_recent_history.record.json
smoke_output/loso_folds/heldout_2022/backtests/driver_race_start_power_from_recent_history.record.npz
```

### loso_folds/heldout_2023/backtests/ (12 modules)

```
smoke_output/loso_folds/heldout_2023/backtests/constructor_quali_power_from_race_weekend.record.json
smoke_output/loso_folds/heldout_2023/backtests/constructor_quali_power_from_race_weekend.record.npz
smoke_output/loso_folds/heldout_2023/backtests/constructor_quali_power_from_recent_history.record.json
smoke_output/loso_folds/heldout_2023/backtests/constructor_quali_power_from_recent_history.record.npz
smoke_output/loso_folds/heldout_2023/backtests/constructor_race_power_from_race_weekend.record.json
smoke_output/loso_folds/heldout_2023/backtests/constructor_race_power_from_race_weekend.record.npz
smoke_output/loso_folds/heldout_2023/backtests/constructor_race_power_from_recent_history.record.json
smoke_output/loso_folds/heldout_2023/backtests/constructor_race_power_from_recent_history.record.npz
smoke_output/loso_folds/heldout_2023/backtests/constructor_race_start_power_from_race_weekend.record.json
smoke_output/loso_folds/heldout_2023/backtests/constructor_race_start_power_from_race_weekend.record.npz
smoke_output/loso_folds/heldout_2023/backtests/constructor_race_start_power_from_recent_history.record.json
smoke_output/loso_folds/heldout_2023/backtests/constructor_race_start_power_from_recent_history.record.npz
smoke_output/loso_folds/heldout_2023/backtests/driver_quali_power_from_race_weekend.record.json
smoke_output/loso_folds/heldout_2023/backtests/driver_quali_power_from_race_weekend.record.npz
smoke_output/loso_folds/heldout_2023/backtests/driver_quali_power_from_recent_history.record.json
smoke_output/loso_folds/heldout_2023/backtests/driver_quali_power_from_recent_history.record.npz
smoke_output/loso_folds/heldout_2023/backtests/driver_race_power_from_race_weekend.record.json
smoke_output/loso_folds/heldout_2023/backtests/driver_race_power_from_race_weekend.record.npz
smoke_output/loso_folds/heldout_2023/backtests/driver_race_power_from_recent_history.record.json
smoke_output/loso_folds/heldout_2023/backtests/driver_race_power_from_recent_history.record.npz
smoke_output/loso_folds/heldout_2023/backtests/driver_race_start_power_from_race_weekend.record.json
smoke_output/loso_folds/heldout_2023/backtests/driver_race_start_power_from_race_weekend.record.npz
smoke_output/loso_folds/heldout_2023/backtests/driver_race_start_power_from_recent_history.record.json
smoke_output/loso_folds/heldout_2023/backtests/driver_race_start_power_from_recent_history.record.npz
```

### uncertainty_calibration_fit/backtests/ (12 modules x 1 year = 12 entries)

```
smoke_output/uncertainty_calibration_fit/backtests/constructor_quali_power_from_race_weekend_2023.record.json
smoke_output/uncertainty_calibration_fit/backtests/constructor_quali_power_from_race_weekend_2023.record.npz
smoke_output/uncertainty_calibration_fit/backtests/constructor_quali_power_from_recent_history_2023.record.json
smoke_output/uncertainty_calibration_fit/backtests/constructor_quali_power_from_recent_history_2023.record.npz
smoke_output/uncertainty_calibration_fit/backtests/constructor_race_power_from_race_weekend_2023.record.json
smoke_output/uncertainty_calibration_fit/backtests/constructor_race_power_from_race_weekend_2023.record.npz
smoke_output/uncertainty_calibration_fit/backtests/constructor_race_power_from_recent_history_2023.record.json
smoke_output/uncertainty_calibration_fit/backtests/constructor_race_power_from_recent_history_2023.record.npz
smoke_output/uncertainty_calibration_fit/backtests/constructor_race_start_power_from_race_weekend_2023.record.json
smoke_output/uncertainty_calibration_fit/backtests/constructor_race_start_power_from_race_weekend_2023.record.npz
smoke_output/uncertainty_calibration_fit/backtests/constructor_race_start_power_from_recent_history_2023.record.json
smoke_output/uncertainty_calibration_fit/backtests/constructor_race_start_power_from_recent_history_2023.record.npz
smoke_output/uncertainty_calibration_fit/backtests/driver_quali_power_from_race_weekend_2023.record.json
smoke_output/uncertainty_calibration_fit/backtests/driver_quali_power_from_race_weekend_2023.record.npz
smoke_output/uncertainty_calibration_fit/backtests/driver_quali_power_from_recent_history_2023.record.json
smoke_output/uncertainty_calibration_fit/backtests/driver_quali_power_from_recent_history_2023.record.npz
smoke_output/uncertainty_calibration_fit/backtests/driver_race_power_from_race_weekend_2023.record.json
smoke_output/uncertainty_calibration_fit/backtests/driver_race_power_from_race_weekend_2023.record.npz
smoke_output/uncertainty_calibration_fit/backtests/driver_race_power_from_recent_history_2023.record.json
smoke_output/uncertainty_calibration_fit/backtests/driver_race_power_from_recent_history_2023.record.npz
smoke_output/uncertainty_calibration_fit/backtests/driver_race_start_power_from_race_weekend_2023.record.json
smoke_output/uncertainty_calibration_fit/backtests/driver_race_start_power_from_race_weekend_2023.record.npz
smoke_output/uncertainty_calibration_fit/backtests/driver_race_start_power_from_recent_history_2023.record.json
smoke_output/uncertainty_calibration_fit/backtests/driver_race_start_power_from_recent_history_2023.record.npz
```

**Total**: 96 sidecar files (48 npz + 48 json) across all three dir families. All 12 modules present in each family.

## Loaded-Record Printout

Module: `driver_quali_power_from_recent_history` from `smoke_output/backtests/`

```
=== Loaded record for driver_quali_power_from_recent_history (mains) ===
event_count: 1
first event_id: '2024:1:Bahrain:quali_history'
pi shape: (20,)
sigma_pi shape: (20, 20)
n_entities: 20
entity_ids[:3]: ['ALB', 'ALO', 'BOT']
module_name: driver_quali_power_from_recent_history
task: quali
entity_scope: driver
```

The max_rounds_per_year=1 bound means only Round 1 (Bahrain) is in the eval set, hence
event_count=1. `pi` is a 1-D vector of length n=20 (one per driver); `sigma_pi` is (20,20)
as specified in the record contract.

## details.json No-Echo Spot-Check

Checked `smoke_reports/gold_cycle_260605_234006_2022thru2023_smoke1.details.json`:

```
emit_module_record present at top level: False
emit_module_record present in run_config: False
```

Top-level keys (confirming no new key from the flag):
`created_at`, `data_coverage`, `entity_scope_calibration_diagnostics`,
`evidence_mode_metrics`, `evidence_source_calibration_diagnostics`,
`fusion_correlation_diagnostics`, `fusion_train_rows`, `invariant_results`,
`module_uncertainty_diagnostics_json`, `module_uncertainty_diagnostics_markdown`,
`modules`, `recent_history_holdout_metrics`, `run_config`, `schema_doc_path`,
`schema_version`, `summary_report_path`, `task_calibration_diagnostics`,
`uncertainty_calibration_path`

The flag is runtime-only and correctly does not appear in the report schema.
Provenance lives in each `.record.json` sidecar (via `source_backtest` and
`module_name` fields), not in the run report.

## Pollution disclosure

The smoke run wrote **one file outside the evidence directory** via the
hardcoded calibration-promotion path in `gold_cycle/runner.py:341-343`
(pre-existing defect, triaged as follow-up candidate **tc4**):

```
params/gold/uncertainty_calibration/unc_cal_260605_234006_2022thru2023_smoke1.json
```

- Slug `260605_234006` matches this run's gold-cycle run ID
  (`gold_cycle_260605_234006_2022thru2023_smoke1`).
- The file was relocated to
  `evidence/escaped_artifacts/unc_cal_260605_234006_2022thru2023_smoke1.json`
  on 2026-06-05 to contain all run outputs within the evidence directory.
- A pre-existing file
  `unc_cal_260520_214442_2023thru2023_smoke1.json` (May-20 slug,
  mtime 07:58:53 2026-05-20) remains at
  `params/gold/uncertainty_calibration/` and was **not touched**.
- `outputs/evo_runs` and `reports/evo` verified clean for the run window
  (no untracked entries matching the 260605_234006 slug).

The root cause is the hardcoded promotion path in `runner.py:341-343`;
remediation of that defect is tracked separately and is out of scope for
this branch.
