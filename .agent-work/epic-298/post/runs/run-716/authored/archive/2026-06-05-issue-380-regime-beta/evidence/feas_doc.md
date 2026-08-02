# Evo Prediction Ceiling & Next Priorities

What we know about where predictive headroom actually exists in the evo pipeline,
what that implies for the work, and how to tackle it. Findings are split into
**durable facts** (properties of the data/labels — stable across retrains) and
**model-bound metrics** (properties of the current gold bundle — recompute every
cycle). Re-derive any number here with:

```
py scripts/diagnose_prediction_ceiling.py
```

Durable numbers below are pooled over 2018–2025; model-bound numbers are the
`2018–2024 → 2025` gold cycle (`gold_cycle_260603_173742`).

---

## 1. What we know

### 1.1 The stack's ordinal value lives almost entirely in the quali stage

The sampled runtime predicts in three stages: **quali → race-start (lap 3) → race.**
Each downstream stage receives the prior stage's order as its handoff. Measured
against the only fair baseline — *the handoff order simply persists* — the
downstream modules add nothing:

| Handoff | Persistence (durable) | Current module sign-acc | Edge |
|---|---:|---:|---:|
| grid → lap-3 | **0.875** | 0.910 (driver) / 0.919 (constructor) | ~0 |
| lap-3 → finish | **0.776** | 0.791 (driver) / 0.740 (constructor) | ~0 |
| grid → finish (ref) | 0.753 | — | — |

The race and race-start power modules sit *at* the persistence ceiling (a hair
above or below). All genuine ordinal skill therefore comes from the **quali
stage** — the one stage that creates an order from scratch, has no persistence
floor to lean on, and whose errors every later stage inherits and cannot recover.

Quali is also the **weakest** module on every metric: driver-quali rank_mae 3.55
(recent) / 3.95 (race-weekend) and sign-accuracy ~0.74, versus race ~0.78 and
race-start ~0.91.

### 1.2 Race-given-grid is ~94% irreducible

Why don't the downstream modules beat persistence? Because there is very little
there to win. Of the grid→finish position movement:

- **~24.7%** of finisher pairs flip order between grid and finish (durable).
- But only **~6.5%** of the *movement* is systematic, learnable team race-pace
  (between-team vs within-team variance, within-season, averaged over 2018–2025;
  per-year range 2.5–10.1%). The remaining ~94% is event-specific — incidents,
  strategy, tyres, traffic, safety cars — and is not recoverable from pre-race
  latent power.
- That ~6.5% is itself partly **grid-position regression** (a front-row car can
  only lose places), so the genuinely learnable car-pace seam is smaller still.

