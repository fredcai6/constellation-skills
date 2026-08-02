# Critic: Testability / Falsifiability — DESIGN_SPEC.md (physics-evo hookup, round 1)

Lens owner: testability/falsifiability. Read spec only (plus targeted repo code to ground findings, per instructions — no exploration record consulted). Findings below, most severe first.

---

## 1. [CRITICAL] Phase 3b's "self-consistency" gate is very likely circular, not a validation

**Finding:** Phase 3b's gate is "utility × capability recomposes observed lap time within σ" — and this is explicitly the *only* gate ("no ground-truth gate" is stated outright). But look at how utility would have to be constructed: capability is a car-level ceiling (confirmed in `src/physics/utilization/car_prior.py`, which builds a per-constructor `CapabilityEnvelope` with no driver dimension at all). Driver utility, per the spec's own description ("per-unit-class access of the car envelope"), can only be estimated by comparing the driver's observed performance against that car ceiling — i.e. utility is defined as (something like) observed / capability. If that's the construction, then "utility × capability recomposes observed lap time" is true by algebraic necessity, not because the decomposition is meaningful. A utility model that's pure noise, or one that's badly wrong in its *class-conditional structure* (the actual claim being made — "corners dominate, power-to-weight ≈ zero"), would pass this gate exactly as well as a correct one, because the gate only checks that the multiplication undoes the division that produced it. This isn't a weak-but-honest gate; it's a gate that cannot discriminate correct from incorrect at all.

