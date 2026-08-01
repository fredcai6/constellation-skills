# Lessons Playbook

<!-- playbook-state: run-tick=1 cap=20 dormancy-runs=10 apply-recurrences=1 apply-confirmed=3 ticked-work-ids=euler-001-20260710 -->

Curated, bounded workflow lessons. Read the Active section at the Commander
context step. Never edit by hand or by LLM: apply structured deltas via
apply_lessons_delta.py, which enforces cap, grounding, and counter rules.

Counter semantics split by scope: for most scopes a confirm is trust
(the lesson held again). For a constellation-scoped lesson it is the
opposite — a recurrence of an unfixed shared-machinery defect, so it
accrues recurrences (debt) and flags recurrence-debt. Pay the debt by
exporting to CONSTELLATION_FEEDBACK and fixing upstream, then retire it;
do not keep confirming it into a permanent workaround.

## Active

### lesson:python-module-form-for-postconditions
- scope: commander
- task-class: planning
- statement: Use python -m <tool> rather than bare <tool> in command postconditions
- grounding: .agent-work/euler-001-20260710/execute.json:162-175 (g1-integrate c1 waived)
- target: docs/agents/ORCHESTRATOR_CONTEXT.md
- mentions: 1
- confirmed: 0
- disconfirmed: 0
- status: active
- added: 2026-07-10 (euler-001-20260710)
- last-confirmed: none
- runs-since-confirmed: 1
