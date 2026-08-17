"""The MCP door must fail CLOSED when nothing usable is bound (issue #603,
cleanup-a-door gate g3).

An unbound door used to do one of two things, never the right one:

* `SPINE_FILE` **unset** -- `KeyError` at module scope, *at import*. The server
  died before it could refuse anything and the client saw only
  `Connection closed`, which names neither the cause nor the fix.
* `SPINE_FILE` **empty** -- `Path("").resolve()` is the process's *cwd*, so the
  door silently bound itself to a directory and answered `IsADirectoryError`.
  This is the case production actually takes: `.mcp.json` writes
  `${SPINE_FILE:-<default>}`, so dropping the default yields `${SPINE_FILE:-}`,
  which a shell expands to **empty, not unset**.

Plus three more that are the same question with a different spelling: a path
that does not exist, a path that is a directory, and a file that cannot be read.
All five are ONE class here -- *no usable spine is bound* -- and every tool
answers a **refusal** rather than a demo answer, a crash, or silence.

The refusal WORDING splits, because an unbound door has no path to name and a
criterion that says "name the path" is unsatisfiable there:

* **unbound** (unset/empty) -- say that nothing is bound and how to bind.
* **bound but unusable** (missing/not-a-file/unreadable) -- name the path *and*
  say how to rebind.

`SPINE_ENGINE` is covered by the same motion. Unset, it was a `KeyError` on the
line above `SPINE_FILE`'s, also at import -- and a session with no `SPINE_FILE`
very likely has no `SPINE_ENGINE` either, so without this the door dies before
any refusal is reachable.

Integration-style by design, like `tests/test_mcp_door_telemetry.py`: the defect
is a *process death*, which no in-process call can observe -- only a subprocess
has an exit code. Every test here spawns the real server with the environment
under test and drives real JSON-RPC over its stdio.
"""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "scripts" / "mcp_spine_server.py"
ENGINE = ROOT / "scripts" / "checklist_engine.py"

# The tools that are REACHABLE with nothing bound, because they are the ways
# out. They split on whether the work exists yet: `spine_open` MINTS a spine and
# binds this process to it; `spine_bind` (issue #567 lane A) binds a spine that
# ALREADY exists. Every other tool refuses. Kept here as data so the enumeration
# test below can assert a COUNT rather than a hand-copied list.
BINDS_WITHOUT_A_BOUND_SPINE = {"spine_open", "spine_bind"}

# Anchors, deliberately short: the wording may be improved, but a refusal that
# stops saying "no spine is bound" or stops naming `spine_open` has stopped
# telling the caller what to do, which is the whole point of the gate.
UNBOUND_ANCHORS = ("no spine is bound", "spine_open")
REBIND_ANCHOR = "rebind"


@dataclass
class DoorRun:
    stdout: str
    stderr: str
    returncode: int

    def answer(self, mid: int) -> dict | None:
        for line in self.stdout.splitlines():
            try:
                msg = json.loads(line)
            except ValueError:
                continue
            if msg.get("id") == mid:
                return msg
        return None

    def tool_text(self, mid: int) -> str:
        answer = self.answer(mid)
        assert answer is not None, (
            f"the door never answered call id={mid}; exit {self.returncode}, "
            f"stderr:\n{self.stderr}")
        result = answer.get("result")
        assert result is not None, f"expected a tool result, got {answer}"
        return "".join(block.get("text", "") for block in result.get("content", []))

    def is_error(self, mid: int) -> bool:
        answer = self.answer(mid)
        assert answer is not None, (
            f"the door never answered call id={mid}; exit {self.returncode}, "
            f"stderr:\n{self.stderr}")
        return bool(answer["result"].get("isError"))


