import importlib.util
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_CREW = ROOT / "scripts" / "run_crew.py"
RECOVER = ROOT / "scripts" / "recover_crews.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


RC = load_module("run_crew", RUN_CREW)
REC = load_module("recover_crews", RECOVER)


def write_handoff(root: Path, work_id: str, gate: str, role: str) -> str:
    rel = f".agent-work/{work_id}/crew-handoffs/{gate}-{role}.md"
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("handoff body\n", encoding="utf-8")
    return rel


def result_rel(work_id: str, gate: str, role: str) -> str:
    return f".agent-work/{work_id}/crew-handoffs/{gate}-{role}-result.md"


@contextlib.contextmanager
def fake_launch(RC_mod, exit_code: int, *, write_result_at: Path | None = None):
    """Replace the single subprocess seam with a fake that records the argv,
    simulates an exit code, and optionally writes the result artifact — so no
    real agent CLI is ever spawned."""
    calls: list[dict] = []
    original = RC_mod.launch_process

    def fake(argv, *, stdin, env, stdout_path, stderr_path):
        calls.append(
            {"argv": argv, "stdin": stdin, "env": env,
             "stdout_path": stdout_path, "stderr_path": stderr_path}
        )
        Path(stdout_path).parent.mkdir(parents=True, exist_ok=True)
        Path(stdout_path).write_text("out\n", encoding="utf-8")
        Path(stderr_path).write_text("err\n", encoding="utf-8")
        if write_result_at is not None:
            Path(write_result_at).parent.mkdir(parents=True, exist_ok=True)
            Path(write_result_at).write_text("RESULT\n", encoding="utf-8")
        return exit_code

    RC_mod.launch_process = fake
    try:
        yield calls
    finally:
        RC_mod.launch_process = original


class SessionNameTests(unittest.TestCase):
    def test_session_name_is_deterministic(self):
        name = RC.session_name("issue-420", "g2", "reviewer", 1)
        self.assertEqual("constellation/issue-420/g2/reviewer/attempt-1", name)
        self.assertEqual(name, RC.session_name("issue-420", "g2", "reviewer", 1))
        self.assertEqual(
            "constellation/issue-420/g2/reviewer/attempt-2",
            RC.session_name("issue-420", "g2", "reviewer", 2),
        )

    def test_build_crew_argv_is_pure_and_includes_model_and_handoff(self):
        argv = RC.build_crew_argv(
            "claude", role="reviewer", handoff="/abs/g2-reviewer.md",
            model="sonnet", session="constellation/issue-420/g2/reviewer/attempt-1",
        )
        self.assertEqual("claude", argv[0])
        self.assertIn("--role", argv)
        self.assertIn("reviewer", argv)
        self.assertIn("--handoff", argv)
        self.assertIn("/abs/g2-reviewer.md", argv)
        self.assertIn("--model", argv)
        self.assertIn("sonnet", argv)
        self.assertIn("constellation/issue-420/g2/reviewer/attempt-1", argv)

    def test_build_crew_argv_omits_model_when_absent(self):
        argv = RC.build_crew_argv(
            "claude", role="implementer", handoff="h.md", model=None, session="s",
        )
        self.assertNotIn("--model", argv)


