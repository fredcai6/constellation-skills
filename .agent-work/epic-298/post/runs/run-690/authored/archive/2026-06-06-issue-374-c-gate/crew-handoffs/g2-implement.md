# Implementer Handoff — G2: models + LOSO CV + bootstrap CIs + measurement

## Gate
`g2`

## Task
Extend `scripts/fusion_replay/metalearner.py` (G1 already built `build_pairwise_dataset`) with the modelling + validation + measurement layer, plus a runner CLI. This produces, **per task**, the gate metric: the LOSO pairwise-log-loss skill gap `Δ_gap = Model1_loss − Model2_loss` with a 95% bootstrap CI over events, the #140 deviation nested-gain, and secondary rank/Spearman robustness numbers. NO production `src/evo_predictor/` changes.

## Protected Intent
This IS the Step-3 gate for epic #372. Model1 must be a GENUINE linear ceiling (the best precision-weighted pool over module pi), so that any positive `Δ_gap` is real interaction headroom — not a Model1 underfit. The decision rule is FROZEN (below); you implement and emit the numbers, you do NOT redefine thresholds or pick verdicts (the Commander applies the rule mechanically at integrate).

## Test Mode
TDD required. Write tests FIRST for: Model1 fit correctness on a synthetic separable fixture, leakage-free LOSO grouping (no event/season appears in both train and held-out), and bootstrap-CI machinery (resamples EVENTS not pairs; CI brackets the point estimate).

## Models (exact specs — these are decided, do not change)
All models operate on the G1 pairwise rows: `X_delta (n_pairs,4)`, optional `dev_delta (n_pairs,2)`, `y (n_pairs,)`, grouped by `event_ids`/`seasons`.

- **Model 1 — best linear pool.** Logistic over the 4 Δpi: `P(i beats j) = sigmoid(w · Δpi)`, **NO bias term** (a pair and its mirror are symmetric: swapping i,j negates Δpi and flips y, so an intercept would break antisymmetry). Fit by minimizing mean pairwise log-loss via `scipy.optimize.minimize` (L-BFGS-B; supply the analytic gradient — it is `Xᵀ(p−y)/n`). This is the CEILING of any precision-weighted fusion: any per-module linear weight on pi reduces to a single `w` on Δpi. Add tiny L2 (e.g. λ=1e-6) only if needed for conditioning; document it.
- **Model 2a — explicit interactions.** Same logistic objective + **no bias**, features = `[Δpi (4), all degree-2 products of the 4 Δpi components (10: 4 squares + 6 cross)]` = 14 features. Same scipy fit. (Squares of Δpi are symmetric under i↔j swap — sign of Δpi flips, square is invariant — so a pure-square term BREAKS antisymmetry unless paired correctly. Resolve this honestly: the clean antisymmetric degree-2 basis is the 6 CROSS products Δpi_a·Δpi_b (a<b) which flip sign correctly, PLUS the 4 linear terms. Squares do NOT flip sign and must be EXCLUDED from the antisymmetric pairwise model. Use the 4 linear + 6 cross = 10 features for Model2a. Document this reasoning in code — it is the subtle correctness point of the gate.)
- **Model 2b — small MLP (torch, CPU, seeded).** Input = the 4 Δpi. To preserve antisymmetry, enforce `f(−x) = −logit`, i.e. model the *logit* as an **odd function** of Δpi: e.g. `logit(x) = g(x) − g(−x)` for a small MLP g (2 hidden layers, ~16–32 units, tanh), then `p = sigmoid(logit)`. This guarantees a pair and its mirror give complementary probabilities. Seed torch; small epochs; Adam. Document the odd-function construction.

Report BOTH Model2 forms; `Δ_gap` uses the BETTER of {Model2a, Model2b} per task (state which won), AND report each separately.

