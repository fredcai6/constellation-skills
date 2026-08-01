# Reviewer Handoff

## Gate
g3-review (issue #102, Move 3 — banner deletion)

## Survey State Location
`.agent-work/issue-102/g3-review/review.json`.

## What Was Implemented
The `**FOLLOW THIS SKILL STRICTLY. USE THE ENGINE RIGOROUSLY**` banner was deleted outright from 6
carriers (charter, commander, explorer, implementer, interrogator, reviewer), leftover blank lines
tidied. IMPLEMENTER_RESULT: `.agent-work/issue-102/crew-handoffs/g3-implement-result.md`.

## How to Inspect the Diff
UNCOMMITTED working tree (prior moves committed): `cd C:/Programs/constellation-wt-102 && git status --porcelain && git diff`.

## Task Statement
Delete the 6 banner lines outright; remove nothing else; keep suite green.

## Close Criteria
- `grep -rn "FOLLOW THIS SKILL STRICTLY" skills/*/SKILL.md` → no output (0 in all 6).
- Exactly the banner line removed per file — no adjacent mechanism-backed prose deleted (inspect each of the 6 diffs; each hunk should be the banner line + at most one collapsed blank).
- No file outside the 6 touched; `git status --porcelain` shows exactly 6 modified files.
- Full suite green: `py -m pytest tests/ -q`.

## Allowed Scope
The 6 SKILL.md only.

## Specific Exclusions
Move-1 compliance pointers, other prose, prototyper, hygiene files (#105). Flag if touched.

## Constraints the Implementation Must Respect
- Delete only the banner line; preserve all adjacent content.

## Evidence Produced
IMPLEMENTER_RESULT has before/after grep (6→0) + suite tail (442 passed). Evidence targets
`g3-integrate.c1`. Reproduce the grep + suite; also eyeball each of the 6 diff hunks.

## Suggested Model Tier
simple bounded — mechanical; the check is that ONLY the banner was removed.

## Stop Conditions
BLOCK if: any banner remains, any adjacent content was removed, a 7th file was touched, or suite red.

## Return Format
Return REVIEW_RESULT (write to `.agent-work/issue-102/crew-handoffs/g3-review-result.md` AND as your
final message): verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations,
workflow feedback. Your FINAL MESSAGE must be the complete REVIEW_RESULT.
