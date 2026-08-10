#!/usr/bin/env python3
"""Score ONE measurement arm's record for gate g4 (DC5), issue #424.

THE COUNTING UNIT IS ONE INVOCATION ATTEMPT BY THE DRIVING AGENT, read from the
driving agent's OWN record (`--output-format stream-json`), not from the
server's log. That choice is the whole point of this instrument: a malformed
call rejected by client-side schema validation never reaches the server, so a
server-side numerator structurally suppresses exactly the fumbles the typed door
is being credited with avoiding -- a measure that cannot lose. The server's
`mcp_calls.jsonl` is corroborating detail only.

ONE scorer, applied identically to both arms. The only arm-dependent thing is
how an engine invocation attempt is RECOGNISED, which cannot be arm-independent:
the CLI arm invokes the engine as a shell command, the MCP arm as a typed tool
call. Every downstream classification is shared code.

THE BATCHING CORRECTION (found mid-measurement, applied before any arm was
scored for the record, and stated here because it moves the number in the
direction that FLATTERS the door). A first pass counted one Bash tool_use as one
attempt. That is not unit parity: the CLI arm freely batches several engine
invocations into a single compound Bash command, while the MCP arm structurally
cannot -- one typed tool call carries exactly one verb. Counting tool calls
would have credited the CLI arm with 10 "attempts" for 16 actual invocations.
The unit this gate specifies is one INVOCATION ATTEMPT, so the CLI arm's count
is the number of `checklist_engine.py` invocations inside its commands, however
they were packaged. Both numbers are reported -- `invocation_attempts` and
`tool_calls_carrying_them` -- because the packaging asymmetry is a finding in
its own right, not a nuisance to normalise away.

Fumble classes counted (only those a typed interface can absorb -- engine bug
fixes are held constant across arms, so engine-state refusals are NOT fumbles):

  shape_error   an invocation rejected on its own SHAPE: unparseable arguments,
                unknown/missing verb, flag in the wrong position, missing
                required flag, or a client-side schema rejection. This is the
                class a typed interface absorbs by construction.
  usage_read    an attempt whose purpose is to learn the interface: --help, or
                reading/grepping the engine source or schema docs.
  far_side      a NON-engine tool call made to recover from a failed attempt --
                inspecting the spine file, listing the directory, re-reading
                state after an error. Counted so that "the agent stopped
                fumbling" stays distinguishable from "the fumbling moved
                somewhere we stopped looking".

Usage: python3 score_arm.py <arm-dir> [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ENGINE_HINT = "checklist_engine.py"
MCP_PREFIX = "mcp__spine__"

# Signatures of a SHAPE error, as emitted by argparse / the harness / the
# engine's own argv layer. Deliberately excludes the engine's STATE refusals
# ("preconditions unmet", "not the active gate", "checklist is owned by") --
# those are the engine doing its job, identical through either interface, and
# held constant across arms.
SHAPE_PATTERNS = [
    r"error: the following arguments are required",
    r"error: argument",
    r"error: unrecognized arguments",
    r"invalid choice",
    r"unexpected keyword argument",
    r"missing required",
    r"is not a valid",
    r"required property",
    r"does not match the expected schema",
    r"No such file or directory",
    r"command not found",
    r"SyntaxError",
    r"TypeError",
]
SHAPE_RE = re.compile("|".join(SHAPE_PATTERNS), re.IGNORECASE)

# A bare `usage:` block with NO error line is itself a shape rejection (argparse
# dumps usage when the verb is missing). But when an error line IS present, the
# usage block is that same failure's second half, not a second failure -- which is
# why `usage:` is no longer in SHAPE_PATTERNS. Found by this gate's own scorer
# controls, which scored one argparse rejection as two. It over-counted CLI shape
# errors, i.e. it FLATTERED the door.
BARE_USAGE_RE = re.compile(r"^usage: checklist_engine", re.MULTILINE)

# Engine STATE refusals: not fumbles. Listed explicitly so the exclusion is
# auditable rather than implicit in the absence of a pattern.
STATE_PATTERNS = [
    r"preconditions unmet",
    r"postconditions unmet",
    r"is not the active gate",
    r"checklist is owned by",
    r"requires a running understanding",
    r"can only resume a blocked gate",
    r"advancing a non-exempt gate",
    # "cannot attest an engine-checked condition" is the engine enforcing its
    # own evidence semantics. It is NOT absorbable by typing: the MCP door's
    # spine_evidence tool earns the identical refusal, because the rule lives in
    # the engine, not in the argument shape. Excluding it moves the CLI arm's
    # fumble count DOWN, i.e. against the door.
    r"is engine-checked; cannot attest",
]
STATE_RE = re.compile("|".join(STATE_PATTERNS), re.IGNORECASE)

USAGE_RE = re.compile(r"--help|\bhelp\b|CHECKLIST_SCHEMA|checklist-engine\.md", re.IGNORECASE)

INSPECT_TOOLS = {"Read", "Grep", "Glob"}


def load(path: Path):
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue


def walk(record_path: Path):
    """Yield (tool_use_id, name, input) and {tool_use_id: (is_error, text)}."""
    uses, results = [], {}
    for ev in load(record_path):
        t = ev.get("type")
        if t == "assistant":
            for c in ev.get("message", {}).get("content", []) or []:
                if isinstance(c, dict) and c.get("type") == "tool_use":
                    uses.append((c.get("id"), c.get("name", ""), c.get("input") or {}))
        elif t == "user":
            for c in ev.get("message", {}).get("content", []) or []:
                if isinstance(c, dict) and c.get("type") == "tool_result":
                    body = c.get("content")
                    if isinstance(body, list):
                        body = " ".join(
                            str(b.get("text", "")) for b in body if isinstance(b, dict))
                    results[c.get("tool_use_id")] = (bool(c.get("is_error")), str(body or ""))
    return uses, results


# Every engine invocation prints exactly one of these to its captured output: a
# `RAIL:` line on a normal run, or a `usage:` block when the invocation asked for
# help. Counting them recovers the RUNTIME invocation count from the result,
# which static command text cannot give for a loop.
RUNTIME_MARK_RE = re.compile(r"^RAIL:|^usage: checklist_engine", re.MULTILINE)


def engine_invocations(name: str, inp: dict, output: str = "") -> int:
    """How many ENGINE INVOCATION ATTEMPTS this one tool_use carries.

    The ONE arm-dependent step. MCP: a typed tool call is exactly one verb, so
    one. CLI: however many times the command actually RAN the engine.

    THE LOOP CORRECTION (found by the g4 reviewer, which BLOCKED on it; it moves
    the number TOWARD the door and is disclosed as such). Counting occurrences of
    `checklist_engine.py` in the command TEXT undercounts a shell loop:

        for cmd in claim start attest advance record release; do
          python3 scripts/checklist_engine.py $cmd --help; done

    is one static occurrence and six real invocations. Static text is therefore a
    FLOOR, not the count. The count is the larger of the static occurrences and
    the number of engine-output marks in the result, so a loop scores its runtime
    invocations and a plain compound command still scores its own."""
    if name.startswith(MCP_PREFIX):
        return 1
    if name != "Bash":
        return 0
    static = str(inp.get("command", "")).count(ENGINE_HINT)
    if not static:
        return 0
    return max(static, len(RUNTIME_MARK_RE.findall(output)))


def score(arm_dir: Path) -> dict:
    uses, results = walk(arm_dir / "record.jsonl")

    attempts = shape_errors = usage_reads = far_side = 0
    other_errors = state_refusals = 0
    carrying_calls = 0
    detail = []
    prev_failed = False

    for uid, name, inp in uses:
        is_err, text = results.get(uid, (False, ""))
        inp_text = json.dumps(inp)
        blob = f"{inp_text}\n{text}"
        n = engine_invocations(name, inp, text)

        if n:
            attempts += n
            carrying_calls += 1
            # Counted as OCCURRENCES, not once per tool call, so a batched CLI
            # command carrying three fumbles scores three -- the same as three
            # separate MCP calls carrying one each.
            # Help reads are counted at RUNTIME too, for the same loop reason: a
            # loop of six `--help` calls is six reads, not one.
            u = len(re.findall(r"--help|\bhelp\b", inp_text, re.IGNORECASE))
            if u:
                u = max(u, len(re.findall(r"^usage: checklist_engine", text,
                                          re.MULTILINE)))
            s = len(SHAPE_RE.findall(text))
            if not s:
                s = len(BARE_USAGE_RE.findall(text)) if not u else 0
            if not s and is_err:
                s = 1
            s = min(s, n)  # never more shape errors than there were invocations
            # A deliberate `--help` PRINTS a usage block -- often several, one
            # per subcommand -- so its own output matches the shape-error
            # signature many times over. Help output is help text, never an
            # error, so an invocation that asked for help scores ZERO shape
            # errors. Without this the CLI arm is charged for reading the manual
            # as though it had crashed. The correction moves the CLI arm's error
            # count DOWN, i.e. AGAINST the door.
            if u:
                s = 0
            st = len(STATE_RE.findall(text))
            usage_reads += u
            shape_errors += s
            state_refusals += st
            o = 0
            if not s and not st and ("REFUSED" in text or "Traceback" in text):
                o = 1
                other_errors += 1
            kind = ("usage_read" if u else "shape_error" if s else
                    "state_refusal" if st else "other_error" if o else "ok")
            detail.append({"tool": name, "invocations": n, "kind": kind,
                           "usage": u, "shape": s, "state": st})
            prev_failed = bool(s or o)
        else:
            # A Bash call that does NOT invoke the engine is an inspection too
            # (`cat spine.json`, `ls`). Without this the far-side detector has a
            # blind spot on exactly the arm most likely to recover that way --
            # the CLI arm -- so its zero would have been partly structural.
            # Found by the g4 reviewer; it moves the count TOWARD the door.
            inspecting = name in INSPECT_TOOLS or name == "Bash"
            if inspecting and prev_failed:
                far_side += 1
                detail.append({"tool": name, "kind": "far_side_recovery"})
            elif inspecting and USAGE_RE.search(inp_text):
                usage_reads += 1
                detail.append({"tool": name, "kind": "usage_read"})
            prev_failed = False

    reached_done = any("DONE: no open items" in t for _, t in results.values())

    return {
        "arm_dir": str(arm_dir),
        "invocation_attempts": attempts,
        "tool_calls_carrying_them": carrying_calls,
        "shape_errors": shape_errors,
        "usage_reads": usage_reads,
        "far_side_recoveries": far_side,
        "state_refusals_excluded": state_refusals,
        "other_errors": other_errors,
        "absorbable_fumbles": shape_errors + usage_reads + far_side,
        "reached_done": reached_done,
        "total_tool_calls": len(uses),
        "detail": detail,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("arm_dir")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    result = score(Path(args.arm_dir).resolve())
    if args.json:
        json.dump(result, sys.stdout, indent=2)
        print()
    else:
        for k, v in result.items():
            if k != "detail":
                print(f"{k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
