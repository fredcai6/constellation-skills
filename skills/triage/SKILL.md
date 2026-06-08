---
name: constellation-triage
description: Create issue-ready recommendations. Use when Commander, Cartographer, Crew, or the user finds future work outside current scope.
---

# Constellation Triage

Write issue-ready recommendations for follow-up work. Triage does not implement, keep backlog, or pull work into current scope unless asked.

**No checklist. Work through the candidates directly.**

## Steps

1. **Load candidates and authority.** Consume all sources: `execute.json` `triage_candidates`, Cartographer findings, review findings, plans, implementation evidence, user notes. Note issue creation authority from `docs/agents/ORCHESTRATOR_CONTEXT.md`.

2. **Classify each candidate.** Assign one or more labels: bug, cleanup, missing test, missing doc, missing architecture packet, missing structural node, missing capability anchor, architecture weakness, structure/constraint mismatch, stale generated map, ungrounded claim/decision, bad map edge, feature, tooling, unresolved decision, research hardening, dependency cleanup, security/privacy, performance/resource. Preserve structural anchor, current truth, future concern, evidence.

   Map-quality findings from Scout map them as: stale map -> `stale generated map`; missing capability anchor -> `missing capability anchor`; bad/high-maintenance edge -> `bad map edge`; ungrounded claim/decision -> `ungrounded claim/decision` (or `unresolved decision` when a decision is in dispute); architecture pressure -> `architecture weakness` or `structure/constraint mismatch`.

3. **Write recommendations.** For each candidate produce an issue-ready recommendation using `templates/TRIAGE_RECOMMENDATION.template.md`: what, importance, evidence, acceptance criteria, out of scope. Create issues where authority allows; otherwise produce recommendations and ask.

## Issue Authority

Ground rules govern direct issue creation. If unclear, produce recommendations and ask.

Templates: `templates/TRIAGE_RECOMMENDATION.template.md`.
