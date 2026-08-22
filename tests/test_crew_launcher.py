import importlib.util
import contextlib
import hashlib
import io
import json
import multiprocessing
import os
import shlex
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from datetime import datetime, timedelta, timezone
from unittest import mock
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


def _concurrent_registry_dispatch_worker(
    run_crew_path: str,
    root_path: str,
    gate: str,
    ready,
    release,
    outcome,
) -> None:
    """Load one stale snapshot, then dispatch after both writers are ready."""
    module = load_module(f"run_crew_concurrent_{gate}", Path(run_crew_path))
    root = Path(root_path)
    work_id = "issue-636"
    entries = module.load_registry(module.registry_path(work_id, root))
    ready.put(gate)
    if not release.wait(timeout=15):
        outcome.put(f"{gate}: timed out waiting for release")
        return
    spec = module.CrewSpec(
        work_id=work_id,
        gate=gate,
        role="implementer",
        handoff=f".agent-work/{work_id}/{gate}-handoff.md",
        result=f".agent-work/{work_id}/{gate}-result.md",
        worktree=".",
        attempt=1,
        model="sonnet",
        parent="test-parent",
    )
    try:
        module.ExternalBackend().dispatch(spec, root=root, entries=entries)
    except Exception as exc:
        outcome.put(f"{gate}: {exc!r}")
    else:
        outcome.put(None)


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
    real agent CLI is ever spawned.

    `cwd` is declared (defaulted, never asserted on here) because the dispatch
    paths now pass the crew's own worktree to the seam (issue #568); the double
    must accept what production sends it. What is actually passed is asserted in
    `tests/test_crew_worktree_cwd.py`, which owns that behaviour."""
    calls: list[dict] = []
    original = RC_mod.launch_process

    def fake(argv, *, stdin, env, stdout_path, stderr_path, cwd=None):
        calls.append(
            {"argv": argv, "stdin": stdin, "env": env, "cwd": cwd,
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


@contextlib.contextmanager
def no_ambient_spine_env():
    """Strip SPINE_FILE/SPINE_SESSION from THIS process's environment for the
    duration of the block. A dispatch with NO explicit `--spine` leaves the
    inherited-environment route untouched (`crew_env()`'s documented contract
    for the Admiral's own bootstrap), so a test running under a harness that
    already has its OWN SPINE_FILE bound (as this suite does, when driven by a
    crew whose own door is bound) would otherwise observe that ambient value
    instead of "no SPINE_FILE at all" for a dispatch that passed none."""
    saved = {k: os.environ.pop(k, None) for k in ("SPINE_FILE", "SPINE_SESSION")}
    try:
        yield
    finally:
        for k, v in saved.items():
            if v is not None:
                os.environ[k] = v


@contextlib.contextmanager
def no_ambient_parent_env():
    """Strip SPINE_PARENT from THIS process's environment for the duration of
    the block -- the parent analog of `no_ambient_spine_env`, for tests that
    must observe a dispatched child's SPINE_PARENT unpolluted by whatever
    parent the TEST-RUNNING process itself happens to carry."""
    saved = os.environ.pop("SPINE_PARENT", None)
    try:
        yield
    finally:
        if saved is not None:
            os.environ["SPINE_PARENT"] = saved


INSTALLER_PY = ROOT / "scripts" / "install_constellation.py"


class InstalledBundleTests(unittest.TestCase):
    """#559 pass 3, blocker 1: `2152ded3` added `import install_constellation`
    at module scope in `run_crew.py` (#539's `assert_shell_safe_command`), but
    no bundle carrying `run_crew.py` shipped `install_constellation.py` as a
    companion -- every installed Commander and Explorer raised
    `ModuleNotFoundError` at import, before argparse ever ran, and could
    launch no crew at all. Reproduced two-sidedly against real installs.

    These build a REAL installed bundle through the installer itself (never a
    hand-picked file copy, which could pass by accident) and run the
    INSTALLED `run_crew.py --help` as a real subprocess -- only a real
    subprocess proves the import resolves in the tree the installer actually
    produces."""

    def _installed_run_crew_help(self, skill: str, installed_name: str) -> subprocess.CompletedProcess:
        installer = load_module("install_constellation", INSTALLER_PY)
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "skills"
            rc = installer.main(
                ["--agent", "claude", "--scope", "user", "--dest", str(dest),
                 "--skills", skill],
                env={}, out=lambda _line: None,
            )
            self.assertEqual(0, rc)
            run_crew = dest / installed_name / "scripts" / "run_crew.py"
            self.assertTrue(run_crew.is_file(), f"{run_crew} was not installed")
            return subprocess.run(
                [sys.executable, str(run_crew), "--help"],
                capture_output=True, text=True,
            )

    def test_installed_commander_bundle_run_crew_help_works(self):
        result = self._installed_run_crew_help("commander", "constellation-commander")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertNotIn("ModuleNotFoundError", result.stderr)

    def test_installed_explorer_bundle_run_crew_help_works(self):
        result = self._installed_run_crew_help("explorer", "constellation-explorer")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertNotIn("ModuleNotFoundError", result.stderr)


class RegistryConcurrencyTests(unittest.TestCase):
    def test_concurrent_registry_dispatches_preserve_both_entries(self):
        """Two independently loaded production writers preserve both entries."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            work = root / ".agent-work" / "issue-636"
            work.mkdir(parents=True)
            for gate in ("writer-a", "writer-b"):
                (work / f"{gate}-handoff.md").write_text(
                    "bounded handoff\n", encoding="utf-8", newline="\n"
                )

            context = multiprocessing.get_context("spawn")
            ready = context.Queue()
            release = context.Event()
            outcome = context.Queue()
            processes = [
                context.Process(
                    target=_concurrent_registry_dispatch_worker,
                    args=(str(RUN_CREW), str(root), gate, ready, release, outcome),
                )
                for gate in ("writer-a", "writer-b")
            ]
            for process in processes:
                process.start()
            observed_ready = {ready.get(timeout=15), ready.get(timeout=15)}
            self.assertEqual({"writer-a", "writer-b"}, observed_ready)
            release.set()
            for process in processes:
                process.join(timeout=15)
                self.assertFalse(process.is_alive(), "concurrent writer did not exit")
                self.assertEqual(0, process.exitcode)
            outcomes = [outcome.get(timeout=5) for _ in processes]
            self.assertEqual([None, None], sorted(outcomes, key=str))

            registry_path = RC.registry_path("issue-636", root)
            registry = RC.load_registry(registry_path)
            self.assertEqual(
                {
                    "constellation/issue-636/writer-a/implementer/attempt-1",
                    "constellation/issue-636/writer-b/implementer/attempt-1",
                },
                {entry["session_name"] for entry in registry},
            )
            json.loads(registry_path.read_text(encoding="utf-8"))

    def test_save_registry_is_atomic_and_keeps_public_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nested" / "crew-runs.json"
            entries = [{"session_name": "crew-a", "crew_id": "crew-a"}]
            calls = []
            real_replace = RC.os.replace

            def track_replace(source, target):
                calls.append((Path(source), Path(target)))
                return real_replace(source, target)

            RC.os.replace = track_replace
            try:
                RC.save_registry(path, entries)
            finally:
                RC.os.replace = real_replace

            self.assertEqual(entries, RC.load_registry(path))
            self.assertEqual(1, len(calls))
            source, target = calls[0]
            self.assertEqual(path, target)
            self.assertEqual(path.parent, source.parent)
            self.assertNotEqual(path, source)
            self.assertEqual([], list(path.parent.glob("crew-runs.json.*.tmp")))

    def test_stable_identity_mutation_preserves_new_unrelated_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "crew-runs.json"
            first = {"session_name": "crew-a", "crew_id": "crew-a", "status": "running"}
            second = {"session_name": "crew-b", "crew_id": "crew-b", "status": "running"}
            RC.save_registry(path, [first])
            stale_first = RC.load_registry(path)[0]
            RC.append_registry_entry(path, second)

            def complete(entry):
                entry["status"] = "completed"

            snapshot, current, _ = RC.mutate_registry_entry(
                path, "crew-a", complete, seed=stale_first
            )
            self.assertEqual({"crew-a", "crew-b"}, {entry["session_name"] for entry in snapshot})
            self.assertEqual("completed", current["status"])
            self.assertEqual(
                {"crew-a", "crew-b"},
                {entry["session_name"] for entry in RC.load_registry(path)},
            )

    def test_seeded_target_absent_preserves_same_session_other_worktree(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "crew-runs.json"
            identity = "constellation/issue-636/g1/implementer/attempt-1"
            persisted_y = {
                "session_name": identity,
                "crew_id": identity,
                "worktree": "/worktree/y",
                "marker": "Y",
                "status": "running",
            }
            expected_y = dict(persisted_y)
            seed_x = {
                "session_name": identity,
                "crew_id": identity,
                "worktree": "/worktree/x",
                "marker": "X",
                "status": "running",
            }
            RC.save_registry(path, [persisted_y])

            def complete(entry):
                entry["status"] = "completed"

            snapshot, current, _ = RC.mutate_registry_entry(
                path, identity, complete, seed=seed_x
            )

            self.assertEqual("X", current["marker"])
            self.assertEqual("/worktree/x", current["worktree"])
            self.assertEqual("completed", current["status"])
            self.assertEqual(2, len(snapshot))
            persisted = RC.load_registry(path)
            persisted_x = next(
                entry for entry in persisted if entry["worktree"] == "/worktree/x"
            )
            persisted_y_after = next(
                entry for entry in persisted if entry["worktree"] == "/worktree/y"
            )
            self.assertEqual("completed", persisted_x["status"])
            self.assertEqual(expected_y, persisted_y_after)

    def test_windows_registry_lock_adapter_contract(self):
        class FakeMsvcrt:
            LK_LOCK = 1
            LK_UNLCK = 2

            def __init__(self):
                self.calls = []

            def locking(self, fd, mode, count):
                self.calls.append((fd, mode, count))

        with tempfile.TemporaryDirectory() as tmp:
            lock_path = Path(tmp) / "crew-runs.json.lock"
            lock_path.write_bytes(b"\0")
            with open(lock_path, "a+b") as lock_file:
                fake = FakeMsvcrt()
                lock_file.seek(1)
                RC._windows_registry_lock(lock_file, fake)
                self.assertEqual(
                    [(lock_file.fileno(), FakeMsvcrt.LK_LOCK, 1)], fake.calls
                )
                lock_file.seek(1)
                RC._windows_registry_unlock(lock_file, fake)
                self.assertEqual(
                    (lock_file.fileno(), FakeMsvcrt.LK_UNLCK, 1), fake.calls[-1]
                )


class SessionNameTests(unittest.TestCase):
    def test_session_name_is_deterministic(self):
        name = RC.session_name("issue-420", "g2", "reviewer", 1)
        self.assertEqual("constellation/issue-420/g2/reviewer/attempt-1", name)
        self.assertEqual(name, RC.session_name("issue-420", "g2", "reviewer", 1))
        self.assertEqual(
            "constellation/issue-420/g2/reviewer/attempt-2",
            RC.session_name("issue-420", "g2", "reviewer", 2),
        )

    def test_assignment_session_name_strips_attempt_tail(self):
        self.assertEqual(
            "constellation/issue-420/g2/reviewer",
            RC.assignment_session_name("issue-420", "g2", "reviewer"),
        )

    def test_assignment_session_name_is_stable_across_attempts(self):
        # The whole point: a respawn (attempt-2) must derive the SAME lease
        # identity as the original (attempt-1), so it resumes instead of reading
        # as a different claimant.
        first = RC.assignment_session_name("issue-420", "g2", "reviewer")
        RC.session_name("issue-420", "g2", "reviewer", 2)  # attempt bump, side-effect-free
        second = RC.assignment_session_name("issue-420", "g2", "reviewer")
        self.assertEqual(first, second)

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

    def test_build_crew_argv_grants_permission_mode_and_allowed_tools(self):
        # A dispatch into a worktree with no hand-written .claude/settings.local.json
        # must be able to do crew work end to end (M2 job 1) -- the launcher, not
        # the operator, grants what a spawned crew needs.
        argv = RC.build_crew_argv(
            "claude", role="implementer", handoff="h.md", model=None, session="s",
        )
        self.assertIn("--permission-mode", argv)
        mode_idx = argv.index("--permission-mode")
        self.assertEqual(RC.DEFAULT_CREW_PERMISSION_MODE, argv[mode_idx + 1])
        self.assertIn("--allowedTools", argv)
        tools_idx = argv.index("--allowedTools")
        tools = argv[tools_idx + 1:]
        for expected in ("Bash", "Read", "Write", "Edit", "mcp__spine__spine_advance"):
            self.assertIn(expected, tools)

    def test_build_crew_argv_adds_settings_before_allowed_tools(self):
        # --settings must land BEFORE --allowedTools so the open-ended
        # `argv[tools_idx + 1:]` slice other tests use to read "the granted
        # tools" is never polluted by an unrelated flag.
        argv = RC.build_crew_argv(
            "claude", role="implementer", handoff="h.md", model=None, session="s",
        )
        self.assertIn("--settings", argv)
        self.assertLess(argv.index("--settings"), argv.index("--allowedTools"))


class SpineOwnershipPromptTests(unittest.TestCase):
    """Issue #559: a dispatched crew's whole job used to be "read this
    document". These pin the pre-#559 handoff prompt byte for byte (the
    CONTROL) and the new spine-carried branch that replaces the CLI-fallback
    instruction with a direct instruction to drive the bound spine."""

    def test_control_handoff_branch_is_byte_identical_to_the_pre_559_prompt(self):
        # CONTROL, recorded verbatim against a1-control: today's -- i.e.
        # pre-#559 -- prompt names the handoff path and never mentions the
        # spine or spine_status anywhere. Updated for E1 fail-up (#559
        # follow-on): every prompt now also names the crew's parent (or says
        # plainly it is unknown), so the pin includes that clause too.
        argv = RC.build_crew_argv(
            "claude", role="reviewer", handoff="/abs/g2-reviewer.md",
            model=None, session="s",
        )
        prompt = argv[2]
        self.assertEqual(
            "You are the constellation reviewer crew for session s. "
            "Your parent is unknown: never invent one. "
            "Read the handoff at /abs/g2-reviewer.md and execute it exactly. "
            "The run is only complete when the result artifact the handoff names exists.",
            prompt,
        )
        self.assertNotIn("spine", prompt.lower())

    def test_handoff_branch_unaffected_by_an_also_bound_spine(self):
        # A crew given BOTH a handoff and a spine (today's normal combined
        # dispatch, e.g. this very implementer run) still gets the handoff
        # prompt, byte for byte: the new branch only fires when handoff is
        # ABSENT, not merely when a spine happens to also be bound.
        with_spine = RC.build_crew_argv(
            "claude", role="reviewer", handoff="/abs/g2-reviewer.md",
            spine="/abs/spine.json", model=None, session="s",
        )
        without_spine = RC.build_crew_argv(
            "claude", role="reviewer", handoff="/abs/g2-reviewer.md",
            model=None, session="s",
        )
        self.assertEqual(without_spine[2], with_spine[2])

    def test_spine_only_branch_names_no_document_and_names_spine_status(self):
        argv = RC.build_crew_argv(
            "claude", role="implementer", handoff=None,
            spine="/abs/.agent-work/w/IMPLEMENTER_PLAN.json",
            model=None, session="constellation/w/g1/implementer/attempt-1",
        )
        prompt = argv[2]
        self.assertNotIn("/abs/.agent-work/w/IMPLEMENTER_PLAN.json", prompt)
        self.assertNotIn(".json", prompt)
        self.assertNotIn(".md", prompt)
        self.assertIn("spine_status", prompt)
        self.assertIn("constellation/w/g1/implementer/attempt-1", prompt)

    def test_spine_only_branch_tells_crew_not_to_author_its_own_plan(self):
        argv = RC.build_crew_argv(
            "claude", role="implementer", handoff=None, spine="/abs/spine.json",
            model=None, session="s",
        )
        self.assertIn("do not author a plan", argv[2].lower())

    def test_neither_handoff_nor_spine_is_refused(self):
        with self.assertRaises(RC.CrewLaunchError):
            RC.build_crew_argv(
                "claude", role="implementer", handoff=None, spine=None,
                model=None, session="s",
            )


class ParentPromptTests(unittest.TestCase):
    """E1 fail-up (#559 follow-on): a crew that hits a check it cannot
    satisfy must have somewhere to ask up. `build_crew_argv` names the
    dispatching parent (or plainly says it is unknown) on BOTH prompt
    branches -- handoff and spine-only -- so a crew reading either one
    always knows who to ask, or that nobody said."""

    def test_handoff_branch_names_the_given_parent(self):
        argv = RC.build_crew_argv(
            "claude", role="implementer", handoff="/abs/h.md", model=None,
            session="s", parent="constellation/epic-1/commander",
        )
        self.assertIn("constellation/epic-1/commander", argv[2])

    def test_handoff_branch_says_unknown_when_parent_omitted(self):
        argv = RC.build_crew_argv(
            "claude", role="implementer", handoff="/abs/h.md", model=None, session="s",
        )
        self.assertIn(f"parent is {RC.UNKNOWN_PARENT}", argv[2])

    def test_spine_only_branch_names_the_given_parent(self):
        argv = RC.build_crew_argv(
            "claude", role="implementer", handoff=None, spine="/abs/spine.json",
            model=None, session="s", parent="constellation/epic-1/commander",
        )
        self.assertIn("constellation/epic-1/commander", argv[2])

    def test_spine_only_branch_says_unknown_when_parent_omitted(self):
        argv = RC.build_crew_argv(
            "claude", role="implementer", handoff=None, spine="/abs/spine.json",
            model=None, session="s",
        )
        self.assertIn(f"parent is {RC.UNKNOWN_PARENT}", argv[2])

    def test_no_parent_given_never_invents_one(self):
        # The ruling this whole gate exists for: a dispatch with no --parent
        # must say plainly it does not know, never guess a name (e.g. the
        # role, the session, or some other in-scope string) that reads as a
        # real identity.
        argv = RC.build_crew_argv(
            "claude", role="implementer", handoff="/abs/h.md", model=None, session="s",
        )
        prompt = argv[2]
        self.assertIn("never invent", prompt.lower())
        self.assertNotIn("Your parent is implementer", prompt)
        self.assertNotIn("Your parent is s.", prompt)


class BlankParentTests(unittest.TestCase):
    """The one hole a cold reviewer found in E1 (#559 follow-on): both
    `_parent_clause` and `_crew_door_env` used plain truthiness on `parent`,
    so `""` correctly collapsed to the unknown marker but a WHITESPACE-ONLY
    string (`"   "`) is truthy and sailed straight through -- into the
    prompt (naming a parent with no real identity) and into the durable
    registry (recorded verbatim, so a resume would read it back as if it
    were a real parent). `_normalize_parent` strips first: a parent that is
    blank after stripping is treated exactly like an omitted one, in both
    places, and in `_crew_door_env`'s SPINE_PARENT binding too."""

    def test_whitespace_only_parent_reads_as_unknown_in_the_prompt(self):
        argv = RC.build_crew_argv(
            "claude", role="implementer", handoff="/abs/h.md", model=None,
            session="s", parent="   ",
        )
        self.assertIn(f"parent is {RC.UNKNOWN_PARENT}", argv[2])
        self.assertNotIn("Your parent is    :", argv[2])

    def test_whitespace_only_parent_is_recorded_as_none_not_verbatim(self):
        entry = RC.build_entry(
            work_id="issue-1", gate="g1", role="implementer", attempt=1,
            worktree=".", handoff="h.md", result="r.md", root=Path("."),
            started="2026-07-07T00:00:00+00:00", backend="cli", pid=1,
            parent="   ",
        )
        self.assertIsNone(entry["parent"])

    def test_whitespace_only_parent_binds_unknown_in_the_door_env(self):
        with no_ambient_parent_env():
            env = RC._crew_door_env(
                work_id="issue-1", gate="g1", role="implementer", spine=None,
                root=Path("."), parent="   ",
            )
        self.assertEqual(RC.UNKNOWN_PARENT, env["SPINE_PARENT"])

    def test_non_blank_parent_with_padding_is_unaffected(self):
        argv = RC.build_crew_argv(
            "claude", role="implementer", handoff="/abs/h.md", model=None,
            session="s", parent="  constellation/epic-1/commander  ",
        )
        self.assertIn("constellation/epic-1/commander", argv[2])
        self.assertNotIn(RC.UNKNOWN_PARENT, argv[2])


class WaiveHookTests(unittest.TestCase):
    """Ruling (human, verbatim): "agent cannot waive itself... always ask up."
    A crew keeps `mcp__spine__spine_evidence` (attest/attach still need it),
    but a PreToolUse hook denies the one action inside it -- `waive` -- that
    would let a crew close its own bound spine's check. These invoke the exact
    hook command `build_crew_argv` embeds, piping fake tool-call JSON at it, so
    the behavior is checked without spawning a real agent CLI."""

    def _run_hook(self, action: str) -> dict:
        argv = RC.build_crew_argv(
            "claude", role="implementer", handoff="h.md", model=None, session="s",
        )
        settings = json.loads(argv[argv.index("--settings") + 1])
        pre_tool_use = settings["hooks"]["PreToolUse"][0]
        self.assertEqual("mcp__spine__spine_evidence", pre_tool_use["matcher"])
        hook = pre_tool_use["hooks"][0]
        command = hook["command"]
        self.assertEqual("command", hook["type"])
        self.assertEqual("bash", hook["shell"])
        # `command` is `<quoted sys.executable> -c '<script>'`; extract
        # `<script>` rather than asking a shell to parse the quoting, so this
        # test does not depend on a shell being on PATH the same way the real
        # hook runner does. `RC.posix_command_word`, not `shlex.quote` -- on
        # Linux `sys.executable` rarely needs escaping either way, but only
        # `posix_command_word` matches what `crew_settings_json` actually
        # emits on a Windows host, where `sys.executable`'s backslashes make
        # the two diverge (`shlex.quote` wraps the whole path in a leading
        # apostrophe; `posix_command_word` never does -- see its module
        # comment in run_crew.py).
        prefix = f"{RC.posix_command_word(sys.executable)} -c '"
        self.assertTrue(command.startswith(prefix))
        self.assertTrue(command.endswith("'"))
        script = command[len(prefix):-1]
        proc = subprocess.run(
            [sys.executable, "-c", script],
            input=json.dumps({
                "tool_name": "mcp__spine__spine_evidence",
                "tool_input": {"action": action, "task_id": "g1"},
            }),
            capture_output=True, text=True,
        )
        self.assertEqual(0, proc.returncode, proc.stderr)
        return json.loads(proc.stdout)

    def test_waive_is_denied(self):
        out = self._run_hook("waive")
        specific = out["hookSpecificOutput"]
        self.assertEqual("deny", specific["permissionDecision"])
        self.assertIn("spine_halt", specific["permissionDecisionReason"])
        self.assertIn("block", specific["permissionDecisionReason"].lower())

    def test_attest_carries_no_opinion(self):
        self.assertEqual({}, self._run_hook("attest"))

    def test_attach_carries_no_opinion(self):
        self.assertEqual({}, self._run_hook("attach"))

    def test_waive_deny_reason_has_no_apostrophe(self):
        # The reason string is interpolated into a single-quoted shell command
        # (`crew_settings_json`); a literal apostrophe would terminate that
        # quoting early and corrupt the emitted hook command.
        self.assertNotIn("'", RC.WAIVE_DENY_REASON)


class HookPortabilityTests(unittest.TestCase):
    """#539: a hardcoded `python3` fails OPEN, not loud, on a host where that
    name is not on PATH -- the hook command cannot run, the harness treats a
    non-JSON/erroring hook as no opinion, and a crew can waive its own bound
    spine check with nothing to say so. The fix names no interpreter but
    `sys.executable` (this process's own, present by construction) and pins
    `shell: bash` so the single-quoted inline program survives a non-POSIX
    parse."""

    def _hook_entry(self) -> dict:
        settings = json.loads(RC.crew_settings_json())
        return settings["hooks"]["PreToolUse"][0]["hooks"][0]

    def test_hook_interpreter_is_sys_executable_not_a_hardcoded_name(self):
        command = self._hook_entry()["command"]
        interpreter = shlex.split(command)[0]
        self.assertEqual(sys.executable, interpreter)
        self.assertNotIn(interpreter, ("python3", "python", "py"))

    def test_hook_entry_carries_shell_bash(self):
        # Matches every hook entry in this repo's own .claude/settings.json:
        # without it, `shlex.split(cmd, posix=False)` leaves the quotes on and
        # a non-POSIX shell (cmd.exe) reads a program starting with an
        # apostrophe and dies -- another silent fail-open.
        self.assertEqual("bash", self._hook_entry()["shell"])

    def test_crew_settings_json_actually_calls_the_shell_safety_guard(self):
        # Proves the guard is wired in, not decorative dead code: force it to
        # raise and confirm `crew_settings_json` propagates that failure
        # instead of swallowing it or never calling it.
        original = RC.install_constellation.assert_shell_safe_command

        def boom(command):
            raise RC.install_constellation.InstallError("forced for test")

        RC.install_constellation.assert_shell_safe_command = boom
        try:
            with self.assertRaises(RC.install_constellation.InstallError):
                RC.crew_settings_json()
        finally:
            RC.install_constellation.assert_shell_safe_command = original


class WindowsInterpreterQuotingTests(unittest.TestCase):
    """89 Windows-CI failures, one bug: `crew_settings_json` used to quote
    `sys.executable` with `shlex.quote`, which wraps ANY string containing a
    shell-unsafe character -- and a bare backslash counts as unsafe by its
    definition, not just a space -- in a leading `'...'` literal. A real
    Windows interpreter path (`C:\\hostedtoolcache\\...\\python.exe`) is all
    backslashes and no spaces, so `shlex.quote` quoted it every time and the
    composed hook command started with an apostrophe: exactly the shape
    `assert_shell_safe_command` (install_constellation.py, #539) exists to
    refuse. `posix_command_word` fixes this by escaping unsafe characters
    individually instead of wrapping the whole word, so the result never
    starts with a quote mark.

    This does not need an actual Windows host: `posix_command_word` is pure
    string logic, and a Windows-shaped path is just a string. Monkeypatching
    `sys.executable` exercises the exact failure shape on Linux."""

    def test_windows_backslash_path_survives_the_shell_safety_guard(self):
        # The exact interpreter string GitHub Actions' windows-latest runner
        # reported in the CI log that motivated this fix.
        windows_python = r"C:\hostedtoolcache\windows\Python\3.12.10\x64\python.exe"
        with mock.patch.object(sys, "executable", windows_python):
            command = json.loads(RC.crew_settings_json())[
                "hooks"]["PreToolUse"][0]["hooks"][0]["command"]
        # Would raise InstallError before this fix -- see the positive
        # control below, which proves the OLD `shlex.quote` composition
        # really does trip this same guard on this same input.
        RC.install_constellation.assert_shell_safe_command(command)
        self.assertEqual(windows_python, shlex.split(command)[0])

    def test_windows_path_with_spaces_also_survives(self):
        # A Program-Files-style install path: needs quoting for the space,
        # same as `shlex.quote` handled correctly -- this is the case the
        # original docstring cited as `shlex.quote`'s reason for existing.
        windows_python = r"C:\Program Files\Python312\python.exe"
        with mock.patch.object(sys, "executable", windows_python):
            command = json.loads(RC.crew_settings_json())[
                "hooks"]["PreToolUse"][0]["hooks"][0]["command"]
        RC.install_constellation.assert_shell_safe_command(command)
        self.assertEqual(windows_python, shlex.split(command)[0])

    def test_positive_control_shlex_quote_alone_trips_the_guard(self):
        # Proves this test suite would have caught the original bug: composing
        # the SAME hook command with plain `shlex.quote` (the pre-fix
        # behavior) on the SAME Windows-shaped path really does start with an
        # apostrophe and really does fail `assert_shell_safe_command`. Without
        # this, the two tests above could pass vacuously -- e.g. if
        # `assert_shell_safe_command` were accidentally disabled -- and no
        # test here would notice.
        windows_python = r"C:\hostedtoolcache\windows\Python\3.12.10\x64\python.exe"
        old_style_command = f"{shlex.quote(windows_python)} -c 'pass'"
        self.assertTrue(old_style_command.startswith("'"))
        with self.assertRaises(RC.install_constellation.InstallError):
            RC.install_constellation.assert_shell_safe_command(old_style_command)

    def test_posix_command_word_round_trips_special_characters(self):
        # `shlex.split` (POSIX mode) is the same escaping grammar bash uses,
        # so a correct escaped word must survive that round trip unchanged --
        # this is what makes the quoting correct, not just guard-satisfying.
        for word in (
            r"C:\hostedtoolcache\windows\Python\3.12.10\x64\python.exe",
            r"C:\Program Files\Python312\python.exe",
            "plain/posix/path/python3",
            "a'quote'in'it",
        ):
            escaped = RC.posix_command_word(word)
            self.assertNotIn(escaped[0], "\"' \t")
            self.assertEqual([word], shlex.split(escaped))


class CrewGrantTiesToDoorTests(unittest.TestCase):
    """`CREW_ALLOWED_TOOLS` used to restate the door's tool names by hand and
    froze at 7 while `mcp_spine_server.TOOLS` grew to 9 -- two tools silently
    denied to every crew. This ties the two lists so that drift fails loudly
    instead of reading as an agent's CLI preference."""

    def _load_mcp_spine_server(self, scratch_root: Path):
        spine_file = scratch_root / "scratch-spine.json"
        spine_file.write_text("{}", encoding="utf-8")
        saved = {k: os.environ.get(k) for k in ("SPINE_FILE", "SPINE_ENGINE", "SPINE_SESSION")}
        os.environ["SPINE_FILE"] = str(spine_file)
        os.environ["SPINE_ENGINE"] = str(ROOT / "scripts" / "checklist_engine.py")
        os.environ.setdefault("SPINE_SESSION", "")
        try:
            # A fresh module name each call: mcp_spine_server reads SPINE_FILE
            # at IMPORT time, so a cached `sys.modules` entry would carry a
            # stale binding on a second load in the same test process.
            return load_module("mcp_spine_server_tie_check", ROOT / "scripts" / "mcp_spine_server.py")
        finally:
            for k, v in saved.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

    def test_crew_grant_mcp_entries_equal_the_doors_own_tool_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            server = self._load_mcp_spine_server(Path(tmp))
        door_tools = {f"mcp__spine__{name}" for name in server.TOOL_NAMES}
        grant_tools = {t for t in RC.CREW_ALLOWED_TOOLS if t.startswith("mcp__spine__")}
        self.assertEqual(
            door_tools, grant_tools,
            "CREW_ALLOWED_TOOLS's mcp__spine__* entries have drifted from "
            "mcp_spine_server.TOOL_NAMES -- a tool the door added (or removed) "
            "is not reflected in the crew grant"
        )

    def test_door_has_all_nine_tools_todays_grant_expects(self):
        # CONTROL for the tie test above: pins the count so a future door
        # regression (e.g. a tool silently dropped) cannot slip through by
        # shrinking BOTH sides of the comparison in lockstep. 9 engine tools +
        # 3 lifecycle tools (spine_open, spine_close -- issue #559, C3/g3; and
        # spine_bind -- issue #559 lane A, which binds the door to a spine that
        # already exists) = 12; unlike test_mcp_adoption.py's Tier3-doc-tied pin,
        # CREW_ALLOWED_TOOLS has no doc dependency, so this one is NOT scoped down.
        #
        # The method name says "nine" and the count has been 11 and is now 12.
        # The name is historical and deliberately left alone: renaming it would
        # churn a control whose whole value is that it is hard to change by
        # accident. Read the assertion, not the name.
        #
        # This control did its job. When lane A added spine_bind, the tie test
        # above went green on its own (both sides moved together, which is
        # exactly the lockstep failure it cannot see) and only this count
        # assertion went red -- forcing the change to be acknowledged here in
        # writing rather than absorbed silently.
        with tempfile.TemporaryDirectory() as tmp:
            server = self._load_mcp_spine_server(Path(tmp))
        self.assertEqual(12, len(server.TOOL_NAMES))


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

    # -- ISSUE #454 regression guard ------------------------------------------
    # The harness exports FORCE_COLOR=3, so the agent CLI colourizes even into the
    # captured stderr file this reads. Every drift marker is a two-word phrase, so
    # one escape between the words silences the hint entirely.

    def test_a_colourized_drift_line_still_yields_the_hint(self):
        hint = RC.cli_drift_hint("\x1b[31merror\x1b[0m: \x1b[1munknown\x1b[0m option '--session'\n")
        self.assertIsNotNone(
            hint,
            "#454 REGRESSION: a colourized flag-drift line produced no hint, so plain "
            "CLI drift would read as an unexplained crew failure.",
        )
        self.assertIn("--backend external", hint)

    def test_the_quoted_line_in_the_hint_is_plain_text(self):
        """A hint that echoes escape bytes back at a human is half a hint.

        The hint interpolates `line.strip()!r`, so an uncleaned escape arrives in
        the message as the four visible characters `\\x1b` -- which is why this
        asserts on that literal rather than on the ESC byte, whose repr would
        never survive to be found.
        """
        hint = RC.cli_drift_hint("\x1b[31munrecognized arguments: --role\x1b[0m\n")
        self.assertIsNotNone(hint)
        self.assertNotIn("\\x1b", hint, "#454 REGRESSION: escape junk reached the human-facing hint.")
        self.assertIn("'unrecognized arguments: --role'", hint)

    def test_colour_stripping_does_not_invent_drift(self):
        """The guard must not have been bought by making the sniff trigger-happy."""
        self.assertIsNone(RC.cli_drift_hint("\x1b[31mRuntimeError: crew died\x1b[0m\n"))


class LaunchTests(unittest.TestCase):
    def test_missing_handoff_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(RC.CrewLaunchError):
                RC.launch_crew(
                    work_id="issue-1", gate="g1", role="implementer",
                    handoff=".agent-work/issue-1/crew-handoffs/g1-implementer.md",
                    result=result_rel("issue-1", "g1", "implementer"),
                    worktree=".", model="sonnet", launcher="claude", attempt=1,
                    root=root, entries=[],
                    parent="test-parent",
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
                    parent="test-parent",
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
                    handoff=handoff, result=result, worktree=".", model="sonnet",
                    launcher="claude", attempt=1, root=root, entries=[],
                    parent="test-parent",
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
                    handoff=handoff, result=result, worktree=".", model="sonnet",
                    launcher="claude", attempt=1, root=root, entries=[],
                    parent="test-parent",
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
                    "--parent", "test-parent",
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
                        "--model", "sonnet",
                        "--parent", "test-parent",
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
                    code = RC.main(["--root", str(root), "--resume", session, "--parent", "test-parent"])
            self.assertEqual(0, code)
            self.assertIn(session, " ".join(calls[0]["argv"]))
            reg = RC.load_registry(RC.registry_path("issue-1", root))
            self.assertEqual("completed", reg[0]["status"])

    def test_resume_unknown_session_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with contextlib.redirect_stderr(io.StringIO()):
                code = RC.main(["--root", str(root), "--resume",
                                "constellation/issue-1/g1/reviewer/attempt-9", "--parent", "test-parent"])
            self.assertEqual(1, code)


class MandatoryModelTests(unittest.TestCase):
    """g2/g3-implement (#633): `CrewSpec.__post_init__` resolves `model`/
    `reason` via `resolve_model` for every fresh/relaunch construction, same
    choke point as its "needs a job"/"needs a completion contract" invariants
    immediately above it. A role/harness pair WITH a `ROLE_MODEL_TIERS` entry
    now resolves an unrequested `model` to that pair's declared default
    instead of unconditionally refusing -- only an undeclared role/harness
    pair, an out-of-set requested model, or a non-default requested model
    given with no `reason` still refuses. `--resume` and a bare `--abandon`
    construct no `CrewSpec` at all (confirmed by reading
    `CliBackend.resume`/`abandon_crew` directly), so neither is touched by
    this resolution."""

    def test_crew_spec_with_falsy_model_resolves_the_role_default(self):
        """g3-implement (#633): `reviewer`/`claude` IS in `ROLE_MODEL_TIERS`, so
        a falsy `model` no longer refuses -- `__post_init__` resolves it to the
        role's declared default via `resolve_model`. The still-refusing case
        for a role/harness pair genuinely absent from the table is covered by
        `test_unpopulated_harness_is_refused_by_name_even_with_model_given`
        below."""
        spec = RC.CrewSpec(
            work_id="issue-1", gate="g1", role="reviewer",
            handoff="h.md", result="r.md", worktree=".", attempt=1,
            model=None,
            parent="test-parent",
        )
        self.assertEqual("sonnet", spec.model)
        self.assertIsNone(spec.reason)

    def test_fresh_dispatch_with_model_records_it(self):
        """Green half: an explicit --model succeeds and the registry entry
        carries it (decision:record-the-resolved-tier, already mechanical via
        `build_entry` -- pinned here through the new mandatory-model seam)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "reviewer")
            result = result_rel("issue-1", "g1", "reviewer")
            with fake_launch(RC, 0, write_result_at=root / result):
                with contextlib.redirect_stdout(io.StringIO()):
                    code = RC.main([
                        "--root", str(root), "--work-id", "issue-1", "--gate", "g1",
                        "--role", "reviewer", "--handoff", handoff, "--result", result,
                        "--model", "sonnet",
                        "--parent", "test-parent",
                    ])
            self.assertEqual(0, code)
            reg = RC.load_registry(RC.registry_path("issue-1", root))
            self.assertEqual(1, len(reg))
            self.assertEqual("sonnet", reg[0]["model"])

    def test_fresh_dispatch_with_no_model_resolves_the_role_default(self):
        """g3-implement (#633): `reviewer`/`claude` IS in `ROLE_MODEL_TIERS`, so
        a fresh dispatch through the real CLI entrypoint with no --model given
        no longer refuses -- `CrewSpec.__post_init__` now resolves it to the
        role's declared default (`resolve_model`), and the built registry
        entry carries that resolved default, not a refusal."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "reviewer")
            result = result_rel("issue-1", "g1", "reviewer")
            with fake_launch(RC, 0, write_result_at=root / result) as calls:
                with contextlib.redirect_stdout(io.StringIO()):
                    code = RC.main([
                        "--root", str(root), "--work-id", "issue-1", "--gate", "g1",
                        "--role", "reviewer", "--handoff", handoff, "--result", result,
                        "--parent", "test-parent",
                    ])
            self.assertEqual(0, code)
            self.assertEqual(1, len(calls))  # spawned, unlike the old refusal
            reg = RC.load_registry(RC.registry_path("issue-1", root))
            self.assertEqual(1, len(reg))
            self.assertEqual("sonnet", reg[0]["model"])
            self.assertNotIn("reason", reg[0])

    def test_abandon_relaunch_with_no_model_resolves_the_role_default(self):
        """g3-implement (#633): `reviewer`/`claude` IS in `ROLE_MODEL_TIERS`, so
        `--abandon --relaunch` with no explicit --model no longer refuses --
        no inherit-from-`abandoned.get("model")` fallback (unchanged: this is
        NOT the `reasoning_effort` inherit-on-relaunch shape), just the role's
        declared default resolved fresh, same as any other unrequested model.
        The stored `model="opus"` on the abandoned entry is NOT inherited --
        the relaunch attempt resolves to the default (`sonnet`), not `opus`."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "reviewer")
            result = result_rel("issue-1", "g1", "reviewer")
            entries = [{
                "session_name": "constellation/issue-1/g1/reviewer/attempt-1",
                "crew_id": "constellation/issue-1/g1/reviewer/attempt-1",
                "work_id": "issue-1", "gate": "g1", "role": "reviewer", "attempt": 1,
                "worktree": ".", "status": "running", "abandoned": False,
                "handoff": handoff, "result": result, "model": "opus",
            }]
            RC.save_registry(RC.registry_path("issue-1", root), entries)
            with fake_launch(RC, 0, write_result_at=root / result) as calls:
                with contextlib.redirect_stdout(io.StringIO()):
                    code = RC.main([
                        "--root", str(root),
                        "--abandon", "constellation/issue-1/g1/reviewer/attempt-1",
                        "--relaunch", "--handoff", handoff, "--result", result,
                        "--parent", "test-parent",
                    ])
            self.assertEqual(0, code)
            self.assertEqual(1, len(calls))  # spawned, unlike the old refusal
            reg = RC.load_registry(RC.registry_path("issue-1", root))
            self.assertEqual(2, len(reg))  # abandoned original + relaunched attempt-2
            self.assertEqual("sonnet", reg[1]["model"])
            self.assertNotIn("reason", reg[1])

    def test_abandon_relaunch_with_reason_succeeds_and_entry_carries_reason(self):
        """g3-implement (#633, ruling): `--abandon --relaunch` threads
        `args.reason` into its `CrewSpec(...)` construction exactly parallel
        to the fresh-launch path -- mirrors
        `test_non_default_in_set_model_with_reason_succeeds_and_entry_carries_reason`
        above, for the relaunch call site."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "implementer")
            result = result_rel("issue-1", "g1", "implementer")
            entries = [{
                "session_name": "constellation/issue-1/g1/implementer/attempt-1",
                "crew_id": "constellation/issue-1/g1/implementer/attempt-1",
                "work_id": "issue-1", "gate": "g1", "role": "implementer", "attempt": 1,
                "worktree": ".", "status": "running", "abandoned": False,
                "handoff": handoff, "result": result, "model": "sonnet",
            }]
            RC.save_registry(RC.registry_path("issue-1", root), entries)
            with fake_launch(RC, 0, write_result_at=root / result) as calls:
                with contextlib.redirect_stdout(io.StringIO()):
                    code = RC.main([
                        "--root", str(root),
                        "--abandon", "constellation/issue-1/g1/implementer/attempt-1",
                        "--relaunch", "--handoff", handoff, "--result", result,
                        "--model", "haiku", "--reason", "cheap smoke-test lane",
                        "--parent", "test-parent",
                    ])
            self.assertEqual(0, code)
            self.assertEqual(1, len(calls))  # spawned, unlike the old refusal
            reg = RC.load_registry(RC.registry_path("issue-1", root))
            self.assertEqual(2, len(reg))  # abandoned original + relaunched attempt-2
            self.assertEqual("haiku", reg[1]["model"])
            self.assertEqual("cheap smoke-test lane", reg[1]["reason"])

    def test_explicit_out_of_set_model_is_refused_by_name(self):
        with self.assertRaises(RC.CrewLaunchError) as ctx:
            RC.CrewSpec(
                work_id="issue-1", gate="g1", role="implementer",
                handoff="h.md", result="r.md", worktree=".", attempt=1,
                model="gpt-5",
                parent="test-parent",
            )
        message = str(ctx.exception)
        self.assertIn("gpt-5", message)
        self.assertIn("implementer", message)
        self.assertIn("sonnet", message)
        self.assertIn("haiku", message)

    def test_unpopulated_harness_is_refused_by_name_even_with_model_given(self):
        with self.assertRaises(RC.CrewLaunchError) as ctx:
            RC.CrewSpec(
                work_id="issue-1", gate="g1", role="implementer",
                handoff="h.md", result="r.md", worktree=".", attempt=1,
                model="sonnet", launcher="codex",
                parent="test-parent",
            )
        message = str(ctx.exception)
        self.assertIn("implementer", message)
        self.assertIn("codex", message)

    def test_non_default_in_set_model_with_no_reason_is_refused(self):
        with self.assertRaises(RC.CrewLaunchError) as ctx:
            RC.CrewSpec(
                work_id="issue-1", gate="g1", role="implementer",
                handoff="h.md", result="r.md", worktree=".", attempt=1,
                model="haiku",
                parent="test-parent",
            )
        message = str(ctx.exception)
        self.assertIn("haiku", message)
        self.assertIn("implementer", message)
        self.assertIn("sonnet", message)  # names the default it would override
        self.assertIn("reason", message)

    def test_non_default_in_set_model_with_reason_succeeds_and_entry_carries_reason(self):
        """(d): a resolved non-default tier's `--reason` is threaded end-to-end
        -- CLI flag -> `CrewSpec` -> `build_entry` -- and lands in the durable
        registry entry beside `model`."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "implementer")
            result = result_rel("issue-1", "g1", "implementer")
            with fake_launch(RC, 0, write_result_at=root / result) as calls:
                with contextlib.redirect_stdout(io.StringIO()):
                    code = RC.main([
                        "--root", str(root), "--work-id", "issue-1", "--gate", "g1",
                        "--role", "implementer", "--handoff", handoff, "--result", result,
                        "--model", "haiku", "--reason", "cheap smoke-test lane",
                        "--parent", "test-parent",
                    ])
            self.assertEqual(0, code)
            self.assertEqual(1, len(calls))
            reg = RC.load_registry(RC.registry_path("issue-1", root))
            self.assertEqual(1, len(reg))
            self.assertEqual("haiku", reg[0]["model"])
            self.assertEqual("cheap smoke-test lane", reg[0]["reason"])

    def test_default_tier_dispatch_never_requires_or_records_a_reason_key(self):
        """(e): a default-tier dispatch, whether the default is EXPLICIT
        (--model sonnet) or RESOLVED (no --model at all, covered by
        `test_fresh_dispatch_with_no_model_resolves_the_role_default` above),
        never requires --reason and never writes a "reason" key into the
        registry entry."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "implementer")
            result = result_rel("issue-1", "g1", "implementer")
            with fake_launch(RC, 0, write_result_at=root / result) as calls:
                with contextlib.redirect_stdout(io.StringIO()):
                    code = RC.main([
                        "--root", str(root), "--work-id", "issue-1", "--gate", "g1",
                        "--role", "implementer", "--handoff", handoff, "--result", result,
                        "--model", "sonnet",
                        "--parent", "test-parent",
                    ])
            self.assertEqual(0, code)
            self.assertEqual(1, len(calls))
            reg = RC.load_registry(RC.registry_path("issue-1", root))
            self.assertEqual(1, len(reg))
            self.assertEqual("sonnet", reg[0]["model"])
            self.assertNotIn("reason", reg[0])

    def test_old_shape_registry_entry_with_model_and_no_reason_key_resumes_cleanly(self):
        """A `crew-runs.json` entry from before `reason` existed (a `model` key
        present, no `reason` key at all) must round-trip through `resume_crew`
        without error -- `CliBackend.resume` reads `entry.get("model")`
        directly and never constructs a fresh `CrewSpec`, so an absent
        `reason` key is simply never looked up."""
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
                "handoff": handoff, "result": result, "model": "opus",
                "stdout": RC._relativize(str(stdout), root),
                "stderr": RC._relativize(str(stderr), root),
            }]  # deliberately no "reason" key
            RC.save_registry(RC.registry_path("issue-1", root), entries)
            with fake_launch(RC, 0, write_result_at=root / result):
                with contextlib.redirect_stdout(io.StringIO()):
                    code = RC.main(["--root", str(root), "--resume", session, "--parent", "test-parent"])
            self.assertEqual(0, code)
            reg = RC.load_registry(RC.registry_path("issue-1", root))
            self.assertEqual("opus", reg[0]["model"])
            self.assertNotIn("reason", reg[0])

    def test_resume_needs_no_model_at_all(self):
        """`--resume` constructs no `CrewSpec` (`CliBackend.resume` reads the
        stored entry directly), so a legacy entry with no `model` key at all
        must still resume cleanly -- the new refusal does not reach this path."""
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
            }]  # deliberately no "model" key
            RC.save_registry(RC.registry_path("issue-1", root), entries)
            with fake_launch(RC, 0, write_result_at=root / result):
                with contextlib.redirect_stdout(io.StringIO()):
                    code = RC.main(["--root", str(root), "--resume", session, "--parent", "test-parent"])
            self.assertEqual(0, code)

    def test_bare_abandon_needs_no_model_at_all(self):
        """A bare `--abandon` (no --relaunch) constructs no `CrewSpec` either
        (`abandon_crew` mutates the stored entry directly) -- must succeed with
        no --model given."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entries = [{
                "session_name": "constellation/issue-1/g1/reviewer/attempt-1",
                "crew_id": "constellation/issue-1/g1/reviewer/attempt-1",
                "work_id": "issue-1", "gate": "g1", "role": "reviewer", "attempt": 1,
                "worktree": ".", "status": "running", "abandoned": False,
            }]
            RC.save_registry(RC.registry_path("issue-1", root), entries)
            with contextlib.redirect_stdout(io.StringIO()):
                code = RC.main([
                    "--root", str(root),
                    "--abandon", "constellation/issue-1/g1/reviewer/attempt-1",
                    "--parent", "test-parent",
                ])
            self.assertEqual(0, code)


class ParentOptionalForRecoveryVerbsTests(unittest.TestCase):
    """F2 (deficiency cleanup batch A+B, review-adjudicated): B2's AST
    patches added `--parent` to `--resume`/`--verify-result` test calls
    that construct no `CrewSpec` and never needed it -- exactly why B2 put
    the requirement at `CrewSpec.__post_init__` rather than a blanket
    argparse `required=True`. The reviewer verified by hand that these
    three paths still work with no `--parent`; this class is the missing
    proof, mirroring `MandatoryModelTests`'s existing
    `test_resume_needs_no_model_at_all` / `test_bare_abandon_needs_no_model_
    at_all` pattern for the same reason: it is what would catch someone
    later "tidying" the enforcement up into argparse and silently breaking
    all three."""

    def test_resume_succeeds_with_no_parent(self):
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
            }]  # deliberately no "parent" key
            RC.save_registry(RC.registry_path("issue-1", root), entries)
            with fake_launch(RC, 0, write_result_at=root / result):
                with contextlib.redirect_stdout(io.StringIO()):
                    code = RC.main(["--root", str(root), "--resume", session])
            self.assertEqual(0, code)
            self.assertEqual(
                "completed", RC.load_registry(RC.registry_path("issue-1", root))[0]["status"]
            )

    def test_bare_abandon_succeeds_with_no_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entries = [{
                "session_name": "constellation/issue-1/g1/reviewer/attempt-1",
                "crew_id": "constellation/issue-1/g1/reviewer/attempt-1",
                "work_id": "issue-1", "gate": "g1", "role": "reviewer", "attempt": 1,
                "worktree": ".", "status": "running", "abandoned": False,
            }]  # deliberately no "parent" key
            RC.save_registry(RC.registry_path("issue-1", root), entries)
            with contextlib.redirect_stdout(io.StringIO()):
                code = RC.main([
                    "--root", str(root),
                    "--abandon", "constellation/issue-1/g1/reviewer/attempt-1",
                ])
            self.assertEqual(0, code)
            entry = RC.load_registry(RC.registry_path("issue-1", root))[0]
            self.assertTrue(entry["abandoned"])

    def test_verify_result_succeeds_with_no_parent(self):
        # `ExternalBackend.verify` reads the stored entry directly -- no
        # `CrewSpec` is built on the verify path either. Uses the
        # `--accept-mtime-only-risk` escape hatch (#432) rather than a
        # spine, so no dispatch of any kind (which WOULD need --parent) is
        # needed to set the fixture up.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = result_rel("issue-1", "g1", "implementer")
            session = "constellation/issue-1/g1/implementer/attempt-1"
            entries = [{
                "session_name": session, "crew_id": session,
                "work_id": "issue-1", "gate": "g1", "role": "implementer", "attempt": 1,
                "worktree": ".", "status": "running", "abandoned": False,
                "dispatch": "external", "pid": None,
                "result": result, "started_at": RC._now(),
            }]  # deliberately no "parent" key
            RC.save_registry(RC.registry_path("issue-1", root), entries)
            (root / result).parent.mkdir(parents=True, exist_ok=True)
            (root / result).write_text("RESULT\n", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                code = RC.main([
                    "--root", str(root), "--verify-result", session,
                    "--accept-mtime-only-risk", "no spine on this dispatch, result alone accepted",
                ])
            self.assertEqual(0, code)
            self.assertEqual(
                "completed", RC.load_registry(RC.registry_path("issue-1", root))[0]["status"]
            )


class ResolveModelTests(unittest.TestCase):
    """g2-implement (#633): `resolve_model`'s five branches, pure, by direct
    import -- no argv, no subprocess, no filesystem. `ROLE_MODEL_TIERS` and
    `resolve_model` are additive-only this gate: nothing in `run_crew.py`
    calls either yet (that wiring is g3), so every case here constructs its
    own inputs and calls the function directly."""

    CLAUDE_ROLES = (
        "commander", "commander-delegated", "implementer", "reviewer", "critic", "cartographer",
    )

    def test_every_populated_claude_role_resolves_to_its_own_default(self):
        for role in self.CLAUDE_ROLES:
            resolved = RC.resolve_model(role, "claude", None, None)
            self.assertEqual("sonnet", resolved.model)
            self.assertIsNone(resolved.reason)
        resolved = RC.resolve_model("admiral", "claude", None, None)
        self.assertEqual("opus", resolved.model)
        self.assertIsNone(resolved.reason)

    def test_blank_string_requested_also_resolves_to_default(self):
        resolved = RC.resolve_model("implementer", "claude", "", None)
        self.assertEqual("sonnet", resolved.model)
        self.assertIsNone(resolved.reason)

    def test_out_of_set_model_is_refused_by_name(self):
        with self.assertRaises(RC.CrewLaunchError) as ctx:
            RC.resolve_model("implementer", "claude", "gpt-5", None)
        message = str(ctx.exception)
        self.assertIn("gpt-5", message)
        self.assertIn("implementer", message)
        self.assertIn("sonnet", message)
        self.assertIn("haiku", message)

    def test_codex_harness_refuses_by_name_branch_one(self):
        with self.assertRaises(RC.CrewLaunchError) as ctx:
            RC.resolve_model("implementer", "codex", None, None)
        message = str(ctx.exception)
        self.assertIn("implementer", message)
        self.assertIn("codex", message)

    def test_local_harness_refuses_by_name_branch_one(self):
        with self.assertRaises(RC.CrewLaunchError) as ctx:
            RC.resolve_model("implementer", "local", None, None)
        message = str(ctx.exception)
        self.assertIn("implementer", message)
        self.assertIn("local", message)

    def test_unknown_role_under_known_harness_refuses_by_name_branch_one(self):
        with self.assertRaises(RC.CrewLaunchError) as ctx:
            RC.resolve_model("scout", "claude", None, None)
        message = str(ctx.exception)
        self.assertIn("scout", message)
        self.assertIn("claude", message)

    def test_non_default_in_set_choice_with_no_reason_is_refused(self):
        with self.assertRaises(RC.CrewLaunchError) as ctx:
            RC.resolve_model("implementer", "claude", "haiku", None)
        message = str(ctx.exception)
        self.assertIn("haiku", message)
        self.assertIn("implementer", message)
        self.assertIn("sonnet", message)  # names the default it would override
        self.assertIn("reason", message)

    def test_non_default_in_set_choice_with_reason_succeeds_and_carries_reason(self):
        resolved = RC.resolve_model(
            "implementer", "claude", "haiku", "cheap smoke-test lane"
        )
        self.assertEqual("haiku", resolved.model)
        self.assertEqual("cheap smoke-test lane", resolved.reason)

    def test_default_tier_explicit_choice_never_requires_a_reason(self):
        resolved = RC.resolve_model("implementer", "claude", "sonnet", None)
        self.assertEqual("sonnet", resolved.model)
        self.assertIsNone(resolved.reason)

    def test_default_tier_explicit_choice_passes_reason_through_if_given(self):
        """A reason is never REQUIRED for a default-tier explicit choice, but
        one given anyway is not discarded either."""
        resolved = RC.resolve_model("implementer", "claude", "sonnet", "why not")
        self.assertEqual("sonnet", resolved.model)
        self.assertEqual("why not", resolved.reason)

    def test_resolved_model_is_a_frozen_dataclass(self):
        resolved = RC.resolve_model("implementer", "claude", None, None)
        with self.assertRaises(Exception):
            resolved.model = "haiku"

    def test_role_model_tiers_allowed_values_are_frozenset(self):
        self.assertIsInstance(
            RC.ROLE_MODEL_TIERS["claude"]["implementer"]["allowed"], frozenset
        )

    def test_codex_and_local_harnesses_are_declared_empty(self):
        self.assertEqual({}, RC.ROLE_MODEL_TIERS["codex"])
        self.assertEqual({}, RC.ROLE_MODEL_TIERS["local"])

    def test_commander_tier_is_sonnet_or_opus_haiku_excluded(self):
        """#567 lane L, human ruling verbatim: 'commander should be sonnet or
        opus allowed, haiku can't handle it.' Upward-only change from the
        original {sonnet, haiku}: default stays sonnet, opus is added, haiku
        is removed. Every other row (including admiral's opus-only row) is
        untouched by this gate."""
        self.assertEqual(
            {"default": "sonnet", "allowed": frozenset({"sonnet", "opus"})},
            RC.ROLE_MODEL_TIERS["claude"]["commander"],
        )
        resolved = RC.resolve_model("commander", "claude", "opus", "epic-567 ruling")
        self.assertEqual("opus", resolved.model)
        with self.assertRaises(RC.CrewLaunchError) as ctx:
            RC.resolve_model("commander", "claude", "haiku", None)
        self.assertIn("haiku", str(ctx.exception))


class EntryLivenessTests(unittest.TestCase):
    """Issue #599: `entry_liveness`'s corroborated three-state rule, and its
    wiring into `active_duplicate` so a corroborated-dead entry stops
    blocking a fresh launch while an uncorroborated one still blocks
    (fail-toward-active). The two `active_duplicate` cases per direction (1-4
    below) are this gate's load-bearing evidence."""

    def _cli_entry(self, pid):
        return {
            "session_name": "constellation/issue-1/g1/reviewer/attempt-1",
            "crew_id": "constellation/issue-1/g1/reviewer/attempt-1",
            "work_id": "issue-1", "gate": "g1", "role": "reviewer", "attempt": 1,
            "worktree": ".", "status": "running", "abandoned": False,
            "backend": "cli", "pid": pid,
        }

    def _external_phantom_entry(self, started_at):
        """Shaped exactly like the real archived phantom entry
        `constellation/epic-568-441/g1/implementer/attempt-1` in
        `.agent-work/archive/2026-08-15-epic-568-441/crew-runs.json` (pid null,
        backend external, last_heartbeat == started_at) -- status forced to
        `running` here (the archive already shows it `abandoned`, which this
        test does not exercise) so the duplicate-guard path is live."""
        return {
            "crew_id": "constellation/epic-568-441/g1/implementer/attempt-1",
            "work_id": "epic-568-441",
            "gate": "g1",
            "role": "implementer",
            "attempt": 1,
            "status": "running",
            "session_name": "constellation/epic-568-441/g1/implementer/attempt-1",
            "backend": "external",
            "pid": None,
            "worktree": "/home/tommy/projects/constellation-skills/.worktrees/epic-568-441",
            "handoff": ".agent-work/epic-568-441/crew-handoffs/g1-implementer-handoff.md",
            "result": ".agent-work/epic-568-441/crew-handoffs/g1-implementer-result.md",
            "spine": None,
            "parent": "constellation/epic-568-441",
            "stdout": ".agent-work/epic-568-441/crew-runs/g1-implementer-attempt-1.stdout.txt",
            "stderr": ".agent-work/epic-568-441/crew-runs/g1-implementer-attempt-1.stderr.txt",
            "started_at": started_at,
            "last_heartbeat": started_at,
            "completed_at": None,
            "abandoned": False,
            "dispatch": "external",
            "model": "gpt-5.6-sol",
        }

    # -- entry_liveness bucket unit tests -------------------------------- #

    def test_liveness_pid_bucket_active_and_stale(self):
        now = datetime(2026, 8, 16, tzinfo=timezone.utc)
        entry = self._cli_entry(pid=12345)
        self.assertEqual("active", RC.entry_liveness(entry, now, alive=lambda pid: True))
        self.assertEqual("stale", RC.entry_liveness(entry, now, alive=lambda pid: False))

    def test_liveness_external_bucket_heartbeat_age(self):
        started_at = "2026-08-14T18:10:25.409092+00:00"
        entry = self._external_phantom_entry(started_at)
        hb = datetime.fromisoformat(started_at)
        within_8h = hb + timedelta(hours=4)
        past_8h = hb + timedelta(hours=9)
        self.assertEqual("active", RC.entry_liveness(entry, within_8h))
        self.assertEqual("stale", RC.entry_liveness(entry, past_8h))

    def test_liveness_external_bucket_falls_back_to_started_at(self):
        started_at = "2026-08-14T18:10:25.409092+00:00"
        entry = self._external_phantom_entry(started_at)
        del entry["last_heartbeat"]
        hb = datetime.fromisoformat(started_at)
        self.assertEqual("stale", RC.entry_liveness(entry, hb + timedelta(hours=9)))

    def test_liveness_external_bucket_unparseable_heartbeat_is_unknown(self):
        entry = self._external_phantom_entry("not-a-timestamp")
        self.assertEqual("unknown", RC.entry_liveness(entry, datetime.now(timezone.utc)))

    def test_liveness_legacy_bucket_no_pid_no_backend_is_unknown_no_heartbeat_lookup(self):
        # Exactly the fixture shape test_duplicate_active_lock_is_refused uses:
        # no pid, no backend/dispatch key -- bucket 3, unknown directly.
        entry = {
            "session_name": "constellation/issue-1/g1/reviewer/attempt-1",
            "crew_id": "constellation/issue-1/g1/reviewer/attempt-1",
            "work_id": "issue-1", "gate": "g1", "role": "reviewer", "attempt": 1,
            "worktree": ".", "status": "running", "abandoned": False,
        }
        self.assertEqual("unknown", RC.entry_liveness(entry, datetime.now(timezone.utc)))

    # -- active_duplicate wiring: required evidence 1-4 ------------------- #

    def test_evidence_1_cli_dead_pid_frees_the_slot(self):
        entries = [self._cli_entry(pid=99999)]
        dup = RC.active_duplicate(
            entries, "issue-1", "g1", "reviewer", ".", alive=lambda pid: False,
        )
        self.assertIsNone(dup)

    def test_evidence_2_cli_live_pid_still_blocks(self):
        entries = [self._cli_entry(pid=99999)]
        dup = RC.active_duplicate(
            entries, "issue-1", "g1", "reviewer", ".", alive=lambda pid: True,
        )
        self.assertIsNotNone(dup)
        self.assertEqual(entries[0], dup)

    def test_evidence_3_external_phantom_past_8h_frees_the_slot(self):
        started_at = "2026-08-14T18:10:25.409092+00:00"
        entry = self._external_phantom_entry(started_at)
        entries = [entry]
        now = datetime.fromisoformat(started_at) + timedelta(hours=9)
        dup = RC.active_duplicate(
            entries, "epic-568-441", "g1", "implementer",
            entry["worktree"], now=now,
        )
        self.assertIsNone(dup)

    def test_evidence_4_external_within_8h_still_blocks(self):
        started_at = "2026-08-14T18:10:25.409092+00:00"
        entry = self._external_phantom_entry(started_at)
        entries = [entry]
        now = datetime.fromisoformat(started_at) + timedelta(hours=4)
        dup = RC.active_duplicate(
            entries, "epic-568-441", "g1", "implementer",
            entry["worktree"], now=now,
        )
        self.assertIsNotNone(dup)
        self.assertEqual(entry, dup)


class ParentCliTests(unittest.TestCase):
    """`--parent` end to end through the CLI. B2 (deficiency cleanup batch
    A+B) made it REQUIRED for a fresh or relaunched dispatch -- a dispatch
    with none is refused at construction, naming what to pass. An
    abandon+relaunch that inherits a real parent already stored on the
    original entry needs no --parent reasserted."""

    def test_fresh_launch_with_parent_records_it_in_the_registry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "reviewer")
            result = result_rel("issue-1", "g1", "reviewer")
            with fake_launch(RC, 0, write_result_at=root / result):
                code = RC.main([
                    "--root", str(root), "--work-id", "issue-1", "--gate", "g1",
                    "--role", "reviewer", "--handoff", handoff, "--result", result,
                    "--parent", "constellation/epic-1/commander", "--model", "sonnet",
                ])
            self.assertEqual(0, code)
            reg = RC.load_registry(RC.registry_path("issue-1", root))
            self.assertEqual("constellation/epic-1/commander", reg[0]["parent"])

    def test_fresh_launch_with_no_parent_is_refused_naming_what_to_pass(self):
        # B2 (deficiency cleanup batch A+B) reverses this test's old premise:
        # a fresh dispatch with no --parent used to work silently (recording
        # `parent: null`, 373 of 545 registry entries in the wild); it is
        # now refused, at CrewSpec construction, with a message naming
        # exactly what to pass.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "reviewer")
            result = result_rel("issue-1", "g1", "reviewer")
            with fake_launch(RC, 0, write_result_at=root / result):
                with contextlib.redirect_stderr(io.StringIO()) as err:
                    code = RC.main([
                        "--root", str(root), "--work-id", "issue-1", "--gate", "g1",
                        "--role", "reviewer", "--handoff", handoff, "--result", result,
                        "--model", "sonnet",
                    ])
            self.assertEqual(1, code)
            self.assertIn("a crew needs a parent", err.getvalue())
            self.assertIn("--parent", err.getvalue())
            # refused before any registry write, before any process spawn
            self.assertEqual([], RC.load_registry(RC.registry_path("issue-1", root)))

    def test_abandon_relaunch_inherits_stored_parent_when_not_reasserted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "reviewer")
            result = result_rel("issue-1", "g1", "reviewer")
            entries = [{
                "session_name": "constellation/issue-1/g1/reviewer/attempt-1",
                "crew_id": "constellation/issue-1/g1/reviewer/attempt-1",
                "work_id": "issue-1", "gate": "g1", "role": "reviewer", "attempt": 1,
                "worktree": ".", "status": "running", "abandoned": False,
                "handoff": handoff, "result": result, "parent": "constellation/epic-1/commander",
            }]
            RC.save_registry(RC.registry_path("issue-1", root), entries)
            with fake_launch(RC, 0, write_result_at=root / result):
                with contextlib.redirect_stdout(io.StringIO()):
                    # NO --parent on the relaunch itself -- B2 (deficiency
                    # cleanup batch A+B) makes --parent required for a
                    # dispatch, but the abandon+relaunch path is not "a
                    # dispatch with no parent": `parent = args.parent or
                    # abandoned.get("parent")` inherits the STORED entry's
                    # parent, which is real here, so CrewSpec's requirement
                    # is satisfied without reasserting it. This is exactly
                    # the case this test is named for.
                    code = RC.main([
                        "--root", str(root),
                        "--abandon", "constellation/issue-1/g1/reviewer/attempt-1",
                        "--relaunch", "--handoff", handoff, "--result", result,
                        "--model", "sonnet",
                    ])
            self.assertEqual(0, code)
            reg = RC.load_registry(RC.registry_path("issue-1", root))
            by_name = {e["session_name"]: e for e in reg}
            self.assertEqual(
                "constellation/epic-1/commander",
                by_name["constellation/issue-1/g1/reviewer/attempt-2"]["parent"],
            )

    def test_abandon_relaunch_inherits_stored_reasoning_effort_when_not_reasserted(self):
        """Recovery keeps metadata AND forwards it as the launcher's real
        `--effort` flag (decision:reasoning-effort-follows-tier) -- the inherited
        value is not just recorded, it is also what the relaunched child receives."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "reviewer")
            result = result_rel("issue-1", "g1", "reviewer")
            entries = [{
                "session_name": "constellation/issue-1/g1/reviewer/attempt-1",
                "crew_id": "constellation/issue-1/g1/reviewer/attempt-1",
                "work_id": "issue-1", "gate": "g1", "role": "reviewer", "attempt": 1,
                "worktree": ".", "status": "running", "abandoned": False,
                "handoff": handoff, "result": result, "reasoning_effort": "high",
            }]
            RC.save_registry(RC.registry_path("issue-1", root), entries)
            with fake_launch(RC, 0, write_result_at=root / result) as calls:
                with contextlib.redirect_stdout(io.StringIO()):
                    code = RC.main([
                        "--root", str(root),
                        "--abandon", "constellation/issue-1/g1/reviewer/attempt-1",
                        "--relaunch", "--handoff", handoff, "--result", result,
                        "--model", "sonnet",
                        "--parent", "test-parent",
                    ])
            self.assertEqual(0, code)
            relaunched = RC.load_registry(RC.registry_path("issue-1", root))[1]
            self.assertEqual("high", relaunched["reasoning_effort"])
            argv = calls[0]["argv"]
            self.assertIn("--effort", argv)
            self.assertEqual("high", argv[argv.index("--effort") + 1])

    def test_abandon_relaunch_legacy_registry_without_reasoning_effort_stays_compatible(self):
        """The optional field is read on relaunch, so an older record may omit it."""
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
                        "--model", "sonnet",
                        "--parent", "test-parent",
                    ])
            self.assertEqual(0, code)
            relaunched = RC.load_registry(RC.registry_path("issue-1", root))[1]
            self.assertNotIn("reasoning_effort", relaunched)


class CrewEnvSpineBindingTests(unittest.TestCase):
    """CONTROL A, made green: `crew_env()` must bind SPINE_FILE/SPINE_SESSION to
    the crew it is actually building an environment FOR, not silently omit them
    or leak whatever spine this (dispatching) process happens to carry."""

    def test_no_binding_requested_sets_neither_var(self):
        env = RC.crew_env({"PATH": "/usr/bin"})
        self.assertNotIn("SPINE_FILE", env)
        self.assertNotIn("SPINE_SESSION", env)

    def test_binds_spine_file_and_session_when_given(self):
        env = RC.crew_env(
            {"PATH": "/usr/bin"},
            spine_file="/abs/work/PLAN.json",
            spine_session="constellation/issue-1/g1/reviewer",
        )
        self.assertEqual("/abs/work/PLAN.json", env["SPINE_FILE"])
        self.assertEqual("constellation/issue-1/g1/reviewer", env["SPINE_SESSION"])

    def test_explicit_derived_binding_wins_over_inherited_caller_value(self):
        # ASSIGN semantics (Admiral ruling, reversing the earlier setdefault
        # ruling that froze this defect in place): an explicit spine_file/
        # spine_session argument is MORE SPECIFIC than whatever SPINE_FILE/
        # SPINE_SESSION already sits in the base environment, so it must win —
        # a door-bound dispatcher's own binding must never leak to a child it is
        # launching with its own explicit spine.
        base = {"SPINE_FILE": "/caller/own.json", "SPINE_SESSION": "constellation/caller/own"}
        env = RC.crew_env(
            base, spine_file="/derived/child.json", spine_session="constellation/child/derived",
        )
        self.assertEqual("/derived/child.json", env["SPINE_FILE"])
        self.assertEqual("constellation/child/derived", env["SPINE_SESSION"])

    def test_default_base_env_would_leak_parents_own_spine_without_a_binding(self):
        # Demonstrates the RAW defect `crew_env()` used to have with no binding
        # params at all: base_env defaults to dict(os.environ), so a dispatching
        # process that already has ITS OWN SPINE_FILE/SPINE_SESSION bound (e.g.
        # this very implementer) hands that SAME spine to every child it
        # dispatches, regardless of the child's own work_id/gate/role — UNLESS
        # the caller supplies the child's own binding explicitly.
        old = dict(os.environ)
        try:
            os.environ["SPINE_FILE"] = "/parent/own.json"
            os.environ["SPINE_SESSION"] = "constellation/parent/own"
            env_with_no_binding = RC.crew_env()
            self.assertEqual("/parent/own.json", env_with_no_binding["SPINE_FILE"])
            # A caller that DOES supply the child's real binding overrides this —
            # this is the actual fix: an explicit binding is assigned over the
            # parent's own inherited environment, not merely setdefault-ed.
            env_with_binding = RC.crew_env(
                spine_file="/child/own.json", spine_session="constellation/child/own",
            )
            self.assertEqual("/child/own.json", env_with_binding["SPINE_FILE"])
            self.assertEqual("constellation/child/own", env_with_binding["SPINE_SESSION"])
        finally:
            os.environ.clear()
            os.environ.update(old)


class DispatchDoorBindingTests(unittest.TestCase):
    """A crew dispatched (or resumed) through `launch_crew`/`resume_crew` gets a
    door bound to its OWN spine and an assignment-keyed SPINE_SESSION, not the
    dispatcher's leftover environment."""

    def test_fresh_dispatch_binds_own_spine_and_assignment_session(self):
        with no_ambient_spine_env(), tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "implementer")
            result = result_rel("issue-1", "g1", "implementer")
            spine_rel = ".agent-work/issue-1/IMPLEMENTER_PLAN.json"
            with fake_launch(RC, 0, write_result_at=root / result) as calls:
                RC.launch_crew(
                    work_id="issue-1", gate="g1", role="implementer",
                    handoff=handoff, result=result, spine=spine_rel,
                    worktree=".", model="sonnet", launcher="claude", attempt=1,
                    root=root, entries=[],
                    parent="test-parent",
                )
            env = calls[0]["env"]
            self.assertEqual(str(root / spine_rel), env["SPINE_FILE"])
            self.assertEqual("constellation/issue-1/g1/implementer", env["SPINE_SESSION"])
            # attempt tail must NOT be in the lease identity
            self.assertNotIn("attempt", env["SPINE_SESSION"])

    def test_dispatch_without_spine_binds_neither_var(self):
        # A caller with nothing to bind (e.g. a legacy call site not yet updated
        # to pass --spine) must not crash. Both SPINE_FILE and SPINE_SESSION are
        # bound only as a PAIR: deriving the assignment identity without the file
        # it belongs to hands the child a lease with nothing telling it which
        # spine to claim it against (the bootstrap-mismatch the Admiral ruled
        # against) — see `test_dispatch_without_spine_leaves_ambient_pair_untouched`.
        with no_ambient_spine_env(), tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "implementer")
            result = result_rel("issue-1", "g1", "implementer")
            with fake_launch(RC, 0, write_result_at=root / result) as calls:
                RC.launch_crew(
                    work_id="issue-1", gate="g1", role="implementer",
                    handoff=handoff, result=result,
                    worktree=".", model="sonnet", launcher="claude", attempt=1,
                    root=root, entries=[],
                    parent="test-parent",
                )
            env = calls[0]["env"]
            self.assertNotIn("SPINE_FILE", env)
            self.assertNotIn("SPINE_SESSION", env)

    def test_dispatch_explicit_spine_overrides_ambient_dispatcher_binding(self):
        # Reverses the earlier "RULED design" here: a cold reviewer showed that
        # letting a SPINE_FILE/SPINE_SESSION already present in the dispatching
        # process's own environment win over an explicit --spine is a silent
        # hijack — a door-bound dispatcher's child claims the DISPATCHER's own
        # lease instead of the one it was explicitly told to drive, because
        # `claim` matches on string equality and the refuse-or-force-with-reason
        # construct never sees a conflicting identity. The Admiral's bootstrap
        # (exporting env, passing NO --spine) is unaffected: that path never
        # reaches this branch, since spine_file stays None there. Covered at the
        # crew_env() level by CrewEnvSpineBindingTests; this confirms the SAME
        # contract survives through the full launch_crew() dispatch path.
        with tempfile.TemporaryDirectory() as tmp:
            saved = {k: os.environ.pop(k, None) for k in ("SPINE_FILE", "SPINE_SESSION")}
            try:
                os.environ["SPINE_FILE"] = "/explicit/caller-bound.json"
                os.environ["SPINE_SESSION"] = "constellation/caller-work/g9/implementer"
                root = Path(tmp)
                handoff = write_handoff(root, "child-work", "g1", "reviewer")
                result = result_rel("child-work", "g1", "reviewer")
                spine_rel = ".agent-work/child-work/REVIEW_SURVEY.json"
                with fake_launch(RC, 0, write_result_at=root / result) as calls:
                    RC.launch_crew(
                        work_id="child-work", gate="g1", role="reviewer",
                        handoff=handoff, result=result, spine=spine_rel,
                        worktree=".", model="sonnet", launcher="claude", attempt=1,
                        root=root, entries=[],
                        parent="test-parent",
                    )
                env = calls[0]["env"]
                self.assertEqual(str(root / spine_rel), env["SPINE_FILE"])
                self.assertEqual("constellation/child-work/g1/reviewer", env["SPINE_SESSION"])
                # the ambient/dispatcher binding must not leak through at all
                self.assertNotEqual("/explicit/caller-bound.json", env["SPINE_FILE"])
                self.assertNotEqual("constellation/caller-work/g9/implementer", env["SPINE_SESSION"])
            finally:
                for k, v in saved.items():
                    if v is None:
                        os.environ.pop(k, None)
                    else:
                        os.environ[k] = v

    def test_dispatch_without_spine_leaves_ambient_pair_untouched(self):
        # CONTROL: a dispatcher that is ITSELF door-bound (ambient SPINE_FILE +
        # SPINE_SESSION already in this process's environment, e.g. a live
        # Admiral/Commander crew) launches a child with NO --spine. "No --spine
        # means the inherited environment route is genuinely untouched" requires
        # BOTH values to pass through unmodified as a PAIR — binding only
        # SPINE_SESSION (deriving the child's own assignment identity) while
        # SPINE_FILE still points at the dispatcher's spine hands the child a
        # mismatched pair: the dispatcher's checklist file with the child's own
        # identity, which claims a lease on a spine nothing prepared it to drive.
        with tempfile.TemporaryDirectory() as tmp:
            saved = {k: os.environ.pop(k, None) for k in ("SPINE_FILE", "SPINE_SESSION")}
            try:
                os.environ["SPINE_FILE"] = "/admiral/EPIC_SPINE.json"
                os.environ["SPINE_SESSION"] = "constellation/epic/admiral"
                root = Path(tmp)
                handoff = write_handoff(root, "issue-1", "g1", "implementer")
                result = result_rel("issue-1", "g1", "implementer")
                with fake_launch(RC, 0, write_result_at=root / result) as calls:
                    RC.launch_crew(
                        work_id="issue-1", gate="g1", role="implementer",
                        handoff=handoff, result=result,
                        worktree=".", model="sonnet", launcher="claude", attempt=1,
                        root=root, entries=[],
                        parent="test-parent",
                    )
                env = calls[0]["env"]
                self.assertEqual("/admiral/EPIC_SPINE.json", env["SPINE_FILE"])
                self.assertEqual("constellation/epic/admiral", env["SPINE_SESSION"])
            finally:
                for k, v in saved.items():
                    if v is None:
                        os.environ.pop(k, None)
                    else:
                        os.environ[k] = v

    def test_resume_rebinds_door_to_the_stored_spine(self):
        with no_ambient_spine_env(), tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "implementer")
            result = result_rel("issue-1", "g1", "implementer")
            session = "constellation/issue-1/g1/implementer/attempt-1"
            spine_rel = ".agent-work/issue-1/IMPLEMENTER_PLAN.json"
            stdout, stderr = RC.run_log_paths("issue-1", "g1", "implementer", 1, root)
            entries = [{
                "session_name": session, "crew_id": session,
                "work_id": "issue-1", "gate": "g1", "role": "implementer", "attempt": 1,
                "worktree": ".", "status": "running", "abandoned": False,
                "handoff": handoff, "result": result, "spine": spine_rel,
                "stdout": RC._relativize(str(stdout), root),
                "stderr": RC._relativize(str(stderr), root),
            }]
            RC.save_registry(RC.registry_path("issue-1", root), entries)
            with fake_launch(RC, 0, write_result_at=root / result) as calls:
                RC.resume_crew(session=session, root=root, entries=entries)
            env = calls[0]["env"]
            self.assertEqual(str(root / spine_rel), env["SPINE_FILE"])
            self.assertEqual("constellation/issue-1/g1/implementer", env["SPINE_SESSION"])

    def test_resume_of_legacy_entry_without_spine_key_does_not_crash(self):
        # An entry recorded before this field existed has no "spine" key at all
        # (not even None) — resume must degrade gracefully, not KeyError.
        with no_ambient_spine_env(), tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
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
            with fake_launch(RC, 0, write_result_at=root / result) as calls:
                RC.resume_crew(session=session, root=root, entries=entries)
            env = calls[0]["env"]
            self.assertNotIn("SPINE_FILE", env)
            self.assertNotIn("SPINE_SESSION", env)


