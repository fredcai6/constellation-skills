"""Every committed path must be creatable on Windows.

Found the hard way: epic 569 wave 3 committed 40 files under a literal
`.agent-work/<work-id>/` directory -- the template placeholder, never
substituted -- and Windows checkout died before running a single test:

    error: invalid path '.agent-work/<work-id>/context/g0-corpus-survey.json'
    The process 'C:\\Program Files\\Git\\bin\\git.exe' failed with exit code 128

Nothing caught it. The Windows CI job that would have was already red for
unrelated reasons, so its verdict carried no information -- the epic's own
family-C shape. This test is the check that would have failed on day one.
"""
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Characters git refuses to check out on Windows, plus the shell-hostile ones.
WINDOWS_FORBIDDEN = set('<>:"|?*')


def _tracked_paths():
    out = subprocess.run(
        ["git", "ls-files", "-z"], cwd=str(ROOT),
        capture_output=True, text=True, encoding="utf-8", check=True,
    )
    return [p for p in out.stdout.split("\0") if p]


class CommittedPathsAreWindowsCheckoutable(unittest.TestCase):
    def test_no_tracked_path_uses_a_windows_forbidden_character(self):
        offenders = [
            p for p in _tracked_paths()
            if WINDOWS_FORBIDDEN & set(p)
        ]
        self.assertEqual(
            offenders, [],
            "these tracked paths cannot be checked out on Windows -- git fails "
            "the whole checkout with 'invalid path', before any test runs:\n  "
            + "\n  ".join(offenders),
        )

    def test_no_tracked_path_carries_an_unsubstituted_template_placeholder(self):
        """The specific shape that caused it: a `<placeholder>` that a template
        instantiation was supposed to replace and did not."""
        offenders = [p for p in _tracked_paths() if "<" in p and ">" in p]
        self.assertEqual(
            offenders, [],
            "these tracked paths contain an unsubstituted template placeholder:\n  "
            + "\n  ".join(offenders),
        )

    def test_the_guard_can_fail(self):
        """Red-proof: the predicate rejects the exact path that shipped."""
        planted = ".agent-work/<work-id>/context/g0-corpus-survey.json"
        self.assertTrue(WINDOWS_FORBIDDEN & set(planted))
        self.assertTrue("<" in planted and ">" in planted)


if __name__ == "__main__":
    unittest.main()
