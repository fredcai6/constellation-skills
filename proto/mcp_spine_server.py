#!/usr/bin/env python3
"""Throwaway MCP front door for the checklist engine (prototype exc-9).

Zero dependencies: newline-delimited JSON-RPC 2.0 over stdio, which is what the
MCP stdio transport is. No SDK install, so nothing leaks outside the worktree.

It WRAPS the engine -- it does not reimplement it. Every tool builds an argv and
calls `checklist_engine.main(argv)`, capturing stdout/stderr and the exit code.
That means the rails, the refusal composition, the journal sidecar, the lease
enforcement and the recovery hints all come through unchanged.

Ambient state bound at server-config time (env), NOT exposed as tool args:
  SPINE_FILE   -- the --file every engine call needs
  SPINE_ENGINE -- path to checklist_engine.py
  SPINE_SESSION-- the --session-id every mutating verb needs once a lease exists
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
from pathlib import Path

ENGINE = Path(os.environ["SPINE_ENGINE"]).resolve()
SPINE = Path(os.environ["SPINE_FILE"]).resolve()
SESSION = os.environ.get("SPINE_SESSION", "mcp-arm")

sys.path.insert(0, str(ENGINE.parent))
import checklist_engine  # noqa: E402

PROTOCOL_DEFAULT = "2025-06-18"

# Every engine call is logged here so the tracer can count calls without parsing
# the agent transcript for engine traffic.
CALLLOG = Path(os.environ.get("SPINE_CALLLOG", str(SPINE.parent / "mcp_calls.jsonl")))


def _log(rec: dict) -> None:
    with CALLLOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def run_engine(verb: str, *rest: str, mutating: bool = True) -> dict:
    """Call the real engine main() with a constructed argv."""
    argv = ["--file", str(SPINE), verb, *rest]
    if mutating:
        argv += ["--session-id", SESSION]
    out, err = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = checklist_engine.main(argv)
    except SystemExit as exc:  # argparse rejected the argv
        code = int(exc.code or 0)
    except Exception as exc:  # noqa: BLE001 - a prototype surfaces everything
        code = 1
        err.write(f"{type(exc).__name__}: {exc}")
    rec = {"verb": verb, "argv": argv, "code": code,
           "stdout": out.getvalue(), "stderr": err.getvalue()}
    _log(rec)
    return rec


def as_result(rec: dict) -> dict:
    """Engine output -> MCP tool result. A refusal comes back as isError so the
    model sees a failed tool call, not prose it has to parse."""
    text = (rec["stdout"] + rec["stderr"]).strip() or "(no output)"
    return {"content": [{"type": "text", "text": text}], "isError": rec["code"] != 0}


# --------------------------------------------------------------------------- #
# The tool surface: 7 tools grouping the engine's 18 verbs.
# --------------------------------------------------------------------------- #
TOOLS = [
    {
        "name": "spine_status",
        "description": (
            "Read where you are in the spine: the current gate, its imperative "
            "(the instruction you must carry out now), its unmet conditions, and "
            "any standing doctrine. Read-only. Call this first and after every "
            "change to see what the engine expects next."
        ),
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "spine_lease",
        "description": (
            "Take or give back the working lease on this spine. Claim it once "
            "before any other tool that changes state (safe to call again); "
            "release it as your last action when the spine is done."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["claim", "release"]},
                "claimed_by": {
                    "type": "string",
                    "description": "claim only: the role driving this spine, e.g. 'agent'",
                },
            },
            "required": ["action"],
            "additionalProperties": False,
        },
    },
    {
        "name": "spine_start",
        "description": (
            "Begin work on one gate. Moves it from pending to in-progress. The "
            "engine refuses if the gate's preconditions are not met or it is not "
            "the next gate in order."
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
        "name": "spine_attest",
        "description": (
            "Assert that one named condition on a gate is satisfied. Use this for "
            "conditions the engine cannot check for itself (the ones with no "
            "automatic check). Conditions that ARE machine-checked are verified by "
            "the engine when you advance -- do not attest those, just make them true."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "the gate id, e.g. 'g2'"},
                "condition_id": {
                    "type": "string",
                    "description": "the condition id shown by spine_status, e.g. 'c2'",
                },
                "which": {
                    "type": "string",
                    "enum": ["preconditions", "postconditions"],
                    "description": "which list the condition is in; defaults to postconditions",
                },
                "note": {"type": "string", "description": "optional evidence note"},
            },
            "required": ["task_id", "condition_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "spine_advance",
        "description": (
            "Close a gate and move to the next one. The engine re-verifies every "
            "postcondition and REFUSES if any is unmet, so make them true first. "
            "You must supply either 'why' (your running understanding that "
            "justifies closing this gate) or mechanical=true (this gate carried no "
            "new understanding)."
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
            },
            "required": ["task_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "spine_halt",
        "description": (
            "Mark a gate blocked when you genuinely cannot proceed, or resume a "
            "gate you previously blocked."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["block", "resume"]},
                "task_id": {"type": "string"},
                "reason": {
                    "type": "string",
                    "description": "block: what is blocking you. resume: why you can now proceed.",
                },
            },
            "required": ["action", "task_id", "reason"],
            "additionalProperties": False,
        },
    },
    {
        "name": "spine_survey_result",
        "description": (
            "Survey spines only (not gated spines): record one check's pass/fail "
            "result, or consolidate all recorded results into one verdict."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["record", "consolidate"]},
                "task_id": {"type": "string", "description": "record only: the check id"},
                "result": {"type": "string", "enum": ["pass", "fail"], "description": "record only"},
                "finding": {"type": "string", "description": "record only"},
                "verdict": {"type": "string", "description": "consolidate only"},
                "summary": {"type": "string", "description": "consolidate only"},
            },
            "required": ["action"],
            "additionalProperties": False,
        },
    },
]


def call_tool(name: str, args: dict) -> dict:
    if name == "spine_status":
        return as_result(run_engine("current", mutating=False))
    if name == "spine_lease":
        if args["action"] == "release":
            return as_result(run_engine("release"))
        return as_result(run_engine("claim", "--claimed-by", args.get("claimed_by", "agent"),
                                    "--worktree", "."))
    if name == "spine_start":
        return as_result(run_engine("start", args["task_id"]))
    if name == "spine_attest":
        rest = [args["task_id"], "--cond", args["condition_id"],
                "--which", args.get("which", "postconditions")]
        if args.get("note"):
            rest += ["--note", args["note"]]
        return as_result(run_engine("attest", *rest))
    if name == "spine_advance":
        rest = [args["task_id"]]
        if args.get("mechanical"):
            rest.append("--mechanical")
        elif args.get("why"):
            rest += ["--why", args["why"]]
        return as_result(run_engine("advance", *rest))
    if name == "spine_halt":
        if args["action"] == "block":
            return as_result(run_engine("block", args["task_id"], "--blocker", args["reason"]))
        return as_result(run_engine("resume", args["task_id"], "--reason", args["reason"]))
    if name == "spine_survey_result":
        if args["action"] == "record":
            rest = [args["task_id"], "--result", args["result"]]
            if args.get("finding"):
                rest += ["--finding", args["finding"]]
            return as_result(run_engine("record", *rest))
        rest = []
        if args.get("verdict"):
            rest += ["--verdict", args["verdict"]]
        if args.get("summary"):
            rest += ["--summary", args["summary"]]
        return as_result(run_engine("consolidate", *rest))
    raise KeyError(name)


def main() -> None:
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
                "serverInfo": {"name": "spine", "version": "0.0.1"},
            }
        elif method == "tools/list":
            result = {"tools": TOOLS}
        elif method == "tools/call":
            nm = params.get("name", "")
            try:
                result = call_tool(nm, params.get("arguments") or {})
            except KeyError as exc:
                # A required arg the schema should have caught, or an unknown tool.
                _log({"verb": f"TOOLERR:{nm}", "argv": [], "code": 1,
                      "stdout": "", "stderr": f"missing/unknown: {exc}"})
                result = {"content": [{"type": "text",
                                       "text": f"tool error: missing or unknown {exc}"}],
                          "isError": True}
        elif method == "ping":
            result = {}
        elif mid is None:
            continue  # a notification we do not handle
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
