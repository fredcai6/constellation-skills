# Launch order — Codex model-tier routing

## Mission

Add the smallest backward-compatible crew-registry path for an external Codex launcher to consume a persisted model and optional reasoning effort, analogous to the existing Claude model intent.

## Prior-wave verdicts

Main is `0448275e`. Linux was green at 2,980 passed, 7 skipped, and 1,130 subtests. Measurement found `--model` already persists and resumes; nullable `reasoning_effort` is the missing field. `ExternalBackend` is intentionally record-only.

## Pre-rulings

- decision:metadata-only — thread nullable reasoning effort through CLI, `CrewSpec`, registry dispatch/relaunch, and tests; do not invent an external process launcher.
  @grade: settled/human · leans execute
- decision:claude-argv — preserve Claude argv and defaults; Codex metadata must not become a Claude flag.
  @grade: settled/human · leans execute
- decision:legacy-registry — old entries without the field remain readable via optional lookup/defaults.
  @grade: settled/human · leans execute

## Honest-null clause

A red-first proof that the metadata already survives end to end is a complete measured null. Name what was and was not tested.

## Inherited latitude

Choose the smallest parser/schema threading. Float any migration, launcher behavior, default change, schema incompatibility, or edits outside the owned files.

## File ownership

Sole writer for `scripts/run_crew.py`, focused `tests/test_crew_launcher.py`, and worktree-local `notes-1.md`. Do not edit engine, hook, lifecycle, or architecture files.

## Workspace

`/home/tommy/projects/constellation-skills/.worktrees/epic-568-codex-tier-routing`, branch `epic-568-codex-tier-routing`, base `0448275e`, originally created with `git worktree add` and moved repo-locally after the sandbox incident. First verify isolation with `python /home/tommy/.claude/skills/constellation-admiral/scripts/verify_worktree_isolation.py --here /home/tommy/projects/constellation-skills/.worktrees/epic-568-codex-tier-routing`.

## Inherited context

Drive `.agent-work/epic-568-codex-tier-local/spine.json` only through `scripts/mcp_spine_server.py` over stdio with session `constellation/epic-568-codex-tier-local`; do not invoke checklist-engine CLI or read/hand-edit engine JSON. Use targeted automated tests and the relevant broader suite. Local/non-Windows failures block. Windows failures may be recorded without fixing. No push, PR, merge, or issue mutation.

## Pre-empted steps

Admiral has established context, measured the baseline, selected the implementation shape, and ratified this launch order. Cite it at delegated user-decision gates.

## Data locations

All inputs are tracked in this worktree. The older `.agent-work/epic-568-codex-tier-routing/` records the abandoned, released sibling-path attempt and is not the active job file.

## Budget

- Model tier: `gpt-5.6-terra`, medium reasoning.
- Session: bounded mechanical implementation; stop on scope expansion.

## Stop conditions

Stop and float if behavior beyond metadata threading is required, tests expose a non-Windows regression, or any owned-file boundary must expand.

## Return shape

Write a durable result under the active work area before returning. Include isolation output, red-first proof, changed files, exact test commands/exit codes, remaining risk, spine status, and READY-FOR-REVIEW or FLOAT.
