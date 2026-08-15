# Launch order — #510 HARD refresh advisory

## Mission

Correct the pending-HARD trip advisory so it accurately teaches the already-legal refresh path: attach refresh-request, start the guarded task, then advance with `--why`, preserving the digest.

## Prior-wave verdicts

Main is `0448275e`; Linux baseline is green. Measurement found the issue body's runtime premise is superseded: the legal engine path already exists. The remaining defect is advisory text in `_trip_advisory`; there is no verb, default, state, or schema change.

## Pre-rulings

- decision:advisory-only — change only the status-aware pending-HARD advisory and its direct regression test.
  @grade: settled/measured · leans execute
- decision:legal-sequence — advice must order attach refresh, start, then advance with why; test must execute that sequence and prove successor current carries the digest.
  @grade: settled/human · leans execute
- decision:no-runtime-expansion — do not modify trip guards, defaults, verbs, or schema.
  @grade: settled/human · leans execute

## Honest-null clause

If current pending-HARD output already gives the exact legal ordered path and the sequence test passes before editing, return a scoped null.

## Inherited latitude

Choose concise wording and focused test placement near existing HARD guard coverage. Float any runtime behavior or file-scope expansion.

## File ownership

Sole writer for `scripts/checklist_engine.py`, focused `tests/test_checklist_engine.py`, and worktree-local `notes-1.md`. Do not edit spine rail, crew launcher, or lifecycle code.

## Workspace

`/home/tommy/projects/constellation-skills/.worktrees/epic-568-510`, branch `epic-568/510-hard-advisory`, base `0448275e`, created with `git worktree add -b epic-568/510-hard-advisory .worktrees/epic-568-510 main`. First verify isolation with `python /home/tommy/.claude/skills/constellation-admiral/scripts/verify_worktree_isolation.py --here /home/tommy/projects/constellation-skills/.worktrees/epic-568-510`.

## Inherited context

Drive `.agent-work/epic-568-510/spine.json` through the local MCP stdio server with session `constellation/epic-568-510`; no checklist-engine CLI and no engine JSON reads/edits. Target `_trip_advisory` and the existing `TripHardGuardsBeginNotClose` neighborhood. Local/non-Windows failures block; Windows failures may be recorded.

## Pre-empted steps

Admiral has established context, measured the current behavior, bounded the change, and ratified the launch order. Cite it at delegated checkpoints.

## Data locations

All inputs are tracked in the isolated worktree.

## Budget

- Model tier: `gpt-5.6-terra`, medium reasoning.
- Session: small advisory/test correction.

## Stop conditions

Stop if runtime behavior must change, files beyond the owned pair are required, or any non-Windows regression appears.

## Return shape

Write the durable result before returning. Include isolation, red/green proof, exact changed files/tests, remaining risks, spine status, and READY-FOR-REVIEW or FLOAT.