class LaunchTests(unittest.TestCase):
    def test_missing_handoff_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(RC.CrewLaunchError):
                RC.launch_crew(
                    work_id="issue-1", gate="g1", role="implementer",
                    handoff=".agent-work/issue-1/crew-handoffs/g1-implementer.md",
                    result=result_rel("issue-1", "g1", "implementer"),
                    worktree=".", model=None, launcher="claude", attempt=1,
                    root=root, entries=[],
                )

    def test_records_entry_before_launch_and_completes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "reviewer")
            result = result_rel("issue-1", "g1", "reviewer")
            entries: list[dict] = []
            with fake_launch(RC, 0, write_result_at=root / result) as calls:
                code, entry = RC.launch_crew(
                    work_id="issue-1", gate="g1", role="reviewer",
                    handoff=handoff, result=result, worktree=".", model="sonnet",
                    launcher="claude", attempt=1, root=root, entries=entries,
                )
            self.assertEqual(0, code)
            self.assertEqual("completed", entry["status"])
            # empty stdin + UTF-8 env passed to the seam
            self.assertEqual(b"", calls[0]["stdin"])
            self.assertEqual("1", calls[0]["env"]["PYTHONUTF8"])
            self.assertEqual("utf-8", calls[0]["env"]["PYTHONIOENCODING"])
            # durable registry written with a running record + final completed
            reg = RC.load_registry(RC.registry_path("issue-1", root))
            self.assertEqual(1, len(reg))
            self.assertEqual("completed", reg[0]["status"])
            self.assertEqual("constellation/issue-1/g1/reviewer/attempt-1", reg[0]["session_name"])
            self.assertEqual(1, reg[0]["attempt"])
            # stdout/stderr captured to deterministic files
            self.assertTrue((root / reg[0]["stdout"]).is_file())
            self.assertTrue((root / reg[0]["stderr"]).is_file())

    def test_nonzero_child_exit_returns_nonzero_and_marks_failed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "reviewer")
            result = result_rel("issue-1", "g1", "reviewer")
            with fake_launch(RC, 3, write_result_at=root / result):
                code, entry = RC.launch_crew(
                    work_id="issue-1", gate="g1", role="reviewer",
                    handoff=handoff, result=result, worktree=".", model=None,
                    launcher="claude", attempt=1, root=root, entries=[],
                )
            self.assertNotEqual(0, code)
            self.assertEqual("failed", entry["status"])

    def test_missing_result_artifact_returns_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "reviewer")
            result = result_rel("issue-1", "g1", "reviewer")
            with fake_launch(RC, 0, write_result_at=None):  # child exits 0 but writes nothing
                code, entry = RC.launch_crew(
                    work_id="issue-1", gate="g1", role="reviewer",
                    handoff=handoff, result=result, worktree=".", model=None,
                    launcher="claude", attempt=1, root=root, entries=[],
                )
            self.assertNotEqual(0, code)
            self.assertEqual("failed", entry["status"])

    def test_duplicate_active_lock_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "reviewer")
            result = result_rel("issue-1", "g1", "reviewer")
            # a running attempt already holds this gate/role/worktree
            entries = [{
                "session_name": "constellation/issue-1/g1/reviewer/attempt-1",
                "crew_id": "constellation/issue-1/g1/reviewer/attempt-1",
                "work_id": "issue-1", "gate": "g1", "role": "reviewer", "attempt": 1,
                "worktree": ".", "status": "running", "abandoned": False,
            }]
            dup = RC.active_duplicate(entries, "issue-1", "g1", "reviewer", ".")
            self.assertIsNotNone(dup)
            # CLI refuses the duplicate launch
            RC.save_registry(RC.registry_path("issue-1", root), entries)
            with contextlib.redirect_stderr(io.StringIO()):
                code = RC.main([
                    "--root", str(root), "--work-id", "issue-1", "--gate", "g1",
                    "--role", "reviewer", "--handoff", handoff, "--result", result,
                ])
            self.assertEqual(1, code)

    def test_abandon_relaunch_increments_attempt_and_marks_prior_abandoned(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "reviewer")
            result = result_rel("issue-1", "g1", "reviewer")
            entries = [{
                "session_name": "constellation/issue-1/g1/reviewer/attempt-1",
                "crew_id": "constellation/issue-1/g1/reviewer/attempt-1",
                "work_id": "issue-1", "gate": "g1", "role": "reviewer", "attempt": 1,
                "worktree": ".", "status": "running", "abandoned": False,
                "handoff": handoff, "result": result,
            }]
            RC.save_registry(RC.registry_path("issue-1", root), entries)
            with fake_launch(RC, 0, write_result_at=root / result):
                with contextlib.redirect_stdout(io.StringIO()):
                    code = RC.main([
                        "--root", str(root),
                        "--abandon", "constellation/issue-1/g1/reviewer/attempt-1",
                        "--relaunch", "--handoff", handoff, "--result", result,
                    ])
            self.assertEqual(0, code)
            reg = RC.load_registry(RC.registry_path("issue-1", root))
            by_name = {e["session_name"]: e for e in reg}
            self.assertTrue(RC.is_abandoned(by_name["constellation/issue-1/g1/reviewer/attempt-1"]))
            self.assertIn("constellation/issue-1/g1/reviewer/attempt-2", by_name)
            self.assertEqual(2, by_name["constellation/issue-1/g1/reviewer/attempt-2"]["attempt"])
            # after abandon, a fresh duplicate check no longer blocks attempt-1's slot
            self.assertEqual("completed", by_name["constellation/issue-1/g1/reviewer/attempt-2"]["status"])

    def test_resume_uses_stored_session_and_handoff(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "reviewer")
            result = result_rel("issue-1", "g1", "reviewer")
            session = "constellation/issue-1/g1/reviewer/attempt-1"
            stdout, stderr = RC.run_log_paths("issue-1", "g1", "reviewer", 1, root)
            entries = [{
                "session_name": session, "crew_id": session,
                "work_id": "issue-1", "gate": "g1", "role": "reviewer", "attempt": 1,
                "worktree": ".", "status": "running", "abandoned": False,
                "handoff": handoff, "result": result,
                "stdout": RC._relativize(str(stdout), root),
                "stderr": RC._relativize(str(stderr), root),
            }]
            RC.save_registry(RC.registry_path("issue-1", root), entries)
            with fake_launch(RC, 0, write_result_at=root / result) as calls:
                with contextlib.redirect_stdout(io.StringIO()):
                    code = RC.main(["--root", str(root), "--resume", session])
            self.assertEqual(0, code)
            self.assertIn(session, calls[0]["argv"])
            reg = RC.load_registry(RC.registry_path("issue-1", root))
            self.assertEqual("completed", reg[0]["status"])

    def test_resume_unknown_session_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with contextlib.redirect_stderr(io.StringIO()):
                code = RC.main(["--root", str(root), "--resume",
                                "constellation/issue-1/g1/reviewer/attempt-9"])
            self.assertEqual(1, code)


