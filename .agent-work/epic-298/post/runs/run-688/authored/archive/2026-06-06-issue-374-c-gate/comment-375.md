## Gate input from #374 (Step-3 interaction-headroom measurement)

The #374 gate measured whether interactions over the four module outputs carry ordering signal that the best linear opinion pool leaves behind. Result (PR #418; full verdict on #374; details in `docs/evo/fusion_rework_findings.md`):

**GREENLIGHT this conditioned net - but scope it to the two downstream tasks: `race_start` and `race`. DEFER it for `quali`.**

| Task | Interaction skill gap (LOSO, B=1000) | 95% CI | Verdict |
|---|---|---|---|
| race_start | **+0.01230** pairwise-LL | [+0.00810, +0.01683] | GREENLIGHT |
| race | **+0.00624** pairwise-LL | [+0.00364, +0.00892] | GREENLIGHT |
| quali | +0.00054 pairwise-LL | [-0.00103, +0.00239] | DEFER (not significant) |

Two design implications for #375 when you build it:

1. **The signal is non-linear / non-multiplicative.** It was found only by an antisymmetric MLP; explicit degree-2 cross-product terms added nothing. A fixed product-term head will likely miss it - favour a flexible (small) network. If you operate on pairwise Delta-pi, make the head **antisymmetric by construction** (e.g. `logit(x) = g(x) - g(-x)`), as the gate's Model2b did - this guarantees a pair and its mirror give complementary probabilities.
2. **The #140 deviation feature (weekend - recent) is not the carrier.** It added no ordering power beyond main effects on any task, so don't anchor the conditioned net's design on that hypothesis.

**On quali (DEFER is conservative, not "done").** The gate sees only module outputs; #414 showed quali has real information below that layer (a cross-channel practice-pace anchor recovering ~68-72% of the race_weekend head's ~19pp gap). The cheaper, proven quali lever is that anchor - revisit a conditioned quali net only after richer features are exposed to the fusion layer or the #414 anchor is exhausted.
