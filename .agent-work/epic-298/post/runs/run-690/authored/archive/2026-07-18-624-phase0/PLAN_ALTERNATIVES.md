# Plan alternatives — issue #624 Phase 0 gate structure

Design-it-twice: the *what* (5 probes) is fixed by the launch order; the *how* (gate structure, reasoning-gate vs crew-gate) is this run's actual design choice.

## Candidate A — all reasoning gates (commander-direct)

One gate per probe (correlation screen, wide-σ A/B, integration tracer, SQ probe, baseline lock), each driven directly by me (the commander) in this context, no crew dispatch. Constraint: minimize turn/wall-clock cost, since the launch order frames these as "cheap probes."

- **Depth**: low overhead, fast — I already hold deep source-verified context from the understand-step research (exact seams, schemas, row counts).
- **Locality**: all analysis code + findings stay in one authoring context; consistent methodology across probes.
- **Seam placement**: n/a (no interface introduced).
- **Testability**: WEAKEST — no independent verification of statistical correctness (partial-correlation sign conventions, join correctness, pre-registration discipline) or of the sampler-touching wide-σ A/B code. Self-graded-homework risk on the one probe (g1) the launch order calls MANDATORY-rigor.

## Candidate B — all crew gates (implement + review per probe)

Every probe becomes a full crew gate (`gN-implement` dispatches an Agent-tool implementer via `run_crew.py` registry per `lesson:run-crew-cli-launcher-misfit`; `gN-review` dispatches an independent reviewer). Constraint: maximize independent verification, matching default commander-core doctrine for code-producing gates.

- **Depth**: shallow per-gate (crews start cold each time, re-deriving context I already hold — seam citations, schema, row counts already verified above).
- **Locality**: worse — 5x context-loading overhead, each crew re-reads the same architecture map/DB schema I already read once.
- **Seam placement**: n/a.
- **Testability**: STRONGEST in principle, but for probes 3-5 (integration tracer = running one already-verified CLI invocation; SQ probe = one well-scoped function call; baseline lock = freezing already-computed numbers into a doc) the "independent implementer + independent reviewer" machinery is disproportionate to the risk it retires — these are not load-bearing interfaces, they're single verified commands and doc-writes.

## Chosen: named hybrid (converged)

**Crew gate** for the two probes with genuine methodological/code risk that a second pair of eyes materially de-risks:
- **g1 (correlation screen)** — the launch-order MANDATORY-rigor item (Pre-Ruling #1); a partial-correlation script has real failure modes (sign errors, leakage, join grain mismatches between per-constructor physics estimates and per-driver quali rows) that self-review is weak against.
- **g2 (wide-σ A/B)** — touches the sampler and a real (if prototype) injection seam; wiring mistakes here are exactly the class of bug the launch order's #623-adjacent history shows recurs (headless deadlocks, thread caps).

**Reasoning gate** (commander-direct, no crew) for the remaining three, each low-risk given the context already verified above:
- **g3 (integration tracer)** — a single already-verified `sampled-predict` CLI invocation (exact command pasted in the launch order) plus reading its four-record output; no new code logic to get wrong.
- **g4 (SQ probe)** — one function call (`estimate_session` against an SQ-typed session) with a small, easily self-checked failure surface (does it load, does it error, why).
- **g5 (baseline lock)** — freezing numbers already computed at g1 into a durable doc; a write task, not an analysis task.

This converges Candidate A's speed on the low-risk probes with Candidate B's rigor on the two probes where it actually retires risk — avoiding both self-graded-homework on the mandatory-rigor screen and disproportionate crew overhead on a doc-freeze and a single CLI run.

**Untaken road**: a full 5-crew-gate structure (Candidate B) was not run — surfaced here as the road not taken, reason above (disproportionate cost on low-risk probes).

## Cold critic

Dispatched as a separate subagent (agent id `a699118cf8226027e`, no authoring context beyond this file + `MISSION_FRAME.md`). 7 findings (1 CRITICAL, 4 MAJOR, 2 MINOR). Disposition (this run's principal = the launch order + my own delegated latitude for gate-structure choices — not an Admiral float, this is plan-structure judgment within scope):

1. **CRITICAL (g5 independently re-reads the store, inheriting g1's risk with no review)** — EDIT, and on inspection the correct fix is even cleaner than first drafted: x4's exact per-axis floor numbers and x7's five-fracture list are NOT something g5 (or g1) needs to (re)compute at all — they already exist as complete, reviewed artifacts from the prior exploration wave: `.agent-work/archive/2026-07-17-explore-physics-evo-hookup/excursions/x4-normalization-RESULT.md` (full per-axis table: field σ, noise SD abs/rel, weekends-to-resolve) and `x7-basis-map-RESULT.md` (the five named fractures). g5's imperative is corrected to TRANSCRIBE from those two archived files only — zero new DB queries, zero dependency on g1's new correlation numbers. Close criteria include a mechanical diff check (the frozen doc's numbers must match the archived source files verbatim).
2. **MAJOR (g3 touches the LIVE sampler, not a prototype — maybe under-reviewed)** — EDIT (proportionate, not a crew upgrade). Added a concrete, falsifiable close-criterion: an assert-schema script over the produced four-record contract, rather than promoting to a crew gate (the CLI invocation itself is pre-verified in the launch order; the residual risk is interpretation, which a schema-assert check retires cheaply).
3. **MAJOR (g3 "round-trips" undefined; target weekend TBD)** — EDIT. Weekend fixed NOW: 2025 Japan (the exact working example cited in the launch order). "Round-trips" defined operationally: all four record types produced without error, each matches its documented schema, spot-check ≥3 driver rows against DB ground truth.
4. **MAJOR (g4 crash-only check misses silently-wrong-numbers failure mode)** — EDIT. g4 close criteria strengthened: beyond load/error, numerically sanity-check the SQ-derived axis values against the SAME driver/constructor's adjacent-round Q-session values (plausible magnitude/sign, not just non-crash).
5. **MAJOR (g4/g5 carry the `physics_region_no_evo_import` boundary risk with no independent check — self-blind spot)** — EDIT. Added a mechanical, non-self-gradable check to both gates' close criteria: `grep` for `evo_predictor`/`src.evo_predictor` imports in any touched `src/physics/` file, expect zero hits.
6. **MINOR (a middle "implement + independent-review-only" tier was never considered)** — REJECT-with-reason. Noted as a second untaken road: given the informational-probe framing and turn-cost, the mechanical checks added per findings 2-5 substitute cheaply for a review tier on the three low-stakes gates; full independent review stays reserved for g1/g2 where Pre-Ruling #1 makes it mandatory and the sampler-wiring risk is real.
7. **MINOR (g5 had no verification step)** — EDIT, folded into #1's fix.

All CRITICAL/MAJOR findings resolved by edits now reflected in `execute.json`; both MINORs accepted as named untaken roads with reasons.
