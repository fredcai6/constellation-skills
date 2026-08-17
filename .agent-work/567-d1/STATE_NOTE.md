# Crash-resume state note — 567-d1

- **step:** `execute` is COMPLETE — `execute.json` driven through `g5-final`, lease released, `verify_iterative_role_artifacts.py commander --work-id 567-d1` ok. The return artifact EXISTS at `.agent-work/epic-567-door/results/lane-d1-RETURN.md`. Remaining spine steps: **reconcile → triage → review → feedback → archive**, plus opening the PR.
- **slug:** 567-d1 · branch `feat/567-d1-doctrine-sweep-guard` · worktree `/home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard`
- **next command:** advance the parent spine from `reconcile`. Branch is rebased on `origin/main` 5099eea1; verified head 1037ab86. **Lane D2 must merge before this lane.**
- **old next command:**
  ```sh
  cd /home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard
  py /home/tommy/.claude/skills/constellation-commander/scripts/recover_crews.py 567-d1
  py scripts/checklist_engine.py --file .agent-work/567-d1/execute.json current
  ```
  Then dispatch `g1-implement` through `run_crew.py`, **with `SPINE_FILE`/`SPINE_SESSION`/`CREW_SCRATCH_DIR` stripped from the launching environment** (`env -u SPINE_FILE -u SPINE_SESSION -u CREW_SCRATCH_DIR ...`): a no-`--spine` crew inherits those variables and its door would otherwise bind **this lane's** spine.
- **pid:** none — the Commander runs in the foreground; `run_crew.py` blocks on each crew.
- **expected artifact:** `.agent-work/epic-567-door/results/lane-d1-RETURN.md` (the run is complete only when this exists), plus `tests/test_cli_retirement_guard.py` as the gate deliverable.

## Crew state

`constellation/567-d1/g1/implementer/attempt-1` died at launch with a bare `Execution error`
(0 bytes of work, no result artifact, PID 2330638 dead). Abandoned and relaunched as attempt-2.

## What a fresh Commander must not re-derive

Read `.agent-work/567-d1/notes-1.md` (measurements), `MISSION_FRAME.md`, `decision-anchors.md`,
and `plan-rigor/RESULT-critic.md`. The three things that cost the most to establish:

1. **The regrowth mechanism is a test.** `tests/test_mcp_adoption.py` mandates the text across
   **nine** assertions, not one. The sweep is an inversion of an existing test.
2. **The door cannot drive a second checklist** (measured, fresh process): it refuses to rebind
   while the process holds its own lease. So 3 of the 13 clauses get reworded, not deleted.
3. **Guard scope = the existing `INSTRUCTION_FILES` walk**, extended to `specs/**/*.toml`.
   Exception list length **zero**, measured.

_Updated: 2026-08-17T18:05:00Z_
