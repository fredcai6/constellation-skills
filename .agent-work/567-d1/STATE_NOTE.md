# Crash-resume state note — 567-d1

- **step:** execute · pending, NOT started. A `refresh-request` (`e-execute-1`) is filed against it. Steps init → plan are complete; the plan is frozen at commit `bd677d7c`.
- **slug:** 567-d1 · branch `feat/567-d1-doctrine-sweep-guard` · worktree `/home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard`
- **next command:** `spine_status` (door, already bound to this spine) → reload the `constellation-commander` skill → `attest execute --cond p1 --which preconditions` → `start execute` → drive `.agent-work/567-d1/execute.json` from **g1-implement** (author `tests/test_cli_retirement_guard.py` against the still-dirty tree; it must go RED naming 13 clause sites and 9 `<engine>` sites). Dispatch every crew through `py /home/tommy/.claude/skills/constellation-commander/scripts/run_crew.py`, and run `recover_crews.py 567-d1` before each dispatch.
- **pid:** none — foreground
- **expected artifact:** `.agent-work/epic-567-door/results/lane-d1-RETURN.md` (the run is complete only when this exists)

## What a fresh Commander must not re-derive

Read `.agent-work/567-d1/notes-1.md` (measurements), `MISSION_FRAME.md`, and
`plan-rigor/CONVERGENCE.md` (design-it-twice convergence + the cold critic's 13 triaged
findings). The three things that cost the most to establish:

1. **The regrowth mechanism is a test.** `tests/test_mcp_adoption.py` mandates the text, across
   **nine** assertions, not one. The sweep is an inversion of an existing test.
2. **The door cannot drive a second checklist** (measured, fresh process): it refuses to rebind
   while the process holds its own lease. So 3 of the 13 clauses get reworded, not deleted.
3. **Guard scope = the existing `INSTRUCTION_FILES` walk**, extended to `specs/**/*.toml`.
   Exception list length **zero**, measured.

_Updated: 2026-08-17T17:56:00Z_
