#!/usr/bin/env python3
"""MCP front door for the checklist engine (issue #424, workstream F of epic #418).

Zero dependencies: newline-delimited JSON-RPC 2.0 over stdio, which is what the
MCP stdio transport is. No SDK install, so nothing new leaks into the corpus.

This server WRAPS the engine -- it never reimplements it. Every tool builds an
argv and calls `checklist_engine.main(argv)`, capturing stdout, stderr and the
exit code. That means refusals, recovery hints, rails, the trip ledger, the
journal sidecar and lease enforcement all ride through completely unchanged,
because they are never re-derived here. A refusal (non-zero exit) is surfaced
as `isError: true` carrying the engine's own stdout+stderr verbatim -- the
model sees a failed tool call, not prose it has to parse to notice failure.

This door used to be strictly cwd-independent: it read its whole world from
the environment and never changed the process's working directory. That is no
longer true, in ONE narrow place, on purpose (issue #568). The engine's
worktree guard (`checklist_engine.origin_worktree_refusal`) compares a spine's
stamped `origin.worktree` against the engine's AMBIENT cwd, and this door calls
the engine IN PROCESS -- so for the duration of that one call, `run_engine`
stands in the bound spine's own worktree and restores the previous directory in
a `finally` (`_standing_in_the_bound_spines_worktree`). Without it, the very
first verb on a spine `spine_open` had just created in a NEW worktree was
refused by construction, because no process can already be standing inside a
directory that did not exist a moment earlier. Everything else here stays
cwd-independent, and the helpers that ask git a question still pass `cwd`
explicitly -- more strictly than before, since the process's own cwd is now a
thing that moves.

Ambient state is bound at launch, at `spine_open`, OR at `spine_bind` -- at
launch from the environment, and thereafter by `_bind_process_to`, the one place
`SPINE` and `SESSION` are assigned outside module scope: when a successful
`spine_open` binds this process to the spine it just minted
(`decision:bind-on-open-over-new-verb`, issue #603), and when `spine_bind` binds
it to a spine that already exists (issue #567). Only the MOMENT of decision
moves; the count never rises above one, and `_rebind_refusal` still blocks the
swap while this process holds an active lease -- `decision:one-spine-per-process-stands`.

The SESSION is never a tool argument in either case: `spine_open` takes it from
what it minted, and `spine_bind` derives it from the spine's own work id
(`spine_lifecycle.session_id_for`, the one definition, shared with `open_work`).
So a model still cannot NAME an identity. What it can now do, stated plainly
rather than left for the tests to certify, is name a SPINE -- see the second
declared path property below. The values:
  SPINE_FILE    -- the --file every engine call needs
  SPINE_ENGINE  -- path to checklist_engine.py (this repo's own copy; dogfooding
                   convention -- see checklist-engine.md "Dogfooding on the
                   skill-source repo")
  SPINE_SESSION -- the --session-id every mutating verb needs once a lease
                   exists; keyed session_id#agentId by the caller's own
                   environment (the committed .mcp.json's ${VAR} expansion
                   is what sets it on a real dispatch; the server just uses
                   whatever string it is handed)

TWO declared tool properties carry a filesystem path, and they are different in
kind. This sentence used to read "exactly ONE" and was stated in the singular
because that one exception cost a measured gate closure on a fabricated APPROVE;
the second one arrived with issue #567 and is named here rather than left to be
discovered.

* `spine_advance.from_child` does not redirect the door -- the call still
  addresses the bound spine -- but the child's `consolidation` is attached to
  that spine as a `review-result`, which is the evidence type an artifact
  postcondition consumes, so an unconfined path would let any JSON file carrying
  a `consolidation` key close a gate. `_identity_violation` therefore CONFINES it
  to the bound spine's own directory tree, the containment every real use in this
  repo already satisfies. See IDENTITY_TRADE.md §2.
* `spine_bind.spine_file` DOES decide which spine is bound -- that is its whole
  job -- which makes it the wider of the two and the reason `spine_bind` exists as
  its own tool rather than as an argument on one that promises creation. It is
  confined to `<this door's own checkout>/.agent-work/`, by
  `_own_checkout_for_binding` plus the SAME `_resolve_confined` predicate, and a
  candidate whose own `git rev-parse --show-toplevel` differs from this door's is
  refused even when its path is lexically inside. Both halves are asked of the
  RESOLVED path: while the second half asked about the argument's own parent, a
  symlink inside this work area pointing at a nested checkout satisfied both at
  once, and the door bound another repository's spine. The replacement isolation
  property, in one line: **one checkout's work-area tree per process.** The
  identity it confers is the spine's own, never the caller's. See
  IDENTITY_TRADE.md §7 for the measured reach delta this bought.

--------------------------------------------------------------------------- #
Tool surface: 9 tools covering all 18 of the engine's verbs
--------------------------------------------------------------------------- #

The engine exposes 18 verbs: current, claim, heartbeat, release, start,
advance, record, consolidate, skip, block, resume, reopen, append, amend,
attest, waive, attach, flag-candidate.

This used to be a 7-tool, 13-of-18 surface, on a "roughly seven" tool-count
budget (decision:mcp-is-the-vehicle), with `skip`, `amend`, `append`, `reopen`
and `flag-candidate` left CLI-only as "genuinely rarer" moves. That budget and
that escape clause are OVERTURNED (issue #559, N1): the human's ruling is
"anything that we want to do for the spine needs to be accessible via mcp. the
agents should not know about the cli. period. anything that we can only do via
the cli is a defect." Verb coverage is not a grouping decision weighed against
a tool count, and it is not conditional on a later gate proving a verb
load-bearing -- every verb the engine has gets a path through this door, full
stop. The grouping-into-tools STYLE survives (one tool per family of related
verbs, not one tool per verb); only the "stop at ~7 and leave 5 on the CLI"
policy is gone.

Grouping decision, and why: `spine_halt` already covered `block`/`resume` --
both change a gate's status without doing the gate's work -- so `skip` and
`reopen` join it rather than a fourth tool, for the same reason (`spine_halt`
is NOT renamed despite "halt" reading oddly once it also skips and reopens --
a rename would break any agent mid-run, and stability outranks the naming
tension). `append` and `flag-candidate` both add a new item to the plan (a
task, or an out-of-scope candidate) and fold into a new `spine_capture`.
`amend` is a different concern from either -- deliberate re-planning under a
named authority -- and gets its own `spine_amend`.

  1. spine_status        -- current                                  (read-only)
  2. spine_lease         -- claim | release | heartbeat
  3. spine_start         -- start
  4. spine_advance       -- advance
  5. spine_evidence      -- attest | attach | waive
  6. spine_halt          -- block | resume | skip | reopen
  7. spine_survey_result -- record | consolidate              (survey plans only)
  8. spine_capture       -- append | flag-candidate
  9. spine_amend         -- amend

18 of 18 verbs covered. There is no CLI-fallback table below this one: every
verb the engine has is reachable through this door.

`amend` is a PASS-THROUGH, deliberately. Its CLI shape is `--delta <file.json>
--reason ... --authority ...`, where the delta file holds `{"ops": [...]}` --
a grammar this door does not re-derive or validate (a second definition of
that grammar at the MCP boundary is exactly the second-rendering-path failure
this repo keeps fixing elsewhere). `spine_amend` instead accepts `delta` as a
JSON object in the tool arguments, writes it to a file BESIDE the bound spine
(`_write_amend_delta`, in the spine's own work directory, never a system temp
dir, so the artifact is per-task coherent and survives for audit), and hands
the engine the same `--delta <path>` the CLI already parses -- the engine
alone validates the ops. That written path is then run back through
`_identity_violation`'s containment check (`_resolve_confined`, the same
predicate `spine_advance.from_child` already used) before the engine ever
sees it.

--------------------------------------------------------------------------- #
The lifecycle door: 3 more tools, dispatched OUTSIDE call_tool
--------------------------------------------------------------------------- #

`spine_open` and `spine_close` (issue #559, C3/g3) wire `scripts/spine_lifecycle.py`'s
`open_work`/`close_work` onto this same, already-registered server -- no
`.mcp.json` change, because a tool is not a server. They are NOT engine
pass-throughs: neither ever calls `run_engine`, so they are dispatched from
`call_lifecycle_tool`, a MODULE-LEVEL SIBLING of `call_tool` with its own
containment pin (`tests/test_mcp_lifecycle.py`), routed from `main()`'s
`tools/call` branch rather than from inside `call_tool` -- `call_tool`'s own
choke-point pin resolves ITS `ast.FunctionDef` node by name and walks only
that subtree, so a sibling is structurally outside it, and its body is
untouched.

Their identity postures are opposite, matching `spine_open` acting on a spine
that does not exist yet and `spine_close` acting only on the one this door is
already bound to: `spine_open` never references `SPINE`, `SESSION` or
`run_engine` in its OWN source (checked, not merely claimed -- see
`tests/test_mcp_lifecycle.py`), taking the primary checkout it opens work from
`_primary_checkout_for_lifecycle` instead. That helper reads no environment at
all -- not `SPINE_FILE`, not anything: it anchors on the BOUND spine's own
directory when there is one, and on THIS SCRIPT's own when there is not. The
identifier ban is on `_spine_open`'s own source, which that helper is not, so
what the ban buys is that no ARGUMENT on the call can redirect the open onto
the bound spine -- never that the bound spine is invisible to the tool.
`spine_close` takes no arguments at all and acts on `SPINE` alone, because
there is no field to redirect.

`spine_bind` (issue #567, lane A) is the third, and it is a third posture rather
than a copy of either: it acts on a spine that already exists and is NOT the one
this door is bound to. So it reads `SPINE` -- for the idempotency short-circuit,
for its containment anchor, and for `_rebind_refusal` -- and the `_spine_open`
identifier ban does not reach it, which is deliberate and pinned: the ban is
resolved against `_spine_open`'s own `ast.FunctionDef` by name, and
`test_spine_close_is_not_held_to_the_same_ban` already pins that the scoping is
per-function rather than a module sweep.

The two roots do not agree, and must not. `spine_open` confines against
`_primary_checkout_for_lifecycle()` (`--git-common-dir`) because it must CREATE a
worktree, and worktrees nest under the primary checkout. `spine_bind` confines
against `_own_checkout_for_binding()` (`--show-toplevel`) because it must not
REACH one: the primary-checkout root admits every sibling worktree nested under
it, measured at 6102 candidate files against 1014. One flag, two questions, both
named -- do not "simplify" them into one helper.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

def _spine_from_env() -> Path | None:
    """The spine named by the environment, or None when NOTHING is named.

    Three readings of "nothing" collapse into one here, deliberately (issue
    #603):

    * **unset** -- this used to be `os.environ["SPINE_FILE"]`, a `KeyError` at
      module scope, *at import*. The server died before it could refuse
      anything and the client saw only `Connection closed`.
    * **empty** -- this is the case production actually takes. `.mcp.json`
      writes `${SPINE_FILE:-<default>}`, so dropping the default yields
      `${SPINE_FILE:-}`, which a shell expands to an empty string, not to an
      unset variable. `Path("").resolve()` is the process's **cwd**, so the old
      form silently bound the door to whatever directory it was standing in.
    * **whitespace** -- the same accident with a space in the config.

    None means "no spine is named", NOT "the named spine is fine": whether the
    named path is a readable spine file is `_unbound_refusal`'s question, asked
    per call rather than once at import, because a spine's directory can be
    removed while this process is running (issue #604)."""
    named = os.environ.get("SPINE_FILE", "").strip()
    return Path(named).resolve() if named else None


def _engine_from_env() -> Path:
    """The engine this door wraps: `SPINE_ENGINE` when set, else the copy that
    ships BESIDE this script.

    `SPINE_ENGINE` unset was a `KeyError` one line above `SPINE_FILE`'s, and a
    session that never bound a spine very likely never set an engine either --
    so without this, the door died at import and #603's refusal was
    unreachable, for the *other* variable, before the refusal path ever ran.

    The fallback is not a guess. `checklist_engine.py` and this file ship in the
    same directory and are installed together, so the script's own location
    answers the question with no new environment variable, no ambient cwd read,
    and no way to disagree with an explicit `SPINE_ENGINE` (which still wins
    whenever it is set)."""
    named = os.environ.get("SPINE_ENGINE", "").strip()
    if named:
        return Path(named).resolve()
    return Path(__file__).resolve().parent / "checklist_engine.py"


ENGINE = _engine_from_env()
SPINE: Path | None = _spine_from_env()
SESSION = os.environ.get("SPINE_SESSION", "")

sys.path.insert(0, str(ENGINE.parent))
import checklist_engine  # noqa: E402
import spine_lifecycle  # noqa: E402

PROTOCOL_DEFAULT = "2025-06-18"
SERVER_NAME = "spine"
SERVER_VERSION = "0.1.0"

def _telemetry_path(env_var: str, beside_the_spine: str) -> Path | None:
    """Where one telemetry side-channel writes, asked FRESH on every call.

    Three things had to be true at once here, and each of them rules out an
    obvious shorter version (issue #603):

    * **Late-bound, not import-time.** `spine_open` can rebind this process to a
      new spine mid-life (`_bind_process_to`), and a path captured at import
      would keep writing this run's telemetry beside the spine the door has
      stopped driving.
    * **The env override still wins.** A naive "recompute from `SPINE.parent`"
      late-binding silently discards `SPINE_CALLLOG` / `SPINE_START_MARKER` /
      `SPINE_REJECTION_LOG`, which `tests/test_mcp_lifecycle.py` and four other
      suites set to keep test telemetry out of the repo. Read the override
      first, exactly as the import-time form did.
    * **None when nothing is bound**, and None is a real answer, not a gap.
      With no spine there is no directory to sit beside, and inventing one
      (the cwd, a temp dir) is the very fail-open this gate exists to end. The
      callers SKIP the write instead -- and they must, because g1's telemetry
      guard catches `OSError` only, so an `AttributeError` on `None` would sail
      straight past it and take the server down.
    """
    override = os.environ.get(env_var, "").strip()
    if override:
        return Path(override)
    return None if SPINE is None else SPINE.parent / beside_the_spine


def _calllog() -> Path | None:
    """One JSONL line per engine call this server made, so a tracer/reviewer can
    count real engine dispatches without scraping a model transcript. Never read
    back by the server itself -- corroborating detail only, per MISSION_FRAME's
    claim table (a server-log numerator would structurally undercount the client
    rejections a schema-typed tool surface is supposed to prevent)."""
    return _telemetry_path("SPINE_CALLLOG", "mcp_calls.jsonl")


def _start_marker() -> Path | None:
    """A start-marker file: written on first successful engine call, so an
    external probe (the delivery-path measurement in MISSION_FRAME) can tell
    "config was valid and the server actually ran" from "config was merely
    accepted"."""
    return _telemetry_path("SPINE_START_MARKER", "mcp_server_started")

def _rejectionlog() -> Path | None:
    """One JSONL line per rejection the DOOR ITSELF issues -- an unknown tool
    name, an unknown multiplexed `action`, a missing required argument (issue
    #541), or a call made with no spine bound (issue #603). Every one of those
    returns `_tool_error(...)` BEFORE `run_engine()` is ever called (see the
    module docstring's "Zero dependencies" section and `call_tool()` below), so
    `_log()` and the call log never see it and the engine's own refusal counter
    never moves -- this file is that path's only durable trace. Beside the
    spine, like the call log, for the same reason: one location a run's own
    evidence-gathering has to remember, not two."""
    return _telemetry_path("SPINE_REJECTION_LOG", "mcp_rejections.jsonl")


def _report_dropped_telemetry(target: Path, exc: OSError, lost: str) -> None:
    """Report one telemetry write this door could not make -- never raises.

    Same shape and same principle as `_log_rejection` below: **fail loud, every
    occurrence** -- no batching, no once-per-run flag, no silent drop. `stderr`,
    never `stdout`, because `main()` writes the JSON-RPC protocol to `stdout` and
    a diagnostic there would corrupt the transport."""
    sys.stderr.write(
        f"TELEMETRY WRITE FAILED: could not write to {target} "
        f"({type(exc).__name__}: {exc}). Lost record: {lost}\n"
    )
    sys.stderr.flush()


def _log(rec: dict) -> None:
    """Append one call record, and write the start marker on first success.

    Both writes are guarded, and guarded SEPARATELY: these are two independent
    side-channels, so one destination being unwritable must not suppress the
    other. The catch is `OSError` -- covering `FileNotFoundError` (issue #604: the
    bound spine's directory is gone), `PermissionError` and `IsADirectoryError` --
    and deliberately not bare `Exception`, which would swallow programming errors
    in this module and hide them behind a telemetry message.

    **A diagnostic side-channel must never take down the thing it observes.**
    Before issue #604 neither write was guarded, `run_engine` called this OUTSIDE
    its own try/except (`:461`), and `main()` caught only `KeyError` -- so an
    unwritable call log killed the whole server and the client saw only a closed
    connection.

    A destination of `None` -- no spine bound and no env override, so there is no
    directory to write beside (issue #603) -- SKIPS that write. It is not routed
    through the `OSError` guard above, because it is not an I/O failure: nothing
    was attempted and nothing was lost that a report could name. And it could not
    be routed there anyway: the guard catches `OSError`, while `None.open()`
    raises `AttributeError`, which would sail past it and take the server down --
    the exact class of death this gate exists to end."""
    line = json.dumps(rec, ensure_ascii=False)
    calllog, start_marker = _calllog(), _start_marker()
    if calllog is not None:
        try:
            with calllog.open("a", encoding="utf-8") as fh:
                fh.write(line + "\n")
        except OSError as exc:
            _report_dropped_telemetry(calllog, exc, line)
    if start_marker is not None:
        try:
            if not start_marker.exists():
                start_marker.write_text(f"started for {SPINE}\n", encoding="utf-8")
        except OSError as exc:
            _report_dropped_telemetry(start_marker, exc, f"start marker for {SPINE}")


def _resolve_confined(
    value: str, *, join_relative_to: Path | None, bound_dir: Path | None = None,
) -> tuple[Path, bool]:
    """Resolve `value` and report whether it escapes `bound_dir`. Shared by
    both `--from-child` and `--delta` in `_identity_violation` -- one
    containment predicate, not two, for the two flags that carry the same
    underlying hazard: a filesystem path the engine will read and act on.

    `join_relative_to` is where the two flags genuinely differ, and it is a
    parameter rather than a second copy of this function for exactly that
    reason. `advance()` resolves a relative `from_child` against the parent
    checklist's own directory (a rule it implements itself); the caller passes
    `SPINE.parent` here to mirror that. `amend()` applies NO such rule to
    `--delta` -- it does a bare `Path(args.delta).read_text()`, so a relative
    value resolves against the process's own cwd, same as Python's own
    default; the caller passes `None` here, and this function then resolves
    `value` exactly as `Path(value).resolve()` would, matching the engine
    faithfully rather than asserting a base directory `amend()` never uses.

    One wrinkle since issue #568: `run_engine` stands in the bound spine's
    worktree while the engine runs, so "the process's own cwd" is not the same
    directory here as it is inside `main()`. This function is called from
    `_identity_violation`, which runs BEFORE that move and is deliberately
    left outside it -- resolving a containment check against a directory the
    door is about to enter would change what "confined" means mid-check. No
    live divergence follows: this door only ever hands the engine an ABSOLUTE
    `--delta` (`_write_amend_delta`) and joins a relative `from_child` to
    `SPINE.parent`, so no relative path reaches the engine to be resolved
    under either cwd.

    `bound_dir` defaults to `SPINE.parent` -- exactly what every call inside
    `_identity_violation` needs, unchanged -- but is a parameter so
    `spine_open`'s own containment check (`tests/test_mcp_lifecycle.py`) can
    confine a candidate WORKTREE path to `wt_root` instead: `SPINE.parent` is
    the CURRENTLY bound spine's directory, an unrelated boundary for a spine
    that does not exist yet, and `spine_open`'s own source may never reference
    `SPINE` at all (see `call_lifecycle_tool`'s docstring). Reusing this one
    predicate with a different `bound_dir` is the whole point: not a second,
    differently-shaped check.

    That default is spelled `None`-then-resolve rather than `bound_dir: Path =
    SPINE.parent`, because a default ARGUMENT is evaluated once, at import --
    the subtlest of the four import-time `SPINE` derivations this door used to
    carry (issue #603). After `spine_open` rebinds this process, an import-time
    default would still be confining paths to the directory of the spine the
    door has stopped driving, and nothing in the containment check itself would
    look wrong. `SPINE` is not None at the only site that omits `bound_dir`
    (`_identity_violation`, which `run_engine` reaches only after
    `_unbound_refusal` has already passed)."""
    if bound_dir is None:
        bound_dir = SPINE.parent
    p = Path(value)
    if not p.is_absolute() and join_relative_to is not None:
        p = join_relative_to / value
    try:
        escapes = not p.resolve().is_relative_to(bound_dir.resolve())
    except (OSError, ValueError, RuntimeError):
        escapes = True  # a path that cannot be resolved is not proof it is inside
    return p, escapes


_HOW_TO_BIND = (
    "Call `spine_bind` with the path to a spine that already exists, or `spine_open` to "
    "mint a spine and bind this process to it."
)
_HOW_TO_REBIND = (
    "Call `spine_bind` with the path to a spine that already exists, or `spine_open` to "
    "mint a spine and rebind this process to it."
)


def _unusable_spine_reason(spine: Path) -> str | None:
    """Why `spine` is not a readable spine FILE, or None when it is.

    Three of `_unbound_refusal`'s five inputs, extracted so they can be asked
    about ANY candidate path rather than only the bound one -- `spine_bind` needs
    exactly this question about the path it was handed. Extracted rather than
    copied: two ladders would drift in wording, and a caller who meets two
    different phrasings of one condition learns to distrust the words. The other
    two inputs (`SPINE_FILE` unset/empty/whitespace) are not here because they
    are questions about the ENVIRONMENT, which `_spine_from_env` already
    collapsed to `None`; there is no path to ask about.

    The read is a one-byte open, not `os.access`: `access` answers about the
    permission bits, while the caller's next act is to READ the file, and those
    two questions disagree under ACLs, read-only mounts and a file being replaced
    underneath. Ask the question the caller is about to ask."""
    try:
        if spine.is_dir():
            return "that path is a directory, not a spine file"
        if not spine.exists():
            return "no file exists at that path"
        with spine.open("rb") as fh:
            fh.read(1)
    except OSError as exc:
        return f"that file cannot be read ({type(exc).__name__})"
    return None


def _unbound_refusal() -> str | None:
    """Is a USABLE spine bound? Returns None when one is, else the refusal.

    Five inputs, one class (issue #603). `SPINE_FILE` unset, empty or
    whitespace-only means nothing was ever named (`_spine_from_env` already
    collapsed those three into `None`); a path that does not exist, is a
    directory, or cannot be read means something was named that no tool can act
    on. All five used to produce a different wrong answer -- a crash at import,
    a silent binding to the cwd, a raw `FileNotFoundError`, an
    `IsADirectoryError` -- and none of them told the caller what to do.

    **The wording splits, and the split is not cosmetic.** An unbound door has
    no path to name, so a single message that promises to name one is
    unsatisfiable there and invites a fabricated path. So: unbound says nothing
    is bound and how to bind; named-but-unusable NAMES the path and says how to
    rebind. Both name `spine_bind` AND `spine_open`, because since these gates
    those are the two ways out of either state without relaunching: `spine_open`
    for work that does not exist yet, `spine_bind` for work that already does
    (issue #567). Before `spine_bind` existed, both messages had to end
    "or relaunch this door with SPINE_FILE set to an existing spine file" --
    advice a model running INSIDE that door usually cannot follow. That clause is
    gone; the way out is now a call.

    **Asked per call, never cached.** The bound spine's directory can be removed
    while this process runs (issue #604), and `spine_open`/`spine_bind` can
    rebind this process to a different spine mid-life, so the answer is not a
    property of server-launch time.

    The last three of the five inputs live in `_unusable_spine_reason`, shared
    with `_spine_bind` rather than inlined here -- one ladder, so the `why` a
    caller meets is byte-identical whichever refusal produced it. See that
    function for why the read is a one-byte open."""
    spine = SPINE
    if spine is None:
        return (
            f"REFUSED: no spine is bound to this door, so there is nothing for this tool "
            f"to act on. {_HOW_TO_BIND}"
        )
    why = _unusable_spine_reason(spine)
    if why is None:
        return None
    return (
        f"REFUSED: this door was pointed at {str(spine)!r}, but {why} -- so no spine is "
        f"bound that this tool could act on. {_HOW_TO_REBIND}"
    )


def _identity_violation(argv: list[str]) -> str | None:
    """Does this argv, AS THE REAL PARSER RESOLVES IT, still address the bound
    spine under the bound session? Returns None when it does, else the refusal
    message.

    This is the runtime half of the property
    `tests/test_mcp_identity.py::IdentityBindingPinTests` pins, and it is why
    the module docstring's "a model cannot point the door at a different spine
    or identity" is a statement about what this process DOES rather than a
    statement about what CI would notice later.

    **It asks argparse, it does not read tokens.** Six predecessors of this
    check each modelled a SHAPE a redirect might take -- declared tool
    arguments, key names, argv contents, containment, argv position, and
    finally token spelling -- and each was defeated by a shape it had not
    enumerated. `--file X`, `--file=X` (one token) and `--fil X` / `--fi=X`
    (unambiguous prefix abbreviations, which argparse accepts by default) are
    all the same option to the parser and all different strings to a scanner,
    and `--file` is a plain `store`, so the LAST occurrence is the one the
    engine reads. Enumerating spellings is the defect; the only predicate that
    cannot be out-spelled is the parser's own answer.

    Three deliberate properties of how this is written:

    * `getattr(ns, "session_id", None)`, never `ns.session_id`. Read-only verbs
      (`current`) declare no `--session-id` at all, so attribute access would
      raise AttributeError on every status call.
    * A `SystemExit` from this parse is NOT a violation. `parse_args` exits 2 on
      malformed argv (e.g. `heartbeat` with no session once SPINE_SESSION is
      unset), and the caller's own `main()` is about to produce exactly that
      message; refusing here would replace the engine's error text with ours.
      The parse's own stderr is swallowed into a scratch buffer for the same
      reason -- otherwise the usage block would be emitted twice.
    * Scoped to `ns.file`, `ns.session_id` and `ns.from_child`, never "no
      repeated flags". `--field` is `action="append"` BY DESIGN and
      `spine_evidence attach` with two fields is legitimate; a repeated-flag
      rule would break it.

    **Why `--from-child` is checked at all, and why it is checked differently.**
    A SEVENTH review found that `spine_advance.from_child` is a DECLARED tool
    property carrying a filesystem path. `advance()` does `Path(from_child)`,
    honours an absolute path, reads that file and attaches its `consolidation`
    into the BOUND spine as a `review-result` -- with `ns.file` still resolving
    to the bound spine, so both halves of the check above stayed blind. That is
    not merely a data read: `review-result` is the evidence type an `artifact`
    postcondition consumes, so any JSON file anywhere carrying a `consolidation`
    key could close a gate. Measured live before this clause existed: a
    `from_child` outside the binding advanced g1 to `complete` on a fabricated
    APPROVE.

    So this one is a CONTAINMENT question, not an equality one -- `--from-child`
    legitimately names a DIFFERENT file (the child checklist), it just may not
    name one outside the bound spine's own directory tree. Measured before
    restricting it: every real use in this repo -- the engine's own tests, the
    schema doc's worked example, and every live/archived run record -- resolves
    inside the parent checklist's own directory (children are written under the
    work area the spine sits in). Resolution mirrors `advance()` exactly: a
    non-absolute path resolves against the parent checklist's directory, which
    IS `SPINE.parent` here because `ns.file` was already proven equal to it.

    `amend`'s `--delta` is the same shape of hazard (a filesystem path the
    engine reads and acts on) added by the N1 verb-closure change, so it is
    confined by the SAME `_resolve_confined` helper rather than a second check.
    """
    scratch = io.StringIO()
    try:
        with contextlib.redirect_stdout(scratch), contextlib.redirect_stderr(scratch):
            ns = checklist_engine.parse_args(list(argv))
    except SystemExit:
        return None  # malformed argv -- the real main() owns that message
    except Exception:  # noqa: BLE001 - a parser that cannot answer is not evidence of a redirect
        return None

    resolved_file = getattr(ns, "file", None)
    if resolved_file != str(SPINE):
        return (
            f"REFUSED: this door is bound to one spine for the life of its process, and "
            f"this call resolves --file to {resolved_file!r}, not the bound {str(SPINE)!r}. "
            f"Identity is not a per-call argument here (see IDENTITY_TRADE.md); if you need "
            f"to drive a different spine, launch a door bound to it, or use the CLI."
        )

    resolved_session = getattr(ns, "session_id", None)
    if resolved_session not in (SESSION, None):
        return (
            f"REFUSED: this call resolves --session-id to {resolved_session!r}, not the bound "
            f"session {SESSION!r}. The lease this door can take is the one its own process was "
            f"launched for; a claim under any other identity would record a lease nobody holds."
        )

    resolved_child = getattr(ns, "from_child", None)
    if resolved_child:
        resolved, escapes = _resolve_confined(resolved_child, join_relative_to=SPINE.parent)
        if escapes:
            return (
                f"REFUSED: --from-child names a child checklist INSIDE the bound spine's own "
                f"directory ({str(SPINE.parent)!r}); this call resolves it to {str(resolved)!r}, "
                f"which is outside. The child's `consolidation` is attached to the bound spine "
                f"as a review-result, and a review-result is what closes an artifact "
                f"postcondition -- so a path outside the binding would let any JSON file carrying "
                f"a `consolidation` key close a gate. Put the child under the spine's work area, "
                f"or use the CLI, which is per-call by construction."
            )

    # `amend`'s --delta is the SAME hazard as --from-child (a filesystem path the
    # engine will read and act on), so it goes through the SAME containment
    # predicate (`_resolve_confined`) rather than a second one -- but NOT the same
    # relative-path rule: `amend()` does a bare `Path(args.delta).read_text()`,
    # with no base-dir join of its own (unlike `advance()`'s from_child), so a
    # relative --delta resolves against the process's cwd, not SPINE.parent -- and
    # since issue #568 that cwd is the bound spine's worktree by the time the
    # engine reads it, while this check runs before the door moves there (see
    # `_resolve_confined`'s docstring). This door only ever writes the delta file
    # itself, beside the spine it amends (see `_write_amend_delta`, always an
    # absolute path), so this whole branch is defense in depth against a future
    # change to that call site, not a path a caller can steer today -- `delta` is
    # declared as a JSON object in the tool schema, never as a path argument.
    resolved_delta = getattr(ns, "delta", None)
    if resolved_delta:
        resolved, escapes = _resolve_confined(resolved_delta, join_relative_to=None)
        if escapes:
            return (
                f"REFUSED: --delta names a delta file INSIDE the bound spine's own directory "
                f"({str(SPINE.parent)!r}); this call resolves it to {str(resolved)!r}, which is "
                f"outside. `amend` applies the delta's ops to the bound spine's own gates, so a "
                f"path outside the binding could feed re-planning ops read from anywhere on disk."
            )
    return None


@contextlib.contextmanager
def _standing_in_the_bound_spines_worktree():
    """Stand in the bound spine's OWN worktree for the duration of the block,
    then return to where the process was, unconditionally (issue #568).

    Why the door moves at all. `checklist_engine.origin_worktree_refusal`
    compares a spine's stamped `origin.worktree` against the engine's AMBIENT
    cwd, and `run_engine` calls the engine IN PROCESS -- so "where this door's
    process happens to stand" became load-bearing engine input. It is not
    input this door can supply by argument: the guard deliberately has no off
    switch outside the spine. The structural case is `spine_open`, which
    creates a NEW worktree and stamps `origin.worktree` to it; the next verb on
    that spine is `claim`, and a process cannot already be standing inside a
    directory that did not exist a moment earlier. Moving for the length of one
    engine call is what makes the door genuinely BE in the tree it is driving,
    rather than exempt from a rule everyone else obeys.

    The derivation is `_worktree_root_for_lifecycle` (defined below, resolved at
    call time) -- `git rev-parse --show-toplevel` from the spine's own
    directory. Deliberately the same one `spine_close` uses, not a second
    derivation that could disagree with it.

    Unresolvable is NOT a failure. A spine outside any worktree, a removed
    directory, no `git` on PATH: no chdir happens and the call proceeds exactly
    as it did before this change. A door that cannot locate a tree must not
    become a door that cannot run.

    `chdir` is process-global, so this is only safe because the door handles
    exactly ONE request at a time: `main()` is a plain `for line in sys.stdin:`
    loop that writes each reply before reading the next line, and the module
    imports no threading, asyncio or multiprocessing. There is no second
    in-flight request whose cwd this could corrupt.
    `tests/test_mcp_door_engine_cwd.py::SingleThreadedDoorPinTests` pins both
    halves of that so a future concurrent door fails there instead of here.

    The restore is in a `finally`, so it runs on a normal return, on an
    exception and on `SystemExit` alike. It is NOT itself guarded: if the
    directory we came from has vanished, that surfaces as a failed call rather
    than a server left silently standing somewhere it did not choose."""
    moved = False
    previous = None
    try:
        previous = os.getcwd()
        target = _worktree_root_for_lifecycle()
        if target.is_dir():
            os.chdir(target)
            moved = True
    except Exception:  # noqa: BLE001 - any failure to locate the tree means "do not move"
        moved = False
    try:
        yield
    finally:
        if moved:
            os.chdir(previous)


def run_engine(verb: str, *rest: str, mutating: bool = True) -> dict:
    """Call the real engine main() with a constructed argv. This is the ONLY
    place this module talks to the engine, and it never inspects or rewrites
    the output beyond capturing it -- see module docstring.

    Before the call, `_identity_violation` asks the engine's own parser what
    this argv actually resolves to and refuses if it is not the bound spine
    under the bound session. That check sits INSIDE the redirect block on
    purpose: `parse_args` writes a usage block to stderr and raises
    SystemExit(2) on malformed argv, and outside this block that text would
    escape onto the real transport's stderr and the exit would take the whole
    server process down with it.

    The engine call itself runs inside `_standing_in_the_bound_spines_worktree`
    -- the door deliberately stands in the spine's own tree for that call, and
    only for that call. `_identity_violation` stays OUTSIDE it: it resolves
    caller-supplied paths for containment, and resolving them against a
    directory this door just moved to would change what "confined" means
    mid-check.

    `_unbound_refusal` is asked FIRST, before an argv is even built, and this is
    the second of its two call sites (issue #603). `main()`'s dispatch is the
    first and covers the whole tool surface uniformly; this one is defense in
    depth for the pass-through path specifically, and it is not optional
    politeness: with no spine bound there is no `--file` to construct, and the
    old expression would have handed the engine the string `'None'`. Same
    predicate at both sites, never a second differently-shaped check -- the
    failure `_identity_violation`'s own docstring records six times over."""
    refusal = _unbound_refusal()
    if refusal is not None:
        rec = {"verb": verb, "argv": [verb, *rest], "code": 2,
               "stdout": "", "stderr": refusal + "\n"}
        _log(rec)
        return rec

    argv = ["--file", str(SPINE), verb, *rest]
    if mutating and SESSION:
        argv += ["--session-id", SESSION]
    out, err = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            violation = _identity_violation(argv)
            if violation is not None:
                code = 2
                err.write(violation + "\n")
            else:
                with _standing_in_the_bound_spines_worktree():
                    code = checklist_engine.main(argv)
    except SystemExit as exc:  # argparse rejected the argv (e.g. missing required flag)
        code = int(exc.code or 0)
    except Exception as exc:  # noqa: BLE001 - surface everything, never swallow
        code = 1
        err.write(f"{type(exc).__name__}: {exc}")
    rec = {"verb": verb, "argv": argv, "code": code,
           "stdout": out.getvalue(), "stderr": err.getvalue()}
    _log(rec)
    return rec


def as_result(rec: dict) -> dict:
    """Engine output -> MCP tool result, verbatim. A refusal comes back as
    isError so the model sees a failed tool call, not prose it must parse."""
    text = (rec["stdout"] + rec["stderr"]).strip() or "(no output)"
    return {"content": [{"type": "text", "text": text}], "isError": rec["code"] != 0}


def _log_rejection(tool: str, rejection_class: str, detail: str) -> None:
    """Append ONE record for a door-own rejection to `_rejectionlog()` -- never raises.

    Carries what a diagnosis needs: `tool` (which tool was called), `class` (which
    of the three in-scope rejection shapes this is), `detail` (the door's own
    _tool_error message, naming what was missing/unknown) and `ts` (when).

    **Fail loud, every occurrence.** If the write itself fails, that is reported to
    stderr immediately -- no batching, no once-per-run flag, no retry, no silent
    drop. A capture that swallows its own failure would recreate, one level down,
    exactly the defect it exists to end: a diagnosable event turning invisible.
    """
    record = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tool": tool,
        "class": rejection_class,
        "detail": detail,
    }
    line = json.dumps(record, ensure_ascii=False)
    destination = _rejectionlog()
    if destination is None:
        # No spine bound and no override: no directory to write beside. Skipped,
        # not failed -- see `_log`. The rejection still reaches the caller as the
        # tool result itself, which is the channel that matters.
        return
    try:
        with destination.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write(line + "\n")
    except OSError as exc:
        sys.stderr.write(
            f"REJECTION CAPTURE FAILED: could not write to {destination} "
            f"({type(exc).__name__}: {exc}). Lost record: {line}\n"
        )
        sys.stderr.flush()


def _tool_error(message: str, *, tool: str | None = None, rejection_class: str | None = None) -> dict:
    """The door's OWN rejection result. When `tool`/`rejection_class` are BOTH
    given, this also logs one record via `_log_rejection` before returning --
    folded IN here, rather than a separate wrapper around it, because
    `call_tool()`'s own choke-point pin
    (`tests/test_mcp_identity.py::IdentityBindingPinTests.test_call_tool_can_only_produce_content_two_ways`)
    restricts every `return` in that function to literally
    `as_result(run_engine(...))` or `_tool_error(...)` and nothing else -- a second
    named call at the same site would be a third way to answer, which that pin
    exists to catch. The two optional keywords let this single call satisfy both
    the pin (unchanged call shape) and the capture (issue #541) at once. Callers
    with nothing to log (main()'s dead KeyError fallback in `call_tool`, which
    `TOOL_NAMES` makes unreachable) simply omit them."""
    if tool is not None and rejection_class is not None:
        _log_rejection(tool, rejection_class, message)
    return {"content": [{"type": "text", "text": message}], "isError": True}


def _write_amend_delta(delta: dict) -> Path:
    """Write an `amend` delta BESIDE the bound spine (`SPINE.parent`) -- the
    human's ruling: "we can and should use the agent work folder that is
    coherent per task just like the spine" -- never a system temp dir, so the
    artifact is per-task coherent and survives for audit. This is the ONLY
    place this module builds the `--delta` path handed to the engine; the path
    is never caller-supplied (the tool schema declares `delta` as a JSON
    object, not a path), and it is still run back through
    `_identity_violation`'s `_resolve_confined` containment check before the
    engine ever reads it, the same as `spine_advance.from_child`.

    The engine, not this function, validates the delta's `{"ops": [...]}`
    shape -- this only serialises whatever object the caller sent."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
    path = SPINE.parent / f"mcp_amend_delta_{ts}.json"
    path.write_text(json.dumps(delta, ensure_ascii=False), encoding="utf-8")
    return path


# --------------------------------------------------------------------------- #
# The lifecycle door -- spine_open / spine_close. See the module docstring's
# "The lifecycle door" section for why these are dispatched OUTSIDE call_tool.
# --------------------------------------------------------------------------- #

def _git_rev_parse(*args: str, cwd: Path) -> str:
    """Run one read-only `git rev-parse`, with `cwd` an explicit parameter --
    never the process's own ambient cwd.

    That used to be justified by "this door's request-handling loop never
    changes cwd". It now does, deliberately and narrowly: `run_engine` stands
    in the bound spine's own worktree for the duration of one in-process
    engine call (`_standing_in_the_bound_spines_worktree`, issue #568),
    because the engine's `origin.worktree` guard reads the ambient cwd and a
    door that cannot enter the tree it is driving cannot drive it at all.

    So the explicit parameter is no longer a stylistic preference -- it is
    what keeps every lifecycle question answerable against a NAMED directory
    while the process's own cwd is a thing that moves. Do not "simplify" it
    back to an ambient read.

    Raises `RuntimeError` on a non-zero exit, naming the directory and git's
    own stderr."""
    proc = subprocess.run(["git", "rev-parse", *args], cwd=str(cwd), capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"git rev-parse {' '.join(args)} failed in {cwd}: {proc.stderr.strip()}")
    return proc.stdout.strip()


def _primary_checkout_for_lifecycle() -> Path:
    """The PRIMARY checkout: the BOUND SPINE's own, falling back to THIS
    SCRIPT's own when nothing is bound. Never the ambient cwd.

    This used to read `os.environ["SPINE_FILE"]` unconditionally, so that
    `_spine_open`'s own source never contained the identifier `SPINE`. That
    worked only while every door was born bound. Gate g3 (issue #603) makes an
    UNBOUND door reachable, and `spine_open` is the one tool it must serve -- at
    which point that read is a `KeyError`, raised on `spine_open`'s own path,
    and `_spine_open` catches `(OSError, RuntimeError)`, which does not include
    it. Measured: the caller got `tool error: missing or unknown 'SPINE_FILE'`,
    not a binding and not even a refusal.

    **The fallback is a fallback, not a replacement, and that was measured the
    hard way.** The handoff's preferred answer was to derive from
    `Path(__file__)` outright. Both derivations return the SAME primary checkout
    in production -- verified from a linked worktree's `scripts/` and from the
    primary checkout's own -- because the door is addressed as the
    project-relative `scripts/mcp_spine_server.py` and therefore always runs
    from inside the checkout it serves. But they part company the moment the
    script and the spine live in DIFFERENT repositories, and one caller does
    exactly that: `tests/test_mcp_lifecycle.py::FullStdioRoundTripTests` binds a
    door to a spine in a throwaway repo while running this repo's own script.
    Under the outright replacement that test opened `roundtrip-work` in the
    DEVELOPER'S REAL CHECKOUT and still passed, because `spine_close` tidied up
    after it. A derivation that can silently redirect `spine_open` into a
    different repository than the caller's own spine is not a safe default.

    So the bound spine still answers whenever there IS one -- unchanged
    behaviour, unchanged isolation -- and the script's location answers only the
    case the old form could not answer at all. `SPINE` is read here rather than
    `os.environ` because they cannot disagree (`_bind_process_to` writes both)
    and the global is already `None`-safe; the identifier ban is on
    `_spine_open`'s own source, which this function is not.

    This adds no fourth ambient input: no new environment variable, no cwd read.
    A door outside any checkout AND unbound fails to resolve, which surfaces as
    `_spine_open`'s existing `(OSError, RuntimeError)` refusal, not a crash.

    This is `open_work`'s own `root`:
    `scripts/spine_lifecycle.py`'s `_default_wt_root` is the ONE place that
    answers "where do worktrees live" -- `<root>/.worktrees`, nested under the
    primary checkout -- so a NEW worktree must always nest under the primary
    checkout, never under whatever (possibly already-linked) worktree this
    door's own bound spine happens to live in.

    `git rev-parse --git-common-dir` resolves to the PRIMARY checkout's `.git`
    from ANY worktree, linked or not -- `verify_worktree_isolation.
    primary_checkout()` does the same resolution but reads it off the
    process's ambient cwd; this does the identical join, explicit about
    `cwd` instead. A linked worktree's common dir is already absolute; the
    primary checkout's own is `.git`, relative to `cwd` -- joined against
    `spine_dir`, never `Path.resolve()`'s implicit reliance on the real cwd.

    That last distinction hardened from preference into requirement when
    `run_engine` began entering the bound spine's worktree for the length of
    one engine call (`_standing_in_the_bound_spines_worktree`, issue #568).
    Nothing here runs inside that window, but this process's cwd is no longer
    a constant, so an ambient read would be answering a different question
    depending on when it ran."""
    anchor = SPINE.parent if SPINE is not None else Path(__file__).resolve().parent
    common = Path(_git_rev_parse("--git-common-dir", cwd=anchor))
    if not common.is_absolute():
        common = anchor / common
    return common.resolve().parent


def _checkout_containing(directory: Path) -> Path:
    """The checkout `directory` belongs to -- `git rev-parse --show-toplevel`,
    resolved. A LINKED worktree answers with itself, not with the primary
    checkout; that is the whole difference from `--git-common-dir`.

    One derivation, three anchors, each named by its caller: the bound spine's
    own directory (`_worktree_root_for_lifecycle`, for standing in the tree and
    for `close_work`'s `root`), and either that or this script's own directory
    (`_own_checkout_for_binding`, for `spine_bind`'s containment). Extracted so
    those questions cannot be answered by two subtly different derivations --
    the failure `_identity_violation`'s own docstring records six times over.
    `cwd` is explicit here, as everywhere: this process's own cwd moves for the
    length of an engine call (`_standing_in_the_bound_spines_worktree`)."""
    return Path(_git_rev_parse("--show-toplevel", cwd=directory)).resolve()


def _own_checkout_for_binding() -> Path:
    """The ONE checkout this door may bind a spine within: **its own** -- the
    bound spine's when there is one, and THIS SCRIPT's own when there is not.

    **Deliberately NOT `_primary_checkout_for_lifecycle()`, and that distinction
    is this gate's whole security content.** That helper resolves
    `--git-common-dir`, which jumps from any worktree to the PRIMARY checkout --
    and `.worktrees/` nests INSIDE the primary checkout, so a root derived that
    way admits every sibling lane's work area. Measured in the live tree when
    this was written, counting readable JSON objects under an `.agent-work/`
    carrying a derivable `work_id`:

      --git-common-dir root  6102 candidates, 307 under an active lease
      --show-toplevel  root  1014 candidates,  51 under an active lease

    The 5088-file difference is other lanes' work. `_primary_checkout_for_lifecycle`
    is right for `spine_open`, which must CREATE a worktree and therefore must
    nest it under the primary checkout; it is wrong for `spine_bind`, which must
    not reach one. Two questions, two roots, both named.

    The property, stated so it can be attacked: **one checkout's work-area tree
    per process.** `_spine_bind` confines to `<this>/.agent-work/` and
    additionally refuses any candidate whose OWN `--show-toplevel` differs from
    this one, which is what makes the isolation claim true rather than
    aspirational -- lexical containment alone would admit a checkout nested
    inside the work area.

    **Both halves of that pair are asked of the RESOLVED path, and the property
    was false until they were.** The reviewer of this gate defeated the second
    half with a symlink: the link sat inside this work area, so lexical
    containment (which resolves) passed, and the cross-checkout check asked git
    about the LINK's parent -- this door's own directory -- rather than the
    target's, so it passed too. A nested linked worktree's spine and an unrelated
    repository's spine were both bound that way. The property now holds by any
    spelling of the path, which is the only form of it worth stating.

    Unbound, the anchor is `Path(__file__).resolve().parent`, which is the same
    fallback `_primary_checkout_for_lifecycle` uses and for the same reason: it
    is the only anchor an unbound door has that is not ambient. NOT the process
    cwd -- `_spine_from_env`'s docstring records that `Path("").resolve()` once
    "silently bound the door to whatever directory it was standing in", and that
    cwd now MOVES mid-call. And not a new environment variable: a launcher that
    knows the work area's path can set `SPINE_FILE` in the same breath, so the
    variable would buy nothing (`IDENTITY_TRADE.md` §3).

    `.mcp.json` launches the door as the project-relative
    `scripts/mcp_spine_server.py`, so a crew running inside a linked worktree
    runs THAT worktree's copy and this resolves to that worktree -- which is
    exactly where its own `IMPLEMENTER_PLAN.json` lives. An Admiral in the
    primary checkout resolves to the primary checkout, where its own
    `spine.json` lives. Both real cases are inside their own answer."""
    anchor = SPINE.parent if SPINE is not None else Path(__file__).resolve().parent
    return _checkout_containing(anchor)


def _derivable_work_id(spine: dict) -> str | None:
    """The `work_id` a spine dictates for itself: `origin.work_id` when present,
    else the spine's own top-level `work_id`. None when neither is there.

    **The fallback is not a convenience, it is the correction this gate exists
    for.** `origin` is stamped only by `open_work` (via `build_origin`), so
    deriving from `origin.work_id` alone refuses every spine minted another way
    -- `init_work_area.py`, `generate_spine.py`, a hand-compiled plan. Measured
    over the live population (spine-shaped files under `.agent-work/` and
    `.worktrees/*/.agent-work/`, excluding `archive/` and `templates/`): 5 of 60
    carry `origin.work_id`, 55 carry only the top-level `work_id`, 0 carry
    neither. The 55 include `.agent-work/epic-567-door/spine.json` -- an
    Admiral's own live spine -- and
    `.agent-work/implementer-315-native-g1/IMPLEMENTER_PLAN.json`, which are the
    two cases this tool exists for. A door that could bind neither of them would
    be theatre.

    `origin.work_id` still WINS where present, so a spine `open_work` minted
    yields byte-identical identity through either field.

    Whitespace-only and non-string values are read as absent, not as an identity:
    `checklist_engine.claim` refuses an empty `--session-id`, so a session of
    `constellation/` is a door that cannot claim, and a door that cannot claim is
    not bound. Fail closed."""
    origin = spine.get("origin")
    if isinstance(origin, dict):
        stamped = origin.get("work_id")
        if isinstance(stamped, str) and stamped.strip():
            return stamped
    own = spine.get("work_id")
    if isinstance(own, str) and own.strip():
        return own
    return None


def _worktree_root_for_lifecycle() -> Path:
    """The worktree `SPINE` itself lives in -- its own toplevel, NOT the
    primary checkout. This is `close_work`'s own `root`: it computes
    `work_id` as `spine_path.parent.relative_to(root / ".agent-work")`, and a
    spine `open_work` created lives under a LINKED worktree's `.agent-work/`,
    not the primary checkout's (`tests/test_spine_lifecycle.py`'s own
    `TestCloseWorkEndToEndRealEngine` passes `root=worktree`, the linked
    worktree, never the repo it was opened from) -- so this is deliberately
    NOT `_primary_checkout_for_lifecycle`, a different derivation for a
    different question. Safe to read `SPINE` here: unlike `_spine_open`,
    `_spine_close` acts on the bound spine by design.

    The `--show-toplevel` resolution itself lives in `_checkout_containing`,
    shared with `spine_bind`'s containment root; this function's own content is
    the choice of ANCHOR, which is the part that differs."""
    return _checkout_containing(SPINE.parent)


def _bind_process_to(spine_file: str, session: str) -> None:
    """THE one place `SPINE` and `SESSION` are assigned outside module scope.

    `decision:bind-on-open-over-new-verb`: a successful `spine_open` binds THIS
    process to the spine it just minted, rather than the caller having to
    relaunch the door to use work it just created. Before this, a session that
    started with no `SPINE_FILE` could mint a spine and then do nothing with it,
    which is the epic's exit criterion left unmet.

    **Both roots, never one.** `open_work` returns THREE binding values and two
    of them are identity: `SPINE_FILE` and `SPINE_SESSION`. Binding the spine
    alone leaves `SESSION` empty, `run_engine` then omits `--session-id`, and
    `checklist_engine.claim` refuses with "claim requires a non-empty
    --session-id". A door that cannot `claim` is not bound, so "bound" here
    means both.

    **`decision:one-spine-per-process-stands`.** This changes WHEN the binding
    is decided, never HOW MANY are live: one process still drives exactly one
    spine at a time, and `_rebind_refusal` blocks the swap while this process
    still holds an active lease. `_identity_violation` is untouched and keeps
    comparing against `SPINE` at CALL time, so it refuses a foreign spine after
    a rebind exactly as it did before -- the binding moved, the guard did not.

    `os.environ` is updated alongside the globals so the two views of this
    door's identity cannot disagree for any later reader; the module docstring's
    "bound at server-launch time" is now "bound at launch OR at `spine_open`",
    and nothing may be left describing the previous spine.

    Deliberately narrow: this takes the two values as plain strings and assigns
    them. It does not decide WHETHER to rebind (`_rebind_refusal`), and it does
    not mint anything (`spine_lifecycle.open_work`). A single named binder is
    what makes the module-wide AST pin in `tests/test_mcp_lifecycle.py`
    expressible at all -- that pin asserts the set of assignments to these two
    names is exactly {module scope, this function}, so a second, quieter rebind
    site added later fails there."""
    global SPINE, SESSION
    SPINE = Path(spine_file).resolve()
    SESSION = session
    os.environ["SPINE_FILE"] = str(SPINE)
    os.environ["SPINE_SESSION"] = session


def _rebind_refusal(acting_tool: str = "spine_open") -> str | None:
    """May this process rebind? None when it may, else the refusal.

    `acting_tool` exists because the refusal names the tool to retry, and there
    are now two tools that rebind (`spine_open` mints and binds; `spine_bind`
    binds a spine that already exists). ONE parameter on ONE text, never a second
    refusal function answering the same question in different words -- the
    failure `_identity_violation`'s own docstring records six times over. The
    sentence is "Rebinding this door now", which is accurate for both: even for
    `spine_open` the check runs before anything is minted, precisely because the
    REBIND is what it protects.

    **Ruled for gate g3:** a rebind is refused while this process still HOLDS an
    active lease on its current spine. A lease records who is driving; rebinding
    out from under one leaves a lease on a spine nobody is holding, and the next
    session to arrive must then force it. Releasing first is one call
    (`spine_lease` `action: release`) and is what the door's own closeout
    already does.

    Scoped to a lease THIS process holds -- `session_id == SESSION` -- not to
    any active lease at all. A lease held by some other session is not this
    door's to orphan, and refusing on it would let an unrelated agent's stale
    lease block this one from opening new work.

    Fails OPEN, deliberately, in three directions: nothing bound, an unreadable
    or unparseable spine, and no lease. In each case there is demonstrably no
    lease of ours to orphan, so there is nothing for this check to protect --
    and a check that refuses when it cannot answer would make an unbound door
    unable to open the work it exists to open. `checklist_engine._active_lease`
    is reused rather than re-deriving "is this lease live", so this cannot drift
    from the engine's own reading of its own field."""
    spine = SPINE
    if spine is None or not SESSION or _unbound_refusal() is not None:
        return None
    try:
        current = json.loads(spine.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    lease = checklist_engine._active_lease(current) if isinstance(current, dict) else None
    if lease is None or lease.get("session_id") != SESSION:
        return None
    return (
        f"REFUSED: this door still holds an active lease on {str(spine)!r} as "
        f"{SESSION!r}, and one door drives one spine at a time. Rebinding this door now "
        f"would leave that lease held by nobody. Release it first (`spine_lease` with "
        f"action 'release'), then call `{acting_tool}` again."
    )


def _lifecycle_result(payload: dict) -> dict:
    """The lifecycle door's OWN success answer: the returned dict, JSON-encoded
    as text, `isError: False`. Mirrors `as_result`'s content/isError shape
    without going through `run_engine` -- a lifecycle call is not an engine
    pass-through (see the module docstring)."""
    return {"content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False)}], "isError": False}


def _spine_open(args: dict) -> dict:
    """`spine_open`'s own dispatch path. Never references `SPINE`, `SESSION`
    or `run_engine` -- checked by `tests/test_mcp_lifecycle.py`, with a
    mutated positive control proving that check can fail. It acts on a spine
    that does not exist yet, so nothing here may presuppose one is bound: the
    repo root comes from `_primary_checkout_for_lifecycle`, which reads no
    environment at all -- the bound spine's own checkout when there is one,
    THIS SCRIPT's own location when there is not, which is the unbound case
    this tool exists to serve -- and `parent` comes from `SPINE_PARENT` (the
    dispatching session this door's own process was launched under -- a
    DIFFERENT env var from `SPINE_SESSION`/`SESSION`, never read elsewhere in
    this module).

    Containment: the candidate worktree path `work_id` derives is resolved
    against `wt_root` through `_resolve_confined` -- the SAME predicate
    `_identity_violation` already uses for `--from-child`/`--delta`, reused
    rather than a second, differently-shaped check, just with `wt_root` (not
    `SPINE.parent`) as `bound_dir`. This is defense in depth: `open_work`
    itself already refuses an unsafe `work_id` via `run_crew.validate_work_id`
    before it ever runs `git worktree add`; this check runs before `open_work`
    is even called, and it is what `tests/test_mcp_lifecycle.py` exercises
    against `_resolve_confined` directly."""
    err = _require(args, "work_id", "spec")
    if err:
        return _tool_error(
            f"spine_open: {err}", tool="spine_open", rejection_class="missing-required-argument",
        )
    work_id = args["work_id"]
    spec = args["spec"]
    if not isinstance(spec, dict) or not spec:
        return _tool_error(
            "spine_open: spec must be a non-empty JSON object",
            tool="spine_open", rejection_class="bad-argument-type",
        )
    base = args.get("base") or "HEAD"

    # Asked BEFORE anything is minted. A refusal that arrived after `open_work`
    # would leave a real branch and a real worktree behind for work this door
    # then declined to drive.
    blocked = _rebind_refusal()
    if blocked is not None:
        return _tool_error(blocked, tool="spine_open", rejection_class="lease-held")

    try:
        root = _primary_checkout_for_lifecycle()
    except (OSError, RuntimeError) as exc:
        return _tool_error(
            f"spine_open: could not resolve the primary checkout: {exc}",
            tool="spine_open", rejection_class="root-resolution-failed",
        )

    wt_root = Path(spine_lifecycle._default_wt_root(root))
    candidate, escapes = _resolve_confined(
        spine_lifecycle.worktree_path_for(work_id, wt_root=str(wt_root)),
        join_relative_to=None, bound_dir=wt_root,
    )
    if escapes:
        return _tool_error(
            f"spine_open: work_id {work_id!r} resolves to a worktree path outside "
            f"{wt_root} ({candidate}); refused before `git worktree add` would ever run",
            tool="spine_open", rejection_class="path-escape",
        )

    parent = os.environ.get("SPINE_PARENT") or "unknown"
    try:
        opened = spine_lifecycle.open_work(work_id, spec, root=root, base=base, parent=parent)
    except spine_lifecycle.SpineLifecycleError as exc:
        return _tool_error(f"spine_open: {exc}", tool="spine_open", rejection_class="open-refused")

    # The open succeeded, so this door now drives what it just minted
    # (`decision:bind-on-open-over-new-verb`). Both identity roots, from
    # `open_work`'s own return value -- binding the spine without the session
    # produces a door that cannot `claim`, which is not a bound door.
    _bind_process_to(opened["SPINE_FILE"], opened["SPINE_SESSION"])
    return _lifecycle_result(opened)


#: The closing clause every containment refusal in this module ends with, so a
#: caller who is confined meets ONE consistent way out rather than three
#: differently-worded ones. Lifted from `_identity_violation`'s own escape
#: hatches for `--from-child` and `--delta`.
_THE_CLI_IS_PER_CALL = (
    "Name a spine under that work area, or use the CLI, which is per-call by construction."
)


def _spine_bind(args: dict) -> dict:
    """`spine_bind`'s own dispatch path: bind this door to a spine that ALREADY
    EXISTS (issue #567, lane A).

    **Why this exists.** The previous lane made rebinding SAFE -- one named binder
    (`_bind_process_to`), an AST pin over it, late-bound telemetry, an uncached
    `_unbound_refusal` -- and left it with one trigger: `spine_open`, which MINTS.
    So an unbound door faced with work that already exists had nothing to call.
    `decision:bind-on-open-over-new-verb` already moved WHEN the binding is
    decided; this adds one more moment, before any verb runs, and never a second
    live binding. `decision:one-spine-per-process-stands`: the count never rises
    above one.

    **This function assigns neither `SPINE` nor `SESSION`.** It calls
    `_bind_process_to` and lets that function move both roots together, which is
    what keeps the module-wide AST pin
    (`tests/test_mcp_lifecycle.py::OneBinderPinTests`) expressible. Binding the
    spine without the session yields a door that cannot `claim`, which is not a
    bound door.

    **The identity is the SPINE's, never the caller's.** Derived through
    `_derivable_work_id` and `spine_lifecycle.session_id_for` -- the same function
    `open_work` returns `SPINE_SESSION` from -- so after this returns, this door
    is indistinguishable from a door LAUNCHED bound to that spine. A `session`
    argument was settled against in `IDENTITY_TRADE.md` §3 Option B: "any string
    it can supply, it can supply its parent's."

    Nine refusals, in dispatch order, each a pure function of `(args, SPINE,
    filesystem)` and each reachable on its own
    (`tests/test_mcp_spine_bind.py`). Each returns through `_tool_error` with a
    `rejection_class`, so every one lands in the rejection log:

      R1  missing-required-argument  no `spine_file`
      R2  bad-argument-type          not a non-empty string
      R2b bad-argument-type          a string, but no path resolves from it
      R0  (SUCCESS)                  already bound to this exact path -- a no-op
      R3  root-resolution-failed     this door's own checkout will not resolve
      R4  path-escape                outside `<own checkout>/.agent-work/`
      R5  no-spine-there             nothing readable at that path
      R6  cross-checkout             the resolved path's own checkout is not ours
      R7  not-a-spine                not a JSON object
      R8  no-derivable-identity      neither `origin.work_id` nor `work_id`
      R9  identity-held              that identity is live somewhere else
      R10 lease-held                 this door still holds a lease of its own

    **R0 is FIRST of the guards that read the world, and the ordering is easy to
    get backwards.**
    `_rebind_refusal` refuses whenever this process holds an active lease -- so an
    agent that binds, claims, then calls `spine_bind` again with the SAME path (a
    retry, a resumed transcript, a re-read of its own state) would be refused for
    rebinding to where it already is, and told to release a lease it correctly
    holds. R0 makes the second call a no-op that succeeds and changes nothing: no
    `_bind_process_to`, no environment write, no engine contact. Comparison is on
    `resolve()`, matching `_bind_process_to`'s own, so a relative path, a symlink
    or a trailing-slash spelling of the bound spine reads as the same spine.

    **R6 is what makes the isolation claim true rather than aspirational, and it
    only became true when it started resolving.** R4 is lexical, and a checkout
    can be NESTED under `.agent-work/`, at which point a path inside the boundary
    is still in another repository. So the RESOLVED path's own `--show-toplevel`
    is asked and compared. Resolved, because R4 returns its candidate unresolved:
    while R6 asked git about `candidate.parent`, a symlink inside this door's own
    work area pointing at a nested checkout's spine satisfied both guards at once
    -- R4 followed the link and saw the target inside the boundary, R6 did not
    follow it and saw our own directory. This gate's reviewer bound both a nested
    linked worktree's spine and a wholly separate repository's spine that way. See
    `_own_checkout_for_binding` for the measured reach delta this pair buys and
    `tests/test_mcp_spine_bind.py::ASymlinkCannotHideAnotherCheckoutTests` for the
    topology that can see the difference.

    Reuse, never a second notion: `_resolve_confined` for containment (the same
    predicate `_identity_violation` and `_spine_open` already use, with a
    different `bound_dir`), `_unusable_spine_reason` for the usability ladder
    shared with `_unbound_refusal`, `checklist_engine._active_lease`/`_is_stale`/
    `load_config` for "is this identity live", `_rebind_refusal` for "may this
    door rebind at all"."""
    err = _require(args, "spine_file")
    if err:
        return _tool_error(
            f"spine_bind: {err}", tool="spine_bind",
            rejection_class="missing-required-argument",
        )
    raw = args["spine_file"]
    # `bool` is excluded explicitly: `True` is an `int`, not a `str`, but a
    # truthy non-string reaching `Path()` would raise rather than refuse.
    if not isinstance(raw, str) or not raw.strip():
        return _tool_error(
            "spine_bind: spine_file must be a non-empty path to an existing spine file",
            tool="spine_bind", rejection_class="bad-argument-type",
        )

    # R2b -- the string will not resolve to a path at all. Placed BEFORE R0
    # because R0's own `resolve()` is one of the two lines that raised: a NUL byte
    # makes `Path(raw).resolve()` raise `ValueError: embedded null byte`, and
    # `main()`'s lifecycle branch catches only `KeyError`, so the exception unwound
    # out of `main()` and the door EXITED -- taking all twelve tools with it for
    # the rest of the session, and giving the next call a `BrokenPipeError`. That
    # is the opposite of this gate's Protected Intent ("Fail closed. A spine that
    # cannot be identified refuses"): it neither refused nor logged a rejection.
    # `spine_bind` is the first lifecycle tool to take a caller-supplied filesystem
    # path -- the pre-existing analogue, `spine_advance`'s `--from-child`, survives
    # only because `_identity_violation` runs inside `run_engine`'s
    # `except Exception` net, and the lifecycle path has no such net -- and it is
    # reachable with NOTHING bound (`BINDS_WITHOUT_A_BOUND_SPINE`), so it is
    # reachable at the moment an agent has no other way in. `OSError` and
    # `RuntimeError` join `ValueError` for the same reason the two root resolutions
    # below catch them: a name too long and a symlink loop are the same class of
    # answer as a NUL, and each must be a refusal rather than a dead door.
    try:
        requested = Path(raw).resolve()
    except (OSError, ValueError, RuntimeError) as exc:
        return _tool_error(
            f"spine_bind: spine_file is not a usable filesystem path "
            f"({type(exc).__name__}: {exc}). Pass an absolute path to a spine file that "
            f"exists -- the SPINE_FILE value `spine_open` returned.",
            tool="spine_bind", rejection_class="bad-argument-type",
        )

    # R0 -- already bound here. Asked before anything that reads the filesystem or
    # git, including the root: a no-op cannot escape a boundary it does not cross.
    if SPINE is not None and requested == SPINE:
        return _lifecycle_result({
            "SPINE_FILE": str(SPINE), "SPINE_SESSION": SESSION,
            "already_bound": True,
            "note": "this door was already bound to that spine; nothing changed",
        })

    try:
        checkout = _own_checkout_for_binding()
    except (OSError, RuntimeError) as exc:
        return _tool_error(
            f"spine_bind: could not resolve the checkout this door may bind within: {exc}",
            tool="spine_bind", rejection_class="root-resolution-failed",
        )
    work_area = checkout / ".agent-work"

    candidate, escapes = _resolve_confined(raw, join_relative_to=None, bound_dir=work_area)
    if escapes:
        return _tool_error(
            f"REFUSED: this door may only bind a spine inside its OWN checkout's work area "
            f"({str(work_area)!r}); spine_file resolves to {str(candidate.resolve() if candidate.is_absolute() else candidate)!r}, "
            f"which is outside. One checkout's work-area tree per process: a spine elsewhere "
            f"-- including a sibling worktree of this same repository -- belongs to work whose "
            f"worktrees, hooks and tests this door knows nothing about, and binding it would "
            f"make this process the driver of a run it cannot see. {_THE_CLI_IS_PER_CALL}",
            tool="spine_bind", rejection_class="path-escape",
        )

    why = _unusable_spine_reason(candidate)
    if why is not None:
        return _tool_error(
            f"REFUSED: spine_bind was given {str(candidate)!r}, but {why} -- so there is no "
            f"spine there to bind. Name a spine file that exists, or call `spine_open` to "
            f"mint one.",
            tool="spine_bind", rejection_class="no-spine-there",
        )

    # R6 asks git about the RESOLVED path, and the `resolve()` is the whole guard.
    # `_resolve_confined` computes containment on `p.resolve()` but returns the
    # candidate UNRESOLVED -- so a SYMLINK at `<work area>/link.json` pointing at a
    # spine in another checkout passed R4 (the target is inside the boundary) and
    # then passed R6 too, because `candidate.parent` is our own work area and git
    # dutifully answered with our own checkout. This gate's reviewer bound a nested
    # linked worktree's spine and a wholly separate repository's spine exactly that
    # way (`tests/test_mcp_spine_bind.py::ASymlinkCannotHideAnotherCheckoutTests`).
    # Resolving first asks about the spine this door would ACTUALLY drive, which is
    # the same path `_bind_process_to` resolves and the same one R4's own refusal
    # text names. `_identity_violation`'s docstring records six guards each
    # defeated by a shape it had not enumerated; this one enumerated a single
    # spelling of "which checkout is this path in", and one resolve retires the
    # spelling question rather than adding a second guard beside it.
    resolved = candidate.resolve()
    try:
        candidate_checkout = _checkout_containing(resolved.parent)
    except (OSError, RuntimeError) as exc:
        return _tool_error(
            f"spine_bind: could not resolve which checkout {str(resolved)!r} belongs to: {exc}",
            tool="spine_bind", rejection_class="root-resolution-failed",
        )
    if candidate_checkout != checkout:
        return _tool_error(
            f"REFUSED: {str(resolved)!r} sits inside a DIFFERENT checkout "
            f"({str(candidate_checkout)!r}) than this door's own ({str(checkout)!r}), even "
            f"though its path is under this door's work area -- a checkout nested there is "
            f"still another repository. One checkout's work-area tree per process. "
            f"{_THE_CLI_IS_PER_CALL}",
            tool="spine_bind", rejection_class="cross-checkout",
        )

    try:
        payload = json.loads(candidate.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return _tool_error(
            f"REFUSED: {str(candidate)!r} does not hold a JSON object, so it is not a spine "
            f"this door could drive ({type(exc).__name__}). Name the SPINE_FILE `spine_open` "
            f"returned, or call `spine_open` to mint one.",
            tool="spine_bind", rejection_class="not-a-spine",
        )
    if not isinstance(payload, dict):
        return _tool_error(
            f"REFUSED: {str(candidate)!r} does not hold a JSON object (it holds a "
            f"{type(payload).__name__}), so it is not a spine this door could drive. Name the "
            f"SPINE_FILE `spine_open` returned, or call `spine_open` to mint one.",
            tool="spine_bind", rejection_class="not-a-spine",
        )

    work_id = _derivable_work_id(payload)
    if work_id is None:
        return _tool_error(
            f"REFUSED: {str(candidate)!r} carries neither `origin.work_id` nor a top-level "
            f"`work_id`, so this door cannot derive the session identity that spine is driven "
            f"under -- and a door bound with no session cannot `claim` "
            f"(`checklist_engine.claim` refuses an empty --session-id), which means it would "
            f"not be a bound door at all. Every spine the engine drives carries a `work_id`; "
            f"a fragment or a hand-written JSON file does not. Drive that one through the CLI, "
            f"which takes --session-id per call.",
            tool="spine_bind", rejection_class="no-derivable-identity",
        )
    session = spine_lifecycle.session_id_for(work_id)

    # R9 -- the identity this bind would ASSUME is live somewhere else. Scoped to
    # that identity, not to any active lease at all: another session's lease is
    # not this door's to collide with, and refusing on it would let an unrelated
    # agent's lease block a legitimate bind. Staleness preserves the legitimate
    # case -- `run_crew.assignment_session_name`'s docstring records that a
    # respawn MUST reproduce its predecessor's session string, and a genuine
    # respawn follows a DEAD predecessor.
    lease = checklist_engine._active_lease(payload)
    if lease is not None and lease.get("session_id") == session:
        config = checklist_engine.load_config(payload, candidate.parent)
        if not checklist_engine._is_stale(lease, config):
            return _tool_error(
                f"REFUSED: {str(candidate)!r} is under an active lease held as {session!r}, and "
                f"that is the very identity this bind would take (it is derived from the "
                f"spine's own work id, never supplied). Two processes under one session id are "
                f"indistinguishable to the engine, so this bind would put two agents on one "
                f"lease. Whoever holds it must release it first (`spine_lease` with action "
                f"'release'), or its lease must go stale.",
                tool="spine_bind", rejection_class="identity-held",
            )

    blocked = _rebind_refusal("spine_bind")
    if blocked is not None:
        return _tool_error(blocked, tool="spine_bind", rejection_class="lease-held")

    _bind_process_to(str(candidate), session)
    return _lifecycle_result({
        "SPINE_FILE": str(candidate.resolve()), "SPINE_SESSION": session,
        "work_id": work_id, "already_bound": False,
        "note": "this door now drives that spine; call spine_status to see where it is",
    })


def _spine_close(args: dict) -> dict:  # noqa: ARG001 - spine_close takes no arguments; args always {}
    """`spine_close`'s own dispatch path. Acts on `SPINE` -- the spine THIS
    door is bound to -- and nothing else; there is no field to redirect
    because the tool schema declares none. `close_work` itself refuses,
    doing nothing at all, unless the caller already drove the bound spine to
    a released, terminal close through the existing `spine_advance`/
    `spine_lease` tools (see `scripts/spine_lifecycle.py`'s own docstring)."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    try:
        root = _worktree_root_for_lifecycle()
    except (OSError, RuntimeError) as exc:
        return _tool_error(
            f"spine_close: could not resolve the bound spine's own worktree: {exc}",
            tool="spine_close", rejection_class="root-resolution-failed",
        )
    try:
        closed = spine_lifecycle.close_work(SPINE, root=root, today=today)
    except spine_lifecycle.SpineLifecycleError as exc:
        return _tool_error(f"spine_close: {exc}", tool="spine_close", rejection_class="close-refused")
    return _lifecycle_result(closed)


def call_lifecycle_tool(name: str, args: dict) -> dict:
    """A NEW MODULE-LEVEL SIBLING of `call_tool`, never a branch inside it --
    `call_tool`'s own choke-point pin
    (`tests/test_mcp_identity.py::IdentityBindingPinTests.test_call_tool_can_only_produce_content_two_ways`)
    resolves `call_tool`'s `ast.FunctionDef` node BY NAME and walks only that
    subtree, so a true sibling function is structurally outside it and that
    pin stays exactly as strict, untouched.

    `spine_open` and `spine_close` are NOT pass-throughs the way the other 9
    tools are -- neither ever calls `run_engine` -- so they get their OWN
    containment pin here rather than inheriting one written for a different
    hazard (`tests/test_mcp_lifecycle.py`): an AST pin restricting THIS
    function's own return shapes to `_spine_open(...)`/`_spine_close(...)`
    (mirroring `call_tool`'s `as_result(run_engine(...))`/`_tool_error(...)`
    shape), plus the `SPINE`/`SESSION`/`run_engine` non-reference check on
    `_spine_open` specifically -- its own top-level `ast.FunctionDef`, found
    by name, the same way the choke-point pin finds `call_tool`.

    Two tools, never one `action` switch: their identity postures are
    opposite (`spine_open` acts on a spine that does not exist and must never
    touch `SPINE`/`SESSION`; `spine_close` acts on the bound spine and
    nothing else), and folding them into one function BODY would be exactly
    the "a guard written for one hazard covers the other by accident" failure
    `_identity_violation`'s own docstring records as history -- so each gets
    its own top-level implementation (`_spine_open`, `_spine_close`) and this
    function does nothing but route to one of them by name."""
    if name == "spine_open":
        return _spine_open(args)
    if name == "spine_bind":
        return _spine_bind(args)
    if name == "spine_close":
        return _spine_close(args)
    raise KeyError(name)


# --------------------------------------------------------------------------- #
# Tool schemas
# --------------------------------------------------------------------------- #
TOOLS = [
    {
        "name": "spine_status",
        "description": (
            "Read where you are in the spine: the active gate's id, status and "
            "imperative (the instruction you must carry out now), its unmet "
            "conditions, constraints, anchors, and any standing doctrine or trip "
            "advisory. Read-only, no lease required. Call this first and after "
            "every change to see what the engine expects next."
        ),
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "spine_lease",
        "description": (
            "Take, refresh, or give back the working lease on this spine. "
            "'claim' once before any other mutating tool (safe to call again -- "
            "the same session id re-claiming is idempotent); 'heartbeat' only "
            "during a genuine idle gap (mutating calls already refresh it); "
            "'release' as your last action when the spine is done."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["claim", "release", "heartbeat"]},
                "claimed_by": {
                    "type": "string",
                    "description": "claim only: the role driving this spine, e.g. 'implementer'",
                },
                "worktree": {
                    "type": "string",
                    "description": "claim only: worktree path recorded with the lease; defaults to '.'",
                },
                "force": {
                    "type": "boolean",
                    "description": "claim: take over an active lease from another session. release: force-release a lease you do not own. Both require 'reason'.",
                },
                "reason": {
                    "type": "string",
                    "description": "required with force=true",
                },
            },
            "required": ["action"],
            "additionalProperties": False,
        },
    },
    {
        "name": "spine_start",
        "description": (
            "Begin work on one gate: moves it from pending to in-progress. The "
            "engine refuses if the gate's preconditions are unmet or it is not "
            "the next gate in order -- attest the precondition first, then retry."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "the gate id, e.g. 'g1'"}
            },
            "required": ["task_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "spine_advance",
        "description": (
            "Close a gate and move to the next one. The engine re-verifies every "
            "postcondition and REFUSES if any is unmet -- satisfy it first (via "
            "spine_evidence or by making a command-checked condition genuinely "
            "true), then retry. Requires either 'why' (the running understanding "
            "that justifies closing this gate) or mechanical=true (this gate "
            "carried no new understanding); the engine may require 'why' even "
            "with mechanical unset when context pressure is high."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "the gate id to close"},
                "why": {
                    "type": "string",
                    "description": "the understanding that justifies advancing past this gate",
                },
                "mechanical": {
                    "type": "boolean",
                    "description": "true when this gate carried no new understanding; use instead of 'why'",
                },
                "from_child": {
                    "type": "string",
                    "description": "path to a child checklist file whose consolidation attaches as review-result before advancing",
                },
            },
            "required": ["task_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "spine_evidence",
        "description": (
            "Apply evidence to a gate's condition: 'attest' manually confirms a "
            "condition with no automatic check (do NOT attest a command-checked "
            "condition -- satisfy it by making it true, then advance); 'attach' "
            "records an evidence artifact (e.g. a review-result, a "
            "refresh-request) against a gate, satisfying an artifact "
            "postcondition; 'waive' is the human override of a check that would "
            "otherwise block the gate -- only sanctioned when a human has "
            "decided that specific check is non-blocking, and refused unless the "
            "condition declares itself waivable (pass force=true to override "
            "that refusal deliberately, as a last resort)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["attest", "attach", "waive"]},
                "task_id": {"type": "string", "description": "the gate id"},
                "condition_id": {
                    "type": "string",
                    "description": "attest/waive: the condition id shown by spine_status, e.g. 'c2'",
                },
                "which": {
                    "type": "string",
                    "enum": ["preconditions", "postconditions"],
                    "description": "attest/waive: which list the condition is in (attest defaults to preconditions, waive to postconditions -- always pass this explicitly)",
                },
                "note": {"type": "string", "description": "attest: optional evidence note"},
                "evidence_ref": {
                    "type": "string",
                    "description": "attest: an existing evidence id that already satisfies this condition by reference, instead of re-attaching the same artifact",
                },
                "authority": {
                    "type": "string",
                    "description": "waive: who is accepting the risk, e.g. 'human' (required)",
                },
                "reason": {
                    "type": "string",
                    "description": "waive: why the check is accepted as non-blocking",
                },
                "force": {
                    "type": "boolean",
                    "description": "waive: override even without a declared override_policy (high friction, recorded as forced: true)",
                },
                "evidence_type": {
                    "type": "string",
                    "description": "attach: the evidence type, e.g. 'review-result', 'refresh-request'",
                },
                "fields": {
                    "type": "object",
                    "description": "attach: key/value payload fields, e.g. {\"verdict\": \"APPROVE\"}",
                    "additionalProperties": {"type": "string"},
                },
            },
            "required": ["action", "task_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "spine_halt",
        "description": (
            "Change a gate's status without doing its work: 'block' when you "
            "genuinely cannot proceed (bubbles to the parent agent/human); "
            "'resume' a gate you previously blocked; 'skip' to mark a gate "
            "Overtaken By Events, never doing its work; 'reopen' to rework a "
            "complete gate -- resets its conditions and CASCADES every "
            "downstream complete/in-progress gate back to pending (their "
            "evidence is superseded, not deleted), gated behind the engine's "
            "rework cap."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["block", "resume", "skip", "reopen"]},
                "task_id": {"type": "string"},
                "blocker": {"type": "string", "description": "block: what is blocking you (required)"},
                "authority": {
                    "type": "string",
                    "description": "block: who must resolve it; defaults to 'parent agent'",
                },
                "next_action": {"type": "string", "description": "block: suggested next step"},
                "reason": {
                    "type": "string",
                    "description": "resume: why you can now proceed (required). skip/reopen: why (required)",
                },
                "note": {"type": "string", "description": "resume: optional detail"},
            },
            "required": ["action", "task_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "spine_survey_result",
        "description": (
            "Survey-type plans only (reviewer/interrogator checklists, not a "
            "gated spine): record one item's pass/fail result, or consolidate "
            "every recorded result into one verdict."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["record", "consolidate"]},
                "task_id": {"type": "string", "description": "record only: the item id"},
                "result": {"type": "string", "enum": ["pass", "fail"], "description": "record only"},
                "finding": {"type": "string", "description": "record only: what you found"},
                "verdict": {"type": "string", "description": "consolidate only"},
                "summary": {"type": "string", "description": "consolidate only"},
                "override_reason": {
                    "type": "string",
                    "description": "consolidate only: required to force APPROVE while an item is fail",
                },
            },
            "required": ["action"],
            "additionalProperties": False,
        },
    },
    {
        "name": "spine_capture",
        "description": (
            "Add a new item to the plan: 'append' a new sibling leaf on a "
            "survey checklist (the reviewer, the interrogator); 'flag-candidate' "
            "records an out-of-scope discovery for Triage to drain later, from "
            "any gate."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["append", "flag-candidate"]},
                "task_id": {"type": "string", "description": "append: the new item's id"},
                "title": {"type": "string", "description": "append: the new item's title (required)"},
                "imperative": {"type": "string", "description": "append: the new item's imperative (required)"},
                "from": {"type": "string", "description": "flag-candidate: the gate id the discovery came from (required)"},
                "statement": {"type": "string", "description": "flag-candidate: what was found (required)"},
            },
            "required": ["action"],
            "additionalProperties": False,
        },
    },
    {
        "name": "spine_amend",
        "description": (
            "Deliberate, validated re-planning of a GATED checklist under a "
            "named authority: add/drop/rescope pending gates, or retext-check "
            "a pending/in-progress gate's check text. 'delta' is the same "
            "{\"ops\": [...]} object the CLI's --delta file holds -- this tool "
            "writes it to a file beside the bound spine and hands the engine "
            "that path; the engine alone validates the ops, never this door. "
            "All-or-nothing: a refusal leaves the plan unmutated."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "delta": {
                    "type": "object",
                    "description": "the {\"ops\": [...]} delta object (required) -- validated by the engine, not this schema",
                },
                "reason": {"type": "string", "description": "why this re-planning is justified (required)"},
                "authority": {"type": "string", "description": "who ratified the amendment, e.g. 'human' (required)"},
            },
            "required": ["delta", "reason", "authority"],
            "additionalProperties": False,
        },
    },
]

# The lifecycle door (issue #559, C3/g3) -- see the module docstring's "The
# lifecycle door" section. A SEPARATE list, concatenated into TOOLS below,
# because `LIFECYCLE_TOOL_NAMES` is what lets the identity sweep
# (`tests/test_mcp_identity.py`) scope itself to the 9 engine-pass-through
# tools it was written for, without re-deriving that set a second way.
LIFECYCLE_TOOLS = [
    {
        "name": "spine_open",
        "description": (
            "Open Constellation work in one call: creates a worktree, a "
            "branch, a scaffolded work area, and a compiled, origin-stamped "
            "spine for `work_id`, then returns the values (SPINE_FILE, "
            "SPINE_SESSION, SPINE_PARENT, the branch, the worktree) a crew's "
            "own door binds to. Acts on a spine that does not exist yet -- "
            "never the spine THIS door is itself bound to."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "work_id": {
                    "type": "string",
                    "description": "the new work's id, e.g. 'epic-560/some-slug'",
                },
                "spec": {
                    "type": "object",
                    "description": "the gate-plan spec generate_spine compiles into the new spine",
                },
                "base": {
                    "type": "string",
                    "description": "git ref to branch from; defaults to HEAD",
                },
            },
            "required": ["work_id", "spec"],
            "additionalProperties": False,
        },
    },
    {
        "name": "spine_bind",
        "description": (
            "Bind this door to a spine that ALREADY EXISTS, so this process can "
            "drive it with the other tools. Acts on a spine `spine_open` (or the "
            "CLI) already created -- it creates nothing and mints nothing. Call "
            "this when a tool answered 'no spine is bound to this door' and the "
            "work you need to drive is already on disk. The session identity is "
            "NOT an argument: it is derived from the spine's own work id, so "
            "binding a spine yields exactly the identity that spine is driven "
            "under. Confined to one checkout's work-area tree per process -- "
            "refused for a spine outside this door's own checkout's "
            "`.agent-work/`, including a sibling worktree of the same repository, "
            "and refused for a spine in a checkout NESTED inside that "
            "`.agent-work/`. The path is judged after resolution, so a symlink is "
            "not a way around either refusal. "
            "Also refused while this door still holds an active lease on a "
            "different spine (release it first), and while the identity it would "
            "take is live somewhere else. Binding the spine this door is already "
            "bound to is a no-op that succeeds."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "spine_file": {
                    "type": "string",
                    "description": (
                        "path to the existing spine file -- the SPINE_FILE value "
                        "`spine_open` returned. Must resolve inside this door's own "
                        "checkout's `.agent-work/`. Pass an absolute path: this door's "
                        "cwd moves for the length of an engine call, so a relative one "
                        "is resolved against a directory you cannot predict."
                    ),
                },
            },
            "required": ["spine_file"],
            "additionalProperties": False,
        },
    },
    {
        "name": "spine_close",
        "description": (
            "Close the spine THIS door is bound to: moves the work area and "
            "the spine (last) into the archive and commits, once the caller "
            "has already driven the bound spine to a released, terminal "
            "close through spine_advance and spine_lease. Acts on the bound "
            "spine and nothing else -- no arguments, because there is "
            "nothing to redirect."
        ),
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
]
LIFECYCLE_TOOL_NAMES = {t["name"] for t in LIFECYCLE_TOOLS}

TOOLS = TOOLS + LIFECYCLE_TOOLS
TOOL_NAMES = {t["name"] for t in TOOLS}

# The tools reachable with NO usable spine bound -- every other tool refuses
# (issue #603, `_unbound_refusal`). Both names here are ways OUT of that state,
# and they split on whether the work exists yet: `spine_open` acts on a spine
# that does not exist and binds this process to the one it mints; `spine_bind`
# (issue #567) acts on a spine that already does. Exactly two names, and it is a
# SET rather than an `!=`/`in (a, b)` so each exemption is a listed fact a reader
# can find, not a comparison buried in a dispatch chain. `spine_close` is
# deliberately NOT here: it acts on the bound spine, so with nothing bound it has
# nothing to close and must refuse like the rest.
#
# Adding a name here is the load-bearing half of shipping a bind tool: without
# it, `main()`'s uniform gate refuses the call before `call_lifecycle_tool` is
# ever reached, and the result is a bind tool that only works on an already-bound
# door -- the inverse of its purpose.
BINDS_WITHOUT_A_BOUND_SPINE = {"spine_open", "spine_bind"}


def _require(args: dict, *names: str) -> str | None:
    missing = [n for n in names if not args.get(n)]
    if missing:
        return f"missing required argument(s): {', '.join(missing)}"
    return None


def call_tool(name: str, args: dict) -> dict:
    if name == "spine_status":
        return as_result(run_engine("current", mutating=False))

    if name == "spine_lease":
        action = args.get("action")
        if action == "claim":
            rest = ["--claimed-by", args.get("claimed_by", "agent"),
                     "--worktree", args.get("worktree", ".")]
            if args.get("force"):
                rest.append("--force")
                if args.get("reason"):
                    rest += ["--reason", args["reason"]]
            return as_result(run_engine("claim", *rest))
        if action == "release":
            rest = []
            if args.get("force"):
                rest.append("--force")
                if args.get("reason"):
                    rest += ["--reason", args["reason"]]
            return as_result(run_engine("release", *rest))
        if action == "heartbeat":
            return as_result(run_engine("heartbeat"))
        return _tool_error(
            f"spine_lease: unknown action {action!r}",
            tool="spine_lease", rejection_class="unknown-action",
        )

    if name == "spine_start":
        err = _require(args, "task_id")
        if err:
            return _tool_error(
                f"spine_start: {err}",
                tool="spine_start", rejection_class="missing-required-argument",
            )
        return as_result(run_engine("start", args["task_id"]))

    if name == "spine_advance":
        err = _require(args, "task_id")
        if err:
            return _tool_error(
                f"spine_advance: {err}",
                tool="spine_advance", rejection_class="missing-required-argument",
            )
        rest = [args["task_id"]]
        if args.get("from_child"):
            rest += ["--from-child", args["from_child"]]
        if args.get("mechanical"):
            rest.append("--mechanical")
        elif args.get("why"):
            rest += ["--why", args["why"]]
        return as_result(run_engine("advance", *rest))

    if name == "spine_evidence":
        action = args.get("action")
        err = _require(args, "task_id")
        if err:
            return _tool_error(
                f"spine_evidence: {err}",
                tool="spine_evidence", rejection_class="missing-required-argument",
            )
        task_id = args["task_id"]
        if action == "attest":
            err = _require(args, "condition_id")
            if err:
                return _tool_error(
                    f"spine_evidence attest: {err}",
                    tool="spine_evidence", rejection_class="missing-required-argument",
                )
            rest = [task_id, "--cond", args["condition_id"],
                     "--which", args.get("which", "preconditions")]
            if args.get("note"):
                rest += ["--note", args["note"]]
            if args.get("evidence_ref"):
                rest += ["--evidence", args["evidence_ref"]]
            return as_result(run_engine("attest", *rest))
        if action == "waive":
            err = _require(args, "condition_id", "authority")
            if err:
                return _tool_error(
                    f"spine_evidence waive: {err}",
                    tool="spine_evidence", rejection_class="missing-required-argument",
                )
            rest = [task_id, "--cond", args["condition_id"],
                     "--which", args.get("which", "postconditions"),
                     "--authority", args["authority"]]
            if args.get("reason"):
                rest += ["--reason", args["reason"]]
            if args.get("force"):
                rest.append("--force")
            return as_result(run_engine("waive", *rest))
        if action == "attach":
            err = _require(args, "evidence_type")
            if err:
                return _tool_error(
                    f"spine_evidence attach: {err}",
                    tool="spine_evidence", rejection_class="missing-required-argument",
                )
            rest = [task_id, "--type", args["evidence_type"]]
            for key, value in (args.get("fields") or {}).items():
                rest += ["--field", f"{key}={value}"]
            return as_result(run_engine("attach", *rest))
        return _tool_error(
            f"spine_evidence: unknown action {action!r}",
            tool="spine_evidence", rejection_class="unknown-action",
        )

    if name == "spine_halt":
        action = args.get("action")
        err = _require(args, "task_id")
        if err:
            return _tool_error(
                f"spine_halt: {err}",
                tool="spine_halt", rejection_class="missing-required-argument",
            )
        task_id = args["task_id"]
        if action == "block":
            err = _require(args, "blocker")
            if err:
                return _tool_error(
                    f"spine_halt block: {err}",
                    tool="spine_halt", rejection_class="missing-required-argument",
                )
            rest = [task_id, "--blocker", args["blocker"],
                     "--authority", args.get("authority", "parent agent")]
            if args.get("next_action"):
                rest += ["--next", args["next_action"]]
            return as_result(run_engine("block", *rest))
        if action == "resume":
            err = _require(args, "reason")
            if err:
                return _tool_error(
                    f"spine_halt resume: {err}",
                    tool="spine_halt", rejection_class="missing-required-argument",
                )
            rest = [task_id, "--reason", args["reason"]]
            if args.get("note"):
                rest += ["--note", args["note"]]
            return as_result(run_engine("resume", *rest))
        if action == "skip":
            err = _require(args, "reason")
            if err:
                return _tool_error(
                    f"spine_halt skip: {err}",
                    tool="spine_halt", rejection_class="missing-required-argument",
                )
            return as_result(run_engine("skip", task_id, "--reason", args["reason"]))
        if action == "reopen":
            err = _require(args, "reason")
            if err:
                return _tool_error(
                    f"spine_halt reopen: {err}",
                    tool="spine_halt", rejection_class="missing-required-argument",
                )
            return as_result(run_engine("reopen", task_id, "--reason", args["reason"]))
        return _tool_error(
            f"spine_halt: unknown action {action!r}",
            tool="spine_halt", rejection_class="unknown-action",
        )

    if name == "spine_survey_result":
        action = args.get("action")
        if action == "record":
            err = _require(args, "task_id", "result")
            if err:
                return _tool_error(
                    f"spine_survey_result record: {err}",
                    tool="spine_survey_result", rejection_class="missing-required-argument",
                )
            rest = [args["task_id"], "--result", args["result"]]
            if args.get("finding"):
                rest += ["--finding", args["finding"]]
            return as_result(run_engine("record", *rest))
        if action == "consolidate":
            rest = []
            if args.get("verdict"):
                rest += ["--verdict", args["verdict"]]
            if args.get("summary"):
                rest += ["--summary", args["summary"]]
            if args.get("override_reason"):
                rest += ["--override-reason", args["override_reason"]]
            return as_result(run_engine("consolidate", *rest))
        return _tool_error(
            f"spine_survey_result: unknown action {action!r}",
            tool="spine_survey_result", rejection_class="unknown-action",
        )

    if name == "spine_capture":
        action = args.get("action")
        if action == "append":
            err = _require(args, "task_id", "title", "imperative")
            if err:
                return _tool_error(
                    f"spine_capture append: {err}",
                    tool="spine_capture", rejection_class="missing-required-argument",
                )
            rest = [args["task_id"], "--title", args["title"], "--imperative", args["imperative"]]
            return as_result(run_engine("append", *rest))
        if action == "flag-candidate":
            err = _require(args, "from", "statement")
            if err:
                return _tool_error(
                    f"spine_capture flag-candidate: {err}",
                    tool="spine_capture", rejection_class="missing-required-argument",
                )
            rest = ["--from", args["from"], "--statement", args["statement"]]
            return as_result(run_engine("flag-candidate", *rest))
        return _tool_error(
            f"spine_capture: unknown action {action!r}",
            tool="spine_capture", rejection_class="unknown-action",
        )

    if name == "spine_amend":
        err = _require(args, "reason", "authority")
        if err:
            return _tool_error(
                f"spine_amend: {err}",
                tool="spine_amend", rejection_class="missing-required-argument",
            )
        delta = args.get("delta")
        if not isinstance(delta, dict) or not delta:
            return _tool_error(
                "spine_amend: missing required argument(s): delta",
                tool="spine_amend", rejection_class="missing-required-argument",
            )
        try:
            delta_path = _write_amend_delta(delta)
        except OSError as exc:
            return _tool_error(
                f"spine_amend: could not write delta file: {exc}",
                tool="spine_amend", rejection_class="delta-write-failed",
            )
        rest = ["--delta", str(delta_path), "--reason", args["reason"], "--authority", args["authority"]]
        return as_result(run_engine("amend", *rest))

    raise KeyError(name)


# --------------------------------------------------------------------------- #
# JSON-RPC 2.0 over newline-delimited stdio (the MCP stdio transport)
# --------------------------------------------------------------------------- #
def _utf8_stdio() -> None:
    """Pin the protocol encoding to UTF-8 explicitly rather than inheriting
    the platform default. On Windows, Python's stdio falls back to the ANSI
    code page (cp1252), not UTF-8, unless a stream is reconfigured -- the
    same trap scripts/checklist_engine.py's own `_utf8_stdio()` already
    names for the CLI's stdout/stderr (that CLI never reads stdin, so it
    never had to cover this door's own extra surface: `sys.stdin`, read
    every request off, here). The MCP stdio transport IS UTF-8 by spec, so
    this is conformance, not a workaround -- do not "simplify" it back to
    the platform default."""
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass


def main() -> None:
    _utf8_stdio()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            continue
        mid, method, params = msg.get("id"), msg.get("method"), msg.get("params") or {}

        if method == "initialize":
            result = {
                "protocolVersion": params.get("protocolVersion", PROTOCOL_DEFAULT),
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            }
        elif method == "tools/list":
            result = {"tools": TOOLS}
        elif method == "tools/call":
            nm = params.get("name", "")
            call_args = params.get("arguments") or {}
            # Fail closed, for the WHOLE surface at once (issue #603).
            # Deliberately here rather than inside each tool's own branch: this
            # runs before any required-argument check, so an unbound door
            # answers the question the caller actually has ("nothing is bound")
            # instead of a downstream complaint about an argument that would not
            # have helped anyway. `spine_open` is exempt because it is the way
            # OUT of this state -- it mints a spine and binds this process to it.
            unbound = None if nm in BINDS_WITHOUT_A_BOUND_SPINE else _unbound_refusal()
            if nm not in TOOL_NAMES:
                result = _tool_error(
                    f"unknown tool {nm!r}",
                    tool=nm or "(empty)", rejection_class="unknown-tool",
                )
            elif unbound is not None:
                result = _tool_error(unbound, tool=nm, rejection_class="unbound-door")
            elif nm in LIFECYCLE_TOOL_NAMES:
                # Routed here, never inside call_tool -- see the module
                # docstring's "The lifecycle door" section.
                try:
                    result = call_lifecycle_tool(nm, call_args)
                except KeyError as exc:
                    result = _tool_error(f"tool error: missing or unknown {exc}")
            else:
                try:
                    result = call_tool(nm, call_args)
                except KeyError as exc:
                    result = _tool_error(f"tool error: missing or unknown {exc}")
        elif method == "ping":
            result = {}
        elif mid is None:
            continue  # a notification (e.g. notifications/initialized); no reply
        else:
            sys.stdout.write(json.dumps({
                "jsonrpc": "2.0", "id": mid,
                "error": {"code": -32601, "message": f"unknown method {method}"}}) + "\n")
            sys.stdout.flush()
            continue

        if mid is None:
            continue
        sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": mid, "result": result}) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
