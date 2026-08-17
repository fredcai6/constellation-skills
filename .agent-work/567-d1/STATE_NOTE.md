# Crash-resume state note — 567-d1

- **step:** `execute` · **in-progress**. Child checklist `.agent-work/567-d1/execute.json` is claimed under CLI session id `commander-567-d1-execute`. `e0-context`, `g1-implement`, `g1-review` and `g1-integrate` are **complete**. The plan was amended at g1-integrate (new gate `g1b` widens the guard; `g2`/`g3`/`g4` integrate checks rescoped). `g1b-implement` was REOPENED after its review returned BLOCK (rework 1/3, `_ENGINE_VERBS` omitted the engine verb `resume`); the active gate is **`g1b-implement`** on its rework handoff. All five command postconditions were corrected from `set -o pipefail` (illegal in dash, which is what the engine runs checks under) to POSIX form.
- **slug:** 567-d1 · branch `feat/567-d1-doctrine-sweep-guard` · worktree `/home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard`
- **next command:**
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
