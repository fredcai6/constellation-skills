# Crash-resume state note — epic-559/c3-lifecycle

- **step:** `archive` · **BLOCKED**, bubbled to the Admiral. All five gates integrated with an APPROVE each; `execute`, `reconcile`, `triage`, `review` and `feedback` are complete. `archive.c2` (branch pushed) and `archive.c2b` (OPEN or MERGED PR) are outward-facing acts this run is not authorized to take; neither declares an `override_policy` and the crew-waive hook denied the waive, so it blocked rather than forced, per the launch order. The work area is deliberately NOT moved — the fixed ordering is advance → release → move, and `archive` has not advanced.
- **slug:** epic-559/c3-lifecycle · branch `epic-559/c3-lifecycle` · worktree `/home/tommy/projects/constellation-skills-wt/c3-lifecycle` · HEAD `5ca15589`
- **next command:** the Admiral pushes the branch and opens the PR, then `spine_halt action=resume task_id=archive`, waives `c2`/`c2b` with human authority, `spine_advance archive`, `spine_lease release`, and only then `python -c "import sys; sys.path.insert(0,'scripts'); import spine_lifecycle as sl; print(sl.close_work('.agent-work/epic-559/c3-lifecycle/execute.json', root='.', today='2026-08-12'))"` to move the work area spine-last and commit.
- **pid:** none — foreground; this Commander is ending its turn with the run BLOCKED, not stalled.
- **expected artifact:** `.agent-work/epic-559/c3-lifecycle/COMMANDER_RETURN.md` — **written and committed**; that write was the delivery.

**The lease is deliberately still HELD**, not released: releasing on a non-terminal spine would let a second agent in, which is exactly the failure this run found (`tc4`). Re-claim with the same session id (idempotent) or `--force` if it has gone stale.

_Updated: 2026-08-12T13:30:00+00:00_
