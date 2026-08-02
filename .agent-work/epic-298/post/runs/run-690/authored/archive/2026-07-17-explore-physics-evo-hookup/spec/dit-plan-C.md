# DIT Plan C — Earliest-Signal / Parallel Tracks

Constraint: maximize early information per unit of work. Six tracks run concurrently from day one of round 1, each front-loaded with its cheapest decisive probe. Tracks converge at named integration gates (IG#), which feed the program's own evidence gates already pinned in the Ideas Board (G0 correlation screen → G1 quali sign-acc/Brier vs baseline+ceiling → G2 fantasy pts/race). I do not redefine G0/G1/G2 — I sequence six tracks to hit them as early and as cheaply as possible, and to stop tracks that stop paying for themselves.

Round-1 scope inherited, not re-litigated: dry conditions only, quali task only, composite-only feature injection (five-view composite, not per-axis), direct-BT-field prototype (not the NN end-state), 2022–2025 walkforward scored / 2019–2021 appendix, constructor grain. Calendar is not a constraint.

## The six tracks

**Track 0 — Harness & compose scaffold.**
Build the mechanical infrastructure every other track needs to turn a feature into a gate reading: the #450 compose step, the A/B manifest toggle (physics-fusion-step behind one flag, anchor pattern), and the three gate scorers (G0 correlation script, G1 sign-acc/Brier vs baseline and the ~0.80 FP-data ceiling, G2 fantasy-pts walkforward). Split internally: the G0 scorer is a trivial join+correlation script (hours); the G1/G2 harness (#450 + BT injection + manifest toggle) is real but self-contained infra work, gated on nothing except itself. Starts day one, in parallel with everything.

**Track 1 — Q-only earliest-signal probe (the cheapest decisive move in the whole plan).**
Run the G0 correlation screen TODAY against the EXISTING five-view Q estimate store (2019–2026, all constructors, weekend-relative normalized per x4's already-proven canonical form) joined to evo's own quali errors (the diagnose_quali_* harness already exists per B12). Zero new estimator code — this is a join and a correlation, not a build. Decisive because it answers the one question every downstream track's priority depends on: does today's admittedly-imperfect physics axis carry information evo's own errors don't already have? A strong positive result licenses pushing a Q-only prototype through the full gate sequence immediately, in parallel with the expensive FP build (see IG3). A null/weak result doesn't kill anything (no kill switch, per the board) but reweights effort toward affinity/race-distance/σ layers rather than betting the round on FP refinement alone.

**Track 2 — SQ coverage extension.**
Invoke the unmodified Q estimator against SQ sessions (single-flying-lap format, plausibly compatible per x1's read-only finding — "never invoked"). Near-free: no new code, just a new session-type argument. Decisive in two ways: it expands Track 1's n onto sprint weekends without any build, and it retires the specific risk x1 flagged twice this cycle — that coverage optimism from a memory/doc read turns out wrong once actually exercised (SQ was flagged UNKNOWN in exploration, unlike Q/R which were verified by store rows). Fold results into Track 1's screen; don't stand up a separate gate for it.

**Track 3 — FP mechanics build (#513, the user-named single biggest concern).**
The heaviest, most valuable, structurally load-bearing track: `fp_mass()`, run-purpose classification (quali-sim vs race-sim), lap-level representativeness weights (continuous, never binary-dropped), and the grip-from-exit-speed power-to-weight extraction that de-confounds sandbagging from real pace. Starts day one — earliest-signal does NOT mean "do the cheap tracks first, then the hard one." Its own internal sequencing still front-loads the cheapest sub-probe: before building the full lap-level weighting machinery, hand-validate grip-from-exit-speed discrimination on a small known set of FP2 quali-sim vs race-sim laps (teams whose run purpose is publicly known from timing-sheet commentary or lap-time clustering). If exit-speed-derived grip can't separate a hand-picked obvious case, the fuller build is de-risked before it's funded.

**Track 4 — Segmentation + circuit-demand substrate (x6 buildout, cycle-4 decision #1).**
Cheapest-first move applied to the constraint's own recommended build: before building the property-mixture soft-segmentation vocabulary the cycle-4 decision calls for, test whether the EXISTING segment_classifier tagging (already labels every sample straight_brake/straight_throttle/coast/corner) suffices for a first-pass per-circuit regime time-share rollup with no new vocabulary work at all (self-gate IG2). Only proceed to the fuller property-mixture rebuild if the cheap rollup is visibly too coarse to route observability. This track's output is round-1 raw material (affinity substrate), not a round-1 feature — per the board, affinity/driver-utility *consumption* is explicitly round-2 scope, so Track 4 must not be allowed to balloon into a full affinity feature build this round.

**Track 5 — Stage-1 product contract scaffold (four-layer weekend-state model, cycle-4 decision #3).**
Build the four record types (weekend-state / car-basis posterior with full covariance / lap evidence / as-of-stamped feature view) as a THIN schema first, populated by pure re-projection of the CURRENT five-view store — no new modeling. This proves the contract is usable end-to-end (and gives Track 0's harness something real to consume) before either Track 1's Q-only signal or Track 3's FP signal has to conform to it. Track 3 must write into this contract from the moment it has any output, not retrofit at the end — this is the plan's main defense against the constraint's named failure mode (see integration-risk section).

**Track 6 — 2026 posture (two-state Z/X aero, cycle-4 decision #5).**
Lowest urgency for round 1's own gates: the A/B harness walkforward window is 2022–2025 (dry, 2019–2021 appendix), so 2026 never enters G0/G1/G2 scoring this round. Its only job here is to retire the one named unknown — magnitude of single-theta_D mis-fit on actual 2026 sessions (flagged unknown by both x1 and x3) — using dependencies already delivered (active_aero_zones.py, active_aero_identification.py, PR #622 RegulationEra fix). Cheap: a handful of 2026 sessions run through both the old and new aero treatment, diffed. Gates live 2026 rollout, not round-1 evidence.

## Integration gates

- **IG1 (arrives first, ~day 1–2, no build required):** Track 0's G0 scorer + Track 1's join produce the program's first hard evidence — before FP mechanics work is anywhere near done. This is where **G0 evidence first arrives.**
- **IG2 (self-gate, cheap):** Track 4 reports whether existing segment tags suffice. Positive → short-circuit to affinity substrate handoff (banked for round 2). Negative → fuller property-mixture build, explicitly scoped as continuing background work, not a round-1 gate dependency.
- **IG3 (the plan's central early win):** Track 5's thin schema + Track 0's harness combine to push a **Q-only, FP-free** composite feature through the FULL G0→G1→G2 sequence on the 2022–2025 walkforward. This proves every mechanical piece (compose, BT injection, manifest toggle, all three scorers) works end-to-end using only data that exists today, and produces a real (if unambitious) fantasy-pts-per-race baseline before the expensive FP track has delivered anything.
- **IG4:** Track 3 delivers its first lap-level representativeness weights into Track 5's populated contract → re-run G1 with FP-augmented composite features → compare directly against IG3's Q-only G1 result. This is where FP's actual marginal value gets measured against a real number instead of the user's (well-founded) prior that it matters most.
- **IG5 (optional / likely round-2):** Track 4's circuit-demand rollup, if it proceeded past IG2, crosses with Track 3's regime outputs into affinity candidates. Feature injection here is out of round-1 scope per the board's own consolidation ("NN + driver-utility consumption = round 2"); IG5 exists only so the substrate isn't wasted if it's ready early — do not let it pull a gate rerun into round 1's critical path.
- **IG6:** Track 6's magnitude read gates the go/no-go on including 2026 in *live* rollout once round-1 passes on 2022–2025. Does not touch G0–G2.

## Dependency graph (text)

```
Track 0 (harness) ──────────────┬─> IG1 ──┬─> IG3 ─> G1(Q-only) ─> IG4 ─> G1(FP-aug) ─> G2
Track 1 (Q-only G0 probe) ──────┘         │
Track 2 (SQ coverage) ─── extends T1 ─────┘
Track 5 (stage-1 contract, thin) ─────────────────> IG3 ─(populated by T3)─> IG4
Track 3 (FP mechanics) ──────────────────────────────────────────────────> IG4
Track 4 (segmentation) ──> IG2 ─┬─ [suffices: handoff, banked] 
                                 └─ [insufficient: fuller build] ──> IG5 (optional, round-2-leaning)
Track 6 (2026 posture) ──> IG6 (live-rollout gate only, outside G0–G2)
```

## Risk-retirement order (cheapest/most-decisive first)

1. **G0 Q-only correlation** (Track 1) — does physics carry any signal at all beyond what evo's errors already imply. Cheapest possible probe in the plan.
2. **SQ coverage** (Track 2) — is the coverage-optimism pattern (x1/x3 already caught it twice) wrong a third time.
3. **Segmentation sufficiency** (Track 4, IG2) — is the property-mixture rebuild actually needed before funding it.
4. **Stage-1 contract usability** (Track 5, thin re-projection) — is the four-record schema real or aspirational, tested with zero new physics.
5. **Harness mechanics** (Track 0) — does #450 + BT injection + manifest toggle + all three scorers actually run, in parallel with 1–4, converging at IG3.
6. **Full-loop Q-only read** (IG3) — does the WHOLE pipeline, even with admittedly mediocre features, produce a sane fantasy-pts number end to end. Highest-value single retirement in the plan: it converts every other track's future output into "swap a feature in," not "build a pipeline."
7. **FP mechanics + IG4** — the expensive, structurally-necessary, user-flagged-hardest track, deliberately retired last because it is the most expensive to build and its value is measurable against IG3's real baseline instead of argued from first principles.
8. **2026 magnitude** (Track 6) — retire whenever convenient; blocks nothing upstream.

## Integration-risk exposure

The constraint's named failure mode — divergent tracks that never integrate — concentrates in two places:

- **Track 3 (FP mechanics) is the real exposure.** It is the longest-running, most complex track, and if it builds its own internal representation instead of writing into Track 5's contract from its first output, IG4 becomes a rebuild, not an integration. Mitigation is structural, not procedural: Track 5's thin schema must exist and be validated (IG3) *before* Track 3 has anything to write, so there is never a moment where Track 3 has output with nowhere sanctioned to put it.
- **Track 4 (segmentation) risks running past its own mandate.** Affinity feature consumption is explicitly round-2 scope; IG2's self-gate exists specifically to stop Track 4 from quietly becoming a full affinity build inside round 1. If IG2's verdict is ignored in practice (the track keeps building past "existing tags suffice"), it permanently diverges from the round-1 endpoint and its output either arrives too late to matter or never gets consumed this round.
- Tracks 1/2/6 carry low integration risk: they are short, self-contained, and either fold into IG1/IG3 within days or terminate as a standalone answer (Track 6) that gates a decision outside G0–G2 entirely.

## Self-critique (constraint's failure modes, honestly)

1. Parallelizing Track 3 rather than front-loading it risks the earliest-signal bias quietly becoming an easy-work-first bias: the plan *says* Track 3 starts day one, but six concurrent tracks compete for the same finite attention, and cheap probes are gratifying to close out — the user-named hardest problem is exactly the one most likely to get shorted in practice.
2. IG3's Q-only end-to-end number is genuinely valuable as infra proof, but it is also a trap: a plausible-looking fantasy-pts figure from mediocre features can read as "round 1 basically works," deflating urgency on the FP track the user explicitly called the single biggest concern.
3. Six genuinely concurrent tracks assumes six genuinely independent execution slots. If capacity is actually 2–3 agents, the tracks serialize anyway and this plan's ordering becomes the de facto priority list — which is fine, but the parallel framing then oversells what's actually happening.
4. Tracks 4 and 6 are both designed to ask "can we skip this" as their first move, which is efficient, but it means real design attention on the unified-basis/observability-router thematic bearing (a foundational idea per cycle 3) can get deferred past round 1 entirely if both self-gates come back "good enough."
5. IG1's G0 read runs on a store x7 already flagged as having unmodeled cross-view covariance and a duplicated a_long definition — a null result there could be measurement noise, not an absence of signal, and this plan doesn't build in a check against over-reading IG1 as more decisive than the underlying store quality supports.