class ParentEnvBindingTests(unittest.TestCase):
    """`crew_env()`'s own contract for SPINE_PARENT: bound when given, left
    untouched when not (the plain-optional half of the contract; the
    "always resolve to a definite value" half lives one level up, in
    `_crew_door_env`, covered by `ParentDoorBindingTests` below)."""

    def test_no_parent_requested_leaves_spine_parent_unset(self):
        env = RC.crew_env({"PATH": "/usr/bin"})
        self.assertNotIn("SPINE_PARENT", env)

    def test_binds_spine_parent_when_given(self):
        env = RC.crew_env({"PATH": "/usr/bin"}, parent="constellation/epic-1/commander")
        self.assertEqual("constellation/epic-1/commander", env["SPINE_PARENT"])


class ParentDoorBindingTests(unittest.TestCase):
    """A crew dispatched (or resumed) through `launch_crew`/`resume_crew` gets
    a definitive SPINE_PARENT -- the given `--parent`, or plainly
    `UNKNOWN_PARENT` -- never the ambient value of whatever parent the
    DISPATCHING process itself happens to carry (that would silently name
    the wrong rung: the dispatcher's own parent, not the dispatcher)."""

    def test_fresh_dispatch_binds_given_parent(self):
        with no_ambient_parent_env(), tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "implementer")
            result = result_rel("issue-1", "g1", "implementer")
            with fake_launch(RC, 0, write_result_at=root / result) as calls:
                RC.launch_crew(
                    work_id="issue-1", gate="g1", role="implementer",
                    handoff=handoff, result=result, parent="constellation/epic-1/commander",
                    worktree=".", model="sonnet", launcher="claude", attempt=1,
                    root=root, entries=[],
                )
            env = calls[0]["env"]
            self.assertEqual("constellation/epic-1/commander", env["SPINE_PARENT"])
            self.assertIn("constellation/epic-1/commander", calls[0]["argv"][2])

    def test_fresh_dispatch_with_no_parent_is_refused_never_reads_ambient(self):
        # B2 (deficiency cleanup batch A+B) reverses this test's old premise:
        # `launch_crew` with no `parent` used to bind `UNKNOWN_PARENT` and
        # succeed; it is now refused at `CrewSpec.__post_init__`, before any
        # process is spawned. What survives from the original test is the
        # DEEPER guarantee it was written to prove: the ambient SPINE_PARENT
        # in THIS process's own environment is never silently read as the
        # crew's parent -- there being no fallback path left to reach it at
        # all is a stronger version of that guarantee, not a weaker one.
        with tempfile.TemporaryDirectory() as tmp:
            saved = os.environ.pop("SPINE_PARENT", None)
            try:
                os.environ["SPINE_PARENT"] = "constellation/some-other/dispatcher"
                root = Path(tmp)
                handoff = write_handoff(root, "issue-1", "g1", "implementer")
                result = result_rel("issue-1", "g1", "implementer")
                with fake_launch(RC, 0, write_result_at=root / result) as calls:
                    with self.assertRaises(RC.CrewLaunchError) as ctx:
                        RC.launch_crew(
                            work_id="issue-1", gate="g1", role="implementer",
                            handoff=handoff, result=result,
                            worktree=".", model="sonnet", launcher="claude", attempt=1,
                            root=root, entries=[],
                        )
                self.assertIn("a crew needs a parent", str(ctx.exception))
                self.assertEqual([], calls, "must refuse before any process is spawned")
            finally:
                if saved is None:
                    os.environ.pop("SPINE_PARENT", None)
                else:
                    os.environ["SPINE_PARENT"] = saved

    def test_resume_rebinds_the_stored_parent(self):
        with no_ambient_parent_env(), tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "implementer")
            result = result_rel("issue-1", "g1", "implementer")
            session = "constellation/issue-1/g1/implementer/attempt-1"
            stdout, stderr = RC.run_log_paths("issue-1", "g1", "implementer", 1, root)
            entries = [{
                "session_name": session, "crew_id": session,
                "work_id": "issue-1", "gate": "g1", "role": "implementer", "attempt": 1,
                "worktree": ".", "status": "running", "abandoned": False,
                "handoff": handoff, "result": result, "parent": "constellation/epic-1/commander",
                "stdout": RC._relativize(str(stdout), root),
                "stderr": RC._relativize(str(stderr), root),
            }]
            RC.save_registry(RC.registry_path("issue-1", root), entries)
            with fake_launch(RC, 0, write_result_at=root / result) as calls:
                RC.resume_crew(session=session, root=root, entries=entries)
            env = calls[0]["env"]
            self.assertEqual("constellation/epic-1/commander", env["SPINE_PARENT"])
            self.assertIn("constellation/epic-1/commander", calls[0]["argv"][2])

    def test_resume_of_legacy_entry_without_parent_key_says_unknown(self):
        # An entry recorded before this field existed has no "parent" key at
        # all (not even None) -- resume must degrade to UNKNOWN_PARENT, not
        # KeyError and not a leaked ambient value.
        with no_ambient_parent_env(), tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
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
            with fake_launch(RC, 0, write_result_at=root / result) as calls:
                RC.resume_crew(session=session, root=root, entries=entries)
            env = calls[0]["env"]
            self.assertEqual(RC.UNKNOWN_PARENT, env["SPINE_PARENT"])


