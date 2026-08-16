#!/usr/bin/env python3
"""The door stands in the bound spine's own worktree for an engine call
(issue #568, the g1b delta).

`checklist_engine.origin_worktree_refusal` compares a spine's stamped
`origin.worktree` against the engine's AMBIENT cwd, and `run_engine` calls
`checklist_engine.main(argv)` IN PROCESS. The door's own process is launched
wherever its caller happened to stand, so before this change the very first
verb on a spine `spine_open` had just created in a brand-new worktree was
refused by construction: the door could not already be inside a directory that
did not exist a moment earlier.

`run_engine` now chdirs into the bound spine's worktree for the duration of
that one call and restores the previous directory in a `finally`. These tests
pin all four halves of that contract:

  * it really stands there DURING the call (observed from inside the engine
    call, not inferred from the result);
  * the previous cwd is restored afterwards -- on success, on an exception, and
    on `SystemExit`;
  * a spine whose worktree cannot be resolved is NOT a failure: no chdir, the
    call proceeds exactly as it did before;
  * the door remains a single-threaded stdio loop, which is what makes a
    process-global `chdir` safe here at all.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import os
import shutil
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

HAS_GIT = shutil.which("git") is not None
requires_git = pytest.mark.skipif(not HAS_GIT, reason="git not available")


def _init_repo(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", str(path)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(path), "-c", "user.email=t@t", "-c", "user.name=t",
         "commit", "-q", "--allow-empty", "-m", "init"],
        check=True, capture_output=True,
    )


def _spine_payload(worktree: Path) -> dict:
    """A minimal one-gate spine carrying the `origin` stamp the engine guards
    on -- the shape `init_work_area.instantiate_spine` / `spine_lifecycle.
    open_work` write at creation."""
    return {
        "work_id": "door-cwd",
        "type": "gated",
        "origin": {"work_id": "door-cwd", "worktree": str(worktree), "opened_by": "test"},
        "items": ["m1"],
        "tasks": {
            "m1": {
                "id": "m1", "title": "do it", "imperative": "do the thing",
                "preconditions": [],
                "postconditions": [{"id": "c1", "statement": "done", "check": None, "satisfied": False}],
                "constraints": [], "directives": None, "child_checklist": None,
                "status": "pending", "status_detail": {}, "result": None,
                "finding": None, "evidence": [], "rework_count": 0,
            }
        },
        "consolidation": None, "triage_candidates": [], "blockers": [],
    }


_MODULE_SEQ = [0]


def _load_module(spine: Path, session: str = "door-cwd-session", logdir: Path | None = None):
    """Import a FRESH copy of the server bound to `spine` -- the same pattern
    `tests/test_mcp_lifecycle.py::_load_module` uses, because the binding is
    read from the environment at import time.

    `logdir` places the door's own call log OUTSIDE the spine's directory when
    a test deletes that directory mid-run; it defaults to beside the spine."""
    spine.parent.mkdir(parents=True, exist_ok=True)
    logdir = logdir if logdir is not None else spine.parent
    env_patch = {
        "SPINE_FILE": str(spine),
        "SPINE_ENGINE": str(ENGINE),
        "SPINE_SESSION": session,
        "SPINE_CALLLOG": str(logdir / "door_cwd_calls.jsonl"),
        "SPINE_START_MARKER": str(logdir / "door_cwd_started"),
        "SPINE_PARENT": "unknown",
    }
    saved = {k: os.environ.get(k) for k in env_patch}
    os.environ.update(env_patch)
    _MODULE_SEQ[0] += 1
    try:
        spec = importlib.util.spec_from_file_location(f"_door_cwd_{_MODULE_SEQ[0]}", SERVER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


class _CwdSpy:
    """Stand in for `checklist_engine.main` and record where the process was
    standing when it ran -- the only honest way to observe "for the duration of
    the call" rather than infer it from an outcome."""

    def __init__(self, *, code: int = 0, raises: BaseException | None = None):
        self.code = code
        self.raises = raises
        self.seen: list[str] = []

    def __call__(self, argv):
        self.seen.append(os.getcwd())
        if self.raises is not None:
            raise self.raises
        return self.code


class _EngineSpyMixin:
    """Install a `_CwdSpy` over the engine's `main` AND take it back off again.

    `module.checklist_engine` is the engine module object, which is SHARED
    across every freshly-loaded copy of the server -- assigning to its `main`
    without restoring leaks a fake engine into every later test in the same
    process (observed: it reds `tests/test_mcp_identity.py` when the two files
    run in one session)."""

    def spy_on_engine(self, module, **kwargs) -> _CwdSpy:
        spy = _CwdSpy(**kwargs)
        engine = module.checklist_engine
        original = engine.main
        engine.main = spy
        self.addCleanup(setattr, engine, "main", original)
        return spy


