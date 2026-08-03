# Lessons Inbox

<!-- playbook-state: run-tick=41 dormancy-runs=10 apply-recurrences=1 apply-confirmed=3 ticked-work-ids=issue-87,issue-99,issue-103,issue-106,issue-142,issue-140,issue-141,issue-143,issue-145,epic-138-audit,epic-178,epic-198-burndown,epic-226-lessons-audit,governor-261,governor-269,governor-268,governor-265,303,299,issue-309,issue-308 -->

Transitory inbox for between-audit workflow signal — **not** a playbook, and not a
permanent home for any rule. Read the Active section at the Commander context step
and condition planning/handoff authoring on it. Never edit by hand or by LLM: apply
structured deltas via `apply_lessons_delta.py`, which enforces cap, grounding, and
counter rules.

Lessons are **transitory**. An audit *ends* every lesson it reads: the operative
content **graduates** into the permanent doc that owns it — a template, a skill's
doctrine section, a reference file, or a code-fix issue — and the lesson is then
**retired**; a lesson with no durable home is **deleted with a reason**. Nothing an
audit reads stays active. The `retire` op is the deletion path; a graduation is a
paired edit-plus-retire whose retire reason names the destination. Between audits,
new signal may be **added** here as staging, but this file is where lessons pass
through, not where they live.

Counter semantics split by scope: for most scopes a confirm is trust (the lesson
held again). For a constellation-scoped lesson it is the opposite — a recurrence of
an unfixed shared-machinery defect, so it accrues recurrences (debt) and flags
recurrence-debt. Pay the debt by exporting to CONSTELLATION_FEEDBACK and fixing
upstream, then retire it; do not keep confirming it into a permanent workaround.

## Active
