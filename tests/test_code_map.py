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
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.code_map import checks, cli, discovery  # noqa: E402

CODE_MAP = ROOT / "scripts" / "code_map"


def _git(*args, cwd):
    return subprocess.run(("git",) + args, cwd=str(cwd), check=True,
                          capture_output=True, text=True)


class HarnessError(AssertionError):
    """The mutation did not land. NOT a killed check -- a broken harness.

    Same rule as tests/test_mutation_floor.py: a substitution that silently
    fails to match produces a run that is indistinguishable from a passing one,
    so the harness must fail LOUDLY instead of reporting a green."""


def mutated_package(tmpdir, module, subs):
    """A COPY of scripts/code_map with `subs` applied to one of its modules.

    The copy is what lets a check be attacked without touching the shipped
    tree: `python -m scripts.code_map` run from `tmpdir` imports the mutated
    package, and `checks.PACKAGE_HOST` is derived from the module's own
    location, so the determinism check inside the copy rebuilds through the
    copy too.

    Every substitution must occur exactly once in the original and zero times
    after, and the replacement's count must go UP by exactly one -- a count
    delta, not `in`, so a replacement that already appears elsewhere cannot fake
    the assertion."""
    dest = Path(tmpdir) / "scripts" / "code_map"
    shutil.copytree(CODE_MAP, dest, ignore=shutil.ignore_patterns("__pycache__"))
    original = (CODE_MAP / module).read_text(encoding="utf-8")
    text = original
    for old, new in subs:
        if original.count(old) != 1:
            raise HarnessError(
                f"HARNESS ERROR: anchor occurs {original.count(old)} time(s) in "
                f"{module}, expected exactly 1. The module was edited without "
                f"updating this harness. This is NOT a caught mutation.\n  anchor: {old!r}")
        text = text.replace(old, new, 1)
    for old, new in subs:
        if text.count(old) != 0:
            raise HarnessError(f"HARNESS ERROR: {old!r} survived the substitution")
        if text.count(new) != original.count(new) + 1:
            raise HarnessError(
                f"HARNESS ERROR: replacement {new!r} did not increase by exactly one "
                f"(before={original.count(new)}, after={text.count(new)})")
    (dest / module).write_text(text, encoding="utf-8", newline="\n")
    return Path(tmpdir)


def run_code_map(host, *args):
    """`python -m scripts.code_map <args>` against the package under `host`.

    `python`, never `py`: the launcher has no pytest and no way to reach this
    package, and its failure reads like a clean run."""
    env = dict(os.environ)
    env.pop("FORCE_COLOR", None)
    env.pop("PYTHONIOENCODING", None)
    return subprocess.run([sys.executable, "-m", "scripts.code_map", *args],
                          cwd=str(host), capture_output=True, text=True, env=env)


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


_IMPORTING_SOURCE = '''"""A module with enough imports that a hash-ordered listing visibly churns."""
import collections
import json
import os
import pathlib
import re
import subprocess
import sys
import textwrap


def gather():
    """Name every import, so the extractor records each one."""
    return (collections, json, os, pathlib, re, subprocess, sys, textwrap)
'''


def _make_import_repo(tmp: Path):
    """A repo whose module imports eight stdlib names.

    Eight, not one: the determinism mutation below drops a `sorted()` around a
    SET of import names, and a one- or two-element set orders the same under
    every hash seed — the fixture has to be wide enough for the mutation to
    show."""
    (tmp / "pkg").mkdir()
    (tmp / "pkg" / "__init__.py").write_text("", encoding="utf-8", newline="\n")
    (tmp / "pkg" / "wide.py").write_text(_IMPORTING_SOURCE, encoding="utf-8", newline="\n")
    _git("init", "-q", cwd=tmp)
    _git("add", "pkg/__init__.py", "pkg/wide.py", cwd=tmp)


_CALLEE_SOURCE = '''"""The module other modules point at."""


def target():
    """Called from this module and from another."""
    return 1


def near():
    """Calls target from inside its own module."""
    return target() + target()
'''

_FAR_SOURCE = '''"""A module that calls and reads across the module boundary."""
from pkg.callee import target


def far():
    """Call it twice, then hand the function itself back."""
    target()
    target()
    return target
'''


