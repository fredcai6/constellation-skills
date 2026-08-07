# Crash-resume state note — issue-456

If this session dies, a fresh agent resumes from exactly these five lines — no
forensics. Rewritten before entering `execute` and again before **each** crew
dispatch (the PID changes every time).

- **step:** execute · item `g0-review` — **in-progress**. The review RAN and
  returned **BLOCK** (`e-g0-review-2`, `crew-handoffs/g0-review-RESULT.md`); all
  five close criteria passed, two blockers. **B2** (the page count that cannot go
  wrong) is out with a remediation implementer against
  `crew-handoffs/g0-remediate.md`. **B1** (every page carries a source position,
  against a `settled/human` ruling) is **ESCALATED TO TOMMY AND UNANSWERED** —
  `g0` must NOT advance until he picks (a) strip the suffix, assigned to a named
  gate, or (b) amend the ruling and accept the churn. **Next after `g0-review`:
  `g0-integrate`.** 11 gates: g0 g1 g2 g3 g4 g5 gb g6 g7 g8 gs
- **slug:** work-id `issue-456` · branch `issue-456/code-map` (pushed to origin)
  · worktree `C:/Programs/constellation-skills/.claude/worktrees/issue-456`
- **next command:** `python C:/Users/fredc/.claude/skills/constellation-commander/scripts/checklist_engine.py --file .agent-work/issue-456/spine.json current` — then re-claim lease `commander-issue-456` idempotently (same id, NOT a takeover), read the DIGEST, and drive `.agent-work/issue-456/execute.json` from `current`. Before any crew: `python scripts/recover_crews.py issue-456`, then dispatch only via `python scripts/run_crew.py --dispatch external --verify-result`.
- **pid:** none — the g0 reviewer is an Agent-tool subagent (`g0-reviewer`), not
  an OS process. Registry entry: `constellation/issue-456/g0/reviewer/attempt-1`.
  Recover with `python scripts/recover_crews.py issue-456`; a `resumable` crew is
  resumed in place via `SendMessage` to its agent id, a `needs-abandon` one via
  `run_crew.py --abandon <session> --relaunch`. The three implementer attempts
  are all resolved (1 and 2 ABANDONED after clean context-trip handoffs, 3
  COMPLETE) — do not rerun them.
- **expected artifact:** immediate — `.agent-work/issue-456/crew-handoffs/g0-review-RESULT.md`. Final — `.agent-work/issue-456/execute.json` with all 34 items `complete`, and each gate's `IMPLEMENTER_RESULT`/`REVIEW_RESULT` under `.agent-work/issue-456/crew-handoffs/`

**Baseline, measured at this commit:** full suite `1688 passed, 2 skipped, 0 failed`
before `g0`; **`1706 passed, 2 skipped, 0 failed` after `g0`**, reproduced
independently by the Commander. Any red below that line is this run's doing.
Clear `FORCE_COLOR` and `PYTHONIOENCODING` before trusting a suite number
(`tc3`, `tc7`).

**Authority reminder for a fresh agent:** push and a full non-draft PR are
PRE-APPROVED for this work. **Merge to `main` is NOT approved.** Never
force-push. `C:/Programs/f1Brainz` and `C:/Programs/superCoolSpaceSim` are
read-only corpora. Do **not** `git add -A` in this worktree — the untracked
3,635-page `map/` tree is staged at `gs`, deliberately last; stage explicit paths.

_Updated: 2026-08-07T22:12:00Z_
