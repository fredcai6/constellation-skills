#!/usr/bin/env python3
"""Run one tracer arm: a cold headless `claude -p` agent driving the toy spine.

Usage: python run_arm.py <mcp|cli> <arm-name>

Both arms get an IDENTICAL task core and an IDENTICAL built-in toolset. They
differ only in the door they reach the engine through. All setting sources are
disabled so the repo's Bash PostToolUse spine-rail hook -- which would push rail
text to the CLI arm only -- cannot skew the comparison.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROTO = ROOT / "proto"
ENGINE = ROOT / "scripts" / "checklist_engine.py"

door, name = sys.argv[1], sys.argv[2]
arm = ROOT / "runs" / name
subprocess.run([sys.executable, str(PROTO / "make_toy_spine.py"), str(arm)], check=True)

spine = arm / "spine.json"
calllog = arm / "engine_calls.jsonl"
calllog.write_text("", encoding="utf-8")

# ---- the identical task core -------------------------------------------------
CORE = (
    f"There is a gated work checklist (a 'spine') at {spine.as_posix()}. "
    "Drive it to done. At each gate: read what the gate tells you to do, actually "
    "do it, then satisfy that gate and move to the next one. Keep going until the "
    f"spine reports it is done. Do all your file work inside {arm.as_posix()}."
)

MCP_SUFFIX = "Use the available spine tools."

CLI_SUFFIX = (
    "Drive it with this command: "
    f"python {(PROTO / 'engine_cli.py').as_posix()} --file {spine.as_posix()} <verb> [args]. "
    "Pass --session-id cli-arm on every verb that changes state."
)

suffix = MCP_SUFFIX if door == "mcp" else CLI_SUFFIX
prompt = CORE + " " + suffix

env = dict(os.environ)
env["SPINE_ENGINE"] = str(ENGINE)
env["SPINE_CALLLOG"] = str(calllog)

cmd = [
    "claude", "-p", prompt,
    "--model", "sonnet",
    "--setting-sources", "",
    "--permission-mode", "bypassPermissions",
    "--tools", "Read,Write,Bash,Glob,Grep",
    "--output-format", "stream-json", "--verbose",
    "--strict-mcp-config",
]

if door == "mcp":
    mcp_cfg = arm / ".mcp.json"
    mcp_cfg.write_text(json.dumps({"mcpServers": {"spine": {
        "command": "python",
        "args": [str(PROTO / "mcp_spine_server.py")],
        "env": {
            "SPINE_FILE": str(spine),
            "SPINE_ENGINE": str(ENGINE),
            "SPINE_SESSION": "mcp-arm",
            "SPINE_CALLLOG": str(calllog),
        },
    }}}, indent=2), encoding="utf-8")
    cmd += ["--mcp-config", str(mcp_cfg)]
else:
    empty = arm / "no-mcp.json"
    empty.write_text('{"mcpServers":{}}', encoding="utf-8")
    cmd += ["--mcp-config", str(empty)]

transcript = arm / "transcript.jsonl"
(arm / "prompt.txt").write_text(prompt, encoding="utf-8")

with transcript.open("w", encoding="utf-8") as fh:
    proc = subprocess.run(cmd, cwd=str(arm), stdout=fh,
                          stderr=subprocess.PIPE, text=True, env=env, timeout=1500)

print(f"arm={name} door={door} exit={proc.returncode}")
print("prompt words:", len(prompt.split()))
if proc.stderr.strip():
    print("STDERR:", proc.stderr[-2000:])
