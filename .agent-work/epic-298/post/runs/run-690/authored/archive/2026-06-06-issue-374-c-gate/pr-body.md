## What this answers (plain English)

Before we spend effort building a fancy "context-conditioned" fusion network (#375), this PR settles a prerequisite question with a measurement: **is there ordering signal hiding in the *interactions* between our four module outputs that a simple weighted blend can't capture?**

The answer is **yes for the two race-day predictions, no for qualifying**:

- **Race-start ordering: GREENLIGHT** - a flexible model finds real, significant extra ordering skill (+1.23 percentage points of pairwise log-loss) beyond the best possible linear blend.
- **Race ordering: GREENLIGHT** - same story, +0.62pp, also significant.
- **Qualifying ordering: DEFER** - the extra skill is tiny (+0.05pp) and not statistically distinguishable from zero, so a bespoke conditioned net is not justified *for quali* on this evidence.

So the recommendation for **#375 is: build it, but scope it to the two downstream tasks (race-start and race); hold off for quali.**

Two important nuances:
1. The extra skill is only found by a **flexible neural model**, not by adding simple "multiply two modules together" terms - so the structure is genuinely non-linear, which is exactly what a conditioned net is good at.
2. This is a **conservative lower bound**. The meta-learner only sees the four module *outputs*. Wave-1 issue #414 already proved qualifying has useful information *below* that layer (a cross-channel practice-pace anchor recovered ~68-72% of a 19pp head gap) that this measurement cannot see. So "DEFER quali" means "no extra juice in the module outputs themselves," **not** "quali is already optimal" - the #414 anchor remains the cheaper proven lever there.

The #140 hypothesis (that "upgrades / track-fit" show up as weekend-vs-recent-form disagreement) was also tested: **no** - that deviation signal adds no ordering power beyond the main effects on any task.

## How it was measured (technical)

This is a measurement/decision issue (the Step-3 gate for epic #372), not a feature build. **No production `src/evo_predictor/` code changed** - all new code is under `scripts/fusion_replay/` with tests under `tests/unit/evo_predictor/`.

- **Data builder** (`scripts/fusion_replay/metalearner.py::build_pairwise_dataset`) reuses the #373 scorecard harness (`_preprocess_events`, `_build_module_field_results`, `_align_driver_pi`, `project_constructor_field_to_drivers`) so each module's pi is aligned exactly as the production scoring path sees it. Coverage = **173 events/task** for all three tasks (matches #373). Per event it emits one row per unordered driver pair (i<j, distinct finishing positions) with features = the four module **Delta-pi** and per-scope deviation differences; label = who-finished-ahead.
- **Model 1 (the ceiling):** no-bias logistic over the 4 Delta-pi (scipy L-BFGS-B). No bias -> exactly antisymmetric. Any precision-weighted linear pool reduces to a weight vector on Delta-pi, so this is the best linear pool by construction.
- **Model 2 (interaction):** *2a* = 4 linear + 6 degree-2 cross products; *2b* = a small seeded torch MLP whose logit is an **exact odd function** of Delta-pi (`g(x)-g(-x)`), preserving antisymmetry regardless of learned weights.
- **Validation:** leave-one-season-out CV (2018-2025, 8 folds); the gate statistic is the event-mean-of-means pairwise-LL skill gap `Delta_gap = Model1 - Model2`, with a **95% cluster bootstrap over events** (B=1000, seed=0). Per task, never averaged.
- **Frozen decision rule** (set before measuring): GREENLIGHT iff `Delta_gap >= 0.005` AND the 95% CI excludes 0; else DEFER. tau_mag=0.005 is ~1/3 of the smallest #373 fusion-tuning lever.

### Results (LOSO, B=1000)

| Task | Model1 LL | Delta_gap (best M2) | 95% CI (events) | Verdict |
|---|---|---|---|---|
| quali | 0.46440 | +0.00054 (M2b) | [-0.00103, +0.00239] | **DEFER** |
| race_start | 0.33702 | +0.01230 (M2b) | [+0.00810, +0.01683] | **GREENLIGHT** |
| race | 0.47799 | +0.00624 (M2b) | [+0.00364, +0.00892] | **GREENLIGHT** |

Sanity: Model1's pooled pairwise-LL is below the #373 baselines on every task (quali 0.6489, race_start 0.6154, race 0.6400), confirming it is a fair (strong) linear ceiling. The signal is carried only by the antisymmetric MLP (Model2b); explicit degree-2 cross products (Model2a) add nothing (gaps <= 0), and an independent review confirmed Model2a's non-antisymmetry is not faking a positive (its gap is non-positive and collapses under mirror-symmetrization). #140 deviation interaction is not significant on any task (all CIs include 0).

### Rigor

- TDD throughout; **28 unit tests** (Model1 fit correctness, exact antisymmetry for Model1/Model2b, leakage-free LOSO grouping, event-not-pair bootstrap, deviation-feature math, real-record coverage).
- Two independent reviewer passes (G1 data-builder, G2 models) that **re-derived** the key numbers by independent code paths (Model1 LOSO loss matched to 0.0e+00; quali gaps reproduced; coverage and dev feature confirmed to 1e-9).
- One bug fixed in-run (OddMLP epoch-shuffle generator was re-seeded each epoch -> identical batch order); the fix only made the result more conservative.
- Findings appended to `docs/evo/fusion_rework_findings.md` (the #374 section).

Reproduce:
```
py -m scripts.fusion_replay.generate_records --out-dir outputs/evo_runs/issue-374-records --years 2018..2025
py -m scripts.fusion_replay.metalearner --records-dir outputs/evo_runs/issue-374-records --out outputs/evo_runs/issue-374-metalearner-results.json --bootstrap 1000 --seed 0
py -m pytest tests/unit/evo_predictor/test_metalearner.py -q
```

Closes #374

🤖 Generated with [Claude Code](https://claude.com/claude-code)
