"""Tests for scripts/code_map/ — the derived code map (issue #456, gate g0).

Gate g0 introduces exactly two behaviors of its own: the discovery layer that
enumerates the **mappable corpus**, and the argparse CLI. Those two are
test-first. The three pipeline stages (extract, supplement, render) are a port
of the reference prototype and are covered by end-to-end evidence, not by unit
tests that would freeze prototype behavior gates g2/g3 are going to change.

`mappable corpus` is the set of source files the map is derived FROM. It is not
the skills `corpus` of docs/agents/GLOSSARY.md — different thing, same English
word; the code says `mappable corpus` wherever the distinction matters.

The exclusion tests are the load-bearing ones: `.agent-work/` is deliberately
TRACKED in this repo, so `git ls-files` alone does not exclude it, and letting
it into the corpus makes roughly a third of the map run scratch. Each exclusion
test asserts that the thing being excluded was actually PRESENT in the input —
a filter test over an input with nothing to filter passes without ever
exercising the filter.
"""

import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.code_map import cli, discovery  # noqa: E402


def _git(*args, cwd):
    return subprocess.run(("git",) + args, cwd=str(cwd), check=True,
                          capture_output=True, text=True)


def _make_repo(tmp: Path):
    """A synthetic git repo whose tracked set spans every case the filter sees:
    a source file, a run-scratch file under .agent-work/, a nested scratch file,
    a tracked non-Python file, and an untracked Python file."""
    (tmp / "src").mkdir()
    (tmp / ".agent-work" / "issue-1").mkdir(parents=True)
    (tmp / "src" / "a.py").write_text("x = 1\n", encoding="utf-8", newline="\n")
    (tmp / "b.py").write_text("y = 2\n", encoding="utf-8", newline="\n")
    (tmp / "README.md").write_text("doc\n", encoding="utf-8", newline="\n")
    (tmp / ".agent-work" / "scratch.py").write_text("z = 3\n", encoding="utf-8", newline="\n")
    (tmp / ".agent-work" / "issue-1" / "deep.py").write_text("w = 4\n", encoding="utf-8", newline="\n")
    (tmp / "untracked.py").write_text("u = 5\n", encoding="utf-8", newline="\n")
    _git("init", "-q", cwd=tmp)
    _git("add", "src/a.py", "b.py", "README.md",
         ".agent-work/scratch.py", ".agent-work/issue-1/deep.py", cwd=tmp)