class SpineOnlyDispatchTests(unittest.TestCase):
    """Issue #559: `--handoff` becomes optional -- a crew with a bound `--spine`
    and no `--handoff` is a legal dispatch on the cli backend, refused only when
    NEITHER is given. The external backend keeps requiring a handoff (it cannot
    bind a spine, so a spine-only dispatch there would leave the crew with no
    job at all)."""

    def test_cli_backend_spine_only_dispatch_records_null_handoff(self):
        with no_ambient_spine_env(), tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = result_rel("issue-1", "g1", "implementer")
            spine_rel = ".agent-work/issue-1/IMPLEMENTER_PLAN.json"
            (root / spine_rel).parent.mkdir(parents=True, exist_ok=True)
            (root / spine_rel).write_text("{}", encoding="utf-8")
            with fake_launch(RC, 0, write_result_at=root / result) as calls:
                exit_code, entry = RC.launch_crew(
                    work_id="issue-1", gate="g1", role="implementer",
                    handoff=None, result=result, spine=spine_rel,
                    worktree=".", model="sonnet", launcher="claude", attempt=1,
                    root=root, entries=[],
                    parent="test-parent",
                )
            self.assertEqual(0, exit_code)
            self.assertIsNone(entry["handoff"])
            reg = RC.load_registry(RC.registry_path("issue-1", root))
            self.assertIsNone(reg[0]["handoff"])
            prompt = calls[0]["argv"][2]
            self.assertIn("spine_status", prompt)
            self.assertNotIn(spine_rel, prompt)

    def test_cli_backend_neither_handoff_nor_spine_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = result_rel("issue-1", "g1", "implementer")
            with self.assertRaises(RC.CrewLaunchError):
                RC.launch_crew(
                    work_id="issue-1", gate="g1", role="implementer",
                    handoff=None, result=result, spine=None,
                    worktree=".", model="sonnet", launcher="claude", attempt=1,
                    root=root, entries=[],
                    parent="test-parent",
                )

    def test_main_cli_neither_handoff_nor_spine_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = result_rel("issue-1", "g1", "implementer")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                code = RC.main([
                    "--root", str(root), "--work-id", "issue-1", "--gate", "g1",
                    "--role", "implementer", "--result", result,
                    "--parent", "test-parent",
                ])
            self.assertEqual(1, code)
            self.assertIn("REFUSED", stderr.getvalue())
            self.assertEqual([], RC.load_registry(RC.registry_path("issue-1", root)))

    def test_main_cli_spine_only_dispatch_with_result_still_succeeds(self):
        # `--result` and `--spine` may both be given (existing behavior, kept
        # byte-identical): completion is judged on the result artifact, exactly
        # as before spine-only dispatch existed at all.
        with no_ambient_spine_env(), tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = result_rel("issue-1", "g1", "implementer")
            spine_rel = ".agent-work/issue-1/IMPLEMENTER_PLAN.json"
            (root / spine_rel).parent.mkdir(parents=True, exist_ok=True)
            (root / spine_rel).write_text("{}", encoding="utf-8")
            with fake_launch(RC, 0, write_result_at=root / result):
                with contextlib.redirect_stdout(io.StringIO()):
                    code = RC.main([
                        "--root", str(root), "--work-id", "issue-1", "--gate", "g1",
                        "--role", "implementer", "--result", result, "--spine", spine_rel,
                        "--model", "sonnet",
                        "--parent", "test-parent",
                    ])
            self.assertEqual(0, code)
            self.assertIsNone(RC.load_registry(RC.registry_path("issue-1", root))[0]["handoff"])

    def test_resume_of_spine_only_entry_does_not_crash_on_null_handoff(self):
        with no_ambient_spine_env(), tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = result_rel("issue-1", "g1", "implementer")
            spine_rel = ".agent-work/issue-1/IMPLEMENTER_PLAN.json"
            (root / spine_rel).parent.mkdir(parents=True, exist_ok=True)
            (root / spine_rel).write_text("{}", encoding="utf-8")
            with fake_launch(RC, 0, write_result_at=root / result):
                RC.launch_crew(
                    work_id="issue-1", gate="g1", role="implementer",
                    handoff=None, result=result, spine=spine_rel,
                    worktree=".", model="sonnet", launcher="claude", attempt=1,
                    root=root, entries=[],
                    parent="test-parent",
                )
            entries = RC.load_registry(RC.registry_path("issue-1", root))
            session = entries[0]["session_name"]
            with fake_launch(RC, 0, write_result_at=root / result) as calls:
                exit_code, entry = RC.resume_crew(session=session, root=root, entries=entries)
            self.assertEqual(0, exit_code)
            self.assertIsNone(entry["handoff"])
            prompt = calls[0]["argv"][2]
            self.assertIn("spine_status", prompt)

    def test_external_backend_refuses_spine_only_with_no_handoff(self):
        # A spine-only dispatch on `external` would leave the crew with no job
        # at all: the backend cannot bind a spine (spawns no process), and now
        # there is also no handoff document to read.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spine_rel = ".agent-work/issue-1/IMPLEMENTER_PLAN.json"
            result = result_rel("issue-1", "g1", "implementer")
            with self.assertRaises(RC.CrewLaunchError):
                RC.record_external_attempt(
                    work_id="issue-1", gate="g1", role="implementer",
                    handoff=None, result=result, spine=spine_rel,
                    worktree=".", model="sonnet", attempt=1, root=root, entries=[],
                    parent="test-parent",
                )


