# Student-t Migration: Sample-Adaptive Tails — Design

**Date:** 2026-05-31
**Status:** Approved design, pending spec review
**Topic:** Complete the Gaussian → Student-t migration and add a principled, sample-size-aware method for tuning tail fatness.

## Problem

The codebase is migrating distributional modeling from Gaussian to Student-t, but two gaps remain:

1. **Thoroughness.** Student-t currently lives in exactly one place — the latent-power loss
   (`student_t_nll` in `src/latent_power/losses.py`, fixed global `nu=4.0` from
   `src/latent_power/config.py`, per ADR-0008). Everything else that produces samples or
   intervals is still Gaussian or empirical. Most notably there is a **train/inference
   consistency leak**: `src/fantasy_scoring/expected_assignment.py` learns `sigma` under a
   Student-t likelihood but then samples scenarios with `rng.normal(...)` — fat tails fit,
   thin tails sampled. Similar collapses exist in the quali simulator (`norm.cdf`,
   `src/simulation/quali_simulator.py:167`), tire-wear confidence intervals (hardcoded
   `1.96·sigma`), gold-cycle calibration, and `mean ± k·sigma` visualization bands.

2. **No tuning method for tail fatness vs data volume.** The single global `nu=4` is applied
   identically across ~15 latent-power modules plus the compound-prior and physics estimators,
   whose effective sample sizes span roughly three orders of magnitude (early-season
   recent-history modules near `n_eff≈0`; sparse tyre compounds C4–C6 with <50k segments;
   data-rich race-weekend modules with ~33k pairwise labels). Tails do not adapt to how much
   data backs each estimate.

## Key Conceptual Distinction (the crux)

"Fat tails" arise from two independent sources that tune oppositely:

- **Aleatoric** — the phenomenon itself is heavy-tailed (driver error, safety car, mechanical
  failure). Its true tail heaviness is a property of the world; more data lets you *estimate*
  it better but does not change it. This is what the loss `nu` represents.
- **Epistemic** — you have little data, so your own `sigma`/`mu` estimate is uncertain. This is
  the classical origin of the Student-t: estimating variance from `n` samples yields a
  predictive `t` with `nu = n − 1`. Small `n` → low `nu` → fat tails; large `n` → `nu → ∞` →
  Gaussian.

"Tune the tails by the population available" is purely the **epistemic** story, and it is
currently implemented **nowhere**. The global `nu=4` is an aleatoric knob. This design adds the
missing epistemic layer without disturbing the aleatoric one.

## Design Decisions

### Fork 1 — Where adaptive `nu` lives: split by layer (chosen)

The loss keeps its fixed global `nu` (ADR-0008 untouched, gradients stay cheap) as the
**aleatoric** knob. All **sample-size adaptivity** lives in a new **predictive/interval layer**
that inflates tails based on `n_eff` (the **epistemic** knob). The two compose: the predictive
distribution is the aleatoric `t(nu_loss, sigma)` widened by parameter uncertainty, approximated
as a single Student-t with a blended effective `nu` and inflated scale.

Rejected alternative: making the loss `nu` itself data-adaptive. This reopens ADR-0008 — the
`nu`-dependent NLL constants stop dropping out, gradients get more expensive, and loss values
become incomparable across batches. High cost, conflates the two tail sources.

### Fork 2 — The tuning rule: hybrid (chosen), validated empirically

`nu(n_eff)` is a **pluggable strategy** behind one interface. Two implementations:

- **FormulaRule:** `nu = nu_prior + k·n_eff` (closed form from the Kish ESS / DQI already
  computed). Stable everywhere, no fitting, no small-`n` failure mode.
- **HybridRule:** MLE fit of `nu` from residuals, shrunk toward the formula prior with weight
  `w = n_eff / (n_eff + tau)`. Data-rich tasks learn their true tails; data-starved tasks fall
  back to the principled formula automatically.

Hybrid is the synthesis of the two original concerns: "fit the tail from the population, but
when the population is too small to fit, the formula keeps it appropriately fat." The
calibration harness arbitrates formula vs hybrid and the value of `tau` per task. **The design
does not presuppose hybrid wins** — if Phase 4 shows the plain formula matches on coverage, we
ship the formula and treat the MLE machinery as not worth its complexity.

### Starting parameters (Phase 0 defaults, harness-tuned in Phase 4)

Statistically-defensible defaults, not final values — Phase 4 retunes them against
coverage/CRPS per task. Principled rather than guessed:

- **`nu_prior = 2.5`** — the floor `nu` at `n_eff → 0`. The smallest df giving a finite,
  well-defined variance (Student-t variance requires `nu > 2`; the loss code already hard-floors
  at 2), with margin. The fattest tail the layer will ever produce.
