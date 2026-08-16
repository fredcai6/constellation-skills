"""Criterion 10: unset SPINE_ENGINE must not kill the door at import.

Two cases, because "does not kill it" is only half the claim -- the other half is
that the sibling fallback actually WORKS, i.e. the door still reaches a real
engine with no SPINE_ENGINE at all.

Run from the repo root with a cwd DELIBERATELY not the repo, so a relative
`scripts/checklist_engine.py` could not accidentally resolve.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]


def run(label, *, spine, engine, cwd):
    env = dict(os.environ)
    env["SPINE_SESSION"] = ""
    env.pop("SPINE_PARENT", None)
    tmp = Path(tempfile.mkdtemp(prefix="g3eng-"))
    env["SPINE_CALLLOG"] = str(tmp / "calls.jsonl")
    env["SPINE_START_MARKER"] = str(tmp / "started")
    env["SPINE_REJECTION_LOG"] = str(tmp / "rej.jsonl")
    if spine is None:
        env.pop("SPINE_FILE", None)
    else:
        env["SPINE_FILE"] = spine
    if engine is None:
        env.pop("SPINE_ENGINE", None)
    else:
        env["SPINE_ENGINE"] = engine

    msgs = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                    "clientInfo": {"name": "rev", "version": "0"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
         "params": {"name": "spine_status", "arguments": {}}},
    ]
    r = subprocess.run(
        [sys.executable, str(REPO / "scripts/mcp_spine_server.py")],
        input="\n".join(json.dumps(m) for m in msgs) + "\n",
        capture_output=True, text=True, env=env, cwd=cwd, timeout=90,
    )
    text = "(no answer)"
    for line in r.stdout.splitlines():
        try:
            m = json.loads(line)
        except ValueError:
            continue
        if m.get("id") == 2:
            res = m.get("result", {})
            text = "".join(c.get("text", "") for c in res.get("content", []))
    print(f"--- {label}")
    print(f"    SPINE_FILE={spine!r}  SPINE_ENGINE={engine!r}  cwd={cwd}")
    print(f"    ANSWER: {text[:220]!r}")
    print(f"    STDERR: {(r.stderr.strip()[:300] or '(none)')!r}")
    print(f"    EXIT {r.returncode}")
    print()


outside = tempfile.mkdtemp(prefix="g3cwd-")
run("A: SPINE_ENGINE unset + SPINE_FILE unset -> must REFUSE, not die",
    spine=None, engine=None, cwd=outside)
run("B: SPINE_ENGINE unset + a REAL spine -> sibling fallback must reach the engine",
    spine=str(REPO / ".agent-work/cleanup-a-door/g3-review/review.json"),
    engine=None, cwd=outside)
run("C: SPINE_ENGINE set to a BOGUS path + a real spine (implementer's stated gap #2)",
    spine=str(REPO / ".agent-work/cleanup-a-door/g3-review/review.json"),
    engine="/tmp/definitely-not-an-engine.py", cwd=outside)
run("D: SPINE_ENGINE RELATIVE (what .mcp.json ships) launched from a foreign cwd (stated gap #1)",
    spine=str(REPO / ".agent-work/cleanup-a-door/g3-review/review.json"),
    engine="scripts/checklist_engine.py", cwd=outside)
