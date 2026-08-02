# DIT Plan B — Foundation-First / Deep-Module Correctness

Constraint: no consumer touches a component until it is believable. Build the architecture to
solve the hardest problem, once, correctly. The ordering below is the one named in the brief —
segmentation substrate → four-layer weekend-state model on Q → unified-basis refit with full
covariance → FP extension → feature view → injection → A/B — with a Phase 0 baseline lock added
in front (foundation-first needs a frozen "beat this" target before phase 2 can claim it beat
anything) and a driver-utility phase (3b) inserted where the thematic bearings put it: as part
of the foundation, not a downstream consumer.

**Evidence scale used below** (not an existing repo convention — defined here for self-containment):
- **L1** — runs: code executes against real data, produces output.
- **L2** — internally consistent: sanity checks, leakage tests, unit tests, self-consistency
  (e.g. utility × capability recomposes observed lap time within σ).
- **L3** — validated against an independent benchmark or held-out truth, quantified before/after.
- **L4** — decision-grade: reviewed, gated, feeds a conclusion someone downstream is allowed to
  build on without re-checking it.

---

## Phase 0 — Baseline lock (no code)

**Proves/retires:** Freezes the two numbers every later phase is measured against, and kills two
stale framings before they contaminate design decisions. (1) Retires "2023-Q proven" — x1 already
shows Q+R store coverage is 2019–2026, full 8 seasons; the model only needs to *beat*, not
*build*, coverage. (2) Locks x4's weekend-relative noise numbers (noise SD 49–85% of absolute
across all 11 axes; ~3–5 weekends to resolve a 0.3-field-σ step under relative vs 9–52 under
absolute) as the literal floor Phase 2 must beat on the *same* metric, not a proxy. (3) Locks
x7's five-item fracture list (grip triplet, dual CdA, split a_long, unpropagated shared-trajectory
noise, no cross-view covariance blob) as Phase 3's closure checklist, item for item.

**Gate evidence:** L1 only — a written baseline artifact (this doc + the two excursion results it
cites). No physics claim is made here, so no higher bar applies.

**Unblocks:** every later phase's gate is "beat baseline," not "seems better."

---

## Phase 1 — Segmentation substrate + circuit time-share rollup

