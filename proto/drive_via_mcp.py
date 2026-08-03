#!/usr/bin/env python3
"""Drive the toy spine to done through the MCP server, speaking raw JSON-RPC.

This is the server's own correctness check: no model in the loop. If this
reaches DONE, the server is a working MCP endpoint and any later failure is in
the harness/registration layer, not the server.

Usage: python drive_via_mcp.py <arm-dir>
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

arm = Path(sys.argv[1]).resolve()
proto = Path(__file__).resolve().parent
root = proto.parent

env = dict(os.environ)
env["SPINE_FILE"] = str(arm / "spine.json")
env["SPINE_ENGINE"] = str(root / "scripts" / "checklist_engine.py")
env["SPINE_SESSION"] = "selftest"

srv = subprocess.Popen(
    [sys.executable, str(proto / "mcp_spine_server.py")],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, env=env, bufsize=1,
)

_id = 0


def rpc(method: str, params: dict | None = None) -> dict:
    global _id
    _id += 1
    srv.stdin.write(json.dumps({"jsonrpc": "2.0", "id": _id,
                                "method": method, "params": params or {}}) + "\n")
    srv.stdin.flush()
    return json.loads(srv.stdout.readline())


def call(name: str, **args) -> str:
    r = rpc("tools/call", {"name": name, "arguments": args})
    res = r["result"]
    text = res["content"][0]["text"]
    print(f"--- {name}({args}) isError={res.get('isError')}\n{text}\n")
    return text


init = rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                          "clientInfo": {"name": "selftest", "version": "0"}})
print("INITIALIZE:", json.dumps(init["result"]["serverInfo"]))
tools = rpc("tools/list")["result"]["tools"]
print("TOOLS:", [t["name"] for t in tools])
print("TOOL SCHEMA BYTES:", len(json.dumps(tools)))

ws = arm / "workspace"
call("spine_status")
call("spine_lease", action="claim", claimed_by="agent")
call("spine_start", task_id="g1")
(ws / "notes.txt").write_text("building a toy widget\n", encoding="utf-8")
call("spine_attest", task_id="g1", condition_id="c2")
call("spine_advance", task_id="g1", why="work area is set up")
call("spine_start", task_id="g2")
(ws / "widget.txt").write_text("hello widget\n", encoding="utf-8")
call("spine_advance", task_id="g2", why="widget built with the required content")
call("spine_start", task_id="g3")
call("spine_attest", task_id="g3", condition_id="c1")
call("spine_advance", task_id="g3", why="read widget.txt back, matches g2")
call("spine_start", task_id="g4")
(ws / "SUMMARY.md").write_text("# summary\nBuilt a toy widget and verified it.\n", encoding="utf-8")
call("spine_attest", task_id="g4", condition_id="c2")
call("spine_advance", task_id="g4", why="run summarized")
final = call("spine_status")
call("spine_lease", action="release")

srv.stdin.close()
srv.wait(timeout=10)
print("SELFTEST:", "PASS" if "DONE: no open items." in final else "FAIL")
sys.exit(0 if "DONE: no open items." in final else 1)
