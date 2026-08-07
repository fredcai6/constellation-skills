import importlib.util
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


def iso(ts: float) -> str:
    """ISO-8601 UTC string for a POSIX timestamp — used to build `started_at`
    values relative to a controlled file mtime."""
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def write_result_with_mtime(path: Path, mtime: float) -> None:
    """Write a result artifact and stamp its mtime deterministically into the
    past/future, so STALE vs FRESH is decided by the clock we choose, not by
    wall-time flakiness."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("RESULT\n", encoding="utf-8")
    os.utime(path, (mtime, mtime))


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

    def test_build_crew_argv_is_pure_and_carries_role_handoff_session_in_prompt(self):
        argv = RC.build_crew_argv(
            "claude", role="reviewer", handoff="/abs/g2-reviewer.md",
            model="sonnet", session="constellation/issue-420/g2/reviewer/attempt-1",
        )
        self.assertEqual("claude", argv[0])
        self.assertEqual("-p", argv[1])
        prompt = argv[2]
        self.assertIn("reviewer", prompt)
        self.assertIn("/abs/g2-reviewer.md", prompt)
        self.assertIn("constellation/issue-420/g2/reviewer/attempt-1", prompt)
        self.assertIn("--model", argv)
        self.assertIn("sonnet", argv)

    def test_build_crew_argv_emits_no_legacy_flags(self):
        # issue #91: the claude CLI has no --session/--role/--handoff flags; the
        # old form died with `error: unknown option '--session'`.
        argv = RC.build_crew_argv(
            "claude", role="implementer", handoff="h.md", model="sonnet", session="s",
        )
        for legacy in ("--session", "--role", "--handoff"):
            self.assertNotIn(legacy, argv)

    def test_build_crew_argv_omits_model_when_absent(self):
        argv = RC.build_crew_argv(
            "claude", role="implementer", handoff="h.md", model=None, session="s",
        )
        self.assertNotIn("--model", argv)


class CliDriftHintTests(unittest.TestCase):
    def test_unknown_option_stderr_yields_actionable_hint(self):
        hint = RC.cli_drift_hint("error: unknown option '--session'\n")
        self.assertIsNotNone(hint)
        self.assertIn("--backend external", hint)
        self.assertIn("unknown option '--session'", hint)

    def test_unrecognized_arguments_yields_hint(self):
        self.assertIsNotNone(RC.cli_drift_hint("usage: x\nerror: unrecognized arguments: --role\n"))

    def test_ordinary_crew_failure_yields_no_hint(self):
        self.assertIsNone(RC.cli_drift_hint("Traceback (most recent call last):\nRuntimeError: crew died\n"))
        self.assertIsNone(RC.cli_drift_hint(""))


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
            self.assertIn(session, " ".join(calls[0]["argv"]))
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


class ResultFreshnessTests(unittest.TestCase):
    """The canonical freshness gate: a result artifact must exist AND be at/after
    the crew's dispatch time. A stale leftover from a prior attempt is not fresh."""

    BASE = 1_000_000_000.0  # fixed reference clock (2001) — deterministic

    def test_missing_file_is_not_fresh(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertFalse(
                RC.result_fresh("nope/result.md", root, iso(self.BASE))
            )

    def test_result_after_dispatch_is_fresh(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = root / "result.md"
            write_result_with_mtime(result, self.BASE + 60)  # written after dispatch
            self.assertTrue(RC.result_fresh("result.md", root, iso(self.BASE)))

    def test_stale_result_before_dispatch_is_not_fresh(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = root / "result.md"
            write_result_with_mtime(result, self.BASE - 60)  # leftover from before
            self.assertFalse(RC.result_fresh("result.md", root, iso(self.BASE)))

    def test_same_second_is_not_falsely_stale(self):
        """Sub-second `started_at` after the file mtime within the SAME whole
        second must still read fresh — the floor guards coarse mtime resolution."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = root / "result.md"
            write_result_with_mtime(result, self.BASE + 0.2)
            # dispatch stamped 0.7s in — same whole second, later fraction
            self.assertTrue(
                RC.result_fresh("result.md", root, iso(self.BASE + 0.7))
            )

    def test_verify_result_stale_refuses_and_leaves_running(self):
        """--verify-result on a STALE leftover prints a STALE refusal, returns 1,
        and leaves the entry running (its hold on the gate is not cleared)."""
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
            # a leftover result from a PRIOR attempt, older than this dispatch
            entry = RC.load_registry(RC.registry_path("issue-1", root))[0]
            dispatch_ts = datetime.fromisoformat(entry["started_at"]).timestamp()
            write_result_with_mtime(root / result, dispatch_ts - 3600)
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                code = RC.main(["--root", str(root), "--verify-result", session])
            self.assertEqual(1, code)
            self.assertIn("stale", err.getvalue().lower())
            reg = RC.load_registry(RC.registry_path("issue-1", root))[0]
            self.assertEqual("running", reg["status"])
            self.assertTrue(reg["result_present"])
            self.assertFalse(reg["result_fresh"])

    def test_verify_result_missing_refuses_with_absent_message(self):
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
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                code = RC.main(["--root", str(root), "--verify-result", session])
            self.assertEqual(1, code)
            self.assertIn("absent", err.getvalue().lower())
            reg = RC.load_registry(RC.registry_path("issue-1", root))[0]
            self.assertEqual("running", reg["status"])

    def test_launch_finding_only_stale_result_marks_failed(self):
        """A spawn that exits 0 but leaves only a STALE prior-attempt result at the
        path is `failed`, not `completed`."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "reviewer")
            result = result_rel("issue-1", "g1", "reviewer")
            # a leftover from a prior attempt is already on disk, far in the past
            write_result_with_mtime(root / result, self.BASE)
            # the fake child exits 0 but writes nothing new
            with fake_launch(RC, 0, write_result_at=None):
                code, entry = RC.launch_crew(
                    work_id="issue-1", gate="g1", role="reviewer",
                    handoff=handoff, result=result, worktree=".", model=None,
                    launcher="claude", attempt=1, root=root, entries=[],
                )
            self.assertNotEqual(0, code)
            self.assertEqual("failed", entry["status"])
            self.assertTrue(entry["result_present"])   # the leftover exists
            self.assertFalse(entry["result_fresh"])    # but it predates dispatch

    def test_recover_default_predicate_rejects_stale_uses_started_at(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = result_rel("issue-1", "g1", "reviewer")
            write_result_with_mtime(root / result, self.BASE)
            predicate = REC._default_result_present(root)
            stale = {"result": result, "started_at": iso(self.BASE + 3600)}
            fresh = {"result": result, "started_at": iso(self.BASE - 3600)}
            legacy = {"result": result}  # no started_at -> existence fallback
            self.assertFalse(predicate(stale))
            self.assertTrue(predicate(fresh))
            self.assertTrue(predicate(legacy))


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


class BuildEntryTests(unittest.TestCase):
    """The ONE consolidated entry constructor shared by both backends."""

    def _kwargs(self, **over):
        base = dict(
            work_id="issue-1", gate="g1", role="reviewer", attempt=1,
            worktree=".", handoff="h.md", result="r.md",
            root=Path("."), started="2026-07-07T00:00:00+00:00",
        )
        base.update(over)
        return base

    def test_cli_entry_carries_backend_cli_and_pid_no_dispatch(self):
        entry = RC.build_entry(backend="cli", pid=4321, **self._kwargs())
        self.assertEqual("cli", entry["backend"])
        self.assertEqual(4321, entry["pid"])
        self.assertEqual("running", entry["status"])
        self.assertEqual("constellation/issue-1/g1/reviewer/attempt-1", entry["session_name"])
        self.assertEqual(entry["session_name"], entry["crew_id"])
        # cli entries carry no external dispatch marker and (as before) no model
        self.assertNotIn("dispatch", entry)
        self.assertNotIn("model", entry)
        self.assertFalse(entry["abandoned"])
        self.assertIsNone(entry["completed_at"])

    def test_external_entry_keeps_dispatch_marker_pidless_and_model(self):
        entry = RC.build_entry(
            backend="external", pid=None, dispatch=RC.DISPATCH_EXTERNAL,
            model="sonnet", **self._kwargs(role="implementer"),
        )
        self.assertEqual("external", entry["backend"])
        self.assertIsNone(entry["pid"])
        self.assertEqual("external", entry["dispatch"])
        self.assertEqual("sonnet", entry["model"])

    def test_falsy_model_is_not_stored(self):
        entry = RC.build_entry(backend="external", pid=None, model=None, **self._kwargs())
        self.assertNotIn("model", entry)


class FinalizeFromExitCodeTests(unittest.TestCase):
    """The ONE finalize tail both CliBackend.dispatch and .resume call — no forked
    completed/failed rule, reusing the single result_fresh."""

    BASE = 1_000_000_000.0

    def test_exit0_and_fresh_result_completes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_result_with_mtime(root / "r.md", self.BASE + 60)
            entry = {}
            final = RC.finalize_from_exit_code(
                entry, exit_code=0, result="r.md", root=root, since=iso(self.BASE)
            )
            self.assertEqual(0, final)
            self.assertEqual("completed", entry["status"])
            self.assertTrue(entry["result_present"])
            self.assertTrue(entry["result_fresh"])
            self.assertEqual(0, entry["exit_code"])
            self.assertIsNotNone(entry["completed_at"])
            self.assertEqual(entry["completed_at"], entry["last_heartbeat"])

    def test_nonzero_exit_fails_and_returns_that_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_result_with_mtime(root / "r.md", self.BASE + 60)  # fresh, but child failed
            entry = {}
            final = RC.finalize_from_exit_code(
                entry, exit_code=7, result="r.md", root=root, since=iso(self.BASE)
            )
            self.assertEqual(7, final)
            self.assertEqual("failed", entry["status"])

    def test_exit0_but_stale_result_fails_with_code_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_result_with_mtime(root / "r.md", self.BASE - 60)  # leftover, predates dispatch
            entry = {}
            final = RC.finalize_from_exit_code(
                entry, exit_code=0, result="r.md", root=root, since=iso(self.BASE)
            )
            self.assertEqual(1, final)
            self.assertEqual("failed", entry["status"])
            self.assertTrue(entry["result_present"])
            self.assertFalse(entry["result_fresh"])


class EntryBackendTests(unittest.TestCase):
    """Legacy entries without a `backend` field are inferred; explicit wins."""

    def test_explicit_backend_wins(self):
        self.assertEqual("cli", RC.entry_backend({"backend": "cli", "dispatch": "external"}))
        self.assertEqual("external", RC.entry_backend({"backend": "external"}))

    def test_legacy_external_dispatch_infers_external(self):
        self.assertEqual("external", RC.entry_backend({"dispatch": "external"}))

    def test_legacy_no_marker_infers_cli(self):
        self.assertEqual("cli", RC.entry_backend({}))
        self.assertEqual("cli", RC.entry_backend({"pid": 111}))


class BackendEquivalenceTests(unittest.TestCase):
    """The backends carry the behavior; the module functions are thin wrappers.
    Each backend's dispatch/verify/resume matches the old function it replaces."""

    def test_cli_dispatch_matches_launch_crew_and_tags_backend(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "reviewer")
            result = result_rel("issue-1", "g1", "reviewer")
            spec = RC.CrewSpec(
                work_id="issue-1", gate="g1", role="reviewer", handoff=handoff,
                result=result, worktree=".", attempt=1, model="sonnet", launcher="claude",
            )
            entries: list[dict] = []
            with fake_launch(RC, 0, write_result_at=root / result) as calls:
                code, entry = RC.CliBackend().dispatch(spec, root=root, entries=entries)
            self.assertEqual(0, code)
            self.assertEqual("completed", entry["status"])
            self.assertEqual("cli", entry["backend"])
            self.assertEqual(os.getpid(), entry["pid"])
            # spawned through the single seam with empty stdin + UTF-8 env
            self.assertEqual(b"", calls[0]["stdin"])
            self.assertIn("constellation/issue-1/g1/reviewer/attempt-1", " ".join(calls[0]["argv"]))

    def test_cli_dispatch_missing_handoff_refuses_with_launch_wording(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = RC.CrewSpec(
                work_id="issue-1", gate="g1", role="reviewer",
                handoff=".agent-work/issue-1/crew-handoffs/g1-reviewer.md",
                result=result_rel("issue-1", "g1", "reviewer"), worktree=".", attempt=1,
            )
            with self.assertRaises(RC.CrewLaunchError) as ctx:
                RC.CliBackend().dispatch(spec, root=root, entries=[])
            self.assertIn("refusing to launch", str(ctx.exception))

    def test_external_dispatch_records_without_spawning_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "implementer")
            result = result_rel("issue-1", "g1", "implementer")
            spec = RC.CrewSpec(
                work_id="issue-1", gate="g1", role="implementer", handoff=handoff,
                result=result, worktree=".", attempt=1, model="opus",
            )
            entries: list[dict] = []
            with fake_launch(RC, 0, write_result_at=root / result) as calls:
                code, entry = RC.ExternalBackend().dispatch(spec, root=root, entries=entries)
            self.assertIsNone(code)              # record-only: no exit code
            self.assertEqual([], calls)          # nothing spawned
            self.assertEqual("external", entry["backend"])
            self.assertEqual("external", entry["dispatch"])
            self.assertIsNone(entry["pid"])
            self.assertEqual("opus", entry["model"])
            self.assertEqual("running", entry["status"])

    def test_external_dispatch_missing_handoff_refuses_with_record_wording(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = RC.CrewSpec(
                work_id="issue-1", gate="g1", role="implementer",
                handoff=".agent-work/issue-1/crew-handoffs/g1-implementer.md",
                result=result_rel("issue-1", "g1", "implementer"), worktree=".", attempt=1,
            )
            with self.assertRaises(RC.CrewLaunchError) as ctx:
                RC.ExternalBackend().dispatch(spec, root=root, entries=[])
            self.assertIn("refusing to record", str(ctx.exception))

    def test_verify_is_uniform_across_backends(self):
        """CrewBackend.verify (used by both backends) finalizes on a fresh result
        exactly like verify_external_result — the same instance/API on either."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "implementer")
            result = result_rel("issue-1", "g1", "implementer")
            session = "constellation/issue-1/g1/implementer/attempt-1"
            entries = [RC.record_external_attempt(
                work_id="issue-1", gate="g1", role="implementer", handoff=handoff,
                result=result, worktree=".", model=None, attempt=1, root=root, entries=[],
            )]
            # not written yet -> not fresh, stays running
            fresh_cli, _ = RC.CliBackend().verify(entries, session, root=root)
            self.assertFalse(fresh_cli)
            self.assertEqual("running", entries[0]["status"])
            # write it, verify through the external backend -> completed
            (root / result).parent.mkdir(parents=True, exist_ok=True)
            (root / result).write_text("RESULT\n", encoding="utf-8")
            fresh_ext, entry = RC.ExternalBackend().verify(entries, session, root=root)
            self.assertTrue(fresh_ext)
            self.assertEqual("completed", entry["status"])

    def test_cli_resume_relaunches_and_finalizes(self):
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
            with fake_launch(RC, 0, write_result_at=root / result) as calls:
                code, entry = RC.CliBackend().resume(session, root=root, entries=entries)
            self.assertEqual(0, code)
            self.assertEqual("completed", entry["status"])
            self.assertIn(session, " ".join(calls[0]["argv"]))

    def test_external_resume_is_unrecoverable_by_wrapper(self):
        entries = [{
            "session_name": "constellation/issue-1/g1/implementer/attempt-1",
            "crew_id": "constellation/issue-1/g1/implementer/attempt-1",
            "work_id": "issue-1", "gate": "g1", "role": "implementer", "attempt": 1,
            "worktree": ".", "status": "running", "abandoned": False,
            "backend": "external", "dispatch": "external", "pid": None,
        }]
        with self.assertRaises(RC.CrewLaunchError) as ctx:
            RC.ExternalBackend().resume(
                "constellation/issue-1/g1/implementer/attempt-1",
                root=Path("."), entries=entries,
            )
        msg = str(ctx.exception).lower()
        self.assertIn("unrecoverable", msg)
        self.assertIn("abandon", msg)


class SelectBackendTests(unittest.TestCase):
    """Decision 4: explicit override always wins; None/auto auto-detects from PATH
    presence via the injectable `which`."""

    @staticmethod
    def _found(_launcher):
        return "/usr/bin/claude"   # CLI present on PATH

    @staticmethod
    def _absent(_launcher):
        return None                # CLI not on PATH

    def test_explicit_cli_wins_even_when_cli_absent(self):
        b = RC.select_backend("cli", which=self._absent)
        self.assertIsInstance(b, RC.CliBackend)
        self.assertEqual("cli", b.name)

    def test_explicit_external_wins_even_when_cli_present(self):
        b = RC.select_backend("external", which=self._found)
        self.assertIsInstance(b, RC.ExternalBackend)
        self.assertEqual("external", b.name)

    def test_auto_detects_cli_when_launcher_on_path(self):
        self.assertIsInstance(RC.select_backend("auto", which=self._found), RC.CliBackend)

    def test_auto_detects_external_when_launcher_absent(self):
        self.assertIsInstance(RC.select_backend("auto", which=self._absent), RC.ExternalBackend)

    def test_none_auto_detects_like_auto(self):
        self.assertIsInstance(RC.select_backend(None, which=self._found), RC.CliBackend)
        self.assertIsInstance(RC.select_backend(None, which=self._absent), RC.ExternalBackend)

    def test_auto_detect_uses_the_launcher_argument(self):
        seen = []

        def which(launcher):
            seen.append(launcher)
            return None

        RC.select_backend("auto", launcher="my-cli", which=which)
        self.assertEqual(["my-cli"], seen)

    def test_unknown_token_fails_visibly(self):
        with self.assertRaises(RC.CrewLaunchError):
            RC.select_backend("bogus", which=self._found)


class BackendFlagRoutingTests(unittest.TestCase):
    """Decision 5: --backend resolves + dispatches through the right backend;
    --dispatch stays backward compatible (no auto-detect unless --backend auto)."""

    def _launch_argv(self, root, work_id, gate, role, handoff, result, extra):
        return [
            "--root", str(root), "--work-id", work_id, "--gate", gate,
            "--role", role, "--handoff", handoff, "--result", result,
        ] + extra

    def test_backend_cli_spawns_through_the_cli_backend(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "reviewer")
            result = result_rel("issue-1", "g1", "reviewer")
            with fake_launch(RC, 0, write_result_at=root / result) as calls:
                with contextlib.redirect_stdout(io.StringIO()):
                    code = RC.main(self._launch_argv(
                        root, "issue-1", "g1", "reviewer", handoff, result,
                        ["--backend", "cli"],
                    ))
            self.assertEqual(0, code)
            self.assertEqual(1, len(calls))  # spawned through the seam
            reg = RC.load_registry(RC.registry_path("issue-1", root))
            self.assertEqual("cli", reg[0]["backend"])
            self.assertEqual("completed", reg[0]["status"])

    def test_backend_external_records_without_spawning(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "implementer")
            result = result_rel("issue-1", "g1", "implementer")
            with fake_launch(RC, 0, write_result_at=root / result) as calls:
                with contextlib.redirect_stdout(io.StringIO()):
                    code = RC.main(self._launch_argv(
                        root, "issue-1", "g1", "implementer", handoff, result,
                        ["--backend", "external"],
                    ))
            self.assertEqual(0, code)
            self.assertEqual([], calls)          # nothing spawned
            reg = RC.load_registry(RC.registry_path("issue-1", root))
            self.assertEqual("external", reg[0]["backend"])
            self.assertEqual("external", reg[0]["dispatch"])
            self.assertIsNone(reg[0]["pid"])

    def test_backend_wins_over_conflicting_dispatch(self):
        """--backend external overrides --dispatch spawn (explicit override wins)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "implementer")
            result = result_rel("issue-1", "g1", "implementer")
            with fake_launch(RC, 0, write_result_at=root / result) as calls:
                with contextlib.redirect_stdout(io.StringIO()):
                    code = RC.main(self._launch_argv(
                        root, "issue-1", "g1", "implementer", handoff, result,
                        ["--dispatch", "spawn", "--backend", "external"],
                    ))
            self.assertEqual(0, code)
            self.assertEqual([], calls)          # external won -> nothing spawned
            self.assertEqual(
                "external", RC.load_registry(RC.registry_path("issue-1", root))[0]["backend"]
            )

    def test_default_no_backend_flag_resolves_to_cli_without_autodetect(self):
        """No --backend + default --dispatch spawn -> cli, regardless of PATH
        (byte-for-byte backward compatible: no silent auto-detection)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "reviewer")
            result = result_rel("issue-1", "g1", "reviewer")
            with fake_launch(RC, 0, write_result_at=root / result) as calls:
                with contextlib.redirect_stdout(io.StringIO()):
                    code = RC.main(self._launch_argv(
                        root, "issue-1", "g1", "reviewer", handoff, result, [],
                    ))
            self.assertEqual(0, code)
            self.assertEqual(1, len(calls))      # cli path spawned
            self.assertEqual(
                "cli", RC.load_registry(RC.registry_path("issue-1", root))[0]["backend"]
            )


class ExternalResumeRefusalTests(unittest.TestCase):
    """Decision 6: --resume routes by the recorded entry's backend. An external
    entry is unrecoverable by the wrapper — it reports rather than spawning."""

    def test_external_resume_refuses_and_never_spawns(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            session = "constellation/issue-1/g1/implementer/attempt-1"
            entries = [{
                "session_name": session, "crew_id": session,
                "work_id": "issue-1", "gate": "g1", "role": "implementer", "attempt": 1,
                "worktree": ".", "status": "running", "abandoned": False,
                "backend": "external", "dispatch": "external", "pid": None,
                "handoff": write_handoff(root, "issue-1", "g1", "implementer"),
                "result": result_rel("issue-1", "g1", "implementer"),
            }]
            RC.save_registry(RC.registry_path("issue-1", root), entries)
            err = io.StringIO()
            with fake_launch(RC, 0) as calls:
                with contextlib.redirect_stderr(err):
                    code = RC.main(["--root", str(root), "--resume", session])
            self.assertEqual(1, code)            # refused, not exit-0
            self.assertEqual([], calls)          # never spawned
            self.assertIn("unrecoverable", err.getvalue().lower())

    def test_legacy_external_dispatch_marker_also_refuses_resume(self):
        """A legacy external entry (dispatch marker, no `backend` field) still routes
        to the external backend via entry_backend and refuses to spawn."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            session = "constellation/issue-1/g1/implementer/attempt-1"
            entries = [{
                "session_name": session, "crew_id": session,
                "work_id": "issue-1", "gate": "g1", "role": "implementer", "attempt": 1,
                "worktree": ".", "status": "running", "abandoned": False,
                "dispatch": "external", "pid": None,
                "result": result_rel("issue-1", "g1", "implementer"),
            }]
            with fake_launch(RC, 0) as calls:
                with self.assertRaises(RC.CrewLaunchError) as ctx:
                    RC.resume_crew(session=session, root=root, entries=entries)
            self.assertEqual([], calls)
            self.assertIn("unrecoverable", str(ctx.exception).lower())

    def test_cli_entry_resume_still_relaunches(self):
        """A cli entry keeps today's resume behavior (relaunch + finalize)."""
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
                "backend": "cli", "handoff": handoff, "result": result,
                "stdout": RC._relativize(str(stdout), root),
                "stderr": RC._relativize(str(stderr), root),
            }]
            with fake_launch(RC, 0, write_result_at=root / result) as calls:
                code, entry = RC.resume_crew(session=session, root=root, entries=entries)
            self.assertEqual(0, code)
            self.assertEqual("completed", entry["status"])
            self.assertIn(session, " ".join(calls[0]["argv"]))


class BackendInvariantContractTests(unittest.TestCase):
    """Decision 2: the result contract is backend-invariant — both backends verify
    exists-AND-fresh identically against the entry's started_at via the single
    `result_fresh`, never forked."""

    BASE = 1_000_000_000.0

    def _entry_for(self, root, backend_name):
        handoff = write_handoff(root, "issue-1", "g1", "implementer")
        result = result_rel("issue-1", "g1", "implementer")
        entry = RC.build_entry(
            work_id="issue-1", gate="g1", role="implementer", attempt=1,
            worktree=".", handoff=handoff, result=result, root=root,
            started=iso(self.BASE), backend=backend_name, pid=None,
        )
        RC.save_registry(RC.registry_path("issue-1", root), [entry])
        return result, entry

    def test_both_backends_verify_exists_and_fresh_identically(self):
        session = "constellation/issue-1/g1/implementer/attempt-1"
        for backend in (RC.CliBackend(), RC.ExternalBackend()):
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                result, entry = self._entry_for(root, backend.name)
                entries = [entry]
                # (a) result missing -> not fresh, stays running
                fresh, e = backend.verify(entries, session, root=root)
                self.assertFalse(fresh, backend.name)
                self.assertEqual("running", e["status"], backend.name)
                # (b) STALE leftover (mtime predates dispatch) -> present but not fresh
                write_result_with_mtime(root / result, self.BASE - 60)
                fresh, e = backend.verify(entries, session, root=root)
                self.assertFalse(fresh, backend.name)
                self.assertTrue(e["result_present"], backend.name)
                self.assertFalse(e["result_fresh"], backend.name)
                self.assertEqual("running", e["status"], backend.name)
                # (c) FRESH result (mtime at/after dispatch) -> completed
                write_result_with_mtime(root / result, self.BASE + 60)
                fresh, e = backend.verify(entries, session, root=root)
                self.assertTrue(fresh, backend.name)
                self.assertEqual("completed", e["status"], backend.name)


class RecoverBackendActionTests(unittest.TestCase):
    """Decision 6: recover classification stays uniform; only the RESUMABLE
    resume-ACTION text in the report becomes backend-aware."""

    @staticmethod
    def _resumable_entry(**over):
        base = {
            "session_name": "constellation/issue-1/g1/implementer/attempt-1",
            "work_id": "issue-1", "gate": "g1", "role": "implementer", "attempt": 1,
            "worktree": ".", "status": "running", "pid": None, "resumable": True,
            "result": result_rel("issue-1", "g1", "implementer"),
        }
        base.update(over)
        return base

    def _report_lines(self, entry):
        classified = REC.classify_registry(
            [entry], alive=lambda pid: False, result_present=lambda e: False
        )
        # classification is identical regardless of backend
        self.assertEqual(REC.STATE_RESUMABLE, classified[0][1])
        lines: list[str] = []
        REC.report(classified, out=lines.append)
        return lines

    def test_cli_resumable_action_names_run_crew_resume(self):
        lines = self._report_lines(self._resumable_entry(backend="cli", pid=222))
        joined = " ".join(lines)
        self.assertIn("RESUMABLE", joined)
        self.assertIn("run_crew.py --resume", joined)

    def test_external_resumable_action_names_sendmessage_or_relaunch(self):
        lines = self._report_lines(
            self._resumable_entry(backend="external", dispatch="external", pid=None)
        )
        joined = " ".join(lines)
        self.assertIn("RESUMABLE", joined)             # classification unchanged
        low = joined.lower()
        self.assertIn("unrecoverable by the wrapper", low)
        self.assertIn("abandon", low)
        self.assertNotIn("run_crew.py --resume", joined)  # not the cli action

    def test_legacy_external_marker_infers_external_action(self):
        """A legacy external entry (dispatch marker, no `backend`) still gets the
        external resume action via entry_backend inference."""
        lines = self._report_lines(self._resumable_entry(dispatch="external", pid=None))
        self.assertIn("unrecoverable by the wrapper", " ".join(lines).lower())


if __name__ == "__main__":
    unittest.main()
