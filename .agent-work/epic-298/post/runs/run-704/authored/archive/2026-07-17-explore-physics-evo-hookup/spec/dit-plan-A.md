# DIT Plan A — Tracer-Bullet-First

**Constraint:** land one real end-to-end vertical slice as early as possible — one weekend, crude
stage-1, injected into fusion behind a toggle, scored by the existing eval harness — before
deepening any single component. Every later phase deepens a piece the tracer bullet deliberately
faked or skipped, and states honestly what that means throwing away.

**Scope inherited from the Ideas Board, not re-litigated:** round-1 endpoint = believable/honest
physics features feeding a direct-BT prototype injection, A/B'd on quali only, dry conditions
first, gates G0 (correlation-with-evo-errors) → G1 (sign-acc/Brier vs baseline + ~0.80 ceiling) →
G2 (fantasy pts/race). NN consumption and driver-utility/affinity are round 2. Calendar is not a
constraint.

---

## 0. What makes a tracer bullet possible here (no new build required to start)

Three things already exist and compose into a same-day slice:

- **The store**: `data/physics_estimates.db:session_estimates` — five-view (braking / traction /
  power_drag / lateral / coast) per-(year, gp, constructor) estimates, `session_type='Q'`, rows
  present for **every season 2019–2026** (x1 verdict). No physics pipeline run is required to get
  the first number.
- **The injection seam**: `driver_residual_history_adapter.py`'s
  `build_neutral_driver_residual_history_field` pattern — construct a `ModuleFieldResult` directly
  (`runtime_contracts.py:89-133`), skip PairBatch/NN/field_solve entirely. This is the exact shape
  #601 Wave 8 already names ("inject as a Bradley-Terry field directly, skip the neural module for
  v1"). Constructor-scope output projects to drivers via `constructor_projection.py` — matches
  cycle-4 decision 3's "constructor grain = accepted round-1 trade."