- **`k = 1.0`** — couples epistemic df to sample size as `nu_epistemic = nu_prior + k·n_eff`,
  recovering the classical result that estimating scale from `n` effective observations yields a
  predictive `t` with `df ≈ n`. Treated as a *sensitivity* the harness may retune; `k=1` is the
  theory-matched starting point.
- **`tau = 10`** — the hybrid shrinkage half-point: `w = n_eff / (n_eff + tau)` reaches 0.5 trust
  in the MLE fit at `n_eff = 10`, leaning on the formula below that.

**`nu_pred = min(nu_loss, nu_prior + k·n_eff)`**, enforcing the invariant. The adaptive range is
therefore `[nu_prior, nu_loss]`, and epistemic fattening only bites where `n_eff` is genuinely
small — which is correct: a task with abundant effective data rides the aleatoric floor
`nu_loss`, and you cannot out-data the true heavy-tailedness of the phenomenon. This makes the
**semantics of `n_eff` per site decisive** (see plumbing): it must be the *effective number of
independent observations behind the scale estimate*, not a raw row count, or the coupling
miscalibrates.

### The invariant

**Epistemic uncertainty can only make tails fatter than the aleatoric floor, never thinner.**
`nu_pred` ranges from a low floor (~2–3) up to `nu_loss` as `n_eff` grows, and clamps there.
A data-rich task collapses to exactly the trained `t(nu_loss, sigma)`; a data-starved one
fattens automatically. No call site can produce tails thinner than the model was fit with.
Scale is inflated alongside: `scale = sigma·√(1 + 1/n_eff)`.

### Acceptance signal

- **Gate:** held-out backtest interval coverage (PIT) + a proper score (CRPS) per task. A change
  ships only if coverage is no worse than the prior phase's baseline (ideally better).
- **Dashboard:** the existing G4 `r/sigma` p95/p99 tail-quantile diagnostics, extended to report
  per task, watched while tuning.

## Architecture

A single new seam sits between trained models and every consumer that samples or builds intervals.

```
trained model (mu, sigma)  ┐
n_eff (Kish ESS / DQI)      ┼─►  predictive_t(rule) ─►  one Student-t ─►  sample() / interval() / cdf()
nu_loss (fixed, aleatoric)  ┘                                                ▲
                                                              every call site routes here
```

## Components

### New: `src/common/student_t.py`

The only place that turns `(mu, sigma, n_eff)` into a distribution.

- `predictive_t(mu, sigma, n_eff, *, nu_loss, rule) -> PredictiveT` — builds the frozen
  Student-t (`nu_pred`, `loc`, `scale`).
- `PredictiveT.sample(rng, size)`, `.interval(level)`, `.cdf(x)`, `.ppf(q)` — shared by fantasy
  sampling, quali probabilities, and CI bands.
- Tail rules behind a tiny interface: `FormulaRule(nu_prior, k)` and `HybridRule(nu_prior, k,
  tau)`. Swappable via config.

### `n_eff` plumbing (genuinely new work)

The values exist but die before reaching the interval point:

- **Kish ESS** — already computed in `src/compound_prior/baseline.py`. Tire-wear CIs are drawn
  *per compound*, so each compound supplies its **own** `n_eff` — this is what makes C4–C6 fat
  and C3 tight, automatically.
- **DQI** — per-entity/per-event in the adapters; the `n_eff` proxy for latent-power predictive
  intervals and the fantasy sampler.
- Sites that carry neither to the interval point get `n_eff` threaded through. **Every migrated
  site answers "where does `n_eff` come from here" explicitly — no silent default of
  `n_eff = ∞`** (which would quietly revert to thin tails).

### New: calibration harness — its own top-level package `src/calibration/`

The harness is a cross-cutting concern used across the whole project (every task's intervals get
scored), so it lives in its own dedicated package rather than nested under any one consumer.

- **Gate:** held-out backtest computing interval coverage (PIT) + CRPS per task.
- **Dashboard:** existing G4 `r/sigma` p95/p99 diagnostics, extended per task.
- Sources held-out races from the database (the single source of truth — no direct FastF1 calls).

### Out of scope (deliberately Gaussian — documented, not oversights)

- Kalman measurement noise in `src/preprocessing/measurement_models.py` (sensor-level electronic
  noise is genuinely Gaussian).
- Physics parameter covariances in `src/physics/parameter_estimator.py` (telemetry-rich,
  sensor-level).

These will be documented as intentional so they are not later mistaken for missed sites.

### Not a migration target: gold-cycle calibration

`src/evo_predictor/gold_cycle/calibration.py` fits `calibrated_trace = alpha·raw_sigma_trace +
beta·dof` to match `rank_mae²` via grid search. It is a **moment-matching scale calibration of
sigma** (how big sigma should be), distribution-agnostic — no Gaussian quantiles are baked in.
It sits *upstream* of the predictive layer; `predictive_t` consumes its calibrated sigma. The one
interaction: it matches a *variance* target, and a low-`nu` Student-t inflates variance by
`nu/(nu−2)` relative to `sigma²`, so calibrated sigma and t-interval width can drift. That drift
is caught empirically by the coverage harness and is a Phase 4 cross-check, not a code migration.