def drive_door(env_under_test: dict, calls: list[tuple[int, str, dict]], *,
               cwd: Path | None = None) -> DoorRun:
    """Spawn the real door with `env_under_test` and make `calls` through it.

    `env_under_test` is the WHOLE environment (plus PATH), not an overlay: this
    file is about variables being absent, and an overlay cannot express absence
    when the test process's own environment may carry them -- this suite may
    itself run under a dispatched crew with `SPINE_FILE` set.

    `cwd` matters for exactly one case: an EMPTY `SPINE_FILE` used to resolve to
    the process's own working directory, so the empty-string test runs the door
    somewhere it would visibly bind if the defect returned.
    """
    env = {"PATH": os.environ.get("PATH", ""), **env_under_test}
    messages = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                    "clientInfo": {"name": "unbound-test", "version": "0"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
    ]
    for mid, tool, args in calls:
        messages.append({"jsonrpc": "2.0", "id": mid, "method": "tools/call",
                         "params": {"name": tool, "arguments": args}})
    proc = subprocess.Popen(
        [sys.executable, str(SERVER)],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", env=env, cwd=str(cwd) if cwd else None,
    )
    try:
        out, err = proc.communicate(
            "\n".join(json.dumps(m) for m in messages) + "\n", timeout=120)
    except subprocess.TimeoutExpired:  # pragma: no cover - a hung door, not the defect
        proc.kill()
        out, err = proc.communicate()
        raise AssertionError("the door never exited")
    return DoorRun(out, err, proc.returncode)


def unbound_env(**extra: str) -> dict:
    """The environment of a session that never bound a door: `SPINE_FILE` is
    genuinely ABSENT, not empty. The two are different failure worlds and this
    file measures both -- so absence is expressed by BUILDING the variable in
    only when a caller asks for it, never by setting it and deleting it again.
    `drive_door` passes this as the whole environment, so what is not here is
    not there."""
    return {"SPINE_ENGINE": str(ENGINE), "SPINE_SESSION": "", **extra}


def door_tool_names() -> list[str]:
    """Every tool the door declares, asked of the door itself rather than
    hand-copied -- so a tool added later is covered here the day it ships."""
    proc = subprocess.Popen(
        [sys.executable, str(SERVER)],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", env={"PATH": os.environ.get("PATH", ""), **unbound_env()},
    )
    out, err = proc.communicate(json.dumps(
        {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}) + "\n", timeout=120)
    for line in out.splitlines():
        try:
            msg = json.loads(line)
        except ValueError:
            continue
        if msg.get("id") == 1:
            return [t["name"] for t in msg["result"]["tools"]]
    raise AssertionError(
        f"the unbound door could not even list its tools; exit {proc.returncode}, "
        f"stderr:\n{err}")


# --------------------------------------------------------------------------- #
# 1. The five unbound-class inputs, one at a time.
# --------------------------------------------------------------------------- #

