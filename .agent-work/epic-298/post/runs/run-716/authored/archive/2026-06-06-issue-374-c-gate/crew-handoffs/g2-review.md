# Reviewer Handoff — G2: models + LOSO CV + bootstrap CIs + measurement

## Gate
`g2`

## What Was Implemented
`scripts/fusion_replay/metalearner.py` extended (G2 layer below the `# G2` banner, ~line 231 onward) with: Model1 (no-bias logistic over 4 Δpi via scipy L-BFGS-B = the linear-pool ceiling), Model2a (4 linear + 6 cross-product Δpi features, same logistic), Model2b (`_OddMLP`: logit = g(x)−g(−x), exactly antisymmetric, torch CPU seeded), LOSO 8-fold CV (`_loso_cv_linear`, `_loso_cv_mlp`), event-level bootstrap CI (`_bootstrap_gap_ci`), #140 deviation probe (linear null + dev×Δpi interaction), secondary rank-MAE/Spearman, `run_task`, and a CLI `_main`. `tests/unit/evo_predictor/test_metalearner.py` extended to 28 tests (all pass).

## How to Inspect the Diff
```powershell
Set-Location C:/Programs/f1Brainz/.claude/worktrees/agent-ade67b306f11aa4fb
git status --short
git diff --stat
# metalearner.py is untracked (new this run); read it in full, focus lines 231-end:
```
Read `scripts/fusion_replay/metalearner.py` from ~L231 to end. Read `tests/unit/evo_predictor/test_metalearner.py` in full. Harness scoring helpers you may reuse for an independent recompute: `scripts/fusion_replay/scoring.py`.

## Task Statement
Per task, produce the gate metric Δ_gap = Model1_loss − Model2_loss (LOSO pooled held-out pairwise log-loss, Model2 = better of {2a,2b}), with a 95% bootstrap CI over EVENTS; plus the #140 deviation nested gain (interaction form) with its own event-bootstrap CI; plus secondary rank-MAE/Spearman. Model1 must be a GENUINE linear ceiling so any positive Δ_gap is real interaction headroom, not a Model1 underfit. Decision-rule thresholds are FROZEN (τ_signif: CI excludes 0; τ_mag: Δ_gap ≥ 0.005 pairwise-LL) — the implementer emits numbers; the Commander applies the rule.

## Close Criteria (RE-DERIVE — do not trust the implementer's prose)
- **C1 — Model1 is a genuine linear ceiling.** Confirm Model1 = no-bias logistic over exactly the 4 Δpi, fit to minimize mean pairwise log-loss (analytic grad `Xᵀ(p−y)/n + λw`, λ=1e-6). No interaction/extra features leak into Model1. INDEPENDENTLY recompute Model1's pooled-LOSO loss for ONE task (quali): build the dataset, run your own 8-fold LOSO logistic fit (you may use scipy directly), pool held-out logits, compute mean log-loss, and assert it matches the builder's `model1_loss` to ~1e-3.
- **C2 — Model1 ≤ #373 baseline (sanity).** quali ≤ 0.6489, race_start ≤ 0.6154, race ≤ 0.6400 (pooled-LOSO; Model1 optimizes the weights #373 fixed, so it must be ≤ baseline up to CV noise). If Model1 is materially WORSE, the fit/alignment is broken — BLOCK. Report the three Model1 losses you observe from a real run.
- **C3 — LOSO is leakage-free.** For each fold, the held-out season's pairs are NEVER in the training mask; standardization (Model2b scale-std) is computed on the TRAIN fold only. Verify by reading `_loso_cv_linear`/`_loso_cv_mlp` and by asserting (independent snippet) that for a held-out season, no training row carries that season.
- **C4 — Bootstrap resamples EVENTS not pairs.** Read `_bootstrap_gap_ci`: the resample unit is `unique_events`, pooling all pairs of each drawn event. Verify the CI brackets the point estimate. INDEPENDENTLY re-derive ONE task's gap_best CI by your own event-bootstrap (resample events, recompute mean per-pair gap) with the same B/seed and confirm the lo/hi match to ~1e-3 (or overlap closely given RNG-stream differences — if you use a different RNG, assert your CI brackets the point estimate and is the same order of magnitude).
- **C5 — Δ_gap correctness + RE-DERIVE one task.** `gap_best = model1_loss − min(model2a,model2b)_loss`, sign convention positive = Model2 better. INDEPENDENTLY recompute, for quali, BOTH gap_model2a and gap_model2b from your own LOSO runs of Model1, Model2a (4 linear + 6 cross), and Model2b (or at minimum Model2a, which is deterministic scipy — Model2b is torch/seed-sensitive so an approximate match is acceptable). Confirm the builder's `gap_model2a` matches yours to ~1e-3.
- **C6 — #140 deviation probe is a proper nested comparison.** `dev_linear_gain` must be ≈0 (the implementer asserts dev_delta is a linear combination of Δpi → collinear → null by construction; verify dev[:,0]=X[:,2]−X[:,0], dev[:,1]=X[:,3]−X[:,1] and that the linear gain is ~1e-6). The REAL probe `dev_interaction_gain` adds dev×Δpi cross terms (8) to Model1; verify it is a nested superset of Model1's features (Model1 ⊂ Model1+dev-interaction) so the gain is interpretable, and that its CI is event-bootstrap.
- **C7 — Model2a non-antisymmetry: is the gap REAL or an artifact? (CRITICAL — Commander flagged this).** The implementer correctly notes cross-products Δpi_a·Δpi_b are EVEN under i↔j swap, so Model2a's logit is NOT antisymmetric, whereas Model1 (odd, no bias) IS. RISK: on one-sided i<j data with y-mean ≠ 0.5, an even feature (or an implicit even component) can fit the marginal class imbalance in a way the odd Model1 cannot — manufacturing a positive `gap_model2a` that is NOT ordering-interaction signal. INVESTIGATE: (a) report the y-mean per task (one-sided imbalance); (b) check whether Model2a's advantage over Model1, if any, survives when you symmetrize — e.g. augment the data with mirror rows (−Δpi, 1−y) and refit Model2a; does the gap persist? (c) Confirm Model2b (the EXACTLY antisymmetric OddMLP) is the trustworthy interaction probe and report its gap separately. State clearly in your verdict: for each task, is the interaction signal present under the ANTISYMMETRIC Model2b (the conservative, correct probe), independent of Model2a.
- **C8 — antisymmetry tests are real.** `test_model1_antisymmetry` and `test_model2b_antisymmetry` assert P(i>j)+P(j>i)=1 (logit(−x)=−logit(x)). Confirm they actually exercise a swap and that Model2b's holds to <1e-5. (Model2a has NO antisymmetry test — confirm that omission is intentional and documented, per C7.)
- **C9 — tests green.** `py -m pytest tests/unit/evo_predictor/test_metalearner.py -q` → 28 passed (Commander re-ran: 28 passed in 3.69s). Confirm.
- **C10 — scope clean.** `git diff` shows ZERO `src/evo_predictor/` edits. No sklearn import (scipy.optimize + torch only). Confirm.

