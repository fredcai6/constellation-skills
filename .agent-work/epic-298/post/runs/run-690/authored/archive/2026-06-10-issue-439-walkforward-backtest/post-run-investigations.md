# Post-run investigations — requested + discovered

## RESULT (run b1l0qm80s complete, exit 0, attestation_all_pass=true)
- Committed summary.json: season_total=833 vs baseline_total=707 — BUT MIXED PATH (P0 full-evidence 155 +
  P1-3 sampled-runtime), so NOT a valid comparison. Report needs consistent-path fix (G5).
- CLEAN like-for-like (both sampled-runtime, R7-24 = where the model differs; P0 R1-6 identical reuse):
    P1 R7-12: gold 174 vs wf 199 (+25) ; P2 R13-18: 250 vs 227 (-23) ; P3 R19-24: 248 vs 252 (+4)
    R7-24 total: gold 672 vs wf 678 (+6) -> IN-SEASON RETRAINING IS A WASH (within noise; ~0.3/race).
- Full-season sampled-runtime: baseline 849 vs wf(mixed) 833 ; baseline full-evidence 707 (beats human 711).
- Bottom line: fixed gold model ~= quarter-by-quarter retrain for 2025 fantasy. Strengthens the
  "inherit gold fusion / skip in-season LOSO" case (and questions in-season base retrain too).

## STILL TODO
1. Consistent-path re-score for the committed report: put walk-forward P1-3 on the FULL-EVIDENCE path
   (run full-evidence per-race inference on each saved period model for its eval rounds), so the report shows
   walk-forward vs 707 vs 711 apples-to-apples. Fix summary.json/.md to stop comparing mixed scales.
2. Fusion-inheritance ablation (section A) — does in-season fusion add anything over inherited gold fusion.

---
# (original agenda below)

## A. In-season fusion retrain vs INHERIT gold fusion (user's sharpened question)
THE question: must each walk-forward period re-derive fusion weights + sigma calibration (84 LOSO + 12
calibration runs), or can it INHERIT them from the gold run and retrain ONLY the 12 base modules?
Per period: 12 base + 84 LOSO + 12 cal = 108 runs. Inherit fusion+cal -> 12 runs/period = ~9x fewer
(~order of magnitude; this ~14h run -> ~1.5-2h).

Hypothesis (prior: in-season fusion retrain gains ~nothing on fantasy):
- Fusion weights encode structural per-task module reliability — stable; +6..18 races of 2025 on a ~150-race
  base won't move the combination recipe. Base modules carry the in-season adaptation.
- Inheriting gold fusion is MORE leakage-safe: gold fusion = 2018-2024 LOSO only, zero 2025. Per-period
  fusion risks a 2025-partial LOSO fold bleeding into the weights.

Test post-run (cheap, inference-only — period base modules are saved + gold fusion config exists):
- For each period, re-fuse its saved base modules with the GOLD fusion config (instead of the period fusion),
  run the sampled-runtime comparison for the period rounds, fantasy-score, compare to the per-period-fusion
  result. If within noise across P1-P3 -> drop per-period LOSO/calibration; pipeline change: run the period
  gold-cycle with emit_fusion_train_rows="none" (base modules only) + assemble trained manifest from the
  inherited gold fusion + gold calibration. ~9x speedup for future walk-forwards.

Context data point (promoted gold, SAMPLED-RUNTIME path) — fusion vs no-fusion (NOT the per-period question):
- default (pre-fusion) season fantasy = 956.0 ; trained (gold fusion) = 849.0  -> gold fusion buys ~107 (~11%).
  So BASELINE fusion clearly matters; the open question is whether RE-deriving it in-season adds anything.

## B. Inference-PATH inconsistency (DISCOVERED — affects result interpretability)
Two inference paths give different fantasy scores for the SAME promoted (trained) model:
- FULL-EVIDENCE per-race export (params/gold/per_race_predictions): 707  <- baseline + human(711) comparison
  (readout-consistent: rank == position_distribution-mean, 707 both, top-10 identical 24/24)
- SAMPLED-RUNTIME backtest (rt_comparison .trained.json): 849 (the robustness path; averages degraded states)

The walk-forward orchestrator extracts P1-P3 from the SAMPLED-RUNTIME trained.json (~849 scale) but P0 reuses
the FULL-EVIDENCE per-race export (707 scale). => the committed summary.json will MIX scales and is NOT
directly comparable to the 707 baseline / 711 human.

TODO post-run (cheap, no re-train — period models are saved):
- Re-score all 24 races on ONE consistent path. Preferred: FULL-EVIDENCE for every period (comparable to
  707/711). For P1-P3 that means running the full-evidence per-race prediction on each saved period model
  for its eval rounds, then fantasy-scoring. Baseline stays 707 (full-evidence). Then the walk-forward vs
  707 delta is clean = the true value of in-season RETRAINING.
- Report both: full-evidence (vs 707/711) and sampled-runtime (vs 849) so the path effect is explicit.

## Data provenance
- DB actuals: data/f1_data_2025.db session_classifications R.
- Gold backtests: reports/evo/sampled_runtime_backtests/*.{default,trained}.json (sampled-runtime).
- Gold per-race (full-evidence): params/gold/per_race_predictions/round*.json.
- Walk-forward period predictions: outputs/walkforward_2025/p{1,2,3}/reports/sampled_runtime_backtests/*.trained.json
