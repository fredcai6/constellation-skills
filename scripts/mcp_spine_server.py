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

--------------------------------------------------------------------------- #
Tool surface: 7 tools grouping the engine's 18 verbs
--------------------------------------------------------------------------- #

The engine exposes 18 verbs: current, claim, heartbeat, release, start,
advance, record, consolidate, skip, block, resume, reopen, append, amend,
attest, waive, attach, flag-candidate. A door with one tool per verb would be
18 tools for a "roughly seven" budget (decision:mcp-is-the-vehicle -- MCP is
the current vehicle, not the destination; do not gold-plate the grouping).

Grouping decision, and why: driving a *real* role spine (this very issue's own
commander run) needed `attest`, `attach` and `waive` -- a door missing `attach`
cannot satisfy a `user-decision` checkpoint, and a door missing `waive` cannot
close a gate whose check the principal accepted as non-blocking. Both are
therefore covered, folded into `spine_evidence` alongside `attest` (all three
are "apply evidence to a condition/gate" actions with different argument
shapes, not different concerns). `skip`, `amend`, `append`, `reopen` and
`flag-candidate` are genuinely rarer -- deliberate re-planning, escalation and
out-of-scope capture, not the drive loop's everyday path -- so they stay
CLI-only rather than inflating the tool count to be safe.

  1. spine_status        -- current                          (read-only)
  2. spine_lease         -- claim | release | heartbeat
  3. spine_start         -- start
  4. spine_advance       -- advance
  5. spine_evidence      -- attest | attach | waive
  6. spine_halt          -- block | resume
  7. spine_survey_result -- record | consolidate              (survey plans only)

13 of 18 verbs covered. Verb coverage is a grouping decision, not a cap: this
budget must be revisited if a later gate proves one of the 5 CLI-only verbs is
load-bearing on the drive loop the way `attach`/`waive` turned out to be here.

--------------------------------------------------------------------------- #
CLI-fallback table: every verb NOT covered by a tool
--------------------------------------------------------------------------- #

The CLI door stays -- F is additive, not a replacement. Every uncovered verb
keeps this documented fallback (run from the repo/worktree root):

  skip <id> --reason "..." [--session-id <id>]
      Mark a gate Overtaken By Events without doing its work. Uncovered
      because it is a deliberate re-scoping decision a human/commander makes
      about the PLAN, not a step the agent driving the plan reaches for while
      working it -- rare enough that a tool slot is not worth it.

  reopen <id> --reason "..." [--session-id <id>]
      Rework: cascades every downstream complete/in-progress gate back to
      pending and marks their evidence superseded. Uncovered because it is a
      high-blast-radius escalation (it can undo several gates' worth of
      state), and the engine already gates it behind the rework cap and a
      human-legible cascade -- a tool call that silently resets multiple
      gates is a worse shape than making the agent go to the CLI for it.

  append <id> --title "..." --imperative "..." [--session-id <id>]
      Survey-only: add a new sibling leaf. Uncovered because it only applies
      to `survey`-type plans (the reviewer, the interrogator), which are a
      minority of what this door drives, and it is inherently a re-planning
      move like `amend`/`skip`.

  amend --delta <file.json> --reason "..." --authority <who> [--session-id <id>]
      Validated, all-or-nothing plan re-shape (add/drop/rescope pending gates
      on a gated plan; retext-check on a survey). Uncovered because its input
      is a delta FILE, not a few scalar arguments -- forcing that through a
      tool's JSON args would mean re-deriving the delta schema at the MCP
      boundary, which is exactly the kind of second rendering path this door
      must not grow. Also a deliberate re-plan, not a drive-loop step.

  flag-candidate --from <id> --statement "..." [--session-id <id>]
      Record an out-of-scope discovery for Triage to drain later. Uncovered
      because it is infrequent (once-per-run at most, typically at closeout)
      and a plain CLI call costs nothing extra at that point in a run.

Every fallback above takes `--session-id <id>` once a lease is active, matching
the CLI's own rule (see checklist-engine.md "Session lease").
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ENGINE = Path(os.environ["SPINE_ENGINE"]).resolve()
SPINE = Path(os.environ["SPINE_FILE"]).resolve()
SESSION = os.environ.get("SPINE_SESSION", "")

sys.path.insert(0, str(ENGINE.parent))
import checklist_engine  # noqa: E402

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


def _log(rec: dict) -> None:
    with CALLLOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    if not START_MARKER.exists():
        START_MARKER.write_text(f"started for {SPINE}\n", encoding="utf-8")


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
    * Scoped to `ns.file` and `ns.session_id`, never "no repeated flags".
      `--field` is `action="append"` BY DESIGN and `spine_evidence attach` with
      two fields is legitimate; a repeated-flag rule would break it.
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
    return None


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
    server process down with it."""
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
            "Mark a gate blocked when you genuinely cannot proceed (bubbles to "
            "the parent agent/human), or resume a gate you previously blocked."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["block", "resume"]},
                "task_id": {"type": "string"},
                "blocker": {"type": "string", "description": "block: what is blocking you (required)"},
                "authority": {
                    "type": "string",
                    "description": "block: who must resolve it; defaults to 'parent agent'",
                },
                "next_action": {"type": "string", "description": "block: suggested next step"},
                "reason": {"type": "string", "description": "resume: why you can now proceed (required)"},
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
]

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
