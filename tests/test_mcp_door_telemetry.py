"""The MCP door's telemetry writes must never fail a call or kill the server
(issue #604, cleanup-a-door gate g1).

`_log()` writes two diagnostic side-channels -- the call log (`SPINE_CALLLOG`)
and the start marker (`SPINE_START_MARKER`). It is called from `run_engine()`
*outside* that function's own `try/except`, and `main()` catches only `KeyError`
around the dispatch. So before this gate, an `OSError` from either write unwound
the entire process: the client saw no reply at all, just a closed connection.

**A diagnostic side-channel must never be able to take down the thing it is
observing.** These tests pin that: with the telemetry destination unwritable the
door still answers, the process still exits 0, `stdout` stays pure JSON-RPC, and
the dropped record is reported on `stderr` rather than silently discarded.

Integration-style by design, like `tests/test_mcp_spine_server.py` and
`tests/test_mcp_friction_capture.py`: the real server is spawned as a subprocess
and driven over real JSON-RPC. The defect is a *process death*, which no in-process
call of `_log()` can observe -- only a subprocess has an exit code.

Two OSError shades are covered, because the door meets both in the field: a path
under a directory that does not exist (`FileNotFoundError`) and a path that is
itself a directory (`IsADirectoryError` on POSIX, `PermissionError` on Windows --
both `OSError`, which is why the assertions are about behaviour and not about the
exception type). `test_healthy_run_writes_both_telemetry_files` is the positive
control: without it, a guard that simply never wrote anything would pass every
other test here.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "scripts" / "mcp_spine_server.py"
ENGINE = ROOT / "scripts" / "checklist_engine.py"


def write_minimal_spine(root: Path) -> Path:
    """One pending gate -- just enough for `spine_status` to answer."""
    spine = {
        "work_id": "test-door-telemetry",
        "type": "gated",
        "config": {"rework_cap": 99},
        "items": ["g1"],
        "consolidation": None,
        "triage_candidates": [],
        "blockers": [],
        "tasks": {
            "g1": {
                "id": "g1", "title": "a gate to report on",
                "imperative": "do nothing; this gate exists to be reported",
                "preconditions": [],
                "postconditions": [{
                    "id": "c1", "statement": "never satisfied here",
                    "check": {"kind": "artifact", "evidence_type": "review-result"},
                    "satisfied": False,
                }],
                "constraints": [], "directives": None, "child_checklist": None,
                "status": "pending", "status_detail": {}, "result": None,
                "finding": None, "evidence": [], "rework_count": 0,
            }
        },
    }
    path = root / "spine.json"
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(spine, indent=1) + "\n")
    return path


class DoorRun:
    """One complete server lifetime: what it wrote, and how it died."""

    def __init__(self, stdout: str, stderr: str, returncode: int):
        self.stdout, self.stderr, self.returncode = stdout, stderr, returncode

    def answer(self, request_id: int) -> dict | None:
        """The reply to one request id, or None if the door never answered."""
        for line in self.stdout.splitlines():
            try:
                msg = json.loads(line)
            except ValueError:
                continue
            if msg.get("id") == request_id:
                return msg
        return None

    def unparseable_stdout_lines(self) -> list[str]:
        """Every stdout line that is not JSON-RPC. `stdout` is the protocol
        channel; a traceback or a diagnostic there corrupts the transport."""
        bad = []
        for line in self.stdout.splitlines():
            if not line.strip():
                continue
            try:
                msg = json.loads(line)
            except ValueError:
                bad.append(line)
                continue
            if msg.get("jsonrpc") != "2.0":
                bad.append(line)
        return bad


def drive_door(spine: Path, *, calllog: Path, start_marker: Path) -> DoorRun:
    """Spawn the real door bound to `spine`, call `spine_status` through it, and
    report what came back plus the process exit code."""
    env = {
        "PATH": os.environ.get("PATH", ""),
        "SPINE_FILE": str(spine),
        "SPINE_ENGINE": str(ENGINE),
        "SPINE_SESSION": "",
        "SPINE_CALLLOG": str(calllog),
        "SPINE_START_MARKER": str(start_marker),
        "SPINE_REJECTION_LOG": str(spine.parent / "mcp_rejections.jsonl"),
    }
    messages = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                    "clientInfo": {"name": "telemetry-test", "version": "0"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
         "params": {"name": "spine_status", "arguments": {}}},
    ]
    proc = subprocess.Popen(
        [sys.executable, str(SERVER)],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", env=env,
    )
    try:
        out, err = proc.communicate(
            "\n".join(json.dumps(m) for m in messages) + "\n", timeout=60)
    except subprocess.TimeoutExpired:  # pragma: no cover - a hung door, not the defect
        proc.kill()
        out, err = proc.communicate()
        raise AssertionError("the door never exited")
    return DoorRun(out, err, proc.returncode)


class TelemetryNeverFatalTests(unittest.TestCase):
    """With its own log unwritable, the door stays usable."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.spine = write_minimal_spine(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def _assert_door_survived(self, run: DoorRun) -> None:
        answer = run.answer(2)
        self.assertIsNotNone(
            answer,
            f"the door never answered the call; exit {run.returncode}, stderr:\n{run.stderr}")
        self.assertIn("result", answer, f"expected a tool result, got {answer}")
        self.assertEqual(
            0, run.returncode,
            f"the door died on its own telemetry write; stderr:\n{run.stderr}")

    def _lost_call_record(self, stderr: str) -> dict:
        """The call record the door reported as dropped, parsed back out of its
        own stderr line. Asserting on the parsed record rather than on the
        sentence around it keeps this a test of what was reported, not of how it
        was worded."""
        for line in stderr.splitlines():
            marker = "Lost record: "
            if "TELEMETRY WRITE FAILED" not in line or marker not in line:
                continue
            payload = line.split(marker, 1)[1]
            try:
                record = json.loads(payload)
            except ValueError:
                continue  # the start-marker drop reports no JSON record
            return record
        self.fail(f"no dropped call record was reported; stderr:\n{stderr}")

    def test_call_log_under_a_missing_directory_is_not_fatal(self):
        """The reproduction from issue #604: the bound spine's directory is gone,
        so the call log beside it cannot be opened."""
        gone = self.root / "gone"
        run = drive_door(self.spine, calllog=gone / "mcp_calls.jsonl",
                         start_marker=gone / "mcp_server_started")
        self._assert_door_survived(run)

    def test_call_log_that_is_a_directory_is_not_fatal(self):
        """A second OSError shade: the destination exists but is not a file."""
        blocked = self.root / "mcp_calls.jsonl"
        blocked.mkdir()
        run = drive_door(self.spine, calllog=blocked,
                         start_marker=self.root / "mcp_server_started")
        self._assert_door_survived(run)

    def test_start_marker_alone_being_unwritable_is_not_fatal(self):
        """The second write in `_log` is guarded independently of the first: here
        the call log is perfectly writable and only the marker is not."""
        run = drive_door(self.spine, calllog=self.root / "mcp_calls.jsonl",
                         start_marker=self.root / "gone" / "mcp_server_started")
        self._assert_door_survived(run)
        self.assertTrue((self.root / "mcp_calls.jsonl").exists(),
                        "the writable channel must still be written")

    def test_an_unwritable_call_log_does_not_suppress_the_start_marker(self):
        """The two writes are guarded SEPARATELY, and this is the test that says
        so. One `try` around the whole of `_log` would pass every other test in
        this file: it survives, and it answers. What it would NOT do is reach the
        second write after the first raised -- the marker would silently stop
        being written the moment the call log became unwritable, which is one
        side-channel taking out the other."""
        marker = self.root / "mcp_server_started"
        run = drive_door(self.spine, calllog=self.root / "gone" / "mcp_calls.jsonl",
                         start_marker=marker)
        self._assert_door_survived(run)
        self.assertTrue(
            marker.exists(),
            "the start marker must still be written when only the call log is unwritable")

    def test_the_dropped_record_is_reported_on_stderr(self):
        """Never a silent drop. `_log_rejection`'s principle, applied here: fail
        loud, every occurrence."""
        gone = self.root / "gone"
        run = drive_door(self.spine, calllog=gone / "mcp_calls.jsonl",
                         start_marker=gone / "mcp_server_started")
        self._assert_door_survived(run)
        self.assertIn(str(gone / "mcp_calls.jsonl"), run.stderr,
                      f"the drop was not reported on stderr; stderr:\n{run.stderr}")
        self.assertIn(str(gone / "mcp_server_started"), run.stderr,
                      "both dropped writes are reported, not just the first")
        lost = self._lost_call_record(run.stderr)
        self.assertEqual("current", lost["verb"],
                         "the report must carry the lost record itself, not just a path")
        self.assertEqual(0, lost["code"])

    def test_stdout_stays_pure_json_rpc_when_telemetry_fails(self):
        """`stdout` is the protocol channel and nothing else may enter it."""
        gone = self.root / "gone"
        run = drive_door(self.spine, calllog=gone / "mcp_calls.jsonl",
                         start_marker=gone / "mcp_server_started")
        self.assertEqual([], run.unparseable_stdout_lines())

    def test_healthy_run_writes_both_telemetry_files(self):
        """The positive control. A guard that dropped the writes entirely would
        pass every test above; this is what stops that from being a green run."""
        calllog = self.root / "mcp_calls.jsonl"
        marker = self.root / "mcp_server_started"
        run = drive_door(self.spine, calllog=calllog, start_marker=marker)
        self._assert_door_survived(run)
        self.assertEqual("", run.stderr.strip(), "a healthy run reports no drop")
        records = [json.loads(line) for line in
                   calllog.read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertEqual(1, len(records), "one engine call, one record")
        self.assertEqual("current", records[0]["verb"])
        self.assertTrue(marker.exists(), "the start marker is written on first success")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
