# STATE NOTE — issue-690

- **Step:** `plan` COMPLETE. `execute` is `pending` and was **deliberately not entered** — this
  engagement was planning-only.
- **Slug:** `issue-690` — per-class G σ⁺ band scale.
- **Engine lease:** `cmdr-690-plan` (still ACTIVE, by `commander-690`). A resuming session re-claims
  with the **same** `--session-id` (idempotent, free); a different session needs
  `--force --reason "resuming this run"`.
- **Next command:**
  `py C:/Users/fredc/.claude/skills/constellation-commander/scripts/checklist_engine.py --file .agent-work/issue-690/spine.json current`
- **PID:** n/a — nothing detached, no background work launched, no crew dispatched.
- **Expected artifacts (present):** `PROBLEM_STATEMENT.md`, `MISSION_FRAME.md` (verify-frame
  FRAME-OK), `PLAN_DECISIONS.md`, `execute.json` (frozen, engine-validated),
  `map-orientation.json`, `spine.json`.
- **Expected artifact (NOT yet produced):** `BAND_DISTRIBUTION_REPORT.md` — g4's deliverable.

## Before resuming into `execute`, read this

1. **The branch base is the first thing to check.** This planning worktree
   (`C:/Programs/f1bwt/post690`) is detached at `3541d292`, which **predates** #721. The plan is cut
   against `main` (`3cf79f78`), where #721 landed as `54c7860f`. `e0-context.c1` is a non-waivable
   machine check for exactly this; cut the work branch off `main`.
2. **Repo state at the end of this engagement:** no source, test, or documentation file was
   modified; nothing committed, pushed, or commented. `git status` shows only the untracked
   `.agent-work/issue-690/` work area.
3. **Two things a resuming Commander may want before g1:** a genuinely **cold** critic panel on the
   frozen plan (named untaken road in `PLAN_DECISIONS.md` — this run's critic shared the author's
   context), and confirmation that no sibling W2 issue has since minted a band-distribution reporter
   (g3's imperative already carries the extend-don't-duplicate precondition).
