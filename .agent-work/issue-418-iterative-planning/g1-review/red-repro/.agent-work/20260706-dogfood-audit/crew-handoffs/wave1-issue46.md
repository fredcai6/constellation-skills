# Launch Order: wave1-46 — Crew integrity: exists-AND-fresh gate + verify-claimed-side-effects doctrine (#46)

## Mission
Two halves of one distrust slice (full issue: `gh issue view 46`):
1. **Engine/harness gate**: `run_crew.py --verify-result` currently checks result EXISTENCE, not freshness. Dogfood failures: crews background their own long step and go idle with the result unwritten or stale (`crew-idle-strands-deliverable`, 3 recurrences; `crew-result-staleness-verify-gap`). Add a "result exists AND fresh" check — fresh relative to dispatch time (mtime and/or a run-stamp in the result contract). A stale/missing result must produce a clear, visible refusal naming what was expected.
2. **Doctrine**: encode `verify-claimed-side-effects` in `skills/reviewer/SKILL.md` and the commander gN-integrate doctrine (`skills/commander/SKILL.md`): claimed side-effects (issue filed, migration ran, file changed) are verified against the world, never accepted from the report. Dogfood evidence: a commander claimed a filed issue that didn't exist; a crew claimed a migration it never ran.

## Prior-Wave Verdicts
None — wave 1.

## Pre-Rulings
- Freshness metric must be robust to clock-skew-free local runs (single machine); simple and visible beats clever.
- `recover_crews.py` may need the same freshness awareness — in scope if the diff is small; otherwise file it as a triage candidate.
- Positive-recipe form for the doctrine edits (state what the reviewer DOES, not a prohibition list).

## Workspace
Worktree: `C:/Programs/constellation-skills-worktrees/issue-46`, branch `constellation/issue-46`, base origin/main 363d27a. First step: `py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-skills-worktrees/issue-46` must exit 0; paste output.

## File Ownership
`scripts/run_crew.py`, (optionally `scripts/recover_crews.py`), `skills/reviewer/SKILL.md`, the gN-integrate portion of `skills/commander/SKILL.md`, their tests. Fence: do not touch `checklist_engine.py` (#44 owns it this wave), commander spine JSON template (#45, wave 2), install script.

## Budget
Model tier: opus-class. One implementer pass + one fresh-context reviewer subagent before the PR.

## Stop Conditions
Stop and query the Admiral if: the result contract shape itself needs redesign (that's #53's design space); or commander SKILL.md changes would collide with #45/#50 scope (wave 2 — keep your edit surgical to gN-integrate).
