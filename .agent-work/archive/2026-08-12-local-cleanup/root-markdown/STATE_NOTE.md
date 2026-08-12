# Crash/handoff resume state — `cmdr-440-binding-cwd` (issue #440)

**Status: run COMPLETE and green; archive BLOCKED on an action reserved for the Admiral.**
This is a handoff, not a crash.

| | |
|---|---|
| step | `archive` — **blocked**, bubbled to parent |
| spine | `.agent-work/archive/2026-08-07-issue-440-binding-cwd/spine.json` (moved by the archive step) |
| lease | `cmdr-440-binding-cwd` — **STILL HELD, deliberately** |
| worktree | `C:/Programs/constellation-skills-wt/epic418-a2-440` |
| branch | `epic-418/a2-440-binding-cwd` @ `9dd21c9`, clean, 7 commits on `cbd9aee` |
| result artifact | `RETURN.md` at the worktree root |

## Why the lease is still held

The archive step is explicit: release only **after** the postconditions pass and the closing
`advance` runs, because releasing earlier leaves archive's own closeout entries after the release and
fails the terminal provenance check. `c2`/`c2b` have not passed, so releasing now would corrupt the
provenance. It is held on purpose, not abandoned.

## What is blocked, and why it is not a failure

`c2` (branch pushed) and `c2b` (open PR). My dispatch reserves both: *"Do NOT push, open a PR, or
merge — that is the Admiral's step."* `_COMMON.md` does pre-clear `git push on epic-418/*` and
`gh pr create`, so this is **not** a permission block and not the #145 environmental shape — the
capability exists and I declined to use it because my principal withheld it.

## Next commands, for whoever picks this up

```bash
cd C:/Programs/constellation-skills-wt/epic418-a2-440
git push -u origin epic-418/a2-440-binding-cwd
gh pr create -F <body-file>          # -F, never --body, on Windows
# then, against the MOVED spine path:
python scripts/checklist_engine.py --file .agent-work/archive/2026-08-07-issue-440-binding-cwd/spine.json current
```

Declare **FINAL** in the PR title — the run is complete and green, not partial.

Then satisfy `c2`/`c2b`, check `c4` (git-change-policy; a human waives it via the engine override path
if anything in the staged diff is intentional), run the closing `advance archive`, and **only then**
`release --session-id cmdr-440-binding-cwd` as the final journal entry.

## Two things to handle at PR time

1. **Base drift.** `main` has advanced to `4fbdf6e` (`to-issues` → `to-initial-issues` plus the new
   `replan` skill); this branch is based on `cbd9aee`. The dispatch said this is handled at PR time,
   so no rebase was done mid-gate.
2. **Harvest the staged feedback.** `.agent-work/staged-feedback/issue-440-binding-cwd/` — its
   `FENCE.md` lists the three harvest steps and pastes the validated `--dry-run` output, so the delta
   is not applied blind.

## Needs adjudication (both detailed in `RETURN.md` §7)

- The `FORCE_COLOR` false-red invalidates the recorded `cbd9aee` baseline of `exit 0` and affects
  **every** Commander dispatched into this repo. Filed **#454**; belongs in `_COMMON.md` beside the
  `py` warning.
- **#452**'s fix may require changing the gauge binding key shape, which is outside Commander
  latitude.
