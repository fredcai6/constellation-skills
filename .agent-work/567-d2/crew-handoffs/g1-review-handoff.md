# Reviewer Handoff

## Gate
g1-review (work-id 567-d2)

## Survey State Location
`.agent-work/567-d2/g1-review/review.json`

## What Was Implemented
`skills/workbench/SKILL.md`, `skills/workbench/references/checklist-engine.md`, and
`skills/workbench/references/status-model.md` were shrunk from teaching-heavy prose to only
the sections proven load-bearing (by two pre-existing test suites and by files outside this
lane's ownership that cite them by name). `docs/agents/CREW_CONTEXT.md` had one stale
measurement paragraph replaced with a current one (#561).

## How to Inspect the Diff
Uncommitted working tree in
`/home/tommy/projects/constellation-skills/.worktrees/567-d2-workbench-sunset` (a linked
worktree — do NOT use `git diff main...HEAD`). Use `git status --porcelain` then `git diff`.

## Task Statement
Same as `.agent-work/567-d2/crew-handoffs/g1-implement-handoff.md`'s Task section — apply the
"full replacement" content in `.agent-work/567-d2/g1-target-content.md` byte-for-byte to the
three workbench files, and the single-paragraph CREW_CONTEXT.md edit, touching nothing else.

## Close Criteria
- All three "full replacement" files in `.agent-work/567-d2/g1-target-content.md` match the
  actual files in the repo EXACTLY (verify by direct comparison, not eyeball — e.g. diff the
  extracted block against the real file).
- `docs/agents/CREW_CONTEXT.md`'s diff is exactly the one paragraph named in
  `g1-target-content.md`'s CREW_CONTEXT.md block — nothing else in that file changed.
- `py -m pytest tests/test_mcp_adoption.py tests/test_commander_evidence_convention.py tests/test_install_constellation.py -q` is green.
- `git diff --name-only` shows exactly: `skills/workbench/SKILL.md`,
  `skills/workbench/references/checklist-engine.md`,
  `skills/workbench/references/status-model.md`, `docs/agents/CREW_CONTEXT.md` — nothing else,
  and nothing under `skills/workbench/templates/`.
- `grep -c "Nothing here removes or discourages the CLI." skills/workbench/references/checklist-engine.md` is exactly 1.

## Allowed Scope
Read-only review across the whole repo; the implementer's write scope was limited to the four
files named above.

## Specific Exclusions
Everything outside those four files was off-limits to the implementer — flag as BLOCK only if
`git diff --name-only` shows anything else.

## Constraints the Implementation Must Respect
- No template under `skills/workbench/templates/` moved, renamed, or edited.
- The retained prose (the `## MCP door` and `## Session lease` sections of checklist-engine.md
  especially) must be byte-identical to the pre-change file — a reworded-but-equivalent version
  is a BLOCK even if it reads fine, because `tests/test_mcp_adoption.py` pins exact phrases and
  one exact sentence.

## Map Anchors (inbound)
- **Structural:** `skills/workbench/SKILL.md`, `skills/workbench/references/checklist-engine.md`,
  `skills/workbench/references/status-model.md`, `docs/agents/CREW_CONTEXT.md`.
- **Constraints/assumptions:** templates move nowhere (settled/human).
- **Decision anchors:** workbench stays a template package
  `@grade: settled/human · leans g1-review`; partial not full deletion, evidenced at understand
  `@grade: settled/measured · leans g1-review · settle: full suite green post-change`.
- **Evidence expectations:** `tests/test_mcp_adoption.py` Tier2+Tier3 stay green;
  `tests/test_install_constellation.py` post-install read-back stays green;
  `tests/test_commander_evidence_convention.py` stays green.

## Evidence Produced
IMPLEMENTER_RESULT at `.agent-work/567-d2/crew-handoffs/g1-implement-result.md` claims: 4 files
changed exactly as scoped, byte-exact verification of the 3 full-replacement files via
programmatic string equality, targeted tests green before AND after (388 passed, 2 skipped, 506
subtests both runs), canonical CLI sentence count 1. The Commander (dispatcher) independently
re-ran the same three-file pytest command post-integration and confirms 388 passed, 2 skipped,
506 subtests, and independently confirmed `git diff --name-only` scope. Re-verify all of this
yourself from scratch — do not treat the above as settled.

## Suggested Model Tier
simple bounded — a bounded diff review against a fully-specified target-content file, with
existing tests as the oracle.

## Stop Conditions
Stop and return BLOCK if: any retained section is not byte-identical to the original
(check especially the `## MCP door` section and the `Nothing here removes or discourages the
CLI.` sentence), any file outside the 4 allowed changed, or the named tests are not green.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope
observations, workflow feedback.

**Delivery.** Write the full `REVIEW_RESULT` to
`.agent-work/567-d2/crew-handoffs/g1-review-reviewer-result.md` before ending your turn.
