# Thread 2 — Stage-specific interaction hypotheses & conditioning variables

Framed as INPUTS to the #374 probe plan and the #375 conditioning design. NOT build
decisions. Every hypothesis tagged by evidence strength:
- **[MEASURED]** — a number exists in a named artifact.
- **[INFERRED]** — follows from measured facts + domain structure; not directly measured.
- **[SPECULATIVE]** — domain-plausible, no supporting measurement in repo.

Artifacts: [CD]=`prediction_ceiling_and_priorities.md`, [FD]=`fusion_rework_findings.md`,
[414]=[CD §7.6.3], [SC]=#373 scorecard.json.

---

## 2A. Why the #140 quali story does not transplant

[CD] / brief: the #140 "weekend-pace vs recent-form disagreement ⇒ pending upgrade / step
change" hypothesis is a QUALI-PACE story — it conditions on a disagreement between two views of
*single-lap pace*. Downstream stages are not pace-resolution problems:
- race_start (lap 3) is a **launch + first-lap-chaos** problem on top of a near-frozen grid.
- race is a **degradation / strategy / tyre-management / overtaking** problem on top of a
  near-frozen lap-3 order.
[CD §1.1] both downstream stages are persistence-dominated (grid→lap3 0.875, lap3→finish 0.776),
so the dominant signal each receives is the **prior stage's order as a handoff**, not a fresh pace
read. The richest interaction is therefore structurally different from quali's: it lives in
**prior-stage-order × pace-deviation**, a term the quali probe cannot have (quali has no prior
stage). [INFERRED from measured persistence + handoff architecture.]

---

## 2B. The #414 analogue: is there an information-not-calibration deficit downstream, and what
would anchor it?

#414 [414] found quali's standalone `race_weekend` head is missing INFORMATION (a cross-channel
"who is generally fast" pace anchor): a global pace-anchor blend recovers ~68–72% of its ~19pp
gap at α=0.5; a magnitude-only recalibration is an exact no-op (Δ=0.0). The brief asks for the
downstream analogue.

**Key structural difference [INFERRED]:** quali's deficit was the head ignoring *pace evidence it
already received*. Downstream, the dominant evidence is the **handoff order**, and [CD §1.2] shows
race finishing order is ~94% irreducible from pre-race latent power (only ~6.5% of movement is
systematic team race-pace, partly grid-regression). So a race/race_start head that "just backs the
handoff" is NOT obviously missing information the way quali's head was — most of what it could add
is genuinely not in any pre-race signal.

**BUT there IS a measured downstream information channel that the means provably ignore today —
and it is an UNCERTAINTY signal, not an ordering one:**

- **[MEASURED]** The event-conditioned spread target `s_e` [CD §9.5] is genuinely
  event-conditioned downstream: cross-event CV ≈ **0.31 (race) / 0.35 (race_start)** (vs retro
  labels' ~0.001). Real event-to-event spread structure exists that the current scalar-`pi` +
  bootstrapped-σ path does not consume.
- **[MEASURED]** The companion **pace→finish disagreement rate** rises **quali ~3% → race ~16% →
  race_start ~19%** [CD §9.5]. This is the fraction of pairs where green-flag pace order and
  finishing order disagree — i.e. the rate at which the stage's own mechanics (launch, incidents,
  strategy) decouple pace from outcome. It is small on quali and ~5–6× larger downstream.

**Verdict on the analogue [INFERRED, strong]:** the downstream analogue of #414 is NOT an
ordering-information deficit (the ordering headroom is ~persistence-capped, [CD §1.2]); it is an
**uncertainty-information deficit**. The means already sit at the persistence ceiling [CD §1.1];
what they demonstrably ignore is the event-conditioned *spread/flip-risk* signal that `s_e` and
the disagreement rate now expose. This mirrors [FD]'s conclusion exactly — the correlated-fusion
correction also moved CALIBRATION not ORDERING downstream (Thread 1) — and converges with [CD §2]
Thrust B (race/race_start = a distribution problem). The "anchor," in the #414 sense, is the
per-event `s_e` + disagreement_rate that [CD §9.5] already routes to #386/#388/#389. So the
downstream information-not-calibration story is REAL but lives on the σ/spread axis, where it is
already being acted on — not on the ordering axis #375 conditions.

---

## 2C. race_start (lap 3) — interaction hypotheses + candidate conditioning variables

Persistence context [CD §1.1]: grid→lap3 = **0.875** (highest of the three handoffs) → least
ordering headroom. The interactions worth probing are the ones that perturb a *mostly-frozen*
launch order.

