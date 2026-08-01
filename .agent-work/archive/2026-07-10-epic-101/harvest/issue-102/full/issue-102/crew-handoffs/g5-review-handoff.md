# Reviewer Handoff

## Gate
g5-review (issue #102, Moves 6, 7 — two orchestrator rules into global-orchestrator.md)

## Survey State Location
`.agent-work/issue-102/g5-review/review.json`.

## What Was Implemented
Two orchestrator-tier doctrines consolidated into `skills/_shared/global-orchestrator.md`:
- Move 6 unchanged-tree shortcut: shared evidence contract moved from commander + admiral SKILL.md;
  commander keeps its "does not change engine postcondition execution" tail, admiral keeps its
  wave-batching tail. Carrier bold headings renamed off the signature phrase.
- Move 7 idle-subagent adjudication: shared rule moved from commander + admiral SKILL.md;
  admiral/references/fleet-doctrine.md reduced to its epic-specific "Adjudication invariants" bite +
  pointer.
IMPLEMENTER_RESULT: `.agent-work/issue-102/crew-handoffs/g5-implement-result.md`.

## How to Inspect the Diff
UNCOMMITTED working tree: `cd C:/Programs/constellation-wt-102 && git status --porcelain && git diff`.
Expect exactly 4 modified files: global-orchestrator.md + commander, admiral SKILL.md + admiral/references/fleet-doctrine.md.

## Task Statement
Consolidate the two orchestrator rules to global-orchestrator with per-move grep evidence; keep
role-specific tails; fleet-doctrine keeps only epic delta.

## Close Criteria (per-move)
- **Move 6:** unchanged-tree evidence contract (HEAD-hash match AND clean porcelain AND pasted prior
  green; any change voids) reads once in global-orchestrator; commander + admiral are pointers + genuine
  tails; no meaning dropped.
- **Move 7:** idle-subagent rule (idle+complete artifacts = done; judge from artifact set; judges
  verdict not liveness — confirm dead before reuse) reads once; commander + admiral pointers + tails;
  fleet-doctrine keeps ONLY its epic bite + pointer (does not restate the full shared rule).
- No new global-*.md; only the 4 expected files changed; commander/admiral changed ONLY at the
  unchanged-tree + crew-idle passages (other passages byte-identical — diff to confirm).
- Full suite green: `py -m pytest tests/ -q`.

## Allowed Scope
Review only; the 4 files above.

## Specific Exclusions
Other gates' doctrine in commander/admiral (delegate-not-replacement, world-verification, sibling-ids,
design-it-twice). If changed here, BLOCK. The admiral "dies or stalls / inspect worktree" RECOVERY
doctrine shares the idle bullet — confirm only the idle sentences moved, recovery doctrine intact.

## Constraints the Implementation Must Respect
- Append into existing global-orchestrator.md only; each carrier keeps a pointer + genuine tail.
- fleet-doctrine keeps epic delta only.

## Evidence Produced
IMPLEMENTER_RESULT has two grep pairs + canonical/pointer quotes + suite tail (442 passed). Evidence
targets `g5-integrate.c1`. Reproduce greps + suite; diff commander/admiral for scope.

## Suggested Model Tier
stronger — two orchestrator reconciles; verify no meaning dropped and fleet-doctrine kept epic-only.

## Stop Conditions
BLOCK if: a move dropped meaning; fleet-doctrine restated the full rule or lost its epic delta;
commander/admiral changed outside the two passages or lost recovery doctrine; new global-*.md; suite red.

## Return Format
Return REVIEW_RESULT (write to `.agent-work/issue-102/crew-handoffs/g5-review-result.md` AND as your
final message): verdict (APPROVE or BLOCK), per-move findings, blockers, out-of-scope observations,
workflow feedback. Your FINAL MESSAGE must be the complete REVIEW_RESULT.
