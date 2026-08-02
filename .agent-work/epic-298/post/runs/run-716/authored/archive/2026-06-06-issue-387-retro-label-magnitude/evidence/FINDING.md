# Issue #387 — Decisive measurement finding (the option-1-fails STOP)

## TL;DR

The user's leaned option (#1: fix the labels via a magnitude-preserving re-solve) **cannot
restore event-to-event spread magnitude — at any ridge, scalar or not.** Not because it
degrades ordering (it does the opposite: ordering is *perfectly* preserved), but because the
ridge is the wrong lever. The missing magnitude signal is **structurally absent from the
binary-outcome BT observation**, so no re-solve of those observations can recover it. Per
standing orders this is the STOP-and-report finding; the fallback to option 2 is a
scope-defining choice reserved for the Admiral.

## What I measured (CPU-only, on the 1040 persisted retro artifacts + reconstructed observations)

Re-solved every (event, phase) at a lambda sweep using the SAME `retro_solve.solve()` on the
SAME `PhaseObservation` (pair_index / observed_y / start_bias / weight reconstructed from the
persisted pairwise diagnostics). Two axes measured per event: ordering stability (Spearman of
new pi vs old pi, vs the durable observed order; pairwise sign flips) and magnitude (per-event
pi std and its cross-event CV).

### Axis 1 — ORDERING STABILITY (the binding caveat). PERFECT across the whole sweep.

| phase | lambda range tested | Spearman(old,new) mean / min | pairwise sign flips |
|---|---|---|---|
| quali | 1.0 -> 1e-4 | 1.00000 / 1.00000 | 0 / 3040 |
| race | 1.0 -> 1e-4 | 1.00000 / 1.00000 | 0 / 2854 |
| race_start | 1.0 -> 1e-4 | 1.00000 / 1.00000 | 0 / 2854 |

A BT ridge shrinks all pi uniformly toward zero -> argsort is invariant. Lowering lambda does
**not** perturb the durable ordering labels. (So the issue's stated *risk* for option 1 -
"ordering stability / label churn" - is empirically a non-issue. Consistent with §7.6.2/#381:
the ordering-accuracy gap is model-side, not label-side.)

### Axis 2 — MAGNITUDE (the goal). NOT restored by lambda. CV stays ~0 at every lambda.

Full 173-event population, per-event pi std and its cross-event CV:

| phase | lambda=1.0 | lambda=0.1 | lambda=0.01 |
|---|---|---|---|
| quali | mean_std 0.2414, **CV 0.00101** | mean_std 1.0314, **CV 0.00054** | mean_std 2.6697, **CV 0.00014** |
| race | mean_std 0.2417, **CV 0.00221** | mean_std 1.0322, **CV 0.00118** | mean_std 2.6702, **CV 0.00031** |
| race_start | (== race) | | |

Lowering lambda only *uniformly scales* the mean spread (0.24 -> 1.03 -> 2.67). The
cross-event CV does not rise toward "real" variation; it actually drifts toward 0. A blowout
weekend and a chaotic pack still get the same (now larger) spread. **lambda is a global
scale knob, identical in kind to `comparable_scale` - it cannot create event-conditioning.**

## Why — the structural proof (this is the load-bearing part)

Every retro event is a **perfectly clean, transitive binary tournament** (a total order with
no upsets/cycles). Verified: retro pi order vs observed binary outcomes disagree on
**0 of 65,266 (quali) / 0 of 61,526 (race) / 0 of 61,526 (race_start)** directed pairs;
0/173 events have any upset.

For a complete, perfectly-ordered binary tournament, the regularized BT negative log-likelihood
is identical up to entity permutation for every event of the same field size. So the solved
spread profile is the same for every such event (modulo which driver sits where). The only
event-varying inputs in the observation are (a) the outcome permutation - which sets order, not
spread - and (b) field size (n_entities CV ~0.02-0.05, trivial). The persisted `start_bias` is
**0.0 for every event in every phase** (the only continuous channel, and it is empty).

=> The "how spread/compressed was this field" magnitude lives in the **finishing-time gaps /
margins**, which are discarded when outcomes are binarized into win/loss pairs. It is not in the
BT observation, therefore not recoverable by any solve of that observation - independent of the
ridge. Option 1 as framed ("re-solve to preserve magnitude") has nothing to preserve: the
magnitude was never in the solved quantity; it was removed at binarization, upstream of lambda.

## What this means for the issue's options

- **Option 1 (magnitude-preserving re-solve): not viable for restoring event-to-event spread.**
  A re-solve at lower lambda restores *average* magnitude (and keeps ordering perfectly) but
  delivers the SAME per-event-constant spread - i.e. exactly what `comparable_scale` already
  does, just folded into the solve. It does not produce an event-conditioned target. (A
  non-scalar/per-event lambda would just be hand-injecting the answer - it would have to be
  driven by an external dispersion signal, which IS option 2 wearing option 1's clothes.)

- **Option 2 (external event-conditioned spread target from observed dispersion): the only path
  that can carry the signal**, because the signal (finishing-gap variance / pack compression)
  lives in the DB, not in the binarized labels. Ordering labels stay untouched by construction.

## The honest recommendation (for the Admiral's ruling)

Adopt **option 2**: build an event-conditioned spread target from observed dispersion (a DB-side
derivation: per-event finishing-gap dispersion / pack-compression statistic, with an explicit
as-of contract), exposed as an artifact the #386 sigma-floor/tail builds consume. Leave the
retro ordering labels and the BT solve untouched. This is *not* a silent fallback - it is what
the measurement forces, and the user asked to see this evidence before locking it in.

## Consequence for #391 (mean-half, next wave) - per acceptance

Because option 1 is out, **#391 does NOT get restored-magnitude labels from this work.** The
quali mean head's gap scale therefore **needs a data-side scale** (a DB-derived quali gap-scale
signal), exactly the coordination note #391 already flags. State this explicitly to #391:
"the retro labels cannot carry magnitude; the mean half needs its own data-side gap scale."

## Decision required (why I am stopping here, not building option 2)

Choosing option 2 is scope-defining (it adds a new DB-side derivation + artifact contract, a new
lane vs "re-solve the existing solve"). Standing orders: the option-1-fails finding -> END and
report; a successor resumes with the ruling. Confirm:
  (D1) Accept option 2 as the path (the measurement rules out option 1)?
  (D2) Should THIS issue build the option-2 spread-target artifact now, or is #387's acceptance
       met by this characterization + measured trade + the option-2 recommendation + the #391
       hand-off note, with the artifact build spun as the next step?
  (D3) If build-now: confirm the dispersion statistic (e.g. std of within-event finishing-gap
       seconds, or a normalized pack-compression index) and that a DB-side as-of derivation in
       the evo lane (not the latent_power generic solver) is the right home.
