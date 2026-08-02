# Student-t — Season-Phase Calibration: does the fixed ν=4 hold early vs late?

**Date:** 2026-06-02
**Experiment:** `scripts/student_t_season_phase_sweep.py`
**Report:** `reports/calibration/season_phase_gold_cycle_260531_051234_2018thru2024.json`
**Bundle:** `…2018thru2024` (so **2025 is the only genuinely held-out season**; 2022–2024
are in-sample — absolute coverage optimistic, used only for the within-season *shape*).

## The question

Phase 4 shipped a fixed aleatoric tail `nu_loss = 4` and validated it only on a
data-rich full-season backtest. Open worry: is ν=4 right at the **start** of a
season (thin within-season history) as well as the end, or are we hard-coding a
tail that's too thin early? Each prediction was tagged by round and bucketed
(early 1–3 / mid 4–8 / late 9+); per bucket we swept Gaussian vs a fixed-ν grid
and read coverage / PIT / best-calibrating ν, plus the model's own mean σ.

## Answer: no early-season cliff — and the worry is inverted

t(4) interval coverage @0.90 (nominal 0.90), mean over modules:

| year | early 1–3 | mid 4–8 | late 9+ | early r/σ p99 | late r/σ p99 |
|---|---|---|---|---|---|
| 2022 (in-sample) | 0.904 | 0.906 | 0.904 | 3.52 | 3.80 |
| 2023 (in-sample) | 0.888 | 0.929 | 0.892 | 3.76 | 4.26 |
| 2024 (in-sample) | 0.942 | 0.970 | 0.922 | 3.18 | 3.67 |
| **2025 (HELD-OUT)** | **0.928** | 0.937 | **0.907** | 3.16 | 3.79 |

- Early-season coverage is right on nominal every year (~0.89–0.94) — it never
  collapses. The central-50% (bulk) coverage is likewise fine early (~0.47–0.55).
- **If anything, late-season is the marginally weakest phase** (0.892–0.922) and
  carries the **fattest realized tails** (r/σ p99 higher late than early every
  year). The fear was upside-down: the start of the season is not the soft spot.

## Why ν=4 holds early: the model's σ is already season-phase-aware

Mean σ, early vs late, pooled across all 4 years:

| module family | early σ | late σ | early/late |
|---|---|---|---|
| `*_recent_history` | 0.214 | 0.194 | **1.11** |
| `*_race_weekend` | 0.195 | 0.195 | 1.00 |

The **recent-history modules widen their own σ by ~11% early-season** — exactly
when within-season history is thin — while the race-weekend modules (which read
the current weekend's practice sessions, independent of how many rounds have run)
stay flat. So the epistemic early-season uncertainty the design worried about is
**already absorbed into the learned σ**, not left for the predictive layer to fix.
A fixed tail ν=4 riding on that phase-adaptive σ stays calibrated at both ends of
the season. This is also why the data-rich backtest never needed ν<4: the
epistemic widening lives in σ, so the FormulaRule's `n_eff` ramp would
double-count it.

## The real residual risk is per-task, not per-phase

`best_nu@0.9` by phase (held-out 2025): early `{4.0:7, 3.5:3, 3.0:1, 2.5:1}`,
mid `{4.0:12}`, late `{4.0:9, 3.5:2, 3.0:1}`. The buckets that want a tail
*fatter* than 4 are the **race-power** modules (r/σ p99 ≈ 3.8–4.75) — intrinsically
heavier-tailed than ν=4 can represent — and they want it in **both** early and late
phases. That is an **aleatoric** property of race-power (vs the lighter quali/
race-start tasks), bounded above by `nu_loss = 4` being the trained loss ν
(ADR-0008). It is not a season-phase effect and not fixable in the predictive
layer without reopening the loss.

## Verdict

- **We will not regret hard-coding ν=4 on the season-phase axis.** It is the right
  operating point at the start of the season (σ compensates) and at the end.
- The one place ν=4 is marginally thin is the **heavy race-power tasks (any phase)**,
  capped by the loss-level aleatoric ν. If we ever want to chase that, the lever is
  ADR-0008 (a per-task or higher loss ν), not the predictive layer — and it should
  be weighed against the mild over-coverage ν=4 already gives the lighter tasks.
- A PIT/coverage-tuned per-phase ν (which this sweep effectively is — `best_nu` is
  chosen by coverage, not likelihood) would pick ν=4 for almost every bucket and
  want only slightly fatter for the heavy race modules — i.e. it confirms, rather
  than overturns, the fixed-formula decision.

### Caveats

- Only 2025 is genuinely held-out; 2022–2024 are in-sample (optimistic absolute
  coverage). The within-season *pattern* is consistent across all four, and the
  held-out year agrees, which is the reassuring part.
- Buckets are coarse (early/mid/late); a finer per-round view is in the JSON
  (`round_NN` could be added) if we ever want round-level resolution.
