# A/B Comparison — issue-335 gold regen
## Fused 2025 backtest (sampled_state, trained manifests)

Gate: G4 evidence. No promotion. Promotion decision deferred to G5 (human checkpoint).

---

## Head-to-head table

| Metric | Arm A (position_quality) | Arm B (quali_pace_gap) | Delta (B−A) | Winner |
|--------|--------------------------|------------------------|-------------|--------|
| **pairwise_brier_against_actual_order** (PRIMARY, lower=better) | 0.2077 | 0.2008 | −0.0069 | **B** |
| pairwise_log_loss_against_actual_order | 0.6861 | 0.6289 | −0.0572 | **B** |
| expected_position_mae | 3.760 | 3.688 | −0.073 | **B** |
| mean_sample_mae | 4.633 | 4.670 | +0.037 | A (marginal) |
| sample_spearman_mean | 0.4524 | 0.4470 | −0.005 | A (marginal) |

Both arms: anchor ON (alpha=0.5), utilization=max, epochs=100, lr=1e-3, dropout-seeded, median-relative encoding, 24/24 races scored.

Arm A gold cycle slug: `gold_cycle_260607_231707_2018thru2024`
Arm B gold cycle slug: `gold_cycle_260608_043414_2018thru2024`
Arm A trained manifest: `outputs/evo_runs/issue335_armA/fusion/reports/evo/fusion_260608_034748_2018thru2024.sampled_runtime_manifest.json`
Arm B trained manifest: `outputs/evo_runs/issue335_armB/fusion/reports/evo/fusion_260608_084626_2018thru2024.sampled_runtime_manifest.json`

---

## Per-race robustness (24 races, paired comparison)

| Stat | Value |
|------|-------|
| B better in N/24 races | **19/24** |
| A better in N/24 races | 5/24 |
| Mean Brier delta (B−A) | **−0.00693** |
| Paired bootstrap 95% CI (seed=0, 5000 resamples) | **[−0.0104, −0.0038]** |
| CI excludes 0 | **YES** (both bounds negative) |

Bootstrap recomputed from per-race `pairwise_brier_against_actual_order` in the two
`backtest_trained_2025.json` files. Aggregate Brier values independently verified:
Arm A 0.2077438 and Arm B 0.2008099 match their respective `summary.txt` files exactly.

Biggest B wins: Brazil (rnd 20) −0.0264, Belgium (rnd 22) −0.0173, Abu Dhabi (rnd 24) −0.0202
Biggest A wins: Emilia Romagna (rnd 9) +0.0054, Spain (rnd 5) +0.0032, Saudi (rnd 2) +0.0034

---

## Baseline context (orientation only — NOT a controlled comparison)

The 260603 production bundle was trained under a different encoding and pipeline scope.
These numbers are directional only.

| Source | MAE | Brier |
|--------|-----|-------|
| 260603 trained rt_comparison 2018-2024 (`reports/evo/rt_comparison_260603_203000_2018thru2024.details.json`, `trained.aggregate_metrics`) | 4.09 | 0.215 |
| Arm A (position_quality, anchor ON) | 3.76 | 0.208 |
| Arm B (quali_pace_gap, anchor ON) | 3.69 | 0.201 |

Both new arms improve over the old production figures on MAE and Brier (directional;
encoding/pipeline changed so not a controlled head-to-head against 260603).

---

## Verdict

**Arm B (quali_pace_gap) wins the fused comparison on the primary Brier metric.**

- Primary Brier: 0.2008 vs 0.2077 (B lower by 0.0069)
- Bootstrap 95% CI [−0.0104, −0.0038] excludes 0 — the advantage is statistically
  supported at the n=24 race level
- B also wins on log-loss (−0.0572) and expected-position MAE (−0.073)
- A wins marginally on mean_sample_mae (+0.037) and sample_spearman (+0.005); both
  margins are small and do not overturn the primary metric verdict
- 19/24 per-race wins for B further confirms robustness

This settles the #369 deferred encoding decision: the data favor `quali_pace_gap`
over `position_quality` for the recent-history quali modules. User preference also
favors pace_gap. The recommendation is to promote Arm B as the new default
(promotion decision remains with the human at G5).
