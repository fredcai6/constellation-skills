# Critic: Simplicity / YAGNI lens — DESIGN_SPEC.md (physics-as-feature-engine, round 1)

Reviewed spec only, as instructed. Findings below, most severe first.

---

## Finding 1 — Phase 0's cheap screen has no wired decision; Phases 1-4 proceed regardless of its result
**Severity: CRITICAL**

The whole rationale for opening with Plan C's "free probes" is to buy go/no-go information cheaply before committing to Plan B's expensive foundation-first build. But the spec never actually wires a decision to the outcome. Phase 0's testing pathway says explicitly: "if the existing physics axis shows no correlation... reweight toward affinity/σ layers (**not a kill**)." There is no stated branch where a weak or null Phase 0 result changes the scope, order, or existence of Phase 1 (segmentation), Phase 2 (four-layer state model), Phase 3 (basis unification), or Phase 4 (FP). Every one of those phases is described as happening unconditionally. If the cheap screen's answer doesn't change what gets built next, it isn't actually a gate — it's a data point collected and then set aside, and the "hybrid plan" claim to be buying go/no-go information cheaply is not backed by the phase plan as written.

**Suggested cut/defer:** Before confirming, add an explicit branch after Phase 0: a strong correlation greenlights Phase 2 as scoped; a weak/null correlation should shrink Phase 2 to the leanest state model that can still be A/B'd (see Finding 5) rather than the full four-layer build, and should push Phase 3's unification work later still. Without this branch, drop the "buys go/no-go information cheaply" framing from the rationale — it's not true as written.

---

## Finding 2 — Phase 3b (driver utility) does no round-1 work; it is round-2 building smuggled into the round-1 phase count
**Severity: CRITICAL**

Phase 3b is explicitly self-described as "produced, not consumed," with "no ground-truth gate (named weak spot)" and "banked for round-2 consumption." Round 1's Intent section is unambiguous: "produce the most believable and honest physics features we can, and prove whether they help predict qualifying." Nothing in Phase 5 (the feature view — weekend-state / car-basis posterior / lap evidence / as-of feature view) or Phase 6 (injection) consumes driver utility. Phase 7's gates (G0 correlation, G1 quali sign/Brier, G2 fantasy pts) don't touch it either. This phase exists purely to have Phase 4's FP-utility output land somewhere, for a consumer that round 1 explicitly declines to build. That is speculative building by the plan's own admission (the task's suspicion is confirmed by the spec's own text, not just inferred).

**Suggested cut/defer:** Remove Phase 3b from the round-1 phase plan entirely. If Phase 4's FP work naturally produces a utility byproduct, file it as a round-2 issue (the same disposition as the "driver-affinity and driver-utility *consumption*" already correctly listed under Out of scope) rather than numbering it as a phase with its own gate. This also removes one of the eight phases standing between the plan and a fantasy-points number.

---

## Finding 3 — Phase 4 (FP)'s round-1 payload is admitted to be a "heavily-downweighted byproduct"; its primary payload feeds the cut Phase 3b
**Severity: MAJOR**

The spec states the reframe plainly: "FP is a *weak* car-performance demonstrator but a *strong* driver-utility demonstrator; its main product feeds 3b, car capability is a heavily-downweighted byproduct that nudges the season-pooled estimate." With Phase 3b cut (Finding 2), Phase 4's stated main product has no round-1 consumer, and its round-1-relevant output is explicitly described as a minor nudge. Combined with x2's excursion finding that quali headroom over the FP-data ceiling is thin (~3pp headline / ~0.3pp out-of-sample), Phase 4 — called "the deepest piece" — is being built in round 1 mostly to feed work round 1 doesn't need.

**Suggested cut/defer:** Defer Phase 4 past the first A/B pass. Run G0/G1/G2 on the Q-only pipeline (Phases 0, 2, 3, 5, 6, 7) first. If that shows the physics axis is worth extending, FP's byproduct-level car-capability nudge is easy to justify as a follow-up; if it doesn't, FP's deepest-piece cost is never paid for a signal nobody asked for.

---

## Finding 4 — Phase 3's full covariance unification is committed to before evidence that the existing five-view estimates can't already carry the signal
**Severity: MAJOR**

x7's own finding, quoted in the exploration digest, is that the five views carry "within-view covariance only" — a σ-quality/precision concern, not a signal-existence concern. Phase 0's correlation screen tests exactly whether the *existing* estimates already correlate with evo's errors. Yet Phase 3 (one physical basis, full cross-view covariance, five fractures closed) is scheduled as a mandatory rebuild ahead of Phase 7's A/B, not as a response to Phase 7 showing the existing basis is precision-limited. The phase's own gate — "an undecided fracture is a phase failure" — cannot produce a "this wasn't worth it" signal; a fracture can only be fixed or "honestly deferred," so the phase is structurally unable to fail in the direction that would save the work.

