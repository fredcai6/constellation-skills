# Ideas Board — `explore-physics-evo-hookup`

The living record of shared understanding and the **source of truth** for this exploration. Every consolidation updates it. The spec crystallizes from it; a resumed session reads it instead of chat history; a mid-exploration shelve files *this file* as the shaped-design issue, loudly marked unconfirmed. Keep it current — it is what survives a reopen cascade.

## The point

**Confirmed (cycle-1 q1):** The fundamental point of the project is to **beat the humans at fantasy**. The current push is **physics as a feature engine** replacing raw times as evo inputs — the user is convinced of this push; it is not up for relitigation. The usability bar for physics-feeding-the-hookup is **low**. Physics-for-its-own-sake is real but tiered: (1) minimum = feature extraction for evo, (2) later = further improved predictions, (3) later = better storytelling. The exploration should **capture paths to best-possible physics** as documented options without chasing them all now.

Two model families exist and neither is yet delivering:

- **Physics** (src/physics + src/preprocessing + super-epic #509): five per-session force-channel views + cross-session pooling produce car-capability estimates that are "just shy of separability" — C3 (#512) verdict: regime-capability vector is circuit-conditional and fine-margin (frac_team ~0–4% vs frac_circuit 0.44–0.65; pooled static power best 1.16σ; constructors overlap within their own σ). Physically honest, predictively unproven.
- **Evo** (src/evo_predictor sampled runtime, 12 latent-power modules, BT field solve + precision-weighted fusion): the live predictor, but currently doing a little worse than human fantasy players who have obvious information gaps the model doesn't (or the model has gaps the humans don't — that asymmetry itself is unexplored).