- **The harness**: `scripts/diagnose_quali_evidence.py` / `diagnose_quali_same_pairs.py` already
  compute the data-only ceiling and model-vs-ceiling sign-accuracy (B12: "eval harness already
  structurally exists"). G0/G1 do not need new scoring infrastructure, only a new column to feed
  them.

The one design move the tracer bullet makes to stay crude: since FP fits are blocked (#513 — no
`fp_mass()`, x1), it uses **prior-round Q-fit history** as the feature, exactly like the existing
`*_from_recent_history` modules use prior results — leak-free by construction, zero new mass-model
work, and it's literally what #601's Wave 7A framing already proposes ("as-of-round join on
prior-round quali fits").

---

## Phases

### Phase 1 — Tracer bullet: one weekend, one number, one gate read
**Builds:** pick one target event with ≥1 prior round of `session_estimates` for its constructors
this season. Composite each constructor's most recent prior-round five-view estimate into a single
weekend-relative scalar (x4's canonical normalization — already the empirically-preferred choice,
no new design needed) with a **placeholder σ** (flat or raw stored-covariance trace — explicitly
not calibrated). Wrap it as a `ModuleFieldResult` via the residual-history pattern, project
constructor→driver, register one `FusionStepConfig` gated by a manifest toggle defaulted **off**.
**Proves/retires:** the entire plumbing chain works end-to-end — store read → composite → as-of
join → `ModuleFieldResult` → fusion registration → toggle → scored output — without betting on any
unbuilt physics. This is the single biggest schedule/integration risk (a seam nobody has exercised
since #450 is still open/unbuilt per x3) and it is now retired for the cost of a script, not an
epic.
**Gate evidence:** informal G0 — does this weekend's composite correlate at all with where evo's
`race_weekend` quali head was wrong? Single data point, directional only, not a go/no-go.
**Thrown away:** the hand-wiring itself (weekend selection, ad hoc composite script) — superseded
by Phase 2's harness integration. The placeholder σ — superseded by Phase 3. The single-scalar
as-of "feature view" is a stub of cycle-4's four-record-type contract, not the real thing.

### Phase 2 — Widen to a real G0 read
**Builds:** run the same crude composite (still prior-round-only, still placeholder σ) across the
full 2022–2025 dry walkforward (2019–2021 as appendix, per cycle-4 decision 4), wired into
whatever walkforward harness the gold pipeline already uses rather than a one-off script.
**Proves/retires:** whether physics-derived capability correlates with evo's actual error pattern
at all, at a statistically meaningful scale — the Wave 7A go/no-go the plan already names. This is
the true G0 gate; Phase 1's read was a smoke test, this is the decision point.
**Gate evidence:** correlation(composite, evo quali-head residual) across ~130+ weekends, reported
with a null-result-is-reportable framing (no kill switch per Ideas Board — a flat G0 still teaches
where the seam is wrong, not whether to stop).
**Thrown away:** nothing new; this phase mostly reuses Phase 1's composite logic verbatim,
confirming it was worth productionizing rather than discarding.

### Phase 3 — σ honesty (#506)
**Builds:** replace the placeholder σ with cross-validated empirical σ (inflate to match observed
out-of-sample error, not the raw bootstrap covariance) for the composite feature.
**Proves/retires:** whether Phase 2's G0 read survives honest uncertainty, and — load-bearingly —
whether the *fusion* step (precision-weighted from here on) would trust an over-confident physics
signal it shouldn't. Sequenced after G0 rather than before it: calibration work is wasted if G0 is
a flat null, so this phase only runs once Phase 2 says the signal is worth trusting at all.
**Gate evidence:** none standalone — this phase is a precondition for Phase 4's G1, not itself
gated. Its evidence is the calibration curve (empirical vs stated σ) attached to Phase 4's report.
**Thrown away:** Phase 1/2's placeholder-σ numbers are retroactively marked informal-only; any
sign-accuracy number computed against them before this phase must not be cited as a G1 result.

### Phase 4 — G1 on the prior-round-only composite
**Builds:** with honest σ, run the composite through real fusion (toggle on) and score
sign-accuracy / Brier against the ~0.80 data-only ceiling and against baseline (toggle off), on the
same walkforward as Phase 2.
**Proves/retires:** whether prior-round physics history alone — the cheapest possible physics
feature, no current-weekend evidence at all — moves quali prediction. This establishes the
**baseline value FP mechanics has to beat**, which is the necessary comparison for Phase 5's
(expensive) build to be judged against anything.
**Gate evidence:** G1 — sign-acc/Brier delta vs baseline, vs ceiling. A null here is diagnostic
(per Ideas Board: "if physics features do worse than FP3 order, the seam was wrong") — it does not
kill the program, it re-scopes what Phase 5+ needs to fix.
**Thrown away:** nothing structural; this is the first phase whose numbers are meant to survive
into the final report.

### Phase 5 — FP mechanics (#513) — the load-bearing spine
**Builds:** `fp_mass()`, run-purpose classification (quali-sim vs race-sim laps), lap-level
representativeness weighting (grip-class apex speeds as mass-robust anchor per cycle-4 decision 2),
and the weekend car-state chain FP1→FP2→FP3→[parc fermé]→Q with process noise. Extends the feature
from "prior-round only" to "current-weekend informed," enabling the three as-of cutoffs
(post-FP1/FP2/FP3) cycle-4 decision 4 specifies.
**Proves/retires:** the user's stated single biggest concern — whether current-weekend FP evidence
adds anything over prior-round history alone (Phase 4's baseline). This is the most expensive build
in round 1 and is deliberately sequenced *after* there is a number to beat, not before.
**Gate evidence:** re-run G1 with FP-informed features; report the delta over Phase 4's
prior-round-only G1, per as-of cutoff (post-FP1 huge-σ expected and fine, per cycle-4 decision 2).
**Thrown away:** Phase 1–4's minimal as-of "feature view" stub is very likely rebuilt here into
cycle-4's real four-record-type contract (weekend-state / car-basis posterior / lap evidence /
feature view) — the storage layer, not just the numbers, changes shape. This is the biggest honest
scaffolding write-off of the whole plan.

### Phase 6 — Unified basis + segmentation (optional depth, judged by Phase 5's margin)
**Builds:** the x7 pull-together list (grip-triplet cross-view correlation, CdA joint persistence
beyond the one-directional Jacobian, shared-trajectory-noise accounting for Braking/Traction/
Lateral, a_long reconciliation) and the property-class segmentation vocabulary (soft/fractional
membership, circuit fingerprint as observability router) that lets the composite become a real
regime×circuit-demand vector instead of one scalar.
**Proves/retires:** whether composite-only (a single number) is leaving the user's named
differentiator (Ferrari-top/RBR-power-7th — an aero/drag-efficiency axis a pooled mean can't
isolate) on the table. Explicitly optional for round 1: if Phase 5's G1 already clears the bar
convincingly, this phase can be deferred whole to round 2 rather than gating G2.
**Gate evidence:** re-run G1 with the multi-axis vector vs Phase 5's scalar; only worth reporting
if it changes the G1 verdict.
**Thrown away:** none of Phase 1–5's plumbing — this phase changes what feeds the same seam, not
the seam itself. Risk: if the joint-basis refit changes the underlying point estimates materially,
Phase 4/5's G1 numbers may need re-running to stay comparable, not just re-interpreting.

### Phase 7 — 2026 posture (two-state Z/X aero)
**Builds:** the two-state latent-mode joint fit for active-aero cars (#499/#483), using the
already-delivered allowance-zone layer (`active_aero_zones.py`) and CdA evidence scorer
(`active_aero_identification.py`).
**Proves/retires:** whether single-θ_D aero mis-fits 2026 sessions badly enough to matter, and
closes the one named hazard that gates the *live* season specifically. Independent of Phases 3–6 in
content (it's a PowerDragView/BrakingView/TractionView fix, not a fusion or FP-mechanics one) so it
can run in parallel with Phase 5/6 rather than strictly after — but it must land before Phase 8 if
2026 weekends are inside the G2 evaluation window.
**Gate evidence:** magnitude-of-mis-fit comparison (single-θ_D vs two-state) on real 2026 sessions;
no fixed pass bar named yet (best-effort posture, no Belgium promise per user).
**Thrown away:** nothing upstream; this phase is additive to the store schema (new fields on
already-delivered 2026 records), not a rebuild.

### Phase 8 — G2: fantasy pts/race, round-1 close-out
**Builds:** nothing new — full dry 2022–2025 walkforward (2026 included if Phase 7 landed) with
whatever composite/vector survived Phases 4–6, scored through `src/fantasy_scoring/` against actual
results.
**Proves/retires:** the actual round-1 endpoint — does the hookup measurably improve fantasy
pts/race vs actual. Closes the program's fundamental question for round 1 and hands off the
decision on round 2 (NN-on-physics-features consumption, driver-utility/affinity).
**Gate evidence:** G2 — fantasy pts/race delta, toggle on vs off, with league placement kept
informational only per the Ideas Board's decision-metric rule.
**Thrown away:** none — this is the terminal report.

---

## Dependency graph (text)

```
Phase 1 (tracer, 1 weekend) ──> Phase 2 (widen, real G0)
                                     │
                                     ▼
                              Phase 3 (σ honesty, #506)
                                     │
                                     ▼
                       Phase 4 (G1, prior-round-only baseline)
                                     │
                    ┌────────────────┼───────────────────┐
                    ▼                                     ▼
      Phase 5 (FP mechanics, #513)               Phase 7 (2026 posture)
                    │                          (parallel-eligible from
                    ▼                           Phase 3 onward; must
      Phase 6 (unified basis + segmentation)     land before Phase 8
      [optional — gated by Phase 5's margin]     IF 2026 in scope)
                    │                                     │
                    └────────────────┬────────────────────┘
                                      ▼
                         Phase 8 (G2, fantasy pts/race)
```

**Where G0 evidence first arrives:** end of Phase 1, same session — a single-weekend,
uncalibrated, directional read. The *decision-grade* G0 (the actual Wave 7A go/no-go) arrives at
the end of Phase 2, before any of the expensive builds (Phase 3 calibration, Phase 5 FP mechanics,
Phase 6 basis unification, Phase 7 aero) are started.

**Risk-retirement order** (cheapest/highest-uncertainty first):
1. **Integration risk** — does the seam even wire together (Phase 1). Nobody has exercised #450
   since it was opened; this was previously unknown and is now cheap to know.
2. **Signal-existence risk** — does physics correlate with evo's errors at all, at scale (Phase 2).
   If this is flatly null, everything downstream is de-prioritized, not cancelled (no kill switch).
3. **Calibration risk** — is an apparently-good G0/G1 read an artifact of over-confident σ fooling
   precision-weighted fusion (Phase 3, gates Phase 4).
4. **Marginal-value-of-expensive-build risk** — does current-weekend FP evidence (the single
   biggest concern, and the most expensive build) actually beat the free prior-round baseline
   (Phase 4 vs Phase 5). This ordering stops #513 from being built on faith.
5. **Depth-vs-composite-is-enough risk** — does unifying the basis / adding regime×circuit
   structure change the verdict, or was a single scalar already sufficient (Phase 6, explicitly
   skippable).
6. **Seasonal-scope risk** — 2026 aero mis-fit magnitude (Phase 7), deferred last because it only
   gates the live season specifically and the primary evaluation window (2022–2025) doesn't need
   it at all.

---

## Thrown-away-work exposure (honest accounting)

- **Phase 1's hand-wiring** (weekend-selection script, ad hoc composite) — thrown away at Phase 2
  in favor of harness-integrated code. Cost: a few hours, deliberately.
- **Phase 1/2's placeholder σ** — every G0/G1-shaped number computed before Phase 3 must be
  re-labeled informal once honest σ lands; nothing computed with it is citable as a final result.
- **The as-of "feature view" schema stub** (Phases 1–4) is very likely rebuilt, not extended, once
  Phase 5 needs the real four-record-type contract (weekend-state / car-basis posterior / lap
  evidence / feature view) to represent the FP1→FP2→FP3→parc-fermé→Q chain. This is the largest
  genuine scaffolding write-off in the plan — a schema built twice because the constraint demands
  something running before the real contract is designed in full.
- **Phase 6's basis unification**, if pursued, can retroactively invalidate the point estimates
  Phases 1–5 were built on (grip-triplet joint fit, CdA reconciliation) — meaning G0/G1 numbers may
  need re-running, not just re-reading, if this phase is taken.
- **Nothing in Phase 7/8** is thrown away; both are additive to whatever precedes them.

---

## Self-critique (tracer-bullet-first, where the constraint hurts)

1. Placeholder σ before Phase 3 means the very first "does this work" signal (Phase 1's informal
   G0) is exactly the kind of over-confident read the user warned against citing as ground truth —
   the constraint front-loads the result most likely to be over-interpreted internally.
2. Building the as-of feature-view schema twice (crude stub, then cycle-4's real four-record
   contract) is real duplicated engineering that a design-the-schema-once approach would avoid —
   the tracer bullet trades integration-risk retirement for a guaranteed rework cost.
3. Testing only prior-round Q history first sidesteps #513 (the user's stated single biggest
   concern) until Phase 5 — an encouraging early G0/G1 could be recent-history-shaped signal evo's
   `*_from_recent_history` modules already capture, not new information, and nothing before Phase 5
   would catch that.
4. Composite-only injection cannot exercise the regime×circuit-demand differentiation (B11) the
   user named as the actual mechanism (Ferrari-top/RBR-power-7th) — early gates structurally
   underestimate physics' real value until Phase 6, which is explicitly optional and might get
   skipped if Phase 5 "looks good enough" on a coarser signal.
5. Sequencing 2026 posture (Phase 7) as parallel-but-late means a 2026-specific failure mode could
   surface only at Phase 8, close to round-1's declared endpoint, despite the dependency (allowance
   zones, evidence scorer) already being delivered and cheap to start earlier.