class ExternalDispatchTests(unittest.TestCase):
    """--dispatch external: record the durable registry entry + duplicate-guard
    + result verification WITHOUT spawning any subprocess (the Agent-tool harness
    has no headless `claude` CLI to launch)."""

    def test_external_dispatch_records_without_spawning(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "implementer")
            result = result_rel("issue-1", "g1", "implementer")
            # fake_launch installs the spawn seam; for external dispatch it must
            # never be called.
            with fake_launch(RC, 0, write_result_at=root / result) as calls:
                with contextlib.redirect_stdout(io.StringIO()):
                    code = RC.main([
                        "--root", str(root), "--work-id", "issue-1", "--gate", "g1",
                        "--role", "implementer", "--handoff", handoff, "--result", result,
                        "--dispatch", "external",
                    ])
            self.assertEqual(0, code)
            self.assertEqual([], calls)  # nothing spawned
            reg = RC.load_registry(RC.registry_path("issue-1", root))
            self.assertEqual(1, len(reg))
            self.assertEqual("external", reg[0]["dispatch"])
            self.assertIsNone(reg[0]["pid"])
            self.assertEqual("running", reg[0]["status"])
            self.assertEqual(
                "constellation/issue-1/g1/implementer/attempt-1", reg[0]["session_name"]
            )

    def test_external_missing_handoff_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = result_rel("issue-1", "g1", "implementer")
            with contextlib.redirect_stderr(io.StringIO()):
                code = RC.main([
                    "--root", str(root), "--work-id", "issue-1", "--gate", "g1",
                    "--role", "implementer",
                    "--handoff", ".agent-work/issue-1/crew-handoffs/g1-implementer.md",
                    "--result", result, "--dispatch", "external",
                ])
            self.assertEqual(1, code)

    def test_external_duplicate_active_lock_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "implementer")
            result = result_rel("issue-1", "g1", "implementer")
            argv = [
                "--root", str(root), "--work-id", "issue-1", "--gate", "g1",
                "--role", "implementer", "--handoff", handoff, "--result", result,
                "--dispatch", "external",
            ]
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(0, RC.main(argv))
            # the first external attempt is `running` and holds the slot
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(1, RC.main(argv))

    def test_verify_result_absent_then_present_marks_completed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "implementer")
            result = result_rel("issue-1", "g1", "implementer")
            session = "constellation/issue-1/g1/implementer/attempt-1"
            with contextlib.redirect_stdout(io.StringIO()):
                RC.main([
                    "--root", str(root), "--work-id", "issue-1", "--gate", "g1",
                    "--role", "implementer", "--handoff", handoff, "--result", result,
                    "--dispatch", "external",
                ])
            # result artifact not written yet -> verify is nonzero, stays running
            with contextlib.redirect_stdout(io.StringIO()):
                code_absent = RC.main(["--root", str(root), "--verify-result", session])
            self.assertEqual(1, code_absent)
            self.assertEqual(
                "running", RC.load_registry(RC.registry_path("issue-1", root))[0]["status"]
            )
            # write the result artifact (the out-of-band crew finished) -> completed
            (root / result).parent.mkdir(parents=True, exist_ok=True)
            (root / result).write_text("RESULT\n", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                code_present = RC.main(["--root", str(root), "--verify-result", session])
            self.assertEqual(0, code_present)
            self.assertEqual(
                "completed", RC.load_registry(RC.registry_path("issue-1", root))[0]["status"]
            )


class ProcessAliveTests(unittest.TestCase):
    def test_pid_zero_or_none_is_dead(self):
        self.assertFalse(RC.process_alive(None))
        self.assertFalse(RC.process_alive(0))

    def test_current_process_is_alive(self):
        import os
        self.assertTrue(RC.process_alive(os.getpid()))


class ClassificationTests(unittest.TestCase):
    @staticmethod
    def _entry(**over):
        base = {
            "session_name": "constellation/issue-1/g1/reviewer/attempt-1",
            "work_id": "issue-1", "gate": "g1", "role": "reviewer", "attempt": 1,
            "worktree": ".", "status": "running", "pid": 111,
            "result": result_rel("issue-1", "g1", "reviewer"),
        }
        base.update(over)
        return base

    def test_completed_with_result_is_complete(self):
        state = REC.classify_entry(
            self._entry(status="completed"), lambda pid: False, lambda e: True
        )
        self.assertEqual(REC.STATE_COMPLETE, state)

    def test_running_with_live_pid_is_active(self):
        state = REC.classify_entry(
            self._entry(status="running"), lambda pid: True, lambda e: False
        )
        self.assertEqual(REC.STATE_ACTIVE, state)

    def test_running_dead_pid_missing_result_is_resumable(self):
        state = REC.classify_entry(
            self._entry(status="running", resumable=True),
            lambda pid: False, lambda e: False,
        )
        self.assertEqual(REC.STATE_RESUMABLE, state)

    def test_running_dead_pid_with_result_is_complete(self):
        state = REC.classify_entry(
            self._entry(status="running"), lambda pid: False, lambda e: True
        )
        self.assertEqual(REC.STATE_COMPLETE, state)

    def test_not_running_not_resumable_needs_abandon(self):
        state = REC.classify_entry(
            self._entry(status="running", resumable=False),
            lambda pid: False, lambda e: False,
        )
        self.assertEqual(REC.STATE_NEEDS_ABANDON, state)

    def test_abandoned_is_ignored(self):
        state = REC.classify_entry(
            self._entry(status="abandoned", abandoned=True),
            lambda pid: True, lambda e: False,
        )
        self.assertEqual(REC.STATE_ABANDONED, state)

    def test_unknown_status_live_pid_is_conflict(self):
        state = REC.classify_entry(
            self._entry(status="??"), lambda pid: True, lambda e: False
        )
        self.assertEqual(REC.STATE_CONFLICT, state)

    def test_two_active_attempts_same_target_become_conflict(self):
        a = self._entry(session_name="s1", status="running", pid=1)
        b = self._entry(session_name="s2", status="running", pid=2, attempt=2)
        classified = REC.classify_registry(
            [a, b], alive=lambda pid: True, result_present=lambda e: False
        )
        states = {e["session_name"]: s for e, s in classified}
        self.assertEqual(REC.STATE_CONFLICT, states["s2"])

    def test_report_signals_unresolved_with_nonzero(self):
        a = self._entry(status="running")
        classified = REC.classify_registry(
            [a], alive=lambda pid: True, result_present=lambda e: False
        )
        with contextlib.redirect_stdout(io.StringIO()):
            code = REC.report(classified)
        self.assertEqual(1, code)

    def test_report_clean_when_all_resolved(self):
        a = self._entry(status="completed")
        classified = REC.classify_registry(
            [a], alive=lambda pid: False, result_present=lambda e: True
        )
        with contextlib.redirect_stdout(io.StringIO()):
            code = REC.report(classified)
        self.assertEqual(0, code)

    def test_recover_cli_reads_registry_and_classifies(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entries = [self._entry(status="completed")]
            RC.save_registry(RC.registry_path("issue-1", root), entries)
            (root / entries[0]["result"]).parent.mkdir(parents=True, exist_ok=True)
            (root / entries[0]["result"]).write_text("R\n", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                code = REC.main(["issue-1", "--root", str(root)])
            self.assertEqual(0, code)


if __name__ == "__main__":
    unittest.main()
