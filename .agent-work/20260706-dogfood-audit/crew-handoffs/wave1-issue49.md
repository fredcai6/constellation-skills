# Launch Order: wave1-49 — Platform reference layer: windows.md imported by Charter (#49)

## Mission
Windows/harness hazards are scattered across per-project dogfood lessons; consolidate them into one shared platform reference that Charter folds into consuming projects (full issue: `gh issue view 49`). Content floor (all four, grounded, with WORKING command forms):
1. Multiline `gh --body` on PowerShell 5.1: heredocs AND `@'...'@` here-strings both fail; only `-F <file>`/`--body-file` works (story_time, 3 consecutive epics).
2. Agent-tool resume is SendMessage-to-agentId, NOT `--resume` (f1Brainz run 510).
3. Agent-tool `isolation:"worktree"` is a no-op on Windows: sequential dispatch unless `git worktree list` shows N distinct paths; `verify_worktree_isolation.py` gates waves.
4. `py` launcher vs `python` on Windows.

IMPORTANT — reconcile, don't duplicate: some of this already lives in the `global-everyone.md` doctrine source ("Windows shell hazards", "Parallel dispatch and worktrees" sections) and `skills/admiral/references/fleet-doctrine.md`. Your deliverable is the SINGLE canonical home (a shared platform reference file under `skills/`), with the existing doctrine sections either pointing to it or kept as the canonical home themselves — decide the cleanest structure, state the decision in the PR. The gap being closed: a CONSUMING PROJECT'S agents (via Charter's compiled context) currently never receive these hazards; charter must wire them in.

## Prior-Wave Verdicts
None — wave 1.

## Pre-Rulings
- `install_constellation.py` may be touched ONLY to ship the new reference file with the appropriate skills (bundle lists for scripts are #43's fence, wave 2 — if your file-shipping change collides with bundle-tuple lines, keep your diff minimal and note it).
- Positive recipe form: each hazard entry states the WORKING form first, the failure mode second.

## Workspace
Worktree: `C:/Programs/constellation-skills-worktrees/issue-49`, branch `constellation/issue-49`, base origin/main 363d27a. First step: `py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-skills-worktrees/issue-49` must exit 0; paste output.

## File Ownership
New platform reference file(s) under `skills/`, `skills/charter/SKILL.md` (wiring), minimal `install_constellation.py` file-shipping lines, Windows-hazards doctrine sections of `global-everyone.md`/`fleet-doctrine.md` sources. Fence: do not touch `checklist_engine.py`, `run_crew.py`, engine-verbs doctrine lines (#44's fence).

## Budget
Model tier: sonnet-class. One implementer pass + one fresh-context reviewer subagent before the PR.

## Stop Conditions
Stop and query the Admiral if: charter's compile flow has no clean seam to import a platform reference (structural change → surfaced); or the reconcile decision would delete doctrine other issues depend on.
