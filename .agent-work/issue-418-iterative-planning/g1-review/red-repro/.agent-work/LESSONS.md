# Lessons Inbox

<!-- playbook-state: run-tick=42 dormancy-runs=10 apply-recurrences=1 apply-confirmed=3 ticked-work-ids=issue-87,issue-99,issue-103,issue-106,issue-142,issue-140,issue-141,issue-143,issue-145,epic-138-audit,epic-178,epic-198-burndown,epic-226-lessons-audit,governor-261,governor-269,governor-268,governor-265,303,299,issue-309,issue-308,issue-307,issue-310 -->

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

### lesson:falsify-a-check-against-a-decoy-before-trusting-it
- scope: constellation
- task-class: gate-authoring
- statement: A gate postcondition must be run against a deliberately-wrong decoy before it is trusted. A check that cannot fail is worse than no check, because it reports green on the exact condition it exists to catch.
- grounding: .agent-work/issue-310/PLAN_ALTERNATIVES.md - 'Two of the four BLOCKING findings were checks that could not fail, sitting in this run's own gate acceptance criteria.' Corroborated by engine telemetry: both checks were replaced by amend at the plan step (commit c60f0ad) BEFORE any gate ran on them, so neither produced a false green in the journal.
- bank-reason: Re-observation will tell whether this is a per-author habit or a template gap. Both instances here were keyword greps standing in for a semantic property, which suggests the template's command-postcondition examples invite grep-shaped checks -- but n=1 run cannot separate that from one commander's authoring style. If a second commander writes a grep-theatre check from the same template, it is the template.
- mentions: 1
- confirmed: 0
- disconfirmed: 0
- status: active
- added: 2026-08-02 (issue-310)
- last-confirmed: none
- runs-since-confirmed: 1

### lesson:a-verdict-must-not-select-on-the-gap-it-escalates
- scope: constellation
- task-class: general-workflow
- statement: When a run escalates a missing input (a threshold, a unit, an authority) it must not then select its own outcome using that same missing input. Re-found the conclusion on a leg that does not need it; do not patch the wording.
- grounding: .agent-work/issue-310/B2_GATE_EVIDENCE.md section 7 - 'Row R3 is deliberately NOT invoked. It would have fired the outcome on a size judgement, which is a threshold denominated in words, i.e. exactly the two choices section 5 says nobody has made.' Found by an independent cold reader, not by the author.
- bank-reason: Needs re-observation to know whether this generalises beyond measurement runs. Here the escalated gap (threshold+unit) and the selection basis (a percentage) were the same kind of thing, which made the circularity visible; where the gap and the basis differ in kind it may be much harder to see, and I do not yet know what the tell would be.
- mentions: 1
- confirmed: 0
- disconfirmed: 0
- status: active
- added: 2026-08-02 (issue-310)
- last-confirmed: none
- runs-since-confirmed: 1

### lesson:grading-a-contested-claim-settled-launders-it
- scope: constellation
- task-class: general-workflow
- statement: A decision anchor's @grade must reflect how contested the claim is, not how confident the author feels. Grading a contested structural claim 'settled' is the precise laundering the grading mechanism exists to prevent.
- grounding: .agent-work/issue-310/MISSION_FRAME.md decision 3 - graded 'settled/structural', regraded 'guess/structural' after a cold critic showed an ablation arm needs zero authoring. Engine telemetry: the claim survived understand and plan ungainsaid; only the cold-critic dispatch surfaced it.
- bank-reason: Bank rather than apply: the failure was mine, not the doctrine's -- global-everyone.md already defines the tiers correctly. Re-observation will show whether authors systematically over-grade their own load-bearing assumptions, which would be a mechanism gap (nothing challenges a grade) rather than a comprehension gap.
- mentions: 1
- confirmed: 0
- disconfirmed: 0
- status: active
- added: 2026-08-02 (issue-310)
- last-confirmed: none
- runs-since-confirmed: 1

### lesson:reasoning-gate-crew-waiver-can-be-wrong-for-synthesis
- scope: constellation
- task-class: dispatch-authoring
- statement: commander-core's 'a crew on a pure design note is shallower, not safer' held for the measurement gate but was wrong for the verdict gate: this run's only real failure mode was in synthesis, and one cold reader with a single-question brief found it.
- grounding: .agent-work/issue-310/PLAN_ALTERNATIVES.md M5 disposition; the cold reader's finding forced a re-founding of the verdict rather than an edit.
- bank-reason: Bank rather than apply: commander-core is right that a crew on a design note is usually shallower, and one counter-instance does not overturn it. Re-observation will show whether the exception is specifically SYNTHESIS gates -- gates whose deliverable combines prior gates rather than producing something new -- or whether it is broader than that.
- mentions: 1
- confirmed: 0
- disconfirmed: 0
- status: active
- added: 2026-08-02 (issue-310)
- last-confirmed: none
- runs-since-confirmed: 1
