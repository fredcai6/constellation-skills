# Lane A working notes — `cleanup/a-door` (#604, #603, #605)

Sole writer: commander `constellation/cleanup-a-door/execute/commander/attempt-1`.
Base `a69bbac4`. Written per `constellation-how-to-talk`.

## Problem statement (understand step)

Reconciled against `LAUNCH_ORDER.md` (frozen principal) and the three filed issues, read
from GitHub 2026-08-16. The order's mechanism claims match the code exactly; nothing in
Mission was already shipped. Three defects, confirmed at file:line:

**#604 — telemetry is fatal.** `_log()` (`scripts/mcp_spine_server.py:180`) opens `CALLLOG`
with no guard, and `run_engine` calls it at `:461` *outside* its own `try/except`. `main()`
catches only `KeyError` around `call_tool` (`:1359`), so a `FileNotFoundError` from `_log`
unwinds the whole process. `START_MARKER.write_text` (`:184`) has the same exposure. The
fix shape already exists in this module: `_log_rejection` (`:472`) wraps its write, reports
to stderr, and never raises.

**#603 — the binding is fixed before the spine exists, and fails open when unset.**
`SPINE = Path(os.environ["SPINE_FILE"]).resolve()` at `:146` is import-time. Worse for
fail-closed: it is `os.environ[...]`, so an *unset* var raises `KeyError` at import and the
server dies at startup — the client sees `Connection closed`, not a refusal. `.mcp.json`
currently prevents that by supplying the demo default, which is the fail-*open* half.

**#605 — the shipped demo spine is unusable.** Six absolute paths into
`constellation-skills-wt/f-424`, a worktree deleted during the epic-418-followon closeout
(`examples/mcp-interactive-demo/spine.json`, lines 20/28/78/86/109/117).

## What bind-on-open actually costs (settles `decision:bind-on-open-over-new-verb`)

The pre-ruling asked me to attempt the `spine_open` binding first and report the cost. The
cost is **not** in the identity guard — it is in four import-time derivations of `SPINE`
that a rebind would leave pointing at the old spine:

- `CALLLOG` (`:162`), `START_MARKER` (`:167`), `REJECTIONLOG` (`:177`)
- `_resolve_confined`'s `bound_dir: Path = SPINE.parent` **default argument** (`:188`),
  evaluated once at import — the subtlest of the four.

