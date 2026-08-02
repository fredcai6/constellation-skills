# Reviewer Handoff

## Gate
`g1` — Activate anchor + prepare A/B arms + pre-flight smoke

## What Was Implemented
1. `configs/evo/gold_defaults.toml`: `quali_pace_anchor_enabled` flipped `false → true` (one line). `utilization`, `alpha`, all else unchanged.
2. New `.agent-work/issue-335-gold-regen/configs/armB_quali_pace_gap.toml`: copy of the anchor-on gold_defaults differing ONLY by `recent_history_form_encoding = "quali_pace_gap"`.
3. New smoke configs `smoke_armA.toml` / `smoke_armB.toml` (smoke-mode, anchor on, each encoding) + smoke run logs.

## How to Inspect the Diff
```bash
cd C:/Programs/f1Brainz
git diff -- configs/evo/gold_defaults.toml
# arm B vs gold_defaults single-line difference:
git --no-pager diff --no-index configs/evo/gold_defaults.toml .agent-work/issue-335-gold-regen/configs/armB_quali_pace_gap.toml
```
Working tree is uncommitted (commander commits at integrate). Evidence: `.agent-work/issue-335-gold-regen/evidence/smoke_armA.log`, `smoke_armB.log`, full result `g1-implementer-result.md`.

## Task Statement
Prepare config for a full gold A/B retrain: activate the quali pace anchor, set up the two encoding arms, and smoke-prove both wire up end-to-end before the ~1.5h real cycles. No src/ logic changes.

## Close Criteria
- `gold_defaults.toml` diff is exactly the anchor flip (true); `utilization` NOT changed.
- `armB_quali_pace_gap.toml` differs from gold_defaults ONLY by `recent_history_form_encoding`.
- Config unit tests pass (`py -m pytest tests/unit/evo_predictor/test_gold_cycle_config.py tests/unit/evo_predictor/test_run_cli_defaults.py -q`).
- Both smoke runs reached manifest assembly with exit 0; logs confirm manifest `quali_pace_anchor.enabled = true` and Arm A `feature_schema_version = ...v1`, Arm B `...v2`.

## Allowed Scope
`configs/evo/gold_defaults.toml` (anchor line only); new files under `.agent-work/issue-335-gold-regen/`; running smoke commands. No `src/`, no `params/gold/`.

## Specific Exclusions
No src/ changes; no committed config change beyond the anchor flip; no promotion.

## Constraints the Implementation Must Respect
- Generated artifacts derived (no hand-edits).
- Gold-mode leakage-free invariants intact.
- Arm-B config stays in the work area.

## Evidence Produced
- gold_defaults diff (anchor line), arm-B diff (single line).
- Config unit tests: 114 passed.
- Smoke: Arm A exit 0 (manifest anchor enabled=true/alpha=0.5, module v1); Arm B exit 0 with `--max-rounds-per-year 1` (~2 min, module v2).

## KNOWN finding (do NOT block G1 on it — already routed)
The smoke surfaced a PRE-EXISTING bug: the sampled-runtime backtest aborts with `TypeError: RaceStartRecentHistoryConfig.__init__() got an unexpected keyword argument 'feature_schema_version'` (both modes, both arms). Root cause: `sampled_runtime._run_stage` (lines 446-449, #369 seam) forwards any manifest `feature_schema_version` into the adapter config; `RaceStartRecentHistoryConfig` has no such field. This is OUT OF SCOPE for G1 (it's a src/ runtime bug) and is being handled as its own fix gate. Confirm it is NOT caused by the G1 config change (it reproduces independent of the anchor flip / encoding), then note it — do not block G1 on it.

## Suggested Model Tier
simple bounded (sonnet) — mechanical config verification + smoke evidence check.

## Stop Conditions
BLOCK if: the gold_defaults diff includes anything beyond the anchor flip, the arm-B config differs by more than the encoding, config tests fail, or a smoke run did not reach manifest assembly for reasons attributable to the G1 change.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE/BLOCK), per-criterion findings, confirmation the TypeError is pre-existing/independent of the G1 change, blockers, out-of-scope observations.
