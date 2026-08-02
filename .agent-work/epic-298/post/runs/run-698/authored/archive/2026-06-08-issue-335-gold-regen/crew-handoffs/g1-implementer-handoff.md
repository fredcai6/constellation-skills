# Implementer Handoff

## Gate
`g1` — Activate anchor + prepare both A/B arms + pre-flight smoke

## Task
Prepare the run configuration for a full gold retrain that activates the quali pace anchor and sets up an A/B over the recent-history form encoding, then smoke-prove both arms wire up end-to-end before the (expensive) real cycles.

1. **Anchor flip**: In `configs/evo/gold_defaults.toml`, change `quali_pace_anchor_enabled = false` → `true`. Leave `quali_pace_anchor_alpha = 0.5` and `utilization` unchanged.
2. **Arm B config**: Create `.agent-work/issue-335-gold-regen/configs/armB_quali_pace_gap.toml` as a copy of the (now anchor-on) `configs/evo/gold_defaults.toml` with exactly one difference: `recent_history_form_encoding = "quali_pace_gap"` (gold_defaults stays `"position_quality"` and is Arm A). Add a one-line comment at top noting it's the issue-335 Arm B experimental config.
3. **Pre-flight smoke (both arms) — must be FAST (target: a few minutes each, not the 100-epoch production config)**: Build a small **smoke-mode** config per arm — base it on `configs/evo/smoke_defaults.toml` (mode="smoke", few epochs, small scale) but set `quali_pace_anchor_enabled = true` and the arm's `recent_history_form_encoding` (`position_quality` for A, `quali_pace_gap` for B). Run each end-to-end so the pipeline trains → fuses → assembles a manifest → runs a sampled backtest (the backtest is what exercises the anchor) without error under each encoding. Put these smoke configs in `.agent-work/issue-335-gold-regen/configs/` (smoke_armA.toml, smoke_armB.toml). Capture full output to `.agent-work/issue-335-gold-regen/evidence/smoke_armA.log` and `.../smoke_armB.log`. Goal is a wiring proof, not a quality measurement.

## Protected Intent
The real production cycles (G2/G3, ~1.5h each) must not fail on a wiring error. This gate is cheap insurance. The committed config change must be exactly the anchor activation — nothing else in `gold_defaults.toml` may change.

## Test Mode
inspection + smoke. The anchor flag and encoding already have unit coverage; this gate verifies config validity + end-to-end wiring, not new logic.

## Close Criteria
- `configs/evo/gold_defaults.toml` has `quali_pace_anchor_enabled = true`; diff shows ONLY that line changed.
- `armB_quali_pace_gap.toml` exists and differs from gold_defaults.toml ONLY by `recent_history_form_encoding`.
- Config unit tests pass: `py -m pytest tests/unit/evo_predictor/test_gold_cycle_config.py tests/unit/evo_predictor/test_run_cli_defaults.py -q`.
- Both smoke runs complete end-to-end (train → static fusion → manifest assembly) with no error, logs saved. Confirm in each log that the anchor is active and Arm B used the quali_pace_gap (v2) encoding.

## Allowed Scope
- `configs/evo/gold_defaults.toml` (the one-line anchor flip only)
- `.agent-work/issue-335-gold-regen/configs/armB_quali_pace_gap.toml` (new)
- `.agent-work/issue-335-gold-regen/evidence/` (smoke logs)
- Running gold-cycle / fusion / manifest commands for the smoke (no promotion).

## Specific Exclusions
- Do NOT change `utilization` in the committed config (passed per-run as `--utilization max`).
- Do NOT touch `params/gold/` or the promoted manifest.
- Do NOT change any `src/` logic. If a wiring bug surfaces, STOP and report it (do not fix here).

## Constraints
- Generated artifacts are derived; no hand-edits.
- Gold-mode leakage-free invariants must remain intact.
- DB is the only data source.
- Arm B config stays in the work area (experimental until/unless it wins).

## Required Evidence
- The two-line-or-less diff of `gold_defaults.toml`.
- `armB_quali_pace_gap.toml` content + a diff vs gold_defaults showing the single difference.
- Config unit-test output (pass).
- `smoke_armA.log` and `smoke_armB.log` showing clean end-to-end completion; quote the lines proving anchor active + Arm B v2 encoding.

## Verification Commands
```bash
# config tests
py -m pytest tests/unit/evo_predictor/test_gold_cycle_config.py tests/unit/evo_predictor/test_run_cli_defaults.py -q
# FAST smoke arm A (smoke-mode copy: anchor on, position_quality). Add --max-rounds-per-year 1 if accepted in smoke mode.
py -m src.evo_predictor.run gold-cycle --config .agent-work/issue-335-gold-regen/configs/smoke_armA.toml --utilization max
# FAST smoke arm B (smoke-mode copy: anchor on, quali_pace_gap)
py -m src.evo_predictor.run gold-cycle --config .agent-work/issue-335-gold-regen/configs/smoke_armB.toml --utilization max
```
Note: `gold-cycle` exposes `--utilization {background,balanced,max}` and `--max-rounds-per-year`. Use smoke MODE (not the gold config) so the smoke is fast and CLI overrides are allowed. The two production arm configs (`gold_defaults.toml` = Arm A, `armB_quali_pace_gap.toml` = Arm B) are what G2/G3 will run at full scale — do NOT run those at full scale here.

## Suggested Model Tier
simple bounded (sonnet). Mechanical config + smoke; the only judgment is choosing the bounded-smoke mechanism if gold mode rejects `--max-rounds-per-year`.

## Authority
Decisions already made by the user: anchor ON; A/B both arms with anchor ON; encoding values are `position_quality` (A) and `quali_pace_gap` (B); utilization=max per-run. You may choose the smoke mechanism. You may NOT change scope, flip any other config, or modify src/.

## Stop Conditions
Stop and return if: a src/ change would be needed, the smoke reveals a wiring bug, a gold-mode restriction blocks a bounded smoke for either arm, or the config tests fail.

## Return Format
Return IMPLEMENTER_RESULT: what you did, files changed, the gold_defaults diff, the arm-B config diff, test mode satisfied, smoke evidence (paths + the anchor/encoding confirmation lines), assumptions, stop conditions hit, out-of-scope observations.
