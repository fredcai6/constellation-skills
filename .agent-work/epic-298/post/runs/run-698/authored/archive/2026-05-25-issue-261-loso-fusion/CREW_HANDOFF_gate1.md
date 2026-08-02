# Crew Handoff — Gate 1: Create `configs/evo/fusion_calibration_loso.toml`

## Your Task

Create `configs/evo/fusion_calibration_loso.toml` in the worktree at:
`C:\Programs\f1Brainz\.worktrees\issue-261-loso-fusion`

This is a **new file only**. Do not touch any existing file.

## Context

The gold cycle has `emit_fusion_train_rows = "none"` by default (correct for production gold). A separate research-mode TOML is needed to run the LOSO calibration cycle that populates `fusion_train_rows` in the details JSON — enabling scipy OOF fusion calibration.

The config loader is at `src/evo_predictor/gold_cycle/config.py`. Key constraints:
- `mode` must be one of `"gold"`, `"research"`, `"smoke"` — use `"research"` (confirmed)
- `emit_fusion_train_rows` must be `"leave_one_season_out"` (the whole point)
- `allow_same_season_compound_prior` must be `false` (leakage guard)
- `lambda_sigma_nll` must be `0.0` (validator enforces this)
- All sections are required: `[data]`, `[training]`, `[uncertainty]`, `[runtime]`, `[outputs]`

## Reference: gold_defaults.toml values to mirror

```toml
schema_version = 1
mode = "gold"  # → change to "research"
profile_name = "gold_default"  # → change to "fusion_calibration_loso"

[data]
train_years = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
eval_year = 2025
db_root = "data"
compound_prior_root = "params/gold/compound_prior"
race_start_target_lap = 3
retro_root = "params/retro_truth"

[training]
target_mode = "retro_delta"
epochs = 25
seed = 0
learning_rate = 0.0001
hidden_dim = 128
dropout = 0.2
optimizer = "adam"
weight_decay = 0.0
early_stop_patience = 10
restore_best_checkpoint = true
min_delta = 0.0
session_dropout_k = 2
session_dropout_session_prob = 0.7

[uncertainty]
enable_sigma_calibration = true
lambda_sigma_nll = 0.0

[runtime]
n_samples = 1000
materialize_race_start_order_from_lap_times = true
emit_fusion_train_rows = "none"  # → change to "leave_one_season_out"
allow_same_season_compound_prior = false

[outputs]
output_dir = "outputs/evo_runs/gold_module_training_cycle"  # → change to "outputs/evo_runs/fusion_calibration_loso"
report_dir = "reports/evo"  # keep same
```

## Acceptance Criteria

Run this validation from the worktree root after writing the file:
```
py -c "
from src.evo_predictor.gold_cycle.config import load_gold_cycle_config
c = load_gold_cycle_config('configs/evo/fusion_calibration_loso.toml')
assert c.mode == 'research', f'mode={c.mode}'
assert c.runtime.emit_fusion_train_rows == 'leave_one_season_out', f'emit={c.runtime.emit_fusion_train_rows}'
assert c.outputs.output_dir == 'outputs/evo_runs/fusion_calibration_loso', f'out={c.outputs.output_dir}'
assert not c.runtime.allow_same_season_compound_prior
print('PASS', c.profile_name)
"
```

It must print `PASS fusion_calibration_loso`.

## Authority / Scope

- **Create only:** `configs/evo/fusion_calibration_loso.toml`
- **Do not touch:** `gold_defaults.toml`, any `src/` file, any test file
- **Worktree:** `C:\Programs\f1Brainz\.worktrees\issue-261-loso-fusion`

## Evidence to Return

1. Full content of the TOML you created
2. Output of the validation one-liner above (`PASS fusion_calibration_loso`)
3. `git diff --stat` showing only the new file

## Stop Conditions

- Config loader raises any error → fix before returning
- Validation asserts fail → fix before returning
- Any existing file was modified → revert and return error
