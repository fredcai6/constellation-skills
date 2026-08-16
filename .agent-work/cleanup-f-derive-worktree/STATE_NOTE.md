# Crash-resume state note — cleanup-f-derive-worktree

- **step:** execute · leg 3 · `execute.json` gate `g2-implement` (rework 3 — reviewer BLOCK B1, a claim-level prose sweep) — under `ADMIRAL_RULING-2.md`: N2 road 1, delete the engine-side `worktree_from_spine_path`; then g3, `skip` g4 (R2) and g5 (R3).
- **slug:** cleanup-f-derive-worktree · branch `cleanup/f-derive-worktree` · worktree `/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree` · HEAD `9953b950` (`main` at `17c2cee5` merged; g2 rework 2 committed)
- **next command:** `py scripts/checklist_engine.py --file .agent-work/cleanup-f-derive-worktree/execute.json current`
- **pid:** foreground/blocking — `run_crew.py` dispatching `g2/implementer/attempt-4` (rework 3). If this session died mid-dispatch, run `py /home/tommy/.claude/skills/constellation-commander/scripts/recover_crews.py cleanup-f-derive-worktree` first and resume or abandon what it flags.
- **expected artifact:** `.agent-work/cleanup-f-derive-worktree/execute.json` driven to terminal, then the spine's `archive` closeout — this leg's result artifact is `.agent-work/cleanup-f-derive-worktree/crew-handoffs/execute-commander-result.md`

**Read first on resume:** `LAUNCH_ORDER-3.md`, `ADMIRAL_RULING-2.md`,
`ADMIRAL_RULING-1.md`, `FLOAT_TO_ADMIRAL-2.md`, then `LAUNCH_ORDER.md`,
`PROBLEM_STATEMENT.md`, `MISSION_FRAME.md`, `UNTAKEN_ROADS.md`.

**State on entry to leg 3.** The g2 rework implementer (attempt-2) completed its
m0–m4 (suite 3196 passed / 5 skipped / 0 failed) and died in `m5-result` with an
`Execution error` before writing `crew-handoffs/g2-implementer-rework-result.md`.
Its work is in the tree (`docs/CHECKLIST_SCHEMA.md`,
`scripts/checklist_engine.py`, `tests/test_spine_origin_isolation.py`); its
evidence is under `g2-implement-rework/`. Its registry entry was destroyed by the
parent launcher's clobber (#617) and restored by union-merge from `HEAD`.

**Nothing is waiting on the Admiral.** Floats-in-waiting: any case where "cannot
place" genuinely must refuse (R2's escape hatch), and publication (always theirs).

_Updated: 2026-08-16T20:56:00+00:00_
