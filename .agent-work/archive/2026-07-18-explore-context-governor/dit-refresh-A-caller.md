# Refresh — design A (constraint: COMMON-CALLER-FIRST / REUSE EXISTING MACHINERY)

Panel: design-it-twice, "Refresh" (context-governor module 4). Constraint assigned to this
design: shape the handoff + signal to reuse what constellation already has — the
`LAUNCH_ORDER`-shaped payload, the crew-dispatch/`run_crew` registry, the existing
`STATE_NOTE` — and minimize NEW protocol. Reach-up itself is settled (X3): Commander
refreshes implementer/reviewer, Admiral refreshes Commander, human at the top. The open
question is packaging + signal only.

## Grounding — what each invoker already knows how to consume

Read `run_crew.py` (Commander's crew launcher), `recover_crews.py` (the classifier),
`fleet-doctrine.md`'s recovery drill (Admiral tier), and the `LAUNCH_ORDER`/`STATE_NOTE`
templates. Three edges, three different "already known" machineries — not one:

- **Commander → implementer/reviewer.** The actual dispatch backend in this harness is
  `ExternalBackend` (Agent-tool subagent — no headless `claude` CLI, so `dispatch` records a
  durable `crew-runs.json` entry and spawns nothing; `pid` is always `None`). Recovery runs
  through `classify_entry(entry, alive, result_present)` — a **pure** function over three
  facts (recorded status, PID liveness, result-artifact existence) — before `execute` and
  before every crew dispatch (already Commander doctrine, not new). Critically:
  `CliBackend.resume()` relaunches a **fresh subprocess** that re-reads the stored handoff
  from disk (not a session-continue) — the crash-recovery resume path already IS "fresh
  re-instantiation from a handoff," which is exactly what module 4 wants. But
  `ExternalBackend.resume()` deliberately **refuses** ("unrecoverable by wrapper") and forces
  the Commander to pick one of two existing actions: `SendMessage` to the crew's agentId
  (**continues with full context** — fleet-doctrine.md line 95-97) or `--abandon <session>
  --relaunch` (bumps `attempt`, a **fresh** dispatch via the same Agent-tool call pointed at
  a handoff path). This fork already exists and already has the right answer sitting in it.
- **Admiral → Commander.** No `run_crew.py` exists under `constellation-admiral/scripts/` —
  Commanders are Agent-tool subagents tracked only by `LAUNCH_ORDER.md` + git worktree +
  `ADMIRAL_LOG.md` `WAVE`/`INCIDENT` entries, resumed per the fleet-doctrine recovery drill:
  `SendMessage` if stalled-but-**alive**, a fresh agent pointed into the worktree if
  **confirmed-dead** ("resume from the engine's on-disk spine/execute state — do not restart
  from zero"). This is a doctrine drill a human/Admiral runs, not a machine classifier.
- **Commander → human.** No machinery at all — a person reading a report, informed by
  whatever channel the Commander already reports through (interactive vs
  delegated-with-launch-order).

**Honest scoping of the assigned constraint:** "the crew-dispatch/`run_crew` registry" is
real and reusable **only** at the Commander↔crew edge. Forcing that same registry onto the
Admiral↔Commander edge would not be reuse — that registry doesn't reach that far in this
codebase today. This design reuses whichever caller machinery each edge *actually has*
(registry+classifier for crews, `LAUNCH_ORDER`+`STATE_NOTE`+`ADMIRAL_LOG` doctrine for
Commanders, plain reporting for the human) rather than inventing one uniform mechanism that
would itself be new protocol at two of the three edges.

## The handoff payload — `REFRESH_HANDOFF.md`

One template, reusing `LAUNCH_ORDER.md`'s section skeleton verbatim (same headers: Mission,
Prior-Wave Verdicts, Pre-Rulings, Honest-Null Clause, Inherited Latitude, File Ownership,
Workspace, Inherited Context, Pre-empted Steps, Data Locations, Budget, Stop Conditions,
Return Shape) — a fresh agent at any tier already knows how to read this shape; no new
document grammar to learn. Path convention matches where handoffs already live:
`.agent-work/<work_id>/<gate>-<role>/REFRESH_HANDOFF.md` for crews,
`.agent-work/<work_id>/REFRESH_HANDOFF.md` for a Commander-tier refresh (siblings to
`STATE_NOTE.md`).

The load-bearing change from `LAUNCH_ORDER` is **what each field is allowed to contain**,
per X1's Pocock finding ("reference, don't duplicate"):

- **Mission / Close criteria / constraints / map anchors** — a **pointer**, not pasted text:
  "unchanged from `<original handoff path>` — read it, nothing here supersedes it." The
  original `IMPLEMENTER_HANDOFF.md`/`REVIEWER_HANDOFF.md`/`MISSION_FRAME.md` is durable and
  already on disk; re-typing it here would be exactly the duplication X1 flags.
- **Seam pointer (new, small):** `work_id`, `gate`/spine-step id, attempt number, and which
  Trip band fired (`soft-accepted` / `soft-declined-then-forced` / `hard`) — reusing Trip's
  existing two-band vocabulary, no new taxonomy.
- **Why pointer (new, small, the one genuinely new field this module owes):** not
  re-serialized digest text, but a coordinate into module 1's already-durable trail — "read
  `why_trail` at `<checklist path>`, entries `<first-seq>..<last-seq>`; live digest is the
  `DIGEST:` line off `current`." The fresh agent's very first `current` call already surfaces
  the latest `now_understand` — this field is a pointer to *how to get there*, not the
  digest text itself, so a stale copy can never fork from the live trail.
- **Detach point — embeds `STATE_NOTE.md` by reference, not by re-derivation.** Rather than
  authoring a second five-line "step/slug/next-command/pid/expected-artifact" block, the
  Refresh module rewrites the **existing** `STATE_NOTE.md` (agents already do this before
  every detach) and `REFRESH_HANDOFF.md`'s "Workspace" section just points at it: "current
  detach point: `<STATE_NOTE.md path>` (rewritten as part of this handoff)." One artifact,
  not two competing sources of "where exactly did you stop."
- **Pre-empted Steps** does the same double duty it already does for launch orders citing
  prior-wave verdicts — it now also cites "this is a refresh, not a fresh dispatch; treat the
  original handoff + why-trail range above as already-established, do not re-derive them."

## The signal — reusing what each invoker already parses

### Commander → implementer/reviewer (the crew-registry edge — strongest reuse)

On a soft-accepted or hard-forced trip, before ending its turn the crew:

1. Rewrites `STATE_NOTE.md` (existing discipline, unchanged).
2. Writes `REFRESH_HANDOFF.md` (above).
3. Returns its **existing** result-report format (`IMPLEMENTER_RESULT`/`REVIEWER_RESULT`)
   with the verdict line replaced by one documented sentinel the Commander's report-parsing
   already has a slot for: `REFRESH_REQUESTED: <path to REFRESH_HANDOFF.md>` — a marker
   riding inside a channel the Commander already reads, not a new channel.
4. Does **not** write the expected result artifact.

Step 4 is the sharp reuse move: `classify_entry()` needs no new code and no new state label
to handle this. An external-backend entry with `status: running`, `pid: None` (always dead by
construction), and no result artifact is **already** exactly `STATE_RESUMABLE` under today's
rules — a voluntary refresh *is*, from the classifier's point of view, indistinguishable from
a resumable crash. Commander's pre-dispatch recovery check (already run before every crew
dispatch, per doctrine) discovers this the very next time it looks, on the existing code
path, zero new branches.

