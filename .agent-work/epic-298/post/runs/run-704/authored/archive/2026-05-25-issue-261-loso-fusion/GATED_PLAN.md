# Gated Plan: issue-261 — Enable LOSO rows for OOF fusion calibration

## Problem Statement

The gold cycle emits `emit_fusion_train_rows = "none"` by default, so `fusion_training.py` never receives LOSO metric rows. Without these rows, `_optimise_scales_from_oof` falls back to `"coarse_static_metric_grid_v1_fallback_insufficient_train_events"`. The OOF benefit (scipy L-BFGS-B scale optimisation from issue #254) is dormant in production.

## Intent Protected

Activate `search_policy = "scipy_oof_lbfgsb_v1"` in the committed `params/gold/fusion/` artifact for the 2018–2024/eval-2025 run, without modifying source code or gold_defaults.toml.

## Scope

**Allowed regions/files:**
- `configs/evo/fusion_calibration_loso.toml` (new file)
- `outputs/evo_runs/fusion_calibration_loso/` (generated; gitignored)
- `params/gold/fusion/static_hierarchical_fusion_2018-2019-2020-2021-2022-2023-2024_eval_2025.json` (updated)
- `reports/evo/` (updated fusion report files)

**Not scope:** Any changes to `src/`, `tests/`, `configs/evo/gold_defaults.toml`, `scripts/`  
**Specific exclusions:** `params/gold/fusion/static_hierarchical_fusion_2021-2022-2023-2024_eval_2025.json` and `2022-2023-2024_eval_2025.json` must not change

## Structural Baseline

**Need:** no  
**Status:** skipped — scope is additive config + operational; no structural truth changes  
**Evidence:** fusion_training.py OOF path confirmed in updated main; runner.py LOSO path confirmed; config.py research-mode constraints confirmed

## Authority / Assumptions

- `mode = "research"` confirmed by user (calibration utility, not production gold)
- Output dir `outputs/evo_runs/fusion_calibration_loso` — separate from production gold outputs
- DBs for 2018–2025 assumed complete (last gold run 5/21 succeeded)
- `params/gold/compound_prior/` and `params/retro_truth/` assumed intact

## Test Mode

**Plan default:** no TDD — Gate 1 only creates a TOML (config file, not behavior code); Gate 3 is operational evidence (artifact inspection + test suite pass)

## Project Mechanics Hooks

| Moment | Hook | Owner | Evidence |
|---|---|---|---|
| After Gate 1 evidence accepted | commit TOML | Conductor | commit SHA |
| After Gate 3 evidence accepted | commit fusion artifact | Conductor | commit SHA |
| Before closeout | push + PR | Conductor | PR URL |

## Gates

### Gate 1: Create `configs/evo/fusion_calibration_loso.toml`

**Purpose:** Provide the research-mode TOML that enables LOSO row emission, with its own output dir, validated by the config loader.  
**Crew cycle:** implementer → integrate evidence → reviewer → integrate evidence → gate close  
**Implementer handoff:** required  
**Reviewer handoff:** required  
**Suggested model tier:** simple bounded  
**Test mode:** validate with `py -c "from src.evo_predictor.gold_cycle.config import load_gold_cycle_config; c = load_gold_cycle_config('configs/evo/fusion_calibration_loso.toml'); assert c.runtime.emit_fusion_train_rows == 'leave_one_season_out'; print('OK', c.profile_name)"`  
**Allowed scope:** `configs/evo/fusion_calibration_loso.toml` only  
**Specific exclusions:** `gold_defaults.toml` must not change

**Close criteria:**
- [ ] TOML loads without error via `load_gold_cycle_config`
- [ ] `emit_fusion_train_rows == "leave_one_season_out"` confirmed
- [ ] `mode == "research"` confirmed
- [ ] `output_dir` differs from gold defaults (`outputs/evo_runs/fusion_calibration_loso`)
- [ ] Implementer evidence integrated
- [ ] Reviewer evidence integrated

**Required evidence:**
- Python one-liner validation output (see test mode above)
- `git diff --stat` showing only the new file

**Stop conditions:** config loader raises — fix before proceeding  
**Next gate:** Gate 2 (LOSO gold cycle run)

---

### Gate 2: Run LOSO gold cycle

**Purpose:** Produce `outputs/evo_runs/fusion_calibration_loso/` with `fusion_train_rows` in the details JSON — the data source for OOF fusion training.  
**Crew cycle:** implementer (operational run) → integrate evidence → gate close (no separate reviewer; evidence is the output artifact inspection)  
**Implementer handoff:** required  
**Reviewer handoff:** skipped — run is deterministic and evidence is objective (JSON field presence + count)  
**Suggested model tier:** simple bounded  
**Test mode:** operational evidence (artifact inspection)  
**Allowed scope:** read-only repo access + write to `outputs/evo_runs/fusion_calibration_loso/`  
**Specific exclusions:** must not touch `outputs/evo_runs/gold_module_training_cycle/`

**Run command:**
```
cd C:\Programs\f1Brainz\.worktrees\issue-261-loso-fusion
py -m src.evo_predictor.run gold-cycle --config configs/evo/fusion_calibration_loso.toml
```

**Close criteria:**
- [ ] Run exits 0
- [ ] `outputs/evo_runs/fusion_calibration_loso/<slug>.details.json` exists
- [ ] `fusion_train_rows` in details JSON is a non-empty list
- [ ] `fusion_train_rows` count reported (expect ~(7 LOSO folds × 12 modules × rounds) rows)

**Required evidence:**
- Exit code 0 + final printed report paths
- `py -c` snippet reading the details JSON and printing `len(details['fusion_train_rows'])`

**Stop conditions:** exit non-zero, missing details JSON, or empty `fusion_train_rows`  
**Next gate:** Gate 3 (fusion training + artifact commit)

---

### Gate 3: Run fusion training + commit artifact

**Purpose:** Produce and commit the OOF-calibrated `params/gold/fusion/static_hierarchical_fusion_2018-2019-2020-2021-2022-2023-2024_eval_2025.json` with `search_policy = "scipy_oof_lbfgsb_v1"`.  
**Crew cycle:** implementer → integrate evidence → reviewer → integrate evidence → gate close  
**Implementer handoff:** required  
**Reviewer handoff:** required (review the new fusion JSON for correctness)  
**Suggested model tier:** simple bounded  
**Test mode:** artifact inspection + test suite pass  
**Allowed scope:** run `scripts/run_static_hierarchical_fusion_training.py`, write to `params/gold/fusion/` and `reports/evo/`

**Run command:**
```
cd C:\Programs\f1Brainz\.worktrees\issue-261-loso-fusion
py scripts/run_static_hierarchical_fusion_training.py \
  --gold-summary reports/evo/fusion_calibration_loso_<slug>.summary.json \
  --gold-details outputs/evo_runs/fusion_calibration_loso/<slug>.details.json \
  --uncertainty-calibration params/gold/uncertainty_calibration/module_uncertainty_calibration_<slug-without-prefix>.json \
  --train-years 2018 2019 2020 2021 2022 2023 2024 \
  --eval-year 2025 \
  --output-dir .
```
*(Implementer must resolve `<slug>` from Gate 2 output paths.)*

**Close criteria:**
- [ ] `params/gold/fusion/static_hierarchical_fusion_2018-2019-2020-2021-2022-2023-2024_eval_2025.json` updated
- [ ] `search_policy == "scipy_oof_lbfgsb_v1"` in all 3 tasks (quali, race_start, race)
- [ ] Fused pairwise log loss on eval year does not worsen vs baseline (check summary JSON)
- [ ] `py -m pytest tests/ -q --tb=short` passes (861+ tests)
- [ ] Git commit made with artifact + report files

**Required evidence:**
- `jq` or `py -c` snippet showing `search_policy` for each task
- Summary JSON metric comparison vs existing `static_hierarchical_fusion_2021-2022-2023-2024_eval_2025.json`
- pytest output (pass count + 0 failures)
- commit SHA

**Stop conditions:** search_policy stays at fallback, metric regression, test failures  
**Next gate:** closeout

## Triage Candidate Log

| Candidate | Reason | Anchor | Evidence | Status |
|---|---|---|---|---|
| — | — | — | — | none |

## Plan-Level Stop Conditions

- LOSO run exits non-zero or produces empty fusion_train_rows
- search_policy remains at fallback after fusion training (OOF threshold not met)
- Test failures after Gate 3

## Final Completion Criteria

- [ ] all 3 gates closed
- [ ] each gate completed its Crew cycle
- [ ] evidence satisfies close criteria
- [ ] assumptions still hold (DBs intact, no data leakage)
- [ ] architecture reconciliation checked
- [ ] Triage candidates: none
