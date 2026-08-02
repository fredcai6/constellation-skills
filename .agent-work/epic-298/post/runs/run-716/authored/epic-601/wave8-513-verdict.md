# Wave 8 · #513 Phase 4 — FP-session fits — VERDICT (Ship I, delegated commander)

**Status:** Machinery COMPLETE + PROVEN CORRECT; powered real held-out run compute-deferred with ETA +
resume command; Phase-4-checkpoint EXPANSION executed (Admiral-directed). Branch `feat/513-fp-fits`
(base main `27b6eac9`). PR #653 open base main, NOT merged (Admiral merges). **See "Phase-4 checkpoint
expansion" section at the bottom for the Admiral-directed additions (G6 re-freeze + faithfulness ruling,
in-flight cleanup fixes, the thin illustrative demo, and the full non-negotiable checklist).**

## Headline
The falsifiable machinery for "does observation-property representativeness weighting beat
clock-distance-to-Q on held-out weekends" is **built, tested, and structurally proven correct** (the
harness's null fixture is reviewer-verified as non-riggable). The FP-fit wiring is **landed, tested, and
live-validated**. The **powered** real held-out run over the frozen 16-weekend LOWO is **infeasible in
one session** — measured single-driver apex-extraction cost is ~120 s, extrapolating to ≈37 h for the
full run — so it is handed back as a bounded, one-command job with a measured ETA (the same disposition
as #646). Honest-scoping of compute is a complete, reportable result.

## What was built (all committed, all reviewer-APPROVED)
- **G1** — `GATE_PROTOCOL.md` FROZEN before any number: 16-weekend 2023 LOWO (hash `f1725bd81cd3eefa`);
  PRIMARY grip (mass-free, read on DIVERGENT cases), SECONDARY longitudinal (matched-σ or
  confounded-labeled); paired-bootstrap significance; emergence (within-session-orthogonal) rule;
  leakage rule; sandbagging = learned<clock; honest-null #628 ship contract; driver-utility transfer.
- **G2** (`d7225e63`) — `mass_model.fp_mass()` returns a **distribution** `FpMass(mass_kg, sigma_kg)` (the
  unobservable FP starting-fuel intercept is carried as σ, never a scalar) + `fp_lap_latent.py`
  (per-lap fuel_est / compound OBSERVED / tyre_life Optional / EMERGENT run_purpose). 155 tests.
- **G3** (`4da241d9`) — per-car `cumulative_track_laps` unlock into `session_estimates`
  (self-healing column + `session_cumulative_track_laps` reusing `compute_cumulative_track_laps`
  unchanged + demo-scoped populate). **Unblocks #626.** 125 tests.
- **G4** (`3a0708b4`) — `fp_representativeness.py`: continuous per-observation weight w∈[0,1] from the
  observation's OWN properties via a transparent logistic — **EMERGENT, no session label**. Passes the
  F3 within-session-orthogonal + F4 cross-session divergent emergence tests (a track-evolution-only
  weighting gets them backwards; reviewer hand-recomputed the sigmoid to confirm). 35 tests.
- **G5** (`f3aa2e84`) — `estimate_session` FP wiring: `session_type`/`mass_kg`/`db_path`; FP resolves mass
  via `fp_mass` at the representative lap. The fp_mass intercept σ **widens** the mass-consuming
  longitudinal axes (cda/p_max/b_b/b_t) via the existing #627 machinery — **widens, never shifts a
  mean**; grip axes untouched; **Q byte-identical** (reviewer verified via git-stash reproduction).
  `estimate_batch` threads `session_type`. 21 FP tests + regression.
- **G6** (`8860d8e4`) — `fp_gate.py` held-out harness encoding the frozen protocol (GateExtractor seam,
  LOWO, learned/clock arms, paired bootstrap, divergent-case read, emergence audit, sandbagging demo,
  both channels) + CLI. 36 synthetic tests incl. **POSITIVE→PASS, NULL→HONEST_NULL (structurally
  non-riggable, reviewer-verified), LEAKAGE (held-out Q cannot reach the learned fit)**.

## Non-circularity proof (grip-anchor → power-residual)
- fuel-accounting → `fp_mass` is independent of any fit (no fit output feeds it). Verified.
- PRIMARY grip (`apex_pace`/lateral) mass-CANCELS → structurally non-circular (mass is absent, nothing
  to smuggle).
- SECONDARY longitudinal: PowerDragView CdA + p/w BOTH consume `fp_mass` (critic F10) → the fp_mass
  intercept σ is propagated into those axes as widened uncertainty (G5), and the SECONDARY is reported
  only at a MATCHED fp_mass-σ stratum or explicitly labeled "confounded, not evidential" (critic F1).
  This is why the SECONDARY is a caveated byproduct, not the primary gate.

## Live validation (real telemetry)
- `fp_mass(2023).mean = 835.5 kg` vs `quali_mass(2023) = 808.0 kg` (+27.5 kg fuel, σ=15 kg) — FP mass ≠
  quali mass, confirmed. Session LOAD ~2 s (store parquet, no FastF1 fallback).

## The compute wall (measured, the reap-trap the launch order flagged)
- Single driver smooth+apex = **120 s** (8 flying laps, 118 apexes). Per session (~15-20 drivers)
  ~30-40 min. Full frozen 16-weekend LOWO grip run (FP1+FP2+FP3+Q) ≈ **37 hours**. 3-weekend slice ≈ 7 h.
- The powered run cannot complete in one session and is NOT safely babysittable with in-turn waiters.

## G7 real-run outcome — HONEST-SCOPED (bounded compute executed; powered run deferred with ETA)
**Bounded compute EXECUTED** in this session: (1) a live FP smoke fit (Q vs FP2) validating the wiring
(`fp_mass` 835.5 vs quali 808.0); (2) a per-driver apex-extraction timing probe (120 s/driver). These
are the bounded-compute measurements the deepest phase's frozen split could feasibly run here; they
established that the **powered** 16-weekend LOWO verdict is a ≈37 h job (infeasible in one commander
session — the reap-trap the launch order flagged).

**Outcome (reported straight, honest-scoping is first-class):** the F10 falsifiable machinery is
**complete and proven correct on synthetic ground truth** — the harness detects a real effect (POSITIVE
fixture → PASS), correctly reports HONEST_NULL where clock is the true signal (NULL fixture, reviewer-
verified structurally non-riggable), and is leakage-free. The **powered real held-out number** (learned
vs clock on the 16 real weekends) is **deferred as a specified, ETA'd job**, not abandoned:
`.agent-work/513-fp-fits/REAL_RUN_HANDBACK.md` carries the real-GateExtractor spec, the nominal-clock
note (DB has no session timestamps), the exact resume command, the frozen split hash, and compute-
reduction levers. **This is a complete deliverable, not a null:** what is proven is the machinery's
correctness + falsifiability; what is deferred is one bounded ≈37 h compute run.

**FLOATED to Admiral** (open at hand-back): whether to (a) accept this honest-scoped deliverable [Ship I
recommendation], (b) commission the real GateExtractor as its own crew gate + run a bounded powered slice,
or (c) run the full ≈37 h job. Ship I proceeded to PR-open under the sanctioned honest-scoping latitude;
the Admiral retains merge control and can redirect on the PR.

## Explicit-unknown status (OWNER HARD REQUIREMENT — satisfied)
- FP starting-fuel intercept: UNRESOLVED → carried as `fp_mass` σ (dominant), never a point value.
- FP longitudinal axes (cda/p_max/b_b/b_t): reserved wide σ via #627 `effective_axis_sigma` /
  `UNRESOLVED_AXIS_SIGMA_FRAC` when a real mass σ is present. Nothing dropped.
- Sandbagging/detuned: wider σ, never bias (direct instance of the discipline).

## Dispositions
- **#646 full re-pop:** HANDED BACK. Bounded demo scope only here. **BLOCKER for #646 (tc3):**
  `scripts/backfill_estimate_store.py` (the D9-canonical writer) has the SAME missing-`session_type` bug
  G5 fixed in `estimate_batch` — it must thread `session_type` into `estimate_session` before any real FP
  backfill, else FP rows silently get quali_mass. Resume command + ETA for the powered run: see G7 section.
- **Parc-fermé full per-team×season fitted distribution:** BOUNDED-DEFERRED (reserved slot). WHAT: a
  learnable per-team Friday→Saturday parc-fermé-reaction distribution as an explicit weekend-chain step.
  WHY: data thinness (per-team×season parc-fermé samples are few) + reap-trap prudence on the heaviest
  phase. The process-noise weekend-chain framing IS carried in the representativeness weighting (earlier
  sessions down-weighted only via their emergent observation properties, not a session label). WHAT'S
  NEEDED: a powered multi-season fit once the real LOWO extractor runs at scale.
- **per-car cumulative_track_laps unlock:** LANDED (G3). ShipE-626 confirmed the semantics
  (rubber-at-representative-lap per constructor, field laps, `< anchor` convention) + flagged a small
  well-signed over-count (fastest lap sits later → slightly over-counts rubber vs the pooled mean);
  documented as an approximation, cleaner pool-weighted-mean definition noted for later.

## Named limits / triage candidates (route at epic closeout — NOT filed by me)
- **tc1** — `fp_lap_latent` track_status uses an empty-string missing sentinel; accepted (unambiguous),
  make it Optional[str]=None for consistency in a follow-on.
- **tc2** — #646 seam: `estimate_batch` resolves constructor via live FastF1 TeamName while
  `session_cumulative_track_laps` uses `session_classifications.team`; reconcile before scale backfill.
- **tc3** — #646 BLOCKER (above): `backfill_estimate_store.py` missing `session_type` threading.
- SECONDARY longitudinal channel is fp_mass-σ-confounded by construction (reported matched-σ or labeled
  confounded — this is honest, not a defect).
- The powered real F10 verdict is compute-deferred (this verdict's headline).

## Exact test counts
G2 155 · G3 125 · G4 35 · G5 21 (FP) + regression · G6 36. All targeted suites green; the full
`tests/unit/physics` region suite exceeds the harness sync timeout (gate checks narrowed to targeted
files; `--baseline` simplification PASS on all touched paths).

## DB-clean confirmation
`git status --short data/` clean at every gate; no `data/*.db` committed (#632). Scratch DBs: none created.

## Compute-tax note (#644)
Detached launches used OPENBLAS/OMP=4. The #644 single-thread cap ~2x's fit time; not changed here
(follow-on #650 owns it). The dominant G7 cost is per-lap trajectory smoothing, not BLAS — thread
recovery helps the numpy/scipy portions only.

## #560 coordination
Extended the existing soft `_support_trust_profile` (no new hard flying-lap floor — #560's explicit
finding); corrected its non-Q reason wording now that FP uses fp_mass, not the quali-mass assumption.

## Cartographer map impact
New: `fp_lap_latent.py`, `fp_representativeness.py`, `fp_gate.py`, `scripts/fp_representativeness_gate.py`;
`mass_model.fp_mass`/`FpMass`; `session_estimator` FP params; `estimate_store` cumulative_track_laps +
mass_sigma_kg_assumed; `session_race.session_cumulative_track_laps`. Reconcile pending (spine `reconcile`).

---

# Phase-4 checkpoint EXPANSION (Admiral-directed, executed after initial spine close)

At the Phase-4 checkpoint the Admiral expanded scope. All items below executed on the same branch/PR #653.

## (a) G6 faithfulness ruling — min-max normalization + L2 shrinkage = FAITHFUL (my call, stated)
The G6 harness's `divergent_case_read` min-max-normalizes BOTH weight arms before differencing, and
`fit_weight_params` uses L2 shrinkage. **RULING: both are FAITHFUL to GATE_PROTOCOL sec 6, not an
easier-pass.** Reasoning: (1) the min-max is an ARM-FAIRNESS fix — clock is an unbounded exponential decay,
learned a bounded logistic; comparing `|w_learned − w_clock|` on their raw native scales let whichever arm
had the wider numeric range monopolize the top-tercile divergent split (a real TDD-RED: false HONEST_NULL on
the raw-scale diff). Min-max is applied SYMMETRICALLY to both arms over the same pooled set — it changes
neither arm's ranking, only puts them on one scale so "where they disagree" is measured fairly. (2) L2
shrinkage regularizes the learned fit against overfit on thin folds — it makes the learned arm MORE
conservative (harder to beat clock), not easier. (3) Both were fixed on SYNTHETIC fixtures BEFORE any real
number, and the harness's NULL fixture remains structurally non-riggable (reviewer-verified: identical
features force the learned weight to a constant regardless of fit). Neither change makes a PASS easier; both
make the comparison honest. **Protocol-implementation delta noted:** GATE_PROTOCOL sec 6's literal
"|w_learned − w_clock|" is implemented as a scale-normalized difference — a faithful encoding, recorded here.

## (b) Harness freeze RE-STAMPED (before any real number)
**HARNESS_FREEZE_HASH = `349216857e6c09d9`** — sha256 over `fp_gate.py` (7f915f8d3b63) +
`fp_representativeness.py` (20fed349c415) + `GATE_PROTOCOL.md` (93c4b5a4cc0f), at git HEAD `74bfc6aa`.
Stamped BEFORE the thin demo ran. Once a real held-out number is observed the harness is untouchable at
this hash.

## (c) Grip-PRIMARY / longitudinal-SECONDARY framing (reported either-way)
Unchanged and reaffirmed: PRIMARY = grip (mass-free, non-circular, read on divergent cases) is the
load-bearing gate; SECONDARY = longitudinal power-to-weight is reported WHICHEVER way it lands. On real
data the SECONDARY is expected `CONFOUNDED_NOT_EVIDENTIAL` because `fp_lap_latent` supplies a CONSTANT
`fp_mass_sigma_kg` (FP_FUEL_INTERCEPT_SIGMA_KG=15 kg) — the per-lap-width refinement that would make it
evidential is **filed as #652** (do NOT fix in #513). An honest-null/confounded SECONDARY is a complete result.

## (d) In-flight cleanup (Admiral standing ruling: fix small triage, don't park) — DONE
- **tc3 (backfill session_type) — FIXED** (commit a83d843a). `scripts/backfill_estimate_store.py` (the
  D9-canonical writer #646 uses) now threads `session_type` + `db_path` into `estimate_session` — same bug
  fixed in `estimate_batch`. RED-first (`assert None == 'FP2'` → GREEN, 11 tests). **This unblocks a clean
  #646 re-pop.** Confirmed: the G7 demo does NOT route through this writer (it calls apex/estimate_session
  directly), so the bug never touched any demo number.
- **tc1 (track_status sentinel) — FIXED** (commit a83d843a). `FpLapLatent.track_status` now `Optional[str]`,
  `None` on NULL (mirrors tyre_life). RED-first, 52 tests.
- **tc2 (constructor-resolution seam) — DEFERRED to #646 with reason** (per the Admiral guardrail: balloons
  past a small fix → file+defer). `estimate_batch`/`fit_batch._list_drivers` resolves constructor via the
  session's `get_driver` TeamName; `session_cumulative_track_laps` uses `session_classifications.team`. A
  naming-normalization reconcile across two seams is a real audit/refactor, NOT a one-liner, and it ONLY
  bites the real #646 backfill at scale (the demo-scoped populate + the harness never hit it). It belongs to
  #646, sequenced with the tc3 fix.
- **Simplification-check-in-Required-Evidence gap** (flagged by G3 + G6 crews) — folded into the run
  retrospective (AGENT_FEEDBACK.md 513-fp-fits): every handoff touching src/tests must name
  `simplification_limits` (--baseline min, strict --paths on touched files) by default.

## (e) Real GateExtractor + thin illustrative demo (Admiral/owner GREENLIT) — HONEST real-data status
Built the real `fp_gate_real_extractor.py` (GateExtractor over apex_extract/apex_pace, reviewer-APPROVED,
frozen harness untouched, commit 807556b7).

**Real-data status (precise — no over-claim):** the extractor is SHAPE-VERIFIED + unit-tested (13 tests).
For the "we've SEEN it run on real telemetry" floor, a MINIMAL real pass was run to completion (Hungary
2023 FP2, 8 drivers, fastest-2-laps): **7 real `RawFpObservation` (533 s) + 6 real `RawQTarget` (691 s),
end-to-end in 1224 s (~20 min)** — real grip values, observed compounds, emergent `run_purpose=push`
(e.g. Alpine FP grip=0.1107 / Ferrari Q grip_capability=0.0263). The RealGateExtractor is thus proven to
produce real observations end-to-end on real telemetry, NOT mocks. [Placeholder filled by Admiral post-hoc
from `.agent-work/513-fp-followup/MINIMAL_PASS.txt`; Ship I's session ended before substituting it.]

**Stall diagnosis (a reviewer non-blocking finding, adjudicated):** the Rx reviewer reported the demo
"stalled, no live process" — that was a MONITORING ARTIFACT, not a hang. The `py` launcher is a #648-inert
stub at 0 CPU; the real `python.exe` CHILD accumulated CPU steadily (417→966→1212 s across checks). Diagnosis
= **(c) genuinely slow**, not #648-hang and not reap. This CONFIRMS the powered run needs the ~5-10 h
optimization (section f) before it is commissioned — a single full session is slow end-to-end.

**The full 4-weekend thin demo** (Hungary/Spain/Singapore/Netherlands, FP2+FP3+Q, fastest-3-laps, 4 LOWO
folds) is **ILLUSTRATIVE-NOT-EVIDENTIAL — NOT the frozen F10 verdict** (4 folds is underpowered by design);
it is compute-heavy (~54 min) and, if it does not complete in-session, its end-to-end real-data validation
folds into the deferred powered run. Result (if it lands): "Thin demo result" subsection below.

## (f) Optimization headroom on the ≈37 h powered run (Admiral question) — YES, plausible
The 120 s/driver cost is per-lap trajectory smoothing. Stackable reductions: (1) the shared per-driver
`sample_cache` `estimate_session` already threads (~2.4x per prior HP-cache work); (2) fastest-K-laps
(K=2-3 vs 8) ~2-3x fewer smooths; (3) a persisted per-(session,driver) apex parquet makes re-runs free.
Stacked, ≈37 h plausibly lands in the **~5-10 h** range. RECOMMENDATION: the owner should optimize-first
rather than brute the 37 h. (Not built here — a scoped follow-on.)

## (g) Parc-fermé — EXPLICIT reserved slot (owner-RATIFIED bounded-defer)
WHAT is deferred: a learnable per-team Friday→Saturday parc-fermé-reaction distribution as an explicit
weekend-chain step (how well each team converts practice info into quali pace). WHY: data thinness
(per-team×season parc-fermé samples are few) + heaviest-phase reap-prudence — owner-ratified at the Phase-4
checkpoint. WHAT'S NEEDED to land it: the powered LOWO extractor running at scale + a multi-season fit. The
process-noise weekend-chain framing is RETAINED in the representativeness weighting (earlier-session
observations down-weighted only via their emergent observation properties, never a session label).

## (h) DB-clean + exact test counts (post-expansion)
`git status --short data/` clean at every commit; no `data/*.db` committed (#632). Test counts: G2 155 · G3
125 · G4 35 · G5 21(FP)+regression · G6 36 · real-extractor 13 · backfill-fix 11 · tc1 52 (fp_lap_latent
suite). All targeted suites green (region suite exceeds the harness sync timeout — gate checks narrowed to
targeted files; `--baseline` simplification PASS on all touched paths).

## (i) #644 single-thread cap 2x tax
The #644 guard caps torch to 1 thread; I set OPENBLAS/OMP=4 in every detached launch ENV (the guard's
setdefault respects it). The dominant cost (per-lap smoothing) is scipy/numpy-BLAS, so thread recovery helps
it; the 2x tax is the residual torch-portion cost. Guard NOT changed (follow-on #650 owns it).

## Post-expansion commits
a83d843a (tc3+tc1 cleanup) · 807556b7 (real extractor). Both on feat/513-fp-fits; PR #653 updated.
