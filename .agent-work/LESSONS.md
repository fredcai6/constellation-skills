# Lessons Inbox

<!-- playbook-state: run-tick=43 dormancy-runs=10 apply-recurrences=1 apply-confirmed=3 ticked-work-ids=issue-87,issue-99,issue-103,issue-106,issue-142,issue-140,issue-141,issue-143,issue-145,epic-138-audit,epic-178,epic-198-burndown,epic-226-lessons-audit,governor-261,governor-269,governor-268,governor-265,303,299,issue-309,issue-308,issue-307,issue-310,governor-262,issue-419-governor-identity,issue-422-wire-invariants -->

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
- mentions: 2
- confirmed: 0
- disconfirmed: 0
- recurrences: 1
- status: exported
- added: 2026-08-02 (issue-310)
- last-confirmed: 2026-08-05 (issue-419-governor-identity)
- runs-since-confirmed: 1
- history: recurred 2026-08-05 (issue-419-governor-identity) (constellation debt, not trust) — .agent-work/issue-419-governor-identity/CRITIC_TRIAGE.md finding 2 - 'Every machine-checkable postcondition in the plan is already green, at HEAD, with zero code written': all three command postconditions I authored were re-runs of the green baseline dressed as verification of a change. A cold critic measured it (140 passed / 1621 passed on the unmodified tree) rather than arguing it. This is the SECOND commander, from the same template, writing checks that cannot fail - which is exactly the discriminator the lesson's own bank-reason named ('If a second commander writes a grep-theatre check from the same template, it is the template'). Corroborated by engine telemetry: the checks were rewritten to name new test node ids at the plan step, before any gate ran on them, so none produced a false green in the journal.
- history: exported 2026-08-05 (issue-419-governor-identity) — .agent-work/CONSTELLATION_FEEDBACK.md 2026-08-05 entry for issue-419-governor-identity - the recurrence is exported with a concrete upstream shape (run every command postcondition against the tree at plan-freeze time and refuse to freeze any that exits 0), because confirming a constellation defect a second time logs debt, not trust.

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
- runs-since-confirmed: 2

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
- runs-since-confirmed: 2

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
- runs-since-confirmed: 2

### lesson:name-scoped-test-filter-gates-are-strong-but-structurally-blind
- scope: constellation
- task-class: testing
- statement: A gate postcondition scoped to a pytest -k name filter makes the gate STRUCTURALLY unable to close on an empty test set -- pytest exits 5 when -k matches nothing, and a non-zero exit fails an engine command check. That is stronger than requiring 'named new tests', which a future editor can weaken by renaming. But the same name-scoping makes the filter BLIND to any behaviour named otherwise, and the blindness is not hypothetical: in this run BOTH gates' only real defects were invisible to their -k filter and were caught solely by the whole-file/whole-suite run (g1's fourth source-resolution site in the test file; g2's entire verify_skill_registered fix, whose only tests live in a different test FILE the gate command never runs). So a -k gate must always be paired with an unfiltered suite check, and the filter's honesty depends on nothing unrelated drifting into matching it.
- grounding: staged-feedback/governor-262/AGENT_FEEDBACK.md 'Lessons applied this run'; execute.json g1-integrate.c1b and g2-integrate.c1b; g1 implementer result (fourth site, -k hook structurally blind, caught only by the whole-file run); g2 reviewer result ('both gate commands are scoped to tests/test_install_constellation.py, so neither can see the verify_skill_registered fix at all'); Admiral verified at base commit b69e6c8 that -k hook and -k 'wire or wiring or detect' each collect 0 of 61, so neither could pass vacuously.
- bank-reason: One run, but two independent confirmations of the blindness within it. Banking rather than promoting because the right REMEDY is not yet clear: it may be 'always pair -k with an unfiltered run' (cheap, what this run did), or 'require the gate to name the test FILE not just the filter', or 'drop -k gates in favour of an evidence artifact listing added test functions'. Re-observe on a gate whose new behaviour spans more than one test file to see which remedy actually catches it.
- mentions: 1
- confirmed: 0
- disconfirmed: 0
- status: active
- added: 2026-08-05 (governor-262)
- last-confirmed: none
- runs-since-confirmed: 1

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
- runs-since-confirmed: 1

### lesson:crew-blocked-on-a-commander-blocked-on-that-crew-has-no-exit
- scope: constellation
- task-class: dispatch-authoring
- statement: The escalation model assumes the tier above is available to answer. It has no exit for the case where a crew needs a ruling from a Commander who is at that moment idle WAITING ON THAT CREW'S RESULT -- a genuine deadlock, not an unresponsive principal. In this run the g2 implementer hit exactly that, escalated twice, then used the engine's amend --op retext-check to align its own mis-authored check text with what the handoff actually required, and left one auditable entry rather than fabricating authority or abandoning. That was the right call, but it was judgement filling a structural gap. Either the handoff should pre-authorize a bounded self-amendment class, or the engine needs a way for a crew to hand a decision back without the Commander having already returned.
- grounding: staged-feedback/governor-262/AGENT_FEEDBACK.md 'Crew self-amendment, ratified'; g2-implement result and its plan's amendments array (one retext-check entry); the crew's own two escalation messages naming the deadlock explicitly before it acted.
- bank-reason: First observation of this specific deadlock shape in the fleet, and the crew's improvised exit happened to be sound. Needs re-observation to tell whether the right fix is a pre-authorized self-amendment class in the handoff template, an engine affordance, or simply better guidance -- and to see what a crew with WORSE judgement does in the same corner, which is the case that actually matters.
- mentions: 1
- confirmed: 0
- disconfirmed: 0
- status: active
- added: 2026-08-05 (governor-262)
- last-confirmed: none
- runs-since-confirmed: 1

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
- runs-since-confirmed: 1