**Suggested cut/defer:** Run Phase 7's G0/G1 once on the existing five-view estimates (with conservative, wider σ to honestly account for the uncoupled covariance) before committing to Phase 3's unification. If the raw estimates already show signal, Phase 3 becomes a precision-improvement investment made with evidence it will move the fantasy-points needle, not a prerequisite taken on faith.

---

## Finding 5 — Phase 2's four-layer weekend-state model is an architecture bet made before any A/B evidence, with no round-1 falsification path for the two hardest layers
**Severity: MAJOR**

The four layers are: (1) explained physics, (2) structured within-session grip evolution, (3) field-car common-mode two-stage decomposition, (4) car signal deltas. Layer 1 is straightforward and clearly load-bearing (density correction, mass). Layers 2 and 3 are genuinely sophisticated inventions — a smooth within-session grip latent, and a two-stage relative-then-reanchor field-car solve. The stated gate for the whole model is "must beat x4's relative floor" on x4's own metric — that's a methodology sanity check (does normalizing help), not a test of whether layers 2 and 3 specifically contribute predictive value for round 1's actual question (does this help quali prediction / fantasy points). It's possible to beat the relative floor with just layer 1 + a single relative-to-field delta, folding 2-4 into one simpler step, and only add the internal decomposition once G1/G2 show headroom worth chasing with a more refined car-signal isolation.

**Suggested cut/defer:** Ship a two-layer version for round 1 (explained physics + single relative-to-field delta) and gate Phase 7's first pass on that. Only build out the full four-layer decomposition (separating within-session evolution from field common-mode) if the simpler version's A/B result shows the extra structure is likely to matter — e.g., residual patterns that look like unmodeled within-session drift.

---

## Finding 6 — Phase 1's segmentation sophistication is partly justified by round-2 consumption, not round-1 need
**Severity: MINOR**

Phase 1 states it serves two consumers: "the observability router (which segments carry evidence for which basis parameters)" — round-1-load-bearing — "and the round-2 circuit-demand/affinity substrate (banked, not chased)" — explicitly round 2. The "soft/fractional property-class membership over a continuous descriptor substrate" is a meaningfully more sophisticated deliverable than a router needs; a router just needs to know which segments carry evidence for which parameters, which a coarser, harder classification could answer adequately for round 1.

**Suggested cut/defer:** Scope Phase 1 to what the observability router needs (segment tags sufficient to route evidence), and treat the soft-membership continuous substrate as a round-2 enhancement filed alongside the circuit-demand/affinity work it's actually for, unless the router demonstrably can't function without it.

---

## Finding 7 — The Phase-A-style integration tracer bullet is deferred until after Phase 2, when it could de-risk the seam earlier, off Phase 0's existing data
**Severity: MINOR**

The plan borrows "one move from Plan A" — push one real weekend through the whole pipe as soon as stage-1 exists in rough form — but ties this to Phase 2's output ("as soon as Phase 2 produces a rough stage-1"). Since Phase 0 already establishes that Q physics estimates exist for 2019–2026 in usable stores, the seam/contract mechanics (Phase 5's feature view, Phase 6's injection, the as-of leakage plumbing) could be exercised against Phase 0's raw estimates immediately, decoupling "does the wiring work" from "is the four-layer architecture right." As written, integration risk and architecture risk are retired together, which means an architecture rework in Phase 2 could force a second pass through the integration plumbing anyway.

**Suggested cut/defer:** Move the tracer-bullet weekend to immediately after Phase 0, using the raw five-view estimates as the feature source. Re-run it again after Phase 2/3 land if the architecture changes materially. This is cheap (it's explicitly framed as reusing the real contract, not throwaway work) and buys earlier confidence that the hardest non-physics part — the seam — actually works.

---

## Summary table

| # | Severity | One-line |
|---|---|---|
| 1 | CRITICAL | Phase 0's screen result changes nothing about what gets built next — not a real gate |
| 2 | CRITICAL | Phase 3b does zero round-1 work; it's round-2 building with a phase number |
| 3 | MAJOR | Phase 4/FP's round-1 payload is admittedly a "heavily-downweighted byproduct"; its main product feeds the cut Phase 3b |
| 4 | MAJOR | Phase 3's full covariance rebuild is committed to before evidence the existing five-view estimates can't already carry signal |
| 5 | MAJOR | Phase 2's four-layer model is an architecture bet with no round-1 falsification path for its two hardest layers |
| 6 | MINOR | Phase 1's soft-membership sophistication is partly justified by round-2 consumption |
| 7 | MINOR | The integration tracer bullet is deferred past Phase 2 when it could de-risk the seam right after Phase 0 |
