"""Tests for the durable-root resolution helper and its wiring into the four
recursive-improvement scripts.

`durable_root(start)` returns the MAIN checkout root only when `start` sits inside
a LINKED git worktree; a plain checkout, a non-git dir, or any git error must
return `start` (or cwd) unchanged. The git-topology tests spin up a real
`git worktree add` in a tmpdir and skip cleanly when git is unavailable.
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GIT = shutil.which("git")


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _norm(p) -> str:
    return os.path.normcase(os.path.realpath(str(p)))


def _git(cwd, *args):
    subprocess.run(
        ["git", *args], cwd=str(cwd), check=True,
        capture_output=True, text=True, encoding="utf-8",
    )


def _init_repo(path: Path) -> None:
    """A git repo with one commit, so `git worktree add` has a valid HEAD."""
    _git(path, "init", "-q")
    (path / "seed.txt").write_text("seed\n", encoding="utf-8")
    _git(path, "add", "seed.txt")
    _git(
        path, "-c", "user.email=t@t", "-c", "user.name=t",
        "commit", "-q", "-m", "init",
    )


def _write_lease(main: Path, epic: str, *, status: str, claimed_by: str) -> Path:
    """Simulate an epic lease: `<main>/.agent-work/<epic>/spine.json` carrying an
    `engine_session` dict with the given status/claimed_by."""
    d = main / ".agent-work" / epic
    d.mkdir(parents=True, exist_ok=True)
    spine = d / "spine.json"
    spine.write_text(
        json.dumps(
            {
                "work_id": epic,
                "type": "gated",
                "engine_session": {"status": status, "claimed_by": claimed_by},
            }
        ),
        encoding="utf-8",
    )
    return spine


@unittest.skipUnless(GIT, "git not available on PATH")
class DurableRootGitTests(unittest.TestCase):
    def setUp(self):
        self.mod = _load("agent_work_root")
        self.tmp = tempfile.TemporaryDirectory()
        self.main = Path(self.tmp.name) / "main"
        self.main.mkdir()
        _init_repo(self.main)

    def tearDown(self):
        # Detach any worktrees before the tmpdir is removed.
        self.tmp.cleanup()

    def test_linked_worktree_resolves_to_main_checkout(self):
        linked = Path(self.tmp.name) / "linked"
        _git(self.main, "worktree", "add", "-q", str(linked))
        resolved = self.mod.durable_root(linked)
        self.assertEqual(_norm(resolved), _norm(self.main))

    def test_durable_agent_work_appends_agent_work(self):
        linked = Path(self.tmp.name) / "linked2"
        _git(self.main, "worktree", "add", "-q", str(linked))
        resolved = self.mod.durable_agent_work(linked)
        self.assertEqual(_norm(resolved), _norm(self.main / ".agent-work"))

    def test_plain_checkout_unchanged(self):
        resolved = self.mod.durable_root(self.main)
        self.assertEqual(_norm(resolved), _norm(self.main))


@unittest.skipUnless(GIT, "git not available on PATH")
class DurableRootEpicLeaseTests(unittest.TestCase):
    """Under an ACTIVE Admiral epic lease in the main checkout, `durable_root`
    honors the linked worktree (its normal fallback) instead of redirecting to the
    fenced main checkout. Any other lease state leaves the redirect unchanged, and
    the lease scan never raises."""

    def setUp(self):
        self.mod = _load("agent_work_root")
        self.tmp = tempfile.TemporaryDirectory()
        self.main = Path(self.tmp.name) / "main"
        self.main.mkdir()
        _init_repo(self.main)
        self.linked = Path(self.tmp.name) / "linked"
        _git(self.main, "worktree", "add", "-q", str(self.linked))

    def tearDown(self):
        self.tmp.cleanup()

    def test_active_admiral_lease_resolves_to_worktree(self):
        _write_lease(self.main, "epic-198-burndown", status="active", claimed_by="admiral")
        resolved = self.mod.durable_root(self.linked)
        self.assertEqual(_norm(resolved), _norm(self.linked))

    def test_active_explorer_lease_resolves_to_main(self):
        # claimed_by filter: an active EXPLORER lease is not an epic lease.
        _write_lease(self.main, "explore-shared-understanding", status="active", claimed_by="explorer")
        resolved = self.mod.durable_root(self.linked)
        self.assertEqual(_norm(resolved), _norm(self.main))

    def test_released_admiral_lease_resolves_to_main(self):
        # status filter: a released admiral lease is not active.
        _write_lease(self.main, "epic-old", status="released", claimed_by="admiral")
        resolved = self.mod.durable_root(self.linked)
        self.assertEqual(_norm(resolved), _norm(self.main))

    def test_no_lease_resolves_to_main(self):
        # `.agent-work` present but holding no spine lease -> unchanged (main).
        (self.main / ".agent-work").mkdir()
        resolved = self.mod.durable_root(self.linked)
        self.assertEqual(_norm(resolved), _norm(self.main))

    def test_malformed_spine_does_not_raise_and_resolves_to_main(self):
        bad = self.main / ".agent-work" / "epic-bad"
        bad.mkdir(parents=True)
        (bad / "spine.json").write_text("{ not valid json", encoding="utf-8")
        resolved = self.mod.durable_root(self.linked)  # must NOT raise
        self.assertEqual(_norm(resolved), _norm(self.main))

    # PRUNED (#447 g4): test_verify_agent_feedback_resolves_to_worktree_under_lease
    # loaded scripts/verify_agent_feedback.py, which this retirement deleted. The
    # durable_root() behaviour it exercised — an active admiral lease resolving to the
    # writable worktree — is still covered by the sibling lease tests in this class; only
    # the deleted verifier's use of it went away.


class DurableRootFallbackTests(unittest.TestCase):
    def setUp(self):
        self.mod = _load("agent_work_root")
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_non_git_dir_unchanged(self):
        d = Path(self.tmp.name)
        resolved = self.mod.durable_root(d)
        self.assertEqual(_norm(resolved), _norm(d))

    def test_nonexistent_start_returns_verbatim(self):
        missing = Path(self.tmp.name) / "does-not-exist"
        # subprocess cwd error -> visible fallback to the given start, no raise.
        self.assertEqual(self.mod.durable_root(missing), missing)

    def test_git_rev_parse_failure_falls_back(self):
        d = Path(self.tmp.name)

        def boom(*a, **k):
            raise RuntimeError("git rev-parse failed")

        self.mod._git_rev_parse = boom  # force the git-error branch
        self.assertEqual(self.mod.durable_root(d), d)

    def test_no_start_returns_cwd(self):
        # With no argument and a non-git cwd, returns cwd unchanged.
        cwd = Path.cwd()
        old = os.getcwd()
        os.chdir(self.tmp.name)
        try:
            resolved = self.mod.durable_root()
        finally:
            os.chdir(old)
        self.assertEqual(_norm(resolved), _norm(self.tmp.name))
        self.assertEqual(_norm(cwd), _norm(old))


class WiringExplicitWinsTests(unittest.TestCase):
    """Explicit path args must ALWAYS win; the durable helper is consulted only
    for the default. Each test poisons the module's `durable_root` so that if a
    script consulted it for an explicitly-supplied path, the test would fail.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    @staticmethod
    def _poison(module):
        def boom(start=None):
            raise AssertionError("durable_root consulted for an explicit path arg")
        module.durable_root = boom

    # PRUNED (#447 g4): test_apply_lessons_delta_explicit_file_wins,
    # test_verify_lessons_applied_explicit_file_wins and
    # test_verify_agent_feedback_explicit_root_wins_for_both each loaded a script this
    # retirement deleted (apply_lessons_delta.py, verify_lessons_applied.py,
    # verify_agent_feedback.py). The explicit-path-wins contract itself is unchanged and
    # still asserted below for collect_feedback, which survives.

    def test_collect_feedback_explicit_inbox_wins(self):
        collect = _load("collect_feedback")
        # collect() legitimately resolves the project ROOT via durable_root; that is
        # not the inbox default. Stub it to identity so root resolution is a no-op,
        # then prove the explicit --inbox path wins over the cwd default.
        collect.durable_root = lambda start=None: Path(start) if start is not None else Path.cwd()
        (self.dir / ".agent-work").mkdir(parents=True)
        (self.dir / ".agent-work" / "CONSTELLATION_FEEDBACK.md").write_text(
            "## epic\n### Lesson: some-finding\n"
            "**Observed:** a thing. **Upstream fix:** fix it.\n",
            encoding="utf-8",
        )
        explicit = self.dir / "explicit" / "INBOX.json"
        default_cwd_inbox = self.dir / ".agent-work" / "CONSTELLATION_INBOX.json"
        old = os.getcwd()
        os.chdir(self.dir)
        try:
            rc = collect.main(
                [str(self.dir), "--file-issues", "--include-singles", "--confirm",
                 "--inbox", str(explicit)],
                filer=lambda *a, **k: {"number": "1", "url": "u"},
                commenter=lambda *a, **k: {},
            )
        finally:
            os.chdir(old)
        self.assertEqual(0, rc)
        self.assertTrue(explicit.is_file())            # explicit ledger written
        self.assertFalse(default_cwd_inbox.is_file())  # default NOT used