The existing fork inside `ExternalBackend.resume()` then does the rest of the work: it
refuses to resume in place and names exactly two options — `SendMessage` (continue, full
context — wrong here) or `--abandon --relaunch` (fresh attempt, fresh Agent-tool dispatch —
right here). The Commander's decision rule is one line: **a report is present and carries
`REFRESH_REQUESTED:` ⇒ always `--abandon --relaunch`, never `SendMessage`.** This is safe
by construction against the "SendMessage a near-full crew back into its own fill" failure,
because a crew that hasn't returned yet has not produced the marker — the doctrine's own
alive/dead split (a *report present* is required before this rule even applies) already keeps
a genuinely stalled-but-alive crew off this path.

`--abandon --relaunch` bumps `attempt` (existing `next_attempt` logic — no new counter), and
the Commander dispatches attempt N+1 via the **same Agent-tool call shape** it already knows,
now pointed at `REFRESH_HANDOFF.md` as the crew's handoff instead of the original
`IMPLEMENTER_HANDOFF.md`/`REVIEWER_HANDOFF.md` — the `handoff` field's existing contract
("the wrapper has already refused a missing one") applies unchanged to the new path. A
genuinely fresh Agent-tool invocation, empty transcript, cold-reading a file, is exactly the
re-instantiation module 4 requires — reached with zero new registry fields and zero new
verbs.

### Admiral → Commander (LAUNCH_ORDER / STATE_NOTE / ADMIRAL_LOG edge — doctrine, not a classifier)

