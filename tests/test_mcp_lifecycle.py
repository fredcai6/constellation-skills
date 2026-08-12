"""Tests for the MCP lifecycle door -- `spine_open`/`spine_close`
(`scripts/mcp_spine_server.py`'s `call_lifecycle_tool`, issue #559, C3/g3).

Frozen contract: `.agent-work/epic-559/c3-lifecycle/LIFECYCLE_CONTRACT.md` section 6.
`scripts/spine_lifecycle.py`'s `open_work`/`close_work` are g1/g2's, frozen; this
file tests the DOOR wiring onto them, never their own behaviour (that lives in
`tests/test_spine_lifecycle.py`).

The existing pin in `tests/test_mcp_identity.py`
(`IdentityBindingPinTests.test_call_tool_can_only_produce_content_two_ways`) was
written for `call_tool`, a PASS-THROUGH to the engine. `call_lifecycle_tool` is
not a pass-through -- neither `spine_open` nor `spine_close` ever calls
`run_engine` -- so it is not covered by that pin and inheriting it would be
exactly the "a guard written for one hazard covers the other by accident"
failure `_identity_violation`'s own docstring records as history. This file
ships the lifecycle surface's OWN containment pin instead, per
`LIFECYCLE_CONTRACT.md` section 6:

  1. An AST pin over `call_lifecycle_tool` restricting its own return shapes,
     with a mutated positive control.
  2. An assertion that `_spine_open` (its own top-level `ast.FunctionDef`,
     found by name, the same way the choke-point pin finds `call_tool`) never
     references `SPINE`, `SESSION` or `run_engine`, with a mutated positive
     control.
  3. Containment on `spine_open`'s one caller-derived path (the worktree
     `work_id` resolves to), reusing `_resolve_confined`'s posture rather than
     a second predicate.

Plus a full stdio JSON-RPC round trip (required evidence): `spine_open`
creates a real worktree and spine in a throwaway git repo under `tmp_path`;
that spine is driven to terminal through the existing engine door tools;
`spine_close` archives it; the verdict names the branch, the commit, and
"ready to PR".
"""

from __future__ import annotations

import ast
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "scripts" / "mcp_spine_server.py"
ENGINE = ROOT / "scripts" / "checklist_engine.py"

SOURCE = SERVER.read_text(encoding="utf-8")

HAS_GIT = __import__("shutil").which("git") is not None
requires_git = pytest.mark.skipif(not HAS_GIT, reason="git not available")

#: The three identifiers `_spine_open`'s own dispatch path may never
#: reference (LIFECYCLE_CONTRACT.md section 6) -- the bound-spine globals and
#: the engine pass-through, none of which apply to a spine that does not
#: exist yet.
BANNED_IDENTIFIERS = {"SPINE", "SESSION", "run_engine"}


def _find_funcdef(tree: ast.AST, name: str) -> ast.FunctionDef:
    return next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name)


def _referenced_names(fn: ast.FunctionDef, banned: set[str]) -> list[str]:
    return sorted({n.id for n in ast.walk(fn) if isinstance(n, ast.Name) and n.id in banned})


def _init_repo(path: Path) -> None:
    subprocess.run(["git", "init", "-q", str(path)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(path), "-c", "user.email=t@t", "-c", "user.name=t",
         "commit", "-q", "--allow-empty", "-m", "init"],
        check=True, capture_output=True,
    )