The fundamental goal (fantasy push #601) is to hook physics into evo. The user wants **physics stability first** before the hookup. This exploration deep-dives the *gaps* — what exactly is missing/unstable on each side — and refines the plan from here to "happiness" (a hookup that measurably improves fantasy pts/race vs actual).

Kill condition: TBD via starting questions.

## The point — additional confirmed facts (cycle-1 q2/q3/q5)

- **Stability =** confidence the good-enough bar is reached and future work is *refinement, not interface rehash*. Structural items (e.g. #496 outer loop) get SETTLED — built or explicitly closed. Not separability.
- **Gap map (user):** driver/circuit affinity = huge; weekend news = big; current form = already handled well (recent-history modules are evo's most reliable part); FP features suck — they trail naive "just use FP3 order".
- **Design principle:** derive the "use FP3, mostly" weighting *from data natively* (e.g. precision weighting), never prescribe it — humans already play that strategy, copying it is a dead end.
- **No kill switch:** parity-with-FP3 still yields a certainty metric + storytelling = valuable. If physics features do worse than FP3 order, that means the seam was wrong — diagnostic, not kill.
- **Affinity must be physics-native (root cause):** classification-history affinity deliberately not built — it would be deleted the day physics affinity lands.

## Current candidates

### Cycle-1 shotgun (gap-closing paths; one-liners; wild sanctioned)

**A. Physics → good-enough-and-a-little-past (structural settles)**
1. **Settle #496 outer loop** — build the Matérn-feedback outer loop OR close it with a decision record "not needed for feature extraction."
2. **Contract freeze v1.0** — version the fit-store schema + pooled-estimate API; evo imports only through that seam; MODEL_VERSION churn stops being downstream-visible.
3. **Coverage sweep** — run the composed estimate pipeline (2023-Q-proven) across all seasons/sessions evo needs; coverage matrix with honest failure buckets.
4. **FP sessions through the estimator** (C4 #513) — FP runs are the actual pre-quali signal; measure fit degradation vs Q (traffic/fuel/engine modes).
5. **σ honesty pass** (#506) — inflate to cross-validated empirical σ so precision-weighted fusion isn't fooled by over-confident physics.
6. **Traction frontier follow-on** (#557) — fix or fence with widened σ.
7. **Physics-aware smoother full rebuild** — capture as the flagship "best possible physics" path; not chased now.

**B. The feature seam (physics → evo)**
8. **13th module** — per-(car,weekend) relative capability vector + σ as a new latent-power module through the existing PairBatch/BT/fusion seam; zero new fusion machinery.
9. **Physics as prior** — inject capability as a prior on existing modules' latent fields instead of a new module (alternative seam).
10. **Derive-FP3-natively** — physics σ per session type flows through precision weighting; the fusion *learns* "FP3 matters most" where true; evaluated on quali Brier.
11. **Regime × circuit-demand features** — not one scalar: the C3 regime vector (power/aero/traction/braking) crossed with per-circuit demand profile (corner fingerprints) → predicted circuit-conditional pace. Root-cause affinity for CARS.
12. **Quali-first eval harness** — quali Brier / rank corr as the gate any physics feature must pass before race prediction is touched.

**C. Driver affinity, physics-native (root cause)**
13. **Driver corner-type fingerprints** — telemetry-derived driver style vs corner classes (corner_fingerprints_* + driver_corner_reliability artifacts already exist) × circuit corner mix → driver×circuit affinity.
14. **Driver utilization vectors** — src/physics utilization (driver's use of car ceiling per regime) × circuit demand = affinity from measured driving, not results history.
15. **Wet/variable-condition driver axis** — weather × driver as a special affinity dimension.

**D. Weekend news (model literally can't see it today)**
16. **Minimal news ingestion** — penalties/grid-drops/substitutions as DB fields with as-of cutoff; manual entry per weekend is acceptable at personal scale.
17. **Weather forecast feature** — with explicit as-of contract.

**E. Race-distance corrections ("gut check over the race")**
18. **Race-pace physics** (C2 #511) — long-run FP stints → tyre-phase-corrected race-pace estimate; the long-run correction channel.
19. **DNF two-arm** (#389) — reliability/incident propensity; the humans' DNF intuition, modeled.

**F. Wild**
20. **Sim-driven storytelling** — pre-weekend ideal-lap sim per car per circuit → predicted pecking order + "X gains 0.3s in the S2 corners" narratives; doubles as a feature sanity check.
21. **Certainty dial → lineup risk** — physics σ directly modulates fantasy beam-search lane choice (mean/risk/balanced/max); the certainty metric becomes a decision input, not just a diagnostic.
22. *(added post-x3)* **2026 multi-state aero** (#499+#483) — single-theta_D physics cannot represent active-aero 2026 cars; must settle before physics features touch 2026 weekends, and 2026 IS the live prediction season.

## Excursions in flight (cycle 1)

| Id | Question (one) | Type | Brief |
|---|---|---|---|
| x1 | Which (season, session-type) cells can physics produce estimates for TODAY; what breaks outside 2023-Q? | research | **DONE** — see Verdicts; result at excursions/x1-coverage-RESULT.md |
| x2 | Where do FP features enter live evo, and what evidence shows them trailing "just use FP3"? | research | excursions/x2-evo-seam-brief.md |
| x3 | What physics debt is open, and per item does "settled" mean build or close? | research | **DONE** — see Verdicts; result at excursions/x3-debt-ledger-RESULT.md |
| x4 | Absolute vs relative-to-field normalization stability | research+compute | **DONE** — relative wins all 11 axes, ~3x faster resolution; excursions/x4-normalization-RESULT.md |
| x5 | Does the live preprocessor use SQ/S as quali evidence on sprint weekends? | research | **DONE** — USED (SQ→qs_*, S→lr_*); doc fear stale; excursions/x5-sq-evidence-RESULT.md |
| x6 | Are corner-fingerprint artifacts sufficient for a circuit regime-demand profile? | research | **DONE** — no (wear-pipeline artifacts); build path = segment_classifier per-circuit rollup; excursions/x6-circuit-demand-RESULT.md |

## Verdicts

| Verdict | Scope (tested / NOT tested) | Source |
|---|---|---|
| Shotgun idea A1 ("settle #496 outer loop") is ALREADY SETTLED: #496 closed 2026-06-25, superseded by decoupled-1D-longitudinal decision record (braking wired via #518 G3; throttle/coast HONEST-NULL, held, future paths parked in #553). The physics-blind-smoother interim is no longer interim. | Verified via gh issue view + decision record. NOT re-verified: end-to-end behavior of the wired braking channel. | cycle-1 / x3 |
| The physics debt ledger already exists: #609 (~26 items, current as of 2026-07-17). Only #589/#577 (backfill completeness) + #506 (honest σ floors) bear on evo feature extraction; the rest is best-possible-physics or hygiene. | Full 60-open-issue sweep + candidate verification. NOT swept: Thrust B #386-390 bodies, archived epic docs line-by-line, #443 end-to-end. | cycle-1 / x3 |
| The actual hookup blocker is not debt: #450 (Phase-3 compose) is open and UNBUILT — zero physics features exist in the live evo predictor today. | Issue state + CLAUDE.md live-path description. NOT tested: whether any prototype wiring exists on unmerged branches. | cycle-1 / x3 |
| 2026 hazard: single-theta_D aero cannot represent 2026 active-aero cars; #499+#483 must settle before physics features touch 2026 weekends — and 2026 is the live prediction season. | Issue bodies; NOT tested: magnitude of the mis-fit on actual 2026 sessions. | cycle-1 / x3 |
| Coverage is far better than memory: Q estimates exist 2019–2026 in all three stores (per-constructor five-view, per-driver fits, per-stint race); backfilled 2026-07-07. The "proven 2023-Q slice" framing is stale (validation scope, not store scope). | Store-row evidence via direct SQL; NOT a fresh execution of any pipeline. | cycle-1 / x1 |
| FP1–3 estimates are BLOCKED, not missing-data: telemetry exists for all FP sessions 2018–2026, but `estimate_session` applies `quali_mass()` unconditionally (session_estimator.py:125; no `fp_mass()` exists) — an FP run today would produce silently fuel-biased numbers. This is the concrete content of #513. | Code inspection + store/log absence; NOT tested: an actual FP run. | cycle-1 / x1 |
| SQ is a cheap probe: single-flying-lap format means the Q estimator + quali_mass assumption plausibly work unchanged; never invoked. Sprint-race stints separately blocked by a hardcoded `session_type='R'` SQL literal (race_stint_batch.py:156,185). | Read-only inspection; NOT tested: any SQ/S invocation. | cycle-1 / x1 |
| FP enters evo as PACE features (practice_preprocessor → qs_*/lr_*/short_run_*/long_run_* on DriverFeatures) into the 6 race_weekend modules; fp1/2/3_pos classification positions are dead weight (zero adapter reads). | Grep of all adapter feature-emission code; NOT examined: non-adapter consumers (reports/display). | cycle-1 / x2 |
| "Trails FP3" is real and measured — but MOSTLY FIXED: pre-#420 quali head 0.6149/0.5656-OOS vs FP3-only 0.7896 (~17–22pp worse, root cause representational per #451); post-#420 anchor blend (live in gold) 0.7765/0.7616 vs data-only ceilings 0.8061/0.7643. Remaining quali headroom vs the FP-data ceiling: **~3pp headline, ~0.3pp OOS**. | Documented measurements (§7.6.x + archived runs); NOT a fresh repro against live gold gold_cycle_260612_054059. | cycle-1 / x2 |
| STRATEGIC: physics moves QUALI prediction only by beating the FP-*data* ceiling (~0.80) — i.e. by being a cleaner pace read than classification-derived pace (fuel/traffic/run-purpose corrected). Otherwise physics value must land in affinity, race-distance, news, or the σ/decision layer. | Inference from x2's ceiling numbers; NOT tested: whether physics Q-fits actually exceed the ceiling. | cycle-1 / x2 |
| ~~The seam decision is largely pre-made: #601 Wave 8 plans DIRECT BT-field injection (skip neural module for v1)~~ **SUPERSEDED by user (cycle-2 frame):** direct injection = prototype only; end goal = neural module consuming physics features (replacing raw-timing features). #601's Wave-8 wording should be corrected during the 601 replay. | Issue body + registry/code inspection; user decision overrides the issue text. | cycle-1 / x2 → cycle-2 user |
| Normalization probe (x4): weekend-relative beats absolute on ALL 11 axes — noise 49–85% of absolute, ~3x fewer weekends to resolve a slow-moving component (0.3 field-σ step: ~4–18 weekends relative vs ~9–52 absolute). Weekend common-mode confounds (ρ/altitude/circuit) dominate noise under the CURRENT estimator. | Current five-view Q store 2019–2026, within-season only; NOT tested: a redesigned stage-1 model, cross-season continuity, jitter-vs-development separation. | cycle-2 / x4 |
| **USER AMENDMENT to x4's framing (cycle 3):** relative-FIRST accepted, but three corrections. (1) *Cake-and-eat-it:* solve relative, then re-anchor onto a best-estimate "field car" state so weekend-to-weekend absolute traction accrues too — two-stage decomposition, not either/or. (2) *Density is NOT noise* — it's modelable known physics (Mexico≠Monaco is known truth); take high-certainty observations when available (measured per-session pressure exists in src/utils/environment) and EXPLAIN it, don't subtract it. (3) *Track rubbering evolves WITHIN a weekend/session* — a weekend-constant median hides structured evolution; ignoring it = foot-gun. Taxonomy needed: modelable physics / structured evolution / residual common-mode / car signal. | User direction; NOT yet tested: any two-stage or evolution-aware variant. | cycle-3 / user |
| Basis map (x7): the five views are 2-param fits with WITHIN-view covariance only — no cross-view structure persisted anywhere. Mechanical grip measured 3× independently (friction-circle covariance never tested); CdA solved twice + point-pinned with one-directional Jacobian propagation; θ_R deliberately walled off (documented); **a_long is literally two different numbers** (Braking = decoupled Kalman-RTS; Traction/PowerDrag/Coast = older cleaner, held back by honest-null #523/#546); Braking/Traction/Lateral share trajectory noise their bootstraps pretend is independent. Existing unification seams: decoupled-1D [E_total,F_vehicle] state, Plan-7 outer loop, cda_frontier_jacobian. This is the concrete content of "the spike needs pulling together." | Code-truth map 2026-07-17; recoverability stated per item; NOT a design proposal. | cycle-3 / x7 |
| **USER AMENDMENT to x6's framing (cycle 3):** "fingerprints can't be crossed" is the wrong takeaway — the CIRCUIT fingerprint (corners + straights + their ordering/interaction — the whole point of a circuit) should be the most telling circuit descriptor. Do fingerprinting BETTER (add straight fingerprinting + sequence), and the per-circuit regime-share profile falls out naturally (traction-limited share etc. automatic). Likely implication: the capability vector's own shape changes to match. Not a spec decision yet — thematic bearings. | User direction; supersedes the "segment-classifier rollup vs fingerprint join" framing as an either/or. | cycle-3 / user |
| Circuit-demand audit (x6): existing fingerprint artifacts are wear-pipeline diagnostics, NOT a demand profile — usable starting material (shed/gain/headroom per corner) but the real deliverable (per-circuit regime TIME-share rollup) is unbuilt everywhere. Best building block: segment_classifier.py already tags every telemetry sample straight_brake/straight_throttle/coast/corner — it's just never aggregated per circuit. Traps: fingerprint `label` is a wear-sensor tag, not a regime tag; coast_frac is driver racecraft, not circuit geometry; corner_matches cross-year map is 9-gp partial. grip_bin_obs (damage_integrals.db) is the better lateral-axis foundation. | Read-only audit of artifacts + producing code; NOT prototyped: the actual join. | cycle-2 / x6 |
| SQ evidence (x5): USED — the doc's "feeds only FP1 on sprint weekends" fear is stale. FP1+SQ laps → qs_* quali-sim bucket (live quali module + anchor); S laps → lr_* long-run only. Optional upgrade: exploit S→Q (0.730) as its own quali feature (seam: DRIVER_QUALI_POWER_FEATURE_NAMES, S–M, small-n caveat). sq_pos/s_pos positions likely dead weight like fp*_pos. | Code-truth on current main + 2025-China data check; NOT dated via git history; NOT checked: historical gold bundles, exhaustive recent_history-module sweep for sq_pos. | cycle-2 / x5 |
| Cheap wins spotted, physics-independent: (a) representational retrain — allfp_best_raw as a genuine trained input was VALIDATED (#451: OOS 0.5868→0.7700) but never productionized (only the post-hoc α=0.5 anchor is live; #425/#375 = principled path); (b) sprint-weekend SQ evidence possibly under-used ("single highest-value fix" per quali_evidence_findings.md §B — unverified against current preprocessor). | Doc + code grep; NOT verified: current practice_preprocessor sprint-weekend behavior. | cycle-1 / x2 |

## Thematic bearings (settled cycle 3 — the stage-1 design frame)

1. **Four-layer weekend-state model:** explained physics (density from measured pressure, mass/fuel) → structured evolution (smooth within-session grip latent) → field-car common-mode state (re-anchors relative deltas; accumulates the absolute story) → car signal (deltas). Every term observation-backed; honest σ per layer; x4's relative-only result is the floor to beat.
2. **One unified physical basis** solved across the entire lap; the circuit fingerprint (corners + straights + ordering) is an **observability router** (which segments carry evidence for which parameters), never a partition into a car×zone matrix. Multi-view redundancy (grip triplet, dual CdA, a_long) must *reduce* uncertainty — x7's map lists exactly where that's currently dropped.
3. **Driver utility on the same basis** (starting point): per-unit-class access of the car envelope, race-history prior, weekend update. Mindful nuances: utility expresses per-axis differently (≈zero on power-to-weight; style dims like throttle-application timing possible; corners dominate), delta-basis evolution stays open.

## Cycle-4 decisions (the five spec-level opens, pinned)

1. **Segmentation vocabulary:** property-based classes over a continuous descriptor substrate; **soft/fractional membership** (a corner is a mixture over property classes — reusable correlation structure); class count support-driven; per-corner identity deferred to a finer view later. Prework: decompose turns into property mixtures.
2. **FP mechanics:** per-lap latents (fuel mass, engine mode, run purpose) + directly observed compound; grip-class apex speeds = mass-robust anchor; straight/traction classes carry the confounded P/m + drag (sandbagging → wider σ, never bias); continuous representativeness weights, nothing binary-dropped. **Weekend car-state chain:** FP1→FP2→FP3→[parc fermé]→Q with process noise (teams tweak/learn); per-team parc-fermé reaction step is learnable (and a storytelling asset). Run-order honesty: post-FP1 huge σ expected and fine.
3. **Stage-1 product contract:** four record types — weekend-state / car-basis posterior (FULL covariance, session-chained) / lap evidence / **as-of-stamped feature view** (the only evo-facing surface). MODEL_VERSION keyed, append-only. Constructor grain = accepted round-1 trade (per-entry divergence banked).
4. **A/B harness:** live gold vs +physics fusion step behind one manifest toggle (anchor pattern); quali task only; 2022–2025 scored walkforward (2019–2021 appendix); gates G0 correlation-with-evo-errors → G1 quali sign-acc+Brier vs baseline and ~0.80 ceiling → G2 fantasy pts/race; three as-of cutoffs (post-FP1/FP2/FP3) make the honesty curve measurable; dry scored, wet flagged; all gates reportable-either-way.
5. **2026 posture:** latent-mode **two-state Z/X joint fit** (shares P_max; generalizes the DRS closed/open machinery) with allowance-zone priors — outside zones Z-certain, mid-straight in-zone X-likely, transition ramps carry targeted σ. Deps already DELIVERED: active_aero_zones.py (allowance layer), active_aero_identification.py (CdA evidence scorer), PR #622 (RegulationEra 2026 fix + aero_axis_2026). Regs verified: two modes only, Z default, no held neutral; Overtake/Boost = PU. #499 (AeroDragSet — should take soft per-sample config probabilities) + #483 = structural exit; status comments posted on both issues 2026-07-17.

## Open threads (post-cycle-2)

1. **Stage-1 model interface** — the load-bearing design: what exactly the coarse math model estimates per lap/session, its honest-σ contract, how FP representativeness weights enter, how the feedback loop attaches later. Design-it-twice at spec time.
2. **FP representativeness mechanics** — how compound + fuel-state get inferred per lap (the mass problem), and how sandbag robustness (power-to-weight via grip/exit-speed) is expressed in the model.
3. **Circuit-demand rollup shape** — segment_classifier per-circuit time-share aggregation: grain (per year? per session?), straights handling, lateral axis via grip_bin_obs.
4. **Prototype injection details** — as-of join semantics, A/B harness vs current gold, gate thresholds (correlation screen → quali sign-acc vs ~0.80 ceiling → fantasy pts/race).
5. **2026 minimum honest handling** — inflated-σ posture concretely (how much, where recorded); #499/#483 deferred.
6. **Backlog (small, physics-independent):** S→Q as explicit quali feature (S–M, small-n); rip out dead fp*_pos/sq_pos/s_pos plumbing; representational retrain #425/#375 (interacts with round-2 NN work).

*(resolved cycle-1: stability definition → q2; gap map → q3; #511 closed, #513 IS on the critical path → x1/x3)*
*(resolved cycle-2: ordering → q1 (hardest-problem-first, #513 = first consumer of stage-1); round-1 scope → q2 (believable honest features; NN + driver-utility consumption = round 2; ignore calendar); v1 feature vector → q3 (five axes + composite-only injection); normalization → x4 (weekend-relative canonical); SQ under-use → x5 (stale fear, already used); affinity raw material → x6 (build segment-classifier rollup, not fingerprint join))*

- **Can physics Q-fits beat the ~0.80 FP-data ceiling on quali sign-accuracy?** The Wave 7A correlation screen in #601 is the planned first read; nobody has run it yet.
- **FP fit design (#513):** what does honest FP fitting need beyond `fp_mass()` — run-purpose classification (quali-sim vs race-sim), thin-fit floors (#560), traffic rejection? This is the load-bearing physics build for the "nail quali" strategy.
- **2026 multi-state aero (#499+#483):** how wrong are single-theta_D fits on 2026 active-aero sessions actually? (Magnitude unknown; 2026 is the live season.)
- **σ honesty (#506):** settle or accept-with-decision-record before physics σ drives fusion precision weights.
- **Backfill verify (#589/#577):** cheap; confirms the 2019–2026 store coverage x1 observed is trustworthy.
- **Driver affinity, physics-native:** which raw material (corner fingerprints, utilization vectors) actually predicts driver×circuit deltas? Unexplored beyond artifact existence.
- **Sprint-weekend SQ evidence under-use** in the practice preprocessor — verify and possibly fix (physics-independent cheap win).
- **Representational retrain** (#425/#375 path) — physics-independent; interacts with the hookup (a healthier trained head changes what physics must add).
- Weekend news + weather ingestion: deliberately unexplored this cycle (D-cluster); revisit after the physics-seam picture settles.

## Banked one-off thoughts (future uncertainty-closers — capture, don't chase)

- **Per-entry spec divergence:** account for weekends where the two cars are known to differ (upgrade on one car only); constructor-pooling is a round-1 approximation with a named blind spot.
- **Cross-weekend cross-driver info pulls:** staggered upgrades (driver A this weekend, driver B next) let one car's data inform the other's future state.
- **Delta basis for driver access:** driver utility as its own basis the driver actually accesses, if same-basis utilization proves too coarse.
- **Style dimensions of utility:** e.g. throttle-application timing — utility axes beyond envelope access; power-to-weight itself has ≈no utility component.
- **Parc-fermé reaction quality as a team trait:** per-team FP3→Q step distribution (already in the weekend chain design; also a storytelling asset).
- **Per-corner identity view:** finer storytelling layer over the property-class substrate ("always weak in T13") — round-2+; substrate already supports it.
- **S→Q as explicit quali feature** (x5; S–M, small-n caveat) and dead fp*_pos/sq_pos/s_pos plumbing removal.
- **Representational retrain** (#425/#375) — interacts with round-2 NN-on-physics-features work.
- **Wet axis manual handling:** inflate σ + slight nod to known wet specialists until modeled properly.

## Rejected ideas (with reasons)

- **Physics as a prior on existing modules (B9)** — rejected cycle-2 frame: user treats physics as a *feature*, not a prior. Revive only if the feature path hits a wall the prior path wouldn't.
- **Classification-history driver affinity** — rejected cycle-1 q5: would be deleted the day physics affinity lands; user drives at root cause.
- **Prescribed FP3 weighting** — rejected cycle-1 q3: humans already play it; must be derived (lap-level representativeness), not hand-coded.
- **Direct BT-field injection as the END STATE** — demoted cycle-2 frame to prototype status; end goal is the neural module on physics features.
- **Parked (not rejected — explicitly next-step):** wet-conditions axis (manual uncertainty handling meanwhile), weekend news + weather (post-prediction adjustment layer), DNF two-arm #389, contract freeze (end-state of this effort), storytelling + certainty-dial (later tiers).

## User reaction pass (cycle-2 frame, 2026-07-17 audio) — decisions and corrections

**Scope bounds (user):** this exploration = effectively a **#601 replay/refresh**. Order: **nail quali first** (FP3-ish evidence, predictable, quali already a huge race predictor), race correlation = next level. **Dry conditions first.** 2026 active aero = best-effort, no Belgium promise; original target stands: **round 1 done by summer break** (the Belgium push was a stretch goal). **Contract freeze = the end-state of this effort**, not a task now.

**Item-by-item decisions:**
- **Staged-model vision (reframes A1+A5+A7):** current five-view estimator = "beginnings of an exploration spike"; needs consolidation, revisiting original intent. Vision: **math model → physics model refresh → more precise physics refresh** — coarse model creates *traction points* (coherent data + honest uncertainties), each stage replaces the uncertainty beneath it. Raw measurements → high-precision physics in one jump = too much. User DOES want the Matérn/feedback loop concept in this consolidated architecture. σ honesty (#506) is part of this concept, and big.
- **A4/#513 FP fits = single biggest concern.** Estimator is Q-only *because mass is hard*. FP confounding is fundamental (sandbagging, detuned engines). Attack: extract power-to-weight via other parameters (grip from exit speeds — energy transfer). Key decomposition: **FP is a weak demonstrator of car performance but a strong demonstrator of DRIVER UTILITY for that track/weekend**; car performance = pooled over the season, FP provides *hints that push the pooling*.
- **B8 seam (CORRECTED — supersedes the "seam pre-made" verdict):** user did NOT agree to "skip the neural module for v1" as an end-state; #601 Wave-8 text overstates. Direct BT-field injection = acceptable **prototype** (avoids training cost while testing signal). **End goal = neural module consuming physics features**: physics answers "what information can we glean," the NN answers "given these features, what does driver A beating driver B look like." Two different problems.
- **B8 core intent:** REPLACE raw-timing features with physics features. Raw timing is not a telling feature; current corrections are questionable; move away entirely — get to the root.
- **B9 physics-as-prior: REJECTED.** Physics is a feature, not a prior.
- **B10 clarified:** not session-weighting — **lap-level representativeness**. Ideal: know each lap's compound + fuel/mass state → "this car ran softs, low mass → most quali-representative." Evidence assembly naturally leans on the most representative laps; if a team quali-sims in FP2, we catch it. Derived, never prescribed.
- **B11 ≈ C13: SAME idea.** Corner fingerprints = the artifact driving affinity. Split **car affinity** (regime × circuit demand) from **driver affinity** (utilization).
- **B12 eval harness: already structurally exists** — the evo pipeline (performance → expected quali order; quali+performance → overtake likelihoods) IS the harness; use it, it works even with poor features.
- **C14 driver utilization:** what we hope to pull from FPs generally. Structure: race HISTORY = prior for how well a driver uses his car; race WEEKEND builds on that prior.
- **C15 wet axis: PARKED** — manual handling near-term (inflate uncertainty, slight nod to known wet specialists). Wild card; dry first.
- **D16/17 news+weather: PARKED (next-step, post-prediction layer)** — predict quali order, THEN apply penalties; separate from the physics-feature effort.
- **E18 race-pace physics:** real concern, but sequenced after quali per the order above.
- **E19 DNF: PARKED** — issue exists (#389), not tracked now.
- **Sprint/SQ evidence under-use:** "that's dumb if it's not used" — emblematic of the real disease: **separate tentacles dropping information**. Fold into the consolidation intent.
- **User philosophy (standing):** agents are chronically pessimistic about what data can do. Chase every avenue optimistically and aggressively; repeated experience = things work once the problem is reframed. (Also: be careful citing stale memory as ground truth — this cycle proved it twice.)
- **The bar accepted:** physics only improves quali if it beats classification-pace information — obviously true, not easy, not broken. The way past it = affinity + cleaner information, which is exactly the point of the push.

## Candidate standings after cycle 1 (consolidation)

- **Already settled/done (culled as work, kept as facts):** A1 (#496 closed+decision-recorded); A3 coverage sweep (Q+R 2019–2026 already backfilled; remains only #589/#577 verify); B12 eval harness (diagnose_quali_* + sign-accuracy metric already exist); B8-vs-B9 seam choice (superseded — #601 Wave 8 already picks direct field injection v1).
- **Load-bearing spine (promoted):** A4/#513 FP fits (with fp_mass + run-purpose handling) → B10 derive-FP3-natively via honest σ (#506) → #450/Wave-8 direct-field injection → judged first by Wave 7A correlation screen / quali sign-accuracy vs the 0.80 ceiling, ultimately by fantasy pts/race.
- **Promoted hazard:** F22 2026 multi-state aero (#499+#483) — gates physics on the live season.
- **Affinity cluster (C13/14/15):** untouched by excursions; the biggest *unexplored* value pocket per the user's gap map.
- **Deferred, on the board:** A2 contract freeze (cheap, do near hookup), A6/#557 (design note), A7 smoother rebuild (best-possible tier), D16/17 news+weather, E18 race-pace (note: race stint estimates ALREADY exist 2019–2026 per x1 — E18 may be closer than assumed), E19 DNF, F20 storytelling, F21 certainty dial.
- **New cheap wins (physics-independent):** representational retrain (#425/#375), sprint-weekend SQ evidence fix (verify first).

## Cycle log

| Cycle | Flavor | Explored | Consolidation |
|---|---|---|---|
| 1 | shotgun | Starting questions (itch/stability/gap-map/kill) + 22-idea shotgun + 3 grounding excursions (x1 coverage, x2 evo seam+baseline, x3 debt ledger) | Point confirmed (beat humans; physics-as-feature-engine; low bar; no kill switch). Physics nearer ready than believed (#496 settled, Q+R stores full 2019–2026); real gaps = #513 FP fits, #506 σ, #450 compose, 2026 aero; quali headroom vs FP-data ceiling only ~0.3pp OOS → physics must beat the data ceiling or deliver via affinity/race/σ layers. Affinity cluster = biggest unexplored pocket. Awaiting human steer for cycle 2. |
| 2 | refine | User reaction pass (staged-model vision; physics-as-feature; NN end-state; parked news/weather/wet/DNF) + q1 ordering, q2 round-1 scope, q3 feature vector + 3 excursions (x4 normalization, x5 SQ evidence, x6 circuit-demand) | Plan honed: hardest-problem-first (stage-1 designed for Q+FP, #513 first consumer); round 1 = believable honest features + direct-BT prototype, NN + driver-utility consumption = round 2; ignore calendar. Empirics: weekend-relative normalization canonical (3x faster resolution, all 11 axes); SQ already used (stale fear); circuit demand = build segment-classifier rollup (fingerprint artifacts are wear diagnostics). Remaining opens are spec-level design questions. |
| 3 | refine | User amendments (noise taxonomy, cake-and-eat-it, fingerprint reframe) + q1 four-layer state model, q2 unified basis + observability router, q3 driver utility placement + x7 basis map | Thematic bearings SET: stage-1 = four-layer weekend-state model (explained physics / structured evolution / field-car / car deltas); one physical basis across the lap, fingerprint routes observability, multi-view redundancy REDUCES uncertainty (x7 = the concrete pull-together list: grip triplet, a_long split, CdA joint, shared-trajectory noise, cross-view covariance); driver utility same-basis start (per-axis expression nuance, delta-basis evolution open). Remaining opens = spec-level design. |
| 4 | refine | The five spec-level opens, one at a time, widest first (segmentation → FP mechanics → contract → A/B → 2026); no excursions needed except reg-fact verification + delivered-work discovery | ALL FIVE PINNED (see Cycle-4 decisions). Bonus discoveries: weekend car-state chain w/ parc-fermé team step (new model element); 2026 aero deps already delivered (zones layer, evidence scorer, RegulationEra fix — stale STATE_NOTE); #499/#483 status comments posted. Banked one-offs list started. Exploration queue empty. |
