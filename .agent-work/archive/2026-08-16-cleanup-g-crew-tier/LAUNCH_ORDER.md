# Launch Order: `cleanup-g-crew-tier — #611`

> Write per `constellation-how-to-talk` — clear, concise, grounded.

Commanders start cold. Everything you need is pasted below. This is a small,
mechanical mission with one trap in it, named at the end.

## Mission

**A crew's model tier must be chosen, and today it never is.** It is inherited
from whatever the dispatching Commander happened to be, or it is nothing at all —
and which of those you get is an accident of the parent's own tier.

Measured across five lanes of this cleanup, 2026-08-16, from the registries
themselves:

```
cleanup-a-door           execute/commander   model='opus'
                         plan/plan-critic    model='opus'
                         g1..g3 implementer  model='opus'   (x5, two of them doc-only reworks)
                         g1..g3 reviewer     model='opus'   (x4)

cleanup-c-liveness-rail  execute/commander   model='sonnet'
                         g1-implement/impl   model=None
                         g1-review/reviewer  model=None
                         g2-implement/impl   model=None
                         g2-review/reviewer  model=None
```

`build_crew_argv` does `if model: argv += ["--model", model]`, so `None` means no
flag reaches the child at all and it falls back to the launcher's global default —
`fable` on this machine, from `~/.claude/settings.json`. An explicitly-Sonnet
Commander therefore dispatched fable crews, and nothing recorded that as a
decision anyone made.

`reasoning_effort` is `None` on every entry across all five lanes. #579 built that
metadata path for the `external` backend and nothing populates it for `cli`.

### Why it is a defect rather than a preference

The place a tier is deliberated and the place it takes effect are disconnected.
`skills/commander/templates/IMPLEMENTER_HANDOFF.template.md:94` and
`skills/commander/templates/REVIEWER_HANDOFF.template.md:60` both carry a
**"Suggested Model Tier"** section — advisory prose a Commander reads and may or
may not turn into `run_crew.py --model`. `skills/commander/references/crew-dispatch.md`,
which is the doctrine for how a dispatch is actually made, does not mention model
at all.

A live example from this cleanup: lane E's reviewer handoff said *"stronger —
concurrency/threading correctness review rewards careful reasoning"*, for a review
of a background-thread change. That request reached nothing; the reviewer ran on
the machine default.

`skills/admiral/templates/LAUNCH_ORDER.template.md` already states the rule this
mission extends: *"Model tier (required) — every dispatch names one, never left
unset."* It binds Commanders and stops dead at the crew boundary.

## Prior-Wave Verdicts (pasted)

From #599, merged at `df6f951b`, because it is the reason the registry is worth
trusting as evidence here: `entry_liveness` corroborates a registry entry rather
than reading its status string, and `active_duplicate` frees a launch slot only on
a corroborated `stale`. The `model` column this mission fills is on the same
entry.

