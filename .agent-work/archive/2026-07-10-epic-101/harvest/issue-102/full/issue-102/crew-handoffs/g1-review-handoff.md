# Reviewer Handoff

Concise fragments.

## Gate
g1-review (issue #102, Move 1)

## Survey State Location
`.agent-work/issue-102/g1-review/review.json` (under the issue workbench, not worktree root).

## What Was Implemented
The mandatory-compliance / engine-drive boilerplate was single-sourced into a new
`## Engine-drive compliance` subsection of `skills/_shared/global-everyone.md`; the inline
paragraph in 10 carriers (admiral, cartographer, charter, commander, implementer, interrogator,
lessons-auditor, reviewer, scout, workbench) was replaced by a one-line pointer, with role-specific
tails kept only where genuinely role-specific. IMPLEMENTER_RESULT:
`.agent-work/issue-102/crew-handoffs/g1-implement-result.md`.

## How to Inspect the Diff
Review the UNCOMMITTED working tree in this worktree (NOT `git diff main...HEAD`):
`cd C:/Programs/constellation-wt-102 && git status --porcelain && git diff`.

## Task Statement
Move 1: consolidate the compliance boilerplate to global-everyone.md; carriers keep a pointer; no
new global-*.md filename; drift reconciled into one canonical wording.

## Close Criteria
- Canonical rule reads cleanly ONCE in global-everyone.md, dense agent-facing register, generalized
  over spine/checklist/survey; meaning not weakened.
- All 10 carriers reduced to a pointer naming references/global-everyone.md; no residual full copy.
- No new global-*.md filename; appended into the existing file.
- Before/after carrier-count grep reproduces (before=10 inline, after=0 inline / 10 pointers / 1 canonical).
- Full suite green: `py -m pytest tests/ -q`.

## Allowed Scope
skills/_shared/global-everyone.md + the 10 carrier SKILL.md only.

## Specific Exclusions
FOLLOW-THIS-SKILL-STRICTLY banners (g3), prototyper, engine-invocation operational string (g2),
manifest.json / ROADMAP / repo-root stray (issue #105). If the diff touches any, flag it.

## Constraints the Implementation Must Respect
- Append into existing global-everyone.md only; each carrier keeps a pointer.
- Register: dense, agent-facing; emphasis only at mechanism-backed gates (canonical is un-bolded).
- Reconcile-then-cut: the canonical must not drop meaning any carrier's copy carried.

## Map Anchors (inbound)
- Structural: global-everyone.md + 10 carriers; install_constellation.py:94-113 bundle.
- Constraints: test_install_constellation.py:196-208 glob stays green.
- Decision: cross-tier compliance rule -> global-everyone.

## Evidence Produced
IMPLEMENTER_RESULT has drift-robust before/after grep + canonical/pointer quotes + suite tail
(442 passed, 2 skipped). Reproduce the grep and the suite yourself. Evidence targets postcondition
`g1-integrate.c1`.

## Suggested Model Tier
stronger — register-sensitive product prose.

## Stop Conditions
BLOCK if: a carrier retains the full paragraph; the canonical drops meaning; a new global-*.md
appears; the suite is red; or scope was exceeded.

## Return Format
Return REVIEW_RESULT (write to `.agent-work/issue-102/crew-handoffs/g1-review-result.md` AND as your
final message): verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations,
workflow feedback. Your FINAL MESSAGE must be the complete REVIEW_RESULT before you idle.
