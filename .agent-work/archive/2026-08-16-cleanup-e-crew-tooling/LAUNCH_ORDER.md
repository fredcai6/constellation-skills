# Launch Order: `cleanup-e-crew-tooling — #607, #525`

> Write per `constellation-how-to-talk` — clear, concise, grounded.

Commanders start cold. Everything you need is pasted below.

## Mission

Two defects in crew tooling, same file, same subsystem. Both are about a crew's
run being legible to everyone else while it happens.

**1. #607 — a Commander blocked on its own crew goes lease-stale while perfectly
healthy.** `run_crew.py` blocks by design, and the doctrine says it should. A
parent sitting in that blocking call issues no mutating verb, and the engine's
heartbeat is a side effect of mutating verbs. So a healthy parent stops
heartbeating for exactly as long as its child runs. **Measured on 2026-08-16: 53
minutes blocked on a live crew, at which point the engine already considered that
lease stale.**

Nothing is broken today — `#599`'s external-entry window is 8h and the observation
is 53m — so this is a hazard filed before it fires. But `#599`'s `entry_liveness`
judges pid-less entries by heartbeat age, `claim --force` reclaims a lease the
engine calls stale, and `#552` proposes a reaper. Every one of them reads a signal
a blocked-but-healthy parent cannot emit. The failure mode is a force-claim of a
spine **out from under a running parent** — two agents on one spine, the exact
collision the lease exists to prevent.

**2. #525 — concurrent crews share one scratch directory and write evidence under
generic names.** During issue #456 a `g8` reviewer found `r0` through `r6`
finding-files already sitting there from an **earlier gate's reviewer**, written
with the same generic names it was about to use. It noticed and prefixed its own.
The next crew silently overwrites the previous crew's evidence, and the loss is
invisible: the file exists, it parses, it describes someone else's gate. Catching
it depended on one agent happening to look.

Its other half — "no liveness signal for a dead crew" — was closed by #599 on
2026-08-16. Do not re-litigate that; #525 is now the scratch-collision issue only.

## Prior-Wave Verdicts (pasted)

From **#599**, merged to `main` at `df6f951b` this morning, which you must build on
rather than around:

> `entry_liveness(entry, now, alive) -> "active" | "stale" | "unknown"` corroborates
> before `active_duplicate` answers. Three buckets: `pid` truthy → `alive(pid)`;
> `pid` falsy and backend `external` → heartbeat age against
> `HEARTBEAT_STALE_SECONDS = 28800`; anything else → `unknown`. `active_duplicate`
> frees the launch slot only on a corroborated `stale`; `active` and `unknown` both
> still block. Nothing in the change sets `abandoned` — reaping stays a separate
> decision with its own blast radius.

The 8h window is measured, not chosen: longest genuinely-`completed` external run
~3h30m, shortest confirmed phantom ~22h27m.

From the run that found #607, in its own words:

> `run_crew.py` is blocking by design and a parent waiting on a child issues no
> mutating verb, so it cannot heartbeat. Measured: 53 minutes blocked on a live
> crew, and the engine already called that lease stale. Anything judging liveness
> by heartbeat can force-claim a spine out from under a running parent.

## Pre-Rulings

- `decision:registry-before-staleness` — a liveness reader consults the crew
  registry before calling a lease stale. A parent with a live child is not idle,
  and that fact is **already recorded** in `crew-runs.json`. This is the smallest
  fix and it composes with what #599 shipped.
  `@grade: guess · leans g1-implement · settle: try it first; if the registry lookup cannot be made available where staleness is judged, say so with the measurement and float the alternatives`
- `decision:no-reaping` — nothing in this lane marks an entry or lease
  `abandoned`, expires it, or force-claims anything. Report state; do not act on
  it. Reaping is #552's, with its own blast radius.
  `@grade: settled/human · leans all gates`
- `decision:fail-toward-alive` — every ambiguity resolves toward "this thing is
  running". A live parent wrongly declared stale is the failure being fixed; do not
  introduce a new one in the opposite direction.
  `@grade: settled/human · leans all gates`
- `decision:namespace-by-assignment` — #525's scratch path is namespaced by
  work-id + gate + role (+ attempt where it exists), the same tuple the registry
  already keys on, rather than by anything new.
  `@grade: guess · leans g2-implement · settle: check what the registry keys on and reuse it verbatim rather than inventing a parallel identity`
- `decision:no-silent-truncation` — if an evidence file would collide under the
  new scheme, that is an error someone hears about, not a quiet overwrite. The
  whole point of #525 is that the loss was invisible.
  `@grade: settled/measured · leans g2-implement`

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable.
Report it with the same rigor as a win.

## Inherited Latitude

**You may decide:** where the registry consultation sits, the namespacing scheme's
exact shape, the error surface for a collision, and test structure.

**You must float to the Admiral:** any change that makes a liveness reader
*shorten* a window or declare something dead sooner; any reaping, expiry or
force-claim; any change to `checklist_engine.py`'s lease semantics; publication.

## File Ownership

Your working-notes file is `notes-e.md`, sole writer this wave.

> Name it `notes-<n>.md`, **never** `findings-<n>.md` — the harness `Write` tool
> refuses any path whose basename contains "findings".

**Files you own:** `scripts/run_crew.py`, `scripts/recover_crews.py`,
`tests/test_crew_launcher.py`, and any new test file for either.

**Fenced — do not touch:** `scripts/mcp_spine_server.py`, `.mcp.json`,
`examples/**`, `scripts/install_constellation.py` and
`skills/commander/templates/**` (lane A is live in all of those),
`scripts/checklist_engine.py`, `scripts/gauge_reader.py`,
`scripts/hooks/gauge_writer_hook.py`.

