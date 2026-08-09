# Lessons Inbox

<!-- playbook-state: run-tick=44 dormancy-runs=10 apply-recurrences=1 apply-confirmed=3 ticked-work-ids=issue-87,issue-99,issue-103,issue-106,issue-142,issue-140,issue-141,issue-143,issue-145,epic-138-audit,epic-178,epic-198-burndown,epic-226-lessons-audit,governor-261,governor-269,governor-268,governor-265,303,299,issue-309,issue-308,issue-307,issue-310,issue-419-governor-identity,issue-422-wire-invariants,issue-456 -->

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
- mentions: 3
- confirmed: 0
- disconfirmed: 0
- recurrences: 2
- status: exported
- added: 2026-08-02 (issue-310)
- last-confirmed: 2026-08-09 (issue-456)
- runs-since-confirmed: 1
- history: recurred 2026-08-05 (issue-419-governor-identity) (constellation debt, not trust) — .agent-work/issue-419-governor-identity/CRITIC_TRIAGE.md finding 2 - 'Every machine-checkable postcondition in the plan is already green, at HEAD, with zero code written': all three command postconditions I authored were re-runs of the green baseline dressed as verification of a change. A cold critic measured it (140 passed / 1621 passed on the unmodified tree) rather than arguing it. This is the SECOND commander, from the same template, writing checks that cannot fail - which is exactly the discriminator the lesson's own bank-reason named ('If a second commander writes a grep-theatre check from the same template, it is the template'). Corroborated by engine telemetry: the checks were rewritten to name new test node ids at the plan step, before any gate ran on them, so none produced a false green in the journal.
- history: exported 2026-08-05 (issue-419-governor-identity) — .agent-work/CONSTELLATION_FEEDBACK.md 2026-08-05 entry for issue-419-governor-identity - the recurrence is exported with a concrete upstream shape (run every command postcondition against the tree at plan-freeze time and refuse to freeze any that exits 0), because confirming a constellation defect a second time logs debt, not trust.
- history: recurred 2026-08-09 (issue-456) (constellation debt, not trust) — .agent-work/AGENT_FEEDBACK.md 2026-08-09 issue-456-code-map entry - 'Re-running the criterion instead of reading the report found six checks that could not fail.' This is the THIRD commander to produce them from the same template, which is past the discriminator the lesson's own bank-reason named. Six instances, all measured rather than argued: g5-integrate c1 selected -k 'caller_split', a name no test in this repo has ever carried (zero collected); gs-integrate c1 selected -k 'map_tree_freshness' at a gate where that test did not yet exist (zero collected, so the criterion could only ever exit 5); g6's negative tests stayed green under whole-feature disable; g7's staleness test fired off the wrong mechanism; g8 pass 4's invariant test was gated behind the condition it asserts. Corroborated by engine telemetry: g5 and g8 each took remediation rounds against reviewer BLOCK verdicts, and no unfailable check produced a false green in the journal because each was caught by re-running the criterion at the gate boundary rather than accepting the crew's report. NEW and worse than prior instances: tc4 sat in the FROZEN PLAN's own postcondition rather than in a crew's work, where no reviewer looks. The mirror form also appeared - a close criterion that could never PASS (git diff d102c05 -- skills/, unsatisfiable once later gates legitimately moved other files there), caught by the implementer rather than by me. Filed upstream as #518 with the concrete mechanical shape the prior export named: run --collect-only on every pytest -k postcondition at plan freeze and refuse a zero-collecting selector, which would have killed two of the six before their gate opened.
- history: exported 2026-08-09 (issue-456) — .agent-work/CONSTELLATION_FEEDBACK.md 2026-08-09 entry for issue-456-code-map, carrying the originating lesson id - 'third recurrence of the vacuous-check family, and the first with a mechanical fix that is cheap enough to just ship'. Exported rather than confirmed again because confirming a constellation defect a third time logs debt, not trust. The export carries two things the prior #419 export did not: (1) the family's MIRROR form, a criterion that can never PASS, shipped this run as an unsatisfiable git diff check and caught by the implementer rather than the commander; (2) the upstream shape is now a filed issue, #518, rather than a recommendation - run pytest --collect-only on every -k postcondition at plan freeze and refuse a zero-collecting selector, which would have killed two of this run's six instances before their gate opened.

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
- runs-since-confirmed: 3

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
- runs-since-confirmed: 3

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
- runs-since-confirmed: 3

