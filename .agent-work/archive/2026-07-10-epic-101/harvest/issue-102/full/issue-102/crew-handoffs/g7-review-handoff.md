# Reviewer Handoff

## Gate
g7-review (issue #102, Move 11 — regression net)

## Survey State Location
`.agent-work/issue-102/g7-review/review.json`.

## What Was Implemented
Two tests added to `tests/test_install_constellation.py`:
- `test_relocated_doctrine_pins_ship_to_installed_destination` — content-pin per moved doctrine
  (moves 1,2,4,5,8 on any installed skill's bundled global-everyone.md; 6,7 on commander's bundled
  global-orchestrator.md; move 9 on lessons-auditor's SKILL.md; move-10 canonical "Design-it-twice"
  on commander's global-orchestrator.md).
- `test_relocated_doctrine_leaves_no_residual_in_carrier_skill_md` — reads source `skills/**/SKILL.md`
  only (excludes all references/), asserts each retired signature absent; move-9 residual
  ("breaks recurrence counting") scoped to admiral/SKILL.md only.
Full suite green: 444 passed, 2 skipped. IMPLEMENTER_RESULT:
`.agent-work/issue-102/crew-handoffs/g7-implement-result.md`.

## How to Inspect the Diff
UNCOMMITTED working tree: `cd C:/Programs/constellation-wt-102 && git status --porcelain && git diff`.
Expect exactly 1 modified file: tests/test_install_constellation.py (additions only).

## Task Statement
Add content-pin + no-residual tests modeling the existing content-pin, with correct per-bucket
destinations and SKILL.md-only residual scoping (move-9 admiral exception).

## Close Criteria — and you MUST EXECUTE falsification (detector + fix share an author, T5)
- Each moved doctrine has a content-pin on the CORRECT installed destination (everyone→any skill;
  orchestrator→commander, NOT a crew skill; move 9→lessons-auditor SKILL.md). Verify the bucket
  mapping against install_constellation.py:98-113.
- Residual test globs source `skills/**/SKILL.md` ONLY (no references/); move-9 residual scoped to
  admiral/SKILL.md. Confirm it does NOT false-fail on the bundled `_shared` copies or the retained role
  references (checklist-engine.md, measurement/ui.md, fleet-doctrine.md).
- **REQUIRED — execute at least one falsification per test class in a scratch copy, report the observed red:**
  (a) delete ONE signature line from a `skills/_shared/global-everyone.md` (scratch/stash) → the
  matching content-pin goes RED; restore.
  (b) re-insert ONE retired inline copy (e.g. paste `reporting misfit is compliance` back into a
  SKILL.md, or the banner) → the residual test goes RED; restore.
  Do this against a throwaway edit (git stash/checkout to restore); do NOT leave the tree modified.
- No new global-*.md; existing structural tests unchanged; full suite green.

## Allowed Scope
Review only; tests/test_install_constellation.py diff. You MAY make throwaway edits to source files for
falsification ONLY IF you restore them (leave the tree clean); do not commit.

## Specific Exclusions
The implementer must not have edited any skills/ production file — flag if the diff shows one.

## Constraints the Implementation Must Respect
- Model on the existing content-pin; residual SKILL.md-only; move-9 admiral-scoped.
- No new global-*.md.

## Evidence Produced
IMPLEMENTER_RESULT has test names, bodies/excerpts, suite tail (444 passed), scoping sanity note.
Evidence targets `g7-integrate.c1`. Reproduce the suite AND run the two required falsifications.

## Note on the move-9 residual
`breaks recurrence counting` appears nowhere now (it was admiral's pre-trim phrasing, removed in
move 9). So that residual is an absence-sentinel that reds only if the trimmed rationale is restored to
admiral — a valid but narrow guard, paired with the "forks its identity" content-pin on the home. This
is acceptable; note it but do not BLOCK on it alone.

## Suggested Model Tier
stronger — you must reason about (and execute) test falsification and confirm the bucket destinations.

## Stop Conditions
BLOCK if: a content-pin asserts on a wrong-tier destination (e.g. an orchestrator signature on a crew
skill's global-everyone, which lacks it); the residual test false-fails or is scoped to include
references/; a falsification does NOT produce the expected red (test is too weak); a production file was
edited; a new global-*.md appeared; or the suite is red.

## Return Format
Return REVIEW_RESULT (write to `.agent-work/issue-102/crew-handoffs/g7-review-result.md` AND as your
final message): verdict (APPROVE or BLOCK), per-check findings, the TWO executed-falsification results
(what you changed, the red you observed, that you restored), blockers, out-of-scope observations,
workflow feedback. Your FINAL MESSAGE must be the complete REVIEW_RESULT.
