#!/usr/bin/env python3
"""A dispatched crew runs in ITS OWN worktree (issue #568, the g1b delta).

`launch_process` is documented as "The ONE place a real crew subprocess is
spawned", and it used to call `subprocess.run` with no `cwd=` at all -- so a
crew inherited the *dispatcher's* working directory, an accident of whoever
happened to launch it. That made the Commander's stated reason ("a dispatched
crew's cwd is its spine's worktree") an assumption rather than a fact, and the
engine's `origin.worktree` guard reads exactly that ambient cwd.

These tests pin the fact, not the assumption. Two halves, deliberately:

  * `CrewSpawnCwdTests` asserts on the value handed to the spawn seam -- the
    `cwd` keyword `dispatch`/`resume` actually pass -- never on a child's
    behaviour inferred from something else.
  * `LaunchProcessCwdTests` spawns a REAL subprocess through the seam and asks
    the child where it is standing, so the keyword is proven to reach the OS
    and not merely to be accepted by the signature.
"""

import contextlib
import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN_CREW = ROOT / "scripts" / "run_crew.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


RC = load_module("run_crew", RUN_CREW)


def write_handoff(root: Path, work_id: str, gate: str, role: str) -> str:
    rel = f".agent-work/{work_id}/crew-handoffs/{gate}-{role}.md"
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("handoff body\n", encoding="utf-8")
    return rel


def result_rel(work_id: str, gate: str, role: str) -> str:
    return f".agent-work/{work_id}/crew-handoffs/{gate}-{role}-result.md"


@contextlib.contextmanager
def recording_launch(RC_mod, *, write_result_at: Path | None = None):
    """Replace the single subprocess seam with a double that RECORDS every
    keyword it was handed, `cwd` included, and spawns nothing."""
    calls: list[dict] = []
    original = RC_mod.launch_process

    def fake(argv, *, stdin, env, stdout_path, stderr_path, cwd=None):
        calls.append({"argv": argv, "stdin": stdin, "env": env, "cwd": cwd,
                      "stdout_path": stdout_path, "stderr_path": stderr_path})
        Path(stdout_path).parent.mkdir(parents=True, exist_ok=True)
        Path(stdout_path).write_text("out\n", encoding="utf-8")
        Path(stderr_path).write_text("err\n", encoding="utf-8")
        if write_result_at is not None:
            Path(write_result_at).parent.mkdir(parents=True, exist_ok=True)
            Path(write_result_at).write_text("RESULT\n", encoding="utf-8")
        return 0

    RC_mod.launch_process = fake
    try:
        yield calls
    finally:
        RC_mod.launch_process = original


