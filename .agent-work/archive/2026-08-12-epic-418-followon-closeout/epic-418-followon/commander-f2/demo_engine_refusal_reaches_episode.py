#!/usr/bin/env python3
"""Demonstrate, rather than assert from a code read, that an ENGINE refusal
arriving THROUGH the MCP door already reaches the run's episode today.

The Admiral's condition on accepting this run's narrowing of #541: the claim
"main() increments `refusals` and episode_capture reads it into the Mechanical
bin" is a statement about behaviour derived from three files. Drive one engine
refusal through the door and watch the counter move, or find out it does not.

Deliberately NOT a unit test. It launches the real server as a subprocess bound
to a scratch spine by the real environment seam, speaks real JSON-RPC to it,
and reads the real spine file and the real mechanical snapshot back off disk.

Run:  python .agent-work/epic-418-followon/commander-f2/demo_engine_refusal_reaches_episode.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SERVER = REPO / "scripts" / "mcp_spine_server.py"
ENGINE = REPO / "scripts" / "checklist_engine.py"
sys.path.insert(0, str(REPO / "scripts"))

OK = 0
FAIL = 0


def check(cond: bool, msg: str) -> None:
    global OK, FAIL
    if cond:
        OK += 1
        print(f"ASSERT OK:   {msg}")
    else:
        FAIL += 1
        print(f"ASSERT FAIL: {msg}")


class Session:
    def __init__(self, spine: Path, session_id: str):
        self.proc = subprocess.Popen(
            [sys.executable, str(SERVER)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, bufsize=1,
            env={
                "PATH": os.environ.get("PATH", ""),
                "SPINE_FILE": str(spine),
                "SPINE_ENGINE": str(ENGINE),
                "SPINE_SESSION": session_id,
                "SPINE_CALLLOG": str(spine.parent / "mcp_calls.jsonl"),
                "SPINE_START_MARKER": str(spine.parent / "mcp_server_started"),
            },
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


SPINE = {
    "work_id": "demo-refusal/nested-child",   # NESTED, like this run's own work-id
    "type": "gated",
    "items": ["s1"],
    "tasks": {
        "s1": {
            "id": "s1", "title": "a gate with a postcondition that is not met",
            "imperative": "do nothing; this gate exists to be refused",
            "preconditions": [],
            "postconditions": [{
                "id": "c1",
                "statement": "an artifact that will never be attached",
                "check": {"kind": "artifact", "evidence_type": "review-result"},
                "satisfied": False,
            }],
            "constraints": [], "directives": None, "child_checklist": None,
            "status": "pending", "status_detail": {}, "result": None,
            "finding": None, "evidence": [], "rework_count": 0,
        }
    },
}


def refusals_of(path: Path):
    return json.loads(path.read_text(encoding="utf-8")).get("refusals")


def main() -> int:
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    spine = root / "spine.json"
    with open(spine, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(SPINE, indent=1) + "\n")

    sess = Session(spine, "demo-refusal/nested-child")
    try:
        sess.rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                "clientInfo": {"name": "demo", "version": "0"}})

        # 1. Claim through the door. This ARMS the counter (checklist_engine.py ~1030).
        claimed = sess.call("spine_lease", action="claim", claimed_by="demo")
        check(not claimed.get("isError"), "spine_lease claim succeeds through the door")
        before = refusals_of(spine)
        check(before == 0, f"counter is ARMED at 0 after claim (read: {before!r})")

        sess.call("spine_start", task_id="s1")

        # 2. An ENGINE refusal through the door: advance a gate whose artifact
        #    postcondition is genuinely unmet. This ENTERS checklist_engine.main()
        #    and raises EngineError -- the path the claim is about.
        refused = sess.call("spine_advance", task_id="s1", mechanical=True)
        text = refused["content"][0]["text"]
        check(refused.get("isError") is True, "engine refusal surfaces as isError=True")
        check("REFUSED" in text, "the engine's own REFUSED marker rides through verbatim")

        after = refusals_of(spine)
        check(after == 1, f"THE COUNTER MOVED: refusals {before} -> {after} (expected 1)")

        # 3. A second engine refusal, to show it counts rather than latches.
        sess.call("spine_advance", task_id="s1", mechanical=True)
        after2 = refusals_of(spine)
        check(after2 == 2, f"counter counts rather than latching: {after} -> {after2}")

        # 4. The DOOR'S OWN rejection -- the silent class. Must NOT move the counter,
        #    and must leave no trace in the server's own call log.
        log = root / "mcp_calls.jsonl"
        lines_before = len(log.read_text(encoding="utf-8").splitlines()) if log.exists() else 0
        own = sess.call("spine_evidence", action="attest", task_id="s1")  # missing condition_id
        own_text = own["content"][0]["text"]
        check(own.get("isError") is True, "the door's own rejection is isError=True")
        check("missing required argument" in own_text,
              "it is the door's own _require() message, not the engine's")
        after3 = refusals_of(spine)
        check(after3 == after2,
              f"THE COUNTER DID NOT MOVE for the door's own rejection: {after2} -> {after3}")
        lines_after = len(log.read_text(encoding="utf-8").splitlines()) if log.exists() else 0
        check(lines_after == lines_before,
              f"and it left NO line in the server's own call log: {lines_before} -> {lines_after}")

        # 5. Does the moved counter reach the Mechanical bin the episode is built from?
        import episode_capture
        checklist = json.loads(spine.read_text(encoding="utf-8"))
        fields = episode_capture.mechanical_fields(checklist, base_dir=spine.parent)
        check(fields.get("refusals") == after3,
              f"episode_capture.mechanical_fields() carries refusals={fields.get('refusals')!r} "
              f"(spine says {after3!r}) into the Mechanical bin")
        check("refusals" in fields, "`refusals` is present in the Mechanical field group")
        print("\nMechanical field group as composed:")
        print(json.dumps(fields, indent=2, sort_keys=True))
    finally:
        sess.close()
        tmp.cleanup()

    print(f"\nASSERT OK: {OK}   ASSERT FAIL: {FAIL}")
    if FAIL == 0:
        print("\nDEMONSTRATED, not inferred:")
        print("  - an ENGINE refusal through the door DOES move `refusals`, and that value")
        print("    IS what episode_capture composes into the Mechanical bin. Already works.")
        print("  - the DOOR'S OWN rejection moves nothing and logs nothing. That is #541.")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
