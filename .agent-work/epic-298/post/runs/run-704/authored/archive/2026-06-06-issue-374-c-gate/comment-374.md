## Gate verdict (#374 - Step-3 interaction-headroom gate)

**Measured, decided, and applied mechanically against the frozen decision rule.** PR: #418. Findings: `docs/evo/fusion_rework_findings.md` (#374 section).

### Per-task verdict

| Task | Delta_gap (best Model2) | 95% CI (event bootstrap) | tau_signif (CI excl 0) | tau_mag (>=0.005) | **Verdict** |
|---|---|---|---|---|---|
| quali | +0.00054 | [-0.00103, +0.00239] | NO | NO | **DEFER** |
| race_start | +0.01230 | [+0.00810, +0.01683] | YES | YES | **GREENLIGHT** |
| race | +0.00624 | [+0.00364, +0.00892] | YES | YES | **GREENLIGHT** |

(LOSO over 2018-2025, B=1000, seed=0, 173 events/task. Model1 = no-bias logistic over the 4 module Delta-pi = best linear pool; gap vs the better of Model2a/Model2b.)

### Overall recommendation for #375

**GREENLIGHT the context-conditioned net (#375), scoped to {race_start, race}. DEFER it for quali.**

### Key findings

- **The signal is non-linear.** It is found only by the antisymmetric MLP (Model2b); explicit degree-2 cross-products of Delta-pi (Model2a) add nothing on any task (gaps <= 0). So the exploitable structure is higher-order / non-multiplicative - precisely what a flexible conditioned net is suited to, and not something a hand-specified product-term blend would recover.
- **#140 deviation probe: ABSENT on all tasks.** Weekend-minus-recent disagreement adds no ordering power beyond the four main pi effects (linear gain ~0 by construction; interaction gain not significant: quali +0.00033 / race_start -0.00005 / race -0.00029, all CIs include 0).
- **Sanity holds.** Model1's pooled pairwise-LL is below the #373 baselines (quali 0.6489, race_start 0.6154, race 0.6400) on every task, so it is a fair (strong) ceiling - any positive gap is genuine interaction headroom, not a Model1 underfit. Independently re-derived by review (Model1 LOSO loss matched to 0.0e+00).

### Lower-bound caveat (why DEFER-quali is conservative, not exoneration)

The meta-learner sees ONLY the four module outputs. Wave-1 #414 demonstrated that quali has real feature-level information *below* this layer (a cross-channel practice-pace anchor recovered ~68% overall / ~72% EASY of the race_weekend head's ~19pp gap at alpha=0.5; magnitude-only recalibration was an exact no-op). That win happened below the module-output layer and is invisible to this measurement, so the gate **under-counts** true headroom. Quali's DEFER means "no extra ordering signal in the module outputs themselves," not "quali is optimal." The banked #414 anchor remains the cheaper, proven quali lever; a conditioned quali net should wait until richer features are exposed to the meta-learner or that anchor is exhausted. For race_start and race the positive result stands on its own (a lower bound that already clears the bar).

### Method / reproducibility

Scripts + tests + findings only; no `src/evo_predictor/` changes. Data-builder reuses the #373 scorecard harness for alignment/lineage. 28 unit tests (Model1 fit, exact antisymmetry for Model1/Model2b, leakage-free LOSO, event-not-pair bootstrap, deviation math). Two independent reviewer passes re-derived the numbers. One in-run fix (OddMLP epoch-shuffle generator re-seeded each epoch) that only made the result more conservative.

```
py -m scripts.fusion_replay.metalearner --records-dir outputs/evo_runs/issue-374-records --out outputs/evo_runs/issue-374-metalearner-results.json --bootstrap 1000 --seed 0
```