**Builds:** Cycle-4 decision #1 (property-based classes over a continuous descriptor substrate,
soft/fractional membership, class count support-driven, per-corner identity deferred). Implemented
by extending `segment_classifier.py`'s existing per-sample tagging
(`straight_brake/straight_throttle/coast/corner`) from hard labels to fractional class weights.
Bundled in the same phase because it's the same underlying substrate: x6's G1 (time-weighting via
integrating 1/v over corner windows, not the current 3-point distance-fraction proxy), G2 (straight
segments as first-class rows — length, duration, top speed reached), G3 (a real lateral-g/radius
axis via `damage_integrals.db:grip_bin_obs`, replacing the fingerprint CSVs' speed-only proxies),
and G8 (the actual per-circuit, per-regime time-share rollup — currently absent everywhere).

This substrate serves two consumers later, deliberately built once: (a) the **observability
router** (thematic bearing #2 — which lap segments carry evidence for which basis parameters) and
(b) the **circuit-demand profile** (idea #11, feeds car/driver affinity in round 2, banked not
chased this round).

**Explicit non-goal:** does not touch the five-view estimator. G4 (cross-year corner-identity
mapping, `corner_matches.csv` at 9/~24 gps today) is widened only for the calendar subset round 1
actually needs, not a full historical backfill — foundation-first on the *load-bearing* piece, not
everything adjacent to it.

**Gate:** L2 — rollup reproduces known circuit character as a sanity check (Monza high power-share,
Monaco high braking/traction-share and low power-share, Spa mixed with long full-throttle sections)
against hand-tagged intuition, not a numeric ground truth (none exists). L1 for G4's widened
match run (corners resolve, jaccard scores sane, no silent renumbering across the round-1 calendar
subset).

**Unblocks:** Phase 2 (the four-layer model's "structured evolution" and "field-car" layers need to
know which segments are informative for which parameter before they can be honestly built) and the
circuit-demand side of round-2 affinity (out of round-1 scope, named so it isn't lost).

---

## Phase 2 — Four-layer weekend-state model on Q

**Builds:** thematic bearing #1, on Q only (already WORKS TODAY per x1, 2019–2026, no coverage
risk). Four layers: **explained physics** (density from measured per-session pressure via
`src/utils/environment`, not fixed RHO=1.2; mass/fuel via `quali_mass()`) → **structured evolution**
(a smooth within-session grip latent — directly answers the user's amendment that track rubbering
evolving *within* a session is a foot-gun a weekend-constant median hides) → **field-car
common-mode state** (the two-stage decomposition the user demanded: solve relative first, *then*
re-anchor onto a best-estimate field-car state so the absolute development story still accrues —
not either/or) → **car signal** (deltas off the field-car state).

**Gate — the one quantitative bar named in the brief:** re-run x4's exact methodology (noise SD of
a car's own weekend readings around its season mean; weekends-to-resolve a 0.3-field-σ step)
against this model's output on the same 11 axes, same 81 trusted car-seasons. Must show
improvement over x4's *relative* numbers (not just over absolute — relative is the current floor,
already 3× better than absolute; beating it means the four-layer model is doing real work beyond
weekend-median subtraction). L3.

**Secondary gate:** the explained-physics layer must demonstrably *explain* known cross-track
differences rather than require a patched correction — e.g. the Mexico-altitude CdA case currently
needs an ad hoc joint-shared-P fix (density-cda-fix memory); under this model that fix should
either become unnecessary or reduce to a documented, quantified residual. L3.

**Retires:** "weekend-median subtraction is the ceiling" and "density is noise" framings (both
explicitly named as wrong in the user's cycle-3 amendment).

**Unblocks:** Phase 3 (needs a stable, honestly-decomposed per-session state to refit the basis
against — refitting a joint covariance on top of a state that still conflates density with car
signal would just re-encode the same fracture one level up) and Phase 3b (utility needs a
believable car-capability baseline to measure "access" against).

---

## Phase 3 — Unified-basis refit with full covariance (x7 closure)

**Builds:** closes x7's five named fractures, one at a time, each with an explicit close-or-defer
call (not a silent partial fix):

1. **Mechanical-grip triplet** (lateral/braking/traction — currently three independent fits, zero
   cross-term, not even tested for co-variation) — fit or test a friction-circle-consistent joint
   relationship; if genuinely independent regimes with no recoverable correlation, say so with a
   number (e.g. measured cross-view Pearson r on point estimates, however weak).
2. **CdA dual-solve reconciliation** (PowerDrag vs Coast — currently an eyeball cross-check, no
   persisted joint covariance) — either a shared joint fit or a persisted `cov(CdA_powerdrag,
   CdA_coast)` computed from the two independent posteriors.
3. **a_long reconciliation** (Braking reads the decoupled-1D Kalman-RTS `[E_total, F_vehicle]`
   state; Traction/PowerDrag/Coast still read `clean_longitudinal_from_raw` — two different numbers
   for the same physical quantity) — retry extending the decoupled filter using Phase 1's
   segmentation substrate as a potential root-cause fix for the #523/#546 throttle-on divergence
   (segmentation may resolve the "circuit-topology-dependent" failure mode named in that honest
   null), OR formally re-affirm the two-estimator split as a documented decision record carrying a
   quantified reconciliation error term forward (mirrors the existing #523/#546 pattern — foundation
   -first values an honest, numbered null over a silent gap, same as that prior decision did).
4. **Shared-trajectory-noise propagation** — Braking/Traction/Lateral already share the same
   smoothed trajectory (`sample_cache`) but each bootstraps its covariance as if independently
   sampled. Propagate the shared upstream trajectory-estimation uncertainty into each view's
   reported covariance (even a documented lower-bound correction is progress over the current zero).
5. **Cross-view covariance persistence** — today `estimate_store` holds five within-view-only 2×2
   blobs; add the cross-view terms recovered by items 1–4 as first-class stored covariance, not
   just a shadow baked additively into one view's diagonal (the current Braking/Traction pin
   mechanism via `cda_frontier_jacobian`).

σ-honesty (#506) is folded in here rather than run as a separate pass — a real, persisted joint
covariance across views *is* the σ-honesty mechanism the fusion layer needs; a bolt-on inflation
factor without the underlying joint structure would be re-deferring the same debt.

**Parallel, non-blocking track — 2026 two-state aero:** the two-state Z/X joint fit (posture #5;
deps already delivered: `active_aero_zones.py`, `active_aero_identification.py`, PR #622's
`RegulationEra`/`aero_axis_2026`) is built alongside Phase 3 but gates only the 2026 cutover, not
this phase's completion. Round 1 validates on 2019–2025 dry Q first (the bulk of the data, and the
coverage where the basis is least confounded); 2026 rows are withheld from the feature view (Phase
5) until this track's own mini-gate closes: does the two-state fit materially change CdA/drag
posteriors vs single-theta_D on 2026 sessions *actually run* (magnitude is currently unknown, per
x3 — this closes that unknown). This is a deliberate, named deviation from strict foundation-first
(see self-critique).

**Gate:** L3 per item — each of the five closes with either a quantified before/after (e.g. "grip
triplet cross-view r now estimable, previously undefined structurally") or an explicit deferral
decision record naming the residual risk carried forward. All five must have a *disposition*, even
if that disposition is "deferred, here's the number this leaves unaccounted for" — an undecided
item is a phase failure, an honestly-deferred item is not.

**Unblocks:** Phase 3b (needs the reconciled car-capability basis to place utility axes against)
and Phase 4 (FP fits need a trustworthy Q-side basis to compare/project against — fitting FP on top
of an unreconciled basis would double-count the same fractures at a second layer).

---

## Phase 3b — Driver utility on the same basis

**Builds:** thematic bearing #3. Driver utility as per-unit-class access of the Phase-3 car
envelope, on the SAME basis (not a separate parameterization) — race-history prior, weekend update.
Uses Phase 1's segmentation to place utility per regime, honoring the per-axis expression nuance
already named: near-zero utility component on power-to-weight, style dimensions (e.g.
throttle-application timing) possible, corners dominate. Delta-basis evolution (utility as its own
basis if same-basis proves too coarse) stays explicitly open/banked, not built this round.

**Gate:** L2 only, by necessity — there is no ground-truth driver-utility number to validate
against (this is the sharpest limit of foundation-first here, see self-critique). Two checks
substitute: (a) internal consistency — utility × car-capability must recompose the observed lap
time within σ, not just look plausible; (b) directional sanity against widely-agreed driver
reputations, used as a smell test only, never as a pass/fail metric.

**Unblocks:** the driver-affinity feature (banked for round 2, out of scope here) and directly
feeds Phase 4's reframing of FP sessions as a driver-utility demonstrator.

---

## Phase 4 — FP extension (C4 / #513)

**Builds:** the piece the user named as the single biggest concern. `fp_mass()` (per-lap fuel/mass
inference — today only `quali_mass()`/`race_mass()` exist, applied unconditionally and wrongly to
FP per x1), run-purpose classification (quali-sim vs race-sim laps within one session), the
weekend car-state process-noise chain (FP1→FP2→FP3→[parc fermé step]→Q, Cycle-4 decision #2, with
the per-team parc-fermé reaction step itself learnable), continuous lap-representativeness weights
(never binary-dropped — grip-class apex speeds as the mass-robust anchor for a power-to-weight
read), and the core reframe: FP is a *weak* car-performance demonstrator (confounded by sandbag/fuel)
but a *strong* driver-utility demonstrator — its main product feeds Phase 3b's per-weekend update,
with car-capability information a secondary, heavily-downweighted byproduct.

**Gate:** L3 — the coverage map FP1/FP2/FP3 × regime with quantified σ vs the Q baseline that x1/
#513 both name as the still-open done-done criterion. Representativeness weighting must be shown to
*derive* something resembling "FP3 is usually most representative" from data on held-out weekends
(concentrating weight on laps independently identifiable as quali-sim by compound+fuel proxy) —
never hand-coded, per the standing rejection of prescribed FP3 weighting. If a known sandbagging
weekend is identifiable in the historical record, the weighting should visibly discount it as an
extra check.

**Unblocks:** Phase 5 (the feature view needs Q + FP + utility all standing on the same reconciled
basis before it can honestly compose a per-weekend feature vector).

---

## Phase 5 — As-of-stamped feature view (Cycle-4 decision #3)

**Builds:** the four record types — weekend-state, car-basis posterior (full covariance,
session-chained), lap evidence, and the as-of-stamped feature view. Only the last is evo-facing;
everything upstream (Phases 1–4's outputs) stays internal. MODEL_VERSION keyed, append-only,
constructor grain (per-entry divergence explicitly banked as a named round-1 approximation, not
silently dropped). 2026 rows only appear here once the Phase 3 parallel aero track has closed its
mini-gate.

**Gate:** L2 — a schema/contract test (append-only: a MODEL_VERSION bump never mutates a
previously-written row — this is literally the "contract freeze" end-state named in the board,
pulled forward here as a testable property rather than deferred hygiene) and an as-of leakage test
(a feature view queried "as of post-FP1" must be provably unable to see FP2/FP3/Q rows — checked by
construction, not by inspection).

**Unblocks:** Phase 6 — this is the first artifact evo is allowed to import.

---

## Phase 6 — Prototype injection (direct-BT field, demoted-to-prototype)

**Builds:** wires the Phase 5 feature view into the BT field solve as one more precision-weighted
source, behind a manifest toggle (anchor pattern). Explicitly a v1 prototype only — per the user's
correction, the end state is a neural module consuming physics features, not this; direct injection
exists solely to test signal cheaply before paying training cost.

**Gate:** L1/L2 — wiring exists, unit-tested, toggled off by default, and the live gold pipeline
runs unchanged (bit-identical) with the physics toggle OFF. This is a regression-safety gate, not a
value gate — no predictive claim is made or measured here.

**Unblocks:** Phase 7 — the only phase allowed to touch real evaluation numbers.

---

## Phase 7 — A/B harness (Cycle-4 decision #4) — LAST

**Builds:** the full three-gate evaluation exactly as pinned — **G0** correlation-with-evo-errors
screen → **G1** quali sign-accuracy + Brier vs baseline and the x2-measured ~0.80 FP-data ceiling
(remaining headroom ~3pp headline / ~0.3pp OOS against current gold) → **G2** fantasy pts/race, the
program's actual decision metric. Three as-of cutoffs (post-FP1/FP2/FP3) make the honesty curve
measurable. 2022–2025 walkforward scored, 2019–2021 as an appendix. Dry-conditions only, wet
flagged and excluded. Every gate is reportable either-way — a loss is diagnostic (the seam was
wrong somewhere upstream), not a kill signal, per the standing "no kill switch" decision.

**Gate:** this phase *is* the gate — there is no further phase to unblock inside round 1. A pass
at G2 is the round-1 endpoint; a stall at G0/G1 sends the finding back to whichever upstream phase
the correlation screen implicates (most likely Phase 4's FP confounding or Phase 3's aero handling,
per the risk-retirement order below), not a restart of the whole plan.

---

## Dependency graph (text)

```
Phase 0 (baseline lock)
   |
   v
Phase 1 (segmentation substrate + circuit rollup)
   |
   v
Phase 2 (four-layer weekend-state model, Q only) --- must beat Phase-0-locked x4 floor
   |
   v
Phase 3 (unified-basis refit, x7 closure) ----+---- Phase 3-2026 (two-state aero, parallel,
   |                                          |      gates ONLY 2026 rows at Phase 5)
   v                                          |
Phase 3b (driver utility, same basis)         |
   |                                          |
   v                                          |
Phase 4 (FP extension, #513)                  |
   |                                          |
   v                                          |
Phase 5 (as-of feature view) <----------------+   (2026 rows gated here)
   |
   v
Phase 6 (prototype injection, wiring only)
   |
   v
Phase 7 (A/B harness — G0 -> G1 -> G2)  <-- FIRST real predictive-value evidence in the plan
```

Every arrow is a hard gate: the downstream phase's engineers should not be able to start
meaningful work until the upstream gate's evidence artifact exists and is reviewed. The one
deliberate exception is the Phase-3-2026 side track, which runs concurrently with Phase 3/3b/4 and
only blocks at the point 2026 rows would enter Phase 5.

## Where G0 evidence first arrives

**Phase 7.** Not before. This is the defining consequence of the constraint: six full phases of
internal-correctness work (segmentation, stage-1 statistical floor, cross-view covariance, FP
confounding, utility placement, contract hygiene) complete before the plan produces a single
number that speaks to whether any of it helps predict a quali session. That is the point of
foundation-first — and its central cost (see late-surprise exposure below).

## Risk-retirement order

1. **Staleness/coverage risk** (Phase 0) — cheapest, retired first, pure bookkeeping.
2. **Observability-routing / circuit-demand structural risk** (Phase 1) — is there even a
   principled way to say which lap segment informs which parameter.
3. **Stage-1 statistical-floor risk** (Phase 2) — does the new state model numerically beat the
   already-good x4 relative floor, on x4's own terms.
4. **Cross-view correlation / σ-honesty risk** (Phase 3) — is the basis internally coherent, or
   does it still contain unrecognized duplicate/independent-in-name-only parameters.
5. **Driver-utility placement risk** (Phase 3b) — weakest gate in the plan (L2 only, no ground
   truth); retired here because it's cheap relative to Phase 4 and unblocks Phase 4's reframing.
6. **FP-confounding / mass-model risk** (Phase 4) — the user's named single biggest concern;
   retired late deliberately, because it needs a trustworthy Q basis (Phase 3) to project against
   and a driver-utility frame (Phase 3b) to route its signal into.
7. **Contract/leakage risk** (Phase 5) — cheap, mechanical, retired just before the evo boundary.
8. **Wiring/regression risk** (Phase 6) — cheapest phase in the plan, deliberately trivial.
9. **Predictive-value risk — does any of this beat FP3/the 0.80 ceiling** (Phase 7) — retired
   LAST, at maximum cost if it fails.

## Late-surprise exposure

This is the named risk of the constraint, stated plainly: **the biggest uncertainty in the whole
program — whether physics features can beat the ~0.80 FP-data quali ceiling at all (x2's finding:
remaining OOS headroom is only ~0.3pp against the CURRENT feature set) — is not tested until
Phase 7, after every other phase has already been paid for.** Six phases of real engineering
investment could complete cleanly, each individually gated and correct, and Phase 7 could still
come back near-flat. Concretely:

- **2026 aero magnitude is genuinely unknown** (x3: "how wrong are single-theta_D fits on 2026
  actually" has no measured answer yet) until the Phase-3 parallel track runs real 2026 sessions —
  which happens mid-plan, not at Phase 0. If the two-state fit turns out to need more than a
  bolt-on (e.g. a genuine basis-shape change), that surfaces after Phase 3's main track has already
  frozen its parameterization, forcing a partial Phase 3 redo.
- **Driver utility (3b) has no ground truth anywhere in this plan.** If the utility layer is
  subtly wrong — plausible, since its only gates are self-consistency and vibes — nothing in
  Phases 4–7 is positioned to catch it; it would only surface once round-2 affinity features
  built on top of it underperform, entirely outside this plan's own evaluation.
- **A single upstream mistake in Phase 2 or 3 propagates silently through three more phases**
  before Phase 7's G0 screen has any chance of flagging it, and even then G0 only says
  "correlates with evo error," not which upstream phase is responsible — the diagnosis work after
  a Phase 7 miss could be substantial.

## Self-critique (constraint costs)

- **Time-to-first-real-signal is long** — six gated phases before any quali/fantasy evidence,
  in tension with the user's stated urgency (round 1 targeted for summer break, ~6 weeks out) and
  explicit standing philosophy ("chase every avenue optimistically," don't be pessimistic about
  what data can do). A foundation-first plan is the slowest of the three constraints to a first
  real result by construction.
- **Risk of gold-plating a component Phase 7 later reveals didn't matter** — e.g. closing the
  grip-triplet cross-view correlation (Phase 3, item 1) is real engineering work, but "does this
  correlation matter for quali prediction" isn't asked until Phase 7, six phases later. A
  cheaper-constraint plan would ask that question first and might legitimately skip item 1 entirely.
- **Driver-utility (3b) is the weakest link precisely because foundation-first insists on building
  it before any consumer exists to validate it against** — there is no external check available at
  the point it's built, only self-consistency, so a subtle error here is the hardest failure mode
  in the whole plan to catch.
- **The 2026 aero parallel-track carve-out is a deliberate, named crack in the constraint** — a
  purist reading would refit the entire basis for two-state aero before declaring Phase 3 done;
  doing so would gate all of round 1 on a live-season-only fix affecting <15% of the historical
  Q store, which felt like the wrong trade, but it is foundation-first bending, not foundation-first
  in full.
- **No cheap early peek at the 0.80 ceiling exists in this plan** — a two-day correlation probe
  using only the Phase-1/2 output, run once and thrown away, would de-risk the entire back half of
  the plan for almost nothing, but strictly obeying "no consumer touches a component until it is
  believable" forbids exactly that kind of throwaway early look.

---

Read-only on the repo; nothing was modified outside this file. Source: `IDEAS_BOARD.md` in full,
plus `excursions/x1-coverage-RESULT.md`, `x4-normalization-RESULT.md`, `x6-circuit-demand-RESULT.md`,
`x7-basis-map-RESULT.md`.
