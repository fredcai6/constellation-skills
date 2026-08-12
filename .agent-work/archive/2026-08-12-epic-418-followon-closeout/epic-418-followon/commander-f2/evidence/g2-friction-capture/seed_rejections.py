#!/usr/bin/env python3
"""End-to-end evidence for gate g2-implement (issue #541): launch the REAL MCP
door as a subprocess, induce a handful of the door's own rejections across all
three server-side classes, and land the resulting JSONL beside this file.

Deliberately not a pytest test (tests/test_mcp_friction_capture.py already covers
the mechanism with throwaway temp spines): this is the one-time run that produces
the artifact the g2 episode's mechanical.artifact-ref cites, under this run's own
nested work-id, per the g2-implement handoff's close criterion 3.

Run:  python .agent-work/epic-418-followon/commander-f2/evidence/g2-friction-capture/seed_rejections.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
SERVER = REPO / "scripts" / "mcp_spine_server.py"
ENGINE = REPO / "scripts" / "checklist_engine.py"

SPINE_PATH = HERE / "spine.json"
REJECTIONLOG = HERE / "mcp_rejections.jsonl"
CALLLOG = HERE / "mcp_calls.jsonl"
START_MARKER = HERE / "mcp_server_started"

SPINE = {
    "work_id": "g2-friction-capture-seed",
    "type": "gated",
    "config": {"rework_cap": 99},
    "items": ["g1"],
    "consolidation": None,
    "triage_candidates": [],
    "blockers": [],
    "tasks": {
        "g1": {
            "id": "g1", "title": "throwaway gate for seeding rejections",
            "imperative": "n/a -- this spine exists only to give the door something to be bound to",
            "preconditions": [], "postconditions": [],
            "constraints": [], "directives": None, "child_checklist": None,
            "status": "pending", "status_detail": {}, "result": None,
            "finding": None, "evidence": [], "rework_count": 0,
        }
    },
}


class Session:
    def __init__(self):
        env = {"PATH": os.environ.get("PATH", "")}
        env["SPINE_FILE"] = str(SPINE_PATH)
        env["SPINE_ENGINE"] = str(ENGINE)
        env["SPINE_SESSION"] = "g2-friction-capture-seed"
        env["SPINE_CALLLOG"] = str(CALLLOG)
        env["SPINE_START_MARKER"] = str(START_MARKER)
        env["SPINE_REJECTION_LOG"] = str(REJECTIONLOG)
        self.proc = subprocess.Popen(
            [sys.executable, str(SERVER)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", bufsize=1, env=env,
        )
        self._id = 0

    def rpc(self, method, params=None):
        self._id += 1
        self.proc.stdin.write(json.dumps(
            {"jsonrpc": "2.0", "id": self._id, "method": method, "params": params or {}}) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line:
            raise RuntimeError("no reply; stderr:\n" + self.proc.stderr.read())
        return json.loads(line)

    def call(self, name, **args):
        return self.rpc("tools/call", {"name": name, "arguments": args})["result"]

    def close(self):
        self.proc.stdin.close()
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()
        return self.proc.stderr.read()


def main() -> int:
    if REJECTIONLOG.exists():
        REJECTIONLOG.unlink()
    if CALLLOG.exists():
        CALLLOG.unlink()
    with open(SPINE_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(SPINE, indent=1) + "\n")

    sess = Session()
    print("-- inducing 3 real door-own rejections through the real server subprocess --")

    r1 = sess.call("spine_lease", action="teleport")  # unknown action
    print("1. spine_lease action=teleport ->", "isError" if r1.get("isError") else "OK",
          "|", r1["content"][0]["text"])

    r2 = sess.call("spine_evidence", action="attest", task_id="g1")  # missing condition_id
    print("2. spine_evidence action=attest task_id=g1 (no condition_id) ->",
          "isError" if r2.get("isError") else "OK", "|", r2["content"][0]["text"])

    r3 = sess.call("does_not_exist")  # unknown tool
    print("3. does_not_exist ->", "isError" if r3.get("isError") else "OK",
          "|", r3["content"][0]["text"])

    stderr = sess.close()
    if stderr.strip():
        print("\n-- server stderr --")
        print(stderr)

    print("\n-- mcp_rejections.jsonl (this run's real capture) --")
    if REJECTIONLOG.exists():
        text = REJECTIONLOG.read_text(encoding="utf-8")
        print(text, end="")
        records = [json.loads(line) for line in text.splitlines() if line.strip()]
    else:
        records = []
        print("(missing)")

    ok = len(records) == 3
    print(f"\n{'OK' if ok else 'FAIL'}: {len(records)} rejection record(s) written (expected 3)")
    print("classes:", [r.get("class") for r in records])
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
