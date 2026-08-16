"""Reviewer's OWN door sweep (g3 / issue #603) -- written independently of the
implementer's probe.

Launches the real door as a SUBPROCESS, asks it (tools/list) what tools it
declares, then calls EVERY declared tool with valid required arguments
synthesized from each tool's own inputSchema -- so the tool list is the door's
answer, never a hand-maintained list that can drift (CREW_CONTEXT.md:
"Define a guard by its consumer's behaviour, not by a hand-maintained list").

`spine_open` is called with a DELIBERATELY missing required argument: it is the
one tool exempt from the unbound refusal, and calling it for real would mint a
branch and a worktree. A missing-argument error proves it got past the unbound
gate; an unbound refusal would prove it did not.

Usage:  py reviewer_sweep.py <case>
        case in: unset | empty | space | missing | dir | unreadable
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]

SENTINEL = "REFUSED:"


def synth(schema):
    """A valid-looking value for one required property, from its own type."""
    t = schema.get("type")
    if t == "string":
        enum = schema.get("enum")
        return enum[0] if enum else "x"
    if t == "object":
        return {"k": "v"}
    if t == "array":
        return ["x"]
    if t == "boolean":
        return True
    if t in ("integer", "number"):
        return 1
    return "x"


def make_case(case, tmp):
    """Returns (env_value_or_None, human_label). None means genuinely unset."""
    if case == "unset":
        return None, "(unset -- variable removed)"
    if case == "empty":
        return "", "'' (empty string -- what ${SPINE_FILE:-} expands to)"
    if case == "space":
        return "   ", "'   ' (whitespace only)"
    if case == "missing":
        p = tmp / "no-such-spine.json"
        return str(p), f"{p} (path does not exist)"
    if case == "dir":
        d = tmp / "a-directory"
        d.mkdir()
        return str(d), f"{d} (a directory, not a file)"
    if case == "unreadable":
        p = tmp / "unreadable.json"
        p.write_text('{"type": "gated"}', encoding="utf-8")
        os.chmod(p, 0o000)
        return str(p), f"{p} (chmod 000)"
    raise SystemExit(f"unknown case {case!r}")


def main():
    case = sys.argv[1]
    tmp = Path(tempfile.mkdtemp(prefix="g3rev-"))
    value, label = make_case(case, tmp)

    env = dict(os.environ)
    env["SPINE_ENGINE"] = "scripts/checklist_engine.py"
    env["SPINE_SESSION"] = ""
    env.pop("SPINE_PARENT", None)
    # Keep this sweep's telemetry out of the repo.
    env["SPINE_CALLLOG"] = str(tmp / "calls.jsonl")
    env["SPINE_START_MARKER"] = str(tmp / "started")
    env["SPINE_REJECTION_LOG"] = str(tmp / "rejections.jsonl")
    if value is None:
        env.pop("SPINE_FILE", None)
    else:
        env["SPINE_FILE"] = value

    p = subprocess.Popen(
        [sys.executable, "scripts/mcp_spine_server.py"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, env=env, cwd=str(REPO),
    )

    # Round 1: find out what the door declares.
    listing = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                    "clientInfo": {"name": "reviewer-sweep", "version": "0"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
    ]
    # We cannot reuse one process for two communicate() calls, so build the
    # whole batch at once: list first, then a call per tool discovered from a
    # throwaway BOUND process. Simpler: discover from a bound door, then sweep.
    p.kill(); p.communicate()

    # -- discovery pass, against a BOUND door so tools/list is definitely served
    disc_env = dict(env)
    disc_env["SPINE_FILE"] = str(REPO / ".agent-work/cleanup-a-door/spine.json")
    d = subprocess.run(
        [sys.executable, "scripts/mcp_spine_server.py"],
        input="\n".join(json.dumps(m) for m in listing) + "\n",
        capture_output=True, text=True, env=disc_env, cwd=str(REPO), timeout=60,
    )
    tools = None
    for line in d.stdout.splitlines():
        try:
            m = json.loads(line)
        except ValueError:
            continue
        if m.get("id") == 2:
            tools = m["result"]["tools"]
    if not tools:
        print("FATAL: discovery pass returned no tools")
        print(d.stdout[:2000]); print(d.stderr[:2000])
        raise SystemExit(1)

    # -- sweep pass: one process, every tool called in turn
    msgs = listing[:2]
    order = []
    for i, t in enumerate(tools):
        name = t["name"]
        schema = t.get("inputSchema") or {}
        props = schema.get("properties") or {}
        req = schema.get("required") or []
        if name == "spine_open":
            args = {}  # deliberately incomplete -- see module docstring
        else:
            args = {r: synth(props.get(r, {})) for r in req}
        order.append((name, args))
        msgs.append({"jsonrpc": "2.0", "id": 100 + i, "method": "tools/call",
                     "params": {"name": name, "arguments": args}})

    r = subprocess.run(
        [sys.executable, "scripts/mcp_spine_server.py"],
        input="\n".join(json.dumps(m) for m in msgs) + "\n",
        capture_output=True, text=True, env=env, cwd=str(REPO), timeout=120,
    )

    answers = {}
    for line in r.stdout.splitlines():
        try:
            m = json.loads(line)
        except ValueError:
            continue
        if isinstance(m.get("id"), int) and m["id"] >= 100:
            answers[m["id"] - 100] = m.get("result", m)

    print(f"=== CASE {case}: SPINE_FILE = {label}")
    print(f"=== door declares {len(tools)} tools; called all {len(order)}")
    refused = alive_answers = fabricated = 0
    for i, (name, args) in enumerate(order):
        res = answers.get(i)
        if res is None:
            print(f"  {name:24s} NO ANSWER  <-- server died or never replied")
            continue
        alive_answers += 1
        text = "".join(c.get("text", "") for c in res.get("content", []))
        is_err = res.get("isError")
        kind = "REFUSAL" if text.startswith(SENTINEL) else "other"
        if kind == "REFUSAL":
            refused += 1
        # fabrication check: an UNBOUND refusal must name no path at all
        nothing_named = value is None or not value.strip()
        if kind == "REFUSAL" and nothing_named and "pointed at" in text:
            fabricated += 1
        print(f"  {name:24s} isError={is_err!s:5s} {kind:8s} :: {text[:150]}")
    print(f"--- answered: {alive_answers}/{len(order)}   refusals: {refused}")
    print(f"--- fabricated-path refusals (should be 0 for unset/empty/space): {fabricated}")
    print(f"--- STDERR: {r.stderr.strip()[:600] or '(none)'}")
    print(f"--- SERVER EXIT: {r.returncode}")
    if case == "unreadable":
        os.chmod(tmp / "unreadable.json", 0o600)


main()