## #140 deviation probe (nested gain)
Fit **Model1+dev** = logistic (no bias) over `[Δpi (4), dev_delta (2)]` (8 features) under the same LOSO protocol. Nested gain `Δ_dev = Model1_loss − (Model1+dev)_loss`. This tests whether weekend-vs-recent disagreement adds ordering power beyond the 4 main pi effects. (Note: dev_delta is a linear combination of Δpi columns — `dev = M[:,2]−M[:,0]` and `M[:,3]−M[:,1]` — so for a PURE-LINEAR Model1 the dev terms are collinear and add nothing by construction. Therefore the meaningful #140 probe is **dev × main interaction**: add the 2 dev columns AND their products with the 4 Δpi (cross terms only, antisymmetric) to Model1, and measure nested gain vs Model1. Document this: the linear-only dev test is a null by construction; the interaction form is the real hypothesis. Report the linear-dev nested gain too, labelled as the expected ~0 sanity check.)

## Downstream secondary probe (cheap, where records make it)
For race_start and race ONLY: add a `prior_stage_order` proxy interaction if cheaply available from the records — if NOT cheaply derivable from the existing arrays, SKIP it and note that it needs the sister commander's stage-order feature. Do not block on it. (The dev×main interaction above already covers the primary #140 hypothesis for all tasks.)

## Validation (mandatory)
- **LOSO CV** over seasons present in the data (expect 2018–2025 = 8 folds). For each fold: fit on all-other-season pairs, predict held-out season's pairs, pool held-out predictions, compute pooled pairwise log-loss PER TASK. Any standardization stats fit on TRAIN only.
- **Bootstrap CI over EVENTS** (not pairs): resample events with replacement (B≥1000), recompute the pooled `Δ_gap` from the held-out predictions restricted to resampled events, take the 2.5/97.5 percentiles. Same for `Δ_dev`.
- **PER TASK, never averaged across tasks.**

## Output artifact (emit this)
Write `outputs/evo_runs/issue-374-metalearner-results.json` (gitignored dir) with, per task:
`{n_events, n_pairs, model1_loss, model2a_loss, model2b_loss, gap_model2a, gap_model2b, gap_best (and which), gap_ci95:[lo,hi], dev_linear_gain, dev_interaction_gain, dev_interaction_ci95:[lo,hi], secondary rank_mae/spearman for Model1 vs Model2_best}` plus a `meta` block (B, seed, λ, seasons, torch/scipy versions). The Commander RUNS the CLI in foreground after you return.

## Runner CLI
`py -m scripts.fusion_replay.metalearner --records-dir outputs/evo_runs/issue-374-records --out outputs/evo_runs/issue-374-metalearner-results.json [--bootstrap 1000 --seed 0] [--tasks quali race_start race]` — runs the requested tasks (default all three), writes the JSON, prints a per-task summary table. **Provide a `--tasks` filter** so the Commander can run a single complete task while others are still generating; default to all three when omitted. The CLI must skip / clearly warn (not crash) for a task whose records are incomplete.

## SANITY CHECKS the Commander/reviewer will verify (build so these hold)
- Model1 pooled-LOSO pairwise-LL per task should be **≤ the #373 baseline** (quali 0.6489, race_start 0.6154, race 0.6400) — Model1 optimizes the weights that the #373 baseline fixed, so it must do at least as well in-sample and comparably out-of-fold. If Model1 is WORSE than baseline by a lot, the fit or alignment is broken — STOP and surface it.
- A pair and its mirror must give complementary probabilities under every model (antisymmetry unit test).
- Bootstrap CI must bracket the point estimate; resampling events (not pairs) — assert the resample unit is events in a test.

## Allowed Scope
- EDIT: `scripts/fusion_replay/metalearner.py` (extend G1 file)
- EDIT/EXTEND: `tests/unit/evo_predictor/test_metalearner.py`
- Import/call existing `scripts/fusion_replay/*`, `scripts/fusion_replay/scoring.py` (reuse `pairwise_log_loss`, `rank_mae`, `spearman` for the secondary metrics on pooled per-event predictions), `src/evo_predictor/*`.

## Specific Exclusions
- NO changes under `src/evo_predictor/` (frozen).
- NO sklearn (scipy.optimize + torch only).
- Do NOT redefine the decision-rule thresholds (τ_signif: CI excludes 0; τ_mag: Δ_gap ≥ 0.005 pairwise-LL). You emit numbers; the Commander applies the rule.
- Do NOT pick GREENLIGHT/DEFER verdicts — that is the Commander's mechanical step at integrate.

## Constraints
- `py` not `python`; tests `py -m pytest`.
- `PYTHONIOENCODING=utf-8` in any python subprocess whose output you capture (PowerShell: `$env:PYTHONIOENCODING='utf-8'`).
- torch CPU; MLP small + **seeded** (torch.manual_seed + numpy seed) for reproducibility. Keep total runtime modest (the Commander has a ≤2.5h compute budget for the whole gate; LOSO×3 tasks×(4 models)+1000 bootstrap should be well under that on CPU — vectorize the bootstrap).
- DB read-only at `C:/Programs/f1Brainz/data` (G1 already handles DB via the harness).
- Records at `outputs/evo_runs/issue-374-records`. **GENERATION STILL IN PROGRESS (Commander ground truth): `quali` and `race_start` are FULLY generated (4 modules × 8 seasons each, ~173 events each); `race` is still being written (its last module may be absent).** For your TDD + smoke run, use the **`quali`** task (complete, known-good, 173 events). Do NOT run the full 3-task measurement and do NOT smoke-run `race` — the Commander runs the full measurement in foreground once `race` completes. Your smoke run = ONE task (`quali`) with `--bootstrap 50` to prove the CLI/JSON shape end-to-end.

## Required Evidence
- `py -m pytest tests/unit/evo_predictor/test_metalearner.py -q` GREEN, output pasted.
- Do NOT run the full measurement yourself (the Commander runs it foreground). But DO paste a short smoke run on ONE COMPLETE task (`--tasks quali --bootstrap 50`) proving the CLI produces the JSON shape end-to-end. Do NOT smoke-run `race` (still generating).

## Suggested Model Tier
strongest — reason: antisymmetry-correct interaction bases, leakage-free LOSO, event-level bootstrap, and a genuinely-optimal linear ceiling are all subtle; a quiet error here produces a wrong epic-level verdict.

## Authority
- Decision rule, target (pairwise-LL), validation (LOSO + event bootstrap), per-task reporting are DECIDED (problem_statement.md). Do not redefine.
- You decide: optimizer details, MLP architecture within "small+seeded+odd", JSON field names (keep them self-describing), test fixtures, bootstrap vectorization.

## Stop Conditions
Stop and return if: you must touch `src/evo_predictor/`; Model1 cannot reach ≤~#373 baseline on any task (alignment/fit bug); antisymmetry cannot be enforced for a model form; or LOSO leaves a fold with too few events to fit.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence (paste test output + smoke-run JSON), assumptions, stop conditions hit, out-of-scope observations.
