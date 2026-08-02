# R1 — Lap-time simulator prior art: QSS vs transient/optimal-control, and what fidelity relative comparisons need

**Question:** How do existing lap-time simulators formulate the ideal-lap problem, and what fidelity level suffices for RELATIVE car/driver comparisons (not absolute lap-time accuracy)?

**Method:** Web search + fetch (WebSearch/WebFetch), academic literature, open-source project docs, practitioner blogs/public team statements. No paywalled full texts were read beyond what the search snippets/abstracts exposed (see Nulls). One survey PDF (Massaro & Limebeer 2021) was located open-access but could not be text-extracted by the available tools (no PDF text layer parser in this environment) — its content below is from the abstract and citing sources only, not the full text.

---

## 1. The taxonomy: two independent axes

The field's own survey paper frames minimum-lap-time simulation as a 2×2 space, not a single spectrum:

> "The paper begins with a survey of advances in state-of-the-art minimum-time simulation for road vehicles... techniques covered include both quasi-steady-state and transient vehicle models, which are combined with trajectories that are either pre-assigned or free to be optimised."
— Massaro, M. & Limebeer, D.J.N., "Minimum-lap-time optimisation and simulation," *Vehicle System Dynamics*, 59(7), 1069–1113, 2021. DOI: 10.1080/00423114.2021.1910718. (Open-access copy: https://www.research.unipd.it/bitstream/11577/3389257/5/2021%20-%20Minimum-lap-time%20optimization%20and%20simulation%20PP.pdf — could not be text-extracted here; citation and framing corroborated via search-result abstract excerpts and citing papers.)

**Axis 1 — vehicle model dynamics:**
- **Quasi-steady-state (QSS):** at each point along the track, the car is assumed to be in local force/moment equilibrium; speed is bounded by a pre-computed g-g (or g-g-v) envelope, then integrated along the track. Fast, low-dimensional, widely used.
- **Transient / dynamic (optimal control):** full equations of motion (ODEs/DAEs) are solved as a minimum-time optimal-control problem (direct transcription + nonlinear programming is the dominant numerical method cited across sources), capturing actual transient states — yaw rate build-up, weight-transfer lag, tyre relaxation, etc.

**Axis 2 — trajectory:**
- **Pre-assigned trajectory:** the racing line is fixed in advance (centerline, or a previously-optimized line); only speed/throttle/brake are solved for.
- **Free trajectory:** the racing line itself is a decision variable, jointly optimized with speed and controls.

A third, hybrid class — **QSS models on a free trajectory** — is explicitly called out as a middle ground (fast like QSS, but not locked to a fixed line):
> "...a third approach solves the minimum-lap-time problem using quasi-steady-state models and free trajectory. The method builds upon g-g maps that can either be derived numerically or experimentally."
— search-result synthesis of Veneri, F. & Massaro, M., "A free-trajectory quasi-steady-state optimal-control method for minimum lap-time of race vehicles," *Vehicle System Dynamics*, 58(6), 933–954, 2020. https://www.researchgate.net/publication/332637470 ; ADS record: https://ui.adsabs.harvard.edu/abs/2020VSD....58..933V/abstract

This QSS-free-trajectory family was later extended to 3D tracks (banking/camber/gradient) — Lovato, Massaro & Limebeer, "A three-dimensional free-trajectory quasi-steady-state optimal-control method for minimum-lap-time of race vehicles," *Vehicle System Dynamics*, 60(5), 2021. https://www.researchgate.net/publication/348837786 — and a "curved-ribbon" road model extending it further to laterally-varying camber (Lovato, Massaro & Limebeer, cited via https://www.semanticscholar.org/paper/A-three-dimensional-free-trajectory-optimal-control-Lovato-Massaro).

**Computational cost trade-off** (stated directly in search-summarized abstracts, consistent across multiple sources):
> "A key advantage of the quasi-steady-state approach is its computational efficiency... shown to have a low computational expenditure when compared with the current transient optimal control method... allows parameter studies to be conducted within a reasonable time frame of a few minutes."
— synthesis drawn from Casanova/Brayshaw-Harrison-class QSS papers and Fraunhofer/e-mobility QSS papers surfaced by search (e.g. https://www.researchgate.net/publication/335493146_A_Quasi-Steady-State_Lap_Time_Simulation_for_Electrified_Race_Cars, Heilmeier et al. 2019).

> "Minimum-lap-time optimal control problems (MLT-OCPs) are a popular tool to assess the best lap time of a vehicle on a racetrack, however MLT-OCPs with high-fidelity dynamic vehicle models are computationally expensive, which limits them to offline use."
— search synthesis of arXiv literature on MLT-OCPs (context: https://arxiv.org/pdf/2111.04650, "Minimum-lap-time Control Strategies for All-wheel Drive Electric Race Cars via Convex Optimization").

---

## 2. Open-source / public lap-time simulators surveyed

| Project | Model class | Trajectory | Notes |
|---|---|---|---|
| **OpenLAP** (mc12027/OpenLAP-Lap-Time-Simulator, MATLAB) | Point-mass QSS, driven by OpenVEHICLE (inertia, torque curve, drivetrain, tyres, aero, steering) + OpenTRACK | Pre-assigned (fixed centerline/track file) | https://github.com/mc12027/OpenLAP-Lap-Time-Simulator |
| **OpenLapSim** (dstrassera) | Point-mass, open-source alternative | Pre-assigned | https://github.com/dstrassera/OpenLapSim |
| **TUMFTM laptime-simulation** (Python, spun out of `global_racetrajectory_optimization`) | QSS, cites Heilmeier et al. 2019 "A Quasi-Steady-State Lap Time Simulation for Electrified Race Cars" for the underlying vehicle model/validation | Used with a separately-optimized raceline (`opt_raceline` module minimizes summed curvature — i.e. trajectory optimization is a *separate* pre-step, not jointly solved) | https://github.com/TUMFTM/laptime-simulation |
| **OptimumLap** (OptimumG, commercial/free tier) | Point-mass QSS, explicitly "mathematically overly simplistic" per the vendor's own framing | Pre-assigned | https://optimumg.com/product/optimumlap/ |
| **Perantoni & Limebeer (Oxford)** F1 minimum-lap-time OCP | Transient, direct transcription + NLP, "variable parameters" (mass, aero, etc. as decision variables) | Free (jointly optimizes driven line + driver controls + car setup) | Perantoni, G. & Limebeer, D., *Vehicle System Dynamics*, 52(5), 653–678, 2014. DOI: 10.1080/00423114.2014.889315. Extended to 3D tracks in two follow-on papers, "Optimal Control of a Formula One Car on a Three-Dimensional Track" Parts 1 (track modeling/identification) & 2 (optimal control) — https://ora.ox.ac.uk/objects/uuid:3a7cfbe2-facf-479f-9208-089b1b22b2ae |

Note on the TUMFTM split: their pipeline treats **trajectory optimization and lap-time/speed simulation as separate stages** (curvature-minimizing raceline first, QSS speed profile second) rather than a single joint free-trajectory optimal-control problem — a materially cheaper, decoupled approximation to the "free trajectory" idea in Section 1, common in practice-oriented tools vs. academic OCP papers.

---

## 3. What each added physics term buys — and which are ESSENTIAL for relative vs absolute accuracy

This is the deliverable the question asked for. Evidence is drawn from multiple independent sources that largely agree, with one real point of tension noted at the end.

### 3a. Point-mass + g-g(-v) envelope + tyre load sensitivity — the load-bearing core, essential even for relative work
Every source that discusses what a QSS point-mass sim *must* have converges on: a friction/g-g envelope whose size depends on vertical tyre load (i.e., load-sensitive tyre model), combined longitudinal+lateral capability (friction ellipse, not independent limits), and aero downforce/drag as a function of speed (and, in richer versions, ride height).

> "For lap time simulation tools, a very simple tire model based mainly on tire load sensitivity is used: the most important aspect for the solver is indeed the friction coefficient of each tire for a given vertical load."
— search synthesis, context: Lovato/Massaro/Limebeer motorcycle g-g work, "The effect of load-dependent tyre friction and aerodynamic cross-flow forces on the g-g maps and minimum-lap-time of motorcycles," *Vehicle System Dynamics*, 63(10), 2024. https://www.tandfonline.com/doi/full/10.1080/00423114.2024.2388289

Practitioner corroboration (Duke FSAE, an entry-level QSS builder's own tool):
> the model "neglects load transfer, kinematics, and the tire sensitivity that accompanies these effects" when kept at its simplest — flagged by the author as a real limitation, not a non-issue.
— https://www.dukefsae.com/single-post/all-models-are-wrong-but

**Verdict:** load-sensitive friction + combined-slip envelope + speed-dependent aero is the floor. Below this, a sim can't even rank cars correctly because grip-vs-load curvature and aero-vs-speed scaling are exactly what differentiates cars of different concept (downforce level, mechanical grip). This matches your framing — capability envelopes (braking/lateral/traction/power-drag frontiers) *are* this floor.

### 3b. Weight transfer (static/quasi-static, i.e., load transfer as a function of instantaneous accel, not the transient dynamics of it) — essential; commonly bundled into "QSS," not an extra
Multiple sources are explicit that a *bare* point-mass-no-load-transfer model (like base OptimumLap) omits this, while calling it out as the main thing separating "toy" QSS from "real" QSS:

> OptimumLap explicitly excludes transient effects and weight transfer: "no weight transfer or transient effects are taken into account" despite using a point-mass formulation — yet "the simulated results still correlate well with logged data" for apex speed / end-of-straight speed / lap time, claimed accurate to "up to 10%."
— https://optimumg.com/product/optimumlap/

> A richer 4-wheel QSS model (DrRacing's build) *does* add "lateral load transfer between axles" and "brake balance and drivetrain torque distribution" on top of the load-sensitive-tyre + aero core, explicitly to get axle-level (not just total-car) grip right — necessary once you care about front/rear balance, not just overall pace.
— https://drracing.wordpress.com/2019/10/18/lap-time-simulation-the-matlab-awakens/

**Verdict — nuanced:** *total-car* relative pace ranking tolerates a pure point-mass with no axle split (this is what OptimumLap's 10%-and-still-correlates claim rests on). But if the comparison needs to attribute *why* one car is faster (front-limited vs rear-limited, braking-stable vs power-limited), quasi-static load transfer across axles becomes necessary — it's the difference between "car A is faster" and "car A is faster because of rear grip," which sounds close to what a module-level (braking/lateral/traction/power-drag) comparison needs.

### 3c. Full TRANSIENT dynamics (yaw inertia, weight-transfer lag, tyre relaxation length, suspension/chassis compliance) — buys ABSOLUTE accuracy at corner entry/exit, not obviously needed for relative ranking
This is the most direct answer to your question, and the sources are consistent:

> "The math [QSS] doesn't capture transient conditions of the lap during corner entry and exit, which are extremely critical to vehicle performance, but are also extremely complex to model."
— search synthesis of practitioner/LinkedIn sources (https://www.linkedin.com/pulse/steady-state-lap-time-simulator-luis-solis, https://www.linkedin.com/pulse/laptime-simulator-mass-point-quasi-steady-state-victor-cort%C3%A9s-abad) and academic framing.

The classic academic direct comparison of QSS vs transient is:
> Kelly, D.P. (PhD thesis, Cranfield University, 2008), "Lap Time Simulation with Transient Vehicle and Tyre Dynamics" — explicitly compares a transient time-optimal-control method against "a traditional quasi-steady-state manoeuvre time simulation method." Related: Kelly & Sharp, "Time-optimal control of the race car: influence of a thermodynamic tyre model," *Vehicle System Dynamics*, 2012.
— https://www.semanticscholar.org/paper/Lap-time-simulation-with-transient-vehicle-and-tyre-Kelly/c6fd2538d73107e98aa288060495c05d4c59fb12

I could not retrieve Kelly's actual delta numbers (thesis full text not accessible via search/fetch in this pass — see Nulls). But the framing across every source that discusses it is consistent: transient effects matter for *absolute* lap time and for *tyre thermal/wear* strategy work (see 3d), and the literature treats "does QSS get the relative ranking right" as a largely separate, less-contested question from "does QSS get the absolute lap time right."

Direct supporting quote (Duke FSAE, reasoning through exactly your relative-vs-absolute distinction):
> "we aren't too concerned about what the stopwatch says" [absolute] — the team deliberately chose QSS over higher fidelity because for **relative** performance-parameter comparisons, steady-state aero/powertrain/architecture sufficed, while acknowledging transient corner-entry/exit dynamics would matter for **absolute** lap time.
— https://www.dukefsae.com/single-post/all-models-are-wrong-but

**One caveat/tension worth flagging:** Massaro & Limebeer's own survey abstract lists yaw-inertia sensitivity as a first-class topic going back to Casanova, Sharp & Symonds, "Minimum time manoeuvring: The significance of yaw inertia," *Vehicle System Dynamics*, 34(2), 77–115, 2000 — i.e., a serious academic line of work exists specifically to show that yaw inertia (a transient-only quantity — meaningless in a point-mass model) *does* measurably affect minimum lap time, which is in tension with "transient effects don't matter for ranking." I did not resolve this tension (see Nulls) — it likely resolves as "yaw inertia changes absolute lap time non-trivially, but its effect scales similarly across broadly similar cars, so it may wash out of *relative* comparisons between cars of similar layout" — but that's my inference, not something a source stated directly.

### 3d. Tyre thermal/thermodynamic models — a distinct axis, mostly matters for strategy (wear/degradation), not raw single-lap pace ranking
> Tremlett et al.: "optimal tyre management in a Formula 1 vehicle and its trade-off with lap time, proving that relatively small changes in control strategy can lead to significant reductions in wear" — using "a minimum lap time optimal control calculation and a thermodynamic tyre wear model."
— https://www.researchgate.net/publication/343396773_Optimal_tyre_management_for_a_high-performance_race_car (see also Tremlett/Massaro-adjacent "Optimal tyre usage for a Formula One car," https://www.researchgate.net/publication/305885957)

**Verdict:** this is orthogonal to the QSS/transient axis discussed above — it's about multi-lap/stint-level state (temperature, wear) rather than single-lap ideal-pace comparison. Not obviously in scope for a "relative car/driver comparison" ideal-lap tool unless the comparison spans a stint.

### 3e. 3D track (banking, camber, gradient) — buys absolute accuracy and matters at specific circuit features, not universally
> Perantoni & Limebeer extended their F1 OCP to 3D tracks specifically because banking/gradient/camber change the normal-load and hence grip envelope at specific corners; Lovato/Massaro/Limebeer's "curved-ribbon" model further generalized this to *laterally varying* camber (track camber that changes across the track width, not just along it), stated to unlock "a more dynamic and realistic driving style... compared to the classic double-track model."
— https://www.semanticscholar.org/paper/A-three-dimensional-free-trajectory-optimal-control-Lovato-Massaro ; https://ora.ox.ac.uk/objects/uuid:3a7cfbe2-facf-479f-9208-089b1b22b2ae

**Verdict:** this is a track-specific fidelity term (matters a lot at e.g. banked ovals or cambered street circuits, negligible on a flat track) rather than a universal essential/non-essential call — no source treated it as required for *relative car* comparison specifically; it reads as required for *absolute accuracy at particular circuits* regardless of comparison purpose.

---

## 4. What real racing teams say publicly

F1 teams treat the "vehicle model" (their term, roughly synonymous with what you'd call the capability-envelope + fusion stack) as core IP, and are not specific about fidelity choices publicly, but two consistent public claims:

> "Formula 1 teams integrate high-fidelity vehicle dynamics models—covering chassis stiffness, suspension kinematics, tire deformation, and aerodynamic loads—to predict lap times and performance sensitivities... the vehicle dynamics group own one of the most jealously guarded pieces of intellectual property in a Formula 1 team: the vehicle model. The holy grail of the vehicle model is to produce an accurate value for the lap time gain (or penalty) associated with any given change... it has to be continuously updated and correlated with real data."
— The MIA (School of Race Engineering), "How do F1 teams use Vehicle Modeling?" https://www.schoolofraceengineering.co.uk/blog/post/14751/how-do-f1-teams-use-vehicle-modeling/

Notably this framing — "accurate value for the *lap time gain/penalty* associated with a change" — is a relative-delta framing, not an absolute-lap-time framing, even at F1 fidelity levels. That's a meaningful signal for your use case: the highest-fidelity real-world users of these tools are *themselves* optimizing for relative deltas, not absolute lap time, and still choose to invest in full multibody-level fidelity (chassis stiffness, suspension kinematics, tyre deformation). This is some evidence against "relative comparison ⇒ low fidelity suffices" being a universal rule — it may instead be "relative comparison changes what fidelity is *worth adding*, not that low fidelity is sufficient," which doesn't fully resolve into a clean verdict from the sources gathered here.

Third-party vendor framing (Canopy Simulations, sells laptime-sim tooling into multiple F1 teams):
> "team after team will re-invent the same laptime simulation technology, with varying degrees of success" — pitching a shared "car model, simulations and data analysis tools."
— https://simulation.michelin.com/canopy (Canopy was later acquired by/partnered with Michelin per this source)

---

## 5. Validation gaps — sim vs real lap-time deltas (published numbers found)

Numeric validation claims found are sparse and mostly vendor-stated rather than independently published:

- **OptimumLap (point-mass QSS, no weight transfer):** vendor claims "up to 10% accuracy compared to real data," validated qualitatively against apex speed, end-of-straight speed, energy consumption, and total lap time — but no independent dataset or error-distribution figures were surfaced. https://optimumg.com/product/optimumlap/
- No published head-to-head QSS-vs-transient-vs-real-telemetry lap-time delta table was found in this pass (see Nulls — this is a real gap, not just an unsearched corner; the closest candidate, Kelly's 2008 thesis, was located but its numeric results were not retrieved).
- Broader (non-motorsport) simulation-validation error rates surfaced by search (7% for cloud workload sim, ~1.7–9.3% MAPE for LiDAR sensor sim) are **not lap-time-simulation-specific** and are included here only as a sanity-check floor for what "well-validated simulation" error rates look like in adjacent engineering domains — treat as context, not as evidence about lap sims.

---

## 6. Synthesis — direct answer to the question as posed

1. **Formulation:** the dominant academic formulation is a 2×2 of {QSS, transient} × {pre-assigned, free trajectory}, with a fast-growing "QSS + free trajectory via g-g maps" hybrid family (Veneri/Massaro/Lovato/Limebeer, 2020–2021) as the practical sweet spot between OpenLAP-style cheap-but-fixed-line tools and Perantoni/Limebeer-style expensive-but-fully-optimized OCPs. Open-source/practitioner tools (OpenLAP, TUMFTM, OptimumLap) are essentially all QSS with a pre-assigned or separately-optimized line — nobody outside academia/F1-tier teams appears to run full free-trajectory transient OCPs routinely, because of cost.
2. **Fidelity floor that's essential even for relative-only comparisons:** load-sensitive tyre friction (g-g envelope shaped by vertical load), combined-slip (friction ellipse, not independent axes), and speed-dependent aero (downforce+drag) — this is the consistent floor across every QSS tool surveyed. Quasi-static (not transient) weight transfer across axles is needed as soon as the comparison must attribute *why* a car is faster (front/rear balance) rather than just rank overall pace.
3. **Fidelity that mainly buys absolute accuracy, with weaker/contested relevance to relative ranking:** full transient dynamics (yaw inertia buildup, weight-transfer lag, tyre relaxation, suspension/chassis compliance), tyre thermal/wear models (relevant to multi-lap strategy, not single-lap ranking), and 3D track geometry (relevant at specific circuit features, not universally). The strongest practitioner statement in your favor is Duke FSAE's explicit "we aren't concerned with what the stopwatch says" reasoning for staying QSS. The strongest complication is that F1 teams themselves — who are also fundamentally chasing *relative* lap-time deltas from setup/design changes, not absolute laps — still invest in near-full-vehicle fidelity, and that the yaw-inertia literature (Casanova/Sharp/Symonds 2000) was motivated specifically because a transient-only quantity was shown to move lap time non-trivially. Neither tension was resolved by a source found in this pass; flagging it rather than smoothing it over.

---

## Scoped nulls — what I did NOT survey

- **No full-text access** to any paywalled Vehicle System Dynamics / Tandfonline article (all returned HTTP 403). All claims from those papers are second-hand via search-engine-generated abstracts/summaries, not verbatim paper text, except where a quote is explicitly marked as a direct excerpt.
- **Massaro & Limebeer (2021) survey full text** was located open-access (unipd.it) but could not be parsed by the tools available in this environment (WebFetch's PDF summarizer returned only binary/structural metadata; the Read tool's PDF renderer requires poppler-utils, not installed here). Its content above is reconstructed from citing/summarizing search results only — treat Section 1's framing as reliable (multiply corroborated) but not as a full account of the survey's ~45 pages.
- **Kelly (2008) PhD thesis** — the one source that directly runs QSS vs transient head-to-head — was identified but its actual quantitative results (lap-time deltas, which corners diverge most) were not retrieved.
- **No FIA / official F1 simulation documentation** — F1 teams' vehicle models are proprietary; only third-party/blog characterizations were found, no primary-source team disclosure.
- **No motorcycle-specific fidelity requirements were explored in depth** despite several motorcycle g-g/lap-time papers surfacing (Lovato/Massaro/Limebeer 2024 on motorcycle g-g maps) — included only where directly relevant to the tyre-load/aero point.
- **No rally/oval/non-circuit-racing lap-time literature was searched** — scope was road-course circuit racing only, matching your context (F1-style).
- **Did not attempt to independently reproduce or numerically check** any of the accuracy/validation claims (e.g., OptimumLap's "10%") — reported as stated by the source, not verified.
- **Did not survey commercial closed-source team-grade tools** (ChassisSim, VI-CarRealTime, Adams, etc.) beyond what surfaced incidentally (Canopy Simulations) — a deliberate scope cut given time, not evidence they're unimportant.