class UnboundDoorRefusesTests(unittest.TestCase):
    """Nothing usable is bound, so every answer is a refusal and the process
    stays alive to give it."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _assert_alive(self, run: DoorRun) -> None:
        self.assertEqual(
            0, run.returncode,
            f"the door died instead of refusing; stderr:\n{run.stderr}")

    def _assert_unbound_refusal(self, run: DoorRun, mid: int = 2) -> str:
        self._assert_alive(run)
        self.assertTrue(run.is_error(mid), "an unbound answer must be isError")
        text = run.tool_text(mid)
        for anchor in UNBOUND_ANCHORS:
            self.assertIn(
                anchor, text,
                f"an unbound refusal must say {anchor!r} -- a caller who cannot "
                f"tell WHY the call failed or HOW to fix it has been told nothing. Got:\n{text}")
        return text

    def _assert_unusable_refusal(self, run: DoorRun, path: Path, mid: int = 2) -> str:
        self._assert_alive(run)
        self.assertTrue(run.is_error(mid), "an unusable-spine answer must be isError")
        text = run.tool_text(mid)
        self.assertIn(
            str(path), text,
            f"a door bound to an unusable path must NAME that path. Got:\n{text}")
        self.assertIn(
            REBIND_ANCHOR, text,
            f"a door bound to an unusable path must say how to rebind. Got:\n{text}")
        return text

    def test_unset_spine_file_refuses_instead_of_dying_at_import(self):
        """The measured pre-fix behaviour: `KeyError: 'SPINE_FILE'` at module
        scope, exit 1, no answer at all."""
        run = drive_door(unbound_env(), [(2, "spine_status", {})])
        self.assertNotIn(
            "KeyError", run.stderr,
            "the door still dies at import on an unset SPINE_FILE")
        self._assert_unbound_refusal(run)

    def test_empty_spine_file_refuses_rather_than_binding_the_cwd(self):
        """`Path("").resolve()` is the cwd. The door must not bind a directory
        it merely happens to be standing in -- and this is the case a shell's
        `${SPINE_FILE:-}` expansion actually produces."""
        run = drive_door(unbound_env(SPINE_FILE=""), [(2, "spine_status", {})], cwd=self.dir)
        text = self._assert_unbound_refusal(run)
        self.assertNotIn("IsADirectoryError", text + run.stderr)
        self.assertNotIn(
            str(self.dir), text,
            "an empty SPINE_FILE silently bound the door to its working directory")

    def test_whitespace_only_spine_file_is_the_same_class_as_empty(self):
        run = drive_door(unbound_env(SPINE_FILE="   "), [(2, "spine_status", {})], cwd=self.dir)
        self._assert_unbound_refusal(run)

    def test_missing_spine_file_names_the_path(self):
        missing = self.dir / "no-such-spine.json"
        run = drive_door(unbound_env(SPINE_FILE=str(missing)), [(2, "spine_status", {})])
        text = self._assert_unusable_refusal(run, missing)
        self.assertNotIn(
            "FileNotFoundError", text,
            "a raw exception name is not a refusal that tells the caller what to do")

    def test_a_directory_as_spine_file_is_refused(self):
        run = drive_door(unbound_env(SPINE_FILE=str(self.dir)), [(2, "spine_status", {})])
        self._assert_unusable_refusal(run, self.dir)

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0,
                     "root reads unreadable files; the case cannot be staged")
    @unittest.skipUnless(hasattr(os, "geteuid"), "POSIX permission bits required")
    def test_an_unreadable_spine_file_is_refused(self):
        spine = self.dir / "locked.json"
        spine.write_text('{"work_id": "x", "type": "gated", "items": [], "tasks": {}}',
                         encoding="utf-8")
        spine.chmod(0o000)
        try:
            run = drive_door(unbound_env(SPINE_FILE=str(spine)), [(2, "spine_status", {})])
            self._assert_unusable_refusal(run, spine)
        finally:
            spine.chmod(stat.S_IRUSR | stat.S_IWUSR)

    def test_unset_spine_engine_does_not_kill_the_server_at_import(self):
        """`SPINE_ENGINE` was a `KeyError` one line above `SPINE_FILE`'s. A
        session that bound neither must still get a refusal it can read."""
        env = unbound_env()
        env.pop("SPINE_ENGINE", None)
        run = drive_door(env, [(2, "spine_status", {})])
        self.assertNotIn("KeyError", run.stderr)
        self._assert_unbound_refusal(run)


# --------------------------------------------------------------------------- #
# 2. The refusal covers the WHOLE tool surface, not the one tool a probe tried.
# --------------------------------------------------------------------------- #

class EveryToolRefusesWhenUnboundTests(unittest.TestCase):
    """A fail-closed door that only fails closed on `spine_status` is a door
    with an unmeasured hole in it. This enumerates the surface from the door's
    own `tools/list` and asserts a COUNT, so a tool added later is covered the
    day it ships."""

    # Enough arguments for each tool's own required-argument check to pass, so
    # what is measured is the UNBOUND refusal and not a missing-argument one.
    ARGS = {
        "spine_lease": {"action": "claim"},
        "spine_start": {"task_id": "g1"},
        "spine_advance": {"task_id": "g1", "mechanical": True},
        "spine_evidence": {"action": "attest", "task_id": "g1", "condition_id": "c1"},
        "spine_halt": {"action": "block", "task_id": "g1", "blocker": "x"},
        "spine_capture": {"action": "append", "task_id": "g1",
                          "title": "x", "imperative": "x"},
        "spine_survey_result": {"action": "record", "task_id": "g1", "result": "PASS"},
        "spine_amend": {"delta": {"ops": []}, "reason": "x", "authority": "human"},
        "spine_open": {"work_id": "x", "spec": {"a": 1}},
    }

    def test_every_tool_but_the_one_that_binds_refuses(self):
        names = door_tool_names()
        self.assertGreaterEqual(len(names), 11, f"unexpectedly few tools: {names}")
        should_refuse = [n for n in names if n not in BINDS_WITHOUT_A_BOUND_SPINE]

        calls = [(10 + i, name, self.ARGS.get(name, {}))
                 for i, name in enumerate(should_refuse)]
        run = drive_door(unbound_env(), calls)
        self.assertEqual(
            0, run.returncode,
            f"the door died partway through the tool surface; stderr:\n{run.stderr}")

        refused = []
        for mid, name, _ in calls:
            text = run.tool_text(mid)
            self.assertTrue(run.is_error(mid), f"{name} did not refuse: {text}")
            for anchor in UNBOUND_ANCHORS:
                self.assertIn(anchor, text, f"{name}'s refusal does not say {anchor!r}: {text}")
            refused.append(name)

        self.assertEqual(
            len(should_refuse), len(refused),
            f"refused {len(refused)} of {len(should_refuse)}: "
            f"{sorted(set(should_refuse) - set(refused))} did not")

    def test_the_exempt_tools_are_genuinely_reachable_when_unbound(self):
        """The OTHER side of the enumeration above, and the reason removing a
        name from `BINDS_WITHOUT_A_BOUND_SPINE` here is not a silent coverage
        loss. That set is a hand copy of the door's own constant; the test above
        would catch a name it lists that the door still refuses only as an
        unexplained pass. So each exempt tool is driven unbound and asserted to
        reach its OWN dispatch -- proved by the refusal being about the ARGUMENTS
        rather than about nothing being bound.

        Together the two tests are two-sided: a name the door exempts but this
        set does not fails the test above; a name this set exempts but the door
        refuses fails here. Neither can drift alone."""
        # Deliberately bad arguments: what is measured is WHICH refusal arrives,
        # so each tool must get past the uniform gate and refuse on its own
        # grounds. `spine_open` gets an empty spec; `spine_bind` an empty path.
        probes = {
            "spine_open": {"work_id": "x", "spec": {}},
            "spine_bind": {"spine_file": ""},
        }
        exempt = sorted(BINDS_WITHOUT_A_BOUND_SPINE)
        self.assertEqual(sorted(probes), exempt,
                         "an exempt tool has no probe here, so it is unmeasured")
        calls = [(40 + i, name, probes[name]) for i, name in enumerate(exempt)]
        run = drive_door(unbound_env(), calls)
        self.assertEqual(0, run.returncode, f"the door died; stderr:\n{run.stderr}")
        for mid, name, _ in calls:
            text = run.tool_text(mid)
            self.assertTrue(run.is_error(mid), f"{name} should still refuse bad arguments: {text}")
            self.assertNotIn(
                "no spine is bound", text,
                f"{name} is listed as reachable with nothing bound, but the uniform gate "
                f"refused it before its own dispatch was reached -- it only works on an "
                f"already-bound door, which is the inverse of its purpose")
            self.assertIn(name, text, f"{name}'s own refusal does not name the tool: {text}")

    def test_stdout_stays_pure_json_rpc_while_refusing(self):
        """`constraint:stdout-is-the-protocol-channel`. A refusal printed to
        stdout would corrupt the transport it travels on."""
        run = drive_door(unbound_env(), [(2, "spine_status", {}), (3, "spine_close", {})])
        # Assert the answers exist FIRST: a door that died writes no stdout at
        # all, and a loop over nothing would pass this vacuously.
        for mid in (2, 3):
            self.assertTrue(run.is_error(mid))
        for line in run.stdout.splitlines():
            if not line.strip():
                continue
            msg = json.loads(line)  # raises if the door wrote prose to stdout
            self.assertEqual("2.0", msg.get("jsonrpc"), f"non-JSON-RPC line: {line}")


# --------------------------------------------------------------------------- #
# 3. Bind on open: the gate's actual exit criterion.
# --------------------------------------------------------------------------- #

HAS_GIT = shutil.which("git") is not None


def stage_a_checkout(into: Path) -> Path:
    """A throwaway git checkout carrying this repo's own `scripts/`.

    `spine_open` on an UNBOUND door derives the primary checkout from the
    server script's own location (`_primary_checkout_for_lifecycle`) -- there is
    no bound spine to derive it from, which is the whole point. So a test that
    ran the repo's own script would open its work in the DEVELOPER'S REAL
    CHECKOUT. Staging a copy is what keeps this test's `git worktree add`
    inside `into`, and it is a faithful staging rather than a workaround: an
    installed constellation really does ship `scripts/` inside the checkout it
    serves."""
    repo = into / "repo"
    repo.mkdir()
    shutil.copytree(ROOT / "scripts", repo / "scripts")
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)],
                   check=True, capture_output=True)
    for key, value in (("user.email", "door@example.invalid"), ("user.name", "Door Test")):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "init"],
                   check=True, capture_output=True)
    return repo


def spec_for(work_id: str) -> dict:
    return {
        "work_id": work_id, "type": "gated",
        "gate": [{
            "id": "m1", "title": "a gate to claim against", "imperative": "do the thing",
            "postconditions": [{"id": "c1", "statement": "done", "kind": "artifact",
                                "evidence_type": "user-decision"}],
        }],
    }


@unittest.skipUnless(HAS_GIT, "git not available")
class BindOnOpenTests(unittest.TestCase):
    """`decision:bind-on-open-over-new-verb`, end to end and in one process.

    The epic's exit criterion, verbatim: a session started with NO `SPINE_FILE`
    calls `spine_open`, gets bound, and drives a real spine without touching the
    CLI. The load-bearing assertion is that **`claim` then succeeds** -- a
    transcript that stops at `spine_status` proves only that `SPINE` moved,
    while `claim` is what proves `SESSION` moved with it. `open_work` returns
    three binding values and two of them are identity; binding one leaves
    `run_engine` omitting `--session-id`, and the engine refuses a claim with no
    session. A door that cannot claim is not bound."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = stage_a_checkout(Path(self.tmp.name))
        self.server = self.repo / "scripts" / "mcp_spine_server.py"

    def tearDown(self):
        self.tmp.cleanup()

    def _env(self) -> dict:
        # `spine_open` runs real git commands including `git commit`, so author
        # identity comes from env vars rather than an ambient global gitconfig
        # that a CI runner may not have.
        return {
            "PATH": os.environ.get("PATH", ""), "SPINE_PARENT": "unknown",
            "GIT_AUTHOR_NAME": "Door Test", "GIT_COMMITTER_NAME": "Door Test",
            "GIT_AUTHOR_EMAIL": "door@example.invalid",
            "GIT_COMMITTER_EMAIL": "door@example.invalid",
        }

    def _drive(self, calls: list[tuple[int, str, dict]]) -> DoorRun:
        messages = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize",
             "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                        "clientInfo": {"name": "bind-test", "version": "0"}}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
        ]
        for mid, tool, args in calls:
            messages.append({"jsonrpc": "2.0", "id": mid, "method": "tools/call",
                             "params": {"name": tool, "arguments": args}})
        proc = subprocess.Popen(
            [sys.executable, str(self.server)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", env=self._env(), cwd=str(self.repo),
        )
        out, err = proc.communicate(
            "\n".join(json.dumps(m) for m in messages) + "\n", timeout=180)
        return DoorRun(out, err, proc.returncode)

    def test_unbound_refuses_then_open_binds_then_claim_succeeds(self):
        run = self._drive([
            (2, "spine_status", {}),
            (3, "spine_open", {"work_id": "bound-work", "spec": spec_for("bound-work")}),
            (4, "spine_lease", {"action": "claim", "claimed_by": "implementer"}),
            (5, "spine_status", {}),
        ])
        self.assertEqual(0, run.returncode, f"the door died; stderr:\n{run.stderr}")

        # 1. Unbound: refuses by name.
        self.assertTrue(run.is_error(2))
        self.assertIn("no spine is bound", run.tool_text(2))

        # 2. spine_open mints a real spine and binds THIS process to it.
        self.assertFalse(run.is_error(3), run.tool_text(3))
        opened = json.loads(run.tool_text(3))
        new_spine = Path(opened["SPINE_FILE"])
        self.assertTrue(new_spine.is_file())
        self.assertTrue(
            new_spine.is_relative_to(self.repo),
            f"spine_open escaped the staged checkout: {new_spine}")

        # 3. THE criterion: a MUTATING verb succeeds, in the same process, with
        #    no relaunch and no CLI. This is what proves SESSION was rebound.
        self.assertFalse(
            run.is_error(4),
            f"claim failed after bind-on-open -- SESSION was not rebound: {run.tool_text(4)}")
        self.assertIn("claimed lease", run.tool_text(4))
        self.assertIn(opened["SPINE_SESSION"], run.tool_text(4))

        # 4. The door is now genuinely driving the NEW spine.
        self.assertFalse(run.is_error(5))
        self.assertIn("LEASE active: " + opened["SPINE_SESSION"], run.tool_text(5))

    def test_a_rebind_is_refused_while_this_process_holds_an_active_lease(self):
        """`decision:one-spine-per-process-stands`. Rebinding out from under a
        lease this door holds would leave it held by nobody.

        The drive STOPS at the refusal on purpose. The "no worktree was minted"
        assertion is about a moment in time, and a later successful re-open in
        the same transcript would satisfy the same path check and quietly make
        this pass for the wrong reason."""
        run = self._drive([
            (2, "spine_open", {"work_id": "first-work", "spec": spec_for("first-work")}),
            (3, "spine_lease", {"action": "claim", "claimed_by": "implementer"}),
            (4, "spine_open", {"work_id": "second-work", "spec": spec_for("second-work")}),
        ])
        self.assertEqual(0, run.returncode, f"the door died; stderr:\n{run.stderr}")
        self.assertFalse(run.is_error(2), run.tool_text(2))
        self.assertFalse(run.is_error(3), run.tool_text(3))

        self.assertTrue(run.is_error(4), "a rebind under a held lease was allowed")
        self.assertIn("still holds an active lease", run.tool_text(4))
        self.assertFalse(
            (self.repo / ".worktrees" / "second-work").exists(),
            "the refused rebind still created a worktree -- it must refuse BEFORE minting")

    def test_releasing_the_lease_is_a_real_way_forward_not_just_advice(self):
        """The refusal above tells the caller to release first. A refusal whose
        stated remedy does not actually work is worse than no refusal, so the
        remedy is measured rather than asserted in prose."""
        run = self._drive([
            (2, "spine_open", {"work_id": "first-work", "spec": spec_for("first-work")}),
            (3, "spine_lease", {"action": "claim", "claimed_by": "implementer"}),
            (4, "spine_lease", {"action": "release"}),
            (5, "spine_open", {"work_id": "second-work", "spec": spec_for("second-work")}),
            (6, "spine_lease", {"action": "claim", "claimed_by": "implementer"}),
        ])
        self.assertEqual(0, run.returncode, f"the door died; stderr:\n{run.stderr}")
        for mid in (2, 3, 4):
            self.assertFalse(run.is_error(mid), run.tool_text(mid))
        self.assertFalse(
            run.is_error(5), f"a rebind after release was refused: {run.tool_text(5)}")
        second = json.loads(run.tool_text(5))
        self.assertFalse(run.is_error(6), run.tool_text(6))
        self.assertIn(
            second["SPINE_SESSION"], run.tool_text(6),
            "the door claimed under the OLD session -- the rebind moved SPINE but not SESSION")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
