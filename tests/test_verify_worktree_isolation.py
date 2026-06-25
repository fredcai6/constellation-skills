import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PORCELAIN = """worktree C:/Programs/main
HEAD abc123
branch refs/heads/main

worktree C:/Programs/wt/c1
HEAD def456
branch refs/heads/issue-33-c1

worktree C:/Programs/wt/c2
HEAD 789abc
detached
"""


class NormalizeTests(unittest.TestCase):
    def setUp(self):
        self.m = load("verify_worktree_isolation")

    def test_separator_and_case_fold_equal_on_windows(self):
        a = self.m.normalize_path("C:/Programs/Constellation")
        b = self.m.normalize_path("C:\\Programs\\constellation")
        if os.name == "nt":
            self.assertEqual(a, b)
        else:
            # POSIX is case- and separator-sensitive; assert idempotence instead.
            self.assertEqual(a, self.m.normalize_path(a))

    def test_dot_segments_folded(self):
        with tempfile.TemporaryDirectory() as tmp:
            direct = self.m.normalize_path(tmp)
            dotted = self.m.normalize_path(os.path.join(tmp, "sub", ".."))
            self.assertEqual(direct, dotted)

    def test_symlink_or_junction_resolved(self):
        # realpath must resolve a link to its real target; skip where links
        # cannot be created (Windows without privilege / developer mode).
        with tempfile.TemporaryDirectory() as tmp:
            target = os.path.join(tmp, "target")
            link = os.path.join(tmp, "link")
            os.mkdir(target)
            try:
                os.symlink(target, link, target_is_directory=True)
            except (OSError, NotImplementedError, ValueError):
                self.skipTest("symlink creation not permitted on this platform")
            self.assertEqual(
                self.m.normalize_path(link), self.m.normalize_path(target)
            )


class ParseTests(unittest.TestCase):
    def setUp(self):
        self.m = load("verify_worktree_isolation")

    def test_extracts_only_worktree_paths(self):
        self.assertEqual(
            self.m.parse_worktree_list(PORCELAIN),
            ["C:/Programs/main", "C:/Programs/wt/c1", "C:/Programs/wt/c2"],
        )

    def test_empty_input_is_empty_list(self):
        self.assertEqual(self.m.parse_worktree_list(""), [])


class CheckDistinctRealTests(unittest.TestCase):
    def setUp(self):
        self.m = load("verify_worktree_isolation")
        self.registered = ["/repo/main", "/repo/wt/c1", "/repo/wt/c2"]
        self.primary = "/repo/main"

    def test_distinct_registered_nonprimary_pass(self):
        ok, reason = self.m.check_distinct_real(
            ["/repo/wt/c1", "/repo/wt/c2"], self.registered, self.primary
        )
        self.assertTrue(ok, reason)
        self.assertEqual(reason, "")

    def test_unregistered_path_fails(self):
        ok, reason = self.m.check_distinct_real(
            ["/repo/wt/ghost"], self.registered, self.primary
        )
        self.assertFalse(ok)
        self.assertIn("ghost", reason)
        self.assertIn("not a registered", reason)

    def test_primary_checkout_rejected(self):
        ok, reason = self.m.check_distinct_real(
            ["/repo/main"], self.registered, self.primary
        )
        self.assertFalse(ok)
        self.assertIn("main checkout", reason)

    def test_duplicate_provisioned_paths_fail(self):
        ok, reason = self.m.check_distinct_real(
            ["/repo/wt/c1", "/repo/wt/c1"], self.registered, self.primary
        )
        self.assertFalse(ok)
        self.assertIn("same worktree", reason)


class CheckHereTests(unittest.TestCase):
    def setUp(self):
        self.m = load("verify_worktree_isolation")

    def test_match_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            ok, reason = self.m.check_here(tmp, tmp)
            self.assertTrue(ok, reason)

    def test_mismatch_names_both(self):
        ok, reason = self.m.check_here("/repo/main", "/repo/wt/c1")
        self.assertFalse(ok)
        self.assertIn("/repo/main", reason)
        self.assertIn("/repo/wt/c1", reason)


HAS_GIT = shutil.which("git") is not None


@unittest.skipUnless(HAS_GIT, "git not available")
class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.m = load("verify_worktree_isolation")
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        self._git("init", "-q")
        self._git(
            "-c", "user.email=t@t", "-c", "user.name=t",
            "commit", "-q", "--allow-empty", "-m", "init",
        )
        self.wt = Path(self.tmp.name) / "wt-c1"
        self._git("worktree", "add", "-q", "-b", "issue-33-c1", str(self.wt))
        self._cwd = os.getcwd()

    def tearDown(self):
        os.chdir(self._cwd)
        self.tmp.cleanup()

    def _git(self, *args):
        subprocess.run(
            ["git", "-C", str(self.repo), *args],
            check=True, capture_output=True, text=True,
        )

    def test_gate_passes_for_real_worktree(self):
        os.chdir(self.repo)
        self.assertEqual(self.m.main([str(self.wt)]), 0)

    def test_gate_rejects_main_checkout(self):
        os.chdir(self.repo)
        self.assertEqual(self.m.main([str(self.repo)]), 1)

    def test_gate_rejects_missing_path(self):
        os.chdir(self.repo)
        self.assertEqual(self.m.main([str(self.repo / "does-not-exist")]), 1)

    def test_here_passes_from_inside_worktree(self):
        os.chdir(self.wt)
        self.assertEqual(self.m.main(["--here", str(self.wt)]), 0)

    def test_here_fails_from_main_checkout(self):
        os.chdir(self.repo)
        self.assertEqual(self.m.main(["--here", str(self.wt)]), 1)


if __name__ == "__main__":
    unittest.main()
