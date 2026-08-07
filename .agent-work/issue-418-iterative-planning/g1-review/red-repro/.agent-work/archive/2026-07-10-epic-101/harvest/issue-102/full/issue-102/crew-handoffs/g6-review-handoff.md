# Reviewer Handoff

## Gate
g6-review (issue #102, Moves 9, 10)

## Survey State Location
`.agent-work/issue-102/g6-review/review.json`.

## What Was Implemented
- Move 9 (dedup-sibling-ids): admiral/SKILL.md harvest substep 4 trimmed from a full inline restatement
  to an operative reminder (sibling ids for same defect = confirm/amend not new add) + slug pointer to
  the lessons-auditor home; lessons-auditor/SKILL.md (the home) untouched.
- Move 10 (design-it-twice): reported SUBSUMED by prior #99 — commander:97 and explorer:63 are already
  pointers to the canonical _shared home; explorer:62 is explorer's own excursion-type mechanic (kept).
  No edit made for move 10.
Only `skills/admiral/SKILL.md` changed. IMPLEMENTER_RESULT:
`.agent-work/issue-102/crew-handoffs/g6-implement-result.md`.

## How to Inspect the Diff
UNCOMMITTED working tree: `cd C:/Programs/constellation-wt-102 && git status --porcelain && git diff`.
Expect exactly 1 modified file: skills/admiral/SKILL.md.

## Task Statement
Move 9: single-home sibling-ids at lessons-auditor, admiral trimmed to reminder + pointer (not
stranded). Move 10: design-it-twice restatements → pointer lines (or confirm subsumed by #99).

## Close Criteria (per-move)
- **Move 9:** admiral keeps the OPERATIVE rule inline (harvest still self-sufficient — NOT a bare
  pointer) plus a pointer to the lessons-auditor home; the full rationale (forks-identity / recurrence
  counting / export fingerprint) no longer fully restated in admiral. lessons-auditor:22 still carries
  the full rule once. No meaning lost from harvest usage.
- **Move 10:** independently confirm the subsumption claim — grep commander + explorer for design-it-twice
  and verify they are pointers to the canonical home (global-orchestrator §Design-it-twice +
  design-it-twice-brief), NOT doctrine restatements; explorer's excursion-type description is kept; the
  canonical text is untouched (`git status --porcelain skills/_shared/` empty).
- No new global-*.md; only admiral/SKILL.md changed; full suite green (`py -m pytest tests/ -q`).

## Allowed Scope
Review only; admiral/SKILL.md diff + read commander/explorer/lessons-auditor/_shared to confirm claims.

## Specific Exclusions
Other gates' doctrine. Flag if the diff touches anything but admiral/SKILL.md.

## Constraints the Implementation Must Respect
- Admiral not stranded (operative sentence stays inline); canonical design-it-twice untouched;
  lessons-auditor remains the single full home.
- Honest-null clause: reporting move 10 subsumed-by-#99 is a complete deliverable — do NOT BLOCK for
  "no move-10 edit" if the carriers are genuinely already pointers.

## Evidence Produced
IMPLEMENTER_RESULT has before/after grep for admiral, subsumption grep for move 10, canonical-untouched
confirmation, suite tail (442 passed). Evidence targets `g6-integrate.c1`. Reproduce them.

## Suggested Model Tier
simple-to-stronger — small diff; the judgment is (a) admiral not stranded, (b) move-10 subsumption real.

## Stop Conditions
BLOCK if: admiral was stranded (operative rule removed) OR still fully restates the rationale; the
canonical design-it-twice or lessons-auditor home was altered; a genuine design-it-twice doctrine
restatement was left un-cut in commander/explorer; a file other than admiral/SKILL.md changed; suite red.

## Return Format
Return REVIEW_RESULT (write to `.agent-work/issue-102/crew-handoffs/g6-review-result.md` AND as your
final message): verdict (APPROVE or BLOCK), per-move findings, blockers, out-of-scope observations,
workflow feedback. Your FINAL MESSAGE must be the complete REVIEW_RESULT.
