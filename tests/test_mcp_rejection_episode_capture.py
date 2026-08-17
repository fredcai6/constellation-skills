"""Unit-level tests for the door-own rejection -> `episodes/` capture path
(issue #541, epic #567 lane E).

`_log_rejection` already writes one JSONL line per door-own rejection to a local
sidecar; `_capture_refusal_episode` (called first, from inside `_log_rejection`) adds
a SECOND side effect: a real episode written into a tracked `episodes/` store via
`scripts/apply_episode_delta.py`, so a refusal survives worktree teardown instead of
living only in a gitignored file.

Mock/fixture-based by design (the handoff's Test Mode: "mock/fixture-based is fine
for these; the fresh-process trigger [...] is the separate, additional acceptance
proof, not a substitute"). Every test here calls the module's internal functions
directly, in-process, against a throwaway git checkout -- never the real repo's own
`episodes/`. The genuinely-fresh-subprocess acceptance proof (a real refusal, a real
capture, read back with `query_episodes.py`, plus a negative control) lives outside
pytest, in the g1-implementer-result evidence, per that same Test Mode note.

Harness mirrors `tests/test_mcp_spine_bind.py::_load_module`: a FRESH server module
per test (module-level `SPINE`/`SESSION`/`_CAPTURED_REJECTIONS` would otherwise leak
across tests sharing one cached import), bound to a real throwaway git repo so
`_own_checkout_for_binding()` (`git rev-parse --show-toplevel`) has something real to
resolve, with `episodes/` landing under that throwaway repo, never this one's.
"""

from __future__ import annotations

import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "scripts" / "mcp_spine_server.py"
ENGINE = ROOT / "scripts" / "checklist_engine.py"

HAS_GIT = shutil.which("git") is not None
requires_git = pytest.mark.skipif(not HAS_GIT, reason="git not available")


def _init_repo(path: Path) -> None:
    subprocess.run(["git", "init", "-q", "-b", "main", str(path)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(path), "-c", "user.email=t@t", "-c", "user.name=t",
         "commit", "-q", "--allow-empty", "-m", "init"],
        check=True, capture_output=True,
    )