def _write_spine(path: Path, *, done: bool) -> None:
    """A minimal `checklist_engine`-shaped spine with one item, `complete` when
    `done` else `pending` -- just enough for `checklist_engine.active_id` to
    read a real terminal/non-terminal state."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "work_id": "issue-1",
        "type": "gated",
        "items": ["w1"],
        "tasks": {"w1": {"id": "w1", "status": "complete" if done else "pending"}},
    }), encoding="utf-8")


def _write_parked_spine(path: Path) -> None:
    """The spine a crew leaves when it PARKS at the engine's context line: the
    gate it was inside is closed (`advance --why ...`, what the HARD band tells
    it to do) and the rest are still pending. Nothing is `in-progress`."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "work_id": "issue-1",
        "type": "gated",
        "items": ["w1", "w2"],
        "tasks": {
            "w1": {"id": "w1", "status": "complete"},
            "w2": {"id": "w2", "status": "pending"},
        },
    }), encoding="utf-8")


def _write_crashed_spine(path: Path) -> None:
    """The spine a crew leaves when it dies MID-GATE: the gate it was inside is
    still `in-progress`. Same non-terminal, same partly-done shape as a park --
    the in-progress gate is the only thing that tells them apart."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "work_id": "issue-1",
        "type": "gated",
        "items": ["w1", "w2"],
        "tasks": {
            "w1": {"id": "w1", "status": "complete"},
            "w2": {"id": "w2", "status": "in-progress"},
        },
    }), encoding="utf-8")


def _write_blocked_spine(path: Path, *, blocked_id: str = "w1") -> None:
    """A minimal `checklist_engine`-shaped spine with one BLOCKED gate --
    what a real crew's spine looks like right after `spine_halt block`."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "work_id": "issue-1",
        "type": "gated",
        "items": [blocked_id],
        "tasks": {blocked_id: {
            "id": blocked_id, "status": "blocked",
            "status_detail": {
                "blocker": "cannot satisfy check c1",
                "authority_needed": "human",
                "next_action": "ask parent",
            },
        }},
    }), encoding="utf-8")


