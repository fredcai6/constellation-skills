# Implementation Result

## Assigned gate
`g1: activate anchor + prepare A/B arms + smoke wiring proof`

## Completed slice
1. Flipped `quali_pace_anchor_enabled = false` → `true` in `configs/evo/gold_defaults.toml` (one line only).
2. Created `.agent-work/issue-335-gold-regen/configs/armB_quali_pace_gap.toml` — copy of now-anchor-on `gold_defaults.toml` differing only by `recent_history_form_encoding = "quali_pace_gap"` plus one header comment.
3. Created smoke-mode configs for both arms in `.agent-work/issue-335-gold-regen/configs/`:
   - `smoke_armA.toml` — anchor ON, position_quality encoding, mode=smoke, 2 epochs
   - `smoke_armB.toml` — anchor ON, quali_pace_gap encoding, mode=smoke, 2 epochs
4. Ran Arm A smoke end-to-end (train → manifest → sampled backtest). Exit code 0.
5. Ran Arm B smoke end-to-end (train → manifest → sampled backtest, with `--max-rounds-per-year 1`). Exit code 0.
6. Ran config unit tests: 114 passed.

## Scope
**Files changed:**
- `configs/evo/gold_defaults.toml` — one line: `quali_pace_anchor_enabled = false` → `true`
- `.agent-work/issue-335-gold-regen/configs/armB_quali_pace_gap.toml` — new file (work area only)
- `.agent-work/issue-335-gold-regen/configs/smoke_armA.toml` — new file (work area only)
- `.agent-work/issue-335-gold-regen/configs/smoke_armB.toml` — new file (work area only)
- `.agent-work/issue-335-gold-regen/evidence/smoke_armA.log` — new evidence file
- `.agent-work/issue-335-gold-regen/evidence/smoke_armB.log` — new evidence file

**Specific exclusions touched:** no — `src/` not touched, `params/gold/` not modified, promoted manifest not touched, `utilization = "balanced"` left unchanged in gold_defaults.toml.

## Behavior changed
Yes. `gold_defaults.toml` now has `quali_pace_anchor_enabled = true`. Any gold retrain using the default config will have the pace anchor active. The armB config is a new work-area artifact (not committed); it is not part of the production config path until promoted.

## Test mode
**Required:** `evidence-only` (wiring proof via smoke runs; no TDD required by handoff)
**Satisfied:** yes — both smoke runs exit 0; manifests verified; config tests pass.

## Evidence

**Arm A smoke run:**
```
evidence/smoke_armA.log: exit code 0
- 12/12 modules trained (15:38:06–15:38:43)
- Sampled runtime manifest assembled: outputs/evo_runs/smoke_armA_335/sampled_runtime_manifest.json
- stages.quali.quali_pace_anchor = {"enabled": true, "alpha": 0.5}  ← anchor confirmed
- driver_quali_power_from_recent_history feature_schema_version: driver_quali_power_from_recent_history.v1  ← Arm A = v1 confirmed
- Sampled backtest launched (non-fatal TypeError on sampled_state + oracle_all_states — pre-existing; see Out-of-scope)
- Reports written: reports/evo/gold_cycle_260607_213806_2023thru2023.*
```

**Arm B smoke run:**
```
evidence/smoke_armB.log: exit code 0
- 12/12 modules trained (15:20:20–15:20:27, <10 s with --max-rounds-per-year 1)
- Sampled runtime manifest assembled: outputs/evo_runs/smoke_armB_335/sampled_runtime_manifest.json
- stages.quali.quali_pace_anchor = {"enabled": true, "alpha": 0.5}  ← anchor confirmed
- driver_quali_power_from_recent_history feature_schema_version: driver_quali_power_from_recent_history.v2  ← Arm B = v2 (quali_pace_gap) confirmed
- Same non-fatal TypeError on sampled_state + oracle_all_states (pre-existing)
- Reports written: reports/evo/gold_cycle_260607_222020_2023thru2023_smoke1.*
```

**Config unit tests:**
```
py -m pytest tests/unit/evo_predictor/test_gold_cycle_config.py tests/unit/evo_predictor/test_run_cli_defaults.py -q
114 passed in 0.54s
```

**Result:** all evidence satisfies postconditions; gate g1 complete.

## TDD evidence, if required
N/A — evidence-only test mode per handoff.

## Docs/contracts touched
- None — no src/ or docs/ changes required for this gate.

## Assumptions
1. Arm A smoke used no `--max-rounds-per-year` limit (24 rounds, ~39 min wall time). This was deliberate for a full wiring proof on Arm A.
2. Arm B smoke used `--max-rounds-per-year 1` to keep run time fast (~2 min). This is valid because: (a) smoke mode accepts the override, (b) the wiring proof only needs the pipeline to complete without hard errors, not backtest on all 24 rounds.
3. The "no valid batches" warnings for fp1_sq/fp1_s/sq_s evidence modes are expected with `--max-rounds-per-year 1` (single round does not provide enough variation to form evidence-mode batches). These warnings also appear in full 24-round Arm A smoke and in the production gold cycle — pre-existing, non-fatal.
4. Arm B smoke reports write to a file with `_smoke1` suffix (rather than `_smoke`). This is a runner auto-deconflict on the timestamp — harmless.

## Stop conditions hit
- None. No hard errors or wiring bugs that weren't pre-existing.

## Out-of-scope observations
**TRIAGE CANDIDATE:** Both sampled backtest modes (`sampled_state` and `oracle_all_states`) fail with:
```
TypeError("RaceStartRecentHistoryConfig.__init__() got an unexpected keyword argument 'feature_schema_version'")
```
This error is:
- **Pre-existing**: production gold cycle (260603) also has empty sampled_backtest results in its details JSON.
- **Non-fatal**: runner catches it and continues; exit code 0.
- **Root cause**: `RaceStartRecentHistoryConfig` does not declare `feature_schema_version`, but the module manifest emits it (v2 modules added this field). When the manifest is deserialized, the field is rejected by the config dataclass.
- **Impact**: sampled_state and oracle_all_states backtest modes produce no results. Anchor wiring proved via manifest JSON instead.
- **Recommended action**: add `feature_schema_version` field to `RaceStartRecentHistoryConfig` (or use `**kwargs` / `extra='ignore'` if pydantic). This is a src/ change — out of scope for G1.

## Return status
`complete`
