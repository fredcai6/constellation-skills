# Crash-resume state note — issue-456

If this session dies, a fresh agent resumes from exactly these five lines — no
forensics. Rewritten before entering `execute` and again before **each** crew
dispatch (the PID changes every time).

- **step:** execute · item `g0-implement` — **substantively COMPLETE and verified; only the engine `advance` is outstanding**, blocked by a HARD context trip on the commander (tc1). Evidence attached as `e-g0-implement-1`; the handoff digest is hand-written at `e-g0-implement-2`; refresh filed as `e-g0-implement-3`. Took three implementer passes. **Next after the advance: `g0-review`.** 11 gates: g0 g1 g2 g3 g4 g5 gb g6 g7 g8 gs
- **slug:** work-id `issue-456` · branch `issue-456/code-map` (pushed to origin) · worktree `C:/Programs/constellation-skills/.claude/worktrees/issue-456`
- **next command:** `python C:/Users/fredc/.claude/skills/constellation-commander/scripts/checklist_engine.py --file .agent-work/issue-456/spine.json current` — then re-claim lease `commander-issue-456` idempotently (same id, NOT a takeover), read the DIGEST, and drive `.agent-work/issue-456/execute.json` from `current`. Before any crew: `python scripts/recover_crews.py issue-456`, then dispatch only via `python scripts/run_crew.py --dispatch external --verify-result`.
- **pid:** none — the g0 implementer is an Agent-tool subagent (`g0-implementer`), not an OS process. Registry entry: `constellation/issue-456/g0/implementer/attempt-1`, state `running`. Recover with `python scripts/recover_crews.py issue-456`; a `resumable` crew is resumed in place via `SendMessage` to its agent id, a `needs-abandon` one via `run_crew.py --abandon <session> --relaunch`.
- **expected artifact:** immediate — `.agent-work/issue-456/crew-handoffs/g0-implement-RESULT.md`. Final — `.agent-work/issue-456/execute.json` with all 34 items `complete`, and each gate's `IMPLEMENTER_RESULT`/`REVIEW_RESULT` under `.agent-work/issue-456/crew-handoffs/`

**Baseline, measured at this commit:** full suite `1688 passed, 2 skipped, 0 failed` (`python -m pytest tests/ -q --color=no`, 260s). Any red below that line is this run's doing.

**Authority reminder for a fresh agent:** push and a full non-draft PR are
PRE-APPROVED for this work. **Merge to `main` is NOT approved.** Never
force-push. `C:/Programs/f1Brainz` and `C:/Programs/superCoolSpaceSim` are
read-only corpora.

_Updated: 2026-08-07T20:16:00Z_
