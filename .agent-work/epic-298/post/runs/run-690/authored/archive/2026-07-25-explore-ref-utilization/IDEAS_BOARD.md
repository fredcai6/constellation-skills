# Ideas Board — `explore-ref-utilization`

The living record of shared understanding and the **source of truth** for this exploration. Every consolidation updates it. The spec crystallizes from it; a resumed session reads it instead of chat history.

## The point

Reformulate physics→prediction as a **decomposition**, not a feature injection. Reassemble the derived physics into per-car **reference laps** (the modeled car's ideal); measure each driver as **utilization of their own reference**, conditioned on the circuit's composition. Car = reference; driver = utilization. The truth channel handed to the predictive network is built from this decomposition, replacing raw classification positions that entangle car and driver.

Owner-set structure (cycle 1):
- **Two idealized references** — one targeting QUALI, one targeting RACE — sharing the car-capability core. The race reference carries extra driver-dependent dispersion.
- **Unified cross-driver feature = simulated segment-time distributions** (heavy-tailed, correlated), composing segments → sectors → laps.
- **Quali carries one distribution per driver (push); race carries two (push AND managed)** — the race simulator chooses which to draw from by race state.
- Done feels like: a confirmed design for the decomposition — segment vocabulary, fingerprint mechanism, practice update, sizing instruments, integration sequencing — ready to cut into issues.

## Standing design principles (owner-ratified, cycle 1)

1. **Lowest dimensionality that solves the problem.** Escalation layers (corner phases, transition axes, direction splits, per-class grip curves) exist in the *schema* from day one but activate only when a question demands them.
2. **No baked-in normality.** Student-t / heavy-tailed forms wherever possible.
3. **Segment draws are correlated, not independent.** Correlation structure is measured, not assumed (compensation vs compounding between adjacent segments). Energy-carry is a physical mechanism for the coupling.
4. **No frame-kill condition.** Fingerprint non-replication is a *diagnostic* routing to more structural work (different observables/conditioning), never abandonment. The connective pipeline gets built regardless — the connections are durable assets preventing rediscovery.
5. **Critical eye on every feature.** Physics enters the predictor as a *family* of candidate features at multiple simplicity levels; training data grows until it can say which earn their keep. The NN leaning on physics features = evidence physics works (the tractable proxy for "simulation truth").

## Current candidates — consolidated into 5 clusters (cycle 1)

### A. Segment substrate (build-now foundation)
- Complete tiling: every meter belongs to exactly one typed segment — corner classes (k-severity ladder) + straights + braking zones — **nested inside FIA sectors** (no straddling). Sector-line placement accuracy is part of definition-of-done.
- **Time is the first-class ledger**; speed profiles kept as the diagnostic microscope; **per-segment energy tracked** (owner: energy management is a major modeled axis, esp. battery-heavy tracks under 2026 units; drivers carrying energy through corners).
- Schema carries dormant attributes: optional sub-phase marks (entry/apex/exit), adjacency (neighbor class, following-straight length, direction flip), turn direction.
- Circuit fingerprint = **true time-shares** per segment class via the simulated reference lap of a **field-reference car** (retires #625's distance-share caveat). Each car's own reference still baselines its own utilization.
- Asymmetric channel treatment: straights = car-rich (energy/drag) / driver-thin (slipstream confound, existing negative-control finding); braking zones = driver-rich (best-validated frontier).

### B. Fingerprint mechanism (the core)
- **Per-segment-class utilization** vs the anti-circular causal ceiling (extends #628's 4 regimes to the severity ladder; unify the two taxonomies).
- **The linear join IS the prior** (owner: "exactly the thing"): circuit time-shares × driver per-class utilization = expected weekend utilization. Escalation to sequence/bespoke formulations only if arithmetic under-explains.
- **Hierarchical shrinkage**: field mean → driver-overall → class cell, + class-across-drivers parent; Student-t cells so true outliers escape.
- Recency-weighted fingerprint fit (minimal drift handling; no trajectory modeling — league reality: rookies typically excluded, soft rule).
- Race side: **push + managed distributions per driver** (management split is "super required"); management-efficiency-as-axis = ambitious version; first build may flag/downweight managed laps.
- **Consistency (variance) as first-class channel** feeding race dispersion; race-condition controls are an information-filtering question.

### C. Weekend machinery
- **Two-speed practice update**: weekend loop updates weekend-local state ONLY; fingerprint cells move only in the slow offline loop from quali/race outcomes. FP evidence weighted by **fp_representativeness (F10 machinery)**. Prior-vs-FP disagreement widens σ honestly; persistent disagreement triggers the slow loop.
- **Canonical grip baseline, single owner**: intra-session evolution curve + **inter-session offsets** (how rubbered each session's start is vs the last — overnight/rain/support series). Owner: absolutely necessary; currently half-noted in multiple modules (the convention gap). Scalar first; per-class as escalation.

### D. Instrument panel (first build's exit gates — sizing, not go/no-go)
- **Variance decomposition** on segment times: car-reference / driver-utilization / residual shares (driver share = floor). THE "set the size" instrument; redirects effort, never stops.
- **Split-half replication** of fingerprint cells (odd/even rounds, per class): does the fingerprint exist as a durable trait? Doubles as σ-honesty check.
- **Composed-sector scorecard** vs official FIA sector times, every pipeline weekend: central values + distribution calibration coverage; breaks compensating-error degeneracy; the one external sub-lap anchor.

### E. Integration (sequenced)
1. **Feature family → fusion choir** (Phase-6 seam, (μ,σ) payload) with the critical-eye discipline — multiple simplicity levels from grip-corrected times up to full recomposition; NN reliance tells the story.
2. **Monte-Carlo-as-predictor = future architecture** (owner: "100% exactly what I was thinking") — physics-only sim races the field, scored on same metrics, never expected to win, always expected to explain. Blocked on feature reliability being proven through the NN lens first. Hard part deferred with it: two drivers reacting to each other.
3. **Decomposed input space for the neural modules = roadmap endpoint**, deliberately unscheduled. Owner endpoint vision: physics answers the simple questions; NN-on-physics creates complex interactions. Hybrid input space as safe variant.

## Verdicts

| Verdict | Scope (tested / NOT tested) | Source |
|---|---|---|
| All 22 shotgun ideas dispositioned with owner verdicts — per-idea detail in harness task list #1–#22 metadata | Owner design decisions; nothing empirically tested yet | cycle-1 q4 |
| Segmentation = custom physics-native segments nested in FIA sectors | Structure decided; segment *definitions* (unifying #625 classes / utilization regimes / ephemeris segments, the actual k, boundary placement) NOT designed | cycle-1 q1b |
| Circularity guard holds 4/5 views (one-sided frontier fits; coast feeds no utilization axis) | Fitting-code audit. NOT tested: numeric end-to-end behavior | x2 |
| Reference lap runs in production (#628 Path B, causal + strictly_pre); scalar lap time discarded (1-line recovery). Path A (weekend-local re-fit) untrustworthy per its own P1a findings | Code path + evidence docs. NOT: fresh execution | x2 |
| Circuit corner-class rollup validated (k=4, PASS 5/5, 22 circuits) but MEASURED-not-wired; distance-share lower bound | Inventory + importer grep. NOT: joins | x1 |
| Driver fingerprint raw material full-coverage (`apex_obs` 2019–2026 Q per-corner); no aggregation exists | Schema + live counts. NOT: signal quality | x3 |
| #628 utilization pipeline code-complete + gate-validated; `driver_utility*.db` never built at season scale (rerun, not engineering) | Code + disk inventory. NOT: what the season run shows | x3 |
| Ephemeris lineage (`src/physics/ideal_lap/`): per-corner-segment transit times + mgmt_discount fields = the unified-feature shape; 2023-Bahrain race-lap pilot only | Schema + 2,471 rows. NOT: generalization | x3 |
| **NO complete tiling exists** — FOUR taxonomies (incl. surprise `segment_classifier.py`: complete by construction, bridges to mixture classes via `soft_class_membership`, UNWIRED); disagreements structural (kinematic vs geometric vs pedal gates, 50× curvature-threshold spread, trail-braking the battleground); 10–16% boundary instability across drivers; FIA sector *locations* in no store (durations + telemetry ⇒ derivable) | Crosstabs on 4 circuits 2023 Q. NOT: SegmentClassifier live run, actual composed tiling | xP1 |
| **k=4 severity granularity adds NO noise** — within/between ratio flat vs macro regimes (1.93–2.40 vs 2.32–2.39), ~309 pts/class/driver-weekend (better-supported than macro fast_corner); most scatter is CLASS-INDEPENDENT weekend shift ⇒ a weekend-state term absorbs it | 4 rounds × 3 constructors 2023 Q, live #628 machinery, quantile-bin proxy. NOT: real GMM classes, boundary circuit-stability, n>4 weekends | xP2 |
| Thin **bin-specific** apex fingerprint survives teammate control (50–80m radius: v_apex r=0.46 AND a_lat r=0.59 independently); 3/5 bins collapse post-normalization; suggestive not confirmatory | 2023-Q apex_obs, teammate-subtraction, odd/even split. NOT: ceiling-norm, shrinkage, multiple-comparison correction; store radii cap ~200m | xP3 |
| Composed-sector validation NOT buildable from current ephemeris exports (corner-arcs-only ~35% of lap BY DESIGN); official sector times ARE on disk (`lap_times.sector1/2/3_time`); eph lap times match official exactly (2,471/2,471) | Bahrain 2023 R only. NOT: full-tiling composition (needs the tiling build) | xP4 |
| KE ledger works mechanically (7 straights auto-found consistently, net power 68–390 kW sane); NO deployment cliff — and xR6 explains why: 2026 MGU-K regulatory rampdown makes signatures curved ramps, not kinks. CdA estimates not yet plugged in (known headroom → propulsion/drag split) | Monza 2023 Q, 4 drivers, fixed mass. NOT: drag-model split, matched-speed DRS isolation | xP5+xR6 |
| **Prior-art bounds**: fingerprint×circuit interaction expected SMALL (golf analog: DataGolf ±0.07 strokes typical; independent 119k-round replication found ZERO OOS residual power → the gate that matters = held-out replication of the RESIDUAL after removing overall skill); driver importance IS circuit-conditional (wet + street circuits, externally replicated); constructor share 61–88% unconverged, NOBODY models lap time, no prior art at our granularity | Literature per R1–R3 files | xR1–xR3 |
| Brake/throttle **dynamics** (application shape) = most driver-identifying features in the literature, computable AT our 10 Hz (88.9%/30 drivers braking-impulse study ran at 10 Hz); "driver corners" real (per-corner discriminativeness 33–93%) ⇒ segment-level discriminativeness weighting is a design element; ABS-cycle detail (500–4000 Hz) out of reach | Road-car + sim-racing lit. NOT: F1-grid-size pools; DIMRA (pro race drivers) unread — paywalled, retry-worthy | xR4 |
| Track evolution: index to **cumulative car-laps** not wall clock (~1s/session, big circuit spread); saturating-exponential practitioner form; inter-session chaining has NO prior art anywhere — we build first, from our own cross-session ledger | Literature per R5 file (best source hobbyist GAM, 2021) | xR5 |
| Energy channel honest scope: **relative deployment vs driver's own rolling baseline + phase structure + gross derate flags**; NOT exact SOC/kW/override state. No validated trace→ERS inversion exists anywhere | Literature per R6 file; one synthetic-only preprint | xR6 |
| **VOCABULARY RULED (cycle 3)**: canonical gate = reference-lap kinematics (corner = ref lateral-accel over threshold; braking zone = field-envelope brake onset→corner entry, robust low quantile NOT mean — median-ribbon failure is the precedent; straight = rest); per-lap gates demoted to observation filters; map fixed per weekend, laps scored against it | Owner rulings; thresholds tuned later for cross-weekend map stability | cycle-3 q1 |
| **Maps: seed-then-supersede** — prior-year seed, chucked on contradiction; reprocess-over-change-detection; push laps only feed derivation; map version cited per observable row; NO cross-year corner-history (class-membership-only for the join; corner identity = arc-length within layout version, only for the dormant discriminativeness layer); FIA event docs = auxiliary seed | Owner rulings | cycle-3 q2 |
| **Severity ladder**: reuse mixture machinery — fit on reference-lap descriptors, per RULES-ERA (era pooling = cross-circuit class identity), Student-t components where feasible, memberships SOFT (fractional weights through the join), F12 stability gate = per-era acceptance | Owner rulings; quantile bins + hand edges rejected with reasons | cycle-3 q3 |
| **Sector nesting**: lines derived per weekend via time-to-distance interpolation (pooled median, sub-meter); nesting via SPLIT (sector lines = mandatory cut points, same-class pieces), never snap | Owner: revisit-if-painful | cycle-3 q4 |
| **Push/managed**: soft push-weight per race lap from context signals (clean air, tyre life, stint position, kinematic headroom); pedal-shape features = escalation. **PRE-QUALI CONSTRAINT: quali anchor is post-facto calibration ONLY; live classification = FP + sprint only (fp_representativeness's job)** | Owner ruling; P6 prototype in flight testing the first formula | cycle-3 q5 |
| **Grip module G**: one canonical module; saturating curve in cumulative car-laps; free per-session-start offsets (absorb overnight/support/temperature — support laps invisible by construction); rain = forced offset re-estimate, wide σ; field-pooled fit, Student-t residuals; validation = cross-session reconciliation before/after G | Owner: "dead on" | cycle-3 q6 |
| **Three-build sequencing, 2023-first**: B1 = quali-side end-to-end (vocabulary → G → season-scale class-utilization run + scalar reference recovery → fingerprint+join → instrument panel exit); B2 = race reference (push/managed, consistency, controls); B3 = live loop (two-speed update, live seeding, fusion feature family). Backfill after the panel proves the machine | Owner ruling | cycle-3 q7 |
| **P6 scoped null (well-shaped)**: context-signal weighted-average v1 does NOT separate push/managed (unimodal, 69% ambiguous middle, 5 races 2023 R). Clean-air carries nearly all signal; tyre freshness ~nothing; stint-position component WRONG-SIGNED (flip/drop); SC/VSC exclusion missing. Named variants queued; the kinematic-headroom leg (mgmt_discount-style realized-vs-capability) was UNTESTED — needs Build-1 tiling+ceiling | Kills this formula on these races, NOT soft classification; context-only was the testable subset today | cycle-3 xP6 |

## Open threads (post-cycle-2 — refined by the grounding wave)

1. **Segment vocabulary concrete design** — now a known DECISION LIST, not a mystery (xP1): rule once on the canonical gate (kinematic vs geometric vs pedal-probability; the 50× curvature-threshold spread); fix boundaries driver-invariantly (field-pooled/reference-lap derivation — 10–16% per-driver flip is disqualifying); rule on corner-start convention (turn-in vs braking-point — braking zones as own class resolves it); derive FIA sector locations (time-to-distance join, new but bounded); seed = `segment_classifier.py` (complete, mixture-bridged, unwired). Schema carries dormant attributes.
2. **Energy channel** — BOUNDED by xR6/xP5: coarse relative deployment vs own baseline + phase structure + derate flags, honest σ, never absolute SOC/kW. Next concrete step: plug fitted CdA/drag estimates into the KE ledger → propulsion/drag split. 2026 telemetry should show far stronger signatures (bigger electric fraction).
3. **Managed-vs-push identification mechanics** — unchanged; xR4 adds: throttle/brake application-shape features (computable at 10 Hz) are the literature's best driver-discriminators and plausibly also the best push-vs-managed discriminators.
4. **Grip baseline estimator design** — sharpened by xR5: cumulative-car-laps index, saturating-exponential start, zone-weighted deposition as escalation; inter-session chaining = greenfield (no prior art) built from our own cross-session ledger.
5. **Race reference consumption** — unchanged (how fingerprints + push/managed + consistency compose into correlated race-lap draws).
6. **Sizing-study execution shape** — xP2 de-risked granularity; still need: #628 season-scale run (the rerun), weekend-state term to absorb class-independent shifts (xP2's dominant scatter), residual-replication gate design per xR3 (z-score out overall skill FIRST).
7. **Segment-level discriminativeness weighting** — NEW from xR4+xP3: not all segments of a class carry driver signal ("driver corners", 50–80m bin); the fingerprint should learn/weight where signal lives.
8. **F10 full-run verdict** — still in flight; lands in the practice-update evidence-weighting slot.
9. **tc4 carry-over from epic 601** — `axis_name` threading; likely superseded by the new payload design (decide at spec time).
10. **DIMRA paper retry** — the one paywalled source ranking style metrics for professional race drivers (xR4); worth one attempt with better PDF/OCR tooling.

## Excursion briefs (cycle 2 — full grounding wave, all 11 dispatched at owner's call)

All research (R) briefs: primary sources required, cited findings, contradictions surfaced not smoothed. All prototype (P) briefs: throwaway scripts under `.agent-work/explore-ref-utilization/excursions/scratch/<id>/`, read-only on repo + DBs, pinned interpreter, report even if inconclusive. Every brief: **scoped nulls** — a null is the state of that specific question under those conditions, never a true null (owner-restated).

| ID | Type | The one named question | "Answered" looks like |
|---|---|---|---|
| R1 | research (web/academic) | How do existing lap-time simulators (QSS vs transient; open-source + academic) formulate the ideal-lap problem, and what fidelity suffices for *relative* comparisons? | Cited survey: model classes, what each fidelity term buys, known-essential terms for relative accuracy |
| R2 | research (web/academic) | What car/driver variance splits and methods has the F1 multilevel-modeling literature converged on? | Cited numbers (splits, CIs), method inventory, identification strategies (team switching) |
| R3 | research (web/analytics) | How does golf course-fit modeling (skill-category × venue-composition) handle thin cells/shrinkage/replication, and how big are venue-fit effects? | Cited methodology + effect magnitudes; transferable estimation patterns; baseball park factors secondary |
| R4 | research (web/academic) | Which telemetry observables has driver-identification/style research found discriminative? | Cited feature list ranked by discriminative power, racing + adjacent domains |
| R5 | research (web/academic+practice) | How do others model intra-session and inter-session grip evolution / FP-to-quali correction? | Cited model forms; how the inter-session chaining problem is handled |
| R6 | research (web/academic) | What is inferable about ERS deployment from speed/throttle traces alone, per the optimal-control literature? | Cited deployment-signature description; honest bound on inference without ERS channels |
| P1 | prototype (in-repo spike) | Does a coherent complete tiling (corner classes + braking zones + straights, sector-nested) fall out of existing artifacts on 2-3 circuits, and where do the three taxonomies disagree? | Candidate segment maps + taxonomy-disagreement report + sector-alignment feasibility note |
| P2 | prototype (in-repo spike) | What is per-class per-weekend σ when #628 deficits are re-bucketed by severity class on a handful of 2023 weekends? | σ table per class per weekend + signal-vs-noise verdict at k=4 (scoped) |
| P3 | prototype (in-repo spike) | Do per-driver radius-binned apex curves (2023 `apex_obs`) show split-half structure, raw and within-team-normalized? | Correlation table + honest read (scoped to raw 2023-Q apex speeds) |
| P4 | prototype (in-repo spike) | How big is boundary-placement error when Bahrain ephemeris segment times compose against official sector times? | Error magnitudes + whether official sector times are even stored/accessible in current stores |
| P5 | prototype (in-repo spike) | What does per-segment kinetic-energy bookkeeping from raw telemetry show on one power-sensitive circuit, without ERS channels? | Energy-ledger prototype output + visible deployment signature (or its absence, scoped) |

## Rejected / culled (with reasons — revivable)

- **Raw physics-axis injection as payload** — superseded by decomposition reframe (2026-07-24); entangles car/driver, needs static separation C3 says isn't there. Plumbing kept. Revive: only if decomposition frame dies class-wide.
- **Corner-phase fingerprint axes (entry/apex/exit)** — deferred by design (owner: huge utility, great deal more complexity, save for later). Schema carries sub-phase marks. Revive: after class-level fingerprint replicates.
- **Transition-level fingerprint axes** — schema-only now (adjacency stored). Revive: when class-level join under-explains.
- **L/R asymmetry as driver trait** — kept as stored direction attribute only; owner reframe: value is car behavior through direction transitions, not driver asymmetry.
- **Low-rank driver×class factorization** — deferred far (owner: "a little cute"; clusters would be machinery-driven). Revive: clean car-normalization + correlated residuals across drivers.
- **Teammate-relative anchoring in the fit** — owner deliberately avoids teammate comparison (rabbit hole). Becomes an end-stage diagnostic chased after the pipeline exists.
- **Fingerprint drift/trajectory modeling** — culled to recency weighting (owner: science-projecty; rookies excluded by soft rule — a rookie not finishing last is consistent enough that learning rate doesn't matter).
- **Agent-proposed decomposition-stability kill condition** — REJECTED by owner in favor of no-kill principle #4.

## Cycle log

| Cycle | Flavor | Explored | Consolidation |
|---|---|---|---|
| 1 | shotgun | 3 grounding excursions (circuit lineages / reference-lap+frontier audit / driver observables) + 22 ideas walked one-by-one with owner | 5 clusters + 5 standing principles + deferred set with revival conditions; 8 open threads seed cycle 2; owner decisions: two references, segment nesting, time+energy ledger, push/managed split, linear-join-as-prior, two-speed update, no-kill |
| 2 | refine (grounding wave) | ALL 11 excursions dispatched in parallel at owner's call: 6 prior-art research (R1–R6) + 5 in-repo prototypes (P1–P5); 11/11 returned, verified fresh | Prior art bounds the design (interaction small → residual-replication gate; driver importance circuit-conditional; sim at fidelity floor; evolution + ERS inversion = open fields we build first). Prototypes: no complete tiling (4 taxonomies, structural disagreements, SegmentClassifier = unwired seed); k=4 adds no noise (weekend shifts dominate scatter); thin bin-specific apex fingerprint survives teammate control; sector times on disk but composition needs full tiling; KE ledger works. Open threads refined to 10, incl. NEW segment-discriminativeness weighting |
| 3 | refine (rulings) | Segment vocabulary hardened (q1 canonical gate, q2 map lifecycle, q3 severity ladder, q4 sector nesting) + sticking points ruled (q5 push/managed incl. PRE-QUALI constraint, q6 grip module, q7 three-build sequencing). P6 prototype (push/managed classifier) dispatched mid-cycle | All seven questions ruled by owner; vocabulary fully decided; build order fixed (2023-first, three builds). P6 in flight — carried to consolidation. Remaining open: P6 result, F10 verdict, DIMRA retry, race-reference composition detail (deferred to Build-2 spec) |
