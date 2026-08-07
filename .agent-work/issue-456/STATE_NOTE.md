# Crash-resume state note — issue-456

If this session dies, a fresh agent resumes from exactly these five lines — no
forensics. Rewritten before entering `execute` and again before **each** crew
dispatch (the PID changes every time).

- **step:** execute · item `e0-context` (first of 34; 11 gates g0 g1 g2 g3 g4 g5 gb g6 g7 g8 gs)
- **slug:** work-id `issue-456` · branch `issue-456/code-map` (pushed to origin) · worktree `C:/Programs/constellation-skills/.claude/worktrees/issue-456`
- **next command:** `python C:/Users/fredc/.claude/skills/constellation-commander/scripts/checklist_engine.py --file .agent-work/issue-456/spine.json current` — then re-claim lease `commander-issue-456` idempotently (same id, NOT a takeover), read the DIGEST, and drive `.agent-work/issue-456/execute.json` from `current`. Before any crew: `python scripts/recover_crews.py issue-456`, then dispatch only via `python scripts/run_crew.py --dispatch external --verify-result`.
- **pid:** none — foreground (no detached process running)
- **expected artifact:** `.agent-work/issue-456/execute.json` with every one of its 34 items `complete`, and each gate's `IMPLEMENTER_RESULT`/`REVIEW_RESULT` under `.agent-work/issue-456/crew-handoffs/`

**Authority reminder for a fresh agent:** push and a full non-draft PR are
PRE-APPROVED for this work. **Merge to `main` is NOT approved.** Never
force-push. `C:/Programs/f1Brainz` and `C:/Programs/superCoolSpaceSim` are
read-only corpora.

_Updated: 2026-08-07T20:16:00Z_