class DiscoveryTests(unittest.TestCase):
    """The discovery layer, against a synthetic repo — hermetic, so these do not
    move when this repo's own file list moves."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _make_repo(self.repo)

    def tearDown(self):
        self._tmp.cleanup()

    def test_discovery_excludes_agent_work(self):
        """THE load-bearing one: remove the exclusion and this goes red."""
        tracked = discovery.tracked_python_files(self.repo)
        scratch = [p for p in tracked if p.startswith(".agent-work/")]
        self.assertEqual(sorted(scratch),
                         [".agent-work/issue-1/deep.py", ".agent-work/scratch.py"],
                         "input precondition: the repo must TRACK .agent-work Python "
                         "files, or this test filters nothing and cannot fail")

        corpus = discovery.discover_corpus(self.repo)

        self.assertEqual(corpus, ["b.py", "src/a.py"])
        self.assertEqual([p for p in corpus if p.startswith(".agent-work/")], [])
        self.assertEqual(len(corpus), len(tracked) - len(scratch))

    def test_discovery_excludes_untracked_and_non_python(self):
        corpus = discovery.discover_corpus(self.repo)
        self.assertNotIn("untracked.py", corpus)
        self.assertNotIn("README.md", corpus)
        self.assertTrue(all(p.endswith(".py") for p in corpus))

    def test_discovery_is_sorted_posix_relative_paths(self):
        corpus = discovery.discover_corpus(self.repo)
        self.assertEqual(corpus, sorted(corpus))
        self.assertTrue(corpus)
        for p in corpus:
            self.assertNotIn("\\", p)
            self.assertFalse(Path(p).is_absolute())

    def test_discovery_predicate_and_listing_agree(self):
        """The corpus is defined by the predicate the module itself applies, not
        by a second hand-maintained list that can drift from it."""
        tracked = discovery.tracked_python_files(self.repo)
        self.assertEqual(discovery.discover_corpus(self.repo),
                         sorted(p for p in tracked if discovery.is_mappable(p)))


class DiscoveryOnThisRepoTests(unittest.TestCase):
    """One integration check against the real repo. It asserts the RULE, never a
    pinned file count: this run adds files, so a pinned count goes red for the
    wrong reason."""

    def test_discovery_on_this_repo_excludes_agent_work(self):
        tracked = discovery.tracked_python_files(ROOT)
        scratch = [p for p in tracked if p.startswith(".agent-work/")]
        self.assertTrue(scratch, "input precondition: this repo tracks .agent-work "
                                 "Python files, so the filter has something to remove")
        corpus = discovery.discover_corpus(ROOT)
        self.assertTrue(corpus)
        self.assertEqual([p for p in corpus if p.startswith(".agent-work/")], [])
        self.assertIn("scripts/code_map/discovery.py", corpus)


class CliArgumentTests(unittest.TestCase):
    """The CLI's argument handling — the second behavior gate g0 introduces."""

    def test_cli_parses_every_pipeline_stage_as_a_subcommand(self):
        parser = cli.build_parser()
        for name in ("discover", "extract", "supplement", "render", "build", "check"):
            with self.subTest(subcommand=name):
                args = parser.parse_args([name])
                self.assertEqual(args.command, name)

    def test_cli_root_defaults_to_the_repository_root(self):
        args = cli.build_parser().parse_args(["discover"])
        self.assertEqual(Path(args.root).resolve(), ROOT)

    def test_cli_root_is_overridable(self):
        args = cli.build_parser().parse_args(["build", "--root", "some/where"])
        self.assertEqual(Path(args.root), Path("some/where"))

    def test_cli_rejects_an_unknown_subcommand(self):
        with self.assertRaises(SystemExit) as caught:
            with contextlib.redirect_stderr(io.StringIO()):
                cli.build_parser().parse_args(["nonesuch"])
        self.assertEqual(caught.exception.code, 2)

    def test_cli_requires_a_subcommand(self):
        with self.assertRaises(SystemExit) as caught:
            with contextlib.redirect_stderr(io.StringIO()):
                cli.build_parser().parse_args([])
        self.assertEqual(caught.exception.code, 2)

    def test_cli_artifacts_and_out_default_under_the_root(self):
        args = cli.build_parser().parse_args(["build", "--root", "some/where"])
        self.assertEqual(Path(args.artifacts), Path("some/where") / ".code-map")
        self.assertEqual(Path(args.out), Path("some/where") / "map")


class CliDiscoverCommandTests(unittest.TestCase):
    """`discover` is the discovery layer's caller — it is what keeps
    discover_corpus wired to something a user can actually run."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _make_repo(self.repo)

    def tearDown(self):
        self._tmp.cleanup()

    def test_cli_discover_prints_the_mappable_corpus_and_exits_zero(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = cli.main(["discover", "--root", str(self.repo)])
        self.assertEqual(code, 0)
        self.assertEqual(buf.getvalue().split(), ["b.py", "src/a.py"])


class CliBuildCommandTests(unittest.TestCase):
    """`build` is the whole pipeline's caller. This asserts that the three
    ported stages are WIRED and produce their artifacts — not what they put in
    them. Pinning page content here would freeze prototype behavior that gates
    g2 and g3 exist to change."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _make_repo(self.repo)

    def tearDown(self):
        self._tmp.cleanup()

    def test_cli_build_runs_every_stage_and_writes_the_page_tree(self):
        with contextlib.redirect_stdout(io.StringIO()):
            code = cli.main(["build", "--root", str(self.repo)])
        self.assertEqual(code, 0)
        for produced in (".code-map/statements.jsonl", ".code-map/supplement.json",
                         "map/INDEX.md", "map/ids.jsonl"):
            with self.subTest(artifact=produced):
                self.assertTrue((self.repo / produced).exists())
        self.assertTrue((self.repo / ".code-map/statements.jsonl")
                        .read_text(encoding="utf-8").strip())

    def test_cli_build_maps_the_corpus_and_not_the_scratch(self):
        """The exclusion has to hold through the whole pipeline, not only at the
        discovery call: a scratch module reaching the page tree is the failure
        this gate exists to prevent."""
        with contextlib.redirect_stdout(io.StringIO()):
            cli.main(["build", "--root", str(self.repo)])
        rendered = sorted(p.name for p in (self.repo / "map").iterdir() if p.is_dir())
        self.assertEqual(rendered, ["b", "src.a"])


if __name__ == "__main__":
    unittest.main()
