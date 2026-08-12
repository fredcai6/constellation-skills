# Lessons Playbook

<!-- playbook-state: run-tick=1 cap=20 dormancy-runs=10 apply-recurrences=1 apply-confirmed=3 ticked-work-ids=157-drill -->

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
