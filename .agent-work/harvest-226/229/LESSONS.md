# Lessons Playbook

<!-- playbook-state: run-tick=1 cap=20 dormancy-runs=10 apply-recurrences=1 apply-confirmed=3 ticked-work-ids=issue-229 -->

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

### lesson:prove-command-fails-postcondition
- scope: handoff
- task-class: general-workflow
- statement: A gate that must prove a command CORRECTLY FAILS (e.g. "the guard refuses this input") does not fit the engine's command-postcondition semantics (exit 0 = pass). A `! <command>` bash-negation wrapper as the postcondition's `command` field makes "the guard fired" a mechanically re-verified engine check instead of a self-reported attest.
- grounding: AGENT_FEEDBACK.md 2026-07-24 issue-229 -- implementer's g1-implement-result.md Workflow Feedback section, improvised the negation-wrapper pattern for skip-guard/coverage-floor negative-path proofs
- bank-reason: one data point from one Commander run -- needs to recur on a second gate/issue that also needs to prove a command fails before this is confidently a template-worthy pattern rather than a one-off improvisation
- mentions: 1
- confirmed: 0
- disconfirmed: 0
- status: active
- added: 2026-07-24 (issue-229)
- last-confirmed: none
- runs-since-confirmed: 1
