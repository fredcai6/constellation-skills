"""A failing subtest must be findable by searching for `FAILED`.

The defect this pins, measured during epic #567: pytest marks a test `PASSED`
when its body raises inside `self.subTest(...)`, and prints the failure on a
`SUBFAILED(...)` line. `SUBFAILED` does not match `FAILED ` — the character after
`FAILED` is `(`, not a space — so an agent or a script that greps `FAILED` reads a
clean run. An Admiral's merge gate did exactly that across four lanes.

Each test here runs pytest in a **subprocess** on a temporary probe file, because
the subject is pytest's own terminal output. Asserting against strings this
process built would test the fixture, not the behaviour.

The negative control is the load-bearing half: it runs the same probe with the
repo's `conftest.py` absent and asserts the `FAILED` line is **missing**. Without
it, this file would pass just as well if the hook did nothing, because pytest's
own summary already contains the word `failed` in its tally line.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFTEST = REPO_ROOT / "conftest.py"

PROBE = '''\
import unittest


class Probe(unittest.TestCase):
    def test_body_raises_inside_subtest(self):
        for i in (1, 2):
            with self.subTest(i=i):
                raise RuntimeError(f"boom {i}")
'''


def _run_probe(tmp_path: Path, *, with_conftest: bool) -> subprocess.CompletedProcess:
    probe = tmp_path / "probe_subtest.py"
    probe.write_text(PROBE, encoding="utf-8", newline="\n")
    if with_conftest:
        (tmp_path / "conftest.py").write_text(
            CONFTEST.read_text(encoding="utf-8"), encoding="utf-8", newline="\n"
        )
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:randomly", str(probe.name)],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def _failed_lines(output: str) -> list[str]:
    return [line for line in output.splitlines() if line.startswith("FAILED ")]


def test_the_defect_is_real_pytest_marks_the_test_passed(tmp_path):
    """Ground the premise. If pytest ever stops reporting a raising subtest as a
    passing test, this whole guard is obsolete and should be deleted rather than
    carried."""
    result = _run_probe(tmp_path, with_conftest=False)
    assert "SUBFAILED" in result.stdout, result.stdout
    assert "1 passed" in result.stdout, (
        "the premise no longer holds: pytest no longer counts the raising test as "
        f"passed, so this guard may be unnecessary\n{result.stdout}"
    )
    assert result.returncode != 0, "the build does fail; only the reading was blind"


def test_negative_control_without_the_hook_a_FAILED_grep_finds_nothing(tmp_path):
    """The control that makes the positive test mean something."""
    result = _run_probe(tmp_path, with_conftest=False)
    assert _failed_lines(result.stdout) == [], (
        "a FAILED-prefixed line appeared without the hook, so the positive test "
        f"below proves nothing\n{result.stdout}"
    )


def test_with_the_hook_each_failed_subtest_is_greppable_as_FAILED(tmp_path):
    result = _run_probe(tmp_path, with_conftest=True)
    lines = _failed_lines(result.stdout)
    assert len(lines) == 2, (
        f"expected one FAILED line per failed subtest (2), got {len(lines)}"
        f"\n{result.stdout}"
    )
    for line in lines:
        assert "probe_subtest.py::Probe::test_body_raises_inside_subtest" in line, line
        assert "[subtest" in line, (
            "the restated line must stay distinguishable from a whole-test failure: "
            f"{line}"
        )
    assert "i=1" in " ".join(lines) and "i=2" in " ".join(lines), (
        f"each subtest's own identity must survive into its line\n{lines}"
    )
    assert "2 failed subtest(s)" in result.stdout, (
        "the count must be stated: a guard that loops has to assert what it looped "
        f"over, or a silent truncation reads as a clean run\n{result.stdout}"
    )


def test_a_clean_run_adds_no_section(tmp_path):
    """No false positives: a suite with no failing subtest gains nothing."""
    probe = tmp_path / "probe_subtest.py"
    probe.write_text(
        "import unittest\n\n\nclass Probe(unittest.TestCase):\n"
        "    def test_ok(self):\n"
        "        for i in (1, 2):\n"
        "            with self.subTest(i=i):\n"
        "                self.assertTrue(True)\n",
        encoding="utf-8",
        newline="\n",
    )
    (tmp_path / "conftest.py").write_text(
        CONFTEST.read_text(encoding="utf-8"), encoding="utf-8", newline="\n"
    )
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:randomly", "probe_subtest.py"],
        cwd=str(tmp_path), capture_output=True, text=True, encoding="utf-8",
    )
    assert result.returncode == 0, result.stdout
    assert _failed_lines(result.stdout) == [], result.stdout
    assert "restated as FAILED" not in result.stdout, result.stdout


def test_the_hook_ships_at_the_repo_root_so_it_covers_the_whole_suite():
    """Placement is the mechanism. A hook under tests/ would miss any suite run
    from a different rootdir, and the point is that no one has to remember."""
    assert CONFTEST.is_file(), f"missing {CONFTEST}"
    text = CONFTEST.read_text(encoding="utf-8")
    assert "pytest_terminal_summary" in text
    assert "pytest_runtest_logreport" in text


@pytest.mark.parametrize("word", ["SUBFAILED", "SUBPASSED"])
def test_the_marker_words_still_differ_from_a_plain_FAILED_search(word):
    """Why one search word was not enough, asserted rather than described."""
    assert not word.startswith("FAILED ")
    assert "FAILED " not in word