The current model does not even capture the small recoverable part profitably:
on the 24% of pairs where the grid order flipped, the race module is right only
**29.8%** of the time (it mostly backs the grid and gets punished), while losing
a little on the preserved pairs (94.2% vs persistence's 100%) — netting to a wash.

**Implication:** chasing race / race-start *mean* accuracy is single-digit-percent-
ceiling work. The value those stages can add is *uncertainty*, not order.

### 1.3 The retro labels carry ordering only — no field-spread magnitude

The retro truth solve (`RetroTruthConfig.lambda_ridge = 1.0`) produces a per-event
`pi` field whose **spread is essentially constant** across events:

| scope | phase | mean per-event std | CV |
|---|---|---:|---:|
| driver | quali | 0.2414 | **0.0010** |
| driver | race | 0.2417 | 0.0022 |
| driver | race_start | 0.2417 | 0.0022 |

A CV of ~0 means a blowout weekend and a chaotic pack produce the same label
spread; the ridge dominates the data likelihood and erases magnitude at the solve.
`comparable_scale` rescales the *average* spread per task but is a single global
constant, so it cannot restore event-to-event variation. Consequently the model
has **no label signal for how spread/compressed a given field was** — the σ head
can only bootstrap event uncertainty from its own residuals.

Two model-bound observations on the fresh bundle clarify where the spread problem
does *not* live:

- **The race-start `sigma_corr` is not an anti-signal — it is noise.** The pooled
  race-start `sigma_corr ≈ −0.065` is not uniform; it decomposes into four
  per-module correlations between calibrated σ and rank error: the two
  *recent_history* modules are mildly negative (`driver_race_start_power_from_recent_history`
  r = −0.119, `constructor_…_from_recent_history` r = −0.092) while the two
  *race_weekend* modules are positive (driver +0.108, constructor +0.206).
  Computed over the n = 24 eval-year-2025 events, the critical value is
  `r_crit(n=24, α=0.05) ≈ 0.40`; all four |r| ≤ 0.206, every 95% CI spans 0, and
  every p > 0.33 — so all four are **statistically indistinguishable from zero**.
  The negative sign is sampling noise, not a real anti-correlation: race-start is
  the most *deterministic* phase (driver rank_mae ~1.0–1.7 vs quali ~3.5–4), so σ
  barely varies across events and the correlation is noise-dominated. The
  race-start calibrated-σ **level is coverage-aligned, not "too high / too flat"**
  (its σ/realized-error ratio runs ~19% above the quali/race reference, inside a
  25% materiality bar, and its σ flatness matches the reference). The earlier
  "anti-correlated / too high / too flat / leaving predictability on the table"
  reading was an artifact of treating an insignificant correlation as a defect.
- The mean *link* itself is well-calibrated (held-out Brier ~0.13, reliability
  curve tight, slightly under-confident at the top), so the residual spread
  question is about **event-to-event σ magnitude**, not the probabilities. Note
  this is a coverage/significance result, **not** a proof of absolute calibration:
  the full fused-Brier confirmation is deferred to the next gold cycle (§5).

### 1.4 Two structural facts that shape the design

- **Reliability is near-memoryless.** Team lag-1 DNF: base 0.123, P(DNF | prev
  DNF) 0.142 vs P(DNF | prev finish) 0.119. Reliability is a team/season prior
  and a one-sided (position-loss) tail — not a recent-form feature.
- **Modules are highly redundant.** Fusion correlations stay high (race-start
  0.99 / 0.87, race 0.87, quali 0.71–0.74). The recent-history and race-weekend
  evidence sources, and the driver/constructor scopes, carry largely overlapping
  signal — Gaussian-product fusion of them sharpens without adding independent
  information.

---

## 2. The problem, stated cleanly

The work splits into **two different problems on different stages**, which the
single `lambda_ridge` framing of #325 had been conflating:

1. **Quali = a mean-resolution problem.** This is where ~all ordinal leverage
   and all fantasy-relevant order originate, and it is the least-solved part of
   the stack. Improving quali latent power propagates through every downstream
   stage.

2. **Race / race-start = a distribution problem.** Their mean order is already at
   the persistence ceiling with <6.5% recoverable, so the value to add is
   *uncertainty* — correctly flagging flip-prone pairs and widening toward 50%
   there, instead of confidently backing the grid. This is where the spread/tail
   work belongs, and it is confined to these stages.

The project goal remains a **general** probabilistic prediction; fantasy scoring
is applied downstream and is explicitly *not* a target for honing the model
(e.g. no top-10-specific tuning).

---

## 3. What we need to do

### Thrust A — Quali mean resolution (primary)

Raise quali latent-power skill (rank_mae / sign-accuracy / spearman). This is the
highest-leverage work because race ≈ grid, so quali error is the binding
constraint on the whole chain. Directions to evaluate (general, not fantasy-aware):

- Richer / better quali evidence and features (the quali modules are the weakest
  and the most redundant across evidence sources).
- The close-gap / midfield region is where quali resolution is hardest and where
  ordinal information is densest; improving *resolution* there (not calibration —
  the link is already calibrated) is the target.
- This is the natural home for the **mean** half of #325: give the quali mean
  head a meaningful gap scale, decoupled from the uncertainty target.

### Thrust B — Race / race-start uncertainty (secondary)

Leave the downstream *means* alone (they're at ceiling). Give the σ / tail head a
real, event-conditioned spread target so race / race-start correctly express
flip risk:

- A **context-conditioned σ floor** (track + weather + grid density) for on-track
  shuffle — a modest but real predictable component; do not try to predict which
  race goes sideways.
- A **team/season-prior, one-sided tail** for reliability/DNF (not a recent
  feature, and asymmetric — use the existing `predictive_t` / per-site tail
  machinery).
- The bounded first win here turned out to be **making the σ diagnostic honest,
  not re-leveling σ** — because the measurement showed no mis-level. The
  `sigma_error_correlation_wrong_sign` check is now **n-aware**: it fires only on a
  correlation that is *significantly* negative at the module's event count, and
  statistically insignificant correlations (the race-start case at n=24) get an
  advisory `insignificant` flag instead of reading as a defect. A re-level was
  evaluated against the held-out evidence and **declined** as unsupported. Keep two
  σ levers distinct: the post-hoc calibration (`α·trace + β·dof`, fit vs
  `rank_mae²`) is **monotone in the trace**, so it is a level/scale lever only and
  cannot change a correlation's sign; the only lever that could alter the σ–error
  correlation is the **training-time** σ-production term (`lambda_sigma_nll`, #142),
  which is out of scope here.

### Parked (deliberately, until the generic level is solid)

- **Per-driver bias correction** (systematic but ~0.036 std, second-order).
- **Fusion redundancy pruning** (a speed/simplicity win, not an accuracy win).
- Per the standing exploratory issues: opponent-strength weighting / off-def split
  (#336), recursive priors (#204), ensembles (#208) — revisit only if a
  measurement points at them.

---

## 4. Recommendations on how to tackle it

1. **Sequence A before B.** Quali resolution is upstream of everything and is
   where the leverage is. The downstream uncertainty work (B) also depends on a
   trustworthy gap scale to *define* "excess flip risk beyond what the gap
   predicts," so the mean side should move first.

2. **Split #325 by stage.** Treat the mean-magnitude/gap-scale question as Thrust A
   (quali) and the spread/tail question as Thrust B (race/race-start). Do not tune
   one global `lambda_ridge` to serve both. Note the race-start σ side of this split
   has already been triaged: there is **no significant σ mis-level or wrong-sign
   signal at n=24**, a post-hoc re-level was declined, and the only remaining σ-shape
   lever is the training-time `lambda_sigma_nll` term (#142) — so Thrust B's spread
   work is about a *positive* event-conditioned target, not about correcting an
   anti-signal that the data does not support.

3. **Anchor every result to the durable baseline.** Raw accuracy flatters the
   model because the grid is predictable. The honest KPIs are **edge over
   persistence** at each handoff and **quali rank_mae / sign-accuracy**. Track
   those cycle-over-cycle, not raw accuracy.

4. **Re-verify on every gold cycle.** Run `scripts/diagnose_prediction_ceiling.py`
   after each cycle. The durable section is the fixed yardstick; the model-bound
   section must be regenerated against the current bundles — that requires the
   pairwise export (needs a torch env):

   ```
   py scripts/export_pairwise_predictive_vs_retro.py     # against current gold bundle
   py scripts/diagnose_prediction_ceiling.py
   ```

5. **Mind the ceiling.** Race/race-start mean work is capped at single-digit
   percent; do not invest there expecting ordinal gains. If a downstream change
   doesn't clear the persistence baseline, it isn't adding ordinal value by
   construction.

6. **Confirm the σ result at the next gold cycle (deferred).** The n=24 coverage /
   significance finding rules out a race-start σ mis-level, but does **not** prove
   absolute calibration; a full **fused-Brier** confirmation at the next scheduled
   gold cycle is the remaining tracked done-bar for it.

---

## 5. Durable vs model-bound (for re-checks)

| Finding | Type | Re-check after retrain? |
|---|---|---|
| Persistence baselines & flip rates (0.875 / 0.776 / 0.753) | durable | no |
| Systematic team-pace ceiling (~6.5%) | durable | no |
| Retro label spread CV ≈ 0 (#325) | durable | no |
| Reliability near-memoryless | durable | no |
| Retro order ≡ event order (no softer ceiling) | durable | no |
| Module sign-accuracy vs persistence | model-bound | **yes** |
| Race flip-pair capture (29.8%) | model-bound | **yes** |
| race-start `sigma_corr` — insignificant at n=24 (no mis-level; fused-Brier confirm deferred) | model-bound | **yes** |
| Quali rank_mae / sign-accuracy | model-bound | **yes** |
| Fusion correlations | model-bound | **yes** |

---

## 6. Race-start σ: scope of the conclusion, and held follow-ups

### 6.1 What the race-start σ result does — and does not — say

The finding in §1.3 is deliberately narrow. **Stated:** for the **race-start phase
uncertainty (σ) head specifically**, there is no statistically detectable evidence of
remaining headroom *given today's features and network structure* — the σ/error
correlation is indistinguishable from zero at n = 24 (all |r| ≤ 0.21 vs
`r_crit(n=24, α=0.05) ≈ 0.40`) and the calibrated-σ level is coverage-aligned. This is
an **absence of detectable signal at the current statistical power**, not a proof of
optimality.

**Not claimed, and not expected to generalize.** The result says nothing about:

- the full **race** phase σ — a different, less-deterministic phase with its own
  separately-measured correlations; it is *not* covered by this race-start-specific
  statement;
- **quali**, or any **mean / ordinal** channel (that is Thrust A, where the leverage
  is);
- any **future feature set or network structure** — a richer σ input, or the
  training-time σ-production path (`lambda_sigma_nll`, #142), could create signal that
  does not exist in the modules as built today;
- absolute calibration in **Brier** terms — the deferred gold-cycle confirmation (§4.6).

In short: the race-start σ *modules as they exist today* have no measurable uncertainty
headroom to chase. That is a statement about those specific modules, not about race
uncertainty in general.

### 6.2 Held follow-ups (surfaced during the σ-diagnostic work; not filed as issues)

Collected here for later routing.

- **F1 — Gold-cycle reporter emits `entity_count = None` per event.** *(bug, medium.)*
  Every `event_level_metrics[*].entity_count` in the gold-cycle `details.json` is
  `None`, so the post-hoc calibration's `β · effective_dof` term collapses to a constant
  (`dof → 1`) and the dof-scaling the formula intends never engages. The calibration
  still fits `α` and a constant `β` offset, but a designed mechanism is silently inert.
  *Fix:* populate per-event `entity_count` (the scored field size) in the reporter that
  writes `event_level_metrics`; add a test asserting it is a positive int for scored
  events.

- **F2 — σ/error-correlation diagnostic key-set mismatch.** *(bug, medium.)*
  `module_uncertainty_diagnostics._SIGMA_ERROR_CORR_KEYS` evaluates
  `corr_sigma_pi_trace_vs_{log_loss, brier, rank_mae}`, but the gold cycle only emits
  `…_vs_nll` and `…_vs_rank_mae`. So `log_loss` / `brier` are silently absent and the
  emitted `nll` channel is ignored — the (now n-aware) wrong-sign / insignificant gate
  runs on **`rank_mae` alone**, not the multi-channel set the code implies. *Fix:*
  reconcile the key sets (align the consumer to the emitted `rank_mae` + `nll`, or emit
  `brier` / `log_loss` correlations if they are intended); add a test asserting producer
  keys ≡ consumer keys.

---

## 7. Compound features and the structured-capability direction (feasibility)

This section is the live strategy thread behind Thrust A. It is a **theory/play
space** — the detailed implementation is delegated; here we record what we believe
and the decision points.

### 7.1 The finding: the compound effect is regime-dependent

Raw FP3-pace order predicts quali better than the trained quali modules (pooled
FP3→quali ≈ 0.79 vs `driver_quali` ≈ 0.71 race_weekend / 0.745 recent). The most
likely cause is that we feed the quali modules compound-*normalized* features whose
anchor is fit on the wrong regime. Measured:

- **Low-fuel / qualifying push:** at the grip limit, a softer compound's grip is
  cashed as lap time → a large **pace-intercept** effect (~2%/step empirically;
  upper bound, track-evolution-confounded).
- **Race / managed pace:** sub-limit, so grip is *not* cashed as pace — every
  compound laps ~the same at matched age (~0% intercept by two independent
  estimates). The compound difference moves into **degradation** (the `gamma`
  slope), not the intercept.

Physical principle: **a compound has a grip budget, spent as pace under a push and
as durability under management.** A single race-fit `beta` is therefore the *wrong
physical quantity* for quali normalization, and the current model applies that
~0 race-regime correction to both regimes — leaving the full ~2%/step compound
artifact in the quali features.

The expected race-side structure (not yet recovered by our fit) is a **crossover**:
softer = lower `beta` (faster fresh) + higher `gamma` (faster falloff); harder =
higher `beta` + lower `gamma`; the two cross mid-stint. Our current gold fit shows
`beta≈0` *and* `gamma` collapsed (C1–C4 identical) — i.e. it is missing the trade
entirely, not merely under-identified on one axis.

**Confound warning (hard-won):** compound is entangled with fuel, track evolution,
stint length, and stint phase, because compound *choice* segregates by race phase
(softs early on a rubbering track, hards late on a stable one). Naive within-driver
differencing cannot isolate `beta`/`gamma` — every shortcut we tried was confounded.
Only a joint fit that uses the **stint reset** (tyre age drops to 0, fuel/track
continue) can separate them. This is precisely what `compound_prior` is *for*, which
is why its degenerate output is the thing to investigate, not route around.

### 7.2 Verdict: layered pieces sharing one primitive — not a monolith

The "unified effect" spans two different layers with incompatible data and math:
the **compound trade** is a feature-preprocessing regression over lap times; the
**driver/car capability** is latent inference over pairwise outcomes (neural net +
BT field solve). Fusing them into one solve multiplies identifiability problems and
destroys per-component falsifiability (each piece has its own clean check — physics
for compound, statistics for the latent). So: **targeted pieces, built against one
shared blueprint, unified at the latent-conditioning layer.**

The shared primitive is **latent capability → context-weighted readout**: a latent
(grip; car/driver capability) whose observable expression (pace vs durability; quali
vs race; attack vs defend) is selected by context (push level, fuel, tyre age, race
situation). Keep a **conservation constraint only where physics demands it** (the
tyre grip budget is a true anti-correlated trade; driver offense/defense are
correlated facets, not a budget). The current scalar `pi` per (entity, task) is the
fundamental limit this primitive is meant to relax.

### 7.3 Feasibility ladder

| Piece | What | Feasibility | Buys |
|---|---|---|---|
| **1** | Regime-aware compound model: recover the `beta`/`gamma` crossover; emit regime-tagged params; route `qs_*` features through the push intercept, `lr_*` through the managed deg | **High** — self-contained regression behind the existing normalizer interface, validated against known physics | Likely fixes FP3-beats-model; clean feature signal into quali |
| **2** | Context-conditioned shared latent net: replace the 12 separate modules with **one** net taking context (task/evidence/scope/regime) as conditioning input, shared trunk; output stays scalar `pi` per context so the BT solve is unchanged | **Medium** — standard multi-task pattern | Pools data across the 12 instances ("solve across more data"); learns context-dependence explicitly; directly attacks the measured module redundancy |
| **3** | Structured latent **vector** + conserved-trade readout (offense/defense, grip budget) | **Low / research** — changes the BT solve; identifiability is the whole battle (#336) | The #336 dream; only if a measurement demands it |

"Unify" happens at **Piece 2** (parameter sharing across the context axis), not as a
single physics+latent objective. Design the **context interface once, up front** so
the pieces compose: Piece 1 emits regime as an explicit context tag; Piece 2 consumes
context as a first-class conditioning axis; Piece 3, if ever, swaps the scalar readout
for a vector readout behind the same interface.

### 7.4 The decision gate

Everything above hinges on one load-bearing unknown: **can a proper joint fit recover
the `beta`-down / `gamma`-up crossover where the physics is known?**

- If **yes** → the "latent + conserved-trade readout" primitive is validated on
  physics; Piece 1 ships and Piece 2/3 are worth pursuing.
- If **no** (the fit can't find the trade even with correct identification) → the
  vector-latent direction is premature, and Piece 1 narrows to "use raw, regime-
  appropriate pace for quali features" without the full structured model.

This crossover-identification test is the gate; it is the first delegated build item.

### 7.5 Gate outcome and sizing (resolved)

The gate ran — full method and numbers in
[`compound_crossover_gate_findings.md`](compound_crossover_gate_findings.md);
harness `scripts/fit_compound_crossover_gate.py` (stdlib pooled fixed-effects fit).
**Verdict: PARTIAL.**

- **`beta` (fresh pace) recovered decisively:** strictly monotone-down C1→C6
  (~1%/step, every step ≫ 2 SE) — "softer = faster fresh," exactly as expected.
  The gold fit completely misses this (`beta`≈0, non-monotone, wrong-signed C1). So
  the gold compound anchor *is* provably mis-fit on the intercept.
- **`gamma` (degradation) NOT recovered:** non-monotone, no `gamma`-up ladder, and
  spec-sensitive (per-race `phi` breaks it; single-season fits fail). `gamma` is the
  axis most collinear with the absorbed fuel/evolution term, so this is **identification-
  limited, not refuted** — we can't recover the trade with this method, which is not
  the same as proving it absent.

**Consequence for Piece 3:** the conserved-trade / vector-latent direction is
**premature** — the trade did not identify on the one problem where the physics is
known, so we will not build toward it on physics grounds (but it is not disproven; a
better deg identification could revisit).

**Sizing (the sobering part):** a `beta` correction only changes *cross-compound*
pairs. Measured:

- **~4%** of actual-qualifying best-lap driver pairs are cross-compound (in Q,
  ~everyone runs the softest tyre).
- **~13%** of *practice quali-sim* pairs (what the `qs_*` features see) are
  cross-compound.

So a correct fresh-pace `beta` fixes a real but **minority** slice. It cannot be the
explanation for the model-vs-FP3 quali gap (model 0.71–0.745 vs raw FP3 ≈ 0.79),
because that gap lives on the ~87% of **same-compound** pairs where any compound
offset cancels.

**Reframe of Thrust A (important):** the compound thread produced a genuine
correctness fix but it is a *small* quali lever. The dominant quali gap is **not a
compound problem** — it is the model under-using clean same-compound practice pace
(suspects: evidence-window dilution, since FP1→FP3 climbs 0.742→0.788, and feature
aggregation choices). Net plan:

- **Piece 1 (narrowed):** ship the recovered fresh-pace `beta` for `qs_*`
  normalization as a cheap, principled correctness fix — but do **not** bill it as
  the quali solution; its reach is ≤13% of feature pairs.
- **Primary Thrust A lever:** the model under-extracts the practice-evidence signal
  it already has — see §7.6, which tested the evidence-windowing/aggregation suspects
  (one confirmed-minor, one *reversed*) and isolates the remainder to model-side use.
- **Piece 2** (context-conditioned shared net) is unaffected and stands on its own.
- **Piece 3** gated off (above).

### 7.6 Quali evidence: what's signal vs what's model (resolved)

Tested the §7.5 suspects directly — data-only evidence→target predictability
(pairwise sign accuracy), the *achievable* ceiling, not trained-model behaviour.
Harness `scripts/diagnose_quali_evidence.py`; full numbers in
[`quali_evidence_findings.md`](quali_evidence_findings.md).

- **Evidence-window dilution: REVERSED.** A rank-blend of FP1/FP2/FP3 *beats*
  FP3-only (0.809 vs 0.790) — blending all three sessions sensibly is strictly
  better (it rescues drivers whose FP3 lap was compromised). Only *time*-averaging
  dilutes; rank-blending does not. So my §7.5 "weight FP3, discard FP1/FP2" was
  wrong; the right recipe is **rank-blend all three sessions.**
- **Aggregation (minor, real):** **theoretical-best (min-sectors)** is the best
  aggregate throughout; mean-of-push is worst. Use min-sectors.
- **Normal-weekend Q evidence ceiling ≈ 0.80** (rank-blend, min-sectors, FP1/2/3).

The trained quali modules score ~0.71–0.745. The ~6–9pp gap to the ~0.80 ceiling is
**not** explained by compound (§7.5, ≤13%), dilution (reversed), or aggregation
(minor). By elimination it is **model-side**: how the latent-power module weights/
combines the evidence it has (and possibly recent-history evidence dragging quali).
That comparison needs same-pair scoring against the model's predictions (torch env),
and is the real Thrust A core. *(Caveat: the model's `sign_accuracy` is retro-delta-
weighted, not the same pair population as the 0.80, so the exact gap awaits the
same-pairs check.)*

**Sprint weekends (small-n: 21 weekends, 2022+; direction robust):**

- **SQ → Q = 0.759 vs FP1 → Q = 0.676** (~8pp). SQ (a full low-fuel quali the day
  before) is the strong Q evidence, and the preprocessor reportedly feeds only FP1 on
  sprint weekends — so **feeding SQ as primary Q evidence is the highest-value sprint
  fix**, independent of any model rework.
- **Structural practice penalty ≈ 11pp:** FP1-only predicts the SQ target at ~0.69 vs
  ~0.79 for normal-weekend FP3→Q (one early session, no FP2/FP3). That ~0.69 is the
  sprint→SQ ceiling — a hard limit, not a model failure.

**Confirmed cheap fixes (no model rework):** (1) rank-blend FP1/2/3 on min-sectors;
(2) feed SQ as primary Q evidence on sprint weekends; (3) Piece-1 `beta` (≤13%). All
three are "stop diluting/ignoring signal we already have," and all three are exactly
what Piece 2 would otherwise learn as context-weighting — making the sprint/variable-
evidence case the concrete near-term payoff for Piece 2.