### lesson:enumerate-the-sites-by-command-before-editing-a-claim
- scope: constellation
- task-class: gate-authoring
- statement: When a change falsifies a stated claim, the handoff must require enumerating every site asserting that claim BY COMMAND, with the count stated, before any edit. A handoff that names the site to fix produces a fix at that site and leaves the others, and each later pass finds sites the previous one reported clean.
- grounding: .agent-work/issue-419-governor-identity/results/g3-REVIEW_RESULT.md and g3-IMPLEMENTER_RESULT.md - one claim ('the gauge record is four fields') was asserted at SEVEN sites across four files. The handoff named one; the first review found two and BLOCKed; the rework's by-command enumeration found six; the re-review found a seventh in a fourth file nobody had swept. Each pass had reported the previous state clean.
- bank-reason: Re-observation will tell whether the fix belongs in the handoff template (an explicit enumerate-then-edit step) or in the author's habit. This run cannot separate them: I wrote the under-inclusive handoff AND the enumeration that repaired it, so the same person supplied both the defect and the remedy. If a different commander's handoff names a single site for a claim that turns out to be repeated, it is the template.
- mentions: 1
- confirmed: 0
- disconfirmed: 0
- status: active
- added: 2026-08-05 (issue-419-governor-identity)
- last-confirmed: none
- runs-since-confirmed: 2

### lesson:archive-the-producer-with-the-output
- scope: constellation
- task-class: evidence
- statement: An archived output that cannot be regenerated from its archived producer is testimony, not evidence. Archive the command or script alongside its output, and treat a non-reproducing artifact as a defect even when every number in it independently checks out.
- grounding: .agent-work/issue-419-governor-identity/results/g4-REVIEW_RESULT.md - evidence/g4-assert-control-output.txt does not regenerate from its own archived script: a trailing section was appended from a command that was not recorded. Every number in it reproduced independently when the reviewer re-derived them, so no claim rested on it - which is precisely why nobody would have caught it without a reviewer who tried to regenerate the file rather than read it.
- bank-reason: Needs re-observation to know whether this is worth a mechanical check or stays a habit. Here it was caught only because one reviewer chose to regenerate an artifact instead of reading it, which is not something any current gate asks for. If it recurs where the numbers do NOT reproduce, the cost is a wrong claim surviving review and the case for mechanizing it gets much stronger.
- mentions: 1
- confirmed: 0
- disconfirmed: 0
- status: active
- added: 2026-08-05 (issue-419-governor-identity)
- last-confirmed: none
- runs-since-confirmed: 2

### lesson:specifying-the-case-invites-a-fix-to-the-case
- scope: constellation
- task-class: crew-dispatch
- statement: A remediation brief that names the failing case gets a fix to that case, leaving the same defect standing everywhere else. Name the defect CLASS and the shape that produces it; if you can only name an instance, say explicitly that the instance is an example and the class is the target.
- grounding: .agent-work/AGENT_FEEDBACK.md 2026-08-09 issue-456-code-map entry - 'Three consecutive g8 remediations each fixed exactly what its brief named and left the same defect standing elsewhere - and in all three the narrowing was mine.' Corroborated by engine telemetry: g8 required five passes and three separate remediate/re-review cycles, each closing on the named case and each followed by a reviewer BLOCK finding the same defect at a site the brief had not named. The sequence is worth keeping because every step looked reasonable in isolation: the first brief named a defect the reference material never defined, so the crew fixed the one instance it could identify; each subsequent brief narrowed further in an attempt to be unambiguous. The rule that finally closed it came from the shape rather than the case - branch on the SHAPE, which is fixed and known when the case is written, never on the MEASURED output, which is the thing under test.
- bank-reason: Re-observation will tell whether this is my authoring habit or the IMPLEMENTER_HANDOFF template inviting it. The template asks for close criteria that are unambiguous and mechanically checkable, and the cheapest way to satisfy that is to name a literal instance - so the pressure toward case-shaped briefs may be structural rather than personal. n=1 commander cannot separate those. If a different commander produces the same narrow-brief-then-same-defect-elsewhere sequence from the same template, it is the template, and the fix is a template field that forces the class to be stated separately from the example. Related evidence to watch for on the code side: #522 filed this run is the same disease in test form - a pin test guarding the literal wording of the bug rather than the class, which four reworded variants walked straight past.
- mentions: 1
- confirmed: 0
- disconfirmed: 0
- status: active
- added: 2026-08-09 (issue-456)
- last-confirmed: none
- runs-since-confirmed: 1
