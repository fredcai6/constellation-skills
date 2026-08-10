"""Raw JSON-RPC client for mcp_spine_server.py -- no model in the loop.

This is the server's own correctness harness: if a script built on this reaches
DONE, the server is a working MCP stdio endpoint end to end, and any later
failure (registration, allowedTools, a real agent) is a different layer, not
this one.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
SERVER = REPO_ROOT / "scripts" / "mcp_spine_server.py"
ENGINE = REPO_ROOT / "scripts" / "checklist_engine.py"


class McpSession:
    """Launches the server as a subprocess bound to one spine file, and speaks
    newline-delimited JSON-RPC 2.0 to it over stdio."""

    def __init__(self, spine_file: Path, session_id: str = "scratch-mcp", extra_env: dict | None = None):
        env = {
            "PATH": __import__("os").environ.get("PATH", ""),
            "SPINE_FILE": str(spine_file),
            "SPINE_ENGINE": str(ENGINE),
            "SPINE_SESSION": session_id,
            "SPINE_CALLLOG": str(spine_file.parent / "mcp_calls.jsonl"),
            "SPINE_START_MARKER": str(spine_file.parent / "mcp_server_started"),
        }
        if extra_env:
            env.update(extra_env)
        self.proc = subprocess.Popen(
            [sys.executable, str(SERVER)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, bufsize=1, env=env,
        )
        self._id = 0

    def rpc(self, method: str, params: dict | None = None) -> dict:
        self._id += 1
        req = {"jsonrpc": "2.0", "id": self._id, "method": method, "params": params or {}}
        self.proc.stdin.write(json.dumps(req) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line:
            err = self.proc.stderr.read()
            raise RuntimeError(f"server produced no reply to {method}; stderr:\n{err}")
        return json.loads(line)

    def initialize(self) -> dict:
        return self.rpc("initialize", {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "scratch-mcp-harness", "version": "0"},
        })

    def tools_list(self) -> list[dict]:
        return self.rpc("tools/list")["result"]["tools"]

    def call(self, name: str, **args) -> dict:
        r = self.rpc("tools/call", {"name": name, "arguments": args})
        if "error" in r:
            raise RuntimeError(f"JSON-RPC error calling {name}: {r['error']}")
        return r["result"]

    def close(self) -> None:
        self.proc.stdin.close()
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()