## Allowed Scope
EDIT `scripts/fusion_replay/metalearner.py`, `tests/unit/evo_predictor/test_metalearner.py`. May import existing `scripts/fusion_replay/*`, `src/evo_predictor/*` for your independent recompute.

## Specific Exclusions (flag if touched)
- NO `src/evo_predictor/` edits. NO sklearn. The implementer must NOT have redefined the frozen thresholds or picked GREENLIGHT/DEFER verdicts (that is the Commander's step) — flag if it did.

## Constraints the Implementation Must Respect (each a review check)
- `py` not `python`; `PYTHONIOENCODING=utf-8` in any captured python subprocess (set it in YOUR shell before running anything).
- torch CPU, MLP small + seeded (torch.manual_seed + numpy seed) — verify reproducibility (same seed → same logits).
- LOSO mandatory; CIs bootstrap over events; per-task never averaged across tasks.
- DB read-only at `C:/Programs/f1Brainz/data` (handled inside the harness via the G1 builder).
- Records complete at `outputs/evo_runs/issue-374-records` (all 3 tasks now generated — you MAY run the full thing, but a single-task independent recompute on quali suffices for C1/C4/C5; keep runtime modest, e.g. `--bootstrap 200` for your own spot-checks).

## Evidence Produced (from IMPLEMENTER_RESULT — verify)
- `py -m pytest tests/unit/evo_predictor/test_metalearner.py -q` → 28 passed.
- Implementer's documented design: Model1 no-bias scipy; Model2a 4+6 (cross, even — non-antisymmetric, documented); Model2b OddMLP scale-only-norm antisymmetry <1e-5; LOSO 8-fold; event-bootstrap with >2× CI-width ratio test; dev_linear_gain ≈ −7.7e-7 (null), dev interaction = real probe. Smoke claim: "Model2b positive gap on all three tasks at low B; CIs might exclude 0 at B=1000."

## Suggested Model Tier
strongest — reason: this verdict drives an epic-level greenlight/defer. A quiet error in Model1's optimality, LOSO leakage, the event-bootstrap unit, or the Model2a-artifact question produces a wrong gate. RE-DERIVE quali's gap and Model1 loss by an independent code path; do not merely re-read.

## Stop Conditions
Stop and return BLOCK if: Model1 is not a genuine 4-Δpi no-bias ceiling; Model1 materially exceeds the #373 baseline (alignment/fit bug); LOSO leaks; bootstrap resamples pairs not events; the deviation probe is not a proper nested comparison; you cannot reproduce quali's gap to ~1e-3 (Model2a/Model1 deterministic parts); OR you find the Model2a gap is a class-imbalance artifact AND Model2b shows no signal (in which case the "interaction headroom" claim would be unsupported — report this as a finding, it directly affects the verdict, but it is not necessarily a code BLOCK; distinguish "code correct, signal absent" from "code wrong").

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings C1–C10 with the NUMBERS you independently re-derived (especially: the three Model1 losses vs baselines; quali gap_model2a + gap_model2b re-derived; the y-mean per task; whether the antisymmetric Model2b shows a gap per task and its sign/magnitude), blockers, out-of-scope observations.
