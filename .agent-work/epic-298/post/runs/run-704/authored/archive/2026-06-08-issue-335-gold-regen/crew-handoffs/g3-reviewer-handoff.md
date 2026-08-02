# Reviewer Handoff

## Gate
`g3` — Arm B full gold cycle (quali_pace_gap + anchor ON)

## What Was Implemented
Commander ran the Arm B gold cycle (`run_armB.toml`: quali_pace_gap encoding, anchor ON, epochs=100/lr=1e-3, utilization=max) → static fusion → trained manifest → fused backtest on 2025. Isolated under `outputs/evo_runs/issue335_armB/`; evidence in `.agent-work/issue-335-gold-regen/evidence/armB/`. Slug `gold_cycle_260608_043414_2018thru2024`.

## How to Inspect
```bash
cd C:/Programs/f1Brainz
ls .agent-work/issue-335-gold-regen/evidence/armB/   # gold_details/summary, manifest(trained), unc_diag, backtest_trained_2025.json, summary.txt
# logs: evidence/cycle_armB.log, evidence/fusion_armB.log, evidence/backtest_armB_2025.log
```

## Task Statement
Produce the Arm B (quali_pace_gap) side of the A/B with a captured fused Brier — same pipeline as Arm A, differing ONLY by the encoding. No promotion.

## Close Criteria (independently verify)
- **Encoding took effect**: the two quali recent-history modules stamp `...recent_history.v2` (NOT .v1). Check `outputs/evo_runs/issue335_armB/modules/driver_quali_power_from_recent_history/module_diagnostics.json` → feature_schema_version ends `.v2`; same for constructor. (Arm A is `.v1`.)
- **Arms differ ONLY by encoding**: `run_armB.toml` vs `gold_defaults.toml`/`run_armA.toml` differ only in `recent_history_form_encoding` (+ isolated output/report dirs). Same train_years 2018-2024, eval 2025, seed 0, epochs 100, lr 1e-3, anchor on.
- **v6 schema**: `gold_details.json` has `skill_vs_chance` for all 12 modules.
- **Anchor active**: trained `manifest.json` quali stage `quali_pace_anchor.enabled == true`, alpha 0.5.
- **Leakage-free gold**: `gold_summary.json` run_config = mode gold, allow_same_season_compound_prior false, correct split.
- **Fused Brier captured + sane**: `backtest_trained_2025.json` `pairwise_brier_against_actual_order` ≈ 0.2008 (range ~0.18-0.25).
- **race_count**: sampled_state 24/24, 0 skipped (cycle_armB.log).

## A/B sanity (verify the comparison is fair)
- Confirm both arms backtested with the same harness (mode sampled_state, year 2025, n_samples per config) and the same eval DB materialization. The head-to-head in `evidence/armB/summary.txt` (B better on Brier/log-loss/MAE; B better in 19/24 races; bootstrap CI excludes 0) should be reproducible from the two `backtest_trained_2025.json` files. Spot-check at least the aggregate Brier of both arms.

## Allowed Scope / Exclusions
Read-only verification. The `oracle_all_states` 1-race permutation error (tc2) is known in BOTH arms — note, do not block.

## Constraints
DB-only; leakage-free gold; nothing promoted; params/gold untouched (additive unc_cal only).

## Suggested Model Tier
sonnet — bounded artifact/metric verification + the encoding/fairness check.

## Stop Conditions
BLOCK if: the quali recent-history modules are NOT .v2 (encoding didn't take effect), arms differ by more than the encoding, any module lacks skill_vs_chance, anchor not active, leakage flags wrong, or the fused Brier is missing/degenerate.

## Return Format
Return REVIEW_RESULT: verdict APPROVE/BLOCK, per-criterion findings with commands/results, explicit confirmation the v2 encoding took effect and the arms differ only by encoding, blockers, out-of-scope observations.