def _load_module(spine: Path, session: str = ""):
    """Import a FRESH copy of the server module bound to `spine`, the same
    pattern `tests/test_mcp_identity.py::IdentityBindingPinTests._load_module`
    uses -- a fresh module object per call so one test's monkeypatch (e.g. on
    `module.spine_lifecycle.open_work`) cannot leak into another, and a fresh
    binding is what makes "bound at import" testable at all.

    `SPINE_PARENT` is pinned to `"unknown"` here rather than left to whatever
    the *running test process's own* environment happens to carry (a real
    hazard: this suite may itself run under a dispatched crew with its own
    `SPINE_PARENT` set) -- tests that care about a specific `parent` override
    it explicitly."""
    spine.parent.mkdir(parents=True, exist_ok=True)
    if not spine.exists():
        spine.write_text("{}", encoding="utf-8")
    env_patch = {
        "SPINE_FILE": str(spine),
        "SPINE_ENGINE": str(ENGINE),
        "SPINE_SESSION": session,
        "SPINE_CALLLOG": str(spine.parent / "lifecycle_pin_calls.jsonl"),
        "SPINE_START_MARKER": str(spine.parent / "lifecycle_pin_started"),
        "SPINE_PARENT": "unknown",
    }
    saved = {k: os.environ.get(k) for k in env_patch}
    os.environ.update(env_patch)
    try:
        spec = importlib.util.spec_from_file_location(
            f"_lifecycle_door_{abs(hash((str(spine), session))) % 100000}", SERVER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


# --------------------------------------------------------------------------- #
# 1. The AST pin over call_lifecycle_tool's own return shapes.
# --------------------------------------------------------------------------- #

class CallLifecycleToolChokePointPinTests(unittest.TestCase):
    """`call_lifecycle_tool` is a NEW MODULE-LEVEL SIBLING of `call_tool`, not
    a branch inside it -- `call_tool`'s own choke-point pin resolves ITS
    `ast.FunctionDef` by name and walks only that subtree, so it never sees
    this function at all. Without an equivalent pin here, a future edit could
    grow `call_lifecycle_tool` a third way to answer (a mutate-then-return
    leak, an inlined dict literal, a read from somewhere the two dispatch
    functions never touched) with nothing to catch it."""

    ALLOWED = {"_spine_open", "_spine_close"}

    def test_call_lifecycle_tool_can_only_produce_content_two_ways(self):
        tree = ast.parse(SOURCE)
        fn = _find_funcdef(tree, "call_lifecycle_tool")
        offenders = []
        for node in ast.walk(fn):
            if not isinstance(node, ast.Return) or node.value is None:
                continue
            v = node.value
            ok = isinstance(v, ast.Call) and isinstance(v.func, ast.Name) and v.func.id in self.ALLOWED
            if not ok:
                offenders.append(f"line {node.lineno}: {ast.unparse(v)[:80]}")
        self.assertEqual(
            [], offenders,
            "call_lifecycle_tool now returns content some way other than "
            f"_spine_open(args)/_spine_close(args): {offenders}. Route new lifecycle "
            "logic through its own top-level dispatch function instead of adding a "
            "third way for call_lifecycle_tool itself to answer.",
        )

    def test_the_lifecycle_choke_point_pin_can_fail(self):
        """Positive control, mirroring
        `tests/test_mcp_identity.py::IdentityBindingPinTests.test_the_choke_point_pin_can_fail`:
        bind the result, mutate it, return the name -- a third way to answer
        that the pin above must catch."""
        leaky = (
            "def call_lifecycle_tool(name, args):\n"
            "    out = _spine_open(args)\n"
            "    out['content'][0]['text'] += 'leak'\n"
            "    return out\n"
        )
        fn = next(n for n in ast.walk(ast.parse(leaky)) if isinstance(n, ast.FunctionDef))
        offenders = []
        for node in ast.walk(fn):
            if isinstance(node, ast.Return) and node.value is not None:
                v = node.value
                ok = (isinstance(v, ast.Call) and isinstance(v.func, ast.Name)
                      and v.func.id in self.ALLOWED)
                if not ok:
                    offenders.append(ast.unparse(v))
        self.assertTrue(
            offenders,
            "the lifecycle choke-point detector did not flag a mutate-then-return leak "
            "-- it is incapable of failing and is therefore not evidence",
        )


# --------------------------------------------------------------------------- #
# 2. spine_open never references SPINE, SESSION or run_engine.
# --------------------------------------------------------------------------- #

class SpineOpenNeverBindsIdentityTests(unittest.TestCase):
    """`spine_open` acts on a spine that does not exist yet and must never
    touch the identity this door is itself bound to -- LIFECYCLE_CONTRACT.md
    section 6's "must never touch SPINE/SESSION", made a checked fact rather
    than a claim, over `_spine_open`'s own source (found by name, the same
    way the choke-point pin finds `call_tool`)."""

    def test_spine_open_never_references_spine_session_or_run_engine(self):
        tree = ast.parse(SOURCE)
        fn = _find_funcdef(tree, "_spine_open")
        offenders = _referenced_names(fn, BANNED_IDENTIFIERS)
        self.assertEqual(
            [], offenders,
            f"_spine_open's own source now references {offenders} -- spine_open must act "
            "purely on ambient, server-launch-time state (SPINE_FILE/SPINE_PARENT re-read "
            "fresh) and never on the identity THIS door happens to be bound to, or a call "
            "meant to open unrelated work could be redirected onto the bound spine",
        )

    def test_the_spine_open_identity_pin_can_fail(self):
        """Positive control: a hypothetical `_spine_open` that answers via the
        engine pass-through (exactly the forbidden shape) must be caught."""
        leaky = (
            "def _spine_open(args):\n"
            "    if SESSION:\n"
            "        return as_result(run_engine('current', mutating=False))\n"
            "    return as_result(run_engine('current', mutating=False, file=SPINE))\n"
        )
        fn = next(n for n in ast.walk(ast.parse(leaky)) if isinstance(n, ast.FunctionDef))
        offenders = _referenced_names(fn, BANNED_IDENTIFIERS)
        self.assertTrue(
            offenders,
            "the SPINE/SESSION/run_engine detector did not flag a function that plainly "
            "references all three -- it is incapable of failing and is therefore not evidence",
        )

    def test_spine_close_is_not_held_to_the_same_ban(self):
        """Sanity check on the pin's OWN scope: `spine_close` acts on the
        bound spine BY DESIGN (LIFECYCLE_CONTRACT.md section 6's opposite
        identity posture), so it legitimately references `SPINE` -- proving
        the ban above is `_spine_open`-specific, not a whole-module sweep
        that would make `_spine_close` unwritable."""
        tree = ast.parse(SOURCE)
        fn = _find_funcdef(tree, "_spine_close")
        referenced = _referenced_names(fn, {"SPINE"})
        self.assertEqual(["SPINE"], referenced)


# --------------------------------------------------------------------------- #
# 3. Containment on spine_open's one caller-derived path.
# --------------------------------------------------------------------------- #

class SpineOpenContainmentTests(unittest.TestCase):
    """`work_id` is the only caller-supplied value `spine_open` turns into a
    filesystem path (the candidate worktree). Confined through
    `_resolve_confined` -- the SAME predicate `_identity_violation` already
    uses for `--from-child`/`--delta` -- parameterized with `wt_root` as
    `bound_dir` instead of the default `SPINE.parent`, never a second,
    differently-shaped check."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_resolve_confined_is_genuinely_reused_with_a_different_bound_dir(self):
        """Direct proof that `_resolve_confined` -- not a reimplementation --
        is what spine_open's containment runs on, parameterized by a
        `bound_dir` unrelated to `SPINE.parent`."""
        spine = self.root / "driving" / "spine.json"
        module = _load_module(spine, "")
        bound = self.root / "wt-root"
        bound.mkdir()

        self.assertNotEqual(
            module.SPINE.parent, bound,
            "the test's own bound_dir must be unrelated to SPINE.parent, or this proves "
            "nothing about genuine reuse with a DIFFERENT boundary",
        )

        inside, escapes_in = module._resolve_confined(
            str(bound / "child"), join_relative_to=None, bound_dir=bound)
        self.assertFalse(escapes_in)

        outside, escapes_out = module._resolve_confined(
            str(self.root / "elsewhere"), join_relative_to=None, bound_dir=bound)
        self.assertTrue(escapes_out)

    def test_spine_open_calls_resolve_confined_in_its_own_source(self):
        """Text-level proof the LIVE dispatch path actually invokes the
        predicate above (not merely that the predicate exists, unused)."""
        tree = ast.parse(SOURCE)
        fn = _find_funcdef(tree, "_spine_open")
        calls = {n.func.id for n in ast.walk(fn)
                  if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        self.assertIn("_resolve_confined", calls)

    @requires_git
    def test_spine_open_refuses_before_open_work_ever_runs_when_the_worktree_would_escape(self):
        """Live, end-to-end: a `work_id` whose LAST segment is `".."` makes
        `worktree_path_for` return a path that resolves OUTSIDE `wt_root` (its
        own parent). This is refused before `spine_lifecycle.open_work` is
        ever called -- proved by a spy that raises if reached, not merely by
        reading the result -- even though `open_work`'s OWN internal
        `run_crew.validate_work_id` would also refuse this `work_id`: this
        check is defense in depth, and this test is what makes it a genuine
        gate rather than dead code shadowed entirely by that later check."""
        repo = self.root / "repo"
        repo.mkdir()
        _init_repo(repo)
        bound_spine = repo / ".agent-work" / "driving" / "spine.json"
        module = _load_module(bound_spine, "")

        called = []

        def spy(*args, **kwargs):
            called.append((args, kwargs))
            raise AssertionError("open_work must not be reached when the door's own "
                                  "containment check refuses first")

        original_open_work = module.spine_lifecycle.open_work
        module.spine_lifecycle.open_work = spy
        # `_spine_open` deliberately RE-READS `SPINE_FILE` from the environment
        # at call time (never the module's own bound `SPINE` -- that is the
        # whole point of the identity pin above), so it must still be set now,
        # not merely during `_load_module`'s own import (which already
        # restored the surrounding environment by the time this line runs).
        saved_spine_file = os.environ.get("SPINE_FILE")
        os.environ["SPINE_FILE"] = str(bound_spine)
        try:
            result = module._spine_open({
                "work_id": "attack/..",
                "spec": {"work_id": "attack/..", "type": "gated", "gate": []},
            })
        finally:
            module.spine_lifecycle.open_work = original_open_work
            if saved_spine_file is None:
                os.environ.pop("SPINE_FILE", None)
            else:
                os.environ["SPINE_FILE"] = saved_spine_file

        self.assertEqual([], called, "open_work was reached despite the escaping work_id")
        self.assertTrue(result["isError"])
        self.assertIn("outside", result["content"][0]["text"])


# --------------------------------------------------------------------------- #
# 4. Required evidence: the full stdio JSON-RPC round trip.
# --------------------------------------------------------------------------- #

class _McpRpcClient:
    """Minimal newline-delimited JSON-RPC 2.0 client, spawning the real server
    process -- the same shape as `tests/test_mcp_spine_server.py::McpRpcClient`,
    kept local rather than imported so this file has no cross-test-module
    dependency."""

    def __init__(self, spine_file: Path, session_id: str, base: Path):
        env = {"PATH": os.environ.get("PATH", "")}
        # spine_open/spine_close (unlike the engine-only tools this shape was
        # copied from) run REAL git commands, including `git commit` --
        # deterministic author/committer identity via env vars, never the
        # ambient global gitconfig (absent here: only PATH is forwarded, and
        # a real CI runner may have none configured either).
        env["GIT_AUTHOR_NAME"] = env["GIT_COMMITTER_NAME"] = "Lifecycle Test"
        env["GIT_AUTHOR_EMAIL"] = env["GIT_COMMITTER_EMAIL"] = "lifecycle-test@example.invalid"
        env["SPINE_FILE"] = str(spine_file)
        env["SPINE_ENGINE"] = str(ENGINE)
        env["SPINE_SESSION"] = session_id
        env["SPINE_PARENT"] = "unknown"
        env["SPINE_CALLLOG"] = str(base / "mcp_calls.jsonl")
        env["SPINE_START_MARKER"] = str(base / "mcp_server_started")
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
        self.proc.stdin.close()
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()


@requires_git
class FullStdioRoundTripTests(unittest.TestCase):
    """Required evidence (criterion 4): `tools/call spine_open` creates a real
    worktree and spine in a throwaway git repo under `tmp_path`; that spine is
    driven to terminal through the door's own existing engine tools
    (`spine_lease`, `spine_start`, `spine_evidence`, `spine_advance`); `tools/call
    spine_close` archives it; the verdict names the branch, the commit, and
    "ready to PR"."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        _init_repo(self.repo)
        self._clients = []

    def tearDown(self):
        for c in self._clients:
            c.close()
        self.tmp.cleanup()

    def _client(self, spine_file: Path, session_id: str) -> _McpRpcClient:
        spine_file.parent.mkdir(parents=True, exist_ok=True)
        c = _McpRpcClient(spine_file, session_id, base=self.root)
        self._clients.append(c)
        return c

    def test_open_drive_close_round_trip_names_branch_commit_and_ready_to_pr(self):
        work_id = "roundtrip-work"

        # Door A: bound to a placeholder spine INSIDE the repo (never read by
        # spine_open -- only its own directory matters, to derive the primary
        # checkout).
        door_a = self._client(self.repo / ".agent-work" / "driving" / "spine.json", "driving-session")

        spec = {
            "work_id": work_id,
            "type": "gated",
            "gate": [{
                "id": "m1", "title": "do it", "imperative": "do the thing",
                "postconditions": [
                    {"id": "c1", "statement": "human decided", "kind": "artifact",
                     "evidence_type": "user-decision"},
                ],
            }],
        }
        opened_raw = door_a.call("spine_open", work_id=work_id, spec=spec, base="HEAD")
        self.assertFalse(opened_raw["isError"], opened_raw)
        opened = json.loads(opened_raw["content"][0]["text"])

        new_spine = Path(opened["SPINE_FILE"])
        self.assertTrue(new_spine.is_file(), "spine_open did not write a real spine file")
        new_worktree = Path(opened["worktree"])
        self.assertTrue((new_worktree / ".git").exists(), "spine_open did not create a real worktree")
        self.assertEqual(opened["branch"], work_id)

        # Door B: bound to the NEW spine spine_open just created -- the
        # process a real dispatched crew would be launched with.
        door_b = self._client(new_spine, opened["SPINE_SESSION"])

        claimed = door_b.call("spine_lease", action="claim", claimed_by="test", worktree=".")
        self.assertFalse(claimed["isError"], claimed)
        started = door_b.call("spine_start", task_id="m1")
        self.assertFalse(started["isError"], started)
        attached = door_b.call("spine_evidence", action="attach", task_id="m1",
                                evidence_type="user-decision", fields={"decision": "go"})
        self.assertFalse(attached["isError"], attached)
        advanced = door_b.call("spine_advance", task_id="m1", mechanical=True)
        self.assertFalse(advanced["isError"], advanced)
        released = door_b.call("spine_lease", action="release")
        self.assertFalse(released["isError"], released)

        closed_raw = door_b.call("spine_close")
        self.assertFalse(closed_raw["isError"], closed_raw)
        closed = json.loads(closed_raw["content"][0]["text"])

        self.assertEqual(work_id, closed["work_id"])
        self.assertEqual(work_id, closed["branch"])
        self.assertTrue(closed["head"], "the verdict must name the new commit")
        message = closed["message"]
        self.assertIn(work_id, message, "the verdict does not name the branch")
        self.assertIn(closed["head"], message, "the verdict does not name the commit")
        self.assertIn("ready to PR", message)

        archive_dir = Path(closed["archive"])
        self.assertTrue(archive_dir.is_dir())
        self.assertTrue((archive_dir / "spine.json").is_file(),
                         "the spine itself must have moved into the archive")


if __name__ == "__main__":
    unittest.main()
