# Triage Recommendation: Single source for canonical train_years

## Classification
`architecture weakness`, `cleanup`

## Source checklist/artifact
- reconcile.json tc2 / reconcile-summary.md T2

## Structural anchor
`scripts/run_pipeline_validation.py`, `configs/evo/gold_defaults.toml`

## Problem
`CANONICAL_TRAIN_YEARS` is hard-coded in pipeline validation while gold training policy lives in `gold_defaults.toml`. Values are aligned today (2018–2024) but can drift silently.

## Current truth
- `gold_defaults.toml`: `train_years = [2018, 2019, 2020, 2021, 2022, 2023, 2024]`
- `run_pipeline_validation.py`: `CANONICAL_TRAIN_YEARS = [2018, 2019, 2020, 2021, 2022, 2023, 2024]`
- Schema docs updated to 2018–2024 in issue-292

## Desired/future concern
One authoritative source for train/eval split used by training and validation.

## Evidence
- reconcile-summary.md T2
- issue-292 g4 train_years reconciliation

## Impact
Future gold config changes could pass training but fail validation (or vice versa) without a single import path.

## Suggested scope
Import or derive canonical train years from gold config (or shared evo constants module) in `run_pipeline_validation.py`; add test that validator and gold_defaults stay in sync.

## Non-goals
- Changing the actual train_years policy
- Refactoring all config loading

## Acceptance criteria
- [ ] Pipeline validation reads train years from one shared source with gold_defaults
- [ ] Unit test fails if sources diverge
- [ ] Compact validation still passes

## Recommended priority
`low`

**Reason:** Aligned now; drift prevention.

## Issue creation authority
`ask user`
