"""DC2 (separation) and DC3 (inheritance fails closed) acceptance tests for
the MCP front door (issue #424, workstream F, gate g3).

DC2 — a parent and a subagent drive two different spines at once, each
through its own server instance; leases never collide and each status call
returns its own reading.

DC3 — a subagent dispatched with no special configuration gets a refusal or
no identity, never the parent's lease or the parent's reading.

Both are proven by spawning REAL `scripts/mcp_spine_server.py` subprocesses
and driving them over real newline-delimited JSON-RPC, the same way
`tests/test_mcp_spine_server.py` does -- per doctrine (`global-crew.md`),
generated advice/recovery text is executed and asserted against, never
string-matched around; a wrapper is verified by actually calling through it.

Mechanism disambiguation, kept explicit (do not conflate these two facts):

  - DC3 is about THE DOOR: `mcp_spine_server.py` binds its ambient state
    (SPINE_FILE, SPINE_ENGINE, SPINE_SESSION) from the environment at
    server-launch time -- the module's own docstring calls this "the seam
    identity rides on". DC3 asks whether a subagent given no special
    configuration can reach a server bound to that seam through the
    PARENT's own values.
  - It is a SEPARATE, CLI/engine-lease fact that two different callers can
    pass the identical free-text `--session-id` string to `checklist_engine
    claim` (a convention at the argument-passing layer, e.g. two crews in one
    Commander run sharing one nominal session identity). That is not this
    door leaking; it is a different mechanism entirely, and this file must
    never manufacture or "fix" it to make a test here pass.
"""

from __future__ import annotations

import json
import os
import queue
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "scripts" / "mcp_spine_server.py"
ENGINE = ROOT / "scripts" / "checklist_engine.py"

# Env vars mcp_spine_server.py reads at import time -- the whole identity seam.
SPINE_ENV_KEYS = ("SPINE_FILE", "SPINE_ENGINE", "SPINE_SESSION", "SPINE_CALLLOG", "SPINE_START_MARKER")


def write_marked_spine(root: Path, marker: str, work_id: str) -> Path:
    """A one-gate gated spine whose g1 imperative embeds `marker` -- the
    distinguishing text a spine_status call must surface. Content-based, not
    just path-based: proves the two servers are reading genuinely different
    state, not merely running as two different OS processes."""
    root.mkdir(parents=True, exist_ok=True)
    spine = {
        "work_id": work_id,
        "type": "gated",
        "config": {"rework_cap": 99},
        "items": ["g1"],
        "consolidation": None,
        "triage_candidates": [],
        "blockers": [],
        "tasks": {
            "g1": {
                "id": "g1", "title": "marker gate", "imperative": f"MARKER::{marker}",
                "preconditions": [],
                "postconditions": [{"id": "c1", "statement": "done", "check": None, "satisfied": False}],
                "constraints": [], "directives": None, "child_checklist": None,
                "status": "pending", "status_detail": {}, "result": None,
                "finding": None, "evidence": [], "rework_count": 0,
            },
        },
    }
    path = root / "spine.json"
    path.write_text(json.dumps(spine, indent=2), encoding="utf-8")
    return path


