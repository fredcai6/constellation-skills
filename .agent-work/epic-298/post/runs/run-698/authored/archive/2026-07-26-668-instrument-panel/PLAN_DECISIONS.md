# #668 Converged Gate Plan (design-it-twice + feasibility-probe output)

## Design-it-twice record
- **One thing designed twice:** the gate plan realizing the four fixed instruments + the F12
  gate, under distinct constraints.
- **Candidates:** A = smallest-diff (sonnet Plan agent); B = most-testable (sonnet Plan agent).
- **Panel-vs-single (this brief):** 2 candidates, not a full panel — the instrument set is
  frozen by owner ruling (lowest dimensionality), so the design variance is narrow (gate
  decomposition + two method-realization forks). Named road: a 3rd "best-seam-placement"
  candidate was skipped as low-marginal-value given the frozen shape.
- **Convergence (human-only in spirit; here the delegated Commander converges + the Admiral/
  owner ratify at plan + F12):** a **hybrid** — Candidate B's testable spine (each instrument a
  pure, synthetically-falsifiable module; the golf-correction two-sided synthetic test as the
  load-bearing falsification) + a **diagnosis-first G1** that both candidates' shared finding
  and my feasibility probe forced.

## The shared finding that reshaped the plan (both candidates + my probe)
`driver_class_observables` is **round-aggregated** (one row per driver×class×round), NOT
lap-grain. Therefore:
- The cheap "odd/even distance-sample" split (Candidate A) is **statistically the WRONG
  split-half** — spatial autocorrelation flatters replication by construction (the exact
  "mechanically-plausible-but-wrong" trap the launch order RULING warns of). **Rejected.**
