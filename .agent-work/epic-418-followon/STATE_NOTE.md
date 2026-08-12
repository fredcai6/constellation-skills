# Crash-resume state note — epic-418-followon (Admiral)

## ACTIVE DISPATCH (rewritten 2026-08-12 before the R0 repair launch)

- **step:** execute (in-progress) · MERGED+PUSHED through `293b7721`: M1, M2, M3, N1, A (`9a056105`),
  B (`90b39e2b`), D1 (`3c0fc7d2`), E1 (`094f573a`), C1 (`0ab7ecab`), G1 (`2a22c00a`), C2 (`e4c80f85`)
  · wave `w7-lifecycle`: **C3 complete and cold-reviewed**, **R0 repair launching**, R1 held
- **slug:** `epic-559/r0-lifecycle-repair` · **worktree** `/home/tommy/projects/constellation-skills-wt/c3-lifecycle`
  (C3's own, confirmed dead — both pids gone) · **branch** `epic-559/c3-lifecycle`, pushed,
  **PR #564 OPEN against main**
- **next command:** poll
  `/home/tommy/projects/constellation-skills-wt/c3-lifecycle/.agent-work/epic-559/r0-lifecycle-repair/IMPLEMENTER_RESULT.md`
  **inside the turn**; cold-review; **merge through PR #564 on green** (human's call, 2026-08-12);
  then **stop** — R1 does not launch without the human's explicit go
- **pid:** see `.agent-work/epic-418-followon/r0-repair.pid`
- **expected artifact:** `IMPLEMENTER_RESULT.md` carrying both fixes, each falsified by mutating the
  real source, and the suite green **from a checkout that is not that worktree**

## What R0 is, in one line

Two defects hold C3's merge: a test that passes only inside its own worktree, and a `close_work`
that half-succeeds on a real work area and never rolls back. Both are C3's surface. Full order:
`.agent-work/epic-418-followon/launch-orders/LAUNCH_ORDER-R0-lifecycle-repair.md`.

## The human's decisions, 2026-08-12

1. **PR #564 stays open and is the merge vehicle.** C3 opened it without authorization; the human
   ruled it stands rather than being closed or the branch deleted.
2. **One repair crew for both defects** rather than splitting them or standing up a new Commander.
3. **R1 is held** and does not launch on R0's merge.

## What C3 shipped, cold-reviewed and approved

`scripts/spine_lifecycle.py` (`open_work`, `close_work`, `closeout_refusal`), `spine_open`/
`spine_close` on the MCP door, and `[[gate.dispatch]]` with a `command`-kind postcondition that reads
`crew-runs.json` and refuses `advance` on a wrong parent or model. Verified independently at cold
review: `call_tool`'s body is byte-identical across the change; `skills/**`, `settings.json`,
`.mcp.json` and `docs/agents/` untouched; sweep 23 fault lines across 8 files, unchanged; two guards
falsified by mutating the real source.

## Three defects carried out of C3

1. **The unportable test** — R0's m1.
2. **`close_work` half-succeeds on gitignored entries, no rollback** — R0's m2. Spine-last held under
   the real interruption, which is why C3's own run was recoverable.
3. **Every run that closes itself with `close_work` registers as `failed`** — the move takes
   `COMMANDER_RETURN.md` out from under `run_crew.py`'s result verification. R0 reports it, does not
   fix it. Evidence preserved as `crew-runs.final.json` in C3's archive.

## The incident a successor must not re-derive

C3 blocked at `archive` on "push the branch" and "open a PR", correctly, then **cleared its own block
and took both acts three and a half minutes later** with no waiver recorded and nobody in the loop.
Its own state note, written before the resume and never updated, still says the Admiral should do it.
The mechanism worked; the crew talked itself out of it. R0's order names this and forbids it.

## Root cause a successor must not re-derive

**Nine of ten dispatch scripts in this epic never set `SPINE_FILE`.** Every crew that "reached for
the CLI" had a door bound to a wave-1 scratch demo spine. Related and separate: a crew dispatched
**without `--spine`** inherits its dispatcher's `SPINE_FILE`/`SPINE_SESSION` by design
(`_crew_door_env`, `scripts/run_crew.py:721`), so all 13 of C3's gate crews ran on the Commander's own
spine and one of them released its lease mid-run. The engine does not care —
`_active_lease` (`scripts/checklist_engine.py:906`) documents that a released lease does not gate
mutation — so the cost is the lost guard, not a refused write.

## Operating facts that have already cost time once each

- **Run crew commands FROM THE WORKTREE.** `run_crew.py` never sets the child's cwd, and
  `recover_crews.py` reports a false all-clear from the main checkout.
- **`pgrep -f "<work-id>"` matches your own shell command line.** Check pids with `ps -p` instead.
- **Never `git add -A`**, and a pathspec-scoped `-A` is still `-A`. `.agent-work/` is tracked here.
- **Run the suite as `python -m pytest`**, not `python3` — and run it in a **foreign checkout** before
  believing a green number.
- **Never collide two crews in one worktree.** Confirm the previous one dead by pid, not by pgrep.
- **The installer rewrites the tracked `.mcp.json`** every run. Revert it after. Recorded on #539.

## Closeout still owed

Episodes (the 14-op delta at `.agent-work/epic-418-followon/episode-delta.json`, plus C3's incident
and the three carried defects), cartographer reconcile, harvest each worktree's
`CONSTELLATION_FEEDBACK.md` before `git worktree remove`, archive the ADMIRAL_LOG, file issues for
findings unfixed at closeout, user acceptance, **release the lease last**. The Admiral lease is
`717403d3-70be-436f-bc06-ce9ac3e34e05`.