class ServerInstance:
    """One real mcp_spine_server.py subprocess, bound to its identity purely
    through the environment -- the same seam the committed `.mcp.json`'s
    `${VAR}` expansion binds from the caller's own environment. Not a mock:
    real subprocess, real newline-delimited JSON-RPC 2.0 over stdio.

    `base_env`, when given, REPLACES the inherited environment outright
    (mirrors `subprocess.Popen(env=...)` semantics exactly) -- used by the
    DC3 tests to control precisely what a "subagent with no special
    configuration" does or does not inherit. When omitted, the current
    process's environment is inherited (Popen's own default), with any
    stray SPINE_* left over from a previous instance in this same test
    process stripped first, then this instance's own three set.
    """

    def __init__(self, spine_file: Path | None, session_id: str | None, base_dir: Path,
                 engine: Path = ENGINE, server: Path = SERVER,
                 base_env: dict | None = None, extra_env: dict | None = None):
        if base_env is None:
            env = dict(os.environ)
            for k in SPINE_ENV_KEYS:
                env.pop(k, None)
            if spine_file is not None:
                env["SPINE_FILE"] = str(spine_file)
            env["SPINE_ENGINE"] = str(engine)
            if session_id is not None:
                env["SPINE_SESSION"] = session_id
            env["SPINE_CALLLOG"] = str(base_dir / "mcp_calls.jsonl")
            env["SPINE_START_MARKER"] = str(base_dir / "mcp_server_started")
        else:
            env = dict(base_env)
        if extra_env:
            env.update(extra_env)
        self.env = env
        self.proc = subprocess.Popen(
            [sys.executable, str(server)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            # Explicit UTF-8: the door's own protocol encoding is pinned in
            # scripts/mcp_spine_server.py (Windows/cp1252 hazard); decode the
            # child's pipes explicitly here too, so a future regression in
            # the door surfaces as a decode mismatch instead of being masked
            # by a matching platform default on Linux/CI.
            text=True, encoding="utf-8", bufsize=1, env=env,
        )
        self._id = 0
        # Portable bounded read (see recv() below): a daemon thread owns the
        # blocking readline() loop and hands lines to the main thread over a
        # Queue, whose own timeout= is the cross-platform bound. This exists
        # ONLY because select.select() on a pipe/file object is POSIX-only --
        # on Windows select() accepts sockets exclusively, so the previous
        # select.select([self.proc.stdout], ...) form raised WinError 10038
        # at the first call in every test in this file under Windows CI. The
        # thread itself never blocks anything the main thread does: the main
        # thread's only wait is the bounded queue.get(timeout=...) in recv().
        self._out_q: "queue.Queue[object]" = queue.Queue()
        self._EOF = object()  # sentinel identity, can never collide with a real line
        self._reader = threading.Thread(target=self._read_loop, daemon=True)
        self._reader.start()

    def _read_loop(self) -> None:
        """Runs on the daemon reader thread for the life of the process.
        Pumps whole lines onto self._out_q. On EOF (dead process, process
        that never started, or the pipe closing) or any read error, it puts
        the EOF sentinel and returns -- and recv() puts that sentinel BACK
        after consuming it, so every recv() call after the process is gone
        returns None promptly instead of waiting out the full timeout again."""
        stdout = self.proc.stdout
        if stdout is None:
            self._out_q.put(self._EOF)
            return
        try:
            while True:
                line = stdout.readline()
                if not line:
                    break
                self._out_q.put(line)
        except (OSError, ValueError):
            pass
        self._out_q.put(self._EOF)

    def send(self, method: str, params: dict | None = None) -> int | None:
        """Write one JSON-RPC request and return its id WITHOUT reading a
        reply -- the low-level primitive the concurrency tests use to get two
        requests genuinely in flight (write, write, THEN read, read) instead
        of write-read, write-read. Returns None if the write itself fails
        (dead process / broken pipe)."""
        self._id += 1
        req = {"jsonrpc": "2.0", "id": self._id, "method": method, "params": params or {}}
        try:
            self.proc.stdin.write(json.dumps(req) + "\n")
            self.proc.stdin.flush()
        except (BrokenPipeError, ValueError, OSError):
            return None
        return self._id

    def recv(self, timeout: float = 15.0) -> dict | None:
        """Bounded read: None on any failure to reply (dead process, a
        process that never started, a broken pipe, or a read that would
        block past `timeout`) -- NEVER an unbounded blocking read, which is
        exactly the footgun g1 hit (a blocking pipe read evaluated
        unconditionally inside an eager assertion message deadlocked that
        suite). The bound is queue.get(timeout=...) against the reader
        thread's queue, not select.select() -- portable, because it never
        touches select() on a pipe/file object (POSIX-only; Windows'
        select() accepts sockets only)."""
        if self.proc.stdout is None:
            return None
        try:
            item = self._out_q.get(timeout=timeout)
        except queue.Empty:
            return None
        if item is self._EOF:
            self._out_q.put(self._EOF)  # sticky: next recv() also returns None promptly
            return None
        try:
            return json.loads(item)
        except ValueError:
            return None

    def rpc(self, method: str, params: dict | None = None, timeout: float = 15.0) -> dict | None:
        if self.send(method, params) is None:
            return None
        return self.recv(timeout=timeout)

    def call(self, name: str, timeout: float = 15.0, **args) -> dict | None:
        r = self.rpc("tools/call", {"name": name, "arguments": args}, timeout=timeout)
        if r is None or "error" in r:
            return None
        return r["result"]

    def status_text(self, timeout: float = 15.0) -> str | None:
        r = self.call("spine_status", timeout=timeout)
        if r is None:
            return None
        return r["content"][0]["text"]

    def close(self) -> None:
        try:
            self.proc.stdin.close()
        except (BrokenPipeError, ValueError, OSError):
            pass
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait(timeout=5)
        # Reader thread is daemon=True (never blocks interpreter exit even if
        # left running), but join it with a bound here anyway for hygiene --
        # the process is dead by this point so stdout.readline() should
        # already have hit EOF and the thread should already be finishing.
        self._reader.join(timeout=5)


# --------------------------------------------------------------------------- #
# DC2 — separation
# --------------------------------------------------------------------------- #
class DC2SeparateReadingsTests(unittest.TestCase):
    """Baseline: two server instances, two different spine files, each
    returns its own reading. Concurrency and the collision-detectability
    control are the next test class."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.spine_a = write_marked_spine(self.root / "a", "SPINE-A-MARK", "dc2-work-a")
        self.spine_b = write_marked_spine(self.root / "b", "SPINE-B-MARK", "dc2-work-b")
        self.inst_a = ServerInstance(self.spine_a, "dc2-sess-a", self.root / "a")
        self.inst_b = ServerInstance(self.spine_b, "dc2-sess-b", self.root / "b")

    def tearDown(self):
        self.inst_a.close()
        self.inst_b.close()
        self.tmp.cleanup()

    def test_each_instance_returns_its_own_gate_reading(self):
        text_a = self.inst_a.status_text()
        text_b = self.inst_b.status_text()
        self.assertIsNotNone(text_a, "instance A produced no reply")
        self.assertIsNotNone(text_b, "instance B produced no reply")
        self.assertIn("SPINE-A-MARK", text_a)
        self.assertNotIn("SPINE-B-MARK", text_a)
        self.assertIn("SPINE-B-MARK", text_b)
        self.assertNotIn("SPINE-A-MARK", text_b)

    def test_claiming_a_lease_through_one_instance_never_appears_on_the_other(self):
        claimed = self.inst_a.call("spine_lease", action="claim", claimed_by="agent-A")
        self.assertIsNotNone(claimed)
        self.assertFalse(claimed.get("isError"))

        text_a = self.inst_a.status_text()
        text_b = self.inst_b.status_text()
        self.assertIn("LEASE active: dc2-sess-a (by agent-A", text_a)
        self.assertNotIn("LEASE active", text_b, "instance B's own reading must not show A's lease")

        # Corroborate against the underlying files directly, not just the
        # server's own text projection.
        a_state = json.loads(self.spine_a.read_text(encoding="utf-8"))
        b_state = json.loads(self.spine_b.read_text(encoding="utf-8"))
        self.assertEqual("dc2-sess-a", a_state["engine_session"]["session_id"])
        self.assertEqual("agent-A", a_state["engine_session"]["claimed_by"])
        self.assertNotIn("engine_session", b_state, "spine B's file must carry no lease at all")


class DC2ConcurrencyAndCollisionControlTests(unittest.TestCase):
    """Genuine concurrency between the two instances, plus the
    collision-detectability control the handoff demands: a scenario that
    could actually have been caught had leases leaked."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_interleaved_in_flight_requests_never_cross(self):
        """25 rounds of write-write-read-read (send to BOTH instances before
        reading EITHER reply back), alternating which instance goes first
        each round. Both requests are genuinely in flight in their own OS
        process at once -- not a sequential call-then-wait pattern, which a
        write-read, write-read loop would actually be even with two
        processes involved."""
        spine_a = write_marked_spine(self.root / "a", "IL-A", "il-a")
        spine_b = write_marked_spine(self.root / "b", "IL-B", "il-b")
        inst_a = ServerInstance(spine_a, "il-sess-a", self.root / "a")
        inst_b = ServerInstance(spine_b, "il-sess-b", self.root / "b")
        try:
            for i in range(25):
                first, first_mark = (inst_a, "IL-A") if i % 2 == 0 else (inst_b, "IL-B")
                second, second_mark = (inst_b, "IL-B") if i % 2 == 0 else (inst_a, "IL-A")

                self.assertIsNotNone(first.send("tools/call", {"name": "spine_status", "arguments": {}}),
                                      f"round {i}: write to first instance failed")
                self.assertIsNotNone(second.send("tools/call", {"name": "spine_status", "arguments": {}}),
                                      f"round {i}: write to second instance failed")

                reply1 = first.recv(timeout=10)
                reply2 = second.recv(timeout=10)
                self.assertIsNotNone(reply1, f"round {i}: first instance produced no reply in time")
                self.assertIsNotNone(reply2, f"round {i}: second instance produced no reply in time")

                text1 = reply1["result"]["content"][0]["text"]
                text2 = reply2["result"]["content"][0]["text"]
                self.assertIn(first_mark, text1, f"round {i}: first instance's reply carried the wrong marker")
                self.assertIn(second_mark, text2, f"round {i}: second instance's reply carried the wrong marker")
        finally:
            inst_a.close()
            inst_b.close()

    def test_overlapping_execution_windows_via_threads(self):
        """Two real threads, released at the same instant by a Barrier, each
        driving its own server instance through a burst of calls; record
        wall-clock start/end per thread and assert the windows genuinely
        overlapped -- not merely that both instances existed at some point,
        but that their processing windows actually intersected in time."""
        spine_a = write_marked_spine(self.root / "a", "OV-A", "ov-a")
        spine_b = write_marked_spine(self.root / "b", "OV-B", "ov-b")
        inst_a = ServerInstance(spine_a, "ov-sess-a", self.root / "a")
        inst_b = ServerInstance(spine_b, "ov-sess-b", self.root / "b")
        barrier = threading.Barrier(2)
        windows: dict[str, tuple[float, float]] = {}
        errors: dict[str, str] = {}

        def worker(key: str, inst: ServerInstance, expect: str) -> None:
            try:
                barrier.wait(timeout=10)
                t0 = time.monotonic()
                for _ in range(40):
                    text = inst.status_text()
                    if text is None or expect not in text:
                        errors[key] = f"bad reading {text!r}"
                        return
                windows[key] = (t0, time.monotonic())
            except Exception as exc:  # noqa: BLE001 - surface into the assertion below
                errors[key] = repr(exc)

        try:
            ta = threading.Thread(target=worker, args=("A", inst_a, "OV-A"))
            tb = threading.Thread(target=worker, args=("B", inst_b, "OV-B"))
            ta.start()
            tb.start()
            ta.join(timeout=30)
            tb.join(timeout=30)
            self.assertFalse(ta.is_alive() or tb.is_alive(), "a worker thread did not finish in time")
            self.assertEqual({}, errors)
            self.assertIn("A", windows)
            self.assertIn("B", windows)
            start_a, end_a = windows["A"]
            start_b, end_b = windows["B"]
            overlap = max(start_a, start_b) < min(end_a, end_b)
            self.assertTrue(
                overlap,
                f"execution windows did not overlap: A={windows['A']} B={windows['B']} "
                f"-- the two instances ran sequentially, not concurrently",
            )
        finally:
            inst_a.close()
            inst_b.close()

    def test_collision_would_have_been_caught_if_the_two_instances_shared_one_file(self):
        """The handoff's own bar: 'the collision scenario must be one that
        could actually have been caught had leases leaked -- say how you
        know that.' Demonstrated, not argued: point TWO SEPARATE server
        processes at the SAME spine file (what a real DC2 leak would look
        like -- lease state lives in the file, not in either process's
        memory) and show a lease claimed through one IS visible through the
        other (RED -- collision reproduces). The immediate contrast, same
        shape but genuinely separate files, shows no such cross-visibility
        (GREEN) -- proving the assertions elsewhere in this class are not
        vacuously true; a leak WOULD have been caught by them."""
        shared_spine = write_marked_spine(self.root / "shared", "SHARED-MARK", "shared-work")
        proc1 = ServerInstance(shared_spine, "collide-parent-session", self.root / "shared")
        proc2 = ServerInstance(shared_spine, "collide-subagent-session", self.root / "shared")
        try:
            claimed = proc1.call("spine_lease", action="claim", claimed_by="via-proc1")
            self.assertIsNotNone(claimed)
            self.assertFalse(claimed.get("isError"))

            # RED: proc2 is a DIFFERENT process, with a DIFFERENT SPINE_SESSION,
            # yet its own reading shows proc1's lease verbatim, because both are
            # bound to the same file.
            text_via_proc2 = proc2.status_text()
            self.assertIsNotNone(text_via_proc2)
            self.assertIn(
                "LEASE active: collide-parent-session (by via-proc1", text_via_proc2,
                "collision did not reproduce on a genuinely shared spine file -- "
                "this control is not sensitive enough to have caught a real DC2 leak",
            )
        finally:
            proc1.close()
            proc2.close()

        # GREEN, immediately after, identical shape -- only the file differs.
        spine_a = write_marked_spine(self.root / "contrast-a", "CONTRAST-A", "contrast-a")
        spine_b = write_marked_spine(self.root / "contrast-b", "CONTRAST-B", "contrast-b")
        inst_a = ServerInstance(spine_a, "contrast-sess-a", self.root / "contrast-a")
        inst_b = ServerInstance(spine_b, "contrast-sess-b", self.root / "contrast-b")
        try:
            claimed = inst_a.call("spine_lease", action="claim", claimed_by="via-a")
            self.assertIsNotNone(claimed)
            self.assertFalse(claimed.get("isError"))
            text_b = inst_b.status_text()
            self.assertIsNotNone(text_b)
            self.assertNotIn("LEASE active", text_b,
                              "genuinely separate spine files must show no cross-visibility")
        finally:
            inst_a.close()
            inst_b.close()


def assert_door_is_up_and_serving(case: unittest.TestCase, instance: ServerInstance, expect_substring: str) -> None:
    """The DC3 positive control. 'A refusal or no identity' is also exactly
    what a totally-non-installed door produces -- the server never started,
    the config never delivered, the door absent entirely. So before ANY
    no-identity result from a DIFFERENT probe is allowed to count as DC3
    passing closed, this control must independently prove the door is
    genuinely up and answering REAL engine output. It raises AssertionError
    -- an ordinary, unittest-integrated failure, not a print statement or a
    comment -- so it sits IN the assertion path of every DC3 test that calls
    it, not decorative prose beside them."""
    text = instance.status_text(timeout=10)
    case.assertIsNotNone(text, "DC3 positive control: the door produced no reply at all -- it is not up")
    case.assertIn(
        expect_substring, text,
        f"DC3 positive control: the door replied but not with the expected content {expect_substring!r} "
        f"(got {text!r}) -- it is up but not serving what this test thinks it is",
    )


class DC3PositiveControlTests(unittest.TestCase):
    """The positive control itself, proven capable of failing (RED) before
    it is trusted to gate the DC3 no-identity claim (GREEN) in the next test
    class. Same bar gate g2 sets for its own property check: demonstrate the
    red state, not just claim the check can fail."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_control_is_red_when_the_server_never_started(self):
        """Manipulation: point the server command at a script path that does
        not exist -- 'the server never started' verbatim, the exact failure
        mode DC3's own trap warns is indistinguishable from a genuine
        no-identity result unless this control is checked first. Proof the
        manipulation actually applied: the child process's own exit code and
        stderr, not just 'the control raised' (a control that raises for the
        WRONG reason is not a demonstrated red, it is a lucky one)."""
        spine = write_marked_spine(self.root, "PC-RED", "pc-red-work")
        missing_server = self.root / "does-not-exist" / "mcp_spine_server.py"
        inst = ServerInstance(spine, "pc-red-session", self.root, server=missing_server)
        try:
            with self.assertRaises(AssertionError):
                assert_door_is_up_and_serving(self, inst, "PC-RED")
            inst.proc.wait(timeout=10)
            self.assertNotEqual(0, inst.proc.returncode, "the manipulation did not actually prevent the server from starting")
            stderr = inst.proc.stderr.read()
            self.assertIn("mcp_spine_server.py", stderr,
                           "exit failure is not the one the manipulation was supposed to cause")
            self.assertIn("No such file or directory", stderr)
        finally:
            inst.close()

    def test_control_is_red_when_the_config_never_delivered(self):
        """A second, independent way to reach 'no identity': SPINE_FILE
        itself is simply never set (the config-delivery flavor of DC3's
        trap, distinct from the server-never-started flavor above).
        mcp_spine_server.py requires it at import time, so this crashes
        immediately -- proof of manipulation is the KeyError itself,
        verbatim, in the child's own stderr."""
        base_env = dict(os.environ)
        for k in SPINE_ENV_KEYS:
            base_env.pop(k, None)
        base_env["SPINE_ENGINE"] = str(ENGINE)
        inst = ServerInstance(None, None, self.root, base_env=base_env)
        try:
            with self.assertRaises(AssertionError):
                assert_door_is_up_and_serving(self, inst, "irrelevant")
            inst.proc.wait(timeout=10)
            self.assertNotEqual(0, inst.proc.returncode)
            stderr = inst.proc.stderr.read()
            self.assertIn("KeyError", stderr)
            self.assertIn("SPINE_FILE", stderr)
        finally:
            inst.close()

    def test_control_is_green_when_the_server_genuinely_responds(self):
        spine = write_marked_spine(self.root, "PC-GREEN", "pc-green-work")
        inst = ServerInstance(spine, "pc-green-session", self.root)
        try:
            assert_door_is_up_and_serving(self, inst, "PC-GREEN")  # must not raise
        finally:
            inst.close()

    def test_control_is_red_when_it_is_up_but_serving_the_wrong_content(self):
        """A door that is genuinely up but answering for a DIFFERENT spine
        must not be waved through by this control either -- proves the
        control checks content, not merely liveness."""
        spine = write_marked_spine(self.root, "PC-ACTUAL", "pc-mismatch-work")
        inst = ServerInstance(spine, "pc-mismatch-session", self.root)
        try:
            with self.assertRaises(AssertionError):
                assert_door_is_up_and_serving(self, inst, "PC-SOMETHING-ELSE-ENTIRELY")
        finally:
            inst.close()


class DC3InheritanceMechanismTests(unittest.TestCase):
    """DC3, at the seam `mcp_spine_server.py`'s own module docstring names:
    'Ambient state is bound at server-launch time from the environment ...
    that is the seam identity rides on.' This class measures whether a
    process launched the way a subagent with NO special MCP configuration
    would be launched -- inheriting whatever environment its caller already
    has, no explicit `--mcp-config` of its own -- can end up reading a
    PARENT's already-claimed lease/gate through THIS repo's actual delivery
    mechanism (env vars set by the caller, the same seam the committed
    `.mcp.json`'s `${VAR}` expansion feeds).

    Explicitly OUT of scope for this class (do not conflate, per the
    handoff): whether Claude Code's own Task-tool harness internally reuses
    an already-connected MCP client/server object inside one running
    process, entirely bypassing this environment seam. That is a
    product-internal mechanism with no observation point reachable from a
    subprocess-level test; the honest scope boundary is recorded in the
    IMPLEMENTER_RESULT's DC3 verdict, not silently smoothed over here.

    The "parent" below is launched directly from the environment seam --
    SPINE_FILE/SPINE_ENGINE/SPINE_SESSION set in the env passed to Popen,
    with SPINE_SESSION composed by this test as `session_id#agent_id` --
    exactly what the committed `.mcp.json`'s `${VAR}` expansion delivers to
    a real dispatch, and exactly what every other class in this file already
    does. There is no per-dispatch config file involved.

    Also explicitly NOT this: the separate CLI/engine-lease observation that
    two different callers can pass the identical free-text `--session-id`
    string to `checklist_engine claim` (a convention at the argument-passing
    layer). That is a different mechanism and is never manufactured or
    exercised here."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

        # A "parent": launched directly from the environment seam -- the
        # SPINE_SESSION composed as `session_id#agent_id` right here, the
        # same caller-side convention `.mcp.json`'s `${VAR}` expansion
        # delivers on a real dispatch. No per-dispatch config file involved.
        self.parent_spine = write_marked_spine(self.root / "parent", "PARENT-MARK", "parent-work")

        # Snapshot the CALLING test process's own environment BEFORE
        # launching the parent, so the first test can prove launching it
        # changed nothing here.
        self._env_before = dict(os.environ)

        self.parent = ServerInstance(self.parent_spine, "parent-session#parent-agent", self.root / "parent")
        claimed = self.parent.call("spine_lease", action="claim", claimed_by="parent-agent")
        self.assertIsNotNone(claimed)
        self.assertFalse(claimed.get("isError"))
        # DC3 positive control -- the door must be demonstrably up before any
        # "no identity" result elsewhere in this class is allowed to count.
        assert_door_is_up_and_serving(self, self.parent, "PARENT-MARK")

    def tearDown(self):
        self.parent.close()
        self.tmp.cleanup()

    def test_launching_the_parent_never_touches_the_calling_processs_own_environ(self):
        """The repo's actual delivery mechanism (an explicit `env=` block
        passed to Popen, the same shape the committed `.mcp.json`'s `${VAR}`
        expansion produces from the caller's environment) never mutates the
        CALLING process's own os.environ -- verified here, not assumed, so
        the next test's premise (a sibling process launched with no explicit
        override inherits a clean environment) rests on a measured fact."""
        for key in SPINE_ENV_KEYS:
            self.assertNotIn(key, os.environ, f"{key} leaked into the calling process's own environment")
        self.assertEqual(self._env_before, dict(os.environ))

    def test_subagent_with_no_special_configuration_gets_no_identity_never_the_parents(self):
        """The DC3 claim itself: launch a 'subagent' the way one with no
        special MCP configuration would be launched -- inheriting the
        calling process's real environment, no explicit --mcp-config of its
        own. Per the previous test, that environment structurally cannot
        contain the parent's SPINE_FILE/SPINE_SESSION under this repo's
        delivery mechanism, so the subagent's server crashes on launch (no
        SPINE_FILE at all) -- NO IDENTITY, cleanly, never the parent's
        reading. The positive control is asserted on the PARENT throughout,
        proving the parent's door stayed genuinely up and unaffected while
        the subagent's crashed."""
        subagent = ServerInstance(None, None, self.root / "subagent", base_env=None)
        try:
            text = subagent.status_text(timeout=10)
            self.assertIsNone(text, "a subagent with no special configuration produced a reply -- expected none")
            subagent.proc.wait(timeout=10)
            self.assertNotEqual(0, subagent.proc.returncode)
            stderr = subagent.proc.stderr.read()
            self.assertIn("SPINE_FILE", stderr)

            assert_door_is_up_and_serving(self, self.parent, "PARENT-MARK")
            parent_text = self.parent.status_text()
            self.assertIn("LEASE active: parent-session#parent-agent (by parent-agent", parent_text)
        finally:
            subagent.close()

    def test_ambient_leak_counterfactual_would_have_been_caught(self):
        """The mirror of DC2's collision control, applied to DC3: if the
        parent's SPINE_FILE/SPINE_SESSION HAD somehow become ambient in a
        subagent's environment (the risk the previous test's first assertion
        shows this repo's actual delivery mechanism structurally avoids),
        the subagent WOULD read the parent's own reading -- proving the
        no-identity assertion in the previous test is not vacuously true; a
        real DC3 leak would have been caught by these tests."""
        leaking_env = dict(os.environ)
        for k in SPINE_ENV_KEYS:
            leaking_env.pop(k, None)
        leaking_env["SPINE_FILE"] = self.parent.env["SPINE_FILE"]
        leaking_env["SPINE_ENGINE"] = self.parent.env["SPINE_ENGINE"]
        leaking_env["SPINE_SESSION"] = self.parent.env["SPINE_SESSION"]
        leak_dir = self.root / "leak"
        leak_dir.mkdir(exist_ok=True)
        leaking_env["SPINE_CALLLOG"] = str(leak_dir / "mcp_calls.jsonl")
        leaking_env["SPINE_START_MARKER"] = str(leak_dir / "mcp_server_started")

        leaked_subagent = ServerInstance(None, None, leak_dir, base_env=leaking_env)
        try:
            assert_door_is_up_and_serving(self, leaked_subagent, "PARENT-MARK")
            text = leaked_subagent.status_text()
            self.assertIn(
                "LEASE active: parent-session#parent-agent (by parent-agent", text,
                "the ambient-leak counterfactual did not reproduce -- this control is "
                "not sensitive enough to have caught a real DC3 leak",
            )
        finally:
            leaked_subagent.close()


