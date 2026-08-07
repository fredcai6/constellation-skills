# Reviewer Handoff

Concise fragments. Omit filler.

## Gate
`g4` — Cross-file history sweep

## Survey State Location
`.agent-work/issue-103/g4-review/review.json`.

## What Was Implemented
Three surgical detemporalizations: `skills/explorer/SKILL.md` (design-it-twice "is now a tier-wide standard, not an explorer-only move" → timeless), `skills/charter/references/rigorous-default.md` (posture "is now inherited runtime doctrine, not a Charter-only reference" → timeless), `skills/workbench/templates/WORKFLOW_CLOSEOUT.template.md` ("are now lessons … not a separate advisory table" → timeless). See handoff + result under `.agent-work/issue-103/crew-handoffs/g4-implement-*`.

## How to Inspect the Diff
Review target = UNCOMMITTED working tree in `C:\Programs\constellation-wt-103`. `git status --porcelain` then `git --no-pager diff skills/explorer/ skills/charter/ skills/workbench/`.

## Task Statement
Remove "is now / are now … not …-only" temporal framing from three lines, meaning-preserving, pointers intact; nothing else swept.

## Close Criteria (each a review check)
- Each of the three lines reads as present-tense current truth; the RULE and any pointer are intact (compare against `git show HEAD:<file>`).
- No meaning changed beyond removing the temporal framing.
- Explorer still contains `design-it-twice-brief.md` and `global-orchestrator.md`.
- Exactly the three files changed; no extra lines swept.
- Full suite green: `py -m pytest tests/ -q` (expect 444 passed, 2 skipped — same as baseline).

## Allowed Scope
`skills/explorer/SKILL.md`, `skills/charter/references/rigorous-default.md`, `skills/workbench/templates/WORKFLOW_CLOSEOUT.template.md`.

## Specific Exclusions
No other file (commander, admiral, docent, interrogator, _shared, tests, ROADMAP) may be changed by this gate.

## Constraints the Implementation Must Respect
Meaning-preserving; pointers survive; no unrelated reflow.

## Evidence Produced
IMPLEMENTER_RESULT: diff --stat = 3 files, 5 ins/5 del; forbidden grep empty; explorer pointers present; suite `444 passed, 2 skipped`. Reproduce each. Attach verdict to `g4-review.c1`.

## Suggested Model Tier
`simple bounded — three-line detemporalization check`

## Stop Conditions
BLOCK if: meaning changed, a pointer lost, extra lines swept, an out-of-scope file changed, or the suite reds.

## Return Format
Return REVIEW_RESULT (write to `.agent-work/issue-103/crew-handoffs/g4-review-result.md` AND final message before idling): verdict APPROVE or BLOCK on its own line, per-check findings with reproduced evidence, blockers, out-of-scope observations, workflow feedback.