def _make_cross_module_repo(tmp: Path):
    """A repo whose inbound edges span both directions the rendered line
    distinguishes.

    `pkg.callee:target` is called twice from its OWN module and called twice
    plus read once from another, so its page has to say five sites in two
    modules while naming only the other one. A fixture with references in one
    direction only would let a check that drops half of them still pass."""
    (tmp / "pkg").mkdir()
    (tmp / "pkg" / "__init__.py").write_text("", encoding="utf-8", newline="\n")
    (tmp / "pkg" / "callee.py").write_text(_CALLEE_SOURCE, encoding="utf-8", newline="\n")
    (tmp / "pkg" / "far.py").write_text(_FAR_SOURCE, encoding="utf-8", newline="\n")
    _git("init", "-q", cwd=tmp)
    _git("add", "pkg/__init__.py", "pkg/callee.py", "pkg/far.py", cwd=tmp)


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


class CheckExitCodeTests(unittest.TestCase):
    """Gate g1: `check` must EXIT NON-ZERO on a map that lies.

    Until g1 every check printed and `run()` ended in a literal `return 0`, so a
    completely broken map passed. These tests are the floor under that: an
    intact map exits 0, and a map with a page that exists but holds nothing
    exits non-zero.

    The empty page is `tc26`: the page count is `rglob("*.md")`, which counts a
    file that was created and never written, so a zero-byte page is invisible in
    every count the render report publishes."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _make_entity_repo(self.repo)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["build", "--root", str(self.repo)]), 0)

    def tearDown(self):
        self._tmp.cleanup()

    def _check(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = cli.main(["check", "--root", str(self.repo)])
        return code, buf.getvalue()

    def test_check_exits_zero_on_an_intact_map(self):
        """The positive control. Without it, a `check` that always failed would
        satisfy every other test in this class."""
        code, out = self._check()
        self.assertEqual(code, 0, out)

    def test_check_exits_non_zero_when_a_page_is_empty(self):
        page = self.repo / "map" / "pkg.thing" / "Widget.md"
        self.assertTrue(page.read_text(encoding="utf-8").strip(),
                        "input precondition: the page must have content to remove, "
                        "or emptying it changes nothing and this test cannot fail")

        page.write_text("", encoding="utf-8", newline="\n")

        code, out = self._check()
        self.assertNotEqual(code, 0, "an empty page passed `check`\n" + out)
        self.assertIn("Widget.md", out)


#: The renderer sorts a SET of import names before printing it. Drop the sort
#: and the page tree's content starts depending on the interpreter's string
#: hash seed — the classic build non-determinism, and invisible inside a single
#: process because a seed is fixed for that process's life.
HASH_ORDER_MUTATION = (
    ('    ext = sorted({o.rstrip(":").replace(":", ".") for o, res in imps if res == "external"})\n',
     '    ext = list({o.rstrip(":").replace(":", ".") for o, res in imps if res == "external"})\n'),
)


class DeterminismTests(unittest.TestCase):
    """Gate g1: two builds from unchanged source must be byte-identical.

    The comparison is over BYTES, and any non-empty diff is the failure. The
    run report carries no timings for exactly this reason; adding one would put
    a differing byte on every run and make this check unusable.

    The red proof is a real mutation run end to end, not an assertion that one
    would fail: a COPY of scripts/code_map has its `sorted()` removed, the whole
    pipeline is rebuilt through the copy, and `check` must exit non-zero. The
    unmutated copy is exercised first, so a red below is attributable to the
    mutation rather than to running from a copy at all."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _make_import_repo(self.repo)

    def tearDown(self):
        self._tmp.cleanup()

    def _package(self, subs=()):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return mutated_package(tmp.name, "render.py", subs)

    def test_two_builds_from_unchanged_source_are_byte_identical(self):
        m = checks.MapUnderCheck(self.repo, self.repo / ".code-map", self.repo / "map")
        self.assertEqual(checks.deterministic_rebuild(m), [])

    def test_determinism_reports_every_differing_path_not_a_boolean(self):
        """A reader needs to know WHICH page moved."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        left, right = Path(tmp.name) / "l", Path(tmp.name) / "r"
        for tree in (left, right):
            tree.mkdir()
            (tree / "same.md").write_text("same\n", encoding="utf-8", newline="\n")
        (left / "moved.md").write_text("a\n", encoding="utf-8", newline="\n")
        (right / "moved.md").write_text("b\n", encoding="utf-8", newline="\n")
        (left / "gone.md").write_text("x\n", encoding="utf-8", newline="\n")
        (right / "extra.md").write_text("y\n", encoding="utf-8", newline="\n")

        diff = checks.tree_diff(left, right)

        self.assertEqual(len(diff), 3, diff)
        self.assertTrue(any(d.startswith("gone.md:") for d in diff), diff)
        self.assertTrue(any(d.startswith("extra.md:") for d in diff), diff)
        self.assertTrue(any(d.startswith("moved.md:") for d in diff), diff)
        self.assertFalse(any(d.startswith("same.md") for d in diff), diff)

    def test_determinism_baseline_an_unmutated_package_copy_passes(self):
        """The positive control for the mutation below."""
        host = self._package()
        self.assertEqual(run_code_map(host, "build", "--root", str(self.repo)).returncode, 0)

        proc = run_code_map(host, "check", "--root", str(self.repo))

        self.assertEqual(proc.returncode, 0,
                         "HARNESS ERROR: the unmutated copy does not pass its own "
                         f"checks, so no red below proves anything\n{proc.stdout}\n{proc.stderr}")

    def test_determinism_goes_red_when_the_renderer_orders_pages_by_hash(self):
        host = self._package(HASH_ORDER_MUTATION)
        self.assertEqual(run_code_map(host, "build", "--root", str(self.repo)).returncode, 0)

        proc = run_code_map(host, "check", "--root", str(self.repo))

        self.assertNotEqual(proc.returncode, 0,
                            "MUTANT SURVIVED: a renderer whose output depends on the "
                            f"interpreter's hash seed passed `check`\n{proc.stdout}")
        # "FAIL deterministic-rebuild", not "deterministic-rebuild": the bare
        # name also appears on the passing line, so it would match a red caused
        # by some other check entirely.
        self.assertIn("FAIL deterministic-rebuild", proc.stdout)
        self.assertIn("INDEX.md", proc.stdout)


#: Inbound edges are `calls` AND `reads`. Count only the calls and every page
#: that is handed around as a value under-reports who depends on it.
DROP_READS_MUTATION = (
    ('            if p in ("calls", "reads"):\n',
     '            if p in ("calls",):\n'),
)

#: Attribute an inbound edge to the module that OWNS the target instead of the
#: module the call came from. Every caller then looks local, and the page reads
#: "this module only" -- a map that hides every cross-module dependency while
#: still reporting a plausible number.
WRONG_CALLER_MUTATION = (
    ("                inbound[o][intern(modof(s))] += 1\n",
     "                inbound[o][intern(modof(o))] += 1\n"),
)


class InboundAttributionTests(unittest.TestCase):
    """Gate g1: a page's caller set must match an independent full scan.

    The renderer builds its inbound index while loading the store;
    `checks.StoreScan` builds one again from the raw statements, and the
    comparison is against the RENDERED PAGE rather than against the renderer's
    own dictionary — a check that reads its expected value out of the code under
    test can only ever agree with it.

    Both mutations below are silent by design: the map still builds, every page
    still renders, and the number on the page is still plausible. Nothing but a
    second derivation can tell them from the truth."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _make_cross_module_repo(self.repo)

    def tearDown(self):
        self._tmp.cleanup()

    def _package(self, subs=()):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return mutated_package(tmp.name, "render.py", subs)

    def _map(self):
        return checks.MapUnderCheck(self.repo, self.repo / ".code-map", self.repo / "map")

    def test_caller_sets_agree_with_an_independent_scan_of_the_store(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["build", "--root", str(self.repo)]), 0)
        m = self._map()

        stated = [checks.parse_refs(line)
                  for page, _ in m.entity_pages
                  for line in checks.refs_lines(m.text(page))]
        self.assertTrue(
            any(r and r.sites > 1 and r.modules > 1 and r.named for r in stated),
            "input precondition: some page must be referenced from more than one "
            "module, or this check compares nothing but empty caller sets and "
            "cannot fail")

        self.assertEqual(checks.inbound_attribution(m), [])

    def test_caller_count_goes_red_when_the_renderer_forgets_reads(self):
        host = self._package(DROP_READS_MUTATION)
        self.assertEqual(run_code_map(host, "build", "--root", str(self.repo)).returncode, 0)

        proc = run_code_map(host, "check", "--root", str(self.repo))

        self.assertNotEqual(proc.returncode, 0,
                            "MUTANT SURVIVED: a page under-reporting its inbound "
                            f"sites passed `check`\n{proc.stdout}")
        self.assertIn("FAIL inbound-attribution", proc.stdout)
        self.assertIn("inbound sites", proc.stdout)

    def test_caller_modules_go_red_when_the_renderer_misattributes_the_caller(self):
        host = self._package(WRONG_CALLER_MUTATION)
        self.assertEqual(run_code_map(host, "build", "--root", str(self.repo)).returncode, 0)

        proc = run_code_map(host, "check", "--root", str(self.repo))

        self.assertNotEqual(proc.returncode, 0,
                            "MUTANT SURVIVED: a map that credits every caller to the "
                            f"callee's own module passed `check`\n{proc.stdout}")
        self.assertIn("FAIL inbound-attribution", proc.stdout)
        self.assertIn("as callers", proc.stdout)


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
