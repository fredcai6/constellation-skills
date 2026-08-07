# Reviewer Handoff

Concise fragments. Omit filler.

## Gate
`g1` — Admiral diet

## Survey State Location
Create your review survey at `.agent-work/issue-103/g1-review/review.json` (under the issue workbench, never worktree root).

## What Was Implemented
Diet of `skills/admiral/SKILL.md` + `skills/admiral/references/fleet-doctrine.md` + one line of `skills/admiral/templates/LATITUDE_CONTRACT.template.md`: dropped "learned from field fleets" heading framing; trimmed two operating-doctrine bullets that duplicated `_shared`/fleet-doctrine down to pointers; rewrote all history/temporal framing as timeless current truth. Meaning-preserving. See the IMPLEMENTER_RESULT at `.agent-work/issue-103/crew-handoffs/g1-implement-result.md` and the handoff `.agent-work/issue-103/crew-handoffs/g1-implement-handoff.md` (items A–N) for the exact intended edits.

## How to Inspect the Diff
Review target = the UNCOMMITTED working tree in this worktree (`C:\Programs\constellation-wt-103`), NOT `git diff main...HEAD`. Use:
`git status --porcelain` then `git --no-pager diff skills/admiral/`.

## Task Statement
Fold/detemporalize per handoff items A–N with fold-vs-cut rulings pre-decided; preserve every operative rule.

## Close Criteria (each a review check)
- **Meaning preserved**: no operative rule dropped. Specifically confirm these critic-flagged MUST-SURVIVE facts are still present:
  1. Bullet "dies or stalls": "verify from the artifact set" AND "clean-room reviewer subagent" AND "confirm it dead before you reuse or sweep" AND both pointers (`global-orchestrator.md` §idle-subagent-adjudication + `fleet-doctrine.md` "Adjudication invariants").
  2. Bullet "Field your Commanders' queries": "you are their reachable tier", query-fielding, the return-and-relaunch vs dead-recovery distinction, out-of-band escalation, and the `delegate-not-replacement` pointer to `global-everyone.md`.
  3. The harvest "mostly-automatic vs manual-fallback" caveat survives in BOTH `SKILL.md` (~closeout item 4) and `fleet-doctrine.md` (~line 118 area).
  4. The compact-step operative caveat survives (compaction best-effort, reload mandatory, a self-`compact` spine still runs it).
- **History framing gone**: "learned from field fleets" heading, "is now engine-enforced", "This is now mechanical", "g1's ... now points", "removed — ... before this change", the "Live grounding: this epic ... issue-54 improvise" war story, and "(this epic)" label are all rewritten/removed.
- **No forbidden signature** in `skills/admiral/SKILL.md`: `Unchanged-tree shortcut`, `idle_notification`, `breaks recurrence counting`, `delegate is not a replacement` (un-hyphenated). Confirm `§unchanged-tree-shortcut` (lowercase) and `delegate-not-replacement` (hyphen) ARE still present.
- **Pointer names present**: `global-everyone.md`, `global-orchestrator.md`, `fleet-doctrine.md`.
- **fleet-doctrine.md:10 provenance** ("Distilled from field fleets (f1brainz epics ...)") is intentionally KEPT (honest-null) — its presence is NOT a defect.
- **Suite green**: `py -m pytest tests/test_install_constellation.py -q`.

## Allowed Scope
The three admiral files only. Flag any other changed file.

## Specific Exclusions
`skills/commander/**`, `_shared/**`, `tests/**`, `docs/ROADMAP.md` must be untouched.

## Constraints the Implementation Must Respect
- Meaning-preserving; deltas kept inline, only genuine duplicates cut to pointers.
- No new `global-*.md` filename.

## Evidence Produced
IMPLEMENTER_RESULT reports: wc SKILL 1410→1405, fleet-doctrine 1630→1541; forbidden grep empty; pointers present; suite `38 passed, 118 subtests passed`. Reproduce each yourself — re-run the greps and the suite; do not trust the report.
Attach your verdict to engine postcondition `g1-review.c1` (this review) — `g1-integrate.c2` matches on it.

## Suggested Model Tier
`stronger — register-sensitive meaning-preservation`

## Stop Conditions
BLOCK if: an operative rule was dropped, a forbidden signature appears, a pointer was severed, an out-of-scope file changed, or the suite reds.

## Return Format
Return REVIEW_RESULT (write it to `.agent-work/issue-103/crew-handoffs/g1-review-result.md` AND make it your final message before idling): verdict (APPROVE or BLOCK), per-check findings with reproduced evidence, blockers, out-of-scope observations, workflow feedback.
