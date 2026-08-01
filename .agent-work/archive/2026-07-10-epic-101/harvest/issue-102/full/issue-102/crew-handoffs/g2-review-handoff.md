# Reviewer Handoff

Concise fragments.

## Gate
g2-review (issue #102, Move 2 — engine-invocation string; outcome: subsumed-by-move-1 + narrow pointer edit)

## Survey State Location
`.agent-work/issue-102/g2-review/review.json`.

## What Was Implemented
The implementer determined Move 2's generic engine-invocation clause was already single-sourced by
Move 1 (it rode along with the compliance paragraph into global-everyone.md §"Engine-drive
compliance"). The residual grep found no generic duplicate — every remaining "through the engine one
step at a time" hit is a role-specific spine instruction (names that role's own template) or the
canonical workbench source. The only gap: global-everyone did not point at the canonical engine
MECHANISM. The implementer added a one-clause pointer to `references/checklist-engine.md`.
IMPLEMENTER_RESULT: `.agent-work/issue-102/crew-handoffs/g2-implement-result.md`.

## How to Inspect the Diff
UNCOMMITTED working tree (Move 1 is already committed at 55d2378; inspect only the NEW change):
`cd C:/Programs/constellation-wt-102 && git status --porcelain && git diff`.

## Task Statement
Move 2: single-source the generic engine-invocation string / point at checklist-engine.md for the
mechanism; keep role-specific spine instructions local; report honestly if subsumed by Move 1.

## Close Criteria
- The subsumption finding is CORRECT: reproduce the grep and confirm no generic (role-agnostic)
  engine-invocation duplicate remains outside role-specific/canonical contexts.
- global-everyone.md now points at checklist-engine.md for the engine mechanism EXACTLY once; no new
  global-*.md filename; mechanism content not duplicated.
- Role-specific spine instructions (commander:30 COMMANDER_SPINE 10-step, explorer:33 EXPLORER_SPINE,
  workbench:39 canonical driver) are preserved in substance — NOT force-merged.
- Full suite green: `py -m pytest tests/ -q`.

## Allowed Scope
Only the new diff: skills/_shared/global-everyone.md (+ any carrier the implementer touched — expect none).

## Specific Exclusions
Banners (g3), prototyper, hygiene files (#105), move-1 carriers (done). Flag if the diff touches them.

## Constraints the Implementation Must Respect
- Append into existing global-everyone.md only; no new global-*.md.
- Point at checklist-engine.md, don't duplicate its mechanism content.
- Preserve role-specific workflow content (honest-null clause: reporting subsumption is complete, not a failure — do NOT BLOCK merely because the consolidation was narrow).

## Map Anchors (inbound)
- Structural: global-everyone.md; workbench/references/checklist-engine.md; commander/explorer SKILL.md.
- Decision: generic engine-invocation -> global-everyone; mechanism stays in checklist-engine.md.

## Evidence Produced
IMPLEMENTER_RESULT carries the classified grep + added-pointer quote + suite tail (442 passed).
Evidence targets postcondition `g2-integrate.c1`. Reproduce the grep + suite yourself.

## Suggested Model Tier
simple-to-stronger — small diff, but confirm the reconcile judgment (subsumption + no role-specific loss).

## Stop Conditions
BLOCK only if: a genuine generic duplicate was actually left un-consolidated; role-specific content was
deleted; a new global-*.md appeared; or the suite is red. Do NOT BLOCK on the narrowness of the move.

## Return Format
Return REVIEW_RESULT (write to `.agent-work/issue-102/crew-handoffs/g2-review-result.md` AND as your
final message): verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations,
workflow feedback. Your FINAL MESSAGE must be the complete REVIEW_RESULT.
