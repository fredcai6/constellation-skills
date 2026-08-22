"""Tests for scripts/mcp_spine_server.py (issue #424, workstream F: the MCP
front door on the checklist engine).

Per-dispatch identity is delivered by the committed project-scope `.mcp.json`
`${VAR}` expansion from the caller's environment, not by generating a config
file per dispatch -- the per-dispatch generation path was removed, measured
redundant against the committed `${VAR}` path (see the g1 rework handoff and
MISSION_FRAME.md). `McpJsonVarExpansionLaunchTests` below is the env-seam
coverage that used to live against the generator, carried onto the mechanism
that actually ships.

Integration-style by design: the server's whole job is to be a faithful pass
-through to `checklist_engine.main()`, so these tests spawn the real server as
a subprocess and drive it over real newline-delimited JSON-RPC, the same way a
real MCP client would -- per doctrine (`global-crew.md`), generated
advice/recovery text is executed and asserted against, never string-matched
around; a wrapper is verified by actually calling through it.
"""

from __future__ import annotations

import json
import os
import queue
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "scripts" / "mcp_spine_server.py"
ENGINE = ROOT / "scripts" / "checklist_engine.py"
MCP_JSON = ROOT / ".mcp.json"


def _installer():
    """`install_constellation` is the one home for `.mcp.json` semantics
    (`is_rewritable_mcp_command`, `expand_mcp_var`). Imported by reference so
    this file cannot carry a second, drifting copy of the expansion rule."""
    import importlib.util
    if "install_constellation" in sys.modules:
        return sys.modules["install_constellation"]
    spec = importlib.util.spec_from_file_location(
        "install_constellation", ROOT / "scripts" / "install_constellation.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["install_constellation"] = module
    spec.loader.exec_module(module)
    return module

EXPECTED_TOOLS = {
    "spine_status", "spine_lease", "spine_start", "spine_advance",
    "spine_evidence", "spine_halt", "spine_survey_result",
    "spine_capture", "spine_amend",
}

#: The LIFECYCLE tools -- `mcp_spine_server.LIFECYCLE_TOOL_NAMES`. None of them
#: is an engine pass-through (none ever calls `run_engine`), so none covers an
#: engine verb, and both surface claims below scope themselves off this set the
#: same way `tests/test_mcp_identity.py`'s runtime sweep does. It is stated ONCE
#: here rather than hand-copied into each test, because it has now had to grow
#: twice (issue #559 C3/g3 added `spine_open`/`spine_close`; issue #567 lane A
#: added `spine_bind`) and two copies of a growing set is two chances to update
#: one of them.
LIFECYCLE_TOOLS_COVER_NO_VERB = {"spine_open", "spine_bind", "spine_close"}

#: Every engine verb, and the one tool that reaches it -- the completeness
#: claim `scripts/mcp_spine_server.py`'s own docstring now makes ("18 of 18
#: verbs covered"), pinned against the real TOOLS schemas rather than left as
#: prose (issue #559, N1: `skip`/`reopen`/`append`/`amend`/`flag-candidate`
#: used to have no tool at all and stayed CLI-only; see
#: `AllEighteenVerbsCoveredTests` below and the real-JSON-RPC exercises in
#: `NewlyCoveredVerbsTests`).
VERB_TO_TOOL = {
    "current": "spine_status",
    "claim": "spine_lease", "release": "spine_lease", "heartbeat": "spine_lease",
    "start": "spine_start",
    "advance": "spine_advance",
    "attest": "spine_evidence", "attach": "spine_evidence", "waive": "spine_evidence",
    "block": "spine_halt", "resume": "spine_halt", "skip": "spine_halt", "reopen": "spine_halt",
    "record": "spine_survey_result", "consolidate": "spine_survey_result",
    "append": "spine_capture", "flag-candidate": "spine_capture",
    "amend": "spine_amend",
}

_FILE_EXISTS_SNIPPET = "import sys, pathlib; sys.exit(0 if pathlib.Path(sys.argv[1]).is_file() else 1)"


def file_exists_check(path: str) -> str:
    """Build a `command`-kind postcondition that genuinely checks file
    existence -- portable house pattern (see PASS_COMMAND/FAIL_COMMAND in
    tests/test_checklist_engine.py) driven through `sys.executable` instead of
    the POSIX `test` builtin, which the engine's command checks cannot rely on
    (no `sh`/`test` on a Windows box; see `_find_posix_shell` in
    scripts/checklist_engine.py). `path` is passed as a `python -c` argv
    element -- never interpolated into the Python source text -- and both the
    snippet and the path are `shlex.quote`d before being placed on the outer
    shell command line. That quoting is load-bearing on Windows: an unquoted
    f-string interpolation (the bug this replaces) lets the shell's own
    backslash-escape processing strip a Windows path's backslashes before
    Python ever sees it, and a plain double-quoted interpolation still breaks
    on a path containing a space. `shlex.quote` single-quotes anything with
    such characters, and a POSIX shell (bash on Windows, sh elsewhere) applies
    zero escape processing inside single quotes, so the path survives byte for
    byte. Exits 0 when `path` is a file, non-zero otherwise -- a genuine
    existence check in both directions, never an always-pass stub."""
    return f"{shlex.quote(sys.executable)} -c {shlex.quote(_FILE_EXISTS_SNIPPET)} {shlex.quote(path)}"


def write_gated_spine(root: Path) -> Path:
    """A small gated spine covering every condition shape the tool surface
    must exercise: command-checked, attested (check: null), an artifact
    postcondition, and a waivable postcondition."""
    ws = root / "workspace"
    ws.mkdir(parents=True, exist_ok=True)
    w = str(ws)
    spine = {
        "work_id": "test-mcp-door",
        "type": "gated",
        "config": {"rework_cap": 99},
        "items": ["g1", "g2", "g3"],
        "consolidation": None,
        "triage_candidates": [],
        "blockers": [],
        "tasks": {
            "g1": {
                "id": "g1", "title": "setup", "imperative": f"create {w}/notes.txt",
                "preconditions": [],
                "postconditions": [
                    {"id": "c1", "statement": "notes.txt exists",
                     "check": {"kind": "command", "command": file_exists_check(f"{w}/notes.txt")},
                     "satisfied": False},
                    {"id": "c2", "statement": "understood", "check": None, "satisfied": False},
                ],
                "constraints": [], "directives": None, "child_checklist": None,
                "status": "pending", "status_detail": {}, "result": None,
                "finding": None, "evidence": [], "rework_count": 0,
            },
            "g2": {
                "id": "g2", "title": "decision", "imperative": "record the decision",
                "preconditions": [],
                "postconditions": [
                    {"id": "c1", "statement": "decision attached",
                     "check": {"kind": "artifact", "evidence_type": "user-decision"},
                     "satisfied": False},
                ],
                "constraints": [], "directives": None, "child_checklist": None,
                "status": "pending", "status_detail": {}, "result": None,
                "finding": None, "evidence": [], "rework_count": 0,
            },
            "g3": {
                "id": "g3", "title": "optional check", "imperative": "optional report",
                "preconditions": [],
                "postconditions": [
                    {"id": "c1", "statement": "optional_report.txt exists",
                     "check": {"kind": "command", "command": file_exists_check(f"{w}/optional_report.txt")},
                     "override_policy": {"allowed": True, "authority": "human", "reason_required": True},
                     "satisfied": False},
                ],
                "constraints": [], "directives": None, "child_checklist": None,
                "status": "pending", "status_detail": {}, "result": None,
                "finding": None, "evidence": [], "rework_count": 0,
            },
        },
    }
    path = root / "spine.json"
    path.write_text(json.dumps(spine, indent=2), encoding="utf-8")
    return path


def write_survey(root: Path) -> Path:
    survey = {
        "work_id": "test-mcp-door-survey",
        "type": "survey",
        "config": {"rework_cap": 99},
        "items": ["r1"],
        "consolidation": None,
        "triage_candidates": [],
        "blockers": [],
        "tasks": {
            "r1": {
                "id": "r1", "title": "check", "imperative": "check something",
                "preconditions": [], "postconditions": [],
                "constraints": [], "directives": None, "child_checklist": None,
                "status": "pending", "status_detail": {}, "result": None,
                "finding": None, "evidence": [], "rework_count": 0,
            },
        },
    }
    path = root / "survey.json"
    path.write_text(json.dumps(survey, indent=2), encoding="utf-8")
    return path


class McpRpcClient:
    """Minimal newline-delimited JSON-RPC 2.0 client, spawning the real
    server process bound to one spine file -- exactly the MCP stdio shape."""

    def __init__(self, spine_file: Path, session_id: str = "test-session", tmp_dir: Path | None = None):
        env = {"PATH": __import__("os").environ.get("PATH", "")}
        env["SPINE_FILE"] = str(spine_file)
        env["SPINE_ENGINE"] = str(ENGINE)
        env["SPINE_SESSION"] = session_id
        base = tmp_dir or spine_file.parent
        env["SPINE_CALLLOG"] = str(base / "mcp_calls.jsonl")
        env["SPINE_START_MARKER"] = str(base / "mcp_server_started")
        self.proc = subprocess.Popen(
            [sys.executable, str(SERVER)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            # Explicit UTF-8: decode the door's pipes as UTF-8 rather than
            # the platform default, matching the protocol encoding pinned in
            # scripts/mcp_spine_server.py -- a future regression there then
            # surfaces as a decode mismatch, not a matching-default accident.
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
        self.proc.stdin.close()
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()


class ServerProtocolTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.spine = write_gated_spine(self.root)
        self.client = McpRpcClient(self.spine)

    def tearDown(self):
        self.client.close()
        self.tmp.cleanup()

    def test_initialize_returns_server_info(self):
        result = self.client.rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                                 "clientInfo": {"name": "test", "version": "0"}})
        info = result["result"]["serverInfo"]
        self.assertEqual("spine", info["name"])
        self.assertIn("version", info)

    def test_tools_list_is_exactly_the_nine_committed_tools(self):
        tools = self.client.rpc("tools/list")["result"]["tools"]
        names = {t["name"] for t in tools}
        # The lifecycle tools are not engine pass-throughs (see
        # mcp_spine_server.py's module docstring, "The lifecycle door") --
        # EXPECTED_TOOLS names the original 9 engine tools this test was written
        # for, unchanged, and the count is DERIVED from the two sets rather than
        # written as a literal that has to be remembered.
        self.assertEqual(EXPECTED_TOOLS, names - LIFECYCLE_TOOLS_COVER_NO_VERB)
        self.assertEqual(len(EXPECTED_TOOLS) + len(LIFECYCLE_TOOLS_COVER_NO_VERB), len(tools),
                          "9 engine tools + the lifecycle tools (issue #559 N1/C3, "
                          "issue #567 lane A) -- not one tool per verb, and no verb "
                          "left uncovered")
        for t in tools:
            self.assertIn("description", t)
            self.assertIn("inputSchema", t)
            self.assertEqual("object", t["inputSchema"]["type"])

    def test_unknown_method_returns_json_rpc_error(self):
        r = self.client.rpc("nonexistent/method")
        self.assertIn("error", r)
        self.assertEqual(-32601, r["error"]["code"])

    def test_unknown_tool_is_a_tool_error_not_a_crash(self):
        result = self.client.call("does_not_exist")
        self.assertTrue(result["isError"])


class ToolsWrapEngineTests(unittest.TestCase):
    """Every tool must genuinely call through to checklist_engine.main() --
    verified by comparing tool output against the same spine's real state,
    never by inspecting server internals."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.spine = write_gated_spine(self.root)
        self.client = McpRpcClient(self.spine, session_id="wrap-test")

    def tearDown(self):
        self.client.close()
        self.tmp.cleanup()

    def _cli_current(self) -> str:
        # Explicit UTF-8: the CLI's own stdout is already pinned to UTF-8 by
        # checklist_engine.py's own _utf8_stdio(); decode it explicitly here
        # too rather than falling back to the platform default when reading
        # it back into this test process.
        r = subprocess.run([sys.executable, str(ENGINE), "--file", str(self.spine), "current"],
                            capture_output=True, text=True, encoding="utf-8")
        return r.stdout.rstrip("\n")

    def test_spine_status_matches_real_engine_current_output(self):
        status = self.client.call("spine_status")
        self.assertFalse(status.get("isError"))
        text = status["content"][0]["text"]
        self.assertIn("ACTIVE g1", text)
        self.assertIn("notes.txt", text)
        self.assertEqual(self._cli_current(), text,
                          "spine_status must be byte-identical to the CLI `current` projection")

    def test_byte_identity_check_can_actually_fail(self):
        """Negative control: the equality check above is not vacuous -- a
        deliberately different string must compare unequal."""
        status = self.client.call("spine_status")
        text = status["content"][0]["text"]
        self.assertNotEqual(text, " " + text)
        self.assertNotEqual(text, text.replace("g1", "gX"))

    def test_spine_lease_claim_release_heartbeat(self):
        claimed = self.client.call("spine_lease", action="claim", claimed_by="tester")
        self.assertFalse(claimed.get("isError"))
        self.assertIn("claimed lease", claimed["content"][0]["text"])
        hb = self.client.call("spine_lease", action="heartbeat")
        self.assertFalse(hb.get("isError"))
        released = self.client.call("spine_lease", action="release")
        self.assertFalse(released.get("isError"))
        self.assertIn("released", released["content"][0]["text"])

    def test_spine_start_and_advance_drive_a_gate_to_complete(self):
        self.client.call("spine_lease", action="claim", claimed_by="tester")
        start = self.client.call("spine_start", task_id="g1")
        self.assertFalse(start.get("isError"))
        (self.root / "workspace" / "notes.txt").write_text("hi\n", encoding="utf-8")
        self.client.call("spine_evidence", action="attest", task_id="g1", condition_id="c2",
                          which="postconditions")
        adv = self.client.call("spine_advance", task_id="g1", why="notes.txt written, understood")
        self.assertFalse(adv.get("isError"))
        self.assertIn("g1 -> complete", adv["content"][0]["text"])

    def test_spine_advance_mechanical_flag(self):
        self.client.call("spine_lease", action="claim", claimed_by="tester")
        self.client.call("spine_start", task_id="g1")
        (self.root / "workspace" / "notes.txt").write_text("hi\n", encoding="utf-8")
        self.client.call("spine_evidence", action="attest", task_id="g1", condition_id="c2",
                          which="postconditions")
        adv = self.client.call("spine_advance", task_id="g1", mechanical=True)
        self.assertFalse(adv.get("isError"))

    def test_spine_evidence_attach_satisfies_artifact_postcondition(self):
        self.client.call("spine_lease", action="claim", claimed_by="tester")
        self.client.call("spine_start", task_id="g1")
        (self.root / "workspace" / "notes.txt").write_text("hi\n", encoding="utf-8")
        self.client.call("spine_evidence", action="attest", task_id="g1", condition_id="c2",
                          which="postconditions")
        self.client.call("spine_advance", task_id="g1", mechanical=True)
        self.client.call("spine_start", task_id="g2")
        attach = self.client.call("spine_evidence", action="attach", task_id="g2",
                                   evidence_type="user-decision", fields={"decision": "proceed"})
        self.assertFalse(attach.get("isError"))
        self.assertIn("attached", attach["content"][0]["text"])
        adv = self.client.call("spine_advance", task_id="g2", mechanical=True)
        self.assertFalse(adv.get("isError"))

    def test_spine_evidence_waive_satisfies_without_making_check_true(self):
        self.client.call("spine_lease", action="claim", claimed_by="tester")
        self.client.call("spine_start", task_id="g1")
        (self.root / "workspace" / "notes.txt").write_text("hi\n", encoding="utf-8")
        self.client.call("spine_evidence", action="attest", task_id="g1", condition_id="c2",
                          which="postconditions")
        self.client.call("spine_advance", task_id="g1", mechanical=True)
        self.client.call("spine_start", task_id="g2")
        self.client.call("spine_evidence", action="attach", task_id="g2",
                          evidence_type="user-decision", fields={"decision": "proceed"})
        self.client.call("spine_advance", task_id="g2", mechanical=True)

        self.client.call("spine_start", task_id="g3")
        self.assertFalse((self.root / "workspace" / "optional_report.txt").exists())
        waive = self.client.call("spine_evidence", action="waive", task_id="g3", condition_id="c1",
                                  which="postconditions", authority="human", reason="accepted as non-blocking")
        self.assertFalse(waive.get("isError"))
        adv = self.client.call("spine_advance", task_id="g3", mechanical=True)
        self.assertFalse(adv.get("isError"))
        self.assertIn("WAIVED", adv["content"][0]["text"])
        self.assertFalse((self.root / "workspace" / "optional_report.txt").exists(),
                          "waive must satisfy the gate WITHOUT the underlying check ever becoming true")

    def test_spine_halt_block_and_resume(self):
        self.client.call("spine_lease", action="claim", claimed_by="tester")
        self.client.call("spine_start", task_id="g1")
        blocked = self.client.call("spine_halt", action="block", task_id="g1", blocker="waiting on something")
        self.assertFalse(blocked.get("isError"))
        self.assertIn("blocked", blocked["content"][0]["text"])
        resumed = self.client.call("spine_halt", action="resume", task_id="g1", reason="unblocked")
        self.assertFalse(resumed.get("isError"))
        self.assertIn("resumed", resumed["content"][0]["text"])

    def test_spine_evidence_missing_required_arg_is_a_clean_tool_error(self):
        result = self.client.call("spine_evidence", action="attest", task_id="g1")
        self.assertTrue(result.get("isError"))
        self.assertIn("condition_id", result["content"][0]["text"])

    def test_spine_halt_skip(self):
        """issue #559, N1: `skip` used to have no tool at all. g3 carries a
        waivable postcondition it never needs to satisfy -- skipping it proves
        the gate's own work is genuinely never done, not merely bypassed."""
        self.client.call("spine_lease", action="claim", claimed_by="tester")
        skipped = self.client.call("spine_halt", action="skip", task_id="g3", reason="OBE: superseded")
        self.assertFalse(skipped.get("isError"), skipped)
        self.assertIn("skipped", skipped["content"][0]["text"])
        state = json.loads(self.spine.read_text(encoding="utf-8"))
        self.assertEqual("skipped", state["tasks"]["g3"]["status"])
        self.assertEqual("OBE: superseded", state["tasks"]["g3"]["status_detail"]["reason"])

    def test_spine_halt_reopen(self):
        """issue #559, N1: `reopen` used to have no tool at all. Drives g1 to
        `complete` first (the only status `reopen` accepts), then reopens it
        and checks the REAL cascade side effect (rework_count incremented,
        status back to in-progress), not just a non-error reply."""
        self.client.call("spine_lease", action="claim", claimed_by="tester")
        self.client.call("spine_start", task_id="g1")
        (self.root / "workspace" / "notes.txt").write_text("hi\n", encoding="utf-8")
        self.client.call("spine_evidence", action="attest", task_id="g1", condition_id="c2",
                          which="postconditions")
        self.client.call("spine_advance", task_id="g1", mechanical=True)
        state = json.loads(self.spine.read_text(encoding="utf-8"))
        self.assertEqual("complete", state["tasks"]["g1"]["status"])

        reopened = self.client.call("spine_halt", action="reopen", task_id="g1", reason="rework needed")
        self.assertFalse(reopened.get("isError"), reopened)
        self.assertIn("g1", reopened["content"][0]["text"])
        state = json.loads(self.spine.read_text(encoding="utf-8"))
        self.assertEqual("in-progress", state["tasks"]["g1"]["status"])
        self.assertEqual(1, state["tasks"]["g1"]["rework_count"])

    def test_spine_halt_skip_and_reopen_missing_reason_is_a_clean_tool_error(self):
        skip_err = self.client.call("spine_halt", action="skip", task_id="g1")
        self.assertTrue(skip_err.get("isError"))
        self.assertIn("reason", skip_err["content"][0]["text"])
        reopen_err = self.client.call("spine_halt", action="reopen", task_id="g1")
        self.assertTrue(reopen_err.get("isError"))
        self.assertIn("reason", reopen_err["content"][0]["text"])

    def test_spine_capture_flag_candidate(self):
        """issue #559, N1: `flag-candidate` used to have no tool at all."""
        flagged = self.client.call("spine_capture", action="flag-candidate", **{"from": "g1"},
                                    statement="out-of-scope discovery for Triage")
        self.assertFalse(flagged.get("isError"), flagged)
        self.assertIn("flagged", flagged["content"][0]["text"])
        state = json.loads(self.spine.read_text(encoding="utf-8"))
        self.assertEqual(1, len(state["triage_candidates"]))
        self.assertEqual("g1", state["triage_candidates"][0]["from"])
        self.assertEqual("out-of-scope discovery for Triage", state["triage_candidates"][0]["statement"])

    def test_spine_amend_add_gate_and_delta_file_lands_beside_the_spine(self):
        """issue #559, N1: `amend` used to have no tool at all, and its input is
        a delta FILE the CLI parses -- this tool accepts the delta as a JSON
        object and must not re-derive its {"ops": [...]} grammar. Checks THREE
        things a prose claim could each get away with faking on its own: (1)
        the delta file genuinely lands beside the bound spine (SPINE.parent,
        per the human's ruling to use the per-task work folder, not a system
        temp dir), (2) its content is exactly the object this call sent, and
        (3) the engine genuinely applied it (a new pending gate exists)."""
        before_files = set(self.root.iterdir())
        delta = {"ops": [{"op": "add", "id": "g4", "title": "extra gate",
                           "imperative": "do one more thing",
                           "postconditions": [{"id": "c1", "statement": "done", "check": None}]}]}
        amended = self.client.call("spine_amend", delta=delta, reason="scope grew", authority="human")
        self.assertFalse(amended.get("isError"), amended)
        self.assertIn("added g4", amended["content"][0]["text"])

        new_files = set(self.root.iterdir()) - before_files
        delta_files = [p for p in new_files if p.name.startswith("mcp_amend_delta_")]
        self.assertEqual(1, len(delta_files), f"expected exactly one delta file beside the spine, found {new_files}")
        self.assertEqual(self.root, delta_files[0].parent,
                          "the delta file must land in the bound spine's own directory, not a temp dir")
        self.assertEqual(delta, json.loads(delta_files[0].read_text(encoding="utf-8")))

        state = json.loads(self.spine.read_text(encoding="utf-8"))
        self.assertIn("g4", state["tasks"])
        self.assertEqual("pending", state["tasks"]["g4"]["status"])
        self.assertEqual("extra gate", state["tasks"]["g4"]["title"])

    def test_spine_amend_missing_delta_is_a_clean_tool_error_not_an_engine_call(self):
        """`delta` is the one argument this tool cannot forward blank -- an
        empty/missing delta must never reach the engine as a real --delta file
        (that would silently create a zero-byte or `{}` artifact)."""
        result = self.client.call("spine_amend", reason="r", authority="human")
        self.assertTrue(result.get("isError"))
        self.assertIn("delta", result["content"][0]["text"])
        delta_files = [p for p in self.root.iterdir() if p.name.startswith("mcp_amend_delta_")]
        self.assertEqual([], delta_files,
                          "no delta file should be written when delta itself is missing")


class SurveyToolTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.survey = write_survey(self.root)
        self.client = McpRpcClient(self.survey, session_id="survey-test")

    def tearDown(self):
        self.client.close()
        self.tmp.cleanup()

    def test_record_and_consolidate(self):
        rec = self.client.call("spine_survey_result", action="record", task_id="r1", result="pass")
        self.assertFalse(rec.get("isError"))
        self.assertIn("recorded pass", rec["content"][0]["text"])
        cons = self.client.call("spine_survey_result", action="consolidate", verdict="APPROVE", summary="ok")
        self.assertFalse(cons.get("isError"))
        self.assertIn("verdict=APPROVE", cons["content"][0]["text"])

    def test_spine_capture_append(self):
        """issue #559, N1: `append` used to have no tool at all -- survey-only,
        so exercised against the survey fixture, not the gated one."""
        appended = self.client.call("spine_capture", action="append", task_id="r2",
                                     title="a new check", imperative="check something else")
        self.assertFalse(appended.get("isError"), appended)
        self.assertIn("appended r2", appended["content"][0]["text"])
        state = json.loads(self.survey.read_text(encoding="utf-8"))
        self.assertIn("r2", state["tasks"])
        self.assertIn("r2", state["items"])
        self.assertEqual("a new check", state["tasks"]["r2"]["title"])

    def test_spine_capture_append_on_gated_spine_is_the_engines_own_refusal(self):
        """`append` only applies to survey checklists -- this must be the
        ENGINE'S refusal riding through unchanged, never a door-invented one."""
        tmp = tempfile.TemporaryDirectory()
        try:
            root = Path(tmp.name)
            gated = write_gated_spine(root)
            client = McpRpcClient(gated, session_id="gated-append-test")
            try:
                result = client.call("spine_capture", action="append", task_id="g4",
                                      title="t", imperative="i")
                self.assertTrue(result.get("isError"))
                self.assertIn("append only on survey checklists", result["content"][0]["text"])
            finally:
                client.close()
        finally:
            tmp.cleanup()


class RefusalSurfacesAsIsErrorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.spine = write_gated_spine(self.root)
        self.client = McpRpcClient(self.spine, session_id="refusal-test")

    def tearDown(self):
        self.client.close()
        self.tmp.cleanup()

    def test_premature_advance_is_iserror_with_engine_text_verbatim(self):
        self.client.call("spine_lease", action="claim", claimed_by="tester")
        self.client.call("spine_start", task_id="g1")
        result = self.client.call("spine_advance", task_id="g1", mechanical=True)
        self.assertTrue(result["isError"])
        text = result["content"][0]["text"]
        self.assertIn("REFUSED", text)
        self.assertIn("postconditions unmet", text)
        self.assertIn("Recovery:", text)

        # The tool's refusal text must be exactly what the CLI would have
        # printed to stderr for the identical illegal call -- not a reworded
        # or summarized version. Same session id as the tool call (the lease
        # is already claimed by "refusal-test"): a mismatched id would refuse
        # for a DIFFERENT reason (wrong lease owner), not the one under test.
        cli = subprocess.run(
            [sys.executable, str(ENGINE), "--file", str(self.spine), "advance", "g1",
             "--mechanical", "--session-id", "refusal-test"],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertNotEqual(0, cli.returncode)
        self.assertIn("postconditions unmet", cli.stderr)
        self.assertIn("Recovery:", cli.stderr)


class McpJsonTests(unittest.TestCase):
    def test_mcp_json_exists_and_is_valid(self):
        self.assertTrue(MCP_JSON.is_file())
        config = json.loads(MCP_JSON.read_text(encoding="utf-8"))
        entry = config["mcpServers"]["spine"]
        self.assertIn("command", entry)
        self.assertIn("args", entry)
        self.assertIn("SPINE_FILE", entry["env"])
        self.assertIn("SPINE_ENGINE", entry["env"])

    def test_mcp_json_uses_portable_relative_paths(self):
        """Project-scope .mcp.json is committed to git; a machine-specific
        absolute path would break it on every other checkout."""
        config = json.loads(MCP_JSON.read_text(encoding="utf-8"))
        entry = config["mcpServers"]["spine"]
        for arg in entry["args"]:
            self.assertFalse(Path(arg).is_absolute(), f"args entry is not portable: {arg}")
        for key in ("SPINE_FILE", "SPINE_ENGINE"):
            value = entry["env"][key]
            self.assertFalse(Path(value).is_absolute(), f"{key} is not portable: {value}")

    #: The replacement invariant, named once so the guard and its own positive
    #: control cannot drift apart. Original: "the committed default resolves to
    #: a real, loadable spine." That guard caught this class of defect before --
    #: a `.mcp.json` default pointing at a file that was missing, unparseable,
    #: or not a spine at all -- and gate g3 (issue #603) removed the default it
    #: was written against, because an unbound session must get a REFUSAL rather
    #: than a demo spine's answers. Deleting the guard would have retired the
    #: protection along with the default. So it is conditional now, not gone:
    #: **if a default is present, it must resolve to a real, loadable spine.**
    #: A future default cannot be reintroduced broken.
    @staticmethod
    def _default_spine_problem(raw: str) -> str | None:
        """None when `raw` is an acceptable SPINE_FILE value, else what is wrong.

        Extracted from the test body so the test below can feed it values that
        SHOULD fail. A conditional guard whose condition is currently false is
        exactly the shape that rots into a vacuous pass, and the only defence is
        to keep exercising the branch that is not taken."""
        match = re.fullmatch(r"\$\{SPINE_FILE:-(?P<default>[^}]*)\}", raw)
        if match is None:
            return (f"SPINE_FILE must stay overridable per dispatch via "
                    f"${{SPINE_FILE:-<default>}} expansion; got {raw!r}")
        default = match.group("default").strip()
        if not default:
            return None  # no default: an unbound door refuses, which is the point
        spine_path = ROOT / default
        if not spine_path.is_file():
            return f"the default names a spine that is not there: {spine_path}"
        try:
            loaded = json.loads(spine_path.read_text(encoding="utf-8"))
        except ValueError as exc:
            return f"the default spine is not loadable JSON: {exc}"
        if not isinstance(loaded, dict) or "type" not in loaded:
            return f"the default spine has no 'type' -- it is not a spine: {spine_path}"
        return None

    def test_mcp_json_spine_file_is_overridable_and_any_default_loads(self):
        """SPINE_FILE stays written as `${SPINE_FILE:-<default>}` so a
        dispatcher can rebind it per agent through the calling process's
        environment -- a literal path here would bind one spine for every
        consumer and could not serve two agents driving different spines.

        The default itself is now EMPTY, deliberately. `${SPINE_FILE:-}`
        expands to an empty string, which `mcp_spine_server.py` treats as
        unbound and refuses on, so a session that set nothing is told nothing is
        bound instead of being handed a demo spine's answers as though they were
        its own. See `tests/test_mcp_door_unbound.py`."""
        config = json.loads(MCP_JSON.read_text(encoding="utf-8"))
        raw = config["mcpServers"]["spine"]["env"]["SPINE_FILE"]
        self.assertIsNone(self._default_spine_problem(raw))

    #: The invariant that #553/#575 exist for, and that a probing installer
    #: violated in the field: the committed `command` must name NO machine. It
    #: must stay overridable per machine (the `${VAR:-default}` form, measured
    #: to be expanded by Claude Code in `command`, not just in `env`), and its
    #: DEFAULT -- what a fresh clone that sets nothing actually launches -- must
    #: be a bare, portable interpreter name rather than a path probed on
    #: whoever's box last ran the installer. Same extracted-predicate shape as
    #: `_default_spine_problem` above, for the same reason: a guard needs a
    #: positive control or it rots into a vacuous pass.
    @staticmethod
    def _command_problem(raw: object) -> str | None:
        """None when `raw` is an acceptable committed `command`, else what is wrong."""
        installer = _installer()
        if not installer.is_mcp_var_command(raw):
            return (f"command must stay overridable per machine via "
                    f"${{{installer.MCP_INTERPRETER_ENV_VAR}:-<default>}} expansion; "
                    f"got {raw!r}")
        match = re.fullmatch(r"\$\{(?P<name>\w+)(?::-(?P<default>[^}]*))?\}", raw)
        if match.group("name") != installer.MCP_INTERPRETER_ENV_VAR:
            return (f"command overrides via {match.group('name')!r}, but the documented "
                    f"knob is {installer.MCP_INTERPRETER_ENV_VAR!r}")
        # What a fresh clone launches when it sets nothing.
        default = installer.expand_mcp_var(raw, {})
        if not default:
            return "the default is empty, so a clone that sets nothing launches nothing"
        if "/" in default or "\\" in default:
            return (f"the default is a machine-specific PATH ({default!r}) -- a tracked "
                    f"file must not name one machine's interpreter")
        if default not in installer.MCP_REWRITABLE_BARE_NAMES:
            return (f"the default {default!r} is not a known portable interpreter name "
                    f"({sorted(installer.MCP_REWRITABLE_BARE_NAMES)})")
        return None

    def test_mcp_json_command_names_no_machine(self):
        config = json.loads(MCP_JSON.read_text(encoding="utf-8"))
        raw = config["mcpServers"]["spine"]["command"]
        self.assertIsNone(self._command_problem(raw))

    def test_the_command_guard_still_catches_a_machine_specific_command(self):
        """The positive control. Each entry is a way this has actually gone
        wrong or could: the literal that broke Windows (#553), the probed value
        an installer wrote into the tracked file, and the placeholder."""
        for raw, why in [
            ("python3", "a bare literal -- no per-machine override, and dead on Windows"),
            ("py", "the other bare literal, dead on stock POSIX"),
            ("/home/tommy/.local/bin/py", "a probed absolute path from one operator's box"),
            ("<python-interpreter>", "the placeholder -- not launchable as committed"),
            ("${CONSTELLATION_PYTHON:-}", "no default: a fresh clone launches nothing"),
            ("${CONSTELLATION_PYTHON:-/usr/bin/python3}", "a path as the default"),
            ("${SOME_OTHER_VAR:-python3}", "overridable, but not via the documented knob"),
        ]:
            with self.subTest(why=why):
                self.assertIsNotNone(
                    self._command_problem(raw),
                    f"the guard accepted {raw!r} -- it no longer catches {why}")

    def test_the_command_guard_accepts_the_portable_windows_answer(self):
        """Not just a refusal machine: the form a Windows operator is told to
        use must PASS, or the guidance and the guard disagree."""
        self.assertIsNone(self._command_problem("${CONSTELLATION_PYTHON:-py}"))

    def test_the_default_spine_guard_still_catches_a_broken_default(self):
        """The positive control the conditional above needs to be worth
        anything. Each of these is a way the ORIGINAL guard earned its keep, and
        each must still be caught the moment a default reappears."""
        for raw, why in [
            ("examples/mcp-interactive-demo/does-not-exist.json", "not the ${VAR:-} form at all"),
            ("${SPINE_FILE:-examples/no-such-spine.json}", "a default that is not there"),
            ("${SPINE_FILE:-README.md}", "a default that is not loadable JSON"),
            ("${SPINE_FILE:-.mcp.json}", "a JSON file that is not a spine"),
        ]:
            with self.subTest(why=why):
                self.assertIsNotNone(
                    self._default_spine_problem(raw),
                    f"the guard accepted {raw!r} -- it no longer catches {why}")


class McpJsonVarExpansionLaunchTests(unittest.TestCase):
    """End-to-end replacement for the old generated-config test: per-dispatch
    identity now ships via the committed `.mcp.json` plus `${VAR}` expansion
    from the caller's environment (M1, g1 rework handoff), not a generated
    file. Launches the server EXACTLY as `.mcp.json` specifies (its own
    `command` + `args`, resolved relative to the repo root the way a real
    `claude -p` dispatch resolves them) with SPINE_FILE/SPINE_ENGINE/
    SPINE_SESSION set directly in the caller's environment -- the shell
    `${VAR:-default}` expansion applied by hand, since Python does not
    perform it, matching what a real dispatching shell does before exec'ing
    the command. Also carries over the one substantive assertion the old
    `GenMcpConfigTests` made about the server itself (not about the deleted
    generator): SPINE_SESSION is composed by the CALLER as `session_id#
    agent_id` and the server treats the whole string as opaque -- no
    parsing, no validation -- so it must reach the engine, '#' and all,
    verbatim."""

    def test_var_expansion_path_launches_a_real_server_and_answers_a_tool_call(self):
        config = json.loads(MCP_JSON.read_text(encoding="utf-8"))
        entry = config["mcpServers"]["spine"]
        # `command` is now `${CONSTELLATION_PYTHON:-python3}` and gets the SAME
        # hand-applied expansion this test already applies to the env values --
        # Python does not expand, and a real dispatch resolves the command
        # through the harness before exec. Treating `env` as expandable while
        # treating `command` as literal was the asymmetry that hid the question
        # of whether expansion reaches `command` at all (it does; measured, see
        # install_constellation.MCP_INTERPRETER_ENV_VAR).
        command = _installer().expand_mcp_var(entry["command"], os.environ)
        self.assertTrue(command, f"command expanded to nothing: {entry['command']!r}")
        tmp = tempfile.TemporaryDirectory()
        try:
            root = Path(tmp.name)
            spine = write_gated_spine(root)
            env = dict(os.environ)
            # The caller-set overrides ${SPINE_FILE:-...} / ${SPINE_SESSION:-...}
            # expand to -- exactly the seam a real dispatch uses. The
            # 'session_id#agent_id' composition is a caller-side convention;
            # nothing in this repo composes or validates it anymore.
            env["SPINE_FILE"] = str(spine)
            env["SPINE_ENGINE"] = str(ENGINE)
            env["SPINE_SESSION"] = "varexp-sess#varexp-agent"
            env["SPINE_CALLLOG"] = str(root / "mcp_calls.jsonl")
            env["SPINE_START_MARKER"] = str(root / "mcp_server_started")
            proc = subprocess.Popen(
                [command, *entry["args"]],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, encoding="utf-8", bufsize=1, env=env, cwd=str(ROOT),
            )
            try:
                proc.stdin.write(json.dumps({
                    "jsonrpc": "2.0", "id": 1, "method": "tools/call",
                    "params": {"name": "spine_lease",
                               "arguments": {"action": "claim", "claimed_by": "varexp-tester"}},
                }) + "\n")
                proc.stdin.flush()
                claim_line = proc.stdout.readline()
                if not claim_line:
                    # NOTE: read stderr only on the failure path -- proc.stderr.read()
                    # blocks until EOF, and the child (still alive, stdin open) never
                    # closes it on the success path. An eager f-string message on a
                    # eager assertion would evaluate unconditionally and deadlock here.
                    self.fail(f"no reply to claim; stderr={proc.stderr.read()}")
                claim_reply = json.loads(claim_line)
                self.assertFalse(claim_reply["result"]["isError"], claim_reply)

                proc.stdin.write(json.dumps({
                    "jsonrpc": "2.0", "id": 2, "method": "tools/call",
                    "params": {"name": "spine_status", "arguments": {}},
                }) + "\n")
                proc.stdin.flush()
                status_line = proc.stdout.readline()
                if not status_line:
                    self.fail(f"no reply to status; stderr={proc.stderr.read()}")
                status_reply = json.loads(status_line)
                text = status_reply["result"]["content"][0]["text"]
                self.assertIn("ACTIVE g1", text)
                self.assertIn(
                    "LEASE HELD: varexp-sess#varexp-agent (by varexp-tester", text,
                    "SPINE_SESSION must reach the engine verbatim, opaque '#' and all -- "
                    "the server does no parsing/validation of the caller-composed identity",
                )
            finally:
                proc.stdin.close()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
        finally:
            tmp.cleanup()


class AllEighteenVerbsCoveredTests(unittest.TestCase):
    """The completeness claim `scripts/mcp_spine_server.py`'s own docstring now
    makes ('18 of 18 verbs covered'), pinned against the door's REAL, live
    `tools/list` -- not the docstring text, which is prose and can drift.
    issue #559 (N1): `skip`, `reopen`, `append`, `amend` and `flag-candidate`
    used to have no tool at all and stayed CLI-only; this is what replaces the
    old `CliFallbackTableTests` (there is no CLI-fallback table any more)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.spine = write_gated_spine(self.root)
        self.client = McpRpcClient(self.spine, session_id="coverage-test")

    def tearDown(self):
        self.client.close()
        self.tmp.cleanup()

    def test_every_engine_verb_maps_to_a_tool_the_live_door_actually_advertises(self):
        tools = self.client.rpc("tools/list")["result"]["tools"]
        # The lifecycle tools never call run_engine and so cover no engine verb
        # by design (see mcp_spine_server.py's module docstring, "The lifecycle
        # door") -- excluded here the same way tests/test_mcp_identity.py's
        # runtime sweep scopes itself off LIFECYCLE_TOOL_NAMES, so this stays a
        # completeness claim about the 9 engine tools, not a claim that a
        # lifecycle tool must map to a verb.
        advertised = {t["name"] for t in tools} - LIFECYCLE_TOOLS_COVER_NO_VERB
        self.assertEqual(
            18, len(VERB_TO_TOOL),
            "VERB_TO_TOOL must name all 18 engine verbs, or this test is vacuous",
        )
        for verb, tool_name in VERB_TO_TOOL.items():
            self.assertIn(
                tool_name, advertised,
                f"verb {verb!r} is mapped to {tool_name!r}, which the live door does not advertise",
            )
        self.assertEqual(
            set(VERB_TO_TOOL.values()), advertised,
            "every advertised tool must cover at least one verb, and vice versa",
        )


class Utf8StdioConformanceTests(unittest.TestCase):
    """Byte-level, platform-independent regression coverage for the door's
    OWN stdio encoding (issue #424 post-archive fix, workstream F gate
    g3fix2). On Windows, Python's stdio defaults to the ANSI code page
    (cp1252), not UTF-8, unless a stream explicitly reconfigures itself --
    exactly the trap scripts/checklist_engine.py's own `_utf8_stdio()`
    already names for the CLI's stdout/stderr. `mcp_spine_server.py`
    additionally owns `sys.stdin` (the CLI never reads stdin; this door
    does), so it must pin its own encoding rather than inherit the platform
    default.

    Cannot run Windows here, so this simulates the hazard portably: it
    forces `PYTHONIOENCODING=cp1252` in the SERVER's own environment before
    spawning it -- the standard, documented, cross-platform way to force
    CPython's stdio streams to a non-UTF-8 default, reproducing exactly what
    an unconfigured stdin defaults to on a Windows box, without needing
    Windows itself.

    It talks to the server over RAW binary pipes and builds the request
    line itself with `json.dumps(..., ensure_ascii=False)` -- genuine
    multi-byte UTF-8 bytes on the wire, the shape a real (non-Python) MCP
    client actually sends (e.g. a JS/TS host, whose `JSON.stringify` does
    NOT ASCII-escape). This repo's own `McpRpcClient`/`ServerInstance`
    always call the bare `json.dumps()` default (`ensure_ascii=True`), which
    ASCII-escapes every non-ASCII character into a `\\uXXXX` sequence before
    it ever reaches a pipe -- immune to a codec mismatch by construction, so
    those two convenience clients could never exercise this path, which is
    exactly the kind of Linux-only accidental green the whole gate exists to
    catch. This test bypasses that convenience deliberately.

    The load-bearing assertion compares `.encode('utf-8')` byte strings, not
    plain string equality -- showing the actual bytes that crossed the wire,
    per the handoff's evidence bar, not merely that a comparison passed."""

    def _spawn(self, env_overrides: dict) -> subprocess.Popen:
        tmp = tempfile.TemporaryDirectory()
        self._tmp = tmp  # kept alive until the caller's finally cleans it up
        root = Path(tmp.name)
        spine = write_gated_spine(root)
        env = {"PATH": os.environ.get("PATH", "")}
        env["SPINE_FILE"] = str(spine)
        env["SPINE_ENGINE"] = str(ENGINE)
        env["SPINE_SESSION"] = "utf8-conformance-session"
        env["SPINE_CALLLOG"] = str(root / "mcp_calls.jsonl")
        env["SPINE_START_MARKER"] = str(root / "mcp_server_started")
        env.update(env_overrides)
        # Binary pipes, deliberately -- this test controls the encoding on
        # BOTH ends by hand instead of delegating to Popen's text-mode
        # convenience (the very convenience that hides this bug on Linux).
        proc = subprocess.Popen(
            [sys.executable, str(SERVER)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=env,
        )
        # Bounded read via a daemon reader thread + Queue, NEVER a naked
        # blocking proc.stdout.readline() -- that anti-pattern is exactly
        # what deadlocked tests/test_mcp_identity.py's own suite once
        # already (see that file's ServerInstance docstring); a raw
        # readline() against this exact server, under a forced non-UTF-8
        # PYTHONIOENCODING, was observed to hang indefinitely while writing
        # this test, which is what led to this bounded form.
        self._out_q: "queue.Queue[object]" = queue.Queue()
        self._EOF = object()

        def _read_loop() -> None:
            try:
                while True:
                    line = proc.stdout.readline()
                    if not line:
                        break
                    self._out_q.put(line)
            except (OSError, ValueError):
                pass
            self._out_q.put(self._EOF)

        threading.Thread(target=_read_loop, daemon=True).start()
        return proc

    def _recv(self, timeout: float = 15.0) -> bytes | None:
        try:
            item = self._out_q.get(timeout=timeout)
        except queue.Empty:
            return None
        if item is self._EOF:
            self._out_q.put(self._EOF)  # sticky, mirroring ServerInstance.recv()
            return None
        return item

    def _round_trip_claimed_by(self, proc: subprocess.Popen, non_ascii: str) -> bytes:
        """Claim the lease with a non-ASCII `claimed_by` sent as RAW UTF-8
        bytes (ensure_ascii=False), then read it back through a REAL
        `spine_status` ("current") call and pull the substring out of the
        rendered `LEASE HELD: <id> (by <claimed_by>, last heartbeat ... ago)`
        line -- asserted against rendered behaviour, never against the raw
        argument merely echoed. Returns the round-tripped substring's own
        UTF-8 encoding, for a byte-for-byte comparison by the caller."""
        claim_req = {
            "jsonrpc": "2.0", "id": 1, "method": "tools/call",
            "params": {"name": "spine_lease",
                       "arguments": {"action": "claim", "claimed_by": non_ascii}},
        }
        raw_request = (json.dumps(claim_req, ensure_ascii=False) + "\n").encode("utf-8")
        proc.stdin.write(raw_request)
        proc.stdin.flush()
        claim_reply_line = self._recv()
        if claim_reply_line is None:
            # NOTE: read stderr only on the failure path -- proc.stderr.read()
            # blocks until EOF, and the child (still alive, stdin open) never
            # closes it on the success path. An eager f-string message on an
            # eager assertion would evaluate unconditionally and deadlock here
            # (see McpJsonVarExpansionLaunchTests above for the same note).
            self.fail(f"no reply to claim; stderr={proc.stderr.read()!r}")
        claim_reply = json.loads(claim_reply_line.decode("utf-8"))
        self.assertFalse(claim_reply["result"]["isError"], claim_reply)

        status_req = {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                      "params": {"name": "spine_status", "arguments": {}}}
        proc.stdin.write((json.dumps(status_req) + "\n").encode("utf-8"))
        proc.stdin.flush()
        status_reply_line = self._recv()
        if status_reply_line is None:
            self.fail(f"no reply to status; stderr={proc.stderr.read()!r}")
        status_reply = json.loads(status_reply_line.decode("utf-8"))
        text = status_reply["result"]["content"][0]["text"]

        match = re.search(r"\(by (.*?), last heartbeat", text)
        self.assertIsNotNone(match, f"no 'LEASE HELD: ... (by <claimed_by>, last heartbeat ...)' line found in: {text!r}")
        return match.group(1).encode("utf-8")

    def test_claimed_by_round_trips_byte_for_byte_even_with_a_non_utf8_ambient_default(self):
        """GREEN with the fix: the explicit reconfigure() in
        scripts/mcp_spine_server.py overrides PYTHONIOENCODING=cp1252 (the
        portable stand-in for an unconfigured Windows default), so a real
        non-ASCII claimed_by round-trips correctly regardless of the
        ambient default."""
        non_ascii = "tester—café"  # em dash (U+2014) + e-acute (U+00E9)
        expected_bytes = non_ascii.encode("utf-8")

        proc = self._spawn({"PYTHONIOENCODING": "cp1252"})
        try:
            round_tripped_bytes = self._round_trip_claimed_by(proc, non_ascii)
            self.assertEqual(
                expected_bytes, round_tripped_bytes,
                f"non-ASCII claimed_by did not round-trip byte-for-byte through the "
                f"server's own stdin decode: sent {expected_bytes!r}, got back "
                f"{round_tripped_bytes!r} (decoded: {round_tripped_bytes.decode('utf-8', 'replace')!r})"
            )
        finally:
            proc.stdin.close()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
            self._tmp.cleanup()


if __name__ == "__main__":
    unittest.main()