def _load_module(spine: Path | None, *, session: str = "constellation/test-run/x"):
    """A fresh server module, bound to `spine` (or unbound when `spine` is None).

    Same reasoning as `test_mcp_spine_bind.py::_load_module`: `_capture_refusal_episode`
    reads module-level `SPINE`, and a cached import would carry one test's binding
    (and its `_CAPTURED_REJECTIONS` dedup set) into the next.
    """
    env_patch = {
        "SPINE_ENGINE": str(ENGINE),
        "SPINE_SESSION": session,
        "SPINE_PARENT": "unknown",
    }
    if spine is None:
        env_patch["SPINE_FILE"] = ""
    else:
        spine.parent.mkdir(parents=True, exist_ok=True)
        env_patch["SPINE_FILE"] = str(spine)
        env_patch["SPINE_CALLLOG"] = str(spine.parent / "calls.jsonl")
        env_patch["SPINE_START_MARKER"] = str(spine.parent / "started")
        env_patch["SPINE_REJECTION_LOG"] = str(spine.parent / "rejections.jsonl")
    saved = {k: os.environ.get(k) for k in env_patch}
    os.environ.update(env_patch)
    try:
        spec = importlib.util.spec_from_file_location(
            f"_rejection_capture_door_{abs(hash((str(spine), session))) % 1000000}", SERVER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        for key, value in saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _spine_payload(work_id: str = "test-run") -> dict:
    return {
        "work_id": work_id,
        "type": "gated",
        "items": ["g1"],
        "tasks": {"g1": {"status": "pending", "title": "t"}},
        "engine_session": {"claimed_by": "implementer"},
        "refusals": 0,
    }


def _write_spine(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


COMPLETE_FIELDS = {
    "run": "test-run",
    "project": "throwaway",
    "role": "implementer",
    "spine-step": "g1",
    "context-manifest-ref": "ctx-test-run-g1@deadbeef",
    "refusals": 0,
    "reopens": 0,
    "rework-count": 0,
    "failed-commands": 0,
}


class _CaptureHarness(unittest.TestCase):
    """Common repo+spine scaffolding, torn down after every test."""

    def setUp(self):
        if not HAS_GIT:
            self.skipTest("git not available")
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _init_repo(self.repo)
        self.spine_path = self.repo / ".agent-work" / "test-run" / "spine.json"
        _write_spine(self.spine_path, _spine_payload())
        self.mod = _load_module(self.spine_path)

    def tearDown(self):
        self._tmp.cleanup()

    def episodes_dir(self) -> Path:
        return self.repo / "episodes" / "active"

    def episode_files(self) -> list[Path]:
        d = self.episodes_dir()
        return sorted(d.glob("*.md")) if d.exists() else []


@requires_git
class UnboundDoorSkipsCleanlyTests(unittest.TestCase):
    """No `SPINE_FILE` -> no work-id to attribute an episode to. Skipped, not failed."""

    def test_no_spine_no_episode_no_crash(self):
        mod = _load_module(None)
        self.assertIsNone(mod.SPINE)
        # Must not raise, and must not touch _CAPTURED_REJECTIONS (nothing to dedup
        # against -- the SPINE-None check returns before the dedup set is touched).
        mod._capture_refusal_episode("spine_bind", "path-escape", "REFUSED: outside.")
        self.assertEqual(mod._CAPTURED_REJECTIONS, set())


@requires_git
class CompleteMechanicalFieldsWritesRealEpisodeTests(_CaptureHarness):
    """The full happy path: a complete mechanical bin -> one real episode file,
    with all five agent-supplied assertions and all nine mechanical fields."""

    def test_capture_writes_one_episode_with_all_fields(self):
        self.mod.episode_capture.mechanical_fields = lambda checklist, base_dir: dict(COMPLETE_FIELDS)

        message = (
            "REFUSED: this door may only bind a spine inside its own work area. "
            "One checkout's work-area tree per process. Name a spine under that work area."
        )
        self.mod._capture_refusal_episode("spine_bind", "path-escape", message)

        files = self.episode_files()
        self.assertEqual(len(files), 1, f"expected exactly one episode, found {files}")
        text = files[0].read_text(encoding="utf-8")

        # Mechanical block: all nine scalar fields present.
        for field in self.mod.apply_episode_delta.MECHANICAL_SCALAR_FIELDS:
            self.assertIn(f"- {field}:", text, f"missing mechanical field {field!r} in:\n{text}")

        # Five agent-supplied assertions, literal derivations.
        self.assertIn("Called `spine_bind` through the MCP door.", text)
        self.assertIn(self.mod._tool_description("spine_bind"), text)
        self.assertIn("REFUSED: this door may only bind a spine", text)
        self.assertIn("returned REFUSED before it reached the engine", text)
        self.assertIn("Name a spine under that work area.", text)  # extracted workaround

    def test_dedup_same_key_writes_only_one_episode(self):
        self.mod.episode_capture.mechanical_fields = lambda checklist, base_dir: dict(COMPLETE_FIELDS)
        message = "REFUSED: same shape twice. Try again differently."
        self.mod._capture_refusal_episode("spine_bind", "path-escape", message)
        self.mod._capture_refusal_episode("spine_bind", "path-escape", message)
        self.assertEqual(len(self.episode_files()), 1)

    def test_distinct_keys_write_two_episodes(self):
        self.mod.episode_capture.mechanical_fields = lambda checklist, base_dir: dict(COMPLETE_FIELDS)
        self.mod._capture_refusal_episode("spine_bind", "path-escape", "REFUSED: A. See B.")
        self.mod._capture_refusal_episode("spine_bind", "cross-checkout", "REFUSED: C. See D.")
        self.assertEqual(len(self.episode_files()), 2)


@requires_git
class IncompleteMechanicalFieldsSkipsCleanlyTests(_CaptureHarness):
    """Refuse rather than fabricate: a mechanical bin missing even one of the nine
    required fields skips capture entirely -- no delta, no subprocess call."""

    def test_missing_field_skips_and_reports_which(self):
        incomplete = dict(COMPLETE_FIELDS)
        del incomplete["reopens"]
        self.mod.episode_capture.mechanical_fields = lambda checklist, base_dir: incomplete

        def _must_not_be_called(*a, **k):
            raise AssertionError("apply_episode_delta.py must not be invoked when a field is missing")

        stderr = io.StringIO()
        with unittest.mock.patch.object(self.mod.subprocess, "run", side_effect=_must_not_be_called), \
             unittest.mock.patch.object(self.mod.sys, "stderr", stderr):
            self.mod._capture_refusal_episode("spine_bind", "path-escape", "REFUSED: message.")

        self.assertEqual(self.episode_files(), [])
        self.assertIn("reopens", stderr.getvalue())
        self.assertIn("SKIPPED", stderr.getvalue())


@requires_git
class UnknownToolSkipsCleanlyTests(_CaptureHarness):
    """A tool with no `TOOLS` entry has nothing honest to quote for
    `expected-behavior` -- capture is skipped rather than inventing one."""

    def test_unknown_tool_skips(self):
        self.mod.episode_capture.mechanical_fields = lambda checklist, base_dir: dict(COMPLETE_FIELDS)
        self.mod._capture_refusal_episode("not_a_real_tool", "missing-required-argument", "REFUSED: x.")
        self.assertEqual(self.episode_files(), [])


@requires_git
class SubprocessFailureNeverCrashesTests(_CaptureHarness):
    """`apply_episode_delta.py` failing -- a non-zero exit, or an OSError launching
    it at all -- must reach `stderr`, never raise past the caller."""

    def _run_passthrough_except_writer(self, *, on_writer_call):
        """Real `subprocess.run` for every call EXCEPT the one launching
        `apply_episode_delta.py` -- `_own_checkout_for_binding()` (git rev-parse)
        runs through this same `subprocess.run` first and must see the real thing,
        or the failure this test means to exercise never gets reached at all."""
        real_run = subprocess.run

        def _dispatch(*a, **k):
            argv = a[0] if a else k.get("args")
            if argv and any("apply_episode_delta.py" in str(part) for part in argv):
                return on_writer_call(*a, **k)
            return real_run(*a, **k)

        return _dispatch

    def test_nonzero_exit_reported_not_raised(self):
        self.mod.episode_capture.mechanical_fields = lambda checklist, base_dir: dict(COMPLETE_FIELDS)

        class _FakeCompleted:
            returncode = 1
            stdout = ""
            stderr = "error: delta rejected\n"

        dispatch = self._run_passthrough_except_writer(on_writer_call=lambda *a, **k: _FakeCompleted())

        stderr = io.StringIO()
        with unittest.mock.patch.object(self.mod.subprocess, "run", side_effect=dispatch), \
             unittest.mock.patch.object(self.mod.sys, "stderr", stderr):
            self.mod._capture_refusal_episode("spine_bind", "path-escape", "REFUSED: x.")

        self.assertEqual(self.episode_files(), [])
        self.assertIn("FAILED", stderr.getvalue())

    def test_oserror_launching_subprocess_reported_not_raised(self):
        self.mod.episode_capture.mechanical_fields = lambda checklist, base_dir: dict(COMPLETE_FIELDS)

        def _boom(*a, **k):
            raise OSError("no such file or directory: apply_episode_delta.py")

        dispatch = self._run_passthrough_except_writer(on_writer_call=_boom)

        stderr = io.StringIO()
        with unittest.mock.patch.object(self.mod.subprocess, "run", side_effect=dispatch), \
             unittest.mock.patch.object(self.mod.sys, "stderr", stderr):
            self.mod._capture_refusal_episode("spine_bind", "path-escape", "REFUSED: x.")

        self.assertEqual(self.episode_files(), [])
        self.assertIn("FAILED", stderr.getvalue())

    def test_bug_in_capture_path_still_never_reaches_log_rejection_caller(self):
        """The outer guard in `_log_rejection` (broad `except Exception`, on top of
        `_capture_refusal_episode`'s own narrower guards) is the final net: even a
        capture-internal bug that none of the narrow catches anticipated must not
        propagate out of `_log_rejection` -- the choke-point `_tool_error` calls."""
        def _raise(*a, **k):
            raise RuntimeError("unanticipated bug inside the capture path")

        self.mod._capture_refusal_episode = _raise
        # Must not raise: _log_rejection wraps the call in its own broad except.
        self.mod._log_rejection("spine_bind", "path-escape", "REFUSED: x.")


class WorkaroundExtractionTests(unittest.TestCase):
    """`_episode_workaround` is a pure function: last sentence, or 'none'."""

    def setUp(self):
        if not HAS_GIT:
            self.skipTest("git not available")
        self.mod = _load_module(None)

    def test_multi_sentence_extracts_last(self):
        message = "REFUSED: first thing happened. Second thing too. Do this instead."
        self.assertEqual(self.mod._episode_workaround(message), "Do this instead.")

    def test_single_sentence_yields_none(self):
        message = "REFUSED: no sentence boundary anywhere in this message"
        self.assertEqual(self.mod._episode_workaround(message), "none")

    def test_the_replaced_refusal_tail_is_a_single_sentence(self):
        """Pins m1's design constraint: `_THE_CLI_IS_PER_CALL` must stay ONE
        sentence (no internal '. ' boundary) so the extraction above lands on
        the whole text rather than silently truncating it."""
        tail = self.mod._THE_CLI_IS_PER_CALL
        self.assertEqual(len(tail.split(". ")), 1, f"tail must be one sentence: {tail!r}")
        self.assertNotIn("per-call by construction", tail)


class ToolDescriptionLookupTests(unittest.TestCase):
    def setUp(self):
        if not HAS_GIT:
            self.skipTest("git not available")
        self.mod = _load_module(None)

    def test_known_tool_returns_its_registered_description(self):
        desc = self.mod._tool_description("spine_bind")
        self.assertIsInstance(desc, str)
        self.assertTrue(desc)
        expected = next(t["description"] for t in self.mod.TOOLS if t["name"] == "spine_bind")
        self.assertEqual(desc, expected)

    def test_unknown_tool_returns_none(self):
        self.assertIsNone(self.mod._tool_description("nonexistent_tool_xyz"))


if __name__ == "__main__":
    unittest.main()