if __name__ == "__main__":
    unittest.main()


# =============================================================================
# g1 (issue #542/#541, workstream F2): the identity-binding PIN
# =============================================================================


class IdentityBindingPinTests(unittest.TestCase):
    """Pin the identity binding that `IDENTITY_TRADE.md` selects, so a later
    change cannot move it silently.

    WRITTEN OUTCOME-NEUTRALLY, on purpose. This class does not encode "binding
    identity to the process is correct" -- that is the trade document's job,
    and the trade was genuinely open when this was written. It encodes the
    weaker and more durable claim: *the binding is what the recorded decision
    says it is*. If a future run re-opens the trade and moves identity to a
    per-call argument, these tests go red, and going red is the point: the
    change then has to arrive together with a change to `IDENTITY_TRADE.md`
    rather than instead of one.

    The property being pinned, in one line: **the door can only ever touch the
    spine its own process was launched for, because there is no argument that
    would let it touch another.** That is confinement by construction. It is
    what an in-session Task subagent -- which shares its parent's process and
    therefore its parent's server -- makes load-bearing, and it is what the
    CLI door deliberately does NOT have (`--file`/`--session-id` are per call),
    which is why the two doors are different tools rather than two copies of
    one.

    Companion seam, named but NOT tested here: `scripts/hooks/spine_rail.py`
    has the same defect by a different route (issue #549) -- it is outside this
    run's file fence and is cited by the trade document, not repaired.
    """

    #: Argument names that would carry a spine path or a caller-supplied
    #: identity into a tool call. Substring-matched against every tool
    #: property name, so `spine_file`, `spineFile`, `target_spine` and
    #: `session_id` are all caught without enumerating spellings.
    IDENTITY_ARG_MARKERS = ("spine", "session", "engine", "checklist_file", "identity")

    #: Deliberately NOT matched: `task_id` (a gate id within the bound spine),
    #: `condition_id`, `evidence_ref`, `from_child`. Those address things
    #: INSIDE the spine the server is already bound to; they cannot redirect
    #: it. The distinction is the whole discriminator, so it is stated rather
    #: than left implicit in a regex.
    ADDRESSES_WITHIN_BOUND_SPINE = ("task_id", "condition_id", "evidence_ref", "from_child")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.spine = write_marked_spine(self.root, "PIN-MARK", "pin-work")

    def tearDown(self):
        self.tmp.cleanup()

    def _load_module(self, spine: Path, session: str):
        """Import a FRESH copy of the server module under a chosen environment.

        A fresh module object per call is what makes 'bound at import' a
        testable claim at all: a cached import would carry the first test's
        environment into every later one.
        """
        import importlib.util

        env_patch = {
            "SPINE_FILE": str(spine),
            "SPINE_ENGINE": str(ENGINE),
            "SPINE_SESSION": session,
            "SPINE_CALLLOG": str(spine.parent / "pin_calls.jsonl"),
            "SPINE_START_MARKER": str(spine.parent / "pin_started"),
        }
        saved = {k: os.environ.get(k) for k in env_patch}
        os.environ.update(env_patch)
        try:
            spec = importlib.util.spec_from_file_location(
                f"_pinned_door_{abs(hash(session)) % 100000}", SERVER)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        finally:
            for key, value in saved.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    def test_no_tool_accepts_an_argument_that_could_redirect_the_door(self):
        """THE pin. Identity is not per-call, so no tool may take an argument
        naming a spine, a session or an engine. A future change that adds one
        has moved the binding and must say so in IDENTITY_TRADE.md."""
        module = self._load_module(self.spine, "pin-session#pin-agent")
        offenders = []
        for tool in module.TOOLS:
            schema = tool.get("inputSchema") or {}
            for prop in (schema.get("properties") or {}):
                if prop in self.ADDRESSES_WITHIN_BOUND_SPINE:
                    continue
                lowered = prop.lower()
                if any(marker in lowered for marker in self.IDENTITY_ARG_MARKERS):
                    offenders.append(f"{tool['name']}.{prop}")
        self.assertEqual(
            [], offenders,
            "a tool now accepts an argument that could point the door at a different "
            f"spine or identity: {offenders}. If the identity trade was deliberately "
            "re-opened, update .agent-work/epic-418-followon/commander-f2/IDENTITY_TRADE.md "
            "in the same change -- this test exists so that cannot happen silently.",
        )

    def test_the_pin_can_fail(self):
        """Positive control, in the assertion path. A tool schema carrying a
        spine argument MUST be detected -- otherwise the test above is green
        for the wrong reason and proves nothing."""
        module = self._load_module(self.spine, "pin-control#pin-agent")
        planted = dict(module.TOOLS[0])
        planted["inputSchema"] = {
            "type": "object",
            "properties": {"spine_file": {"type": "string"}},
        }
        offenders = []
        for tool in [planted]:
            for prop in (tool["inputSchema"].get("properties") or {}):
                if any(m in prop.lower() for m in self.IDENTITY_ARG_MARKERS):
                    offenders.append(f"{tool['name']}.{prop}")
        self.assertTrue(
            offenders,
            "the detector did not flag a planted `spine_file` tool argument -- the "
            "pin above is incapable of failing and is therefore not evidence",
        )

    def test_identity_is_bound_at_import_and_is_immune_to_later_environment_change(self):
        """The confinement property itself: once the module is imported, moving
        SPINE_FILE in the environment cannot move where the door points. A
        binding re-read per call would fail this."""
        module = self._load_module(self.spine, "pin-immune#pin-agent")
        bound_spine, bound_session = module.SPINE, module.SESSION
        self.assertEqual(Path(self.spine).resolve(), bound_spine)
        self.assertEqual("pin-immune#pin-agent", bound_session)

        other = write_marked_spine(self.root / "other", "OTHER-MARK", "other-work")
        saved = os.environ.get("SPINE_FILE")
        os.environ["SPINE_FILE"] = str(other)
        try:
            self.assertEqual(
                bound_spine, module.SPINE,
                "the door followed a later environment change -- identity is no longer "
                "bound at import, which is the property IDENTITY_TRADE.md selected",
            )
        finally:
            if saved is None:
                os.environ.pop("SPINE_FILE", None)
            else:
                os.environ["SPINE_FILE"] = saved

    def test_two_doors_bound_to_two_spines_do_not_share_a_binding(self):
        """Two module objects, two environments, two bindings. This is the
        in-process analogue of DC2 and is what makes 'one process = one spine'
        a statement about the module rather than about a subprocess."""
        other = write_marked_spine(self.root / "second", "SECOND-MARK", "second-work")
        first = self._load_module(self.spine, "first#a")
        second = self._load_module(other, "second#b")
        self.assertNotEqual(first.SPINE, second.SPINE)
        self.assertNotEqual(first.SESSION, second.SESSION)

    #: Affixes real code actually uses when naming a path/identity argument.
    #: Crossed with IDENTITY_ARG_MARKERS below to GENERATE adversarial keys
    #: rather than list them. `target_spine` -- the key the g1 re-reviewer used
    #: to defeat the first version of this pin -- falls out of `target_{}` x
    #: `spine` without being written down anywhere.
    ARG_AFFIXES = ("{}", "target_{}", "{}_file", "{}_path", "{}_override",
                   "override_{}", "{}s", "_{}", "{}Path", "the_{}")

    @classmethod
    def _adversarial_keys(cls):
        keys = {a.format(m) for m in cls.IDENTITY_ARG_MARKERS for a in cls.ARG_AFFIXES}
        # Names carrying no marker at all: the property under test is about
        # ANY undeclared argument, not about ones that look suspicious.
        keys.update({"redirect", "f", "path", "x", "cfg", "where", "--file"})
        return sorted(keys)

    #: Minimal valid arguments per tool, so every tool actually reaches the
    #: engine and contributes an argv to inspect. Without these, `_require`
    #: short-circuits and the sweep silently covers only `spine_status`.
    TOOL_MINIMAL_ARGS = {
        "spine_status": {},
        "spine_lease": {"action": "heartbeat"},
        "spine_start": {"task_id": "g1"},
        "spine_advance": {"task_id": "g1", "mechanical": True},
        "spine_evidence": {"action": "attest", "task_id": "g1", "condition_id": "c1"},
        "spine_halt": {"action": "block", "task_id": "g1", "blocker": "x"},
        "spine_survey_result": {"action": "record", "task_id": "r1", "result": "pass"},
    }

    def test_no_argument_can_change_what_the_door_reads_or_where_it_reads_it(self):
        """THE runtime pin. Three reviewers defeated its three predecessors, each
        one layer deeper, so it is now stated as the property the module's own
        docstring claims rather than as a check over some surface.

        The history is the design rationale and is kept:

        1. v1 pinned DECLARED tool arguments. Reviewer 1 honoured an undeclared
           `spine_override` in the handler. Green. *A pin over declarations is a
           pin over intentions.*
        2. v2 pinned five literal key names on one tool. Reviewer 2 used a
           sixth, `target_spine`. Green. *An enumeration is not a property.*
        3. v3 pinned the argv handed to the engine. Reviewer 3 wrote a handler
           that read a decoy file and returned its contents **without ever
           calling the engine**, so no argv existed to inspect. Green. *A
           property over the calls you make says nothing about the answers you
           invent.*
        4. v4 pinned the pass-through but asserted the engine's output was
           CONTAINED in the answer. Reviewer 4 called the engine honestly and
           then **concatenated** leaked file content onto the result. Green.
           *Containment is not equality; a leak adds, it does not replace.*
           Hence `assertEqual` below, and hence the framing that any character
           in the response which did not come from the bound call is itself the
           violation.

        The invariant that closes all three, and the one
        `mcp_spine_server.py`'s docstring already asserts -- "it never inspects
        or rewrites the output beyond capturing it" -- is that **the door is a
        pass-through**:

        For any tool and ANY arguments, either
          (a) the engine was called, addressed at the BOUND spine and the BOUND
              session, and the result text IS that call's output; or
          (b) no engine call happened and the result is the door's own refusal
              (`isError: True`).

        There is no third way to produce content. A redirect must show up as a
        wrong `--file`, as invented output, or as a non-error answer nobody
        computed -- and all three are red here.
        """
        module = self._load_module(self.spine, "passthrough-pin#agent")
        decoy = write_marked_spine(self.root / "decoy3", "DECOY3-MARK", "decoy3-work")
        bound_file, bound_session = str(module.SPINE), module.SESSION
        sentinel = "ENGINE-OUTPUT-SENTINEL-7f3a91"

        seen = []
        real_main = module.checklist_engine.main

        def spy(argv):
            seen.append(list(argv))
            print(sentinel)
            return 0

        # `as_result` builds its text as (stdout + stderr).strip(). The spy writes
        # exactly one line, so the door's ONLY honest answer is that line -- which
        # makes exact equality decidable, and equality is the whole point (see the
        # fourth falsification in the docstring).
        expected_text = sentinel

        module.checklist_engine.main = spy
        try:
            for tool in module.TOOLS:
                base = self.TOOL_MINIMAL_ARGS[tool["name"]]
                for key in self._adversarial_keys():
                    seen.clear()
                    where = f"{tool['name']} with undeclared {key!r}"
                    result = module.call_tool(tool["name"], {**base, key: str(decoy)})
                    text = result["content"][0]["text"]

                    if not seen:
                        # (b) no engine call -> must be the door refusing, never an answer.
                        self.assertIs(
                            True, result.get("isError"),
                            f"{where} produced a NON-ERROR answer without ever calling the "
                            "engine -- the door invented content, so it is no longer a "
                            "pass-through and could be reading anything it likes",
                        )
                        continue

                    # (a) engine called -> bound identity, and the answer is ITS output.
                    for argv in seen:
                        self.assertEqual(
                            bound_file, argv[argv.index("--file") + 1],
                            f"{where} addressed the engine at a DIFFERENT spine",
                        )
                        if "--session-id" in argv:
                            self.assertEqual(
                                bound_session, argv[argv.index("--session-id") + 1],
                                f"{where} addressed the engine under a DIFFERENT identity",
                            )
                    self.assertEqual(
                        expected_text, text,
                        f"{where} returned text that is not EXACTLY the engine's own output. "
                        "Equality, not containment: a handler that calls the engine honestly "
                        "and then CONCATENATES leaked content onto the result passes a "
                        "containment check while leaking. Any character in the response that "
                        "did not come from the bound call is itself the violation.",
                    )
        finally:
            module.checklist_engine.main = real_main

    def test_the_universal_runtime_pin_can_fail(self):
        """Positive control, in the assertion path, using the EXACT key that
        defeated the previous version. If this ever stops detecting it, the pin
        above has silently regressed to an enumeration again."""
        decoy = write_marked_spine(self.root / "decoy4", "DECOY4-MARK", "decoy4-work")
        module = self._load_module(self.spine, "argv-control#agent")
        bound_file = str(module.SPINE)

        seen = []
        real_main = module.checklist_engine.main
        module.checklist_engine.main = lambda argv: (seen.append(list(argv)), 0)[1]
        try:
            # A door that honours an undeclared key -- the re-reviewer's mutation 4.
            module.SPINE = Path(str(decoy)).resolve()
            module.call_tool("spine_status", {"target_spine": str(decoy)})
        finally:
            module.checklist_engine.main = real_main

        self.assertTrue(seen, "the control never reached the engine")
        addressed = seen[0][seen[0].index("--file") + 1]
        self.assertNotEqual(
            bound_file, addressed,
            "the control did not reproduce a redirect -- the universal pin above is "
            "incapable of failing and is therefore not evidence",
        )

    def test_call_tool_can_only_produce_content_two_ways(self):
        """The CHOKE-POINT pin -- key-independent, and the honest answer to a
        limit the runtime sweep cannot escape.

        Reviewer 4's leak fires only on the argument key it chose. My sweep
        generates keys; a generated set is still a set, so a leak keyed on a
        name nobody generated survives it. **Black-box argument fuzzing cannot
        establish a property over all possible argument names** -- that is a
        real limit, not an oversight, and adding more names would repeat
        exactly the enumeration mistake reviewer 2 already caught.

        So this asserts the property where key names do not appear at all: over
        the SHAPE of the code. `call_tool` may produce content in exactly two
        ways -- `as_result(run_engine(...))` or `_tool_error(...)` -- and every
        `return` in it must be literally one of those calls. Reviewer 3's
        suggestion (b), made structural: a handler that reads a file, or
        concatenates onto a result, or builds a dict itself, has to write a
        return this rejects, whatever it names its argument.

        The two pins are complementary and neither subsumes the other: this one
        is blind to a redirect that keeps the right shape (`as_result` of a
        `run_engine` pointed elsewhere), which the runtime sweep catches; the
        sweep is blind to a leak on an unguessed key, which this catches.
        """
        import ast

        source = SERVER.read_text(encoding="utf-8")
        tree = ast.parse(source)
        fn = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "call_tool")

        allowed = {"as_result", "_tool_error"}
        offenders = []
        for node in ast.walk(fn):
            if not isinstance(node, ast.Return) or node.value is None:
                continue
            v = node.value
            ok = (isinstance(v, ast.Call) and isinstance(v.func, ast.Name)
                  and v.func.id in allowed)
            if ok and v.func.id == "as_result":
                # `as_result` must wrap a run_engine call directly -- not a name
                # bound earlier, which is where a mutate-then-return leak hides.
                arg = v.args[0] if v.args else None
                ok = (isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name)
                      and arg.func.id == "run_engine")
            if not ok:
                offenders.append(f"line {node.lineno}: {ast.unparse(v)[:80]}")

        self.assertEqual(
            [], offenders,
            "call_tool now returns content some way other than as_result(run_engine(...)) "
            f"or _tool_error(...): {offenders}. The door is only a pass-through while those "
            "are the ONLY two ways it can answer; a third way is where a leak or a "
            "redirect lives, and it does not need an argument name to get there.",
        )

    def test_the_choke_point_pin_can_fail(self):
        """Positive control: reviewer 4's leak shape -- bind the result, mutate
        it, return the name -- must be detected as a third way to answer."""
        import ast

        leaky = (
            "def call_tool(name, args):\n"
            "    out = as_result(run_engine('current', mutating=False))\n"
            "    out['content'][0]['text'] += open(args['extra']).read()\n"
            "    return out\n"
        )
        fn = next(n for n in ast.walk(ast.parse(leaky))
                  if isinstance(n, ast.FunctionDef))
        offenders = []
        for node in ast.walk(fn):
            if isinstance(node, ast.Return) and node.value is not None:
                v = node.value
                ok = (isinstance(v, ast.Call) and isinstance(v.func, ast.Name)
                      and v.func.id in {"as_result", "_tool_error"})
                if not ok:
                    offenders.append(ast.unparse(v))
        self.assertTrue(
            offenders,
            "the choke-point detector did not flag a mutate-then-return leak -- it is "
            "incapable of failing and is therefore not evidence",
        )

    def test_the_recorded_trade_exists_and_still_names_the_binding_this_pins(self):
        """The pin and the record are one artifact in two files; a pin whose
        record has been deleted is a rule nobody can look up the reason for.
        `identity-trade-is-recorded` makes silence a gate failure, so absence
        is red rather than skipped."""
        trade = ROOT / ".agent-work" / "epic-418-followon" / "commander-f2" / "IDENTITY_TRADE.md"
        self.assertTrue(trade.is_file(), f"the recorded identity trade is missing: {trade}")
        text = trade.read_text(encoding="utf-8")
        for required in ("property given up", "granularity", "spine_rail"):
            self.assertIn(
                required, text,
                f"IDENTITY_TRADE.md no longer discusses {required!r} -- the pin and the "
                "record have drifted apart",
            )
