# Reviewer Handoff

## Gate
g4-review (issue #102, Moves 4, 5, 8 — three cross-tier rules into global-everyone.md)

## Survey State Location
`.agent-work/issue-102/g4-review/review.json`.

## What Was Implemented
Three distinct cross-tier doctrines were each consolidated into a new subsection of
`skills/_shared/global-everyone.md`, carriers reduced to pointer + role-specific tail:
- Move 4 scoped-nulls: general principle moved from explorer + prototyper SKILL.md; prototyper's
  spike applications in references/measurement.md + ui.md KEPT LOCAL (partial move).
- Move 5 world-verification: shared principle from commander + reviewer consolidated; each keeps its
  role application as a tail.
- Move 8 delegate-not-replacement: commander + admiral consolidated; deliberately broadened to all
  tiers (ruled).
IMPLEMENTER_RESULT: `.agent-work/issue-102/crew-handoffs/g4-implement-result.md`.

## How to Inspect the Diff
UNCOMMITTED working tree (prior moves committed): `cd C:/Programs/constellation-wt-102 && git status --porcelain && git diff`.
Expect exactly 6 modified files: global-everyone.md + explorer, prototyper, commander, reviewer, admiral SKILL.md.

## Task Statement
Consolidate the three cross-tier rules to global-everyone with per-move grep evidence; keep
role-specific tails; keep prototyper references local (move 4 partial); do not force-merge move 5 if distinct.

## Do this per-move (NOT a rubber-stamp — three independent judgments)
- **Move 4:** general scoped-null principle reads once in global-everyone; explorer + prototyper
  SKILL.md are pointers + genuine tier tails; `git status --porcelain skills/prototyper/references/`
  is EMPTY (measurement.md/ui.md untouched); no scoped-null meaning dropped.
- **Move 5:** confirm the reconcile decision — the shared principle (independent reproduction; judgment
  rests on observation) is in global-everyone once; commander keeps its integrate-freshness tail,
  reviewer keeps its "unreproducible claim = BLOCK" tail. Confirm this was a justified consolidation of
  ONE principle, not a force-merge that dropped a genuinely role-specific rule.
- **Move 8:** delegate-not-replacement reads once; commander + admiral are pointers + their escalation
  tails; the broadening into crew tier is deliberate (ruled), not a defect.

## Close Criteria
- Three canonical subsections present, meaning preserved, dense register.
- Three carrier→0 grep pairs reproduce; global-everyone carries each once.
- prototyper/references/ untouched; no new global-*.md; only the 6 expected files changed; commander
  and admiral changed ONLY at the move-5/move-8 passages (other passages byte-identical).
- Full suite green: `py -m pytest tests/ -q`.

## Allowed Scope
Review only; the 6 files above.

## Specific Exclusions
prototyper/references (must be untouched — flag if changed); other gates' doctrine (design-it-twice,
sibling-ids, unchanged-tree, crew-idle) — if commander/admiral changed there, BLOCK.

## Constraints the Implementation Must Respect
- Append into existing global-everyone.md only; each carrier keeps a pointer + genuine tail.
- Move 4 partial; move 5 no force-merge; move 8 broadening is ruled.

## Evidence Produced
IMPLEMENTER_RESULT has three grep pairs + canonical/pointer quotes + suite tail (442 passed).
Evidence targets `g4-integrate.c1`. Reproduce the greps + suite; diff commander/admiral to confirm
only the two passages moved.

## Suggested Model Tier
stronger — three semantic reconciles; verify no meaning dropped and move 5 not force-merged.

## Stop Conditions
BLOCK if: a move dropped meaning; prototyper references were touched; move 5 force-merged a genuinely
distinct rule; commander/admiral changed outside the two passages; a new global-*.md; or suite red.

## Return Format
Return REVIEW_RESULT (write to `.agent-work/issue-102/crew-handoffs/g4-review-result.md` AND as your
final message): verdict (APPROVE or BLOCK), per-move findings, blockers, out-of-scope observations,
workflow feedback. Your FINAL MESSAGE must be the complete REVIEW_RESULT.
