# Commander result — `cleanup-f-derive-worktree` (#609 lane F), leg 6 — terminal

## Assigned

`LAUNCH_ORDER-6.md` — bookkeeping only. Re-claim, waive `c2` and `c2b` on the
Admiral's authority, move the work area into the archive, `advance archive`,
`release`, commit. Do not merge and do not push.

## Return status

`final` — **the spine is terminal, the lease is released, and the work area is
archived.** Every step of the order was carried out. Two mechanism frictions are
reported below; neither changed an outcome, and neither needed a decision from
you before I could finish.

## What I did, in the order I did it

1. **Re-claimed** as `commander-cleanup-f-derive-worktree`, no `--force`. The
   lease was still mine from leg 5, so the claim was idempotent — it re-stamped
   the claim and refreshed the heartbeat.
2. **`resume archive`**, citing `ADMIRAL_RULING-5` as the cleared blocker.
3. **Added the reconcile-scoping finding to `FEEDBACK.md`** (it was not there).
   It sits beside the citation rule, as you asked: *scope a prose repair by the
   claim family, not by the file list; grep a fragment short enough to survive
   line wrapping.*
4. **Waived `c2` and `c2b`**, authority `admiral-568-cleanup`, reason recorded
   **verbatim** from `ADMIRAL_RULING-5`. Nothing else waived. `c3` was attested,
   not waived — release stayed last by construction.
5. **Staged the diff** (this run's bookkeeping under `.agent-work/`, nothing
   else) so `c4` inspected real content rather than an empty index.
6. **`advance archive`** → `complete`, with `c1` re-verified at the gate
   (5 episodes, tracked by git) and `c4` clean. Spine terminal: no open items.
7. **`release`** — the last journaled action.
8. **`git mv`** the work area to
   `.agent-work/archive/2026-08-17-cleanup-f-derive-worktree/`.
9. **Committed.** Not merged, not pushed.

## The sequence I used for the move, and why — evidence for #574

**Order used: close `archive` → `release` → move → commit.** The move came last
of the three, after the release, not between the close and the release.

The reason is the one I flagged and you confirmed: `spine.json` and
`spine.json.journal` live *inside* the directory being moved, and both the engine
CLI (`--file`) and the MCP door read the spine at the path they were given at
launch (`SPINE_FILE`). Moving before either the `advance` or the `release` would
have broken the path out from under the two calls that still had to reach it.

Closing between the move and the release was not available for the same reason:
`release` is an engine call, so it needs the spine at its original path just as
much as `advance` does. That leaves exactly one safe cut point — after the last
engine call and before the commit — which is where I put it.

**What this costs, and it is worth stating for the verb's design.** The commit
that carries the archived tree is made *after* the spine is terminal and the
lease is released, so nothing checks it. `c4` inspected the staged diff at
`advance` time; the `git mv` that follows adds ~400 renames that no gate ever
sees. A closeout verb that owns both the move and the commit would close that
window, because it could do the move under its own supervision instead of asking
the lane to sequence it by hand.

**Second hazard for the verb.** The work area is written to *while it is being
archived*. The gauge writer fires on tool calls and writes into the work area by
its original path, so the moved-away directory can be recreated underneath the
lane after the move. The `-post-archive` directories already in
`.agent-work/archive/` are the same footprint. A closeout verb should either move
last-of-all under its own control or expect to sweep a stub. **It did not happen
on this leg** — I checked after the commit and the old path is absent — so this
is a hazard the design should cover, not damage you need to clean up here.

## The one-test discrepancy: accounted, cheaply

**It is `tests/test_spine_lifecycle.py::TestWorktreePathForRealWorktree`, and it
is location-dependent by design.**

The test asserts that `worktree_path_for()` reproduces the *ambient* checkout's
own path. It only applies where the checkout follows the `<wt_root>/<work-slug>`
convention, and it says so in its own skip reason. Measured just now, both arms,
one selector:

| where | verdict |
|---|---|
| this worktree (`.worktrees/cleanup-f-derive-worktree`) | **1 passed** |
| the primary checkout (`/home/tommy/projects/constellation-skills`) | **1 skipped** — "this checkout is not directly inside `…/.worktrees`" |

That is the whole difference. I measured from a conforming worktree, where it
runs; you measured merged `main` from the primary checkout, where it skips. The
totals agree — 3197 collected on both arms — so one test moved from passed to
skipped and none appeared or vanished. It is consistent with your pre-gate arm
too: `main` at `17c2cee5` measured 3171/7 in an isolated clone, which is also not
a conforming worktree.

**No defect here.** The location-dependence is deliberate, and #598's closeout
already built the constructed-topology twin
(`TestDefaultLayoutAgainstAConstructedTopology`) for exactly this reason — so the
composition is covered wherever anyone measures, not only from a worktree.

## Two mechanism frictions, reported not worked around

- **`c2` and `c2b` are not declared waivable, so both waives are recorded
  `FORCED`.** Neither condition carries an `override_policy`; only `c4` does. The
  engine refused the plain waive and named `--force` as the deliberate override,
  which is what I used, with your authority and your verbatim reason. The record
  says `forced: true` on both. I did not hand-edit the spine and I did not widen
  the waive. If the parked-lane path is going to be normal — and this is the
  second lane to need it — `c2`/`c2b` should declare an `override_policy` with
  `authority: human`, so that handing the merge up is an ordinary override rather
  than a forced one. That is the same design seam as the `c2b`-versus-launch-order
  collision you are already taking to #574.
- **The MCP door could not release this lease.** `archive`'s own imperative says
  to release through the `spine_lease` tool because "the door needs no session id
  argument". The door derives its session id from `SPINE_SESSION`
  (`constellation/cleanup-f-derive-worktree/archive/commander`), but the lease is
  held under the id your order mandated, `commander-cleanup-f-derive-worktree`, so
  the door refused: *does not own the lease*. I used the CLI fallback the same
  imperative names, `release --session-id commander-cleanup-f-derive-worktree`,
  which worked and needed no force. The imperative's default and the launch
  order's lease id disagree whenever a lane is re-claimed under a stable id across
  legs — which is every multi-leg lane.

## State at hand-off

- **Branch** `cleanup/f-derive-worktree`, clean, two commits ahead of the
  published `f367cb7d` — your `2e579b6b` (ruling 5 and this order) and my closeout
  commit. Both are `.agent-work/` bookkeeping; no executable line moved on this
  leg. Not merged, not pushed — yours to take.
- **Spine** terminal: `DONE: no open items`, waived `archive.c2`, `archive.c2b`.
- **Lease** released; `released_at` recorded in `engine_session`.
- **Work area** at `.agent-work/archive/2026-08-17-cleanup-f-derive-worktree/`.
- **Record** — five episodes under `episodes/active/cleanup-f-derive-worktree-001`
  …`-005`, tracked by git, already published in `main` at `f367cb7d`. The record
  outlives this worktree.

## After me

Nothing. Lane F is done.
