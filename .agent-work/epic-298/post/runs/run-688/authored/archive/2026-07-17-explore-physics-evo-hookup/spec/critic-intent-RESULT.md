# Critic — Intent-Fit Lens

Reviewer: cold adversarial critic, intent-fit lens only. Source: DESIGN_SPEC.md as written, no exploration record consulted beyond what the spec itself quotes.

Stated intent (spec's own words): "beat human players at fantasy F1," round 1's job is narrow — "produce the most believable and honest physics features we can, and prove whether they help predict qualifying" via honest A/B, decided by fantasy pts/race vs actual. Everything below is measured against that sentence, not against internal consistency with the spec's own "done" bar (which I also treat as suspect, see Finding 4).

---

## Finding 1 — CRITICAL: Phase 3b + the bulk of Phase 4 optimize for round-2 driver-affinity, which Intent explicitly excludes from round 1

The Intent section is unambiguous: "driver-affinity consumption... [is] explicitly round 2+." The phase plan honors this only on a technicality. Phase 3b ("Driver utility on the same basis") is built end-to-end in round 1 — fit, self-consistency gate, the works — and is described in the spec's own words as "banked for round-2 consumption." That's production without consumption, which lets it dodge the round-2 label while consuming round-1 time and engineering budget.

Worse: Phase 4 (FP extension) is labeled "the deepest piece" of the entire plan — i.e., plausibly the single largest engineering lift — and the spec itself states its purpose plainly: "FP is a *weak* car-performance demonstrator but a *strong* driver-utility demonstrator; its main product feeds 3b, car capability is a heavily-downweighted byproduct that nudges the season-pooled estimate." Read that sentence again: the deepest phase in a plan whose stated job is "prove whether physics features help predict qualifying" admits that its main product does not feed qualifying prediction. It feeds round 2. The round-1 payload — car capability, which is what evo/fantasy actually needs — is a "heavily-downweighted byproduct." This is effort misallocation stated in the design's own text, not inferred.

**Fix:** Descope Phase 3b out of round 1 entirely (note it as a round-2 dependency, don't build it). Cut Phase 4 down to exactly what fixes x1's coverage bug (`fp_mass()` so FP1-3 estimates stop being fuel-biased) and produces the car-capability byproduct directly — drop the parc-fermé reaction-step model, the driver-utility-oriented representativeness machinery, and anything whose gate criteria (line 80) are keyed to representativeness/driver signal rather than to car-capability accuracy. If FP mechanics genuinely can't be separated from utility work, that's itself evidence Phase 4 belongs in round 2, not round 1.

---

## Finding 2 — CRITICAL: no gate in the plan can actually stop or shrink the plan

Look at how every phase's failure mode resolves:
- Phase 0's correlation screen: "reportable either way (no kill switch)."
- Phase 2's floor test: falsification just "means the extra layers aren't doing real work" — no stated consequence.
- Phase 7 (line 90): "a stall sends the finding back to the implicated upstream phase, not a restart" — i.e., even the terminal decision gates don't terminate anything; they loop back into more building.

For a plan whose explicit deliverable is "a measured answer to 'does this beat what we have,' reportable either way," this is a design that cannot produce a negative answer with any weight, because a negative answer never reduces scope — it just reroutes to more phases. That converts "prove whether it helps" from a real decision point into a formality sitting after a fixed, unconditional six-phase build (1, 2, 3, 3b, 4, 5, 6) that happens regardless of what Phase 0 or Phase 2 find. If the intent were actually driving the plan, an early null result should visibly shrink what gets built next — cutting Phase 3b, trimming Phase 3's fracture list, or skipping straight to a thin Phase 5/6/7 with Phase-2-only features to get a real answer fast.

**Fix:** Define an actual stop/scope-down condition for at least Phase 0 and Phase 2 — e.g., a Phase-0 correlation near zero AND a Phase-2 floor-beat failure should trigger a descoped round 1 (ship Phase-2 features as-is to Phase 7's G1, skip 3/3b/4 unification work), not "reweight toward affinity/σ layers" while the full phase sequence proceeds unchanged.

---

## Finding 3 — MAJOR: the exploration digest oversells Phase 0 as answering the ceiling question it doesn't test

Line 36 (open threads) states: "whether physics beats the ~0.80 FP-data quali ceiling (the Wave 7A screen answers this, unrun)." But Phase 0's actual Wave-7A test (line 55) is a correlation screen — "does the physics axis correlate with what evo gets *wrong*" — which is a weaker, different question than the head-to-head Brier/sign-accuracy-vs-ceiling comparison that is literally defined as gate G1 in Phase 7 (line 90). A correlation with evo's errors is necessary-ish but nowhere near sufficient to show physics *beats* the ceiling; you can correlate with errors and still not move the needle enough to change predictions.

This matters for intent-fit because it's exactly the kind of self-reassurance that lets a team feel the make-or-break question has an early cheap answer when it doesn't — the actual answer is 6 phases and probably months downstream. If Phase 0 comes back with a mild positive correlation, the plan will likely read that as license to proceed through the full build, without ever having tested the thing that decides whether round 1 succeeds.

**Fix:** Rewrite the open-thread line to stop crediting Wave 7A with answering the ceiling question; state plainly that the ceiling question is untested until G1 in Phase 7, and consider pulling a cheap proxy for G1 (e.g., run Phase-2's raw output through a bare Brier comparison) into Phase 0 or immediately after Phase 2, rather than after the full basis-unification and FP builds.

---

## Finding 4 — MAJOR: the round-1 "done" bar itself already smuggles physics-elegance goals in alongside the actual decision metric

The Intent section's own "done" criteria (line 22) list four things: "physics stability the user trusts," a "consolidated" stage-1 estimator, a clean seam, and "a measured answer." Only the last of these is actually about the stated goal (fantasy pts / quali prediction). The first two are architecture-quality goals with no stated connection to whether the features help predict anything. Because the phase plan is built to satisfy this four-part "done" bar rather than the single-sentence intent above it, phases like Phase 3 (unify five x7 fractures, persist full cross-view covariance, run a parallel 2026 aero-mode sub-track) get justified by "the user's rule is 'build the architecture to solve the hardest problem'" — a methodological preference, not evidence that unification is necessary to answer "does this help fantasy points." Phase 3 is plausibly the single largest technical lift in the entire plan, and it happens before the A/B ever runs.

This isn't necessarily wrong — the user may genuinely want durable architecture over a quick answer — but the spec doesn't confront the tradeoff: a fully unified, cross-correlated, σ-honest basis is a "nice to have for trust" not a "need to have for the G1/G2 test." A partially-unified, honestly-flagged-as-approximate feature set could reach Phase 7 much sooner, and if the A/B result is strongly negative, all the unification work in Phase 3 was spent proving elegance nobody needed. If it's strongly positive, unification becomes a well-motivated round-1.5 refinement instead of an up-front bet.

**Fix:** Either (a) explicitly own that round 1 is scoped to a trust/architecture bar, not a speed-to-answer bar, and drop "prove whether it helps" language that implies urgency, or (b) reorder so a minimally-unified Phase-2 feature set reaches a cheap version of G1 before Phase 3's full fracture-closure work is committed.

---

## Finding 5 — MINOR: Phase 1's circuit time-share rollup pays round-2 cost on round-1's critical path

Phase 1 explicitly serves "two consumers: the observability router... and the round-2 circuit-demand/affinity substrate (banked, not chased)" (line 63). Same pattern as Finding 1 but smaller in scope: work labeled "banked, not chased" is nonetheless being built in round 1's first substantive phase. Low cost relative to Findings 1-2, but it's the same failure mode recurring, which suggests it's structural to how the plan was assembled (dual-purposing round-2 prep as round-1 substrate) rather than a one-off.

**Fix:** If the observability router doesn't strictly need the circuit-demand rollup (only needs the segment classes), split them — build the router now, defer the rollup aggregation step to round 2.

---

## Top 3 (severity order)

1. **CRITICAL** — Phase 3b and most of Phase 4 ("the deepest piece") admit, in the spec's own words, that their main product feeds round-2 driver-affinity, not round-1's quali-prediction goal; car capability is a "heavily-downweighted byproduct." This is the plan's largest effort sink serving the wrong goal.
2. **CRITICAL** — No gate in the design can shrink or stop the plan; every failure mode "reweights" or "sends back upstream," so the full six-phase build (1,2,3,3b,4,5,6) runs unconditionally before the actual decision gates (G1/G2) in Phase 7 ever fire.
3. **MAJOR** — The digest credits Phase 0's correlation screen with answering the ~0.80-ceiling question, but that's a different, weaker test than G1's actual Brier/sign-accuracy comparison — creating false confidence that the make-or-break question is cheaply answered when it's actually untested until deep into the build.