@requires_git
class DoorStandsInTheSpinesWorktreeTests(_EngineSpyMixin, unittest.TestCase):
    """The positive half: where the engine call actually runs."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name).resolve() / "repo"
        _init_repo(self.repo)
        self.spine = self.repo / ".agent-work" / "door-cwd" / "spine.json"
        self.spine.parent.mkdir(parents=True, exist_ok=True)
        self.spine.write_text(json.dumps(_spine_payload(self.repo)), encoding="utf-8")
        self.module = _load_module(self.spine)
        self.addCleanup(self.tmp.cleanup)

    def test_engine_call_runs_inside_the_bound_spines_worktree(self):
        spy = self.spy_on_engine(self.module)
        here = os.getcwd()
        self.module.run_engine("current", mutating=False)
        self.assertEqual([str(self.repo)], [str(Path(p).resolve()) for p in spy.seen],
                         "the engine call did not run inside the spine's own worktree")
        self.assertNotEqual(str(self.repo), str(Path(here).resolve()),
                            "fixture is not exercising anything: the test already ran in the worktree")

    def test_a_guarded_verb_on_a_foreign_worktree_spine_now_succeeds(self):
        """End to end through the REAL engine: `claim` is origin-guarded, the
        spine belongs to a worktree that is not this process's directory, and
        it must go through -- this is the `spine_open` -> `claim` round trip
        that was impossible by construction."""
        rec = self.module.run_engine("claim", "--claimed-by", "test")
        self.assertEqual(0, rec["code"], rec["stdout"] + rec["stderr"])
        self.assertNotIn("refused", (rec["stdout"] + rec["stderr"]).lower())
        state = json.loads(self.spine.read_text(encoding="utf-8"))
        self.assertEqual("door-cwd-session", state["engine_session"]["session_id"])

    def test_cwd_is_restored_after_a_successful_call(self):
        before = os.getcwd()
        self.module.run_engine("current", mutating=False)
        self.assertEqual(before, os.getcwd())

    def test_cwd_is_restored_when_the_engine_raises(self):
        self.spy_on_engine(self.module, raises=RuntimeError("boom"))
        before = os.getcwd()
        rec = self.module.run_engine("current", mutating=False)
        self.assertEqual(before, os.getcwd(), "cwd leaked after an engine exception")
        self.assertEqual(1, rec["code"])
        self.assertIn("boom", rec["stderr"])

    def test_cwd_is_restored_when_the_engine_exits(self):
        self.spy_on_engine(self.module, raises=SystemExit(2))
        before = os.getcwd()
        rec = self.module.run_engine("current", mutating=False)
        self.assertEqual(before, os.getcwd(), "cwd leaked after SystemExit")
        self.assertEqual(2, rec["code"])

    def test_a_refused_call_also_restores_the_cwd(self):
        before = os.getcwd()
        rec = self.module.run_engine("start", "no-such-task")
        self.assertNotEqual(0, rec["code"])
        self.assertEqual(before, os.getcwd())


class UnresolvableWorktreeIsNotAFailureTests(_EngineSpyMixin, unittest.TestCase):
    """A door that cannot locate a tree must not become a door that cannot
    run: no chdir, no refusal, the pre-change behaviour exactly."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def _module_on_a_non_repo_spine(self):
        loose = Path(self.tmp.name).resolve() / "not-a-repo"
        spine = loose / "spine.json"
        spine.parent.mkdir(parents=True, exist_ok=True)
        spine.write_text(json.dumps(_spine_payload(loose)), encoding="utf-8")
        return _load_module(spine, logdir=Path(self.tmp.name)), spine

    def test_spine_outside_any_worktree_still_runs_and_does_not_move(self):
        module, _spine = self._module_on_a_non_repo_spine()
        spy = self.spy_on_engine(module)
        before = os.getcwd()
        rec = module.run_engine("current", mutating=False)
        self.assertEqual(0, rec["code"], rec["stderr"])
        self.assertEqual([before], spy.seen,
                         "an unresolvable worktree must leave the process where it was")
        self.assertEqual(before, os.getcwd())

    def test_removed_spine_directory_refuses_without_moving_or_dying(self):
        """The spine's own directory is gone (a closed-out worktree).

        This used to assert the call still SUCCEEDED -- the pre-g3 fail-open
        reading of "a door that cannot locate a tree must not become a door
        that cannot run". Gate g3 (issue #603) settled the other half of that
        sentence: a door whose spine is not there must not answer as though it
        were. `decision:fail-closed-beats-fail-open`. So the call now refuses,
        by name, before the engine is reached at all.

        What this class is actually about is UNCHANGED and still asserted: the
        process does not move and does not die. An unresolvable worktree is
        still not a failure -- see the test above, whose spine exists and which
        still runs to a clean exit outside any repo. Only the case where there
        is nothing left to read now refuses."""
        module, spine = self._module_on_a_non_repo_spine()
        spy = self.spy_on_engine(module)
        shutil.rmtree(spine.parent)
        before = os.getcwd()
        rec = module.run_engine("current", mutating=False)
        self.assertEqual(2, rec["code"])
        self.assertIn(str(spine), rec["stderr"], "the refusal must name the path")
        self.assertIn("rebind", rec["stderr"])
        self.assertEqual([], spy.seen, "a refused call must never reach the engine")
        self.assertEqual(before, os.getcwd())


class SingleThreadedDoorPinTests(unittest.TestCase):
    """`chdir` is process-global, so it is only safe here because the door
    handles exactly one request at a time: `main()` is a plain
    `for line in sys.stdin:` loop that writes each reply before reading the
    next line. This pins that property, so a future change making the door
    concurrent fails HERE and forces the chdir to be reconsidered rather than
    silently corrupting a sibling request's working directory."""

    CONCURRENCY_MODULES = {"threading", "asyncio", "concurrent", "multiprocessing", "_thread"}

    def test_the_server_imports_nothing_concurrent(self):
        tree = ast.parse(SOURCE)
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertEqual(set(), imported & self.CONCURRENCY_MODULES,
                         "the door became concurrent; run_engine's process-global chdir is no longer safe")

    def test_main_is_one_sequential_loop_over_stdin(self):
        main_fn = next(n for n in ast.walk(ast.parse(SOURCE))
                       if isinstance(n, ast.FunctionDef) and n.name == "main")
        loops = [n for n in ast.walk(main_fn) if isinstance(n, (ast.For, ast.AsyncFor))]
        self.assertEqual(1, len(loops), "main() no longer has exactly one request loop")
        self.assertIsInstance(loops[0], ast.For)
        self.assertNotIsInstance(main_fn, ast.AsyncFunctionDef)


if __name__ == "__main__":
    unittest.main()
