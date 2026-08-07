import importlib.util
import io
import json
import sys
import contextlib
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_corpus_freshness.py"


_CHECKER_MODULE = None


def load_checker():
    # Memoized: a fresh exec each call would mint a distinct FreshnessError class,
    # so a FakeRemote raising one module's error would slip past another module's
    # `except FreshnessError`.
    global _CHECKER_MODULE
    if _CHECKER_MODULE is None:
        spec = importlib.util.spec_from_file_location("check_corpus_freshness", CHECKER)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        _CHECKER_MODULE = module
    return _CHECKER_MODULE


class FakeRemote:
    """Stands in for GitHubRemote — same two methods, zero network."""

    branch = "main"

    def __init__(self, head, compare_result=None, head_error=None, compare_error=None):
        self._head = head
        self._compare = compare_result
        self._head_error = head_error
        self._compare_error = compare_error

    def head_commit(self):
        if self._head_error:
            raise self._head_error
        return self._head

    def compare(self, base, head):
        if self._compare_error:
            raise self._compare_error
        return self._compare


def write_marker(tmp: Path, source_commit) -> Path:
    root = tmp / "skills"
    root.mkdir()
    marker = {"corpus_id": "sha256:abc", "date": "2026-07-10"}
    if source_commit is not None:
        marker["source_commit"] = source_commit
    (root / "CORPUS.json").write_text(json.dumps(marker) + "\n", encoding="utf-8")
    return root


class CorpusFreshnessTests(unittest.TestCase):
    def _run(self, root: Path, remote):
        checker = load_checker()
        buf_out, buf_err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
            code = checker.main(["--skills-root", str(root)], remote=remote)
        return code, buf_out.getvalue(), buf_err.getvalue()

    def test_current_exits_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_marker(Path(tmp), "deadbeef" * 5)
            remote = FakeRemote(head="deadbeef" * 5)
            code, out, _ = self._run(root, remote)
            self.assertEqual(0, code)
            self.assertIn("current", out)

    def test_behind_exits_one_with_count_and_subjects(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_marker(Path(tmp), "0" * 40)
            remote = FakeRemote(
                head="f" * 40,
                compare_result={
                    "ahead_by": 2,
                    "commits": [
                        {"sha": "a" * 40, "commit": {"message": "feat: one\n\nbody"}},
                        {"sha": "b" * 40, "commit": {"message": "fix: two"}},
                    ],
                },
            )
            code, out, _ = self._run(root, remote)
            self.assertEqual(1, code)
            self.assertIn("behind", out)
            self.assertIn("2 commit(s) behind", out)
            self.assertIn("feat: one", out)
            self.assertIn("fix: two", out)
            # only the subject line, never the body
            self.assertNotIn("body", out)

    def test_unknown_source_commit_is_cannot_determine(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_marker(Path(tmp), "unknown")
            code, _, err = self._run(root, FakeRemote(head="f" * 40))
            self.assertEqual(2, code)
            self.assertIn("cannot-determine", err)

    def test_missing_source_commit_is_cannot_determine(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_marker(Path(tmp), None)
            code, _, err = self._run(root, FakeRemote(head="f" * 40))
            self.assertEqual(2, code)
            self.assertIn("cannot-determine", err)

    def test_missing_marker_is_cannot_determine(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "skills"
            root.mkdir()
            code, _, err = self._run(root, FakeRemote(head="f" * 40))
            self.assertEqual(2, code)
            self.assertIn("cannot-determine", err)

    def test_invalid_marker_json_is_cannot_determine(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "skills"
            root.mkdir()
            (root / "CORPUS.json").write_text("{not json", encoding="utf-8")
            with self.assertRaises(checker.FreshnessError):
                checker.read_marker(root)

    def test_remote_unreachable_is_cannot_determine(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            root = write_marker(Path(tmp), "1" * 40)
            remote = FakeRemote(
                head=None, head_error=checker.FreshnessError("network down")
            )
            code, _, err = self._run(root, remote)
            self.assertEqual(2, code)
            self.assertIn("cannot-determine", err)


if __name__ == "__main__":
    unittest.main()
