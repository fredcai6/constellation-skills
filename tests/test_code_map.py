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
import json
import re
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


_ENTITY_SOURCE = '''"""A module that actually defines things."""


class Widget:
    """A widget."""

    def spin(self):
        """Spin the widget."""
        return 1


def helper():
    """Do the small thing."""
    return 2
'''


def _make_entity_repo(tmp: Path):
    """A repo whose modules define real entities, so the renderer emits entity
    pages at all. `_make_repo`'s modules are bare assignments — they produce no
    entity page, so a page-format assertion over that tree would scan nothing
    and pass without ever reading a header."""
    (tmp / "pkg").mkdir()
    (tmp / "pkg" / "__init__.py").write_text("", encoding="utf-8", newline="\n")
    (tmp / "pkg" / "thing.py").write_text(_ENTITY_SOURCE, encoding="utf-8", newline="\n")
    _git("init", "-q", cwd=tmp)
    _git("add", "pkg/__init__.py", "pkg/thing.py", cwd=tmp)


_COLLIDING_SOURCE = '''"""A module whose entity page collides with its own index page."""


class INDEX:
    """Named INDEX, so its page path is the module index's page path."""

    def go(self):
        """Do it."""
        return 1
'''


def _make_collision_repo(tmp: Path):
    """A repo where two pages resolve to ONE output path.

    The renderer names an entity page `<qualified name>.md` inside the module's
    directory, and names the module's own index page `INDEX.md` in that same
    directory. So a class called `INDEX` lands on the module index: two writes,
    one file.

    This is the same failure mode as the real repo's `Verdict` class versus
    `verdict` function, but reachable on every platform. That one collides only
    because Windows and macOS filesystems are case-insensitive; on a
    case-sensitive filesystem the two are separate files and nothing diverges,
    so a fixture built on it would prove nothing on Linux."""
    (tmp / "pkg").mkdir()
    (tmp / "pkg" / "__init__.py").write_text("", encoding="utf-8", newline="\n")
    (tmp / "pkg" / "thing.py").write_text(_COLLIDING_SOURCE, encoding="utf-8", newline="\n")
    _git("init", "-q", cwd=tmp)
    _git("add", "pkg/__init__.py", "pkg/thing.py", cwd=tmp)


#: A source position in a rendered page: a Python file path with a line number
#: welded to it. The confirmed ruling is that nothing committed carries one.
POSITION = re.compile(r"\.py:\d+")


class RenderReportTests(unittest.TestCase):
    """Guards the *method* `pages` is counted by, and nothing more.

    Read this before trusting the field. Counting `write_text()` calls reports
    what the renderer TRIED to do, so a page silently overwriting another is
    invisible in it -- that was the original defect and this test kills it:
    restore the per-write counter and it goes red.

    But the replacement is a count of the tree it describes, which makes it
    tautologically true of that tree, so it cannot detect anything ABOUT the
    tree either. Measured, not argued: delete every second entity page right
    after writing it, or never write a single module `INDEX.md`, or write every
    page flat into `map/` instead of its module directory -- this test stays
    GREEN through all three. It computes its expected value with the same
    `rglob("*.md")` expression as `render.run`, so it can only ever agree with
    it. **`pages` does not detect a lost page. Do not read a green here as
    evidence that the page tree is complete.**

    The check that CAN fail already exists in the report and nothing asserts
    it: `pages - 1 - modules` against `entity_pages` differ by exactly the pages
    lost to filename collisions. Asserting it belongs to `g1`, whose charter is
    a check stage that can fail, together with the collision itself (`tc17`);
    it would be red on arrival here, because `g2` owns the rename that fixes
    it. See `tc24` -- counting the tree again is NOT the fix for the sibling
    field `entity_pages`."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _make_collision_repo(self.repo)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["build", "--root", str(self.repo)]), 0)
        self.report = json.loads(
            (self.repo / ".code-map" / "render_report.json").read_text(encoding="utf-8"))
        self.on_disk = sorted((self.repo / "map").rglob("*.md"))

    def tearDown(self):
        self._tmp.cleanup()

    def _write_calls(self):
        """What a per-write counter would report: the top index, one index per
        module, and one page per entity."""
        supp = json.loads(
            (self.repo / ".code-map" / "supplement.json").read_text(encoding="utf-8"))
        return 1 + len(supp["modules"]) + len(supp["entities"])

    def test_render_report_page_count_equals_the_files_on_disk(self):
        self.assertGreater(
            self._write_calls(), len(self.on_disk),
            "input precondition: the fixture must make two pages resolve to one "
            "path, or a write-call count and a file count agree by luck and this "
            "test cannot fail")

        self.assertEqual(self.report["pages"], len(self.on_disk))


class RenderedPageFormatTests(unittest.TestCase):
    """The page header format, against the confirmed ruling that nothing
    committed carries a source position.

    The ruling splits three things that look alike:

    - a **line number** churns. A 3-line edit near the top of a file shifts
      every entity below it and rewrites hundreds of unrelated pages. It goes.
    - a **file path** does not churn — it changes only when the file moves. It
      stays.
    - an entity's **own size** changes only that entity's own page, which is a
      page changing when its own subject changed. It stays.

    So there are two tests here, not one: removing too much fails the ruling as
    surely as removing too little.

    The fixture is synthetic on purpose. A blunt scan of the REAL page tree
    still reports two hits — both from one authored docstring in
    `tests/test_checklist_engine.py` that names `scripts/checklist_engine.py:449`
    in its own prose, echoed onto the entity page and its module index line.
    That is source text the renderer copied through, not a position the renderer
    emitted, and it churns only when its own docstring changes. Scanning a
    controlled tree is what keeps this test about the renderer."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _make_entity_repo(self.repo)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["build", "--root", str(self.repo)]), 0)
        self.pages = sorted((self.repo / "map").rglob("*.md"))

    def tearDown(self):
        self._tmp.cleanup()

    def _headers(self):
        """The second line of every entity page — the one `loc()` writes."""
        return [(p, p.read_text(encoding="utf-8").splitlines()[1])
                for p in self.pages if p.name != "INDEX.md"]

    def test_no_rendered_page_carries_a_source_line_number(self):
        headers = self._headers()
        self.assertTrue(headers, "input precondition: the tree must contain entity "
                                 "pages, or this scan reads nothing and cannot fail")

        offenders = [(str(p.relative_to(self.repo)), n, line)
                     for p in self.pages
                     for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1)
                     if POSITION.search(line)]

        self.assertEqual(offenders, [], "rendered pages carry a source position")

    def test_page_header_keeps_the_file_path_and_the_entity_size(self):
        """The other half of the ruling: stripping the path or the size is
        over-stripping, and this is what catches it."""
        headers = self._headers()
        self.assertTrue(headers, "input precondition: the tree must contain entity pages")
        for page, header in headers:
            with self.subTest(page=page.name):
                self.assertIn("pkg/thing.py", header)
                self.assertRegex(header, r", \d+ lines\b")


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
