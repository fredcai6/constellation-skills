# Implementer Handoff — Clean, leakage-free, PRE-QUALI fantasy backtest: 2022–2025

## Context (read carefully — there was a leakage incident)
We need **leakage-free, pre-qualifying** fantasy scores for **2022, 2023, 2024, 2025** to compare against
human results. Two hard-won facts:
- **DO NOT TRUST `params/gold/per_race_predictions/` — IT IS LEAKED.** Those files are from a March
  `train-evo-pipeline` run whose `run.log` says `Train years: [2022,2023,2024,2025], Eval year: 2025`
  (trained on the eval season). Never use them.
- The **clean** model is the Jun-8 latent-power gold: `train_years=[2018..2024], eval_year=2025`
  (`reports/evo/gold_cycle_260608_043414_2018thru2024.summary.json`). Its sampled-state 2025 fantasy is
  ~849 (from `reports/evo/sampled_runtime_backtests/...2018-...-2024_eval_2025.trained.json`).

Pick deadline is **pre-qualifying**, so the fair model readout must use **practice only, NOT actual
qualifying** results. The project's design point is pre-quali (FP1/FP2/FP3).

## Task
Produce a clean table — **model fantasy vs human**, leakage-free, pre-quali — for 2022/2023/2024/2025.
Human refs: **2022=739, 2023=632, 2024=615, 2025=711** (lower=better, same scoring as
`src/fantasy_scoring/scoring_rules.py`).

### Step 1 (BLOCKING) — Determine the evidence model with EVIDENCE
Definitively answer: does the `sampled-backtest --mode sampled_state` path feed the model **actual
qualifying** results, or does it predict quali/start from **practice only** (pre-quali)?
- The `oracle_grid`/`oracle_all_states` modes inject actual grid (`sampled_backtest.py:638-643`) — those are
  the leaky/ceiling modes; confirm `sampled_state` does NOT.
- Check `sample_state_adapter.py` (the `source='quali_order'` vs sampled-start logic) and how race_start
  evidence is built. Read the code; cite file:line.
- Conclusion: either (a) `sampled_state` IS pre-quali → use it directly; or (b) it uses observed quali → use
  a practice-only evidence restriction (e.g. an `fp*`/no-quali eval set or the appropriate config) so the
  prediction is genuinely pre-quali. Report which, with proof.

### Step 2 — Clean 2025 number (the anchor)
Using the clean Jun-8 gold (bundles at `params/gold/runtime_bundles/gold_cycle_260608_043414_2018thru2024`
+ fusion `params/gold/fusion/fusion_260608_084626_2018thru2024.json`, or its committed manifest
`reports/evo/fusion_260608_084626_2018thru2024.sampled_runtime_manifest.json`), compute the **pre-quali**
fantasy season score for 2025 (per Step 1's verdict). Sanity: if sampled_state is pre-quali, this should be
~849. Compare to human 711.

### Step 3 — 2022/2023/2024 via LOSO folds (leakage-free by construction)
The gold cycle saved leave-one-season-out fold models on disk:
`outputs/evo_runs/gold_module_training_cycle/loso_folds/heldout_<Y>/modules/` (12 modules each, trained on
the OTHER seasons — i.e. WITHOUT Y). For each Y in {2022, 2023, 2024}:
1. **VERIFY leakage-free:** confirm the heldout_<Y> module bundles' training years EXCLUDE Y (read a module
   manifest). If any include Y, STOP and report.
2. Assemble a v4 sampled-runtime manifest from the heldout_<Y> modules
   (`py -m src.evo_predictor.run assemble-sampled-runtime-manifest ...`), fused with the gold fusion config
   (`params/gold/fusion/fusion_...json`). NOTE the one caveat in your report: gold fusion was trained on LOSO
   that structurally saw Y's OOF metrics — acceptable for a first pass (fusion is structural), flag as a
   follow-up for strict per-season-holdout fusion.
3. Run the **pre-quali** backtest (per Step 1) for season Y over its races, extract per-race top-10
   (position_distribution by ascending mean, the established rule), fantasy-score vs DB actuals
   (`data/f1_data_<Y>.db`, `session_classifications` R).

### Step 4 — Report
A committed artifact under `reports/walkforward/multiseason_fantasy.{json,md}` and a clear table:

| Season | model (leakage-free, pre-quali) | human | delta |
| 2022 | ? | 739 | ? |
| 2023 | ? | 632 | ? |
| 2024 | ? | 615 | ? |
| 2025 | ? | 711 | ? |

Plus: the Step-1 evidence-model verdict (with file:line proof), and a provenance block confirming every model
used excludes its eval season and NO leaked March artifact was touched.

## Constraints
- DB-only; `py` not `python`; run from repo root. Reuse `src/fantasy_scoring/` (season.py aggregator +
  scoring_rules); do not re-implement scoring. `simplification_limits` on any touched src/tests.
- This is INFERENCE only (the LOSO models are trained) — NO retraining, no gold cycle.
- Leakage discipline is paramount. Verify, don't assume. If anything is ambiguous, surface it, don't paper over.

## Suggested Model Tier
`stronger` — leakage-critical, evidence-model determination, multi-artifact provenance.

## Return Format
IMPLEMENTER_RESULT: the table, the Step-1 verdict with proof, per-season provenance verification, files
written, commands run (paste key outputs), assumptions/caveats, anything ambiguous. Do NOT commit.