class WiringDefaultResolutionTests(unittest.TestCase):
    """When the explicit arg is omitted, the default path is computed through
    `durable_root`. Each test stubs the module's `durable_root` to a tmpdir and
    asserts the script reads/writes under `<tmpdir>/.agent-work`.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _stub(self, module):
        root = self.dir
        module.durable_root = lambda start=None: root

    # PRUNED (#447 g4): test_apply_lessons_delta_default_uses_durable_root,
    # test_verify_lessons_applied_default_uses_durable_root and
    # test_verify_agent_feedback_default_durable_split each loaded a script this
    # retirement deleted. The default-resolves-through-durable_root contract is unchanged
    # and still asserted below for collect_feedback, which survives.

    def test_collect_feedback_default_inbox_uses_durable_root(self):
        collect = _load("collect_feedback")
        self._stub(collect)
        # Export one finding under the stubbed durable root so the sweep sees it,
        # then file with default inbox -> ledger lands under durable .agent-work.
        aw = self.dir / ".agent-work"
        aw.mkdir(parents=True)
        (aw / "CONSTELLATION_FEEDBACK.md").write_text(
            "## epic\n### Lesson: some-finding\n"
            "**Observed:** a thing. **Upstream fix:** fix it.\n",
            encoding="utf-8",
        )
        old = os.getcwd()
        os.chdir(self.dir)
        try:
            rc = collect.main(
                [str(self.dir), "--file-issues", "--include-singles", "--confirm"],
                filer=lambda *a, **k: {"number": "7", "url": "http://x/7"},
                commenter=lambda *a, **k: {},
            )
        finally:
            os.chdir(old)
        self.assertEqual(0, rc)
        self.assertTrue((aw / "CONSTELLATION_INBOX.json").is_file())


if __name__ == "__main__":
    unittest.main()