Interaction hypotheses (for #374 probe plan):
1. **prior-quali-order × launch/getaway** [INFERRED]. The handoff is grid order; the perturbation
   is start performance. The interaction (does a strong launcher gain *more* from a midfield slot
   than from P2?) is the structural analogue of #140's disagreement term. Probe: does a
   start-performance deviation predict lap-3 movement *conditioned on* grid slot?
2. **grid-position-dependent first-lap chaos** [INFERRED]. First-lap incident/position-change risk
   is grid-slot-shaped (midfield T1 is the pileup zone; front row is cleaner). This is primarily a
   σ/flip-risk interaction, not a mean one. Supported indirectly by [CD §9.5] race_start
   disagreement ~19% (highest of the three) — pace↔finish decoupling is largest exactly here.
3. **(grid slot) × (car/launch traction prior)** [SPECULATIVE]. Some cars/PUs launch better;
   crossing that with slot could shift lap-3 order. No per-car launch metric exists in repo.

Candidate conditioning variables (for #375):
- prior-stage (grid/quali) order/position — the handoff [MEASURED to be dominant, 0.875].
- grid-slot band (front / midfield / back) as a chaos-risk proxy [INFERRED].
- start-performance / getaway deviation [SPECULATIVE — not known to be a DB feature; flag].
- per-event race_start `s_e` and `disagreement_rate` (≈19%) as the σ-side conditioning input
  [MEASURED, [CD §9.5]].

**Ceiling caveat (carry to Thread 3):** grid→lap3 0.875 means the race_start MEAN has almost no
headroom; these interactions mostly pay on the UNCERTAINTY axis (which pairs to widen toward 50%),
not on reordering. [CD §1.1/§1.2.]

---

## 2D. race — interaction hypotheses + candidate conditioning variables

Persistence context [CD §1.1]: lap3→finish = **0.776** (lowest handoff → MOST downstream ordering
headroom, though still capped at ~6.5% systematic [CD §1.2]). race_start disagreement context:
race 16% [CD §9.5].

Interaction hypotheses (for #374 probe plan):
1. **compound-regime (push vs race-pace β/γ crossover) × pace** [MEASURED premise, NEGATIVE on
   the lever]. [CD §7.1/§7.5/§7.7] establishes the physics: a compound's grip budget is spent as
   pace under a push and as durability (γ) under management; the race regime moves the compound
   effect into degradation (γ), not the intercept (β). This is the brief's "natural conditioning
   signal." **Hard caveat [MEASURED]:** the γ-up degradation crossover did NOT identify from
   race-lap data — [CD §7.7] finds γ is well-resolved but *wrong-signed* (monotone-down in
   softness), the signature of residual confounding with fuel/track-evolution/stint-phase, and
   "a better fit of the same data cannot rescue it." So compound-regime as a *measured per-event
   degradation conditioning variable* is currently **not available** from this data; Piece 3 is
   effectively closed on physics grounds [CD §7.7]. Conditioning #375 on a recovered γ-crossover
   is therefore SPECULATIVE-blocked, not a ready lever. The β (fresh-pace) axis IS recovered but
   reaches only ≤13% of feature pairs [CD §7.5] and is a quali-feature normalizer, not a race
   ordering conditioner.
2. **prior-stage-order (lap-3) × race-pace deviation** [INFERRED, strongest candidate]. The
   handoff is lap-3 order; the perturbation is sustained green-flag pace vs that order. This is the
   direct downstream analogue of the prior-order×pace structure the brief calls out, and it is the
   one place [CD §1.2]'s ~6.5% systematic team race-pace could be cashed (the flip-prone pairs).
   [CD §1.2] also shows the current race module FAILS here — on the 24% of pairs that flip, it is
   right only 29.8% (it backs the grid). So there is a measured, specific failure mode for a
   conditioned model to attack: pairs where race-pace deviates from the lap-3 order.
3. **overtaking difficulty (track) × pace deviation** [SPECULATIVE/INFERRED]. The conversion of a
   pace advantage into a position depends on the circuit (Monaco vs Monza). A track-overtaking
   prior crossed with pace deviation would predict where pace *can* be cashed. No overtaking-
   difficulty feature is known in repo; [CD §9.3] does have a per-event green-pace machine
   (`race_pace_gap.py`) but not a track-passability index. Flag as a candidate needing a feature.
4. **strategy / pit-delta** [SPECULATIVE]. Undercut/overcut and stop count reorder the race; this
   is event-specific and [CD §1.2] folds it into the ~94% irreducible. Likely a σ-widener, not a
   learnable mean conditioner, from pre-race signal.

Candidate conditioning variables (for #375):
- prior-stage (lap-3) order — the handoff [MEASURED dominant, 0.776].
- race-pace deviation vs lap-3 order — the perturbation [INFERRED; `race_pace_gap.py` /
  `integrated_pace_gap` [CD §9.3] is the existing green-pace observable that could source it].
- per-event race `s_e` (CV ≈ 0.31) + `disagreement_rate` (≈16%) for the σ side [MEASURED §9.5].
- compound-regime tag — **caveated**: β only, ≤13% reach, quali-side; γ unavailable [CD §7.5/§7.7].
- track overtaking-difficulty prior — [SPECULATIVE, needs a feature that does not exist].

---

## 2E. The cross-cutting structure the quali probe lacks

[INFERRED, the load-bearing Thread-2 point.] Both downstream stages receive the prior stage's
order as a handoff. So the highest-value interaction term for #375 downstream is
**prior-stage-order × pace-deviation** (lap-3-order × race-pace for race; grid-order ×
start-performance for race_start). The quali stage has no prior-order handoff, so its conditioning
(the #414 cross-channel pace anchor; #140 weekend-vs-form) cannot be transplanted as-is. The
generalization is at the META level — "condition the combination on context" — but the specific
context variables are stage-specific and, downstream, are dominated by the handoff term. This is
the structural reason a single shared conditioned net (#375) is the right home: it can learn
*which* context axis matters per task rather than hard-coding quali's.

---

## 2F. Thread-2 one-line verdict

Downstream interactions are real but live on a different axis than quali's: the ordering side is
~persistence/6.5%-capped, so the transplantable lever is the prior-stage-order × pace-deviation
term (measured failure mode: race module 29.8% on flip pairs), while the genuine
information-not-calibration deficit downstream is on the UNCERTAINTY axis (event-conditioned `s_e`
CV 0.31/0.35 + disagreement 16%/19%, already routed to Thrust B). The compound-regime "natural
conditioning signal" is currently blocked: β is minor/quali-side, γ did not identify (confounded).