**Fix:** State explicitly how utility is fit (what's held out of the fitting objective) so the recomposition check isn't tautological — e.g., fit utility on a subset of laps/sessions and check recomposition on a held-out subset, or check that the *per-axis structure* (corners dominate, power-to-weight ≈ 0) replicates out-of-sample rather than just checking the scalar product. Absent that, rename the gate for what it is ("construction sanity check") and don't let it stand in as *the* Phase 3b gate.

---

## 2. [CRITICAL] Phase 3's "numbered deferral" makes the phase unfailable

**Finding:** The gate is stated twice, consistently: "each fracture closes with a number or a numbered deferral... an undecided fracture is a phase failure" (Testing pathways) and "Close each x7 fracture with a quantified disposition (fix or honestly-numbered deferral)" (Phase 3 body). Read literally, the only failure mode is leaving a fracture *undecided* — but writing "deferred to round 2, estimated residual bias ~X%" for all five fractures (grip triplet cross-coupling, dual-CdA reconciliation, `a_long` reconciliation, shared-trajectory-noise propagation, cross-view covariance) satisfies the letter of the gate while fixing zero of them. There is no stated minimum number of fractures that must actually be *closed* (vs. deferred), and no criterion for when a deferral is "honest" versus rubber-stamped. This converts what reads as a hard integration gate into a paperwork requirement — Phase 3 can complete with the exact same basis fragmentation it started with, as long as every fragment has a number attached to its own persistence.

**Fix:** Require a minimum count or a named subset that must close as fixes (not deferrals) — e.g., cross-view covariance persistence (the thing Phase 5's as-of feature view and G0's honesty curve actually depend on numerically) should be non-deferrable, since deferring it undermines every downstream σ claim. State a ceiling on total deferred fracture count, or require that deferrals carry a quantified downstream-impact bound, not just a label.

---

## 3. [CRITICAL] Phase 2's "must beat x4's floor" has no defined statistic, threshold, or evaluation split

**Finding:** The gate reads: "re-run x4's exact methodology on this model's output; must beat the relative floor, not just absolute." X4 established weekend-relative normalization wins on "all 11 axes" using a speed-of-convergence metric ("~3× faster to resolve a slow-moving component"). But Phase 2's four-layer model is strictly more expressive than the thing x4 tested (it adds a within-session evolution latent, a re-anchored field-car layer, and explicit density/mass explanation) — a strictly more expressive model will essentially always look better *in-sample* on almost any reasonable metric, especially one about convergence speed, simply by having more free parameters to absorb variance. The spec doesn't say: (a) which of the 11 axes must improve, or whether it's a majority/all/weighted-average; (b) whether "beat" is evaluated in-sample or on a train/test split; (c) what margin counts as "beating" versus noise. As written this gate can pass trivially — a model with more knobs fit on the same data it's evaluated against will almost certainly outperform a simpler baseline by *some* margin on *some* subset of 11 axes.

**Fix:** Pin the exact statistic (e.g., median convergence-speed ratio across axes), require improvement on a stated majority (e.g., ≥7/11) or a pre-registered subset, and require held-out evaluation (a weekend range not used to fit the four-layer model's hyperparameters) before claiming "beats the floor."

---

## 4. [MAJOR] Phase 4's "derive FP3-is-most-representative from data" is structurally biased toward confirming itself

**Finding:** The gate requires the representativeness weighting to "derive... from data on held-out weekends, never hand-code it." But if that weighting is fit by minimizing prediction error against the Q outcome (the natural way to fit it, and the only ground truth mentioned anywhere for FP sessions), then FP3 will tend to win almost by construction: it is closest in time to Q, and track/car state evolves quasi-monotonically across a weekend (rubbering in, setup convergence toward the parc-fermé baseline). A model that just learns "weight sessions by inverse temporal distance to Q" would "derive" the FP3-is-most-representative finding without encoding any actual representativeness signal — it would be re-discovering the calendar, not the physics. The spec doesn't propose a control (e.g., comparing against a temporal-distance-only baseline weighting) that would let this finding be genuinely surprising, i.e. falsifiable, versus a foregone conclusion of the fitting setup.

**Fix:** Add a named baseline — "weighting derived purely from |clock_session − clock_Q|" — and require the learned weighting to beat *that* baseline (not just beat "no weighting" or "FP1 unweighted"), so the gate can actually distinguish "learned something about representativeness" from "learned the calendar."

---

## 5. [MAJOR] No kill condition exists anywhere in the eight-phase program

**Finding:** Every gate in the spec is explicitly non-terminal: "Reportable either way (no kill switch)" (Phase 0), "reportable either way" (G0/G1/G2), and the master rule "a stall sends the finding back to the implicated upstream phase, not a restart" (Phase 7). Taken together, there is no predefined condition anywhere in this eight-phase, multi-round program under which the physics-features approach itself is abandoned or descoped. If G1 shows physics loses to the ~0.80 FP-data ceiling, the spec's own protocol is to route the finding to "the implicated upstream phase" — which could be any of Phases 1–6 — and iterate again. Nothing bounds how many iterations of that loop are allowed before the round-1 goal ("prove whether [physics] helps... reportable either way") is itself honored by actually stopping. A program whose only response to negative evidence is "go fix upstream" cannot, in practice, ever conclude "physics doesn't help here" — it can only conclude "we haven't found the right upstream fix yet."

**Fix:** Define an explicit stop-loss: e.g., a maximum number of Phase-7 stall/upstream-fix cycles, or a resource/time budget after which a negative G1/G2 result is accepted as the round-1 answer rather than triggering another upstream pass. This doesn't have to be harsh — even "two failed G1 cycles closes round 1 with a documented null result" would convert the gates from advisory to load-bearing.

---

## 6. [MAJOR] Phase 0 correlation screen risks p-hacking across 11 axes with no correction, and "beyond recent-history" implies an unspecified control analysis

**Finding:** "Does the physics axis correlate with what evo gets wrong?" is being tested against a physics estimate that x4 confirms spans 11 axes. With 11 axes tested for correlation against evo's quali errors, and no stated multiple-comparisons correction or pre-registered axis, the screen can "find" a significant-looking correlation on at least one axis by chance alone, especially over a modest weekend-count sample (2019–2026 dry Q ≈ a few hundred rows at most). Separately, the actual bar stated in Testing pathways is stronger than plain correlation: "no correlation... beyond what recent-history already carries" — that phrasing requires a *partial* correlation or residualized analysis (physics axis vs. evo error, controlling for whatever recent-history features evo already uses), which is a materially different and harder analysis than a raw correlation, and the spec never names the method or the recent-history control set to be used.

**Fix:** Pre-register which axis (or a fixed composite of the 11) is the primary test before running the screen, and specify the control methodology explicitly (e.g., partial correlation of physics-axis residual against evo quali-error, after regressing out evo's existing recent-history feature set) rather than leaving "beyond what recent-history carries" as an implicit, undefined comparison.

---

## 7. [MINOR] Phase 1's gate is explicitly unfalsifiable, yet later phases load-bear on it

**Finding:** "*Gate:* rollup reproduces known circuit character as a sanity check; no numeric ground truth claimed." This is a stated non-gate — there's no criterion under which Phase 1 fails, only an eyeball plausibility check. That would be a fine, low-stakes choice for a purely exploratory phase, except Phase 1's segmentation substrate is explicitly load-bearing downstream: it feeds "the observability router (which segments carry evidence for which basis parameters)" in Phase 2/3, and the per-circuit regime coverage map is cited again as a Phase 4 gate input ("FP × regime coverage map with quantified σ"). An unfalsifiable substrate sitting underneath two later phases that *are* held to numeric gates means a Phase-1 error (e.g., a class-membership scheme that looks plausible on known circuits but generalizes badly) can silently propagate into Phase 2/4's "passing" numbers without ever being caught by its own gate.

**Fix:** At minimum, add one falsifiable check to Phase 1 — e.g., held-out-circuit class-membership stability, or agreement between the soft-membership rollup and an independent circuit-characteristic proxy (lap-time variance by corner type, published downforce-level ratings) — so the substrate that everything else depends on isn't purely vibes-checked.

---

## 8. [MINOR] The "honesty curve" is qualitative, not the quantified calibration check it's presented as

**Finding:** Phase 7 calls the three as-of cutoffs "the honesty curve across three as-of cutoffs... the anti-overconfidence check (a post-FP1 feature that *hurts* exposes bad σ)," and the phase plan calls this "measurable." But the only stated criterion is directional and qualitative ("hurts" exposes "bad σ") — there's no calibration statistic named (e.g., prediction-interval coverage rate, CRPS, PIT histogram) and no threshold for how much "hurt" at post-FP1 versus post-Q counts as a σ problem versus ordinary noise. Three points on a curve with no metric attached is a plot, not a test; it's easy to eyeball three numbers going "roughly the right direction" and call σ honest without ever computing whether the stated uncertainty actually has correct coverage.

**Fix:** Name an explicit calibration statistic (e.g., interval coverage at post-FP1/FP2/FP3 should each fall within a stated tolerance of nominal) so "the honesty curve" is a computed pass/fail rather than a visual impression.

---

## Summary of severities

- CRITICAL: 3 (Phase 3b circular self-consistency gate; Phase 3 numbered-deferral escape hatch; Phase 2 undefined "beat the floor" metric)
- MAJOR: 3 (Phase 4 representativeness confound; no program-wide kill condition; Phase 0 multiple-comparisons/undefined control)
- MINOR: 2 (Phase 1 unfalsifiable substrate feeding falsifiable phases; honesty curve lacks a calibration statistic)
