---
name: constellation-triage
description: Create issue-ready recommendations. Use when Commander, Cartographer, Crew, or the user finds future work outside current scope.
---

# Constellation Triage

Write issue-ready recommendations for follow-up work. Triage does not implement, keep backlog, or pull work into current scope unless asked.

**No checklist. Work through the candidates directly.**

## Fix-Now Eligibility Ladder

A candidate qualifies for the fix-now lane when it clears all four rungs — every rung is required, not most:

- **Bounded diff** — a small number of lines/files; not multi-gate work.
- **Adjacent to current scope** — touches code/doctrine the run already has open; not a cold-start area.
- **Verifiable now** — covered by an existing test, or trivially verifiable by inspection, in the same context.
- **No architecture/production-default impact** — structural changes still route through reconcile; fix-now never carries one.

Clearing three of four does not qualify; route it as `filed` or `recommend-and-defer` instead.

## Steps

1. **Load candidates and authority.** Consume all sources: `execute.json` `triage_candidates`, Cartographer findings, review findings, plans, implementation evidence, user notes. Note issue creation authority from `docs/agents/ORCHESTRATOR_CONTEXT.md` if present (the default posture is the inherited `references/global-orchestrator.md`).

2. **Classify each candidate.** Assign one or more labels: bug, cleanup, missing test, missing doc, missing architecture packet, missing structural node, missing capability anchor, architecture weakness, structure/constraint mismatch, stale generated map, ungrounded claim/decision, bad map edge, feature, tooling, unresolved decision, research hardening, dependency cleanup, security/privacy, performance/resource. Preserve the structural anchor and, for each observation, its conditions, `type` and `rev` — the grounding travels with the observation, so do not strip it while classifying.

   Map-quality findings from Scout map them as: stale map -> `stale generated map`; missing capability anchor -> `missing capability anchor`; bad/high-maintenance edge -> `bad map edge`; ungrounded claim/decision -> `ungrounded claim/decision` (or `unresolved decision` when a decision is in dispute); architecture pressure -> `architecture weakness` or `structure/constraint mismatch`.

3. **Route each candidate to exactly one disposition.** Check it against the Fix-Now Eligibility Ladder above, then land it in exactly one of three — none is ever left unrouted:

   - **`fixed-now`** — eligible per the ladder: fix it now. Still produce the recommendation in the next step with the fix commit sha attached — an unrecorded quick fix is the exact failure this lane exists to prevent.
   - **`filed`** — ineligible for fix-now, and issue-filing authority is clear: file the issue as today; the recommendation records the issue number.
   - **`recommend-and-defer`** — ineligible for fix-now, and filing authority is unclear or unavailable this run: produce the issue-ready recommendation but do not file it; the recommendation records why authority was unclear, so the orchestrator/human decides later instead of the run improvising a filing decision it wasn't authorized to make.

4. **Write recommendations.** For each candidate produce an issue-ready recommendation using `templates/TRIAGE_RECOMMENDATION.template.md`. An issue records observations with baselines; it does not prescribe a solution.

   - **A defect** carries a *list* of observations — one block per occurrence, never merged into one summary. Each block states what's wrong, what was expected, the feeding conditions that enable the bad state (including which environment), `type` (`measured` or `inferred`, and *how* — mandatory for both values), and `rev` (the state the observation was true of).
   - **An enhancement** carries the desired behavior *plus what happens today instead*. Without the current-behavior statement, an enhancement cannot be distinguished from something that already works.
   - **`possible fix` is optional, is a hypothesis rather than a spec, and is a top-level sibling of the observations** — one per issue, not one per observation.
   - **`open questions` is optional and sits alongside `possible fix`** — what is unresolved or in dispute, and what would settle it. Both are thinking out loud; only the observations are load-bearing.

   Then add importance, acceptance criteria, out of scope, and the disposition from step 3 with its disposition-specific detail (fix commit sha / issue number / deferral reason). This step runs for every candidate, including `fixed-now` ones — fixing it now shortens the work, it never skips the record.

## Issue Authority

Ground rules govern direct issue creation. `recommend-and-defer` is the recorded form of "ask" below — produce the recommendation and let authority resolve later rather than guessing. If unclear, produce recommendations and ask.

Templates: `templates/TRIAGE_RECOMMENDATION.template.md`.
