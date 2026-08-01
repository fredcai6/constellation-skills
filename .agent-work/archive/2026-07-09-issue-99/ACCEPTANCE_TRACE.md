# Acceptance trace — issue-99

Every acceptance criterion, scope item, human ruling, and lift → the artifact satisfying it + the mechanical check proving it. Ruling-level sentence mapping: see the ruling-traceability table in `crew-handoffs/g1-implement/IMPLEMENTER_RESULT.md` (not repeated here — referenced per plan).

## Issue #99 acceptance criteria

| # | Criterion | Satisfied at | Mechanical check |
|---|---|---|---|
| 1 | Doctrine names the design-it-twice standard, weight scaling, trivial-skip rule, symmetric with critical-review | `skills/_shared/global-orchestrator.md` § "Design-it-twice (standard, not optional)" (Trigger / Bias-to-yes / Count-panel / Convergence bullets) | g1-integrate.c1 greps (heading, untaken road, when-in-doubt-panel, bias-to-yes) — green; symmetry judged by g1 reviewer side-by-side read (REVIEW_RESULT: APPROVE, criterion 1) |
| 2 | Commander plan step references the standard: alternatives at weight, always-on lightweight plan critic before plan-approved | `skills/commander/SKILL.md` Mission frame consumption paragraph; `COMMANDER_SPINE.template.json` plan imperative + postcondition c4 | g1-integrate.c1 greps (plan.alternatives, plan.critic, untaken road ×2) + c4 JSON assertion — green |
| 3 | Frame-the-problem-while-agents-run is part of the parallel-alternatives contract | Doctrine § Convergence bullet ("framing block... 'not a proposal'"); `design-it-twice-brief.md` § "Framing block — presented to the human WHILE the agents run" | g1-integrate.c1 greps ('not a proposal' in both files) — green |
| 4 | Competitive-critic documented as an option with tension + human-triage safeguard | `skills/_shared/global-orchestrator.md` critical-review §, competitive-critic bullet | g1-integrate.c1 greps (competitive.critic, self.triage) — green; erosion guard verified as named g1-review focus item 3 (APPROVE) |

## Confirmed-scope items and rulings

| Item | Satisfied at | Check |
|---|---|---|
| Shared doctrine symmetric with #92 standard | Doctrine section adjacent + structurally parallel to critical-review | Reviewer criterion 1 (APPROVE) |
| Commander consumption before plan-approved | SKILL.md paragraph + spine c4 | c1 chain + c4 assertion |
| q1 bias-to-yes, named untaken roads | Doctrine Bias-to-yes bullet; brief Untaken-road section; spine c4 | Ruling-traceability table row q1, verified by reviewer criterion 2 |
| q2 critic reads plan+frame only; human disposes every finding | SKILL.md paragraph; critical-review §; spine imperative | Ruling table row q2, reviewer criterion 2 |
| q2b panel preferred / single-if-easy / choice surfaced | Doctrine Count/panel bullet; brief Count + Panel-vs-single sections | Ruling table row q2b, reviewer criterion 2 |
| Shared spun-out contract (not commander-local, not EXCURSION_BRIEF reuse) | `skills/_shared/design-it-twice-brief.md`, shipped via `_GLOBAL_ORCHESTRATOR` tuple | test -f + installer grep + --dry-run — green; reviewer criterion 5 (genuine spin-out) |
| Explorer references only (non-goal: machinery unchanged) | `skills/explorer/SKILL.md` one bullet; `EXCURSION_BRIEF.template.md` one paragraph | g2-close.c1: new-token greps + exact two-file diff + zero-deletion numstat |
| Doctrine followable cold | Dogfood subagent vs pre-registered `DOGFOOD_RUBRIC.md` | g2-close.c3; verdict in `DOGFOOD_TRANSCRIPT.md` |
| No new standalone skill; no engine change; freeze/amend untouched | — (absence) | g1-integrate.c1 allowlist diff check (only five owned files) — green |

## Follow-ups queued (not this run's scope)

- tc1 (execute.json triage_candidates): critical-review has no engine-enforced spine postcondition of its own; c4 co-locates both mechanisms.