## Phased Rollout

Each phase is independently shippable and gated by the harness ("coverage no worse, ideally
better"). Order is chosen so we measure before we change.

- **Phase 0 — Foundation (no behavior change).** Build `student_t.py`, the two tail rules, and
  the `PredictiveT` API. Pure unit tests: the epistemic-only-fattens invariant,
  `nu_pred → nu_loss` as `n_eff → ∞`, scale inflation `√(1+1/n_eff)`, both rules. Nothing calls
  it yet, so nothing can regress.

- **Phase 1 — Measurement first.** Build the calibration harness; capture **baseline
  coverage/CRPS of the current Gaussian world**, per task. The before-picture every later phase
  is judged against.

- **Phase 2 — Fix the consistency leak.** Route the fantasy sampler
  (`src/fantasy_scoring/expected_assignment.py`) through `predictive_t` — it currently learns
  `sigma` under a Student-t likelihood but samples with `rng.normal`. Highest-value change: train
  and inference finally agree. Re-run harness, compare to Phase 1 baseline.

- **Phase 3 — Remaining Gaussian interval sites.** Quali `norm.cdf`
  (`src/simulation/quali_simulator.py:167`), tire-wear CIs (per-compound `n_eff`; C4–C6 fatten),
  and `mean ± k·sigma` visualization bands. Each re-gated.

- **Phase 4 — Tune the rule.** With everything routed through one seam and the harness working,
  sweep formula vs hybrid and the shrinkage weight `tau`, per task, and lock in whatever
  coverage + CRPS prefers. "Decide later" gets decided on evidence here.

## Testing Posture

- Unit tests for the math/invariants (Phase 0).
- The calibration harness *is* the integration test (Phases 1–4).
- Each migrated call site gets a focused test that it routes through `predictive_t` and never
  silently defaults `n_eff` to infinity.

## Open Items for the Implementation Plan

- **Per-site `n_eff` semantics.** For each migrated site, define what counts as the effective
  number of independent observations behind the scale estimate (per-compound Kish ESS, per-entity
  DQI mapped to an effective count, etc.). This is decisive — see the invariant note — and must
  never silently default to `n_eff = ∞`.
- ~~The exact CRPS / PIT-coverage implementation~~ — **done in Phase 1a** (`src/calibration/scoring.py`:
  `pit_values`, `interval_coverage`, `coverage_curve`, `crps_gaussian`, `crps_from_samples`,
  `summarize_calibration`). Remaining: how the harness pulls held-out predictions from the eval
  pipeline (Phase 1b). Source is `evaluate_labeled_batches` (`module_training_orchestration.py:462`)
  which yields per-pair `(pairwise.mu, pairwise.sigma, batch.target_mu)`.
- **Phase 1b must filter `target_mu is None` events before scoring.** The Phase 1a scorers now
  reject non-finite actuals by design (fail-loud, no silent NaN). Events without retro-delta labels
  (`target_mu is None`, see `module_training_orchestration.py:473`) carry no continuous actual and
  must be dropped from the calibration arrays, not passed through.
- **Gaussian-arm vectorization (deferred from Phase 1b-core to 1b-wire).** `evaluate_task_calibration`
  builds N python-level `scipy.stats.norm` frozen dists and loops per-element for PIT/coverage; at
  ~8k preds/task that's ~8s/task of pure object-construction overhead (the Student-t arm is already
  fixed via the cached `PredictiveT._frozen`). Before 1b-wire runs this across ~15 tasks, consider a
  vectorized Gaussian path (`stats.norm.cdf(actuals, loc=mu, scale=sigma)` / `.ppf`) — but size it
  against the REAL per-task N after `target_mu is None` filtering, which may be far smaller.
- **HybridRule floor behavior (found during Phase 0).** `HybridRule` blends `nu_fit` toward the
  *formula* value with weight `w = n_eff/(n_eff+tau)`. Two consequences to decide on in Phase 4:
  (1) the blend asymptotes to `nu_fit + tau·k` (not `nu_fit`) as `n_eff → ∞`, normally masked by
  the `nu_loss` clamp; (2) more importantly, a pathological small-sample MLE `nu_fit` (e.g. a
  garbage thin-tail estimate) can pull the blended `nu` *above* the formula value, thinning the
  tail below the formula's intended fat-tail floor for data-starved tasks — only the `nu_loss`
  clamp bounds it from above, nothing bounds it from below at the formula. Phase 4 should consider
  flooring the hybrid result at the FormulaRule value (making the formula a true two-sided floor)
  and/or guarding/ignoring the MLE fit when `n_eff` is below a minimum. Phase 0 leaves HybridRule
  as specified; it is wired nowhere yet.
