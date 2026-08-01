# Agent Feedback

Unified, cross-run workflow retrospective. Appended before archive; persists across work-ids; never archived with a work-id. Staged worktree-local this run (under-epic; Admiral harvests at closeout — canonical main-checkout write is forbidden mid-epic).

## 2026-07-10 — issue-107 (commander entry-split + diet, delegated under epic-101)

**Followed well:** Full commander spine driven through the engine end to end (init→archive), all four delegated `user-decision` checkpoints satisfied by launch-order citation. Doc gates run as reasoning gates with inspection-attestation (grep + command-derived word counts) per the launch order; the one code gate (delegated skill + install + tests) run as a real implementer+reviewer crew via `run_crew.py --backend external`. Green at every gate boundary (444→446 passed).

**Friction / improvised:**
- **Handoff-authoring collision (cost one rework round-trip).** I authored the delegated SKILL.md body verbatim including the sentence "A delegate is not a replacement", which is a retired inline signature the issue-102 move-8 residual test forbids in any SKILL.md body — and which the launch order itself bound me not to reintroduce. The implementer correctly BLOCKED and floated it rather than force-fixing or amending the guard. Adjudicated: reword to the single-source pointer form (hyphenated `delegate-not-replacement` + `see references/global-everyone.md`), NOT a test carve-out (a carve-out would legitimize the very residual the epic is eliminating). **Lesson:** when authoring verbatim SKILL.md prose in a handoff, dry-run it against the residual-guard grep (`grep -rn "<retired sigs>" skills/**/SKILL.md`) BEFORE dispatch. The retired-signature list lives in `test_relocated_doctrine_leaves_no_residual_in_carrier_skill_md`.
- **Crew resumed but idled before rewriting its result doc.** After I returned the implementer for the reword, it applied the file edit but went idle without rewriting `g2-IMPLEMENTER_RESULT.md` (left stale "blocked" text). Resolved per the idle-crew-at-integrate rule: judged from the completed artifact (the diff) + own world-verification (re-ran the suite green), appended a transparent Commander reconciliation to the result, and integrated. Worked, but a crew that edits then idles mid-report is a recurring external-backend pattern worth a tighter "your FINAL action is rewriting the result doc" nudge.
- **Durable-trio canonical-write tension (recurs every under-epic Commander).** `verify_agent_feedback.py`/`verify_lessons_applied.py` resolve the durable trio to the MAIN checkout via `git-common-dir`, but under-epic launch orders forbid mid-epic canonical writes. Staged AGENT_FEEDBACK worktree-local; feedback.c1/c2 + archive.c1 waived under delegated authority (same as commander-102). Route at Admiral closeout.

**Crew workflow feedback harvested:**
- Implementer: the g2 handoff's "must not leave any test red" + paste-verbatim body were in undetected conflict with the pre-existing residual guard; suggests dry-running verbatim bodies against the guard at handoff-authoring time (adopted as the lesson above). Also noted g1's uncommitted worktree state needed mine-vs-g1 disambiguation in `git status`.
- Reviewer: no blocking finds; handoff was precise; confirmed both new tests bite and the reword is present.

**What would have helped:** the launch order could have flagged that the delegated entry's own doctrine (delegate≠replacement) overlaps a retired signature, pre-naming the pointer-not-paste resolution — it would have saved the round-trip.
