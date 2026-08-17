# Implementer Handoff

## Gate
g1-implement (work-id 567-d2)

## Task
Shrink three `skills/workbench` teaching files to their evidenced-minimal content, and fix a
stale measurement in `docs/agents/CREW_CONTEXT.md` (#561). Exact target content for all four
edits is fully specified in `.agent-work/567-d2/g1-target-content.md` — apply it byte-for-byte
(the "full replacement" blocks are complete file contents; the CREW_CONTEXT.md block is a
find-and-replace of one paragraph only). Do not improvise or paraphrase the retained sections —
they are proven, byte-exact matches against two existing test suites; any rewording risks
breaking them.

## Protected Intent
The MCP door's own tool descriptions now teach the checklist engine's mechanism directly, so
`skills/workbench`'s prose teaching of that mechanism is redundant and should shrink — but two
independent, pre-existing test suites (`tests/test_mcp_adoption.py`, `tests/test_install_constellation.py`,
`tests/test_commander_evidence_convention.py`) and several files outside this lane's ownership
(`skills/commander/references/commander-core.md`, `skills/reviewer/templates/REVIEW_RESULT.template.md`,
`skills/implementer/templates/IMPLEMENTER_RESULT.template.md`, `skills/commander/templates/IMPLEMENTER_HANDOFF.template.md`)
depend on specific retained sections. The four templates under `skills/workbench/templates/`
must not move or change.

## Test Mode
Test-after (inspection + the three existing test files as the oracle) — no new test surface is
being added; the task is deletion plus one factual correction, verified against tests that
already exist.

## Close Criteria
- `skills/workbench/SKILL.md`, `skills/workbench/references/checklist-engine.md`,
  `skills/workbench/references/status-model.md` match the "full replacement" blocks in
  `.agent-work/567-d2/g1-target-content.md` exactly.
- `docs/agents/CREW_CONTEXT.md` has ONLY the Python Invocation measurement paragraph changed, per
  the block in the same file; every other line unchanged.
- `py -m pytest tests/test_mcp_adoption.py tests/test_commander_evidence_convention.py tests/test_install_constellation.py -q`
  is green (or matches a named, reproduced pre-existing baseline failure — run it BEFORE your
  edit too and diff the two runs if anything is red).
- `git diff --name-only` shows only: `skills/workbench/SKILL.md`,
  `skills/workbench/references/checklist-engine.md`, `skills/workbench/references/status-model.md`,
  `docs/agents/CREW_CONTEXT.md`.
- No file under `skills/workbench/templates/` appears in the diff.

## Allowed Scope
- `skills/workbench/SKILL.md`
- `skills/workbench/references/checklist-engine.md`
- `skills/workbench/references/status-model.md`
- `docs/agents/CREW_CONTEXT.md` (Python Invocation section only)

## Specific Exclusions
- `skills/workbench/templates/**` — do not touch, move, or rename (settled by the human).
- Every other file in the repo, including `tests/**`, `skills/_shared/**`,
  `skills/commander/**`, `skills/reviewer/**`, `skills/implementer/**` — read-only, for
  verification purposes only.

## Constraints
- Apply the "full replacement" blocks verbatim — do not summarize, reword, or "improve" the
  retained prose; any rewording of the `## MCP door` section in particular risks silently
  failing `tests/test_mcp_adoption.py`'s byte-exact and section-scoped assertions.
- The CREW_CONTEXT.md edit is a single-paragraph find-and-replace; do not touch anything else
  in that file, including its other sections.

## Map Anchors (inbound)
- **Map entry point:** `.agent-work/567-d2/g1-target-content.md` (this gate's actual target
  content); `.agent-work/567-d2/MISSION_FRAME.md` for the broader mission context.
- **Structural:** `skills/workbench/SKILL.md`, `skills/workbench/references/checklist-engine.md`,
  `skills/workbench/references/status-model.md`, `docs/agents/CREW_CONTEXT.md`.
- **Constraints/assumptions:** templates move nowhere (settled/human); `discover_skills()`
  requires a parseable `SKILL.md` per `skills/*` dir.
- **Decision anchors:** workbench stays a template package
  `@grade: settled/human · leans g1-implement`; partial not full deletion, evidenced at
  understand `@grade: settled/measured · leans g1-implement,g1-review · settle: full suite
  green post-change`.
- **Evidence expectations:** `tests/test_mcp_adoption.py` Tier2+Tier3 stay green;
  `tests/test_install_constellation.py` post-install read-back stays green;
  `tests/test_commander_evidence_convention.py` stays green.

## Deliverable Path Check
- **Committed** — `skills/workbench/SKILL.md`; already tracked, edited in place; not gitignored
  (`git check-ignore skills/workbench/SKILL.md` exits 1).
- **Committed** — `skills/workbench/references/checklist-engine.md`; same.
- **Committed** — `skills/workbench/references/status-model.md`; same.
- **Committed** — `docs/agents/CREW_CONTEXT.md`; same.
No new files are created by this gate.

## Required Evidence
- `git diff --stat` and `git diff --name-only` after the edit.
- `wc -l` on all four files, before and after.
- Full output of `py -m pytest tests/test_mcp_adoption.py tests/test_commander_evidence_convention.py tests/test_install_constellation.py -q`, run both BEFORE your edit (baseline) and AFTER (result) — paste both, not just the tail.
- `grep -c "Nothing here removes or discourages the CLI." skills/workbench/references/checklist-engine.md` — must be 1.
- `which py python python3` output, re-confirming the CREW_CONTEXT.md measurement you're about to write is still accurate on this host right now.

## Wiring Grep
none — this gate deletes and edits prose/doc content, adds no callable symbol.

## Verification Commands
```bash
cd /home/tommy/projects/constellation-skills/.worktrees/567-d2-workbench-sunset
py -m pytest tests/test_mcp_adoption.py tests/test_commander_evidence_convention.py tests/test_install_constellation.py -q
git diff --stat
git diff --name-only
wc -l skills/workbench/SKILL.md skills/workbench/references/checklist-engine.md skills/workbench/references/status-model.md docs/agents/CREW_CONTEXT.md
grep -c "Nothing here removes or discourages the CLI." skills/workbench/references/checklist-engine.md
```

## Suggested Model Tier
simple bounded — the target content is fully specified verbatim; the task is precise file
replacement plus one paragraph edit, then run the named verification commands.

## Authority
The exact retained/deleted content per file is already decided (this lane's Commander, within
its "How workbench is deregistered — yours" / "Replacement wording — yours" latitude, per
LAUNCH_ORDER cmdr-567-d2). Do not decide to keep or cut anything not named in
`g1-target-content.md` — if you find a reason to deviate, stop and report it as a blocker
rather than deciding alone.

## Stop Conditions
Stop and return if: the target content in `g1-target-content.md` does not actually satisfy the
named tests when you run them (report the exact failure); you're asked to touch a file outside
Allowed Scope; a decision outside this handoff's Authority is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence
produced, assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.

The result's `Return status` field (`complete | partial | blocked | out-of-scope | failed`) is
what the Commander copies verbatim, lowercase, into this gate's `implementer-result` evidence.

**Delivery.** Write the full `IMPLEMENTER_RESULT` to
`.agent-work/567-d2/crew-handoffs/g1-implement-result.md` before ending your turn.
