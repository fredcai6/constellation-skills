# Crash-resume state note — cleanup-f-derive-worktree

- **step:** **`archive`, `in-progress`** — nine of ten spine steps complete. The
  local half of archive is done (everything committed; five episodes tracked under
  `episodes/active/`; the archive-phase capture gate passes). The publication half
  is **deliberately untouched** and is with the Admiral: see
  **`FLOAT_TO_ADMIRAL-4.md`**.
- **slug:** cleanup-f-derive-worktree · branch `cleanup/f-derive-worktree` ·
  worktree `/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree`
  · code through **`684502ab`** · `main` at **`17c2cee5`**, re-measured and unmoved.
- **next command:** `env -u CREW_SCRATCH_DIR py scripts/checklist_engine.py --file .agent-work/cleanup-f-derive-worktree/spine.json current`
- **pid:** none — foreground, no crew running and none needed.
- **expected artifact:** `crew-handoffs/execute-commander-result.md` — **written and
  current**; read it first.

**Read first on resume:** `crew-handoffs/execute-commander-result.md`, then
`FLOAT_TO_ADMIRAL-4.md`, then `LAUNCH_ORDER-5.md` and `ADMIRAL_RULING-4.md`.

## What is done

`execute.json` terminal (g1/g2/g3 closed on independent APPROVEs; g4 skipped as
withdrawn under R2; g5 skipped as re-homed under R3) · `execute` · `reconcile`
(six stale-claim sites, all prose, suite unchanged at 3192/5/0) · `triage` (21
recommendations in `TRIAGE_RECOMMENDATIONS.md`, four fixed-now, nineteen
recommend-and-defer, nothing filed) · `review` · `feedback` (five episodes +
`FEEDBACK.md`). `REPLAN_INPUT.json` verifies with `D0`–`D28`.

## What remains — all of it the Admiral's call

`archive.c2` (push), `c2b` (an OPEN or MERGED PR), `c3` (release the lease, which
must come **after** the closing `advance`), plus the `git mv` of this work area to
`.agent-work/archive/<date>-cleanup-f-derive-worktree/`. **Do not open a PR or
push on your own authority** — `LAUNCH_ORDER-5` reserves publication to the
Admiral, and `FLOAT_TO_ADMIRAL-4.md` sets out the three ways to close it.

Re-claim as `commander-cleanup-f-derive-worktree`, **never `--force`**. The lease
is deliberately held; release is the final journal entry or the provenance check
fails.

## The two hazards most likely to bite the next agent

- **A governor refusal is not terminal.** The documented sequence is: attach a
  `refresh-request` for the seam, `start` the pending ACTIVE gate (recorded as
  `begin-instructed`, which the compliance selectors do not count), then
  `advance --why`. Better still: **do the gate's substance while it is still
  pending** — `attest` and `attach` are not governor-guarded — so the start begins
  no work it cannot finish. Two legs on this lane parked on the opposite reading.
- **Never poll your own suite run.** Every tool call fires the gauge chain into
  the `.agent-work/` that `test_containment_repo_agent_work_untouched_by_the_chain`
  snapshots, so watching a run turns it red in a way that looks exactly like a
  regression. Run it quiet, or let the engine's postcondition run it.

Also standing: `env -u CREW_SCRATCH_DIR` on every engine call (`tc12`); commit
`crew-runs.json` as each gate closes (#617); name any baseline clone
`constellation-skills` or `MapTreeFreshnessTests` reports a false red.

_Updated: 2026-08-17T03:05:00+00:00 (leg 5, parked at archive with the publication decision floated)_
