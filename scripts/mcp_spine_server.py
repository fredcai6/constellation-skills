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

Ambient state is bound at server-launch time from the environment, NOT exposed
as tool arguments (so a model cannot point the door at a different spine or
identity mid-conversation):
  SPINE_FILE    -- the --file every engine call needs
  SPINE_ENGINE  -- path to checklist_engine.py (this repo's own copy; dogfooding
                   convention -- see checklist-engine.md "Dogfooding on the
                   skill-source repo")
  SPINE_SESSION -- the --session-id every mutating verb needs once a lease
                   exists; keyed session_id#agentId by the caller's own
                   environment (the committed .mcp.json's ${VAR} expansion
                   is what sets it on a real dispatch; the server just uses
                   whatever string it is handed)

Exactly ONE declared tool property carries a filesystem path:
`spine_advance.from_child`. It does not redirect the door -- the call still
addresses the bound spine -- but the child's `consolidation` is attached to
that spine as a `review-result`, which is the evidence type an artifact
postcondition consumes, so an unconfined path would let any JSON file carrying
a `consolidation` key close a gate. `_identity_violation` therefore CONFINES it
to the bound spine's own directory tree, the containment every real use in this
repo already satisfies. See IDENTITY_TRADE.md §2.

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
The lifecycle door: 2 more tools, dispatched OUTSIDE call_tool
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
`run_engine` (checked, not merely claimed -- see `tests/test_mcp_lifecycle.py`),
deriving the primary checkout it opens work from fresh off `SPINE_FILE`
(ambient, server-launch-time state) rather than the module's own `SPINE`
binding; `spine_close` takes no arguments at all and acts on `SPINE` alone,
because there is no field to redirect.
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

ENGINE = Path(os.environ["SPINE_ENGINE"]).resolve()
SPINE = Path(os.environ["SPINE_FILE"]).resolve()
SESSION = os.environ.get("SPINE_SESSION", "")

sys.path.insert(0, str(ENGINE.parent))
import checklist_engine  # noqa: E402
import spine_lifecycle  # noqa: E402

PROTOCOL_DEFAULT = "2025-06-18"
SERVER_NAME = "spine"
SERVER_VERSION = "0.1.0"

# One JSONL line per engine call this server made, so a tracer/reviewer can
# count real engine dispatches without scraping a model transcript. Never read
# back by the server itself -- corroborating detail only, per MISSION_FRAME's
# claim table (a server-log numerator would structurally undercount the client
# rejections a schema-typed tool surface is supposed to prevent).
CALLLOG = Path(os.environ.get("SPINE_CALLLOG", str(SPINE.parent / "mcp_calls.jsonl")))

# A start-marker file: written on first successful engine call, so an external
# probe (the delivery-path measurement in MISSION_FRAME) can tell "config was
# valid and the server actually ran" from "config was merely accepted".
START_MARKER = Path(os.environ.get("SPINE_START_MARKER", str(SPINE.parent / "mcp_server_started")))

# One JSONL line per rejection the DOOR ITSELF issues -- an unknown tool name, an
# unknown multiplexed `action`, or a missing required argument (issue #541). Every
# one of those returns `_tool_error(...)` BEFORE `run_engine()` is ever called (see
# the module docstring's "Zero dependencies" section and `call_tool()` below), so
# `_log()` and CALLLOG never see it and the engine's own refusal counter never
# moves -- this file is that path's only durable trace. Beside the spine, like
# CALLLOG, for the same reason: one location a run's own evidence-gathering has to
# remember, not two.
REJECTIONLOG = Path(os.environ.get("SPINE_REJECTION_LOG", str(SPINE.parent / "mcp_rejections.jsonl")))


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
    connection."""
    line = json.dumps(rec, ensure_ascii=False)
    try:
        with CALLLOG.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError as exc:
        _report_dropped_telemetry(CALLLOG, exc, line)
    try:
        if not START_MARKER.exists():
            START_MARKER.write_text(f"started for {SPINE}\n", encoding="utf-8")
    except OSError as exc:
        _report_dropped_telemetry(START_MARKER, exc, f"start marker for {SPINE}")


def _resolve_confined(
    value: str, *, join_relative_to: Path | None, bound_dir: Path = SPINE.parent,
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
    differently-shaped check."""
    p = Path(value)
    if not p.is_absolute() and join_relative_to is not None:
        p = join_relative_to / value
    try:
        escapes = not p.resolve().is_relative_to(bound_dir.resolve())
    except (OSError, ValueError, RuntimeError):
        escapes = True  # a path that cannot be resolved is not proof it is inside
    return p, escapes


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
    mid-check."""
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
    """Append ONE record for a door-own rejection to REJECTIONLOG -- never raises.

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
    try:
        with REJECTIONLOG.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write(line + "\n")
    except OSError as exc:
        sys.stderr.write(
            f"REJECTION CAPTURE FAILED: could not write to {REJECTIONLOG} "
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
    """The PRIMARY checkout -- read fresh off `SPINE_FILE` (ambient,
    server-launch-time state), never off the module-level `SPINE` global, so
    `_spine_open`'s own source never contains the identifier `SPINE` (checked
    by `tests/test_mcp_lifecycle.py`). This is `open_work`'s own `root`:
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
    spine_dir = Path(os.environ["SPINE_FILE"]).resolve().parent
    common = Path(_git_rev_parse("--git-common-dir", cwd=spine_dir))
    if not common.is_absolute():
        common = spine_dir / common
    return common.resolve().parent


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
    `_spine_close` acts on the bound spine by design."""
    return Path(_git_rev_parse("--show-toplevel", cwd=SPINE.parent))


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
    repo root comes from `_primary_checkout_for_lifecycle` (ambient
    `SPINE_FILE`, re-read fresh), and `parent` comes from `SPINE_PARENT` (the
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
    return _lifecycle_result(opened)


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
            if nm not in TOOL_NAMES:
                result = _tool_error(
                    f"unknown tool {nm!r}",
                    tool=nm or "(empty)", rejection_class="unknown-tool",
                )
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
