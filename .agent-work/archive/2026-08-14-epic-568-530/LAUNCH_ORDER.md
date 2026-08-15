# Launch order — #530 worktree binding correction

## Mission

Fix spine-rail binding records so a relative spine resolved inside a linked worktree stores that spine's owning worktree, not the launch checkout supplied in hook payload `cwd`. Prove the parent Stop guard excludes the child's foreign worktree correctly.

## Prior-wave verdicts

Main is `0448275e`; Linux baseline is green. Measurement isolated the defect to `scripts/hooks/spine_rail.py`: claim resolves `abs_spine` correctly but stores payload `cwd`. The safe fix derives a normalized owning worktree from the validated `.agent-work/<work-id>/<name>.json` path and uses it consistently for claim and SessionStart. #441 overlaps this store and must wait.

## Pre-rulings

- decision:source-of-truth — derive stored worktree from validated `abs_spine`, never payload cwd, observed `cd`, or `--worktree` text.
  @grade: settled/measured · leans execute
- decision:scope — support JSON checklists under `.agent-work/<work-id>/`; retain existing release resolution behavior.
  @grade: settled/human · leans execute
- decision:serialization — do not implement #441 locking, identity unification, or reaping here.
  @grade: settled/human · leans execute

## Honest-null clause

If a real linked-worktree regression cannot reproduce the wrong stored worktree on `0448275e`, return a scoped null with the exact topology and assertions.

## Inherited latitude

Choose helper naming and focused test arrangement. Float changes to checklist lifecycle, binding schema, release semantics, or files beyond the rail and its tests.

## File ownership

Sole writer for `scripts/hooks/spine_rail.py`, focused `tests/test_spine_rail.py`, and worktree-local `notes-1.md`.

## Workspace

`/home/tommy/projects/constellation-skills/.worktrees/epic-568-530`, branch `epic-568/530-binding`, base `0448275e`, created with `git worktree add -b epic-568/530-binding .worktrees/epic-568-530 main`. First verify isolation with `python /home/tommy/.claude/skills/constellation-admiral/scripts/verify_worktree_isolation.py --here /home/tommy/projects/constellation-skills/.worktrees/epic-568-530`.

## Inherited context

Drive `.agent-work/epic-568-530/spine.json` through the local MCP stdio server with session `constellation/epic-568-530`; no checklist-engine CLI and no engine JSON reads/edits. The acceptance test must use a real git main plus linked worktree, shared session, distinct agent ids, deliberately wrong payload cwd, and production handler paths. Assert child binding points to the linked worktree; parent Stop blocks only its own active spine and becomes non-blocking after parent release while child remains active. Local/non-Windows failures block; Windows failures may be recorded.

## Pre-empted steps

Admiral has established context, run a measured scout, selected this narrow fix, and ratified the launch order. Cite it at delegated checkpoints.

## Data locations

All inputs are tracked in the isolated worktree.

## Budget

- Model tier: `gpt-5.6-terra`, high reasoning.
- Session: bounded hook correction with real-worktree regression.

## Stop conditions

Stop on store-format changes, lifecycle policy, #441 overlap, inability to build a discriminating real-worktree test, or any non-Windows regression.

## Return shape

Write the durable result before returning. Include isolation, red/green proof, exact changed files/tests, blast-radius enumeration, remaining risks, spine status, and READY-FOR-REVIEW or FLOAT.
