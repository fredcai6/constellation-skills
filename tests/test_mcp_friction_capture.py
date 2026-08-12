"""Tests for the MCP door's own rejection capture (issue #541, epic-418-followon
wave 2, gate g2).

**What #541's title gets half right.** An ENGINE refusal riding through the door
already reaches the run's episode today: `checklist_engine.main()` counts it into
`refusals`, and `episode_capture.mechanical_fields()` composes that value into the
`## Mechanical` bin. Reproduced independently, on a real server subprocess, by
`.agent-work/archive/2026-08-12-epic-418-followon-closeout/epic-418-followon/commander-f2/demo_engine_refusal_reaches_episode.py`
-- do not re-test that half here.

**What is actually silent** is the door's OWN rejection: every `_tool_error(...)`
return in `call_tool()`/`main()` short-circuits BEFORE `run_engine()` is ever
called, so `_log()` never runs, `mcp_calls.jsonl` gains no line, and the engine's
`refusals` counter never moves. Three classes take that silent path and are covered
here:

  * unknown tool name       -- `main()`'s `tools/call` branch
  * unknown `action`        -- `call_tool`, the 4 multiplexed tools
  * missing required argument -- `_require()`'s call sites

A FOURTH class -- a client-side schema rejection -- is sharper still and is NOT
covered here: it never reaches this server process at all, so there is nothing
server-side to instrument. See the g2 IMPLEMENTER_RESULT's coverage-boundary
statement.

Integration-style by design, like `tests/test_mcp_spine_server.py`: the door's own
rejection path is verified by actually spawning the real server subprocess and
calling through it over real JSON-RPC, never by importing internals and asserting
against a mock.
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
    """One task with one intentionally unmet postcondition -- just enough to
    exercise a genuine ENGINE refusal (the negative control below) without pulling
    in the fuller fixture `tests/test_mcp_spine_server.py` uses for its own,
    broader tool-surface coverage."""
    spine = {
        "work_id": "test-friction-capture",
        "type": "gated",
        "config": {"rework_cap": 99},
        "items": ["g1"],
        "consolidation": None,
        "triage_candidates": [],
        "blockers": [],
        "tasks": {
            "g1": {
                "id": "g1", "title": "a gate with an unmet postcondition",
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
    path = root / "spine.json"
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(spine, indent=1) + "\n")
    return path


class McpRpcClient:
    """Minimal newline-delimited JSON-RPC 2.0 client, spawning the real server
    process bound to one spine file -- the same shape `tests/test_mcp_spine_server.py`
    uses, with an added `SPINE_REJECTION_LOG` override this file needs and that one
    does not."""

    def __init__(self, spine_file: Path, session_id: str = "friction-test",
                 rejection_log: Path | None = None):
        env = {"PATH": os.environ.get("PATH", "")}
        env["SPINE_FILE"] = str(spine_file)
        env["SPINE_ENGINE"] = str(ENGINE)
        env["SPINE_SESSION"] = session_id
        base = spine_file.parent
        env["SPINE_CALLLOG"] = str(base / "mcp_calls.jsonl")
        env["SPINE_START_MARKER"] = str(base / "mcp_server_started")
        if rejection_log is not None:
            env["SPINE_REJECTION_LOG"] = str(rejection_log)
        self.proc = subprocess.Popen(
            [sys.executable, str(SERVER)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", bufsize=1, env=env,
        )
        self._id = 0

    def rpc(self, method: str, params: dict | None = None) -> dict:
        self._id += 1
        req = {"jsonrpc": "2.0", "id": self._id, "method": method, "params": params or {}}
        self.proc.stdin.write(json.dumps(req) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line:
            raise RuntimeError(f"no reply to {method}; stderr:\n{self.proc.stderr.read()}")
        return json.loads(line)

    def call(self, name: str, **args) -> dict:
        r = self.rpc("tools/call", {"name": name, "arguments": args})
        assert "error" not in r, f"JSON-RPC error: {r['error']}"
        return r["result"]

    def close(self) -> None:
        if self.proc.stdin and not self.proc.stdin.closed:
            self.proc.stdin.close()
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()


class RejectionCaptureRecordsEachClassTests(unittest.TestCase):
    """The door records ITS OWN rejection -- one JSONL record per occurrence,
    carrying enough to diagnose: which tool, which class, what was
    missing/unknown, and when."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.spine = write_minimal_spine(self.root)
        self.rejectlog = self.root / "mcp_rejections.jsonl"
        self.client = McpRpcClient(self.spine, rejection_log=self.rejectlog)

    def tearDown(self):
        self.client.close()
        self.tmp.cleanup()

    def _records(self) -> list[dict]:
        if not self.rejectlog.exists():
            return []
        text = self.rejectlog.read_text(encoding="utf-8")
        return [json.loads(line) for line in text.splitlines() if line.strip()]

    def test_no_rejection_means_no_file_at_all(self):
        """A read-only call that is not a rejection writes nothing -- so a later
        zero-record run is a genuine reading, not a placeholder file nobody
        cleaned up."""
        status = self.client.call("spine_status")
        self.assertFalse(status.get("isError"))
        self.assertFalse(self.rejectlog.exists())

    def test_missing_required_argument_is_recorded(self):
        result = self.client.call("spine_evidence", action="attest", task_id="g1")  # no condition_id
        self.assertTrue(result.get("isError"))
        records = self._records()
        self.assertEqual(1, len(records), "one rejection, one record")
        rec = records[0]
        self.assertEqual("spine_evidence", rec["tool"])
        self.assertEqual("missing-required-argument", rec["class"])
        self.assertIn("condition_id", rec["detail"])
        self.assertIn("ts", rec)

    def test_unknown_action_is_recorded(self):
        result = self.client.call("spine_lease", action="teleport")
        self.assertTrue(result.get("isError"))
        records = self._records()
        self.assertEqual(1, len(records), "one rejection, one record")
        rec = records[0]
        self.assertEqual("spine_lease", rec["tool"])
        self.assertEqual("unknown-action", rec["class"])
        self.assertIn("teleport", rec["detail"])

    def test_unknown_tool_name_is_recorded(self):
        result = self.client.call("does_not_exist")
        self.assertTrue(result.get("isError"))
        records = self._records()
        self.assertEqual(1, len(records), "one rejection, one record")
        rec = records[0]
        self.assertEqual("unknown-tool", rec["class"])
        self.assertIn("does_not_exist", rec["detail"])

    def test_a_seeded_rejection_is_scored_by_the_instrument(self):
        """Close criterion: 'a seeded rejection is scored, so a later zero is a
        reading and not a blind spot.' Two DIFFERENT classes, induced in the SAME
        process, must produce two SEPARATE records -- proving the instrument
        counts occurrences rather than latching a boolean."""
        self.client.call("spine_lease", action="teleport")
        self.client.call("spine_evidence", action="attest", task_id="g1")
        records = self._records()
        self.assertEqual(2, len(records), "two induced rejections, two recorded -- not coalesced")
        self.assertEqual(
            ["unknown-action", "missing-required-argument"],
            [r["class"] for r in records],
        )

    def test_the_same_rejection_twice_in_one_process_yields_two_records(self):
        """PER OCCURRENCE, not per (tool, class), and not per run.

        Added at g2-review. The reviewer mutated `_log_rejection` with a
        per-(tool, rejection_class) dedup memo -- a repeat of an identical
        rejection silently dropped -- and the whole file stayed green. The
        shipped code was already correct; what was missing was any test that
        could tell. Every existing case induced its class exactly once, so
        "one record per occurrence" and "one record per class" were
        indistinguishable to the suite.

        That is the same shape as `fail-loud-every-turn`'s own defect: a
        capture that coalesces repeats reports the first fumble and hides every
        one after it, which is worst precisely when an agent is stuck retrying
        the same malformed call."""
        for _ in range(3):
            result = self.client.call("spine_evidence", action="attest", task_id="g1")
            self.assertTrue(result.get("isError"))

        records = self._records()
        self.assertEqual(
            3, len(records),
            "three identical rejections produced "
            f"{len(records)} record(s) -- the capture is coalescing repeats, so an agent "
            "stuck retrying one malformed call would leave a single trace",
        )
        self.assertEqual(
            [("spine_evidence", "missing-required-argument")] * 3,
            [(r["tool"], r["class"]) for r in records],
        )

    def test_engine_refusal_is_not_double_counted_here(self):
        """Negative control: an ENGINE refusal already reaches the episode through
        `refusals`/`mcp_calls.jsonl` (see the handoff's demo script) -- it is NOT a
        door-own rejection, so this instrument must record nothing for it."""
        self.client.call("spine_lease", action="claim", claimed_by="tester")
        self.client.call("spine_start", task_id="g1")
        refused = self.client.call("spine_advance", task_id="g1", mechanical=True)
        self.assertTrue(refused.get("isError"), "the engine itself must refuse this advance")
        self.assertEqual([], self._records(), "an engine refusal is not this instrument's concern")