def _write_survey_spine(path: Path, *, consolidation) -> None:
    """A minimal `checklist_engine`-shaped SURVEY spine (reviewer/interrogator
    shape): every item recorded terminal, `consolidation` set to whatever the
    caller passes (`None` for "no verdict yet")."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "work_id": "issue-1",
        "type": "survey",
        "items": ["i1", "i2"],
        "tasks": {
            "i1": {"id": "i1", "status": "complete", "result": "pass"},
            "i2": {"id": "i2", "status": "complete", "result": "pass"},
        },
        "consolidation": consolidation,
    }), encoding="utf-8")


class SurveyTerminalTests(unittest.TestCase):
    """#559 pass 3, blocker 2: `spine_terminal` answered a survey question
    with `checklist_engine.active_id`, which walks item statuses and never
    looks at `consolidation`. A real reviewer crew's survey had every item
    recorded and NO consolidation, and `run_crew` recorded it `completed` --
    a Commander told the review is done when no verdict exists anywhere, in
    the one role whose entire deliverable IS the verdict."""

    def test_survey_with_every_item_recorded_but_no_consolidation_is_not_terminal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spine_rel = ".agent-work/issue-1/REVIEW_SURVEY.json"
            _write_survey_spine(root / spine_rel, consolidation=None)
            self.assertFalse(RC.spine_terminal(spine_rel, root))

    def test_survey_with_consolidation_recorded_is_terminal(self):
        # Positive control: same spine, ONLY consolidation differs -- proves
        # the check is a real read of `consolidation`, not a tautology that
        # always refuses a survey.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spine_rel = ".agent-work/issue-1/REVIEW_SURVEY.json"
            _write_survey_spine(
                root / spine_rel,
                consolidation={"verdict": "APPROVE", "summary": "both items pass"},
            )
            self.assertTrue(RC.spine_terminal(spine_rel, root))


class MalformedSpineTests(unittest.TestCase):
    """#559 pass 3, blocker 2 (same function, smaller): `spine_terminal`
    returned `True` for `{}` and `{"items": []}`, directly contradicting its
    own docstring -- "a missing/unparseable/malformed spine is never
    terminal". `checklist_engine.active_id` walks `cl.get("items", [])`, so a
    missing/empty `items` list finds no non-terminal item and returns `None`
    -- terminal by vacuity. Missing files and unparseable JSON already
    correctly returned `False` (covered by `SpineOnlyCompletionContractTests`
    above); this pins the valid-JSON-wrong-shape leak specifically."""

    def test_empty_dict_spine_is_not_terminal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spine_rel = ".agent-work/issue-1/EMPTY.json"
            path = root / spine_rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("{}", encoding="utf-8")
            self.assertFalse(RC.spine_terminal(spine_rel, root))

    def test_empty_items_list_spine_is_not_terminal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spine_rel = ".agent-work/issue-1/EMPTY_ITEMS.json"
            path = root / spine_rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"items": []}), encoding="utf-8")
            self.assertFalse(RC.spine_terminal(spine_rel, root))


class SpineOnlyCompletionContractTests(unittest.TestCase):
    """Issue #559 job 2: a spine-only crew (no `--result`) is judged on its
    BOUND SPINE reaching a terminal state, not on a result artifact it was
    never told to write. The reviewer's probe crew drove its spine to done,
    released the lease, exited 0 -- and the launcher recorded it `failed`
    because `--result` was hard-required and nothing wrote it. These tests
    never pass `write_result_at`: the real crew is never told to write a
    result, so a covering test that writes one anyway would pass for a reason
    that does not exist in production."""

    def test_spine_only_success_is_not_recorded_failed(self):
        with no_ambient_spine_env(), tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spine_rel = ".agent-work/issue-1/IMPLEMENTER_PLAN.json"
            _write_spine(root / spine_rel, done=True)
            with fake_launch(RC, 0):
                with contextlib.redirect_stdout(io.StringIO()):
                    code = RC.main([
                        "--root", str(root), "--work-id", "issue-1", "--gate", "g1",
                        "--role", "implementer", "--spine", spine_rel, "--model", "sonnet",
                        "--parent", "test-parent",
                    ])
            self.assertEqual(0, code)
            entry = RC.load_registry(RC.registry_path("issue-1", root))[0]
            self.assertEqual("completed", entry["status"])
            self.assertFalse(entry["result_present"])

    def test_spine_only_dispatch_with_open_gate_is_recorded_failed(self):
        # Same "no result artifact ever written" setup as the success case
        # above -- ONLY the spine's terminal-ness differs. Proves the check is
        # a real read of the spine, not a tautology that always passes a
        # spine-only dispatch.
        with no_ambient_spine_env(), tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spine_rel = ".agent-work/issue-1/IMPLEMENTER_PLAN.json"
            _write_spine(root / spine_rel, done=False)
            with fake_launch(RC, 0):
                with contextlib.redirect_stdout(io.StringIO()):
                    code = RC.main([
                        "--root", str(root), "--work-id", "issue-1", "--gate", "g1",
                        "--role", "implementer", "--spine", spine_rel, "--model", "sonnet",
                        "--parent", "test-parent",
                    ])
            self.assertEqual(1, code)
            entry = RC.load_registry(RC.registry_path("issue-1", root))[0]
            self.assertEqual("failed", entry["status"])

    def test_spine_only_dispatch_honors_nonzero_exit_even_when_spine_terminal(self):
        # A terminal spine alone must not paper over a crashed child: exit
        # code still matters.
        with no_ambient_spine_env(), tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spine_rel = ".agent-work/issue-1/IMPLEMENTER_PLAN.json"
            _write_spine(root / spine_rel, done=True)
            with fake_launch(RC, 3):
                with contextlib.redirect_stdout(io.StringIO()):
                    code = RC.main([
                        "--root", str(root), "--work-id", "issue-1", "--gate", "g1",
                        "--role", "implementer", "--spine", spine_rel, "--model", "sonnet",
                        "--parent", "test-parent",
                    ])
            self.assertEqual(3, code)
            entry = RC.load_registry(RC.registry_path("issue-1", root))[0]
            self.assertEqual("failed", entry["status"])

    def test_spine_only_dispatch_with_no_spine_file_at_all_is_recorded_failed(self):
        with no_ambient_spine_env(), tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spine_rel = ".agent-work/issue-1/IMPLEMENTER_PLAN.json"  # never written
            with fake_launch(RC, 0):
                with contextlib.redirect_stdout(io.StringIO()):
                    code = RC.main([
                        "--root", str(root), "--work-id", "issue-1", "--gate", "g1",
                        "--role", "implementer", "--spine", spine_rel, "--model", "sonnet",
                        "--parent", "test-parent",
                    ])
            self.assertEqual(1, code)
            entry = RC.load_registry(RC.registry_path("issue-1", root))[0]
            self.assertEqual("failed", entry["status"])

    def test_main_cli_refuses_neither_result_nor_spine(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                code = RC.main([
                    "--root", str(root), "--work-id", "issue-1", "--gate", "g1",
                    "--role", "implementer", "--handoff", "h.md",
                    "--parent", "test-parent",
                ])
            self.assertEqual(1, code)
            self.assertIn("REFUSED", stderr.getvalue())
            self.assertEqual([], RC.load_registry(RC.registry_path("issue-1", root)))


class SpineBlockedIdTests(unittest.TestCase):
    """`spine_blocked_id` reads the same file `spine_terminal` reads, with the
    same defensive parse -- a missing/unparseable/malformed spine has no
    blocked gate to report, never a raise."""

    def test_finds_the_blocked_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spine_rel = ".agent-work/issue-1/IMPLEMENTER_PLAN.json"
            _write_blocked_spine(root / spine_rel, blocked_id="f3-can-it-reach")
            self.assertEqual("f3-can-it-reach", RC.spine_blocked_id(spine_rel, root))

    def test_no_blocked_gate_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spine_rel = ".agent-work/issue-1/IMPLEMENTER_PLAN.json"
            _write_spine(root / spine_rel, done=False)
            self.assertIsNone(RC.spine_blocked_id(spine_rel, root))

    def test_terminal_spine_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spine_rel = ".agent-work/issue-1/IMPLEMENTER_PLAN.json"
            _write_spine(root / spine_rel, done=True)
            self.assertIsNone(RC.spine_blocked_id(spine_rel, root))

    def test_missing_spine_file_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertIsNone(
                RC.spine_blocked_id(".agent-work/issue-1/NEVER_WRITTEN.json", root)
            )

    def test_malformed_spine_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spine_rel = ".agent-work/issue-1/BAD.json"
            (root / spine_rel).parent.mkdir(parents=True, exist_ok=True)
            (root / spine_rel).write_text("not json", encoding="utf-8")
            self.assertIsNone(RC.spine_blocked_id(spine_rel, root))


class BlockedOutcomeTests(unittest.TestCase):
    """E1 fail-up (#559 follow-on): a crew that hits a check it cannot
    satisfy and calls `spine_halt block` before returning did exactly the
    right thing. `blocked` must be recorded as its OWN outcome -- distinct
    from `completed` and from `failed` (which keeps meaning the crew died or
    produced nothing) -- naming the gate and the parent it is asking, said
    plainly in the launcher's own output. Includes the negative control: a
    spine with no blocked gate must never record `blocked`."""

    def test_blocked_gate_is_recorded_blocked_not_failed(self):
        with no_ambient_spine_env(), tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spine_rel = ".agent-work/issue-1/IMPLEMENTER_PLAN.json"
            _write_blocked_spine(root / spine_rel, blocked_id="f3-can-it-reach")
            with fake_launch(RC, 0):
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    code = RC.main([
                        "--root", str(root), "--work-id", "issue-1", "--gate", "g1",
                        "--role", "implementer", "--spine", spine_rel,
                        "--parent", "constellation/epic-1/commander", "--model", "sonnet",
                    ])
            self.assertEqual(0, code)
            entry = RC.load_registry(RC.registry_path("issue-1", root))[0]
            self.assertEqual("blocked", entry["status"])
            self.assertEqual("f3-can-it-reach", entry["blocked_gate"])
            # said plainly in the launcher's own output: gate AND parent
            self.assertIn("f3-can-it-reach", out.getvalue())
            self.assertIn("constellation/epic-1/commander", out.getvalue())
            self.assertIn("blocked", out.getvalue())

    def test_blocked_with_unknown_parent_says_so_plainly(self):
        # B2 (deficiency cleanup batch A+B) made --parent required for a
        # fresh dispatch, so a FRESH blocked crew can no longer reach this
        # output with an absent parent -- the case this test exists for is
        # now only a LEGACY registry entry, recorded before B2 shipped (172
        # of 545 in this checkout carry a real parent; the rest carry
        # `parent: null`, same as this fixture). `_crew_status_line` is the
        # pure function that renders it, and it must keep reading an absent
        # parent as `UNKNOWN_PARENT` rather than crashing or going blank.
        legacy_entry = {
            "session_name": "constellation/issue-1/g1/implementer/attempt-1",
            "status": "blocked", "blocked_gate": "f3-can-it-reach", "parent": None,
        }
        line = RC._crew_status_line("crew", legacy_entry)
        self.assertIn(RC.UNKNOWN_PARENT, line)
        self.assertIn("f3-can-it-reach", line)

    def test_negative_control_no_blocked_gate_never_records_blocked(self):
        # Same spine shape, ONLY the gate's status differs (pending, not
        # blocked) -- proves the check is a real read of the spine, not a
        # tautology that always reports blocked for a spine-only dispatch.
        with no_ambient_spine_env(), tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spine_rel = ".agent-work/issue-1/IMPLEMENTER_PLAN.json"
            _write_spine(root / spine_rel, done=False)
            with fake_launch(RC, 0):
                with contextlib.redirect_stdout(io.StringIO()):
                    RC.main([
                        "--root", str(root), "--work-id", "issue-1", "--gate", "g1",
                        "--role", "implementer", "--spine", spine_rel, "--model", "sonnet",
                        "--parent", "test-parent",
                    ])
            entry = RC.load_registry(RC.registry_path("issue-1", root))[0]
            self.assertNotEqual("blocked", entry["status"])
            self.assertEqual("failed", entry["status"])

    def test_negative_control_terminal_spine_never_records_blocked(self):
        with no_ambient_spine_env(), tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spine_rel = ".agent-work/issue-1/IMPLEMENTER_PLAN.json"
            _write_spine(root / spine_rel, done=True)
            with fake_launch(RC, 0):
                with contextlib.redirect_stdout(io.StringIO()):
                    RC.main([
                        "--root", str(root), "--work-id", "issue-1", "--gate", "g1",
                        "--role", "implementer", "--spine", spine_rel, "--model", "sonnet",
                        "--parent", "test-parent",
                    ])
            entry = RC.load_registry(RC.registry_path("issue-1", root))[0]
            self.assertEqual("completed", entry["status"])

    def test_blocked_takes_priority_over_a_given_result_artifact(self):
        # A crew given BOTH --handoff/--result and --spine (today's normal
        # combined dispatch) that blocks its spine must still record
        # `blocked`, even though no result artifact was ever written.
        with no_ambient_spine_env(), tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "implementer")
            result = result_rel("issue-1", "g1", "implementer")
            spine_rel = ".agent-work/issue-1/IMPLEMENTER_PLAN.json"
            _write_blocked_spine(root / spine_rel)
            with fake_launch(RC, 0):  # no write_result_at: nothing lands
                with contextlib.redirect_stdout(io.StringIO()):
                    code = RC.main([
                        "--root", str(root), "--work-id", "issue-1", "--gate", "g1",
                        "--role", "implementer", "--handoff", handoff, "--result", result,
                        "--spine", spine_rel, "--model", "sonnet",
                        "--parent", "test-parent",
                    ])
            self.assertEqual(0, code)
            entry = RC.load_registry(RC.registry_path("issue-1", root))[0]
            self.assertEqual("blocked", entry["status"])

    def test_blocked_reports_success_exit_code_not_failure(self):
        # blocked is a legitimate, deliberate outcome, not a launcher error --
        # a polling parent reads the durable registry, not the exit code.
        with no_ambient_spine_env(), tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spine_rel = ".agent-work/issue-1/IMPLEMENTER_PLAN.json"
            _write_blocked_spine(root / spine_rel)
            with fake_launch(RC, 0):
                with contextlib.redirect_stdout(io.StringIO()):
                    code = RC.main([
                        "--root", str(root), "--work-id", "issue-1", "--gate", "g1",
                        "--role", "implementer", "--spine", spine_rel, "--model", "sonnet",
                        "--parent", "test-parent",
                    ])
            self.assertEqual(0, code)


class AssignmentKeyedLeaseTests(unittest.TestCase):
    """CONTROL B, made green: an assignment-keyed identity (no `attempt-<n>`
    tail) lets a respawn resume its lease idempotently instead of being refused
    as a different claimant. Drives the REAL `checklist_engine.py` CLI against a
    scratch spine — exactly the command shape the handoff's Control B used."""

    ENGINE = ROOT / "scripts" / "checklist_engine.py"

    def _scratch_spine(self, root: Path) -> Path:
        path = root / "scratch_spine.json"
        path.write_text(json.dumps({
            "work_id": "scratch-work",
            "type": "gated",
            "items": ["g1"],
            "tasks": {
                "g1": {
                    "id": "g1", "title": "scratch gate", "imperative": "do the thing",
                    "preconditions": [],
                    "postconditions": [{"id": "c1", "statement": "done", "check": None, "satisfied": False}],
                    "constraints": [], "directives": None, "child_checklist": None,
                    "status": "pending", "status_detail": {}, "result": None,
                    "finding": None, "evidence": [], "rework_count": 0,
                },
            },
            "consolidation": None, "triage_candidates": [], "blockers": [],
        }), encoding="utf-8")
        return path

    def _claim(self, spine: Path, session_id: str):
        import subprocess
        return subprocess.run(
            [sys.executable, str(self.ENGINE), "--file", str(spine), "claim",
             "--session-id", session_id, "--claimed-by", "implementer", "--worktree", "."],
            capture_output=True, text=True,
        )

    def test_attempt_tagged_identity_is_refused_on_respawn(self):
        # BEFORE picture (still true today — the engine's claim semantics are
        # untouched by this change): an attempt-tagged identity makes a respawn
        # look like a different claimant.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spine = self._scratch_spine(root)
            first = self._claim(spine, RC.session_name("scratch-work", "g1", "implementer", 1))
            self.assertEqual(0, first.returncode, first.stderr)
            second = self._claim(spine, RC.session_name("scratch-work", "g1", "implementer", 2))
            self.assertNotEqual(0, second.returncode)
            self.assertIn("already owned by active session", second.stderr)

    def test_assignment_keyed_identity_resumes_instead_of_refusing(self):
        # AFTER picture: dispatch mints assignment_session_name for BOTH the
        # original attempt and the respawn, so the second claim is idempotent.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spine = self._scratch_spine(root)
            identity = RC.assignment_session_name("scratch-work", "g1", "implementer")
            first = self._claim(spine, identity)
            self.assertEqual(0, first.returncode, first.stderr)
            second = self._claim(spine, identity)
            self.assertEqual(0, second.returncode, second.stderr)
            self.assertIn("resumed lease", second.stdout)


class DoorHijackRealEngineControlTests(unittest.TestCase):
    """CONTROL C: the cold reviewer's blocking finding, reproduced and closed.
    A door-bound dispatcher (its OWN SPINE_FILE/SPINE_SESSION already sitting in
    THIS process's environment, exactly as a live commander crew is bound)
    dispatches a child with its own `--spine`, through the REAL `RC.launch_crew`
    path — not a formula reconstructed inline. Against the real engine, the
    child claims its OWN spine/identity and the dispatcher's lease is provably
    untouched (`test_child_claims_its_own_spine_dispatcher_lease_untouched`
    below fails if `crew_env()` is reverted to the old `setdefault` formula,
    which is what makes it a real control: a companion test that reconstructed
    that old formula inline, exercising no `run_crew.py` code, used to sit here
    too and passed identically with or without the fix — worse than no control
    at all, since it read as evidence. Removed; this one carries the coverage)."""

    ENGINE = ROOT / "scripts" / "checklist_engine.py"

    def _scratch_spine(self, root: Path, name: str) -> Path:
        path = root / name
        path.write_text(json.dumps({
            "work_id": "w", "type": "gated", "items": ["g1"],
            "tasks": {
                "g1": {
                    "id": "g1", "title": "gate", "imperative": "do the thing",
                    "preconditions": [],
                    "postconditions": [{"id": "c1", "statement": "done", "check": None, "satisfied": False}],
                    "constraints": [], "directives": None, "child_checklist": None,
                    "status": "pending", "status_detail": {}, "result": None,
                    "finding": None, "evidence": [], "rework_count": 0,
                },
            },
            "consolidation": None, "triage_candidates": [], "blockers": [],
        }), encoding="utf-8")
        return path

    def _claim(self, spine: Path, session_id: str, claimed_by: str):
        import subprocess
        return subprocess.run(
            [sys.executable, str(self.ENGINE), "--file", str(spine), "claim",
             "--session-id", session_id, "--claimed-by", claimed_by, "--worktree", "."],
            capture_output=True, text=True,
        )

    def test_child_claims_its_own_spine_dispatcher_lease_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dispatcher_spine = self._scratch_spine(root, "dispatcher_spine.json")
            child_spine = self._scratch_spine(root, "child_spine.json")
            dispatcher_session = "constellation/w/commander"
            first = self._claim(dispatcher_spine, dispatcher_session, "commander")
            self.assertEqual(0, first.returncode, first.stderr)

            saved = {k: os.environ.pop(k, None) for k in ("SPINE_FILE", "SPINE_SESSION")}
            try:
                os.environ["SPINE_FILE"] = str(dispatcher_spine)
                os.environ["SPINE_SESSION"] = dispatcher_session
                handoff = write_handoff(root, "w", "g1", "implementer")
                result = result_rel("w", "g1", "implementer")
                with fake_launch(RC, 0, write_result_at=root / result) as calls:
                    RC.launch_crew(
                        work_id="w", gate="g1", role="implementer",
                        handoff=handoff, result=result, spine=str(child_spine),
                        worktree=".", model="sonnet", launcher="claude", attempt=1,
                        root=root, entries=[],
                        parent="test-parent",
                    )
                env = calls[0]["env"]
            finally:
                for k, v in saved.items():
                    if v is None:
                        os.environ.pop(k, None)
                    else:
                        os.environ[k] = v

            child_identity = RC.assignment_session_name("w", "g1", "implementer")
            self.assertEqual(str(child_spine), env["SPINE_FILE"])
            self.assertEqual(child_identity, env["SPINE_SESSION"])

            claim_child = self._claim(Path(env["SPINE_FILE"]), env["SPINE_SESSION"], "implementer")
            self.assertEqual(0, claim_child.returncode, claim_child.stderr)
            self.assertNotIn("resumed lease", claim_child.stdout)  # fresh claim, not a takeover

            # the dispatcher's own lease is untouched by the child's dispatch
            still_dispatcher = self._claim(dispatcher_spine, dispatcher_session, "commander")
            self.assertEqual(0, still_dispatcher.returncode, still_dispatcher.stderr)
            self.assertIn(f"resumed lease {dispatcher_session}", still_dispatcher.stdout)
            state = json.loads(dispatcher_spine.read_text(encoding="utf-8"))
            self.assertEqual("commander", state["engine_session"]["claimed_by"])


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
                        "--dispatch", "external", "--model", "sonnet",
                        "--parent", "test-parent",
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

    def test_cli_parser_persists_model_and_reasoning_effort_to_external_registry(self):
        """The CLI path, not a reconstructed CrewSpec, owns external metadata.
        g3-implement (#633): an arbitrary model string no longer passes
        through -- `"haiku"` is `implementer`'s allowed, non-default tier, so
        this also pins that a `--reason` given alongside a real `--model`
        persists to the registry entry too."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "implementer")
            result = result_rel("issue-1", "g1", "implementer")
            with fake_launch(RC, 0) as calls:
                with contextlib.redirect_stdout(io.StringIO()):
                    code = RC.main([
                        "--root", str(root), "--work-id", "issue-1", "--gate", "g1",
                        "--role", "implementer", "--handoff", handoff, "--result", result,
                        "--backend", "external", "--model", "haiku",
                        "--reason", "budget-constrained dispatch, haiku sufficient for this handoff",
                        "--reasoning-effort", "xhigh",
                        "--parent", "test-parent",
                    ])
            self.assertEqual(0, code)
            self.assertEqual([], calls)
            entry = RC.load_registry(RC.registry_path("issue-1", root))[0]
            self.assertEqual("external", entry["backend"])
            self.assertEqual("haiku", entry["model"])
            self.assertEqual(
                "budget-constrained dispatch, haiku sufficient for this handoff",
                entry["reason"],
            )
            self.assertEqual("xhigh", entry["reasoning_effort"])

    def test_external_dispatch_refuses_spine(self):
        # INTENTIONAL SCENARIO CHANGE (issue #432): `--spine` on the external
        # backend used to be refused outright (binding was impossible, so the
        # old reasoning treated the flag itself as unsafe). #432's fix makes
        # `--spine` verification-only here: it is still never BOUND into an
        # environment (nothing spawns, so nothing can be bound), but it is now
        # ACCEPTED and RECORDED on the entry so a later `--verify-result` can
        # consult it via `spine_terminal`. This test used to assert the old
        # refusal; it now asserts accept-and-record. Drives the real CLI
        # entrypoint (`RC.main`), not a reconstructed formula.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "implementer")
            result = result_rel("issue-1", "g1", "implementer")
            spine_rel = ".agent-work/issue-1/IMPLEMENTER_PLAN.json"
            with fake_launch(RC, 0, write_result_at=root / result) as calls:
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    code = RC.main([
                        "--root", str(root), "--work-id", "issue-1", "--gate", "g1",
                        "--role", "implementer", "--handoff", handoff, "--result", result,
                        "--backend", "external", "--spine", spine_rel, "--model", "sonnet",
                        "--parent", "test-parent",
                    ])
            self.assertEqual(0, code)
            self.assertEqual([], calls)  # still nothing spawned -- external spawns nothing
            reg = RC.load_registry(RC.registry_path("issue-1", root))
            self.assertEqual(1, len(reg))
            # --spine IS recorded on the entry (verification-only, not binding)
            self.assertEqual(spine_rel, reg[0]["spine"])
            self.assertEqual("running", reg[0]["status"])

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
                    "--parent", "test-parent",
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
                "--dispatch", "external", "--model", "sonnet",
                "--parent", "test-parent",
            ]
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(0, RC.main(argv))
            # the first external attempt is `running` and holds the slot
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(1, RC.main(argv))

    def test_verify_result_absent_then_present_marks_completed(self):
        # INTENTIONAL SCENARIO CHANGE (issue #432, the core fix of this gate):
        # this test used to assert that a fresh result artifact ALONE, with no
        # spine evidence and no explicit override, was enough for
        # `--verify-result` to mark the crew `completed` (code_present == 0).
        # That is exactly the silent-clean-pass #432 closes: a crew that drove
        # no spine at all must not read as an unqualified success BY DEFAULT.
        # The final assertion below is rewritten from `code_present == 0` to
        # `code_present == 1` (REFUSE) -- the crew's own bar now requires
        # either a terminal spine (--spine at dispatch or --verify-spine at
        # verify time) or an explicit, reasoned `--accept-mtime-only-risk`.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "implementer")
            result = result_rel("issue-1", "g1", "implementer")
            session = "constellation/issue-1/g1/implementer/attempt-1"
            with contextlib.redirect_stdout(io.StringIO()):
                RC.main([
                    "--root", str(root), "--work-id", "issue-1", "--gate", "g1",
                    "--role", "implementer", "--handoff", handoff, "--result", result,
                    "--dispatch", "external", "--model", "sonnet",
                    "--parent", "test-parent",
                ])
            # result artifact not written yet -> verify is nonzero, stays running
            with contextlib.redirect_stdout(io.StringIO()):
                code_absent = RC.main(["--root", str(root), "--verify-result", session, "--parent", "test-parent"])
            self.assertEqual(1, code_absent)
            self.assertEqual(
                "running", RC.load_registry(RC.registry_path("issue-1", root))[0]["status"]
            )
            # write the result artifact (the out-of-band crew finished) -- but
            # with NO spine evidence and NO --accept-mtime-only-risk override,
            # this must now REFUSE by default (#432), not mark completed.
            (root / result).parent.mkdir(parents=True, exist_ok=True)
            (root / result).write_text("RESULT\n", encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
                code_present = RC.main(["--root", str(root), "--verify-result", session, "--parent", "test-parent"])
            self.assertEqual(1, code_present)
            self.assertIn("REFUSED", stderr.getvalue())
            self.assertIn("432", stderr.getvalue())
            entry = RC.load_registry(RC.registry_path("issue-1", root))[0]
            self.assertEqual("running", entry["status"])
            self.assertFalse(entry["spine_verified"])

    @staticmethod
    def _write_gated_spine(path: Path, *, terminal: bool) -> None:
        """A minimal hand-built gated checklist fixture -- does not need the
        real engine (per spine_terminal's own docstring). `terminal=False`
        mirrors #432's actual evidence: a spine that exists but was never
        advanced past its first (`pending`, i.e. init) item."""
        path.parent.mkdir(parents=True, exist_ok=True)
        status = "complete" if terminal else "pending"
        path.write_text(json.dumps({
            "type": "gated",
            "items": ["m1"],
            "tasks": {"m1": {"id": "m1", "status": status}},
        }), encoding="utf-8")

    def test_verify_named_spine_not_terminal_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "implementer")
            result = result_rel("issue-1", "g1", "implementer")
            session = "constellation/issue-1/g1/implementer/attempt-1"
            spine_rel = ".agent-work/issue-1/IMPLEMENTER_PLAN.json"
            self._write_gated_spine(root / spine_rel, terminal=False)
            with contextlib.redirect_stdout(io.StringIO()):
                RC.main([
                    "--root", str(root), "--work-id", "issue-1", "--gate", "g1",
                    "--role", "implementer", "--handoff", handoff, "--result", result,
                    "--backend", "external", "--spine", spine_rel, "--model", "sonnet",
                    "--parent", "test-parent",
                ])
            (root / result).parent.mkdir(parents=True, exist_ok=True)
            (root / result).write_text("RESULT\n", encoding="utf-8")

            # RED-PROOF: `CrewBackend.verify` is the literal PRE-FIX logic --
            # unchanged by this gate (ExternalBackend.verify is an override,
            # never a base-class edit) -- so calling it directly on this exact
            # entry/result is a genuine, not simulated, demonstration of the
            # #432 bug: a fresh result artifact ALONE reads `completed` despite
            # the un-terminal spine right next to it.
            entries = RC.load_registry(RC.registry_path("issue-1", root))
            pre_fix_fresh, pre_fix_entry = RC.CrewBackend().verify(entries, session, root=root)
            self.assertTrue(pre_fix_fresh, "pre-fix CrewBackend.verify wrongly reads fresh")
            self.assertEqual("completed", pre_fix_entry["status"])

            # Undo CrewBackend.verify's side effect (it mutated + saved the
            # SAME shared registry file the fix must judge next) so the fix's
            # own verify() below observes the crew's true pre-verification
            # state, not the pre-fix demonstration's leftover mutation.
            entries = RC.load_registry(RC.registry_path("issue-1", root))
            entries[0]["status"] = "running"
            RC.save_registry(RC.registry_path("issue-1", root), entries)

            # THE FIX: ExternalBackend.verify() consults the named spine and
            # refuses because it never reached terminal -- AND semantics, the
            # fresh result next to it does not rescue the verdict.
            entries = RC.load_registry(RC.registry_path("issue-1", root))
            fresh, entry = RC.ExternalBackend().verify(entries, session, root=root)
            self.assertFalse(fresh)
            self.assertEqual("running", entry["status"])
            self.assertFalse(entry["spine_verified"])

            # Same story through the real CLI entrypoint.
            stderr = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
                code = RC.main(["--root", str(root), "--verify-result", session, "--parent", "test-parent"])
            self.assertEqual(1, code)
            self.assertIn("REFUSED", stderr.getvalue())
            self.assertIn(spine_rel, stderr.getvalue())

    def test_verify_named_spine_terminal_completes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "implementer")
            result = result_rel("issue-1", "g1", "implementer")
            session = "constellation/issue-1/g1/implementer/attempt-1"
            spine_rel = ".agent-work/issue-1/IMPLEMENTER_PLAN.json"
            self._write_gated_spine(root / spine_rel, terminal=True)
            with contextlib.redirect_stdout(io.StringIO()):
                RC.main([
                    "--root", str(root), "--work-id", "issue-1", "--gate", "g1",
                    "--role", "implementer", "--handoff", handoff, "--result", result,
                    "--backend", "external", "--spine", spine_rel, "--model", "sonnet",
                    "--parent", "test-parent",
                ])
            (root / result).parent.mkdir(parents=True, exist_ok=True)
            (root / result).write_text("RESULT\n", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                code = RC.main(["--root", str(root), "--verify-result", session, "--parent", "test-parent"])
            self.assertEqual(0, code)
            entry = RC.load_registry(RC.registry_path("issue-1", root))[0]
            self.assertEqual("completed", entry["status"])
            self.assertTrue(entry["spine_verified"])

    def test_verify_time_spine_override_completes(self):
        # Dispatch with NO --spine; the crew's actual plan/spine path is only
        # learned AFTER it returns. --verify-spine at verify time must be
        # consulted independently of dispatch-time state (it is not recorded
        # on the entry at all here).
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "implementer")
            result = result_rel("issue-1", "g1", "implementer")
            session = "constellation/issue-1/g1/implementer/attempt-1"
            with contextlib.redirect_stdout(io.StringIO()):
                RC.main([
                    "--root", str(root), "--work-id", "issue-1", "--gate", "g1",
                    "--role", "implementer", "--handoff", handoff, "--result", result,
                    "--dispatch", "external", "--model", "sonnet",
                    "--parent", "test-parent",
                ])
            self.assertIsNone(RC.load_registry(RC.registry_path("issue-1", root))[0].get("spine"))
            (root / result).parent.mkdir(parents=True, exist_ok=True)
            (root / result).write_text("RESULT\n", encoding="utf-8")
            spine_rel = ".agent-work/issue-1/discovered/PLAN.json"
            ExternalDispatchTests._write_gated_spine(root / spine_rel, terminal=True)
            with contextlib.redirect_stdout(io.StringIO()):
                code = RC.main([
                    "--root", str(root), "--verify-result", session,
                    "--verify-spine", spine_rel,
                    "--parent", "test-parent",
                ])
            self.assertEqual(0, code)
            entry = RC.load_registry(RC.registry_path("issue-1", root))[0]
            self.assertEqual("completed", entry["status"])
            self.assertTrue(entry["spine_verified"])

    def test_verify_accept_mtime_only_risk_completes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "implementer")
            result = result_rel("issue-1", "g1", "implementer")
            session = "constellation/issue-1/g1/implementer/attempt-1"
            with contextlib.redirect_stdout(io.StringIO()):
                RC.main([
                    "--root", str(root), "--work-id", "issue-1", "--gate", "g1",
                    "--role", "implementer", "--handoff", handoff, "--result", result,
                    "--dispatch", "external", "--model", "sonnet",
                    "--parent", "test-parent",
                ])
            (root / result).parent.mkdir(parents=True, exist_ok=True)
            (root / result).write_text("RESULT\n", encoding="utf-8")
            stdout, stderr = io.StringIO(), io.StringIO()
            reason = "no spine target available for this legacy dispatch path"
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = RC.main([
                    "--root", str(root), "--verify-result", session,
                    "--accept-mtime-only-risk", reason,
                    "--parent", "test-parent",
                ])
            self.assertEqual(0, code)
            self.assertIn(reason, stdout.getvalue())
            self.assertIn("RISK", stdout.getvalue())
            self.assertIn(reason, stderr.getvalue())
            self.assertIn("RISK", stderr.getvalue())
            entry = RC.load_registry(RC.registry_path("issue-1", root))[0]
            self.assertEqual("completed", entry["status"])
            self.assertIsNone(entry["spine_verified"])
            self.assertEqual(reason, entry["mtime_only_risk_accepted"]["reason"])

    def test_verify_spine_only_external_dispatch_no_crash(self):
        # `result=None` + `--spine` given at dispatch (legal per
        # CrewSpec.__post_init__, newly reachable on this backend since
        # dispatch() stopped refusing --spine). No result artifact is ever
        # involved -- the pre-guard version (`entry["result"]`/bracket access
        # into result_exists/result_fresh) would crash on `Path(None)`; the
        # `.get("result") is not None` guard must prevent that and judge
        # completion solely on the spine.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "implementer")
            session = "constellation/issue-1/g1/implementer/attempt-1"
            spine_rel = ".agent-work/issue-1/IMPLEMENTER_PLAN.json"
            ExternalDispatchTests._write_gated_spine(root / spine_rel, terminal=True)
            with contextlib.redirect_stdout(io.StringIO()):
                code_dispatch = RC.main([
                    "--root", str(root), "--work-id", "issue-1", "--gate", "g1",
                    "--role", "implementer", "--handoff", handoff,
                    "--backend", "external", "--spine", spine_rel, "--model", "sonnet",
                    "--parent", "test-parent",
                ])
            self.assertEqual(0, code_dispatch)
            entry_before = RC.load_registry(RC.registry_path("issue-1", root))[0]
            self.assertIsNone(entry_before["result"])
            with contextlib.redirect_stdout(io.StringIO()):
                code = RC.main(["--root", str(root), "--verify-result", session, "--parent", "test-parent"])
            self.assertEqual(0, code)  # no crash
            entry = RC.load_registry(RC.registry_path("issue-1", root))[0]
            self.assertEqual("completed", entry["status"])
            self.assertTrue(entry["spine_verified"])
            self.assertFalse(entry["result_present"])
            self.assertFalse(entry["result_fresh"])


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
                    "--dispatch", "external", "--model", "sonnet",
                    "--parent", "test-parent",
                ])
            # a leftover result from a PRIOR attempt, older than this dispatch
            entry = RC.load_registry(RC.registry_path("issue-1", root))[0]
            dispatch_ts = datetime.fromisoformat(entry["started_at"]).timestamp()
            write_result_with_mtime(root / result, dispatch_ts - 3600)
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                code = RC.main(["--root", str(root), "--verify-result", session, "--parent", "test-parent"])
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
                    "--dispatch", "external", "--model", "sonnet",
                    "--parent", "test-parent",
                ])
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                code = RC.main(["--root", str(root), "--verify-result", session, "--parent", "test-parent"])
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
                    handoff=handoff, result=result, worktree=".", model="sonnet",
                    launcher="claude", attempt=1, root=root, entries=[],
                    parent="test-parent",
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

    def test_parent_is_recorded_when_given(self):
        entry = RC.build_entry(
            backend="cli", pid=1, parent="constellation/epic-1/commander", **self._kwargs(),
        )
        self.assertEqual("constellation/epic-1/commander", entry["parent"])

    def test_parent_is_recorded_as_none_not_omitted_when_absent(self):
        # Nullable-but-present, matching handoff/result/spine's own shape: a
        # reader can distinguish "no parent given" from "field predates this
        # feature" (KeyError on the latter, None on the former).
        entry = RC.build_entry(backend="cli", pid=1, **self._kwargs())
        self.assertIn("parent", entry)
        self.assertIsNone(entry["parent"])

    def test_build_entry_cli_door_bound_true(self):
        # The cli backend spawns a real child and binds SPINE_FILE/SPINE_SESSION
        # into its environment (_crew_door_env) -- its door is genuinely bound.
        entry = RC.build_entry(backend="cli", pid=1, **self._kwargs())
        self.assertIs(True, entry["door_bound"])

    def test_build_entry_external_door_bound_false(self):
        # The external backend spawns no process and builds no environment, so
        # nothing ever binds SPINE_FILE/SPINE_SESSION for it -- its door
        # resolves to .mcp.json's demo default. This field must state that
        # plainly in the registry rather than let it silently read as bound.
        entry = RC.build_entry(backend="external", pid=None, **self._kwargs())
        self.assertIs(False, entry["door_bound"])


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

    def test_blocked_spine_is_recorded_blocked_with_exit0_final(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spine_rel = "spine.json"
            _write_blocked_spine(root / spine_rel, blocked_id="c1")
            entry = {}
            final = RC.finalize_from_exit_code(
                entry, exit_code=0, result=None, root=root, since=iso(self.BASE),
                spine=spine_rel,
            )
            self.assertEqual(0, final)
            self.assertEqual("blocked", entry["status"])
            self.assertEqual("c1", entry["blocked_gate"])

    def test_no_blocked_gate_and_no_spine_given_is_unaffected(self):
        # Negative control at the unit level: `spine=None` never consults a
        # blocked gate at all.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_result_with_mtime(root / "r.md", self.BASE + 60)
            entry = {}
            RC.finalize_from_exit_code(
                entry, exit_code=0, result="r.md", root=root, since=iso(self.BASE),
                spine=None,
            )
            self.assertEqual("completed", entry["status"])
            self.assertNotIn("blocked_gate", entry)

    def test_finalize_terminal_spine_rescues_missing_result(self):
        # Both --spine and --result given (the archive gate's shape): the
        # result artifact is missing, but the bound spine IS terminal --
        # the terminal spine must rescue the verdict into `completed`
        # rather than inverting it to `failed`.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spine_rel = "spine.json"
            _write_spine(root / spine_rel, done=True)
            entry = {}
            final = RC.finalize_from_exit_code(
                entry, exit_code=0, result="r.md", root=root, since=iso(self.BASE),
                spine=spine_rel,
            )
            self.assertEqual(0, final)
            self.assertEqual("completed", entry["status"])
            self.assertEqual("spine_terminal", entry["verdict_source"])

    def test_finalize_still_fails_when_spine_not_terminal(self):
        # Same both-flags shape, but the spine is NOT terminal and there is
        # still no result -- this must NOT become a rubber stamp: a
        # genuinely failed crew must keep reading `failed`.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spine_rel = "spine.json"
            _write_spine(root / spine_rel, done=False)
            entry = {}
            final = RC.finalize_from_exit_code(
                entry, exit_code=0, result="r.md", root=root, since=iso(self.BASE),
                spine=spine_rel,
            )
            self.assertEqual("failed", entry["status"])
            self.assertNotEqual("spine_terminal", entry["verdict_source"])

    def test_finalize_blocked_wins_regardless_of_result_or_spine(self):
        # A FRESH result AND a spine whose single item is `blocked` (never
        # simultaneously terminal in this engine's vocabulary -- blocked is
        # not `complete`/`skipped`, so spine_terminal reads False here).
        # blocked_gate must still win over both other paths.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_result_with_mtime(root / "r.md", self.BASE + 60)
            spine_rel = "spine.json"
            _write_blocked_spine(root / spine_rel, blocked_id="w1")
            self.assertEqual("w1", RC.spine_blocked_id(spine_rel, root))
            self.assertFalse(RC.spine_terminal(spine_rel, root))
            entry = {}
            final = RC.finalize_from_exit_code(
                entry, exit_code=0, result="r.md", root=root, since=iso(self.BASE),
                spine=spine_rel,
            )
            self.assertEqual(0, final)
            self.assertEqual("blocked", entry["status"])
            self.assertEqual("w1", entry["blocked_gate"])
            self.assertEqual("blocked_gate", entry["verdict_source"])


class ParkedOutcomeTests(unittest.TestCase):
    """Issue #618: a crew that parks at the engine's context line closed its
    gate, wrote its handoff and stopped -- the behaviour the launch order asks
    for. It used to be recorded `failed` with exit 1, the same line a crash
    produces, so every correct long-run stop cost the parent a trip into the
    work area to find out nothing was wrong."""

    BASE = 1_700_000_000.0

    def test_parked_spine_records_partial_and_exits_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_parked_spine(root / "spine.json")
            self.assertTrue(RC.spine_parked("spine.json", root))
            entry = {}
            final = RC.finalize_from_exit_code(
                entry, exit_code=0, result=None, root=root, since=iso(self.BASE),
                spine="spine.json",
            )
            self.assertEqual(0, final)
            self.assertEqual("partial", entry["status"])
            self.assertEqual("spine_parked", entry["verdict_source"])

    def test_crash_mid_gate_still_records_failed(self):
        # The other arm, and the one that must not move: an in-progress gate
        # means nobody closed anything on the way out.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_crashed_spine(root / "spine.json")
            self.assertFalse(RC.spine_parked("spine.json", root))
            entry = {}
            final = RC.finalize_from_exit_code(
                entry, exit_code=0, result=None, root=root, since=iso(self.BASE),
                spine="spine.json",
            )
            self.assertEqual(1, final)
            self.assertEqual("failed", entry["status"])

    def test_nonzero_exit_over_a_parked_spine_still_fails(self):
        # A child that died loudly is failed regardless of how its spine reads.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_parked_spine(root / "spine.json")
            entry = {}
            final = RC.finalize_from_exit_code(
                entry, exit_code=3, result=None, root=root, since=iso(self.BASE),
                spine="spine.json",
            )
            self.assertEqual(3, final)
            self.assertEqual("failed", entry["status"])

    def test_untouched_spine_is_not_parked(self):
        # Nothing closed: the crew never got started, which is not a park.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_spine(root / "spine.json", done=False)
            self.assertFalse(RC.spine_parked("spine.json", root))

    def test_terminal_spine_is_not_parked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_spine(root / "spine.json", done=True)
            self.assertFalse(RC.spine_parked("spine.json", root))

    def test_missing_and_malformed_spines_are_not_parked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "bad.json").write_text("{not json", encoding="utf-8")
            (root / "shape.json").write_text(json.dumps({"items": []}), encoding="utf-8")
            self.assertFalse(RC.spine_parked("absent.json", root))
            self.assertFalse(RC.spine_parked("bad.json", root))
            self.assertFalse(RC.spine_parked("shape.json", root))

    def test_blocked_still_wins_over_parked(self):
        # A spine with a closed gate AND a blocked one reads blocked: the
        # blocked gate names a question for the parent, which outranks
        # "there is work left".
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "spine.json").write_text(json.dumps({
                "work_id": "issue-1", "type": "gated", "items": ["w1", "w2"],
                "tasks": {"w1": {"id": "w1", "status": "complete"},
                          "w2": {"id": "w2", "status": "blocked"}},
            }), encoding="utf-8")
            entry = {}
            final = RC.finalize_from_exit_code(
                entry, exit_code=0, result=None, root=root, since=iso(self.BASE),
                spine="spine.json",
            )
            self.assertEqual(0, final)
            self.assertEqual("blocked", entry["status"])

    def test_status_line_says_parked_not_failed(self):
        line = RC._crew_status_line("crew", {"session_name": "s1", "status": "partial"})
        self.assertIn("partial", line)
        self.assertIn("resume", line)

    def test_recover_classifies_partial_without_result_as_resumable(self):
        entry = {
            "session_name": "constellation/issue-1/g1/commander/attempt-3",
            "work_id": "issue-1", "gate": "g1", "role": "commander", "attempt": 3,
            "worktree": ".", "status": "partial", "pid": 111, "result": None,
        }
        self.assertEqual(
            REC.STATE_RESUMABLE,
            REC.classify_entry(entry, lambda pid: False, lambda e: False),
        )
        self.assertEqual(
            REC.STATE_COMPLETE,
            REC.classify_entry(entry, lambda pid: False, lambda e: True),
        )


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
                parent="test-parent",
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

    def test_cli_dispatch_records_model_when_given(self):
        # `--model sonnet` is visible on run_crew.py's own argv and on the
        # spawned `claude -p` argv (build_crew_argv forwards spec.model) --
        # but the REGISTRY entry must carry it too, or a reader of
        # crew-runs.json cannot tell "no --model given" apart from "--model
        # given and dropped". Issue #559 G1.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "reviewer")
            result = result_rel("issue-1", "g1", "reviewer")
            spec = RC.CrewSpec(
                work_id="issue-1", gate="g1", role="reviewer", handoff=handoff,
                result=result, worktree=".", attempt=1, model="sonnet", launcher="claude",
                parent="test-parent",
            )
            entries: list[dict] = []
            with fake_launch(RC, 0, write_result_at=root / result):
                code, entry = RC.CliBackend().dispatch(spec, root=root, entries=entries)
            self.assertEqual(0, code)
            self.assertEqual("sonnet", entry["model"])

    def test_reasoning_effort_is_recorded_and_forwarded_as_effort_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "reviewer")
            result = result_rel("issue-1", "g1", "reviewer")
            spec = RC.CrewSpec(
                work_id="issue-1", gate="g1", role="reviewer", handoff=handoff,
                result=result, worktree=".", attempt=1, model="sonnet",
                launcher="claude", reasoning_effort="high",
                parent="test-parent",
            )
            entries: list[dict] = []
            with fake_launch(RC, 0, write_result_at=root / result) as calls:
                code, entry = RC.CliBackend().dispatch(spec, root=root, entries=entries)
            self.assertEqual(0, code)
            self.assertEqual("high", entry["reasoning_effort"])
            argv = calls[0]["argv"]
            self.assertNotIn("--reasoning-effort", argv)
            self.assertIn("--effort", argv)
            self.assertEqual("high", argv[argv.index("--effort") + 1])

    def test_cli_resume_reads_reasoning_effort_from_registry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "reviewer")
            result = result_rel("issue-1", "g1", "reviewer")
            entries: list[dict] = []
            with fake_launch(RC, 1) as calls:
                _, entry = RC.CliBackend().dispatch(
                    RC.CrewSpec(
                        work_id="issue-1", gate="g1", role="reviewer", handoff=handoff,
                        result=result, worktree=".", attempt=1, model="sonnet",
                        launcher="claude", reasoning_effort="low",
                        parent="test-parent",
                    ), root=root, entries=entries,
                )
            with fake_launch(RC, 1) as resume_calls:
                RC.CliBackend().resume(entry["session_name"], root=root, entries=entries)
            argv = resume_calls[0]["argv"]
            self.assertNotIn("--reasoning-effort", argv)
            self.assertIn("--effort", argv)
            self.assertEqual("low", argv[argv.index("--effort") + 1])

    def test_legacy_resume_without_reasoning_effort_does_not_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "reviewer")
            result = result_rel("issue-1", "g1", "reviewer")
            entry = RC.build_entry(
                work_id="issue-1", gate="g1", role="reviewer", attempt=1,
                worktree=".", handoff=handoff, result=result, root=root,
                started=RC._now(), backend="cli", pid=1,
            )
            entries = [entry]
            with fake_launch(RC, 1) as calls:
                RC.CliBackend().resume(entry["session_name"], root=root, entries=entries)
            argv = calls[0]["argv"]
            self.assertNotIn("--reasoning-effort", argv)
            self.assertNotIn("--effort", argv)

    def test_cli_dispatch_missing_handoff_refuses_with_launch_wording(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = RC.CrewSpec(
                work_id="issue-1", gate="g1", role="reviewer",
                handoff=".agent-work/issue-1/crew-handoffs/g1-reviewer.md",
                result=result_rel("issue-1", "g1", "reviewer"), worktree=".", attempt=1,
                model="sonnet",
                parent="test-parent",
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
                result=result, worktree=".", attempt=1, model="sonnet",
                parent="test-parent",
            )
            entries: list[dict] = []
            with fake_launch(RC, 0, write_result_at=root / result) as calls:
                code, entry = RC.ExternalBackend().dispatch(spec, root=root, entries=entries)
            self.assertIsNone(code)              # record-only: no exit code
            self.assertEqual([], calls)          # nothing spawned
            self.assertEqual("external", entry["backend"])
            self.assertEqual("external", entry["dispatch"])
            self.assertIsNone(entry["pid"])
            self.assertEqual("sonnet", entry["model"])
            self.assertEqual("running", entry["status"])

    def test_external_dispatch_missing_handoff_refuses_with_record_wording(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = RC.CrewSpec(
                work_id="issue-1", gate="g1", role="implementer",
                handoff=".agent-work/issue-1/crew-handoffs/g1-implementer.md",
                result=result_rel("issue-1", "g1", "implementer"), worktree=".", attempt=1,
                model="sonnet",
                parent="test-parent",
            )
            with self.assertRaises(RC.CrewLaunchError) as ctx:
                RC.ExternalBackend().dispatch(spec, root=root, entries=[])
            self.assertIn("refusing to record", str(ctx.exception))

    def test_external_dispatch_prints_unbound_door_banner(self):
        # The external backend spawns no process and builds no environment, so
        # its MCP door silently resolves to .mcp.json's demo default -- this
        # banner is the visibility fix (binding out-of-band is impossible by
        # construction). It must fire on EVERY external dispatch, unconditionally.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "implementer")
            result = result_rel("issue-1", "g1", "implementer")
            spec = RC.CrewSpec(
                work_id="issue-1", gate="g1", role="implementer", handoff=handoff,
                result=result, worktree=".", attempt=1, model="sonnet",
                parent="test-parent",
            )
            captured = io.StringIO()
            with contextlib.redirect_stderr(captured):
                RC.ExternalBackend().dispatch(spec, root=root, entries=[])
            banner = captured.getvalue()
            self.assertIn("unbound", banner.lower())
            self.assertIn(".mcp.json", banner)
            self.assertIn("demo default", banner)
            self.assertIn("spine_status", banner)

    def test_verify_is_uniform_across_backends(self):
        """INTENTIONAL NARROWING (issue #432) of
        docs/superpowers/specs/2026-07-07-crew-backend-design.md Decision 2
        ("the result contract is backend-invariant ... never forked"). This
        test used to assert CliBackend().verify() and ExternalBackend().verify()
        behave IDENTICALLY on a fresh result with no spine evidence at all --
        that is now intentionally false. The base exists-AND-fresh contract
        itself stays byte-for-byte SHARED (unforked) -- CliBackend keeps the
        exact old mtime-only `CrewBackend.verify` behavior unchanged below.
        ExternalBackend now layers one ADDITIONAL gate on top, for this
        backend only: without spine evidence or an explicit accepted risk, a
        fresh result alone no longer completes it (#432's core fix -- a
        record-only dispatch that drove no spine must not read as an
        unqualified clean success by default). The old mtime-only-pass
        behavior stays reachable through ExternalBackend as an explicit,
        reasoned `accept_mtime_only_risk` override, proven below."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g1", "implementer")
            result = result_rel("issue-1", "g1", "implementer")
            session = "constellation/issue-1/g1/implementer/attempt-1"
            entries = [RC.record_external_attempt(
                work_id="issue-1", gate="g1", role="implementer", handoff=handoff,
                result=result, worktree=".", model="sonnet", attempt=1, root=root, entries=[],
                parent="test-parent",
            )]
            # not written yet -> not fresh, stays running (unchanged on either backend)
            fresh_cli, _ = RC.CliBackend().verify(entries, session, root=root)
            self.assertFalse(fresh_cli)
            self.assertEqual("running", entries[0]["status"])
            # write it: CliBackend's base-class verify is UNCHANGED -- fresh
            # result alone still completes it (CliBackend never calls .verify()
            # in production, but the base-class method itself is untouched).
            (root / result).parent.mkdir(parents=True, exist_ok=True)
            (root / result).write_text("RESULT\n", encoding="utf-8")
            fresh_cli_after, entry_cli = RC.CliBackend().verify(entries, session, root=root)
            self.assertTrue(fresh_cli_after)
            self.assertEqual("completed", entry_cli["status"])

            # Reset to `running` to isolate ExternalBackend's own verdict on
            # the SAME fresh result -- the divergence, not the CLI side.
            entries[0]["status"] = "running"
            RC.save_registry(RC.registry_path("issue-1", root), entries)

            # ExternalBackend now DEFAULT-REFUSES the identical fresh result:
            # no spine evidence, no override -> stays running, not fresh.
            fresh_ext, entry_ext = RC.ExternalBackend().verify(entries, session, root=root)
            self.assertFalse(fresh_ext)
            self.assertEqual("running", entry_ext["status"])
            self.assertFalse(entry_ext["spine_verified"])

            # The old behavior is still REACHABLE, but only via the explicit,
            # reasoned override -- never the default.
            fresh_override, entry_override = RC.ExternalBackend().verify(
                entries, session, root=root, accept_mtime_only_risk="regression-test override",
            )
            self.assertTrue(fresh_override)
            self.assertEqual("completed", entry_override["status"])

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
            "--model", "sonnet", "--parent", "test-parent",
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
                    code = RC.main(["--root", str(root), "--resume", session, "--parent", "test-parent"])
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
    `result_fresh`, never forked.

    INTENTIONAL NARROWING (issue #432): the base exists-AND-fresh contract
    below (missing -> not fresh; stale -> present-but-not-fresh) stays
    byte-for-byte SHARED across both backends -- (a) and (b) are unchanged and
    still run through the same shared loop. Only the FRESH-result case (c)
    diverges, and only on `ExternalBackend`: a fresh result alone no longer
    completes it without spine evidence or an explicit accepted risk (#432's
    core fix). `CliBackend` keeps the old fresh-alone-completes behavior
    verbatim (it never calls `.verify()` in production, but the shared
    base-class method itself is untouched). This is an ADDITIONAL gate
    layered on `ExternalBackend` for its spine-evidence dimension, not a fork
    of the base `result_exists`/`result_fresh` contract itself."""

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
                # (a) result missing -> not fresh, stays running -- SHARED, unchanged
                fresh, e = backend.verify(entries, session, root=root)
                self.assertFalse(fresh, backend.name)
                self.assertEqual("running", e["status"], backend.name)
                # (b) STALE leftover (mtime predates dispatch) -> present but not
                # fresh -- SHARED, unchanged (identical on both backends: the
                # ExternalBackend default-refuse branch computes result_present/
                # result_fresh from the real facts even though `fresh` itself is
                # always False there regardless of staleness).
                write_result_with_mtime(root / result, self.BASE - 60)
                fresh, e = backend.verify(entries, session, root=root)
                self.assertFalse(fresh, backend.name)
                self.assertTrue(e["result_present"], backend.name)
                self.assertFalse(e["result_fresh"], backend.name)
                self.assertEqual("running", e["status"], backend.name)
                # (c) FRESH result (mtime at/after dispatch) -- DIVERGES (#432).
                write_result_with_mtime(root / result, self.BASE + 60)
                fresh, e = backend.verify(entries, session, root=root)
                if backend.name == RC.BACKEND_CLI:
                    self.assertTrue(fresh, backend.name)
                    self.assertEqual("completed", e["status"], backend.name)
                else:
                    # ExternalBackend: fresh result ALONE, no spine evidence, no
                    # override -> default-refuses (the #432 fix).
                    self.assertFalse(fresh, backend.name)
                    self.assertEqual("running", e["status"], backend.name)
                    self.assertFalse(e["spine_verified"], backend.name)
                    # The old behavior stays REACHABLE via the explicit,
                    # reasoned override -- confirming the divergence is
                    # deliberate, not an accidental loss of capability.
                    fresh_override, e_override = backend.verify(
                        entries, session, root=root,
                        accept_mtime_only_risk="regression-test override",
                    )
                    self.assertTrue(fresh_override, backend.name)
                    self.assertEqual("completed", e_override["status"], backend.name)


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


class ParentLeaseHeartbeatTests(unittest.TestCase):
    """Issue #607: `run_crew.py` blocks foreground on its single `launch(...)`
    seam and issues no mutating engine verb of its own during that block, so a
    healthy, merely-blocked parent's own ambient engine-session lease can go
    stale purely from being blocked. `_parent_lease_heartbeat()` is a
    context-managed daemon-thread helper, started around the blocking call in
    both `CliBackend.dispatch` and `CliBackend.resume`, that refreshes the
    DISPATCHING process's own `SPINE_FILE`/`SPINE_SESSION` lease for exactly
    the duration of the block when the child has a different pair. A shared
    child pair suppresses the redundant parent writer. These tests drive it
    directly and through the real call sites."""

    def _claimed_spine(self, root: Path, session_id: str, name: str = "parent_spine.json") -> Path:
        """A real `checklist_engine`-shaped spine with a lease actively claimed
        by `session_id` -- built through the engine's own `claim()`, not a
        hand-rolled dict, so this is the same shape a real Commander's own
        ambient spine has."""
        path = root / name
        cl = {
            "work_id": "w", "type": "gated", "items": [], "tasks": {},
            "consolidation": None, "triage_candidates": [], "blockers": [],
        }
        RC.checklist_engine.claim(cl, session_id, "commander", ".", {})
        RC.checklist_engine.save(path, cl)
        return path

    def _last_heartbeat(self, spine: Path) -> str:
        return json.loads(spine.read_text(encoding="utf-8"))["engine_session"]["last_heartbeat"]

    @staticmethod
    def _wait_until(predicate, *, timeout: float = 3.0, interval: float = 0.01) -> bool:
        """Poll `predicate` instead of a fixed sleep, so the test only proceeds
        once the background thread has actually done the thing, whatever the
        host's real scheduling speed -- a fixed sleep would either flake under
        load or waste time when the thread is fast. A transient exception is
        treated as "not yet", not a failure -- only a timeout is. That tolerance
        is now belt-and-braces: `checklist_engine.save` installs the spine by
        atomic rename (#613), so the predicate reading the SAME file the
        heartbeat thread is mid-write to sees the whole old document or the
        whole new one, never a torn one."""
        def _safe() -> bool:
            try:
                return bool(predicate())
            except (OSError, ValueError):
                return False

        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if _safe():
                return True
            time.sleep(interval)
        return _safe()

    def _heartbeat_thread_alive(self) -> bool:
        return any(t.name == RC._PARENT_HEARTBEAT_THREAD_NAME for t in threading.enumerate())

    # -- (a) no-op when ambient vars are unset ---------------------------- #
    def test_noop_when_ambient_vars_unset(self):
        with no_ambient_spine_env():
            with RC._parent_lease_heartbeat(interval=0.01):
                self.assertFalse(self._heartbeat_thread_alive())
            self.assertFalse(self._heartbeat_thread_alive())

    def test_noop_when_only_one_ambient_var_set(self):
        with no_ambient_spine_env():
            os.environ["SPINE_FILE"] = "/nonexistent/spine.json"
            try:
                with RC._parent_lease_heartbeat(interval=0.01):
                    self.assertFalse(self._heartbeat_thread_alive())
            finally:
                os.environ.pop("SPINE_FILE", None)

    # -- (b) thread starts and advances last_heartbeat --------------------- #
    def test_thread_advances_last_heartbeat_while_active(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            session = "constellation/w/commander"
            spine = self._claimed_spine(root, session)
            before = self._last_heartbeat(spine)
            with no_ambient_spine_env():
                os.environ["SPINE_FILE"] = str(spine)
                os.environ["SPINE_SESSION"] = session
                try:
                    with RC._parent_lease_heartbeat(interval=0.01):
                        self.assertTrue(self._heartbeat_thread_alive())
                        advanced = self._wait_until(
                            lambda: self._last_heartbeat(spine) != before
                        )
                finally:
                    os.environ.pop("SPINE_FILE", None)
                    os.environ.pop("SPINE_SESSION", None)
            self.assertTrue(advanced, "last_heartbeat never advanced while the thread ran")
            self.assertGreater(self._last_heartbeat(spine), before)

    def test_child_env_without_pair_keeps_parent_heartbeat(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            session = "constellation/w/commander"
            spine = self._claimed_spine(root, session)
            before = self._last_heartbeat(spine)
            with no_ambient_spine_env():
                os.environ["SPINE_FILE"] = str(spine)
                os.environ["SPINE_SESSION"] = session
                try:
                    with RC._parent_lease_heartbeat({}, interval=0.01):
                        self.assertTrue(self._wait_until(
                            lambda: self._last_heartbeat(spine) != before
                        ))
                finally:
                    os.environ.pop("SPINE_FILE", None)
                    os.environ.pop("SPINE_SESSION", None)

    # -- (c) thread stops (joined) before the context exits ---------------- #
    def test_thread_is_joined_before_context_manager_returns(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            session = "constellation/w/commander"
            spine = self._claimed_spine(root, session)
            with no_ambient_spine_env():
                os.environ["SPINE_FILE"] = str(spine)
                os.environ["SPINE_SESSION"] = session
                try:
                    with RC._parent_lease_heartbeat(interval=0.01):
                        self.assertTrue(self._heartbeat_thread_alive())
                    # `thread.join()` in the helper's `finally` already
                    # blocked until real thread death -- no sleep needed here.
                    self.assertFalse(self._heartbeat_thread_alive())
                finally:
                    os.environ.pop("SPINE_FILE", None)
                    os.environ.pop("SPINE_SESSION", None)

    # -- (d) a heartbeat exception never propagates/aborts ------------------ #
    def test_heartbeat_exception_is_swallowed_not_propagated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with no_ambient_spine_env():
                # points at a spine file that will NEVER exist: every tick's
                # `checklist_engine.load` raises FileNotFoundError.
                os.environ["SPINE_FILE"] = str(Path(tmp) / "does-not-exist.json")
                os.environ["SPINE_SESSION"] = "constellation/w/commander"
                try:
                    # must not raise, despite every tick failing
                    with RC._parent_lease_heartbeat(interval=0.01):
                        self._wait_until(lambda: False, timeout=0.1)  # let a few ticks fail
                finally:
                    os.environ.pop("SPINE_FILE", None)
                    os.environ.pop("SPINE_SESSION", None)
            # reaching here at all is the assertion: no exception propagated

    # -- (e) shared-spine dispatch: child inherits the SAME ambient pair,
    #        so the parent must not become a second writer ------------------ #
    def test_dispatch_skips_parent_heartbeat_in_shared_spine_case(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            session = "constellation/w/commander"
            spine = self._claimed_spine(root, session)
            before = self._last_heartbeat(spine)

            handoff = write_handoff(root, "w", "g1", "implementer")
            result = result_rel("w", "g1", "implementer")
            observed = {}

            def slow_launch(argv, *, stdin, env, stdout_path, stderr_path, cwd=None):
                # the child's env carries the SAME SPINE_FILE/SPINE_SESSION as
                # the parent -- exactly the no-self-collision-guard case.
                observed["env"] = env
                Path(stdout_path).parent.mkdir(parents=True, exist_ok=True)
                Path(stdout_path).write_text("out\n", encoding="utf-8")
                Path(stderr_path).write_text("err\n", encoding="utf-8")
                Path(root / result).parent.mkdir(parents=True, exist_ok=True)
                Path(root / result).write_text("RESULT\n", encoding="utf-8")
                self.assertFalse(self._heartbeat_thread_alive())
                return 0

            with no_ambient_spine_env():
                os.environ["SPINE_FILE"] = str(spine)
                os.environ["SPINE_SESSION"] = session
                saved_interval = RC.PARENT_HEARTBEAT_INTERVAL_SECONDS
                RC.PARENT_HEARTBEAT_INTERVAL_SECONDS = 0.01
                try:
                    code, entry = RC.launch_crew(
                        work_id="w", gate="g1", role="implementer",
                        handoff=handoff, result=result, spine=None,  # no explicit --spine
                        worktree=".", model="sonnet", launcher="claude", attempt=1,
                        root=root, entries=[], launch=slow_launch,
                        parent="test-parent",
                    )
                finally:
                    RC.PARENT_HEARTBEAT_INTERVAL_SECONDS = saved_interval
                    os.environ.pop("SPINE_FILE", None)
                    os.environ.pop("SPINE_SESSION", None)

            self.assertEqual(0, code)
            self.assertEqual("completed", entry["status"])
            # the child inherited the parent's OWN ambient pair unchanged
            self.assertEqual(str(spine), observed["env"]["SPINE_FILE"])
            self.assertEqual(session, observed["env"]["SPINE_SESSION"])
            # The child owns the shared pair for this call; the parent starts
            # no second writer against the same lease.
            self.assertEqual(self._last_heartbeat(spine), before)
            # the heartbeat thread does not outlive the (now-returned) dispatch
            self.assertFalse(self._heartbeat_thread_alive())

    # -- resume() is wired the same way as dispatch() ----------------------- #
    def test_resume_skips_parent_heartbeat_in_shared_spine_case(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            session = "constellation/w/commander"
            spine = self._claimed_spine(root, session)
            before = self._last_heartbeat(spine)

            handoff = write_handoff(root, "w", "g1", "implementer")
            result = result_rel("w", "g1", "implementer")
            crew_session = "constellation/w/g1/implementer/attempt-1"
            stdout, stderr = RC.run_log_paths("w", "g1", "implementer", 1, root)
            entries = [{
                "session_name": crew_session, "crew_id": crew_session,
                "work_id": "w", "gate": "g1", "role": "implementer", "attempt": 1,
                "worktree": ".", "status": "running", "abandoned": False,
                "handoff": handoff, "result": result,
                "stdout": RC._relativize(str(stdout), root),
                "stderr": RC._relativize(str(stderr), root),
            }]

            def slow_launch(argv, *, stdin, env, stdout_path, stderr_path, cwd=None):
                Path(stdout_path).parent.mkdir(parents=True, exist_ok=True)
                Path(stdout_path).write_text("out\n", encoding="utf-8")
                Path(stderr_path).write_text("err\n", encoding="utf-8")
                Path(root / result).parent.mkdir(parents=True, exist_ok=True)
                Path(root / result).write_text("RESULT\n", encoding="utf-8")
                self.assertFalse(self._heartbeat_thread_alive())
                return 0

            with no_ambient_spine_env():
                os.environ["SPINE_FILE"] = str(spine)
                os.environ["SPINE_SESSION"] = session
                saved_interval = RC.PARENT_HEARTBEAT_INTERVAL_SECONDS
                RC.PARENT_HEARTBEAT_INTERVAL_SECONDS = 0.01
                try:
                    code, entry = RC.CliBackend().resume(
                        crew_session, root=root, entries=entries, launch=slow_launch,
                    )
                finally:
                    RC.PARENT_HEARTBEAT_INTERVAL_SECONDS = saved_interval
                    os.environ.pop("SPINE_FILE", None)
                    os.environ.pop("SPINE_SESSION", None)

            self.assertEqual(0, code)
            self.assertEqual("completed", entry["status"])
            self.assertEqual(self._last_heartbeat(spine), before)
            self.assertFalse(self._heartbeat_thread_alive())

    def test_dispatch_heartbeats_parent_lease_when_child_pair_differs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            session = "constellation/w/commander"
            spine = self._claimed_spine(root, session)
            before = self._last_heartbeat(spine)
            handoff = write_handoff(root, "w", "g1", "implementer")
            result = result_rel("w", "g1", "implementer")

            def slow_launch(argv, *, stdin, env, stdout_path, stderr_path, cwd=None):
                self.assertNotEqual(str(spine), env["SPINE_FILE"])
                self.assertNotEqual(session, env["SPINE_SESSION"])
                Path(stdout_path).parent.mkdir(parents=True, exist_ok=True)
                Path(stdout_path).write_text("out\n", encoding="utf-8")
                Path(stderr_path).write_text("err\n", encoding="utf-8")
                Path(root / result).parent.mkdir(parents=True, exist_ok=True)
                Path(root / result).write_text("RESULT\n", encoding="utf-8")
                self.assertTrue(self._wait_until(lambda: self._last_heartbeat(spine) != before))
                return 0

            with no_ambient_spine_env():
                os.environ["SPINE_FILE"] = str(spine)
                os.environ["SPINE_SESSION"] = session
                saved_interval = RC.PARENT_HEARTBEAT_INTERVAL_SECONDS
                RC.PARENT_HEARTBEAT_INTERVAL_SECONDS = 0.01
                try:
                    code, entry = RC.launch_crew(
                        work_id="w", gate="g1", role="implementer", handoff=handoff,
                        result=result, spine="child_spine.json", worktree=".", model="sonnet",
                        launcher="claude", attempt=1, root=root, entries=[], launch=slow_launch,
                        parent="test-parent",
                    )
                finally:
                    RC.PARENT_HEARTBEAT_INTERVAL_SECONDS = saved_interval
                    os.environ.pop("SPINE_FILE", None)
                    os.environ.pop("SPINE_SESSION", None)

            self.assertEqual(0, code)
            self.assertEqual("completed", entry["status"])
            self.assertGreater(self._last_heartbeat(spine), before)
            self.assertFalse(self._heartbeat_thread_alive())


class ScratchDirPureFunctionTests(unittest.TestCase):
    """`scratch_dir()` (issue #525): a namespaced scratch/evidence directory
    keyed on the FULL `(work_id, gate, role, worktree, attempt)` tuple -- the
    SAME tuple `active_duplicate`/`next_attempt` use for duplicate-detection/
    attempt-numbering. `worktree` MUST stay in the key: `next_attempt` scopes
    attempt numbers PER WORKTREE, so two different worktrees dispatching the
    same work_id/gate/role can each independently reach attempt=1 -- an
    earlier draft of this plan omitted `worktree` from the key, which would
    let those two collide on the identical scratch directory, reintroducing
    #525 one field narrower. These tests pin that the field is actually load-
    bearing in the key, not just documented as such."""

    def test_path_shape_matches_gate_role_attempt_wtkey_convention(self):
        root = Path("/repo")
        path = RC.scratch_dir("issue-1", "g2", "implementer", ".", 3, root)
        wtkey = hashlib.sha256(".".encode("utf-8")).hexdigest()[:12]
        expected = root / ".agent-work" / "issue-1" / "crew-scratch" / f"g2-implementer-attempt-3-{wtkey}"
        self.assertEqual(expected, path)

    def test_different_gate_yields_disjoint_directory(self):
        root = Path("/repo")
        a = RC.scratch_dir("issue-1", "g1", "implementer", ".", 1, root)
        b = RC.scratch_dir("issue-1", "g2", "implementer", ".", 1, root)
        self.assertNotEqual(a, b)

    def test_different_role_yields_disjoint_directory(self):
        root = Path("/repo")
        a = RC.scratch_dir("issue-1", "g1", "implementer", ".", 1, root)
        b = RC.scratch_dir("issue-1", "g1", "reviewer", ".", 1, root)
        self.assertNotEqual(a, b)

    def test_different_attempt_yields_disjoint_directory(self):
        root = Path("/repo")
        a = RC.scratch_dir("issue-1", "g1", "implementer", ".", 1, root)
        b = RC.scratch_dir("issue-1", "g1", "implementer", ".", 2, root)
        self.assertNotEqual(a, b)

    def test_different_worktree_yields_disjoint_directory_at_the_same_attempt(self):
        # The exact regression this gate's Close Criteria calls out: two
        # DIFFERENT worktrees can each independently reach attempt=1 for the
        # SAME work_id/gate/role (next_attempt scopes attempt numbers PER
        # WORKTREE) -- omitting `worktree` from the key would collide these
        # two onto one directory, reintroducing #525 one field narrower.
        root = Path("/repo")
        a = RC.scratch_dir("issue-1", "g1", "implementer", "/tree-a", 1, root)
        b = RC.scratch_dir("issue-1", "g1", "implementer", "/tree-b", 1, root)
        self.assertNotEqual(a, b)

    def test_worktree_is_hashed_as_the_raw_string_not_resolved(self):
        # A relative "." and an absolute equivalent of the SAME repo root are
        # different RAW strings, so they must hash to DIFFERENT scratch
        # directories -- matching active_duplicate's/next_attempt's own raw-
        # string equality (`entry.get("worktree") == worktree`), not "fixing"
        # it into path-equivalence, which is out of scope for this gate.
        root = Path("/repo")
        a = RC.scratch_dir("issue-1", "g1", "implementer", ".", 1, root)
        b = RC.scratch_dir("issue-1", "g1", "implementer", str(root), 1, root)
        self.assertNotEqual(a, b)

    def test_same_tuple_is_deterministic_and_identical(self):
        root = Path("/repo")
        a = RC.scratch_dir("issue-1", "g1", "implementer", ".", 1, root)
        b = RC.scratch_dir("issue-1", "g1", "implementer", ".", 1, root)
        self.assertEqual(a, b)


class ScratchDirReservationTests(unittest.TestCase):
    """`CliBackend.dispatch` reserves this dispatch's own scratch directory
    (issue #525) before the crew is spawned: the directory exists on disk,
    the CLI-backend child's environment carries `CREW_SCRATCH_DIR` pointing
    at it, and the registry entry records it -- the collision-AVOIDANCE half
    of #525 (making a dispatched crew's own skill actually WRITE into it is a
    distinct, unowned follow-up, out of scope here)."""

    def test_dispatch_creates_the_reserved_directory_on_disk(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g2", "implementer")
            result = result_rel("issue-1", "g2", "implementer")
            with fake_launch(RC, 0, write_result_at=root / result):
                RC.launch_crew(
                    work_id="issue-1", gate="g2", role="implementer",
                    handoff=handoff, result=result, worktree=".",
                    model="sonnet", launcher="claude", attempt=1, root=root, entries=[],
                    parent="test-parent",
                )
            expected = RC.scratch_dir("issue-1", "g2", "implementer", ".", 1, root)
            self.assertTrue(expected.is_dir())

    def test_cli_backend_child_env_carries_crew_scratch_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g2", "implementer")
            result = result_rel("issue-1", "g2", "implementer")
            with fake_launch(RC, 0, write_result_at=root / result) as calls:
                RC.launch_crew(
                    work_id="issue-1", gate="g2", role="implementer",
                    handoff=handoff, result=result, worktree=".",
                    model="sonnet", launcher="claude", attempt=1, root=root, entries=[],
                    parent="test-parent",
                )
            expected = RC.scratch_dir("issue-1", "g2", "implementer", ".", 1, root)
            self.assertEqual(str(expected), calls[0]["env"]["CREW_SCRATCH_DIR"])

    def test_registry_entry_records_scratch_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g2", "implementer")
            result = result_rel("issue-1", "g2", "implementer")
            with fake_launch(RC, 0, write_result_at=root / result):
                _, entry = RC.launch_crew(
                    work_id="issue-1", gate="g2", role="implementer",
                    handoff=handoff, result=result, worktree=".",
                    model="sonnet", launcher="claude", attempt=1, root=root, entries=[],
                    parent="test-parent",
                )
            expected = RC.scratch_dir("issue-1", "g2", "implementer", ".", 1, root)
            self.assertEqual(RC._relativize(str(expected), root), entry["scratch_dir"])

    def test_before_after_two_crews_that_used_to_collide_now_write_disjoint_reserved_paths(self):
        # BEFORE this gate: run_crew.py reserved no scratch dir at all -- two
        # concurrent crews sharing one scratch/evidence area under generic
        # filenames (e.g. "r0.md", "r1.md"...) could silently collide (the
        # exact #525 failure: a g8 reviewer found r0-r6 finding-files an
        # EARLIER gate's reviewer had left behind, using the same generic
        # names it was about to use). The OLD, unreserved scheme gave both
        # crews below the identical generic scratch path regardless of which
        # gate/role/attempt/worktree dispatched them:
        old_scheme_path_for_implementer = "SHARED/scratch"
        old_scheme_path_for_reviewer = "SHARED/scratch"
        self.assertEqual(
            old_scheme_path_for_implementer, old_scheme_path_for_reviewer,
        )  # <-- the collision this gate exists to fix

        # AFTER this gate: two crews dispatched under DIFFERENT tuples (here:
        # different roles, same gate/worktree/attempt) each reserve their OWN
        # namespaced directory -- disjoint, not the shared generic path above.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff_a = write_handoff(root, "issue-1", "g2", "implementer")
            result_a = result_rel("issue-1", "g2", "implementer")
            handoff_b = write_handoff(root, "issue-1", "g2", "reviewer")
            result_b = result_rel("issue-1", "g2", "reviewer")
            entries: list[dict] = []
            with fake_launch(RC, 0, write_result_at=root / result_a):
                _, entry_a = RC.launch_crew(
                    work_id="issue-1", gate="g2", role="implementer",
                    handoff=handoff_a, result=result_a, worktree=".",
                    model="sonnet", launcher="claude", attempt=1, root=root, entries=entries,
                    parent="test-parent",
                )
            with fake_launch(RC, 0, write_result_at=root / result_b):
                _, entry_b = RC.launch_crew(
                    work_id="issue-1", gate="g2", role="reviewer",
                    handoff=handoff_b, result=result_b, worktree=".",
                    model="sonnet", launcher="claude", attempt=1, root=root, entries=entries,
                    parent="test-parent",
                )
            self.assertNotEqual(entry_a["scratch_dir"], entry_b["scratch_dir"])
            self.assertTrue((root / entry_a["scratch_dir"]).is_dir())
            self.assertTrue((root / entry_b["scratch_dir"]).is_dir())

    def test_disjoint_reserved_directories_for_same_gate_role_attempt_different_worktree(self):
        # The specific regression this gate's Close Criteria calls out: two
        # DIFFERENT worktrees dispatching the same work_id/gate/role can each
        # independently reach attempt=1 -- their RESERVED directories must
        # not collide.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tree_a = str(root / "tree-a")
            tree_b = str(root / "tree-b")
            handoff = write_handoff(root, "issue-1", "g2", "implementer")
            result = result_rel("issue-1", "g2", "implementer")
            entries: list[dict] = []
            with fake_launch(RC, 0, write_result_at=root / result):
                _, entry_a = RC.launch_crew(
                    work_id="issue-1", gate="g2", role="implementer",
                    handoff=handoff, result=result, worktree=tree_a,
                    model="sonnet", launcher="claude", attempt=1, root=root, entries=entries,
                    parent="test-parent",
                )
            with fake_launch(RC, 0, write_result_at=root / result):
                _, entry_b = RC.launch_crew(
                    work_id="issue-1", gate="g2", role="implementer",
                    handoff=handoff, result=result, worktree=tree_b,
                    model="sonnet", launcher="claude", attempt=1, root=root, entries=entries,
                    parent="test-parent",
                )
            self.assertNotEqual(entry_a["scratch_dir"], entry_b["scratch_dir"])
            self.assertTrue((root / entry_a["scratch_dir"]).is_dir())
            self.assertTrue((root / entry_b["scratch_dir"]).is_dir())


class ScratchDirCollisionTests(unittest.TestCase):
    """`decision:no-silent-truncation`: a genuine collision on the reserved
    scratch directory -- the SAME `(work_id, gate, role, worktree, attempt)`
    tuple reserved twice -- is a LOUD `CrewLaunchError`, never a silent
    overwrite and never a quiet reuse of a directory that was not this exact
    attempt's own (the exact failure mode #525 was filed over: "the file
    exists, it parses, it describes someone else's gate")."""

    def test_forced_collision_raises_crew_launch_error_naming_path_and_tuple(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g2", "implementer")
            result = result_rel("issue-1", "g2", "implementer")
            scratch = RC.scratch_dir("issue-1", "g2", "implementer", ".", 1, root)
            scratch.mkdir(parents=True)  # pre-existing reservation -- forces the collision
            with fake_launch(RC, 0, write_result_at=root / result) as calls:
                with self.assertRaises(RC.CrewLaunchError) as ctx:
                    RC.launch_crew(
                        work_id="issue-1", gate="g2", role="implementer",
                        handoff=handoff, result=result, worktree=".",
                        model="sonnet", launcher="claude", attempt=1, root=root, entries=[],
                        parent="test-parent",
                    )
            message = str(ctx.exception)
            self.assertIn(str(scratch), message)
            self.assertIn("work_id='issue-1'", message)
            self.assertIn("gate='g2'", message)
            self.assertIn("role='implementer'", message)
            self.assertIn("worktree='.'", message)
            self.assertIn("attempt=1", message)
            self.assertIn("#525", message)
            # never spawned -- the collision is refused before launch() runs
            self.assertEqual([], calls)

    def test_forced_collision_leaves_no_partial_registry_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g2", "implementer")
            result = result_rel("issue-1", "g2", "implementer")
            scratch = RC.scratch_dir("issue-1", "g2", "implementer", ".", 1, root)
            scratch.mkdir(parents=True)
            entries: list[dict] = []
            with fake_launch(RC, 0, write_result_at=root / result):
                with self.assertRaises(RC.CrewLaunchError):
                    RC.launch_crew(
                        work_id="issue-1", gate="g2", role="implementer",
                        handoff=handoff, result=result, worktree=".",
                        model="sonnet", launcher="claude", attempt=1, root=root, entries=entries,
                        parent="test-parent",
                    )
            self.assertEqual([], entries)
            self.assertFalse(RC.registry_path("issue-1", root).exists())

    def test_forced_collision_does_not_disturb_the_pre_existing_directorys_contents(self):
        # "the file exists, it parses, it describes someone else's gate" --
        # the exact failure mode #525 was filed over. A collision must never
        # overwrite whatever evidence is already sitting in the reserved
        # directory.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g2", "implementer")
            result = result_rel("issue-1", "g2", "implementer")
            scratch = RC.scratch_dir("issue-1", "g2", "implementer", ".", 1, root)
            scratch.mkdir(parents=True)
            sentinel = scratch / "someone-elses-evidence.md"
            sentinel.write_text("belongs to a different attempt\n", encoding="utf-8")
            with fake_launch(RC, 0, write_result_at=root / result):
                with self.assertRaises(RC.CrewLaunchError):
                    RC.launch_crew(
                        work_id="issue-1", gate="g2", role="implementer",
                        handoff=handoff, result=result, worktree=".",
                        model="sonnet", launcher="claude", attempt=1, root=root, entries=[],
                        parent="test-parent",
                    )
            self.assertEqual(
                "belongs to a different attempt\n", sentinel.read_text(encoding="utf-8"),
            )


class ScratchDirResumeTests(unittest.TestCase):
    """`CliBackend.resume` re-enters the SAME attempt as its original
    dispatch: it GETS the already-reserved scratch directory (recomputed via
    `scratch_dir()`, never re-reserved with `mkdir(exist_ok=False)`) -- an
    existing directory here is expected and correct, not a collision."""

    def test_resume_against_existing_directory_does_not_raise(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g2", "implementer")
            result = result_rel("issue-1", "g2", "implementer")
            entries: list[dict] = []
            with fake_launch(RC, 1):  # nonzero, no result written -> stays resumable
                RC.launch_crew(
                    work_id="issue-1", gate="g2", role="implementer",
                    handoff=handoff, result=result, worktree=".",
                    model="sonnet", launcher="claude", attempt=1, root=root, entries=entries,
                    parent="test-parent",
                )
            session = entries[0]["session_name"]
            with fake_launch(RC, 0, write_result_at=root / result):
                code, entry = RC.CliBackend().resume(session, root=root, entries=entries)
            # reaching here without a CrewLaunchError is the assertion this
            # test exists to make; the completion outcome is a sanity check.
            self.assertEqual(0, code)
            self.assertEqual("completed", entry["status"])

    def test_resume_env_carries_the_same_reserved_scratch_dir_as_original_dispatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g2", "implementer")
            result = result_rel("issue-1", "g2", "implementer")
            entries: list[dict] = []
            with fake_launch(RC, 1) as dispatch_calls:
                RC.launch_crew(
                    work_id="issue-1", gate="g2", role="implementer",
                    handoff=handoff, result=result, worktree=".",
                    model="sonnet", launcher="claude", attempt=1, root=root, entries=entries,
                    parent="test-parent",
                )
            dispatched_scratch = dispatch_calls[0]["env"]["CREW_SCRATCH_DIR"]
            session = entries[0]["session_name"]
            with fake_launch(RC, 0, write_result_at=root / result) as resume_calls:
                RC.CliBackend().resume(session, root=root, entries=entries)
            self.assertEqual(dispatched_scratch, resume_calls[0]["env"]["CREW_SCRATCH_DIR"])

    def test_resume_of_legacy_entry_without_worktree_key_does_not_crash_and_leaves_scratch_dir_unbound(self):
        # An entry recorded before `worktree` was threaded onto the registry
        # has no "worktree" key at all -- `crew_cwd()` already degrades to
        # `None` for this case (issue #568); `scratch_dir()` cannot recompute
        # a path with no worktree to hash, so this must degrade to "no
        # CREW_SCRATCH_DIR bound" rather than raise.
        #
        # #632: the assertion is about the value the LAUNCHER decided not to
        # bind, and `_crew_door_env` builds its env from `os.environ` -- so run
        # this with the variable cleared from the ambient process. Without that,
        # the test reds inside any dispatched crew (whose own
        # `CREW_SCRATCH_DIR` is set by the launcher that spawned it), on an
        # untouched base commit, measuring the runner's environment instead of
        # the code. The danger was never the red: it was a crew "fixing"
        # `run_crew.py` to silence a test that was not measuring its change.
        # Production behaviour is deliberately unchanged -- omitting a
        # scratch dir leaves the inherited route untouched (`_crew_door_env`).
        with mock.patch.dict(os.environ), tempfile.TemporaryDirectory() as tmp:
            os.environ.pop("CREW_SCRATCH_DIR", None)
            root = Path(tmp)
            handoff = write_handoff(root, "issue-1", "g2", "implementer")
            result = result_rel("issue-1", "g2", "implementer")
            session = "constellation/issue-1/g2/implementer/attempt-1"
            stdout, stderr = RC.run_log_paths("issue-1", "g2", "implementer", 1, root)
            entries = [{
                "session_name": session, "crew_id": session,
                "work_id": "issue-1", "gate": "g2", "role": "implementer", "attempt": 1,
                "status": "running", "abandoned": False,
                "handoff": handoff, "result": result,
                "stdout": RC._relativize(str(stdout), root),
                "stderr": RC._relativize(str(stderr), root),
            }]  # deliberately no "worktree" key
            RC.save_registry(RC.registry_path("issue-1", root), entries)
            with fake_launch(RC, 0, write_result_at=root / result) as calls:
                RC.CliBackend().resume(session, root=root, entries=entries)
            self.assertNotIn("CREW_SCRATCH_DIR", calls[0]["env"])


if __name__ == "__main__":
    unittest.main()
