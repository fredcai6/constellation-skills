# Powered F10 — the FP-representativeness held-out gate, full 16-weekend run

**Verdict: HONEST_NULL on the primary channel — decisive, not inconclusive.**

Run: PID 36016, launched 2026-07-24 12:18, finished 2026-07-25 ~01:33.
Wall **48,411s ≈ 13.45h** against an 8.4h pre-flight projection (see "Runtime" below).
16/16 frozen 2023 weekends. Artifacts in this directory; protocol frozen before any
number was produced (`GATE_PROTOCOL.md`, #513 Phase 4).

## What the gate asked

Pre-registered (and this is the whole point): **the learned FP-representativeness
weighting must beat a clock-distance-to-Q baseline on held-out data — otherwise it has
merely rediscovered the calendar.** "Later FP sessions resemble qualifying more" is free;
learning it is not a result.

## What it answered

| Check | Result | Reading |
|---|---|---|
| PRIMARY_GRIP, overall Spearman | mean_delta **−0.0037**, CI [−0.0537, 0.0424] | straddles zero — no gain |
| PRIMARY_GRIP, overall centred-RMSE | mean_delta **+0.0016**, CI [−0.0006, 0.0039] | straddles zero — no gain |
| **Divergent-case read** (the protocol's designated read) | **HONEST_NULL**, n=152/456, `inconclusive=False` | see below — the sharp finding |
| SECONDARY_POWER | CONFOUNDED_NOT_EVIDENTIAL | as pre-registered; cannot be read |
| Emergence audit (F3) | **PASSES** | push_weight 0.9975 vs longrun 0.6399; other-features range 0.62 vs track-evo-only 0.058 |
| Sandbagging demo (F8) | **FAILS** | Canada/Ferrari: learned weight **0.9526** vs clock 0.5403 on a weekend with pace_jump 0.147 |

## The three things actually learned

**1. The null rests on the overall channel. The divergent-case number is WEAKER than it
looks — see the correction below.** The protocol singled out divergent cases — where
learned and clock weightings *disagree* — precisely because the overall primary is
structurally biased toward null (clock-distance genuinely correlates with grip because
rubber goes down over a weekend). The reported divergent Spearman delta is 0.000 with a
zero-width CI on `n_divergent=152/456`.

> **CORRECTION (2026-07-25, after code inspection — see #672).** An earlier version of
> this document called that number "direct evidence that the learned weighting IS the
> calendar." **That was an over-claim and is withdrawn.** `divergent_case_read` computes
> **one delta per LOWO fold** and `paired_bootstrap` resamples *those per-fold values* —
> so the interval has **at most 16 points**, not 152. `paired_bootstrap([0.0]*16)`
> reproduces the reported `(0.0, 0.0, 0.0)` exactly. The zero-width CI means only that
> every contributing fold's Spearman delta was exactly 0.0 — the car ordering never
> flipped on any fold's small divergent subset. Three further unknowns, none recoverable
> from the report: per-fold **car** counts are never recorded (Spearman here is computed
> across cars *within* a weekend, so cars-per-fold is the real sample size); the
> `n_cars >= 2` guard permits folds where Spearman is always ±1 and a zero delta is
> structurally guaranteed; and the `agree_everywhere` guard (`threshold < 1e-6` on
> **min-max normalized** differences) is far too loose to establish that the "divergent"
> third genuinely disagrees in absolute terms. RMSE on the same folds *did* vary
> (CI [−4.16e-05, 4.77e-06]), confirming multiple folds contributed and that the weights
> moved without reordering.
>
> **The verdict is unaffected.** `evaluate_gate` requires overall-favours AND a divergent
> PASS; the overall channel independently straddles zero, so HONEST_NULL holds on the
> overall channel alone. The divergent read was corroboration and cannot bear that weight.

**2. It did learn real structure — that structure just doesn't pay.** Emergence passes
cleanly: the model separates push laps (0.9975) from long-run laps (0.6399), and its
weights vary far more with non-track-evolution features (range 0.62) than with track
evolution alone (0.058). So this is not a broken fit or a degenerate model. It learned
something true about lap character and that knowledge still bought **zero** held-out
ranking gain over "how close in time to Q was this lap". Worth holding onto: a model can
be internally sensible, pass its structural audit, and still be worthless against a
trivial baseline.

**3. The sandbagging failure is the actively bad one.** On the Canada/Ferrari weekend —
where the car demonstrably hid pace (pace_jump 0.147) — the learned weighting assigned
**0.95** where the dumb clock baseline assigned 0.54. It did not merely fail to discount a
sandbagged weekend; it *up-weighted* it, above what recency alone would have given. A
weighting layer that is confidently wrong exactly when a team is hiding pace is worse than
no weighting layer, because downstream consumers inherit the confidence.

## Sample-integrity note (correcting an earlier claim)

114 driver-sessions were skipped for `no flying-lap samples` / smoother-HP calibration
failure. These are **not** concentrated on thin-running backmarkers — the leaders are
**VER and PER (8 each)**, then LEC (7), SAI/HAM/PIA/OCO/ALB (6). The skips are an
extraction property spread across the whole grid, not a back-of-grid sampling bias, so
they do not obviously bias the gate toward or against any part of the field. (An earlier
session note claimed the opposite from a small log window; that claim was wrong.)

## Runtime

13.45h actual vs an 8.4h pre-flight extrapolation, crossing the pre-registered **15h STOP
threshold**'s neighbourhood (it finished under it, at 13.45h — the projection made from
mid-run pacing that suggested 15–17h was pessimistic because the last weekends ran faster
than Miami/Netherlands did). The ~1.6× overrun is consistent with #644's blanket
single-thread BLAS/OMP cap and per-weekend variance from repeated failed smoother-HP fits.
The mid-run decision to let it run past the bar is logged in the ADMIRAL_LOG.

## What this changes downstream

**Epic #659 §6 (practice update, Build 3) names the F10 machinery as "the
evidence-weighting layer."** That assumption is now measured, and it did not hold: as
built, the layer does not beat recency and is sandbag-fooled. Build 3 must not inherit it
uncritically. Concretely, when Build 3 is cut it should either (a) use clock-distance-to-Q
as the honest default weighting and treat anything fancier as needing to clear this same
bar, or (b) re-pose the weighting problem against a target the calendar cannot proxy —
this result says the current target is one the calendar already solves.

**#513 is not invalidated.** Phase 4 built the machinery and a falsifiable gate; the gate
firing negative is the machinery working. The honest-null was on the table by design and
was pre-committed to as a complete deliverable.
