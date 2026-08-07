# Lessons Playbook

<!-- playbook-state: run-tick=1 cap=20 dormancy-runs=10 apply-recurrences=1 apply-confirmed=3 ticked-work-ids=commander-231 -->

Open problems carried forward — NOT a log of everything learned. If a lesson is
understood and fixable, apply the fix and record it in AGENT_FEEDBACK; do not
bank it here. A lesson lives here only because it needs to be re-observed to be
understood, so every `add` states a bank-reason (what re-observation will
clarify). Reaching the cap is a failure mode — it means the bank is being used
to accumulate instead of to adjudicate. Read the Active section at the Commander
context step. Never edit by hand or by LLM: apply structured deltas via
apply_lessons_delta.py, which enforces cap, grounding, and counter rules.

Counter semantics split by scope: for most scopes a confirm is trust
(the lesson held again). For a constellation-scoped lesson it is the
opposite — a recurrence of an unfixed shared-machinery defect, so it
accrues recurrences (debt) and flags recurrence-debt. Pay the debt by
exporting to CONSTELLATION_FEEDBACK and fixing upstream. Once the fix
ships, `resolve` the lesson (cite the shipping PR): it goes terminal
(fixed-upstream) — never ripe again, a later confirm is ignored rather
than re-exported, and it ages out of the playbook on its own. Do not keep
confirming a constellation defect into a permanent workaround.

## Active

### lesson:from-child-refusal-undiscoverable-from-error
- scope: project
- task-class: delegated-planning
- statement: The engine's `advance <id> --from-child <path>` verb has two undiscoverable-from-the-refusal-text rules: (1) a non-absolute <path> resolves against the PARENT checklist's directory (dirname of --file), not cwd -- a cwd-relative path silently 'not found's; (2) it only closes a gate whose child carries a survey `consolidation` -- a `gated` child (e.g. an execute.json) is always refused ('has no consolidation yet'), and the correct recipe is a direct `attest <parent-step> --cond <id>` citing the child's per-gate evidence instead. Both rules are documented in docs/CHECKLIST_SCHEMA.md but NOT surfaced in the REFUSED message text itself, costing a doc round-trip each time they are hit fresh.
- grounding: commander-231 execute step: two REFUSED attempts ("child checklist .agent-work/commander-231/execute.json not found" from a cwd-relative path, then "child execute.json has no consolidation yet" after fixing the path) before falling back to a direct attest citing execute.json's per-gate evidence -- see .agent-work/AGENT_FEEDBACK.md commander-231 entry, Friction section.
- bank-reason: Single data point so far (this is the first delegated-commander run observed authoring a spine with a gated child driven via --from-child on a plain reasoning-heavy execute step). A second delegated commander tripping the same two rules would confirm this as a recurring onboarding cost worth a one-line addition to the engine's REFUSED message text (scripts/checklist_engine.py is fenced this wave -- #227 owns it -- so no fix is applied here).
- mentions: 1
- confirmed: 0
- disconfirmed: 0
- status: active
- added: 2026-07-24 (commander-231)
- last-confirmed: none
- runs-since-confirmed: 1
