# Crash-resume state note — issue-307

If this session dies mid-arm, a fresh agent resumes from exactly these five lines.

- **step:** execute · gate g1-capture (the five POST captures, detached)
- **slug:** issue-307 · branch `epic-298/307` · worktree `C:/Programs/constellation-skills-wt/e298-307` (cut from `4cec87a`; NEVER touch the main checkout `C:/Programs/constellation-skills` — it holds the human's uncommitted WIP)
- **next command:** `cd C:/Programs/constellation-skills-wt/e298-307 && python .agent-work/epic-298/post/run_all_post.py 2>&1 | tee -a .agent-work/epic-298/post/run_all_post.log` — it is RESUMABLE: any run whose `treatment.json` already exists is skipped, so re-running it completes only the missing captures. Then `python .agent-work/epic-298/post/verify_post_arm.py captures`. Engine session-id is `commander-307`; re-claim with `--force --reason "resuming this run"` if the lease blocks.
- **pid:** see `.agent-work/epic-298/post/run_all_post.pid` (rewritten at each detach; "none — foreground" when no capture is in flight)
- **expected artifact:** `.agent-work/epic-298/post/runs/run-{690,688,698,716,704}/treatment.json` — five of them, each reading `TREATMENT-VERIFIED`. Arm-level completion is `.agent-work/epic-298/post/POST_RECORD.md`.

**Do not retry a failed capture to get a better result.** A run whose treatment does not verify
is a FAILED CAPTURE and is reported as one. Retrying until the number comes out right is not
measurement.

**Pinned worktrees:** `C:/Programs/f1bwt/post{690,688,698,716,704}`, all at
`3541d2929b19de37107ae13e56776b7162d07255`. Sweep them at archive with
`git -C C:/Programs/f1Brainz worktree remove --force` plus `worktree prune`.

_Updated: 2026-08-02T19:52:00+00:00_
