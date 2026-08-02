# Student-t Phase 4 — Calibration Sweep Findings & Rule Decision

**Date:** 2026-06-01
**Status:** HITL decision pending (evidence below)
**Harness:** `src/calibration` (`baseline` + `sweep` subcommands)
**Bundle:** `gold_cycle_260531_051234_2018thru2024`, held-out eval year **2025**, `nu_loss = 4.0`
**Reports:** `reports/calibration/baseline_*_eval2025.json`, `reports/calibration/sweep_*_eval2025.json`

## What was measured

Per latent-power task (12 in the bundle), on held-out 2025 pairs, each task's
`(mu, sigma, target)` was scored under:

- **Gaussian** (the pre-migration assumption — the gate baseline),
- a **fixed-`nu` grid** `{2.5, 3.0, 3.5, 4.0}` spanning the adaptive range
  `[nu_prior, nu_loss]` (pure aleatoric `t(nu)`, no epistemic inflation — isolates
  tail shape), and
- the **per-task MLE `nu_fit`** of the standardized residuals (the "fully trust the
  fitted tail" extreme the `HybridRule` shrinks toward).

Gate = interval coverage (PIT). Score = CRPS. Dashboard = `|r/sigma|` tail quantiles.

## Headline results

**Gaussian under-covers every task.** `|r/sigma|` p95 = 2.2–3.1 (vs the Gaussian
1.96) and p99 = 2.9–4.6: real fat tails the Gaussian misses. Coverage @0.90 lands
0.79–0.87; @0.95 lands 0.87–0.92.

**Student-t `t(4)` is the best-calibrating arm**, by mean absolute coverage error
across tasks:

| arm       | mean \|cov−0.90\| | mean \|cov−0.95\| |
|-----------|------------------:|------------------:|
| Gaussian  | 0.069             | 0.058             |
| t(2.5)    | 0.053             | 0.037             |
| t(3.0)    | 0.038             | 0.030             |
| t(3.5)    | 0.026             | 0.022             |
| **t(4.0)**| **0.018**         | **0.017**         |
| MLE fit   | 0.038             | 0.026             |

- **`best_nu` @0.90 = 4.0 for 11/12 tasks** (3.5 for the 12th, marginally).
- Fattening below the floor (`nu` 2.5–3.5) **over-covers** these data-rich tasks —
  epistemic widening is not needed where `n_eff` is large, exactly as designed.
- **CRPS is within ~0.5% across Gaussian / t(4) / fit** for every task (the t-arm's
  tiny excess is the known MC upward bias). Student-t fixes coverage at no CRPS cost.

**The MLE fit (hybrid) is actively unhelpful here.** It is *worse* than the formula's
`nu=4` clamp on **8/12 tasks**. For the quali tasks the residual MLE reads near-Gaussian
(`nu_fit` 20–200) and so **under-covers** (≈0.82–0.84 @0.90) — far worse than the t(4)
floor (0.90–0.94) — because most quali mass is tight while the damaging tail is sparse.
A global df MLE is the wrong lens for these spiky-but-fat-tailed residuals.

## Decision (made — HITL approved 2026-06-01)

1. **Ship `FormulaRule`; remove the `HybridRule`/MLE machinery entirely.**
   The design explicitly licensed this: "if Phase 4 shows the plain formula matches on
   coverage, we ship the formula and treat the MLE machinery as not worth its
   complexity." The evidence is stronger than "matches" — the formula's `nu=4` clamp is
   the single best arm and the MLE degrades 8/12 tasks. `HybridRule`, the `nu_fit`
   plumbing through `predictive_t`/`TailRule`, and the sweep's residual-MLE fit arm were
   deleted; the resolved two-sided-floor concern is recorded here for the record rather
   than carried as dead code.

2. **Lock the Phase-0 defaults — they are the right operating point.**
   `nu_prior = 2.5`, `k = 1.0`, `nu_loss = 4.0`. For these data-rich backtest tasks
   (`n_eff` large) `FormulaRule` rides `nu_loss = 4`, which calibrates near-perfectly.
   The epistemic fattening (`nu < 4`) only bites at small `n_eff` — correct for the
   data-starved early-season / sparse-compound cases the design targets (not exercised
   by this data-rich 2025 eval, so kept at the theory-matched defaults rather than
   retuned downward against tasks that don't need it).

### Note on the resolved HybridRule floor concern (now removed with the rule)

The Phase-0 concern was that a pathological small-sample MLE `nu_fit` could pull the
blended `nu` *above* the formula value, thinning the tail below the intended fat-tail
floor for data-starved tasks. The implemented resolution (before removal) was a
two-sided floor — clamp the blend at the formula value so the MLE may only fatten below
it — plus a `min_n_eff_for_fit` guard that drops the fit entirely below a minimum
effective sample size. With the hybrid dropped in favor of the formula, this is moot;
it is documented here so the concern is not re-discovered as open.

## Caveats / open notes

- Quali tasks are mildly *over*-covered at `t(4)` (e.g. 0.95→0.97–0.99). A slightly
  thinner floor (`nu≈5–6`) would tighten them, but `nu_loss` is the trained aleatoric
  loss `nu` (ADR-0008, fixed global 4); retuning it reopens the loss and is out of
  scope. Over-coverage is the conservative direction — preferred over under-coverage.
- This eval year (2025) is data-rich. The epistemic layer's value is in the
  data-starved regime; that is asserted by construction (the `[nu_prior, nu_loss]`
  range + `√(1+1/n_eff)` scale inflation) and unit-tested, but not exercised by this
  particular backtest. A future sweep on an early-season / sparse-compound slice would
  measure it directly.
