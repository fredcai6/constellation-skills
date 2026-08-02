# Implementer Handoff

## Gate
`g4` — Compare (A vs B) + anchor §7.6.4 acceptance + cleanup verifications

## Task
Produce the consolidated evidence the human needs for the G5 promotion decision. Three deliverables.

### (a) `evidence/comparison.md` — the fused A/B
The A/B fused numbers are already computed and live in `.agent-work/issue-335-gold-regen/evidence/armA/summary.txt` and `evidence/armB/summary.txt`. **Verify them** (recompute from the two `backtest_trained_2025.json` files) and write a clean `evidence/comparison.md` containing:
- Head-to-head table (Arm A position_quality vs Arm B quali_pace_gap), 2025 fused `sampled_state`, trained manifests: pairwise Brier (PRIMARY), pairwise log-loss, expected_position_mae, mean_sample_mae, sample_spearman_mean. (Add pairwise sign-accuracy / reliability if present in the JSON.)
- Per-race robustness: B-better count (expect 19/24), mean Brier delta, **paired bootstrap 95% CI** (expect ≈ [−0.0103, −0.0037], excludes 0). Recompute it (seed 0, 5000 resamples, per-race `metrics.pairwise_brier_against_actual_order` keyed by round_num).
- Baseline context (last production, **for orientation only — not a controlled comparison** because the encoding/pipeline changed): 260603 trained rt_comparison race MAE 4.09 / Brier 0.215 (`reports/evo/rt_comparison_260603_203000_2018thru2024.details.json`, `trained.aggregate_metrics`). Note Arm A 3.76 / 0.208, Arm B 3.69 / 0.201.
- **Verdict**: state which arm wins the fused output and why (primary Brier, CI). Expectation: Arm B (quali_pace_gap) wins → recommend promote pace_gap as the new default (settles the #369 deferred decision; user bias also favors pace_gap).

### (b) `evidence/acceptance_420.txt` — anchor §7.6.4 reproduction on the NEW bundle
`scripts/accept_quali_anchor_420.py` hardcodes `BUNDLE_NAME = "gold_cycle_260603_173742_2018thru2024"` (the OLD bundle) and takes no args. The issue requires running it **against the new bundles**. Parametrize it minimally and reusably: add an optional `--bundle-path` (and/or `--bundle-name`) argparse arg that defaults to the existing 260603 constant, and an optional `--output-dir` (default the existing constant). **Default behavior must be byte-identical** (a no-arg run still targets 260603 and writes to the same place). Then run it against Arm B's quali head:
`outputs/evo_runs/issue335_armB/modules/driver_quali_power_from_race_weekend`
Save the full output to `evidence/acceptance_420.txt`. Confirm the §7.6.4 numbers (alpha=0.5 LOSO overall ≈0.75, EASY ≈0.87; OOS-2025 holds) **reproduce or improve** on the new bundle vs the `REF_HEADLINE`/`REF_OOS` references in the script. Report the actual numbers.

### (c) `evidence/cleanup_checks.json`
Write JSON: `{"nll_ok": <bool>, "race_count": <int>, "threads_note": "<str>"}`
- `nll_ok`: both arms' fresh `unc_diag.json` emit `corr_sigma_pi_trace_vs_nll` and NOT `corr_sigma_pi_trace_vs_log_loss` (already true for Arm A; verify Arm B too).
- `race_count`: the sampled_state scored-race count (expect 24, both arms 24/24/0-skip per the cycle logs).
- `threads_note`: confirm `utilization=max` ⇒ `threads_per_worker=1` (see `src/utils/utilization.py` `_LEVEL_PLANS`), i.e. the bit-reproducible regime; note `_WEIGHT_TOL` (1e-6, #362) is accepted under the threads=1 argument with no full-scale 2-run check (user decision).

## Protected Intent
This gate establishes the evidence; it does NOT promote anything. Do not touch `params/gold/`, the promoted manifest, or `gold_defaults.toml`. The acceptance-harness parametrization must preserve default behavior exactly.

## Test Mode
test-after for the harness change (preserve default = byte-identical, so verify a no-arg run still targets 260603 — you can confirm by argparse defaults + a dry inspection, no need to run the full 260603 sweep). The comparison/cleanup are analysis, not logic.

## Close Criteria
- `evidence/comparison.md` exists, substantive, with the verified head-to-head + bootstrap + verdict.
- `evidence/acceptance_420.txt` exists with real numbers from Arm B's bundle; §7.6.4 reproduced-or-improved (or a clear explanation if not).
- `evidence/cleanup_checks.json` shows `nll_ok=true`, `race_count=24`.
- If `accept_quali_anchor_420.py` was edited: `py -m src.utils.simplification_limits scripts/accept_quali_anchor_420.py` clean; default behavior preserved (no-arg targets 260603).

## Allowed Scope
`scripts/accept_quali_anchor_420.py` (minimal, default-preserving argparse only), `.agent-work/issue-335-gold-regen/evidence/`. Nothing else.

## Specific Exclusions
No promotion, no `params/gold/` writes, no changes to the anchor blend math or §7.6 reference constants, no encoding/config changes.

## Constraints
- Generated artifacts derived; DB-only; leakage-free.
- One canonical path; the harness change must keep the existing no-arg invocation working identically.

## Required Evidence
- The three files above. The recomputed bootstrap CI. The acceptance numbers (alpha sweep headline + OOS) on the new bundle. The harness diff (if any) + simplification_limits output.

## Verification Commands
```bash
py scripts/accept_quali_anchor_420.py --bundle-path outputs/evo_runs/issue335_armB/modules/driver_quali_power_from_race_weekend --output-dir .agent-work/issue-335-gold-regen/evidence/acceptance_armB   # adjust to your arg names
py -m src.utils.simplification_limits scripts/accept_quali_anchor_420.py   # if edited
```

## Suggested Model Tier
sonnet — bounded analysis + a small, careful default-preserving CLI addition.

## Authority
The promotion decision is the human's (G5). You produce evidence only. You may add a default-preserving CLI arg to the acceptance harness; you may NOT change its math, references, or default target.

## Stop Conditions
Stop if: the acceptance harness can't run on the new bundle without changing default behavior or the blend math; the bootstrap can't be reproduced; or any deliverable needs scope beyond the listed files.

## Return Format
IMPLEMENTER_RESULT: the three deliverables (paths), the verified A/B verdict, the acceptance numbers vs §7.6.4, the harness diff (if any) + limits output, the cleanup_checks contents, assumptions, stop conditions, out-of-scope observations. Do NOT commit — leave changes in the working tree.