- A statistically-sound split-half needs a defined **repeated-measurement unit**. My probe:
  GB-Q has 20 drivers, ~16–19 TIMED laps/driver (per-lap rows present in `f1_data_2023.db`),
  but per-lap *speed telemetry* availability and the observables/reference own-DB **locations**
  (they live in the MAIN checkout's `.agent-work/archive/`, not this worktree) are unverified.
- ⇒ The split-half unit is a **load-bearing pre-registration decision** that must be grounded
  in a data-availability diagnosis, then registered in the F12 set and floated to the owner —
  NOT chosen silently at plan time.

## Converged gates (6)
- **G1 — F12 diagnosis + pre-registration proposal (reasoning/diagnosis gate; EVIDENCE-ONLY;
  computes NO replication/coverage/scorecard OUTCOME).** Probe (a) the real GB-Q driver×class
  SUPPORT distribution (n_points per cell) + locate the observables/reference own-DBs; (b)
  realizable split-half units (per-driver timed-lap counts, per-lap v_real telemetry presence,
  segment-instances per severity class); (c) a synthetic noise model (from #665's generative
  model + observed support). Produce the **1-page pre-registration proposal**: `REPLICATION_THRESHOLD`,
  `REPLICATION_MIN_SUPPORT_N` + the `r_floor(n)` support-scaling formula, the channel-comparison
  decision rule + tie margin, and the **split-half-unit registration** (recommended unit +
  rationale + honest bounded-slice caveat). NO frozen module minted yet (owner may adjust the
  values). Self-reviewed (per lesson:self-authored-reasoning-gate-checks-need-review-scrutiny).
  **→ After G1: FLOAT the proposal to the Admiral; BLOCK the real-data run until owner sign-off.**
- **G2 — Instrument 1: variance decomposition** (crew gate; pure module + synthetic tests;
  F12-independent → build in parallel). Car-reference / driver-utilization / residual shares via
  the additive `TwoWayPool` arithmetic (no bespoke model, no interaction term). Driver-utilization
  share reads as a **floor**. Each share falsifiable against synthetic `actual = a·car + b·driver
  + noise`.
- **G3 — Instruments 2+3: golf-corrected split-half replication + σ-honesty + channel-comparison
  MECHANISM** (crew gate; pure module + synthetic tests; F12-independent — thresholds INJECTED as
  params, not baked → buildable before sign-off). Golf-correction = per-driver demean across the
  k severity classes (justified by the additive no-interaction pool); split-half mechanism
  parameterized by the registered unit; σ-honesty via `predictive_t` coverage; per-channel
  replication; channel-comparison decision rule. **Two-sided synthetic falsification** (pure-skill
  signal → ~0 corrected agreement; injected class-shape → recovers its expected strength), reusing
  `scripts/pooling_imbalance_validation_665.py`'s generative model.
- **G4 — Instrument 4: composed-sector scorecard** (crew gate; pure module + synthetic tests;
  F12-independent — consumes the ALREADY-FROZEN `SECTOR_CALIB_*` triple from #660). Position-sum
  construction identity (segments sum EXACTLY to composed FIA sector) + distribution-calibration
  coverage (`predictive_t`, non-Gaussian) vs official sector times; **GATING only on the frozen
  gross-miscalibration bound** (`SECTOR_CALIB_GROSS_MISCALIB_BOUND=0.50`).
- **G5 — Frozen-set finalize (POST-sign-off).** Write the FINAL named `REPLICATION_*` set into
  `src/physics/layer2/frozen_constants.py` with the owner-signed values (no inline literals
  elsewhere). Precondition: F12 sign-off user-decision attached.
- **G6 — Real-data run + versioned report (POST-sign-off; blocked on G5).** Run all four
  instruments on GB-2023-Q (real observables/reference own-DBs + `f1_data_2023.db` sectors),
  wire the frozen values, emit the written **versioned report**: the four instruments' results
  (variance shares incl. the driver floor; golf-corrected replication per class per channel + the
  σ-honesty verdict; the channel-comparison winners; the sector scorecard central + coverage vs
  official) + the frozen constants used + the **1-circuit bounded-scope note (→ #670)**. Reviewer
  verifies numbers reproduce, no sector-outcome leakback, honest bounded-scope + no-frame-kill.

**Parallel while awaiting sign-off:** G2, G3, G4 (synthetic-only). **Blocked on sign-off:** G5, G6.
Map reconcile happens at the spine `reconcile` step (stage `notes-668.md` + `668-cartography/`).

## Cold plan critic — findings triaged (delegated Commander disposition)
A single opus cold critic (3 lenses: intent-fit / testability / simplicity), panel-vs-single:
single strong critic focused on the owner-flagged load-bearing golf-correction hazard (named
road: a full 3-critic panel was available; compressed to one because the instrument shape is
owner-pre-ruled and the highest-value target is one specific hazard). Findings:
- **#1/#2/#4 [BLOCKING] — ACCEPTED, plan corrected.** Per-driver demean is INSUFFICIENT: a
  pooled cell = `grand_mean + driver_effect + class_effect` (`pooling.py:167-169`, additive, no
  interaction), so demeaning per driver leaves the SHARED class main effect, which replicates
  trivially for every driver → a healthy-looking replication with ZERO driver-utilization
  content (the exact artifact the owner ruling warns of). **Fix:** the golf-correction is
  **DOUBLE-CENTERING** — subtract BOTH the driver main effect AND the class main effect from each
  (driver,class) observation; the residual that must replicate is the genuine **driver×class
  interaction** (which the additive pool dumps entirely into `var_resid`). This replicates on the
  **raw `driver_class_observables` substrate**, NOT on pooled cell points (pooled points carry no
  usable within-class-across-drivers variance beyond the shared effect). Double-centering is a
  DATA TRANSFORM (arithmetic residual), **not** a fitted interaction term → owner ruling 4 (no
  interaction terms / no bespoke model) is respected (critic #7). The G3 synthetic falsifier is
  extended: the #665 generator gains a true driver×class interaction term, and a **3-arm**
  falsification — (a) pure overall-skill → ~0 corrected; (b) **pure shared-class, zero
  interaction → ~0 corrected** (the arm that actually distinguishes correct from broken); (c)
  injected interaction → recovers its strength.
- **#3 [SHOULD-FIX] — ACCEPTED.** Add an explicit "no valid split-half / unmeasurable → zero
  signal size is a COMPLETE result" branch (no frame-kill, owner ruling 1). Registered in G1;
  honestly reported in G3/G6.
- **#5 [SHOULD-FIX] — ACCEPTED.** The σ-honesty coverage must be **out-of-sample** (the held-out
  half of the split, or LOO), never self-referential/self-weighted — aligns with the repo's
  `lesson:loo-residual-diagnostic-over-self-weighted-predictor`.
- **#6 [CONSIDER] — ACCEPTED.** `r_floor(n)` + all G1 grounding reads SUPPORT COUNTS (`n_points`)
  and structure ONLY — never a replication/coverage/scorecard outcome. Made explicit in G1.
- **#7 — noted.** Any golf-correction fix must not add a model interaction term; double-centering
  complies.
- **Confirmed sound by the critic:** the G1 pre-registration firewall; instrument-4 leakback
  guard (`strictly_pre=True`, structural cutoff); consume-not-remint of #660 `SECTOR_CALIB_*` +
  #666 `FINGERPRINT_FROZEN`.

## Decision candidates surfaced (grades)
- decision:golf-correction-is-DOUBLE-CENTERING — remove driver AND class main effects; replicate
  the interaction residual on raw observables (NOT pooled cell points). @grade: settled/measured
  (cold-critic-forced correction of the earlier per-driver-demean guess) · leans G1,G3 · settle:
  3-arm synthetic recovery with an interaction-bearing generator.
- decision:golf-correction-is-per-driver-demean — SUPERSEDED by double-centering above after the
  cold critic. @grade: settled/measured · leans G3.
- decision:split-half-unit — @grade: placeholder · leans G1,G3 · settle: G1 data-availability probe
  then owner signature (F12).
- decision:diagnosis-first-G1 — @grade: settled/measured (probe confirmed round-grain + unverified
  telemetry) · leans G1.
- decision:consume-frozen-scorecard-triple — @grade: settled/inherited (#660 already froze it) · leans G4.
