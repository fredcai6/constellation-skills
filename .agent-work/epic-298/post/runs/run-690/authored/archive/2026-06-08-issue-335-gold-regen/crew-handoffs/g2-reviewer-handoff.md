# Reviewer Handoff

## Gate
`g2` — Arm A full gold cycle (position_quality + anchor ON)

## What Was Implemented
Commander ran the full Arm A gold cycle (config `.agent-work/issue-335-gold-regen/configs/run_armA.toml`: position_quality, anchor ON, epochs=100/lr=1e-3, utilization=max) → static fusion training → trained sampled-runtime manifest → fused backtest on 2025. Outputs isolated under `outputs/evo_runs/issue335_armA/`; key evidence copied to `.agent-work/issue-335-gold-regen/evidence/armA/`.

## How to Inspect
```bash
cd C:/Programs/f1Brainz
ls .agent-work/issue-335-gold-regen/evidence/armA/   # gold_details.json, gold_summary.json, manifest.json (trained), unc_diag.json, backtest_trained_2025.json, summary.txt
# cycle log:
#   .agent-work/issue-335-gold-regen/evidence/cycle_armA.log  (LOSO complete 1788 rows/84 runs)
#   .agent-work/issue-335-gold-regen/evidence/fusion_armA.log
```
Slug: `gold_cycle_260607_231707_2018thru2024`. Trained manifest: `outputs/evo_runs/issue335_armA/fusion/reports/evo/fusion_260608_034748_2018thru2024.sampled_runtime_manifest.json`.

## Task Statement
Produce a complete, leakage-free Arm A gold artifact set under the anchored config, with a captured fused-output Brier — the Arm A side of the A/B. No promotion in this gate.

## Close Criteria (independently verify — re-run, don't trust)
- **v6 schema**: gold details report has `skill_vs_chance` for all 12 modules. (`py -c "import sys;t=open(r'.agent-work/issue-335-gold-regen/evidence/armA/gold_details.json',encoding='utf-8').read();print(t.count('skill_vs_chance'))"` → ≥12)
- **Anchor active**: the trained `manifest.json` quali stage has `quali_pace_anchor` `{enabled:true, alpha:0.5}`.
- **Leakage-free gold**: `gold_summary.json` run_config shows `mode=gold`, `train_years` 2018–2024, `eval_year` 2025, `allow_same_season_compound_prior=false`.
- **Fused Brier captured + sane**: `backtest_trained_2025.json` aggregate `pairwise_brier_against_actual_order` ≈ 0.2077 (sanity: a ~20-driver pairwise Brier in ~0.18–0.25 is plausible; flag if degenerate, e.g. 0 or 0.5).
- **Cleanups**: (a) `unc_diag.json` emits `corr_sigma_pi_trace_vs_nll`, no `_vs_log_loss`; (d) `sampled_state` scored 24/24, 0 skipped (cycle log or gold report sampled_runtime section).
- **Trained manifest references the Arm A bundle slug** (`gold_cycle_260607_231707`), not the promoted 260603.

## Allowed Scope
Read-only verification of Arm A artifacts + logs. No changes.

## Specific Exclusions
Do not assess Arm B (not run yet). Do not compare to the promoted baseline beyond a sanity check (the matched baseline backtest is a G4 task). The `oracle_all_states` 1-race permutation error is a known flagged item (tc2) — note it, do not block on it (sampled_state is the production metric).

## Constraints the Implementation Must Respect
- DB-only analysis source; leakage-free gold mode.
- Generated artifacts derived; nothing promoted; params/gold untouched (only additive timestamped unc_cal).

## Evidence Produced
- Cycle: LOSO complete, 1788 rows / 84 runs; gold report v6; 0 `sampled_state` failures.
- Fusion trained; trained manifest produced.
- Fused backtest 2025: Brier 0.2077, log-loss 0.686, spearman 0.452.
- summary.txt with the consolidated numbers.

## Suggested Model Tier
sonnet — bounded artifact/metric verification.

## Stop Conditions
BLOCK if: any of the 12 modules lacks `skill_vs_chance`, the anchor is NOT active in the trained manifest, leakage flags are wrong (same-season prior on, wrong years), the fused Brier is missing/degenerate, or the trained manifest points at the wrong (260603) bundle.

## Return Format
Return REVIEW_RESULT: verdict APPROVE/BLOCK, per-criterion findings with the commands you re-ran and results, confirmation the anchor is active + the run is leakage-free, blockers, out-of-scope observations.