class CrewSpawnCwdTests(unittest.TestCase):
    """What the dispatch paths hand to the spawn seam."""

    def test_cli_default_dot_dispatch_passes_an_absolute_repo_cwd(self):
        with tempfile.TemporaryDirectory() as tmp, contextlib.chdir(tmp):
            root = Path(".")
            handoff = write_handoff(root, "issue-1", "g1", "implementer")
            result = result_rel("issue-1", "g1", "implementer")
            defaults = RC.build_parser().parse_args([])
            self.assertEqual(Path("."), defaults.root)
            self.assertEqual(".", defaults.worktree)

            with recording_launch(RC, write_result_at=Path(result)) as calls:
                RC.launch_crew(
                    work_id="issue-1", gate="g1", role="implementer",
                    handoff=handoff, result=result, worktree=defaults.worktree,
                    model="sonnet", launcher="claude", attempt=1,
                    root=defaults.root, entries=[],
                    parent="test-parent",
                )

            spawned_cwd = Path(calls[0]["cwd"])
            self.assertTrue(spawned_cwd.is_absolute())
            self.assertEqual(Path(tmp).resolve(), spawned_cwd)

    def test_cli_default_dot_resume_passes_an_absolute_repo_cwd(self):
        with tempfile.TemporaryDirectory() as tmp, contextlib.chdir(tmp):
            root = Path(".")
            handoff = write_handoff(root, "issue-1", "g1", "implementer")
            result = result_rel("issue-1", "g1", "implementer")
            session = "constellation/issue-1/g1/implementer/attempt-1"
            stdout, stderr = RC.run_log_paths("issue-1", "g1", "implementer", 1, root)
            entries = [{
                "session_name": session, "crew_id": session,
                "work_id": "issue-1", "gate": "g1", "role": "implementer", "attempt": 1,
                "worktree": ".", "status": "running", "abandoned": False,
                "handoff": handoff, "result": result,
                "stdout": RC._relativize(str(stdout), root),
                "stderr": RC._relativize(str(stderr), root),
            }]
            RC.save_registry(RC.registry_path("issue-1", root), entries)
            defaults = RC.build_parser().parse_args(["--resume", session])
            self.assertEqual(Path("."), defaults.root)

            with recording_launch(RC, write_result_at=Path(result)) as calls:
                RC.resume_crew(session=session, root=defaults.root, entries=entries)

            spawned_cwd = Path(calls[0]["cwd"])
            self.assertTrue(spawned_cwd.is_absolute())
            self.assertEqual(Path(tmp).resolve(), spawned_cwd)

    def test_dispatch_passes_an_absolute_worktree_as_the_child_cwd(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            worktree = root / "wt" / "issue-1"
            worktree.mkdir(parents=True)
            handoff = write_handoff(root, "issue-1", "g1", "implementer")
            result = result_rel("issue-1", "g1", "implementer")
            with recording_launch(RC, write_result_at=root / result) as calls:
                RC.launch_crew(
                    work_id="issue-1", gate="g1", role="implementer",
                    handoff=handoff, result=result, worktree=str(worktree),
                    model="sonnet", launcher="claude", attempt=1, root=root, entries=[],
                    parent="test-parent",
                )
            self.assertEqual(1, len(calls))
            self.assertEqual(worktree, Path(calls[0]["cwd"]),
                             "the crew was not spawned in its own worktree")

    def test_relative_worktree_resolves_against_root_not_the_dispatchers_cwd(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sub").mkdir()
            handoff = write_handoff(root, "issue-1", "g1", "implementer")
            result = result_rel("issue-1", "g1", "implementer")
            with recording_launch(RC, write_result_at=root / result) as calls:
                RC.launch_crew(
                    work_id="issue-1", gate="g1", role="implementer",
                    handoff=handoff, result=result, worktree="sub",
                    model="sonnet", launcher="claude", attempt=1, root=root, entries=[],
                    parent="test-parent",
                )
            self.assertEqual(root / "sub", Path(calls[0]["cwd"]))

    def test_resume_passes_the_stored_worktree_as_the_child_cwd(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            worktree = root / "wt" / "issue-1"
            worktree.mkdir(parents=True)
            handoff = write_handoff(root, "issue-1", "g1", "implementer")
            result = result_rel("issue-1", "g1", "implementer")
            session = "constellation/issue-1/g1/implementer/attempt-1"
            stdout, stderr = RC.run_log_paths("issue-1", "g1", "implementer", 1, root)
            entries = [{
                "session_name": session, "crew_id": session,
                "work_id": "issue-1", "gate": "g1", "role": "implementer", "attempt": 1,
                "worktree": str(worktree), "status": "running", "abandoned": False,
                "handoff": handoff, "result": result,
                "stdout": RC._relativize(str(stdout), root),
                "stderr": RC._relativize(str(stderr), root),
            }]
            RC.save_registry(RC.registry_path("issue-1", root), entries)
            with recording_launch(RC, write_result_at=root / result) as calls:
                RC.resume_crew(session=session, root=root, entries=entries)
            self.assertEqual(worktree, Path(calls[0]["cwd"]),
                             "a resumed crew was not spawned in its own worktree")

    def test_legacy_entry_with_no_worktree_key_still_resumes(self):
        """An entry recorded before the field existed has no `worktree` key at
        all -- resume must degrade to the inherited directory, not KeyError."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "implementer")
            result = result_rel("issue-1", "g1", "implementer")
            session = "constellation/issue-1/g1/implementer/attempt-1"
            stdout, stderr = RC.run_log_paths("issue-1", "g1", "implementer", 1, root)
            entries = [{
                "session_name": session, "crew_id": session,
                "work_id": "issue-1", "gate": "g1", "role": "implementer", "attempt": 1,
                "status": "running", "abandoned": False,
                "handoff": handoff, "result": result,
                "stdout": RC._relativize(str(stdout), root),
                "stderr": RC._relativize(str(stderr), root),
            }]
            RC.save_registry(RC.registry_path("issue-1", root), entries)
            with recording_launch(RC, write_result_at=root / result) as calls:
                RC.resume_crew(session=session, root=root, entries=entries)
            self.assertIsNone(calls[0]["cwd"])

    def test_the_registry_records_the_same_worktree_the_spawn_received(self):
        """The recorded entry and the spawn must not be able to disagree."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            worktree = root / "wt" / "issue-1"
            worktree.mkdir(parents=True)
            handoff = write_handoff(root, "issue-1", "g1", "implementer")
            result = result_rel("issue-1", "g1", "implementer")
            with recording_launch(RC, write_result_at=root / result) as calls:
                _code, entry = RC.launch_crew(
                    work_id="issue-1", gate="g1", role="implementer",
                    handoff=handoff, result=result, worktree=str(worktree),
                    model="sonnet", launcher="claude", attempt=1, root=root, entries=[],
                    parent="test-parent",
                )
            self.assertEqual(Path(entry["worktree"]), Path(calls[0]["cwd"]))


class LaunchProcessCwdTests(unittest.TestCase):
    """The seam itself, against a REAL subprocess."""

    def _paths(self, root: Path) -> tuple[Path, Path]:
        return root / "logs" / "out.txt", root / "logs" / "err.txt"

    def test_child_really_stands_in_the_given_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            worktree = root / "wt"
            worktree.mkdir()
            out, err = self._paths(root)
            code = RC.launch_process(
                [sys.executable, "-c", "import os, sys; sys.stdout.write(os.getcwd())"],
                stdin=b"", env=dict(os.environ), stdout_path=out, stderr_path=err,
                cwd=worktree,
            )
            self.assertEqual(0, code, err.read_text(encoding="utf-8"))
            self.assertEqual(
                worktree.resolve(),
                Path(out.read_text(encoding="utf-8").strip()).resolve(),
            )

    def test_no_cwd_keeps_the_inherited_directory(self):
        """The default is backward-compatible: omitting `cwd` leaves the child
        where it always was, in the dispatching process's own directory."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out, err = self._paths(root)
            code = RC.launch_process(
                [sys.executable, "-c", "import os, sys; sys.stdout.write(os.getcwd())"],
                stdin=b"", env=dict(os.environ), stdout_path=out, stderr_path=err,
            )
            self.assertEqual(0, code, err.read_text(encoding="utf-8"))
            self.assertEqual(
                Path(os.getcwd()).resolve(),
                Path(out.read_text(encoding="utf-8").strip()).resolve(),
            )

    def test_missing_worktree_refuses_by_name_instead_of_a_bare_oserror(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gone = root / "wt" / "never-created"
            out, err = self._paths(root)
            with self.assertRaises(RC.CrewLaunchError) as caught:
                RC.launch_process(
                    [sys.executable, "-c", "pass"],
                    stdin=b"", env=dict(os.environ), stdout_path=out, stderr_path=err,
                    cwd=gone,
                )
            message = str(caught.exception)
            self.assertIn(str(gone), message,
                          "the refusal must name the directory it could not find")
            self.assertIn("worktree", message.lower())

    def test_a_file_where_the_worktree_should_be_is_refused_too(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            not_a_dir = root / "wt-is-a-file"
            not_a_dir.write_text("", encoding="utf-8")
            out, err = self._paths(root)
            with self.assertRaises(RC.CrewLaunchError):
                RC.launch_process(
                    [sys.executable, "-c", "pass"],
                    stdin=b"", env=dict(os.environ), stdout_path=out, stderr_path=err,
                    cwd=not_a_dir,
                )


if __name__ == "__main__":
    unittest.main()