The near-full Commander performs the same two doctrinal moves it already performs before
every detach — `STATE_NOTE.md` rewrite (mandatory, engine-enforced at first write via
`verify_state_note.py`'s `execute` precondition) plus `REFRESH_HANDOFF.md` — then ends its
turn carrying the same `REFRESH_REQUESTED:` marker inside its **existing** return-report
shape. This rides an inspection habit the Admiral already has: "verify an idle Commander from
artifacts; never block on a dropped verdict" (fleet-doctrine.md) already means the Admiral
opens the worktree/report on any Commander that goes idle without a clean verdict — the
marker is one more thing that inspection already finds, not a new inspection to add.

Because there is no JSON classifier at this edge, "confirm dead before touching the
worktree" (TaskStop or verify no live PID) is the Admiral's stand-in for the registry's `pid`
check — same invariant, doctrine-enforced instead of code-enforced, because that is the
machinery this edge actually has. Re-instantiation reuses "worktrees + workbench artifacts
survive the process": the Admiral dispatches a fresh Commander into the **same worktree** via
a fresh Agent-tool call, `LAUNCH_ORDER`'s `Pre-empted Steps` field pointing at
`REFRESH_HANDOFF.md` the same way it already points at prior-wave verdicts.

### Commander → human (top of the chain)

No registry, no doctrine drill — a person. Same `REFRESH_HANDOFF.md` artifact, same
`REFRESH_REQUESTED:` marker, delivered through whichever channel the Commander already
reports through. The human "re-instantiates" by starting a fresh session pointed at the file
— reusing the exact reading habit `LAUNCH_ORDER` already trained on the fleet ("paste, don't
point... forced to guess" — now the audience widens from "a fresh agent" to "a person," same
discipline).

## Symmetric recovery — one artifact, two authors

A crash never gets a `REFRESH_HANDOFF.md` authored by the dying agent. What makes recovery
symmetric here is that the invoker's **crash-path** reconstructs the identical shape from the
identical durable sources a voluntary refresh would have pointed at: `STATE_NOTE.md` (detach
point), `spine.json`/`execute.json` via `current` (mission/plan/criteria), and `why_trail`
(the digest). A voluntary refresh differs only in **who writes the pointer file** — the dying
agent writes it deliberately; on a crash, the invoker derives the same pointers by hand from
the same three sources during its normal recovery drill. One template describes both; the
"symmetric" claim is literal, not just similar-in-spirit — same headers, same reference
targets, same reuse of `STATE_NOTE`.

## Invariants

1. `REFRESH_HANDOFF.md` never re-serializes mission/plan/criteria/map-anchor content that
   already has a durable home — every such field is a pointer.
2. `STATE_NOTE.md` is rewritten as part of every refresh, never duplicated by a second
   detach-point block.
3. A crew's `REFRESH_REQUESTED:` marker is only ever read from a **returned** report — a
   crew that has not returned is never treated as refresh-ready, keeping the
   SendMessage/`--abandon` fork safe by construction.
4. `--abandon --relaunch` (crew tier) always bumps `attempt`; a voluntary refresh consumes an
   attempt slot exactly like a crash-and-retry does — no separate counter.
5. Reach-up terminates at the human; the human's version of this module has no re-instantiation
   machinery beyond "start a fresh session and open the file."

## Error modes

| situation | outcome |
|---|---|
| crew ends turn with `REFRESH_REQUESTED:` marker, no result artifact | classifies `STATE_RESUMABLE` exactly as a crash would; Commander runs `--abandon --relaunch`, never `SendMessage` |
| crew stalls (no report at all) | doctrine's existing alive/dead split applies unchanged; refresh logic never engages until a report exists |
| `REFRESH_HANDOFF.md` written but `STATE_NOTE.md` not rewritten | Commander/Admiral treat this as a doctrine violation identical to any other stale-state-note failure — not a new failure class |
| Commander marks `REFRESH_REQUESTED:` but Admiral's idle-inspection habit misses it | Admiral may `SendMessage` a refresh-seeking Commander back into full context — a real gap, named below, not mechanically prevented at this edge |
| relaunch dispatched with `REFRESH_HANDOFF.md` missing the why-pointer's cited seq range (e.g. trail rotated/pruned) | fresh agent's `current` call still surfaces the live `DIGEST:` line; only historical entries outside the cited range are unreachable — degrades to "less history," never to "no digest" |

## Config

None added. The only "config" this module introduces is a documented sentinel string
(`REFRESH_REQUESTED:`) inside an existing report format and a fixed file-path convention
(`REFRESH_HANDOFF.md` beside the existing handoff/state-note files) — no new schema field on
`crew-runs.json`, no new CLI flag on `run_crew.py`/`recover_crews.py`.

## Self-assessment

**DEPTH.** Deep at the Commander↔crew edge specifically: the entire signal-and-recovery
protocol collapses into "don't write the result artifact, and say `REFRESH_REQUESTED:` in
the report you were already going to write" — everything else (classification, the
resume-vs-relaunch fork, attempt bumping, fresh dispatch) is inherited from machinery that
already exists and needed zero new code. Shallower at the Admiral and human edges, where the
"interface" is closer to a documented convention layered on doctrine than a genuine
abstraction boundary — reuse ran out of registry to lean on past the crew tier, and doctrine
discipline is a thinner hiding mechanism than a refusing verb.