class LoudFailureOnCaptureWriteTests(unittest.TestCase):
    """Constraint: 'a capture that fails quietly is the same defect as the door it
    instruments.' If the log itself cannot be written, the door must say so on
    EVERY occurrence -- never once per run, never coalesced, never only at exit."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.spine = write_minimal_spine(self.root)
        # A DIRECTORY at the log's own path: opening it for append raises OSError
        # on every single attempt, deterministically and portably, within one
        # process -- the shape close criterion 5 demands (N>=2 induced failures,
        # N separate messages).
        self.rejectlog = self.root / "mcp_rejections.jsonl"
        self.rejectlog.mkdir()
        self.client = McpRpcClient(self.spine, rejection_log=self.rejectlog)

    def tearDown(self):
        self.client.close()
        self.tmp.cleanup()

    def _assert_nothing_was_written(self):
        """The induced failure really did prevent every write.

        NOT `assertFalse(self.rejectlog.is_file())` -- `setUp` created that path
        as a DIRECTORY, so `is_file()` is False before a single call is made and
        stays False no matter what the door does. It could not fail, so it was
        not evidence. What IS decidable: the path is still the directory setUp
        made (nothing replaced it), and nothing was written inside it.
        """
        self.assertTrue(
            self.rejectlog.is_dir(),
            "the log path is no longer the directory setUp created -- this test's "
            "whole mechanism for making every write fail has stopped working",
        )
        self.assertEqual(
            [], sorted(p.name for p in self.rejectlog.iterdir()),
            "nothing should have been written: every append to this path raises",
        )

    def test_three_induced_write_failures_in_one_process_yield_three_messages(self):
        """Three DIFFERENT rejection classes. Covers 'each message names its own
        rejection'; see the test below for 'one per occurrence', which this
        shape cannot decide."""
        results = [
            self.client.call("spine_lease", action="teleport"),
            self.client.call("spine_evidence", action="attest", task_id="g1"),
            self.client.call("does_not_exist"),
        ]
        # The isError contract, asserted rather than merely described: a capture
        # failure must not crash the door, must not turn a rejection into a
        # non-error answer, and must not swallow the door's own message.
        for result in results:
            self.assertIs(
                True, result.get("isError"),
                "a rejection whose capture failed must STILL come back to the caller "
                "as a failed tool call -- the caller's contract does not depend on "
                "whether the door managed to write its own log",
            )
            self.assertTrue(result["content"][0]["text"].strip())

        self.client.close()
        stderr = self.client.proc.stderr.read()
        occurrences = stderr.count("REJECTION CAPTURE FAILED")
        self.assertEqual(
            3, occurrences,
            "3 induced write failures in ONE process must yield 3 SEPARATE loud "
            "messages -- one induced failure asserting one message proves nothing "
            "about 'every'",
        )
        # Each occurrence names its OWN rejection -- not three copies of one
        # generic line.
        self.assertIn("teleport", stderr)
        self.assertIn("condition_id", stderr)
        self.assertIn("does_not_exist", stderr)
        self._assert_nothing_was_written()

    def test_the_same_write_failure_three_times_yields_three_messages(self):
        """PER OCCURRENCE on the FAILURE path, not per (tool, class).

        The test above induces three DIFFERENT rejection classes, so "one loud
        message per class" and "one per occurrence" are indistinguishable to it:
        a mutant that memoised the stderr message per `(tool, rejection_class)`
        still emits three, and the whole friction file stays green.

        This is the same gap the g2 reviewer closed on the SUCCESS path
        (`RejectionCaptureRecordsEachClassTests.test_the_same_rejection_twice_in_one_process_yields_two_records`)
        left open on the failure path. It matters for exactly the case the
        constraint was written for: an agent retrying ONE malformed call against
        an unwritable log gets one message and then silence -- reporting the
        first fumble and hiding every one after it, which is worst precisely
        when the agent is stuck.

        Identical rejection, three times: same tool, same class, same detail. If
        anything coalesces, this is the only shape that can see it.
        """
        for _ in range(3):
            result = self.client.call("spine_evidence", action="attest", task_id="g1")
            self.assertIs(
                True, result.get("isError"),
                "every repeat must still be a failed tool call to the caller",
            )

        self.client.close()
        stderr = self.client.proc.stderr.read()
        self.assertEqual(
            3, stderr.count("REJECTION CAPTURE FAILED"),
            "three IDENTICAL induced write failures produced "
            f"{stderr.count('REJECTION CAPTURE FAILED')} loud message(s) -- the failure "
            "path is coalescing repeats, so an agent retrying one malformed call against "
            "an unwritable log would get one message and then silence",
        )
        self.assertEqual(
            3, stderr.count("condition_id"),
            "each of the three messages must carry the lost record, naming what was "
            "missing -- a repeat reported without its payload is not a diagnosable event",
        )
        self._assert_nothing_was_written()


if __name__ == "__main__":
    unittest.main()
