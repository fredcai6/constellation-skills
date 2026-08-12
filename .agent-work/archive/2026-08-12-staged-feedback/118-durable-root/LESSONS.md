# Lessons Playbook

<!-- playbook-state: run-tick=1 cap=20 dormancy-runs=10 apply-recurrences=1 apply-confirmed=3 ticked-work-ids=118-durable-root -->

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

### lesson:engine-attest-preconditions-before-start
- scope: project
- task-class: orchestration
- statement: The checklist engine refuses `start <step>` while a step's null preconditions are unattested, but the `current` imperative narrates only postconditions; attest the preconditions FIRST, then `start`. Discovered by REFUSED loops at understand/plan/g1-review/g1-integrate (attest p1 -> re-run start).
- grounding: .agent-work/118-durable-root/AGENT_FEEDBACK.md (Friction/unclear: 'start REFUSED until I attested p1 first' — 3+ retry round-trips this run)
- bank-reason: Single run so far. Re-observe whether other commanders hit the same REFUSE-then-attest-then-start loop; if it recurs, it justifies an engine `current`-output hint ('attest null preconditions before start') or a `start` that auto-surfaces unmet preconditions, rather than a per-run rediscovery.
- target: checklist_engine current/start output (or commander-core gate-execution note)
- mentions: 1
- confirmed: 0
- disconfirmed: 0
- status: active
- added: 2026-07-19 (118-durable-root)
- last-confirmed: none
- runs-since-confirmed: 1

### lesson:reviewer-docs-only-fowler-pass-framing
- scope: project
- task-class: review
- statement: On a docs-only gate the reviewer skill frames the Fowler/smell pass as a 'skip' needing an independent co-sign, but a genuine all-`absent` per-smell verdict on a prose diff is a COMPLETED pass the rail accepts without a `rail_exception`. The skip framing invites a false rail_exception.
- grounding: .agent-work/118-durable-root/g2-review-result.md workflow note (g2 reviewer took the completed-pass reading rather than logging a skip)
- bank-reason: One reviewer flagged it this run. Re-observe whether docs-only review gates routinely hit the Fowler skip-vs-complete ambiguity; a second occurrence justifies minting an explicit 'docs-only Fowler pass' clause in the reviewer skill rather than each reviewer improvising the reading.
- target: constellation-reviewer skill (Fowler/smell-pass section)
- mentions: 1
- confirmed: 0
- disconfirmed: 0
- status: active
- added: 2026-07-19 (118-durable-root)
- last-confirmed: none
- runs-since-confirmed: 1
