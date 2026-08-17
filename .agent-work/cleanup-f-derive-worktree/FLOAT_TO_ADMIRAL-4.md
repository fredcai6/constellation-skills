# Float to Admiral 4 — lane F, from leg 5 at `archive`

**One decision, not blocking anything else.** Nine of ten spine steps are
complete. `archive` is `in-progress`, its local half done, its publication half
untouched.

## The conflict, stated exactly

`archive` carries three postconditions I will not satisfy on my own authority:

| id | requires | status |
|---|---|---|
| `c2` | branch committed **and pushed** | committed; **not pushed** — no upstream configured |
| `c2b` | an **OPEN or MERGED** pull request for this branch | **none exists** |
| `c3` | engine session lease **released**, as the very last action after the closing `advance` | **held** |

`LAUNCH_ORDER-5` says: *"Park at `archive`. Do not merge. Publication is mine and
nothing is queued behind you."*

A push to `origin` and a PR are both outward-facing publication of your epic's
work. Waiving `c2b` would also be a call about how this branch reaches you, not a
mechanical detail — so I recorded the conflict instead of resolving it.

## What I did not do, and why

- **Did not push, did not open a PR.** Publication is reserved to you in the
  frozen order, and neither action is reversible in the way a local commit is.
- **Did not waive `c2`/`c2b`.** A waive records *who accepted the risk*; the only
  authority for this one is yours, and inventing it would make the spine terminal
  without anyone having decided anything.
- **Did not move the work area** to `.agent-work/archive/<date>-cleanup-f-derive-worktree/`,
  which the archive imperative also asks for. `spine.json` lives inside that
  directory; moving it while the spine is non-terminal would strand the next
  leg's `--file` path. It is a `git mv` once the spine is done.
- **Did not release the lease.** Release is last by construction — it must come
  after the closing `advance`, so releasing now would leave the closeout's own
  journal entries outside the lease and fail the terminal provenance check.

## Three ways to close it, all cheap

1. **Authorize publication.** Say so, and a leg pushes, opens the PR, moves the
   work area, advances `archive`, and releases the lease. Perhaps ten minutes.
2. **Waive `c2`/`c2b` with the fence as the reason**, then the same leg finishes
   the rest. This keeps publication yours while letting the spine reach terminal.
3. **Take the branch yourself.** Everything you need is committed and named in
   `crew-handoffs/execute-commander-result.md`; close the spine as part of
   publication.

## The check's own text argues for option 1, and you should know that

`c2b` does not merely demand a PR — it says, in its own words: *"Open the PR even
if the work is unfinished; declare FINAL or PENDING in its title and **hand the
merge up**."* On that reading a PENDING PR is not publication competing with
yours; it is the mechanism for handing the merge to you, and the thing your order
forbids — merging — stays forbidden either way. Its stated reason is that CI never
runs on an unopened branch, and that every commander which reached a terminal
spine without opening one had to be chased for it.

I still did not open it, because your order reserved publication in words that
cover a push to `origin`, and because an outward-facing action is the wrong place
for me to resolve an ambiguity in my own favour. But if your intent was "do not
merge" rather than "do not surface", **option 1 is the one the engine was designed
around** and one sentence from you closes this lane.

## One thing to weigh, briefly

The order and the spine disagree here **every time** a lane is told to park at
`archive` — `c2b` is unconditional. This is the second lane-level fence I have
seen collide with it. Whether the archive step should carry a fenced variant of
`c2b`, or whether launch orders should waive it explicitly when they fence
publication, is a doctrine question rather than a lane one. Recorded here so it
is visible; not asking you to settle it now.

## Not blocking

Nothing else waits on this. The lane's code is written, reviewed, approved,
measured and committed; the triage is routed; the episodes are captured and
tracked; the replan packet verifies. This is the last decision on lane F.