`scripts/hooks/spine_rail.py` is **not** owned by you and should not need
changing. If your fix genuinely requires it, float before touching it.

## Workspace

`/home/tommy/projects/constellation-skills/.worktrees/cleanup-e-crew-tooling`,
branch `cleanup/e-crew-tooling`, base commit `e36e630b`, created with:

```
git worktree add .worktrees/cleanup-e-crew-tooling -b cleanup/e-crew-tooling e36e630b
```

`main` verified fresh at dispatch: `e36e630b`, clean tree, suite **3103 passed / 7
skipped / 0 failed**. That is your baseline, and you re-measure it at gate time
anyway because lane A is live and may land under you.

First step, before any git operation: **`cd` into that worktree**, then run `py
/home/tommy/.claude/skills/constellation-admiral/scripts/verify_worktree_isolation.py
--here /home/tommy/projects/constellation-skills/.worktrees/cleanup-e-crew-tooling`
— must exit 0, pasted into your report.

> **Order matters.** `--here` asserts about the directory you are standing in. Run
> it before `cd` and you get `fatal: not a git repository`, which reads as "not
> isolated" when the truth is "not arrived". Do **not** pass the path to git
> (`git -C`): that compares the worktree to itself and disarms the check
> (#315 / PR #576).

**Isolation is git-only — hook code is not fenced by it.** `CLAUDE_PROJECT_DIR` is
resolved once at session launch and inherited unchanged by every subagent, so your
worktree still runs the **main checkout's** hook code against the **main
checkout's** state (#269). This lane should not need hook changes, but it does
change how a crew's own liveness reads — so validate in a **fresh process**, never
by reasoning about the session you are in.

## Inherited Context

- **Platform:** Linux, Python 3.12 as `py`. Suite:
  `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q`.
- **Clear `__pycache__` before every measurement.** As of `43c577d4` a cache built
  in another tree fails a **named** test
  (`tests/test_bytecode_cache_provenance.py`) instead of surfacing as an unrelated
  assertion — if you see it, clear and re-measure rather than investigating the
  assertion it lands on.
- **Merge gate:** local Linux green, independent APPROVE, failure-set difference
  against a `main` baseline re-measured at gate time.
- **CI is one `windows-latest` job**, red at baseline. Local Linux is the only real
  signal. `os.kill(pid, 0)` is POSIX; `process_alive` already carries the
  cross-platform seam — do not break it.
- **Drive your spine through the engine CLI** with an explicit `--session-id`. The
  door is bound per-crew by `run_crew.py --spine`, but the operator-side binding is
  still broken and is lane A's mission (#603).
- **You will be living inside your own bug.** This Commander dispatches crews and
  will itself go lease-stale while blocked on them. Note what that does to you —
  it is the best evidence anyone will get, and #607 was found exactly that way.
- **Relaunch works:** re-claiming your own lease re-stamps `claimed_at` (#601), and
  a reading is now owner-keyed (#600), so a fresh leg gets its own number. Never
  pass `--force` for a routine relaunch.
- **`map/INDEX.md` is generated and freshness-tested** — rebuild and commit if
  entities change. It conflicts on every parallel branch (#544); resolve by
  regenerating, never by hand-merging.

## Pre-empted Steps

- **Context is established by this order.**
- **The worktree is provisioned and gate-verified.**
- **Triage is done.** #607 carries the measurement and three fix directions; #525
  carries its own repro. Implement; do not re-triage.

## Data Locations

- The registry shape you are reasoning about, with real entries including the
  phantom and healthy external runs #599's window was derived from:
  `.agent-work/archive/*/crew-runs.json` on `main`.
- #599 as merged: `scripts/run_crew.py`, `entry_liveness` at `:264` and
  `active_duplicate` at `:330`.
- The lane that measured #607: `.agent-work/archive/2026-08-16-cleanup-b-context-identity/`.

## Budget

- **Model tier (required):** Sonnet 5. Both changes have named seams and pre-ruled
  directions. **Escalate to Opus 5 and tell the Admiral** if the registry
  consultation turns out to need a change where staleness is judged rather than
  where it is read.
- **Compute/time, session-window:** one working session. #607 first — it is the one
  that can lose a running agent's work.

## Stop Conditions

Stop and return when scope is exceeded, a decision outside your latitude is
needed, the budget is crossed, evidence is impossible, or you need context this
order does not cover — return-and-query the Admiral. Asking up is always
sanctioned.

**Arriving over the context HARD band is not a stop condition.** It is an absolute
token cap, so you can be over it on turn one having done nothing. The engine
refuses only `start` and `reopen`, and only until a refresh-request exists for that
gate: **attach the refresh-request against the current why-record, then `start`,
then work.** Do not read a HARD advisory, or an inherited `REFRESH REQUESTED:`
line, as an instruction to hand off on turn one.

Handing off at a clean gate boundary when your context is genuinely spent is
**correct** and is how the last two lanes finished. Running long to avoid a
handoff is not.

## Return Shape

A verdict — shipped, blocked with a measured reason, or an honest null — plus:

1. **Evidence per defect.** For #607: a blocked parent that used to read stale and
   now does not, driven through the real registry and the real staleness path. For
   #525: two crews whose evidence used to collide and now does not, plus the error
   surface when a collision is genuinely unavoidable.
2. **Full clean-env, cache-cleared suite** at your published head, plus a `main`
   baseline re-measured at gate time.
3. **Map impact**, triage candidates, workflow feedback.
4. Your `--here` output.

Park at `archive`. **Do not merge** — publication is the Admiral's class.
