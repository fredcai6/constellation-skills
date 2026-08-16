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