**LOCALITY.** The crew-tier reuse is highly local: no change to `run_crew.py`,
`recover_crews.py`, or `crew-runs.json`'s schema at all — the entire mechanism rides existing
fields and existing verbs, with the new content confined to two small template files
(`REFRESH_HANDOFF.md`'s pointer fields, one sentinel in the return-report convention). The
Admiral and human edges add no new files to the *engine* at all, only doctrine text —
maximally local by construction, but that locality is bought by *not* building a mechanism,
which is itself the cost named below.

**SEAM PLACEMENT.** The seam is placed exactly on the fork that already exists inside
`ExternalBackend.resume()` (SendMessage vs `--abandon --relaunch`) and on the classifier's
existing `STATE_RESUMABLE` label — both already-chosen chokepoints, not new ones. This is the
constraint's strongest justification: the seam a governor needs (distinguish "keep this
context" from "start fresh") was already sitting, unused for this purpose, inside code
written for crash recovery. The weak seam placement is at the Admiral edge, where there is no
chokepoint to place anything on — the "seam" is a paragraph of doctrine an Admiral must
remember to read, not a call that can refuse.

**TESTABILITY.** The crew-tier path is testable with the exact fixtures `run_crew.py`/
`recover_crews.py` already use: monkeypatch `result_present`/`alive` to prove a
`REFRESH_REQUESTED:`-marked, resultless external entry classifies `STATE_RESUMABLE`; assert
`ExternalBackend.resume()` still refuses in-place resume (unchanged); assert `--abandon
--relaunch` bumps attempt and the new entry's `handoff` field equals the `REFRESH_HANDOFF.md`
path. Falsifiable and cheap, no new test infrastructure. The Admiral and human edges are
**not** unit-testable the same way — there is no pure function to assert against; verifying
them means a scripted drill (a real or simulated near-full Commander, a real Admiral doctrine
read) or nothing, which is a genuine testability gap the crew-tier reuse does not share.

## What this constraint costs

- **No distinct "voluntary" state anywhere.** `classify_entry()` has exactly one label —
  `resumable` — for both a genuine crash and a deliberate refresh. Anything that later reads
  `crew-runs.json` (a dashboard, a lessons audit, attempt-count triage) sees three "crashes"
  where there might be three healthy refreshes, unless it goes and opens each
  `REFRESH_HANDOFF.md`. A from-scratch protocol would likely add one field
  (`refresh_reason`/`voluntary: true`) to make this legible without opening a second file; this
  design declines that field because the constraint said reuse, not extend the schema.
- **Attempt-counter conflation.** `--abandon --relaunch` bumps the same `attempt` counter a
  real failure bumps — a gate that voluntarily refreshes three times at high fill reads,
  purely from attempt count, exactly like three crash-and-retry cycles. Real information (how
  many times did this actually fail vs. how many times did it just get long) is lost to the
  counter's single dimension.
- **The Admiral edge inherits a real, un-closed enforcement gap.** "Agent-tool dispatch has no
  engine chokepoint to refuse at" is already true doctrine, not something this design
  introduces — but reusing it for Refresh means a missed `REFRESH_REQUESTED:` marker really
  can get a refresh-seeking Commander `SendMessage`'d straight back into the exact full
  context it was trying to escape, with nothing structural to stop it. A from-scratch protocol
  at this edge could have chosen a stronger primitive (e.g., the Commander literally cannot
  end its turn without an artifact the Admiral's *next tool call* is mechanically forced to
  read); reuse forgoes that because no such chokepoint exists here today.
- **`STATE_NOTE` reuse inherits `STATE_NOTE`'s own named weakness.** The template's own text
  says currency across detaches is "your discipline... the engine only guarantees the first
  one exists." Building Refresh's detach-pointer on top of `STATE_NOTE` means a stale note is
  now also a stale refresh handoff — this design does not fix that pre-existing gap, it rides
  on top of it.
- **`REFRESH_HANDOFF.md` is verbose relative to its true information content.** Reusing
  `LAUNCH_ORDER`'s full twelve-header skeleton means most fields on most refreshes are one line
  reading "unchanged — see `<original handoff>`" — a minimal-interface sibling design would
  likely ship a payload a fraction of this size (a handful of pointers, no header ceremony).
  The cost of familiarity (a fresh agent at any tier already knows how to read this shape) is
  paid in template bulk that mostly says "nothing new here."