So bind-on-open requires making these late-bound. `_identity_violation`'s semantics are
untouched: it still compares argv against *the* bound spine and still refuses any argv
naming another. Only *which* spine is bound changes — exactly what
`decision:one-spine-per-process-stands` sanctions ("changes *when* the binding is decided,
never *how many* are live at once").

Two AST pins constrain where the rebind may sit:

- `tests/test_mcp_lifecycle.py:137` pins every `return` in `call_lifecycle_tool` to
  literally `_spine_open(args)` / `_spine_close(args)`. Its positive control (`:162`) is
  literally `out = _spine_open(args)` — so a mutate-then-return in `call_lifecycle_tool`
  is the banned shape.
- `tests/test_mcp_lifecycle.py:194` bans the identifiers `SPINE`, `SESSION`, `run_engine`
  from `_spine_open`'s own source.

The rebind therefore goes in a module-level helper that `_spine_open` calls.

> **Superseded — corrected by the cold critic (finding 7), and recorded rather than
> silently rewritten.** I first wrote here that the helper passes `:194` "on its letter"
> and that the pin must therefore be **extended to state the new truth**. That was wrong,
> and in the dangerous direction. `:194` bans those identifiers from `_spine_open`'s **own
> source**; a module-level binder it *calls* leaves the pin's letter *and its stated
> purpose* intact — nothing is weakened, so there is nothing to extend. Worse, "extend the
> pin" reads naturally as *replace a hard identifier ban with a softer intent-shaped
> statement*, which would have weakened a guard in the very motion I used to argue against
> weakening guards.
>
> **What shipped instead:** `:194` and its positive control are **byte-identical** to
> `a69bbac4` (verified: zero removed lines in that file across the whole branch), and a
> **new, strictly stronger** module-wide AST pin was *added* beside it, asserting that the
> set of assignments to `SPINE` and `SESSION` is exactly {module scope, the one named
> binder}, with its own mutated positive control. That catches the real regression — a
> second, quieter rebind site — which an `_spine_open`-scoped ban cannot see.

The measured cost above (the four import-time derivations) stands, and an independent AST
pass confirmed there is no fifth. Two further identity roots the four-item list excluded
were found by the critic and folded into the gate: `_primary_checkout_for_lifecycle`
(`:593`) did its own hard `os.environ["SPINE_FILE"]` read on `spine_open`'s own path, and
`open_work` returns **three** binding values — so binding `SPINE` without `SESSION` leaves
`claim` refusing and the exit criterion unreached.

## Floated to the Admiral — the "door-detection change" is undefined

**Status: blocking gate 4 only. Gates 1–3 proceed.**

File Ownership grants me `scripts/install_constellation.py` and
`skills/commander/templates/COMMANDER_SPINE.template.json` "**for the door-detection change
only**, which lands last." The order never says what that change is. Measured, not assumed:

- Mission names exactly three defects (#604, #603, #605). None of them touches either file.
- #603, #604 and #605, read from GitHub today, never mention either file.
- `grep -rn "door.detect|detect.*door|door_detect|DOOR_DETECT" scripts/ skills/ docs/`
  returns **one** hit, and it is a false positive: the word "detects" inside the spine
  template's `init` imperative, about `--skill-dir` auto-detection. **There is no
  door-detection concept in this repo to change.**
- The installer does not seed the demo default either — `rewrite_mcp_config_interpreter`
  (`scripts/install_constellation.py:571`) rewrites `mcpServers[*].command` only, never
  `env`. So "drop the demo default from `.mcp.json`" is not undone by an install run, and
  gate 4 is not needed to make gates 1–3 hold.

I will not invent it. The plausible reading — teach the commander spine template to detect
an unbound door and fall back — collides directly with a must-float item: "any change that
makes an agent-facing skill teach the CLI as a default." Guessing here is exactly the
guess-past-the-edge-of-latitude the doctrine forbids.

**Query:** what is the door-detection change, and is it in scope for this lane? If it is
the fallback-teaching reading, that is a decision outside my latitude and I need it ruled.

## Corrections to the launch order (both measured, neither blocking)

1. **"Charter-lite carrier: this repo has no `docs/agents/` overlay" is false.**
   `docs/agents/ORCHESTRATOR_CONTEXT.md`, `GLOSSARY.md` and `CREW_CONTEXT.md` are all
   tracked and present. I read them at `context` rather than substituting README.
2. **Map orientation is DEGRADED repo-wide**, not just for this lane's area.
   `map/ids.jsonl` is tracked but **empty (0 bytes)** at `a69bbac4`, while `map/INDEX.md`
   carries 27KB of generated structure, so `map_orient.py` can resolve no anchor id for
   *any* area. Discharged with four hash-pinned substitutes plus an escalation; receipt at
   `.agent-work/cleanup-a-door/map-orientation.json`. `map/` is not mine this wave — filed
   as a triage candidate, not fixed. This also means the `plan` step's `verify-frame`
   anchor gate cannot be satisfied by any frame and will be taken as a recorded waiver.

---

## Triage candidates (all `recommend-and-defer` — none implemented)

The launch order asks for these "filed as recommendations in your notes, not implemented."
None was fixed. Grouped by who should act.

### For the Admiral — cross-lane and order-level

1. **Three FENCED files carry claims this change falsified.** All three still assert that
   `mcp_spine_server` raises `KeyError` without `SPINE_FILE`/`SPINE_ENGINE`, or reads
   `SPINE_FILE` at module scope. Both are false since #603:
   - `scripts/run_crew.py:468-471`
   - `scripts/hooks/spine_rail.py:1081`
   - `tests/test_spine_rail.py:2698`

   Lanes B and C own these. Reported, not touched. **This is a merge-order hazard**: whoever
   merges last should sweep them, or they become the next run's stale-claim findings.
2. **The "door-detection change" is undefined** (see the float above). Blocks nothing that
   shipped; the two files remain untouched.
3. **`skills/workbench/references/checklist-engine.md` is outside the order's enumerated
   file-ownership list** (though not fenced). I corrected its now-false description of the
   door's binding under `reconcile`'s explicit mandate. Flagging the ownership gap, not the
   correction.
4. **`map/ids.jsonl` is tracked but empty (0 bytes)** at `a69bbac4`, so `map_orient.py`
   resolves no anchor for any area and **every** commander in this repo gets
   `DEGRADED-UNPARSEABLE` orientation and an unsatisfiable `verify-frame` gate. Repo-wide,
   not lane-specific. `map/` was not mine this wave.

### Design — the durable one

5. **Shotgun surgery on the door's binding rule.** The same fact is restated in roughly
   seven places (module docstring, binder docstring, two pin messages, two test docstrings,
   an agent-facing reference, a design doc). Three of this run's four review blockers were
   instances of one of those restatements going stale, and the *final* review found that the
   correction to one of them introduced the next imprecision — the smell producing its own
   next instance in real time. **A better regex is not the fix; one source of truth is.**

### Code quality — `scripts/mcp_spine_server.py`

6. `_log`'s two writes omit `newline="\n"`, which `docs/agents/CREW_CONTEXT.md` requires on
   every write; `_log_rejection` passes it. On Windows the call log and start marker get
   CRLF while the rejection log gets LF. **Pre-existing**, not introduced here.
7. `_report_dropped_telemetry` duplicates `_log_rejection`'s five-line stderr block apart
   from one label. One `_report_lost_record(kind, target, exc, lost)` would carry both and
   keep the two diagnostics guaranteed to match.
8. A `_log` docstring cites `run_engine`'s call site as `:461` without pinning a revision;
   it is `:496` at HEAD. The inherited "pin a claim to the revision you read it at" rule
   applies to history notes in docstrings too.
9. `_rebind_refusal` depends on `checklist_engine._active_lease`, a **private** cross-module
   function. Right trade today; promote to a public engine accessor at a third caller.
10. **`SPINE_ENGINE`'s named sibling fallback is inert.** Measured twice: a bogus or missing
    `SPINE_ENGINE` still starts the server cleanly, because `checklist_engine.py` sits beside
    the server and Python already puts that directory on `sys.path`. The real fix was
    removing the `KeyError`, which holds. **Either make `SPINE_ENGINE` do something or retire
    it.** (This replaces two candidates the g3 implementer raised that the reviewer refuted
    by measurement — they do not reproduce and are not forwarded.)
11. The binder pin's detector misses four alternative rebind forms. Hardening, not a defect.
12. `docs/CHECKLIST_ENGINE_DESIGN.md`'s new paragraph lists `SPINE_ENGINE` among what is
    bound "again" (only `SPINE` and `SESSION` are), and describes the second binding moment
    as reading *from* the environment when those values come from `open_work`'s return and
    are written *into* it. Recorded by the final review as an explicit `fail` carried past
    consolidation by `--override-reason` — never downgraded to a pass. Left as triage
    because I was at the rework cap and a post-review edit would be unreviewed code.

### Test coverage — `examples/mcp-interactive-demo/`

13. No test drives the demo's **default** workspace branch: both drive cases set
    `SPINE_DEMO_WORKSPACE`, so the committed default is only asserted for absoluteness. The
    g2 reviewer drove it by hand from `$HOME` and it works — a coverage gap, not a defect.
14. The expansion test uses `bash -c` where the engine resolves `sh`. Harmless today
    (verified identical under `dash`), but it would miss a future bashism. Cheapest fix:
    call `checklist_engine._find_posix_shell()` instead of hardcoding.
15. The portability guard's vacuity floor is spelled two ways — a named `MIN_SHIPPED_FILES = 3`
    with a comment, and a bare `2` for the same purpose with neither. The unnamed one is the
    easier to weaken by accident.
16. `make_demo_spine.py` accepts an optional `argv[1]` target directory that nothing
    exercises — no test, no README instruction, no other caller.

---
---

# SECOND LANE A, DIFFERENT EPIC — `cmdr-567-a` (#559, bind-own-spine, #613)

> **Two lanes share this filename.** Everything ABOVE this line belongs to
> lane `cleanup/a-door` (#604/#603/#605), committed at `33dc3086`, and is NOT
> mine. My launch order assigned me `notes-a.md` as a fresh working-notes file;
> it is in fact a tracked artifact of that earlier lane. My first write
> CLOBBERED it and I restored it from `git show HEAD:notes-a.md`. Preserved
> verbatim, zero lines removed. See `L1` below.

Sole writer below this line: commander `cmdr-567-a`. Base `600de020`.

## L1 — my assigned notes file was another lane's committed artifact

My launch order says: "Your working-notes file: `notes-a.md`, in your worktree
root. **You are its sole writer.**" I took that at face value and wrote to it.
`notes-a.md` is **tracked**, 197 lines, last written by lane `cleanup/a-door` at
commit `33dc3086`. My write destroyed all of it in the working tree.

Recovered with `git show HEAD:notes-a.md`; the file now holds the prior 197 lines
verbatim followed by my own record. Verified `git diff --numstat notes-a.md` =
`178 0` — **178 added, zero removed**. Nothing of the earlier lane was lost.

The order's fault is small and mechanical: it reuses a per-lane filename across
epics without checking whether the name is already taken in the tree. `notes-1.md`
and `notes-b.md` are also tracked at `600de020`, so lane B this wave has the same
trap set for it and does not know. Worth one line in the next order template:
**a launch order that assigns a working-notes filename should assign one that
`git ls-files` says does not exist.**

Two things follow that matter beyond the filename:

- This is the *third* clobber-and-restore in this epic's recent history. `HEAD~4`
  is literally `chore(609): restore lane F's clobbered crew registry from git
  history`. The repeated shape is an agent writing a path it was told it owned,
  over content it never read.
- It is the **same defect class as my mission**. Lane F's registry, lane G's
  spine, and this file were each clobbered because a writer could not tell that
  someone else's content was already there. The spine case has a lease and still
  lost; this case had an explicit "sole writer" grant in a frozen order and still
  lost. **Authority to write is not knowledge of what is there.** My lane can fix
  the torn-write half for spines; it cannot fix this, and the general lesson is a
  triage candidate, not a fix.

## L2 — context step: what I read, and one honest ordering violation

Read for `context`: `references/global-orchestrator.md`,
`references/global-everyone.md`, `references/design-it-twice-brief.md`,
`references/commander-core.md` (installed commander skill), and project deltas
`docs/agents/ORCHESTRATOR_CONTEXT.md`, `docs/agents/GLOSSARY.md`.

`ORCHESTRATOR_CONTEXT.md` carries a section aimed straight at this lane —
"Dogfooding: The Engine Under Edit Is Not The Engine In Play" — which independently
states my order's `decision:in-session-observation-is-not-evidence` and adds:
"Concurrent lanes editing hook code can break every live session." I touch no
`scripts/hooks/*` (confirmed in my touched-paths accounting), so I do not add that
hazard.

**Ordering violation, stated rather than hidden.** The `context` imperative says
"before you open any source file, resolve and read the map input." I had already
read `scripts/mcp_spine_server.py` and `scripts/checklist_engine.py` during `init`
— findings F2 and F3 above — because I went after the door refusal the moment I
hit it at step one. So my F2/F3 frame was built from code first and reconciled to
doctrine after, which is the exact inversion the imperative exists to prevent. In
mitigation, and it is only partial: the map is DEGRADED repo-wide (empty
`map/ids.jsonl`), so there was no frame available to precede the source read. The
frame I actually used is the previous lane's prose in this same file, which is
recorded as a hash-pinned substitute in the map receipt.

Map orientation: `DEGRADED-UNPARSEABLE`, discharged with 5 hash-pinned
substitutes, 3 `unmapped` statements and 1 escalation. Receipt at
`.agent-work/epic-567-door/cmdr-a/map-orientation.json`. Cause is repo-wide, not
mine: `map/ids.jsonl` is tracked and 0 bytes, `map/INDEX.md` has 29KB of structure
but no citable anchor id. The previous lane A reported this identically at
`a69bbac4` and it is still unfixed at `600de020` — so it has now survived at least
one full epic as a known, filed, unactioned defect.

## L3 — `verify-frame` and the mission-frame template contradict each other

The previous lane A wrote that under DEGRADED "the `verify-frame` anchor gate
cannot be satisfied by any frame." I read `frame_verdict` in
`map_orient.py` and can state it more precisely, which matters because the
imprecise version makes the gate look merely broken when it is actually
*mis-aimed*.

Under a DEGRADED receipt, `frame_verdict` does two things:

1. For **every** token matching `ANCHOR_RE` — that is
   `struct|capability|event|constraint|assumption|claim|decision` followed by
   `:<id>` — it appends a problem, unconditionally. There is no path on which an
   anchor id is accepted when the mode is not `RESOLVED`.
2. Separately it requires `backing` to be non-empty: the frame must cite at least
   one path the receipt hash-pinned as a substitute.

So the gate IS satisfiable under DEGRADED — but only by a frame that contains
**zero anchor-id tokens** and cites the substitute paths. That is a *worse* frame
than mine, and the gate prefers it.

**The contradiction is with the template the same step orders me to use.**
`templates/MISSION_FRAME.template.md` says, in bold, "Grade every anchor with an
`@grade` child line", and its own worked examples are
`- decision:md-decision-is-a-list-item …`. Those are `decision:` tokens.
`ANCHOR_RE` matches them. **Following the template guarantees `FRAME-REFUSED`
whenever the map is degraded.** My frame cites 15 anchors and got exactly 15
problems, one per anchor, each with the identical message.

The step's own imperative also mis-describes the check. It says anchors "must be
one of the substitutes the receipt hash-pinned there, so the frame is compared
against a committed prior declaration." That describes path citations, which is
what `backing` checks — but the anchor loop refuses anchor ids regardless of any
substitute. An author reading the imperative would reasonably conclude that
anchors backed by a pinned substitute pass. They do not.

Measured: `verify-frame` exit **10**, `FRAME-REFUSED`, `problems: 15`. Note the
exit code is only visible unpiped — `... | tail` reports `tail`'s 0 and makes a
refusing gate look green, which is its own small trap.

**My disposition.** I keep the rigorous frame and take `c6` as a **recorded
waiver**, which the step's imperative explicitly sanctions ("c6 is waivable, so
take that escape as a RECORDED waiver rather than as a silent skip"). Stripping 15
real constraint/decision anchors to satisfy a string-matcher would trade a
document that carries the run's actual governing constraints for one that passes a
check. That is the "check that cannot fail" hazard in `global-orchestrator.md`
inverted — here the check *can* fail, but it fails the better artifact.

Triage candidate, not a fix: `map_orient.py` is not mine this wave, and this is a
design question (should a degraded frame be allowed anchor ids backed by pinned
substitutes?) rather than a mechanical defect I may settle alone.

## F5 — the atomic-write pattern already exists in this repo, three times

I do not have to design the `save()` fix. `global-everyone.md` says "one canonical
path; no speculative abstraction", and the canonical path is already here:

- `scripts/hooks/gauge_writer_hook.py:513` — `_atomic_write_json`: `mkdir(parents,
  exist_ok)` → write a `.tmp` sibling → `os.replace(tmp, path)`, with the comment
  "atomic on POSIX and Windows alike". This is the cleanest instance and the one to
  mirror.
- `scripts/hooks/spine_rail.py:369` — `_replace_binding_atomically`: unique-temp
  atomic replace under a lock, described at `:1359` as "closing the
  lost-update/torn-write window".
- `scripts/apply_episode_delta.py:1201` — "A single `os.replace()` is atomic on ..."

`spine_rail.py:163-170` even states my scope boundary in the repo's own words:
"load-modify-save is atomic on the WRITE but not across the read-modify-write."
That is exactly the distinction I am holding — and it means the boundary is already
repo doctrine, not a caveat I invented to limit my scope.

Both hook files are **out of my scope** (`scripts/hooks/*` is untouched, and
concurrent lanes editing hooks can break every live session). I read them for the
pattern only.

### Blast radius of the `save()` change, enumerated by command with a count

Per `global-everyone.md`'s authoring-side rule — "enumerate by command, never by
memory, every artifact that asserts something about what you changed, and state the
count." `grep -rn` for atomicity claims across `scripts/ tests/ docs/ skills/`
returns **13 files**. Of those, exactly **one** asserts something about
`checklist_engine.save` that my change falsifies:

- `tests/test_crew_launcher.py:3250`, inside `_wait_until`'s docstring:
  > "A transient exception (the predicate reads the SAME spine file the heartbeat
  > thread is mid-write to — `checklist_engine.save` writes plain bytes,
  > non-atomically) is treated as 'not yet', not a failure"

Two things about that, and both are worth reporting:

1. **The repo's own test suite already documents this bug and works around it.**
   That docstring is a written record of a torn read being observed in practice, in
   the parent-heartbeat test — which is #613's exact scenario. It is the strongest
   corroboration available that the defect is real and not theoretical, and it was
   sitting in the tests the whole time.
2. **It is a stale claim the moment I land the fix.** The `except (OSError,
   ValueError)` tolerance becomes unnecessary, though harmless. I will correct the
   docstring rather than leave a comment asserting a property the code no longer
   has — a stranger reading it would conclude `save()` is still non-atomic.

`save()` has **3 call sites** in `checklist_engine.py` (`:3580`, `:3595`, plus the
definition at `:237`) and **one** external caller, `scripts/run_crew.py:1433`,
paired with a `load` at `:1431` — that pair IS the parent-heartbeat second writer
from #613. It gets the atomicity benefit for free and keeps the lost-update
exposure, which is the boundary again.

## F6 — the extension points for a binding verb are already built and named

Continuing F2. Beyond `_bind_process_to` itself, the door already carries every
seam a new binding verb would need, each one deliberately factored and commented:

- **`BINDS_WITHOUT_A_BOUND_SPINE = {"spine_open"}`** (`:1425`) — the set of tools
  reachable with no usable spine bound. Its comment says: "Exactly one name, and it
  is a SET rather than an `!=` so the exemption is a listed fact a reader can find,
  not a comparison buried in a dispatch chain." A second binding verb is a
  one-element addition to a set that was *built* to be added to.
- **`LIFECYCLE_TOOLS`** (`:1368`) — a separate schema list from `TOOLS`, with
  `LIFECYCLE_TOOL_NAMES` derived from it (`:1412`) and merged at `:1414`. New
  lifecycle tools have a declared home.
- **`call_lifecycle_tool`** (`:1067`) — a name router that "does nothing but route
  to one of them by name", explicitly a module-level sibling of `call_tool` so
  `call_tool`'s choke-point AST pin stays strict.
- **`_HOW_TO_BIND` / `_HOW_TO_REBIND`** (`:383`, `:387`) — the two remedy strings,
  already extracted as named constants, which is exactly the edit a new verb needs.

**One constraint the candidates must respect, and it is sharp.** The AST pin at
`tests/test_mcp_lifecycle.py:137` restricts every `return` in `call_lifecycle_tool`
to literally `_spine_open(args)` / `_spine_close(args)`. A third route means
extending that pin's literal list. The previous lane's own record contains a
**superseded** passage where it first proposed to "extend a pin" and the cold critic
corrected it as "the dangerous direction", because extending a pin reads naturally
as replacing a hard identifier ban with a softer intent-shaped statement. So:
adding a third *literal* to an allow-list is not the same act as loosening a ban,
and if a candidate proposes it, the distinction has to be made explicitly, with the
pin left strictly as narrow as before. I will hold any winning candidate to that.

`call_lifecycle_tool`'s docstring also rules out one shape in advance: "Two tools,
never one `action` switch", because folding tools with opposite identity postures
into one body is "exactly the 'a guard written for one hazard covers the other by
accident' failure". A candidate that adds an `action: "adopt"` to `spine_open`
collides with a documented, reasoned decision — worth weighing against candidate B.

Read together with F2, the honest summary of my lane's code change is: **one new
route through machinery that was already built for it, plus one line added to a set
that documents itself as a list to add to.** That is a small change on a
well-prepared seam, and it is the strongest argument that the previous lane left
this deliberately one step from done.

## F7 — Candidate A's own falsification test, run, and it FAILS as designed

This is the most important measurement of the run.

Candidate A derives the session identity from the spine's stamped
`origin.work_id`, via a new single-definition `spine_lifecycle.session_id_for()`.
It refuses (its refusal `R7`) any spine that carries no `origin.work_id`. And it
names, in its own §7, the measurement that would prove it wrong:

> "If `origin.work_id` is commonly absent from the spines that need binding, R7
> refuses in the main case and the tool is theatre. ... count spines under
> `.agent-work/` and `.worktrees/*/.agent-work/` with and without a stamped
> `origin.work_id`."

I ran exactly that census. Live population — spine-shaped JSON under `.agent-work/`
and `.worktrees/*/.agent-work/`, excluding `archive/` and `templates/`:

| | count |
|---|---|
| live spine-shaped files | **52** |
| carrying `origin.work_id` | **4** |
| **not** carrying `origin.work_id` | **48** |

**8%.** Candidate A's session derivation refuses 92% of the live population. Two
of the refusals are fatal to the mission specifically:

- **`.agent-work/epic-567-door/spine.json` — the Admiral's own live spine — has
  `origin: None`.** The Admiral's `spine_status` refusal is the grounding the
  launch order gives for `decision:solve-the-general-case`. So Candidate A as
  written **cannot bind the one spine the pre-ruling was written about.**
- **`.agent-work/implementer-315-native-g1/IMPLEMENTER_PLAN.json` — `origin: None`.**
  That is the file type #559 is *literally about*: "the tools ... stay pointed at
  the Commander's `spine.json`, never the Implementer's own `IMPLEMENTER_PLAN.json`."
  A's R7 refuses it.

`execute.json` and `g1-review/review.json` are also `origin: None`. My own
`cmdr-a/spine.json` DOES carry `origin.work_id='epic-567-door/cmdr-a'`, because
`init_work_area.py --spine` stamps it — which is precisely why this defect would
have survived a self-test. **An implementer testing the feature on its own spine
would see it work, and it would fail on every spine the issue names.** That is a
check that cannot fail, and I only caught it because the candidate was honest
enough to name its own falsifier.

### The repair, measured, and it is complete

`origin.work_id` is the wrong field. The right one is the spine's **top-level
`work_id`**, which is a required field on every spine the engine drives:

| | count |
|---|---|
| live spine-shaped files | **52** |
| `origin.work_id` present | 4 |
| no origin, but top-level `work_id` present | **48** |
| **neither** | **0** |

**Deriving the session from `origin.work_id` when present, else the top-level
`work_id`, covers 52/52 — 100% of the live population**, including the Admiral's
spine and `IMPLEMENTER_PLAN.json`. Nothing else about Candidate A has to change:
`session_id_for(work_id)` keeps its single definition and `open_work` keeps
calling it, so a spine minted by `open_work` still yields a byte-identical
session; the fallback only adds coverage for spines minted another way
(`init_work_area.py`, `generate_spine.py`, a hand-compiled plan).

R7 does not disappear, it narrows: refuse only when **neither** field is present,
which the census says is currently never but is still the right fail-closed
posture for a hand-written JSON file that is not a spine at all.

This is what I will recommend as a **named hybrid**: Candidate A's design with the
session derived from `work_id` rather than `origin.work_id`. It is A's seam, A's
containment root, A's refusal set, and one corrected field — where the correction
is the difference between solving the mission and refusing it.



## Bootstrap
- ALIVE. Continuation commander, on bootstrap step 3/4 (work area + lease).
- `cd` does NOT persist between Bash calls in this harness. Every command from
  here on uses an absolute path or an in-command `cd <abs> && ...` subshell.
- `verify_worktree_isolation.py --here <abs>` exits 1 when run bare (it sees the
  main checkout at /home/tommy/projects/constellation-skills). Run as
  `cd <worktree> && py .../verify_worktree_isolation.py --here <worktree>` and it
  exits 0: "worktree OK". Isolation is CONFIRMED.
- Bootstrap floor COMPLETE. Work area + spine at
  `.agent-work/epic-567-door/cmdr-a/spine.json`, lease `cmdr-567-a` -> active.

### Bootstrap defect worth reporting to the Admiral
My launch order named the engine
`/home/tommy/.claude/skills/constellation-commander-delegated/scripts/checklist_engine.py`.
**That file does not exist.** The delegated skill ships only
`SKILL.md`, `interpreter.json`, `references/` — no `scripts/`, no `templates/`.
Its own SKILL.md says it depends on the installed `constellation-commander`
skill for both. The real engine in play is
`/home/tommy/.claude/skills/constellation-commander/scripts/checklist_engine.py`.
Any future launch order citing the delegated path will hard-fail at step 3.

## F1 — bind-own-spine gap REPRODUCED in my own process (primary evidence)

State at time of call: I am a Commander. My spine exists on disk at
`.agent-work/epic-567-door/cmdr-a/spine.json`. I hold its lease (`cmdr-567-a`,
active). My `init` step is `in-progress`. `env | grep SPINE_` returns nothing
(the only hit is `PWD`, because my worktree path contains the word "spine").

The engine's own `init` imperative instructs me:

> "by default, call the `spine_lease` MCP tool with action=claim ... **this is
> your own spine (the one this process's door is bound to)**, so the door needs
> no session id argument, it reads `SPINE_SESSION` from its own environment.
> CLI fallback: `<engine> claim --session-id ...`"

I called the door as instructed:

```
mcp__spine__spine_status  ->
REFUSED: no spine is bound to this door, so there is nothing for this tool to
act on. Call `spine_open` to mint a spine and bind this process to it, or
relaunch this door with SPINE_FILE set to an existing spine file.
```

This is the Admiral's failure, reproduced one tier down, on the first step of
the run. Three facts make it the anchor defect:

1. The engine's step text asserts the door **is** bound to my own spine. It is
   not, and cannot be — I was dispatched into an already-running door.
2. The only two remedies the refusal offers are both wrong for my case.
   `spine_open` **mints** a new worktree/branch/spine — it explicitly "acts on a
   spine that does not exist yet, never the spine THIS door is itself bound to."
   Mine already exists. "Relaunch this door with SPINE_FILE set" is not
   available to a subagent; the door's lifetime is the session's, and a
   dispatched agent cannot relaunch its dispatcher's MCP server.
3. So the CLI fallback in that same imperative is the ONLY path I have. That is
   precisely what epic #567 wants to delete. **You cannot delete a fallback that
   is the only path** — confirming the launch order's framing with a live
   measurement rather than an inference.

The gap is not "dispatched Task-tool crew can't reach their plan" (#559 as
written). It is more general and simpler: **there is no verb that binds a door
to an existing spine file.** `spine_open` mints; nothing attaches. Every role
that did not personally launch its own door is affected, top tier included.

## F2 — the whole mechanism already exists; only the VERB is missing

`scripts/mcp_spine_server.py` already carries every part needed. Nothing has to
be invented; one existing function needs a second caller.

| Piece | Line | What it already does |
|---|---|---|
| `_bind_process_to(spine_file, session)` | 878 | **THE** one place `SPINE`/`SESSION` are assigned outside module scope. Sets both globals AND `os.environ`. |
| `_rebind_refusal()` | 920 | Decides *whether* a rebind is allowed — refuses while this process holds an active lease. |
| `_resolve_confined(value, join_relative_to, bound_dir)` | ~330-380 | Containment predicate, ALREADY parameterized on `bound_dir` so a caller can confine to a root other than `SPINE.parent`. |
| `_unbound_refusal()` | 393 | Asks per call whether a usable spine is bound. Not cached — explicitly because "`spine_open` can rebind this process to a different spine mid-life". |
| `_identity_violation(argv)` | 443 | Compares `--file` to `SPINE` at CALL time, so it follows a rebind automatically. |

The decisive detail: **`spine_open` is mint-and-bind fused into one tool.** Its
only binding act is the single line 1041:

```python
_bind_process_to(opened["SPINE_FILE"], opened["SPINE_SESSION"])
```

recorded under `decision:bind-on-open-over-new-verb` — "a successful spine_open
binds THIS process to the spine it just minted, rather than the caller having to
relaunch the door to use work it just created." That decision solved exactly my
problem for the one case where the spine does not exist yet, and left the case
where it DOES exist with no path at all. `_bind_process_to` takes two plain
strings and does not care where they came from; `spine_lifecycle.open_work` is
the only reason a spine must be new.

So the design space is not "how do we build per-dispatch identity". It is
**"where do we put the second call to `_bind_process_to`"**, and that is a seam
question. `decision:one-spine-per-process-stands` is preserved either way: the
count of live spines per process stays one, only WHEN the binding is decided
moves — which is the precise thing `_bind_process_to`'s docstring already says
its existence changed.

Also relevant, from `_bind_process_to`'s docstring: `tests/test_mcp_lifecycle.py`
holds a **module-wide AST pin** asserting the set of assignments to `SPINE`/
`SESSION` is exactly {module scope, `_bind_process_to`}. Any candidate that
assigns those names anywhere else fails CI by construction. That pin is a
constraint on the design and a free correctness check on it.

## F3 — #613 atomicity: `save()` is a bare `write_bytes`

`scripts/checklist_engine.py:237`, the tail of `save()`:

```python
payload = (json.dumps(data, indent=2) + "\n").encode("utf-8")
eol = _dominant_newline(path)
if eol != b"\n":
    payload = payload.replace(b"\n", eol)
Path(path).write_bytes(payload)     # <-- not atomic
```

`load()` at 220 is a bare `read_text`. So a reader concurrent with a writer can
observe a **truncated or partial** spine — `write_bytes` opens with `O_TRUNC` and
a 35KB spine (mine is 35078 bytes) spans many pages, well past any single-write
atomicity. Consequences ordered by severity: a reader gets `JSONDecodeError` on
valid-on-disk state; worse, a crash between truncate and full write leaves the
spine **permanently corrupt**, and a spine is the only record that the work
happened.

**An honest boundary I will state plainly rather than overclaim.** Atomic
replace fixes *torn reads and corruption*. It does **not** fix **lost updates**:
two writers that each `load()` → mutate → `save()` still clobber each other, and
the loser's update vanishes silently with a perfectly well-formed file left
behind. That read-modify-write race is #613's OTHER half (the parent heartbeat as
a second concurrent writer). My order scopes me to "the atomicity half", and I
hold to that — but the distinction must be in the return, because "we fixed
save() atomicity" would otherwise be read as "concurrent writers are now safe",
which is false, and that misreading is more dangerous than the current bug.

## F4 — lane G's incident is #613's lost-update half, observed live

Handed to me at launch: lane G believed its worktree was compromised with
fabricated engine state. It was not — the writers were its own g1 implementer
crew plus its own design-it-twice FORK. A fork inherits the parent's full
context, so it believed it *was* the Commander and drove the Commander's own
`spine.json` under the identical lease id.

This is the sharpest available statement of the defect class, and it is not
solved by anything in my lane:

- The **lease** did not help. Both writers presented the same session id, so
  every mutating verb was correctly authorized. The lease answers "is a session
  driving this spine", never "is this the SAME agent as last time".
- **Atomic save will not help either.** Both writers were well-formed. The
  damage was a lost update plus unattributable journal entries.
- The root cause is that **nothing records who wrote what.** Lane G could not
  distinguish its own crew's writes from an attacker's, so a correct-looking
  spine was indistinguishable from a compromised one. It reached the worst
  available conclusion and lost its lane to the investigation.

Two consequences I will carry forward. (1) A **write-provenance** record — per
journal entry, which process/agent wrote it — is the actual fix for what bit
lane G, and it is beyond my lane's scope: triage candidate, not a fix. (2) It is
direct evidence for my own method: I must NOT use a context-inheriting fork for
design-it-twice. Fresh agents, explicitly forbidden from touching any spine.