From #607, merged at `0462e315`: `run_crew.py` now heartbeats the dispatching
process's own lease on a background thread while it blocks. **You own that file
too** — do not disturb that thread's start/stop/join ordering, which is
load-bearing (it prevents the heartbeat racing the caller's next mutating write).

## Pre-Rulings

- `decision:refuse-a-tierless-dispatch` — `run_crew.py` refuses a dispatch that
  names no tier, the way the launch order already refuses a tierless Commander.
  Fail closed; do not invent a default.
  `@grade: settled/human · leans g1-implement · settle: if refusing breaks callers that legitimately have no tier to name (tests, tooling, a legacy path), REPORT them rather than adding a silent default — the list is the deliverable, and I will rule on it`
- `decision:do-not-change-what-anything-runs-at` — this mission makes the choice
  **explicit**, it does not pick new tiers. No crew's effective model may change
  as a side effect of this work. If making the choice explicit reveals that some
  dispatch has been running at a surprising tier, that is a finding to report, not
  a thing to fix here.
  `@grade: settled/human · leans all gates`
- `decision:record-the-resolved-tier` — whatever tier a dispatch resolves to is
  written to the registry entry. The column already exists; it is populated for
  `cli` today only when the parent happened to pass one.
  `@grade: settled/measured · leans g1-implement`
- `decision:suggested-tier-becomes-load-bearing` — the handoff templates'
  "Suggested Model Tier" section is the thing a Commander decides **from**. Make
  that connection real in doctrine (`crew-dispatch.md`), so the field stops being
  decorative. Whether it becomes machine-read or stays prose the Commander acts on
  is yours to decide — say which and why.
  `@grade: guess · leans g2 · settle: prefer the smaller change; a field nobody parses but everybody must answer is better than a parser for prose`
- `decision:reasoning-effort-follows-tier` — populate `reasoning_effort` on the
  `cli` path the way #579 does for `external`, **if** the launcher accepts it.
  Check before building: if `claude` has no such flag, say so and leave the field
  alone rather than recording a value nothing consumes.
  `@grade: guess · leans g1-implement · settle: read the launcher's own argument surface first`

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable.
Report it with the same rigor as a win.

## Inherited Latitude

**You may decide:** the refusal's wording and exit code, where the tier is
resolved, whether the handoff field becomes machine-read or stays prose, and test
structure.

**You must float to the Admiral:** any change to what tier a dispatch effectively
runs at; adding a default to satisfy the refusal; touching `checklist_engine.py`,
`scripts/hooks/spine_rail.py` or `scripts/spine_lifecycle.py` (lane F is live in
all three); publication.

## File Ownership

Your working-notes file is `notes-g.md`, sole writer this wave.

> Name it `notes-<n>.md`, **never** `findings-<n>.md` — the harness `Write` tool
> refuses any path whose basename contains "findings".

**Files you own:** `scripts/run_crew.py`, `tests/test_crew_launcher.py`,
`skills/commander/references/crew-dispatch.md`,
`skills/commander/templates/IMPLEMENTER_HANDOFF.template.md`,
`skills/commander/templates/REVIEWER_HANDOFF.template.md`, plus any new test file.

**Fenced — lane F is live:** `scripts/checklist_engine.py`,
`scripts/hooks/spine_rail.py`, `scripts/spine_lifecycle.py` and their tests.

**Fenced — queued work owns these:** `skills/commander/templates/COMMANDER_SPINE.template.json`,
`skills/admiral/templates/LAUNCH_ORDER.template.md`, `skills/admiral/references/fleet-doctrine.md`,
`skills/_shared/**`, `scripts/install_constellation.py` — all of them belong to
#610, which is dispatched next. You are in the same directory as some of these;
stay in your own files.

## Workspace

`/home/tommy/projects/constellation-skills/.worktrees/cleanup-g-crew-tier`, branch
`cleanup/g-crew-tier`, base commit `e0539903`, created with:

```
git worktree add .worktrees/cleanup-g-crew-tier -b cleanup/g-crew-tier e0539903
```

`main` verified fresh at dispatch: `e0539903`, clean tree, suite **3163 passed / 7
skipped / 0 failed**. Re-measure at gate time — lane F is live and may land under
you.

First step, before any git operation: **`cd` into that worktree**, then run `py
/home/tommy/.claude/skills/constellation-admiral/scripts/verify_worktree_isolation.py
--here /home/tommy/projects/constellation-skills/.worktrees/cleanup-g-crew-tier` —
must exit 0, pasted into your report.

> **Order matters.** `--here` asserts about the directory you are standing in. Run
> it before `cd` and you get `fatal: not a git repository`, which reads as "not
> isolated" when the truth is "not arrived". Do **not** pass the path to git
> (`git -C`) — that compares the worktree to itself and disarms the check.

## Inherited Context

- **Platform:** Linux, Python 3.12 as `py`. Suite:
  `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q`.
- **Clear `__pycache__` before every measurement** — a cache built in another tree
  now fails a named test (`tests/test_bytecode_cache_provenance.py`); clear and
  re-measure rather than investigating whatever it lands on.
- **Merge gate:** local Linux green, independent APPROVE, failure-set difference
  against a `main` baseline re-measured at gate time.
- **CI is one `windows-latest` job**, red at baseline. Local Linux is the only real
  signal.
- **The door is usable as of `e3b5a1c8`** (#603): an unbound door refuses by name
  instead of answering about a demo spine, and `run_crew.py --spine` binds each
  child's own `SPINE_FILE`/`SPINE_SESSION`. Drive your own spine through the door
  or the CLI as you prefer; both work now.
- **`map/INDEX.md`** is generated and freshness-tested; rebuild and commit if
  entities change. It conflicts on every parallel branch (#544) — regenerate,
  never hand-merge.

## Pre-empted Steps

- **Context is established by this order**, including the registry measurements
  above, taken 2026-08-16.
- **The worktree is provisioned and gate-verified.**
- **Triage is done.** #611 carries the mechanism and the fix directions.

## Data Locations

- The measurements quoted above came from the archived registries on `main`:
  `.agent-work/archive/2026-08-16-cleanup-*/crew-runs.json`. Read them rather than
  re-deriving; they are the evidence.
- `build_crew_argv`'s `if model:` line and the `--model` plumbing:
  `scripts/run_crew.py`.

## Budget

- **Model tier (required):** Sonnet 5. Mechanical change, named seams, pre-ruled
  direction.
- **Compute/time, session-window:** one working session.

## The trap in this mission

**You will dispatch crews while fixing how crews are dispatched.** Two things
follow.

First, **name a tier for every crew you dispatch**, explicitly, from the moment
you start — before your own change makes it mandatory. If you inherit or default
one, you have reproduced the defect inside its own fix, and your registry will say
so.

Second, if you make `--model` required, **your own later dispatches must satisfy
it**. Sequence the change so you do not lock yourself out mid-run: a refusal that
lands between your implement and review gates will stop your own reviewer from
launching. Say in your report how you sequenced it.

## Stop Conditions

Stop and return when scope is exceeded, a decision outside your latitude is
needed, the budget is crossed, evidence is impossible, or you need context this
order does not cover — return-and-query the Admiral. Asking up is always
sanctioned.

**Arriving over the context HARD band is not a stop condition.** The engine
refuses only `start` and `reopen`, and only until a refresh-request exists for
that gate: attach the refresh-request against the current why-record, then
`start`, then work. Do not read a HARD advisory, or an inherited
`REFRESH REQUESTED:` line, as an instruction to hand off on turn one.

## Return Shape

A verdict — shipped, blocked with a measured reason, or an honest null — plus:

1. **Red/green for the refusal**: a dispatch with no tier refused, one with a tier
   accepted, and the resolved tier present on the registry entry afterward.
2. **The caller list**, if refusing broke anything that legitimately has no tier to
   name. That list is a deliverable, not a failure.
3. **What you did about `reasoning_effort`**, including the launcher's actual
   argument surface if you left it alone.
4. **Your own dispatch record** — the `model` field on every crew you launched
   this run, as evidence you did not reproduce the defect while fixing it.
5. **Full clean-env, cache-cleared suite** at your published head, plus a `main`
   baseline re-measured at gate time.
6. **Map impact**, triage candidates, workflow feedback, and your `--here` output.

Park at `archive`. **Do not merge** — publication is the Admiral's class.
