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

import pytest

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


_WIDGET_SOURCE = '''"""The module other modules point at."""


class Widget:
    """A widget."""

    def spin(self):
        """Spin it."""
        return 1


def helper():
    """Make one."""
    return Widget()
'''

_WIDGET_USER_SOURCE = '''"""A module that uses Widget across the module boundary."""
from pkg.widget import Widget, helper


def use():
    """Call helper twice, then hand Widget itself back."""
    helper()
    helper()
    return Widget
'''


def _make_mixed_repo(tmp: Path):
    """A repo that carries BOTH properties the join tests need at once.

    An entity whose name is not already lowercase (`Widget`), so a mutation that
    renames entities is not silently a no-op; and real cross-module inbound
    edges, so `inbound_attribution` has something to agree about rather than
    comparing empty caller sets. A fixture with only one of the two lets the
    independence claim in `test_join_catches_a_rename...` pass vacuously."""
    (tmp / "pkg").mkdir()
    (tmp / "pkg" / "__init__.py").write_text("", encoding="utf-8", newline="\n")
    (tmp / "pkg" / "widget.py").write_text(_WIDGET_SOURCE, encoding="utf-8", newline="\n")
    (tmp / "pkg" / "user.py").write_text(_WIDGET_USER_SOURCE, encoding="utf-8", newline="\n")
    _git("init", "-q", cwd=tmp)
    _git("add", "pkg/__init__.py", "pkg/widget.py", "pkg/user.py", cwd=tmp)


_FUNCTION_NESTED_SOURCE = '''"""Definitions nested inside a function — both arms of defect D2."""


class Holder:
    """Two methods, each defining a closure of the same name."""

    def first(self):
        """The first method."""

        def shared():
            """The first method's closure."""
            return 1

        return shared

    def second(self):
        """The second method."""

        def shared():
            """The second method's closure."""
            return 2

        return shared


def outer():
    """A function that defines a class."""

    class Bundle:
        """Defined inside a function, so it is not a module-level class."""

        def method(self):
            """A method of a class that is defined inside a function."""
            return 3

    return Bundle
'''


def _make_function_nested_repo(tmp: Path):
    """A repo carrying both arms of defect D2 at once.

    Arm one: two closures named `shared`, in two different METHODS of one class.
    The old symbol was built from the innermost CLASS however deep inside a
    method the definition sat, so both were `pkg.nested:Holder.shared` — one
    symbol, two entities, and one unioned set of facts on both pages.

    Arm two: a class defined inside a function, which the old symbol named as if
    it were module-level. This repository declares NO class inside a function,
    so this fixture is the only place that arm is exercised anywhere."""
    (tmp / "pkg").mkdir()
    (tmp / "pkg" / "__init__.py").write_text("", encoding="utf-8", newline="\n")
    (tmp / "pkg" / "nested.py").write_text(_FUNCTION_NESTED_SOURCE,
                                           encoding="utf-8", newline="\n")
    _git("init", "-q", cwd=tmp)
    _git("add", "pkg/__init__.py", "pkg/nested.py", cwd=tmp)


def contains_sites(artifacts):
    """Every definition symbol in the statement store -> its definition sites.

    Read from the store directly, never through `render.load_stores`: the symbol
    IS what defect D2 was about, and reading it back through the renderer would
    ask the code under test what it thinks it emitted."""
    sites = {}
    with open(Path(artifacts) / "statements.jsonl", encoding="utf-8") as f:
        for line in f:
            statement = json.loads(line)
            if statement["p"] == "contains":
                sites.setdefault(statement["o"], []).append(
                    (statement["q"]["file"], statement["q"]["line"] + 1))
    return sites


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


#: The renderer leaves the page's OWN module out of the named caller list,
#: because the count already accounts for it. Name it anyway and the line
#: contradicts its own convention -- visible without reading the store at all.
OWN_MODULE_NAMED_MUTATION = (
    ("    ext = sorted(m for m in callers if m != mod)\n",
     "    ext = sorted(m for m in callers)\n"),
)


class RefsLineSelfConsistencyTests(unittest.TestCase):
    """Gate g1: a page's referenced-by count must agree with its own list.

    Page-local — no store, no supplement. `inbound_attribution` is stronger
    wherever the store is readable, so the value of this one is its SCOPE (every
    page in the tree, not only pages whose title names a known entity) and its
    independence from the store schema that gate g3 rewrites. The last test
    below is the one that shows that scope is not hypothetical."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _make_cross_module_repo(self.repo)

    def tearDown(self):
        self._tmp.cleanup()

    def _build(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["build", "--root", str(self.repo)]), 0)
        return checks.MapUnderCheck(self.repo, self.repo / ".code-map", self.repo / "map")

    def test_refs_lines_are_self_consistent_on_an_intact_map(self):
        m = self._build()

        parsed = [checks.parse_refs(line)
                  for page in m.pages
                  for line in checks.refs_lines(m.text(page))]
        self.assertTrue(
            any(r and r.modules - len(r.named) == 1 for r in parsed),
            "input precondition: some page must count a module it does not name -- "
            "its own -- or the at-most-one-unnamed rule is never exercised and this "
            "test cannot fail")

        self.assertEqual(checks.refs_line_self_consistent(m), [])

    def test_self_consistent_line_goes_red_when_a_page_names_its_own_module(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        host = mutated_package(tmp.name, "render.py", OWN_MODULE_NAMED_MUTATION)
        self.assertEqual(run_code_map(host, "build", "--root", str(self.repo)).returncode, 0)

        proc = run_code_map(host, "check", "--root", str(self.repo))

        self.assertNotEqual(proc.returncode, 0,
                            "MUTANT SURVIVED: a page contradicting its own caller "
                            f"convention passed `check`\n{proc.stdout}")
        self.assertIn("FAIL refs-line-self-consistent", proc.stdout)
        self.assertIn("its own module", proc.stdout)

    def test_self_consistent_check_sees_pages_the_store_check_cannot(self):
        """The scope claim, measured rather than argued.

        `inbound_attribution` iterates pages whose title names a known entity.
        The top index is not one, so a lie written on it is invisible there and
        caught here. If this ever stops holding, the page-local check is
        genuinely redundant and should be said to be."""
        m = self._build()
        top = self.repo / "map" / "INDEX.md"
        self.assertNotIn(top, [p for p, _ in m.entity_pages],
                         "input precondition: the top index must NOT be an entity page, "
                         "or the two checks have the same scope and this proves nothing")

        top.write_text(top.read_text(encoding="utf-8")
                       + "\nreferenced by: 1 sites in 3 modules (a, b, c)\n",
                       encoding="utf-8", newline="\n")
        m = checks.MapUnderCheck(self.repo, self.repo / ".code-map", self.repo / "map")

        self.assertEqual(checks.inbound_attribution(m), [],
                         "the store check was expected to be blind to this page")
        failures = checks.refs_line_self_consistent(m)
        self.assertTrue(any("INDEX.md" in f for f in failures), failures)


#: Re-introduce defect (b) exactly: keep counting the own module's sites in the
#: totals, stop saying so. The page reads `5 sites in 2 modules (pkg.far)` again
#: and the reader is back to guessing where the other two went.
OWN_SITES_UNACCOUNTED_MUTATION = (
    ('            s += f" + {own} in this module"\n',
     '            s += ""\n'),
)

#: Publish the number and drop the sentence that says what it counted. Every
#: total is still right; a reader whose grep disagrees still cannot tell which
#: question either number answered.
LEGEND_DROPPED_MUTATION = (
    ('    return [s, REFS_LEGEND, ""]\n',
     '    return [s, ""]\n'),
)


class RefsAccountingTests(unittest.TestCase):
    """Gate g2, defect (b): the count and the list must reconcile, and the page
    must say what the count counted.

    `pkg.callee:target` is called twice from its own module and referenced three
    times from `pkg.far`, so its page has to publish 5 sites in 2 modules while
    naming one module. Today the page says `5 sites in 2 modules (pkg.far)` and
    stops: a reader who greps `pkg.far` finds 3 and has no way to learn where the
    other 2 went, or whether the tool simply lost them. Both numbers are
    defensible on their own; a page that shows them without saying what either
    means is the defect.

    Two arms, because the defect has two halves. The first is reconciliation --
    every counted site is attributable from the line alone. The second is the
    legend -- the page states what the count includes and excludes, so a reader
    whose `grep` returns 7 knows which of the two numbers to trust rather than
    guessing."""

    #: Facts about the fixture, asserted as an input precondition before they
    #: are used. If the fixture ever stops having own-module callers this test
    #: silently stops testing anything, so it is checked, not assumed.
    TARGET_PAGE = "target.md"
    TARGET_SITES = 5
    TARGET_OWN = 2

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _make_cross_module_repo(self.repo)

    def tearDown(self):
        self._tmp.cleanup()

    def _build(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["build", "--root", str(self.repo)]), 0)
        return checks.MapUnderCheck(self.repo, self.repo / ".code-map", self.repo / "map")

    def _target_page(self, m):
        for page, key in m.entity_pages:
            if key == "pkg.callee:target":
                return page
        self.fail("input precondition: the fixture must render a page for "
                  "pkg.callee:target")

    def test_a_reader_can_account_for_every_counted_site_from_the_line_alone(self):
        m = self._build()
        page = self._target_page(m)
        line = checks.refs_lines(m.text(page))
        self.assertEqual(len(line), 1, line)
        stated = checks.parse_refs(line[0])
        self.assertIsNotNone(stated, line[0])

        self.assertEqual(stated.sites, self.TARGET_SITES,
                         "input precondition: the fixture's target must be "
                         "referenced from both its own module and another one")
        self.assertEqual(stated.modules, len(stated.named) + 1,
                         "input precondition: exactly one counted module -- the "
                         "page's own -- must go unnamed, or there is nothing here "
                         "for a reader to fail to reconcile")

        # RED on the rendered text, not on a missing helper: the line published
        # today is `5 sites in 2 modules (pkg.far)` and stops there.
        self.assertIn(
            f"{self.TARGET_OWN} in this module", line[0],
            f"the line {line[0]!r} counts {stated.sites} sites across "
            f"{stated.modules} modules but names {len(stated.named)}; a reader "
            f"cannot tell how many of those sites the unnamed module holds")
        self.assertEqual(
            stated.own, self.TARGET_OWN,
            "the grammar in checks.py must expose the own-module sites as a "
            "number, or no check can hold the renderer to them")
        self.assertEqual(
            stated.sites - stated.own, self.TARGET_SITES - self.TARGET_OWN,
            "the sites left after the own-module clause must be the ones the "
            "named modules hold, or the line still does not reconcile")

    def test_every_inbound_line_states_what_the_count_includes_and_excludes(self):
        m = self._build()

        seen = 0
        for page in m.pages:
            lines = m.text(page).splitlines()
            for i, line in enumerate(lines):
                if not line.startswith(checks.REFS_PREFIX):
                    continue
                seen += 1
                follower = lines[i + 1] if i + 1 < len(lines) else ""
                self.assertTrue(
                    follower.startswith("counted:") and "not counted:" in follower,
                    f"{m.rel(page)}: the inbound line {line!r} is not followed by "
                    f"a statement of what the count counted, so a reader whose own "
                    f"grep disagrees cannot tell which number is wrong; got "
                    f"{follower!r}")
        self.assertGreater(seen, 0, "input precondition: some page must carry an "
                                    "inbound line")

    def test_the_legend_names_the_predicates_the_count_actually_counts(self):
        """The legend is a claim about the code, not decoration.

        `load_stores` counts inbound edges for `calls` and `reads` and nothing
        else. If a later gate widens that predicate set and leaves the legend
        alone, the page states something confident and untrue -- which is the
        whole defect class this gate exists to close.

        Falsifier grade B: red by absence today, because there is no legend to
        contradict. It earns its place from the day after, when the legend is a
        sentence someone can leave behind."""
        source = (ROOT / "scripts" / "code_map" / "render.py").read_text(encoding="utf-8")
        self.assertIn('if p in ("calls", "reads"):', source,
                      "input precondition: the renderer must still count exactly "
                      "these two predicates, or the legend below is stale")
        for predicate in ("calls", "reads"):
            self.assertIn(predicate, checks.REFS_LEGEND)
        for excluded in ("definition", "import", "inherit", "write", "docstring",
                         "unresolved"):
            self.assertIn(excluded, checks.REFS_LEGEND)

    def test_check_goes_red_when_the_own_module_sites_stop_being_accounted_for(self):
        """The strengthened rule must be able to fail on the defect it replaced.

        `refs_line_self_consistent` used to allow at most ONE counted module to
        go unnamed, so the pre-fix line passed it. If the new rule cannot kill
        this mutant, the strengthening bought nothing."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        host = mutated_package(tmp.name, "render.py", OWN_SITES_UNACCOUNTED_MUTATION)
        self.assertEqual(run_code_map(host, "build", "--root", str(self.repo)).returncode, 0)

        proc = run_code_map(host, "check", "--root", str(self.repo))

        self.assertNotEqual(proc.returncode, 0,
                            "MUTANT SURVIVED: a page counting sites it does not "
                            f"account for passed `check`\n{proc.stdout}")
        self.assertIn("FAIL refs-line-self-consistent", proc.stdout)
        self.assertIn("must name every module it counts", proc.stdout)

    def test_check_goes_red_when_the_legend_is_dropped(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        host = mutated_package(tmp.name, "render.py", LEGEND_DROPPED_MUTATION)
        self.assertEqual(run_code_map(host, "build", "--root", str(self.repo)).returncode, 0)

        proc = run_code_map(host, "check", "--root", str(self.repo))

        self.assertNotEqual(proc.returncode, 0,
                            "MUTANT SURVIVED: a page publishing an inbound count "
                            f"with nothing saying what it counted passed `check`"
                            f"\n{proc.stdout}")
        self.assertIn("FAIL refs-line-self-consistent", proc.stdout)
        self.assertIn("legend", proc.stdout)


#: The supplement's entity line is one half of the (file, line) join that welds
#: a page to its store symbol. Shift it and the join lands on whatever else is
#: at that position -- or on nothing.
JOIN_SHIFT_MUTATION = (
    ('                        "line": child.lineno,      # store has this\n',
     '                        "line": child.lineno + 1,  # store has this\n'),
)

#: Rename every entity in the supplement while leaving every POSITION intact.
#: The join still resolves, the page still shows the right callers -- and the
#: page is titled after an entity that does not exist under that name. This is
#: the mutation `inbound_attribution` cannot see.
SUPPLEMENT_RENAME_MUTATION = (
    ('                    qual = f"{prefix}.{child.name}" if prefix else child.name\n',
     '                    qual = f"{prefix}.{child.name.lower()}" if prefix else child.name.lower()\n'),
)


class EntitySymbolJoinTests(unittest.TestCase):
    """Gate g1: a page's title must agree with the store symbol at its position.

    `extract.py` and `supplement.py` are two independent AST passes over the
    same source, welded by a (file, line) join. This is the check that notices
    them disagreeing about what sits at a position — which is the map landing a
    page on another entity's docstring and another entity's callers."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _make_mixed_repo(self.repo)

    def tearDown(self):
        self._tmp.cleanup()

    def _package(self, subs=()):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return mutated_package(tmp.name, "supplement.py", subs)

    def test_every_page_title_agrees_with_the_store_symbol_it_is_joined_to(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["build", "--root", str(self.repo)]), 0)
        m = checks.MapUnderCheck(self.repo, self.repo / ".code-map", self.repo / "map")

        self.assertTrue(m.entity_pages,
                        "input precondition: the tree must hold entity pages, or this "
                        "check joins nothing and cannot fail")

        self.assertEqual(checks.entity_symbol_join(m), [])

    def test_join_goes_red_when_the_two_ast_passes_disagree_about_a_position(self):
        host = self._package(JOIN_SHIFT_MUTATION)
        self.assertEqual(run_code_map(host, "build", "--root", str(self.repo)).returncode, 0)

        proc = run_code_map(host, "check", "--root", str(self.repo))

        self.assertNotEqual(proc.returncode, 0,
                            "MUTANT SURVIVED: a map whose pages are joined to the wrong "
                            f"position passed `check`\n{proc.stdout}")
        self.assertIn("FAIL entity-symbol-join", proc.stdout)

    def test_join_catches_a_rename_that_every_other_check_agrees_with(self):
        """The independence proof for this check.

        The supplement renames each entity and moves nothing. Every position is
        still right, so the join still resolves, the caller sets are still
        correct, no page is empty, no page is lost and the build is still
        deterministic — every other check in the gate passes. The map is
        nonetheless titling pages after entities that do not exist under that
        name, and only this check says so."""
        host = self._package(SUPPLEMENT_RENAME_MUTATION)
        self.assertEqual(run_code_map(host, "build", "--root", str(self.repo)).returncode, 0)

        proc = run_code_map(host, "check", "--root", str(self.repo))

        self.assertNotEqual(proc.returncode, 0,
                            "MUTANT SURVIVED: a map titling pages after entities that do "
                            f"not exist passed `check`\n{proc.stdout}")
        self.assertIn("FAIL entity-symbol-join", proc.stdout)
        failed_lines = [ln for ln in proc.stdout.splitlines() if ln.startswith("FAIL ")]
        self.assertEqual(
            [ln.split(":")[0] for ln in failed_lines], ["FAIL entity-symbol-join"],
            "if another check also caught this, the independence claim above is "
            f"overstated and must be rewritten, not left standing\n{proc.stdout}")


class FunctionNestedSymbolIdentityTests(unittest.TestCase):
    """Gate g2, defect D2: a definition's symbol carries its whole enclosing
    chain, not just its innermost class.

    Synthetic, and hermetic: the real-corpus arm is
    `RealCorpusNestedSymbolIdentityTests`, which names four collisions this
    repository actually has. This one covers the shape that repository does NOT
    have — a class defined inside a function — and the reader-visible
    consequence of the shape it does."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _make_function_nested_repo(self.repo)

    def tearDown(self):
        self._tmp.cleanup()

    def _sites(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["extract", "--root", str(self.repo)]), 0)
        return contains_sites(self.repo / ".code-map")

    def test_two_closures_in_two_methods_are_two_symbols(self):
        """The shape the four real collisions have."""
        sites = self._sites()

        self.assertNotIn(
            "pkg.nested:Holder.shared", sites,
            "the symbol drops the enclosing method, so both closures are one "
            "symbol and one page carries the other's facts")
        for symbol in ("pkg.nested:Holder.first.shared",
                       "pkg.nested:Holder.second.shared"):
            with self.subTest(symbol=symbol):
                self.assertIn(symbol, sites)
                self.assertEqual(len(sites[symbol]), 1, sites.get(symbol))

    def test_a_class_defined_inside_a_function_is_not_named_as_module_level(self):
        """THE ARM WITH NO REAL-CORPUS INSTANCE, stated rather than implied.

        This repository declares zero classes inside a function, so `4 -> 0` on
        the measured collisions would close the gate with this arm unwritten.
        The fixture is the only place it runs."""
        sites = self._sites()

        for present, absent in (("pkg.nested:outer.Bundle", "pkg.nested:Bundle"),
                                ("pkg.nested:outer.Bundle.method",
                                 "pkg.nested:Bundle.method")):
            with self.subTest(symbol=present):
                self.assertIn(present, sites)
                self.assertNotIn(absent, sites,
                                 "a class defined inside a function is named as "
                                 "if it were module-level")

    def test_each_closure_page_carries_its_own_docstring_and_not_its_sibling_s(self):
        """The reader-visible consequence, which is why the symbol matters.

        Two closures sharing one symbol share one docstring, one caller set and
        one `uses` block. Both pages then state something specific and confident
        about the other closure."""
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["build", "--root", str(self.repo)]), 0)
        pages = self.repo / "map" / "pkg.nested"

        first = (pages / "Holder.first.shared.md").read_text(encoding="utf-8")
        second = (pages / "Holder.second.shared.md").read_text(encoding="utf-8")

        self.assertIn("The first method's closure", first)
        self.assertNotIn("The second method's closure", first)
        self.assertIn("The second method's closure", second)
        self.assertNotIn("The first method's closure", second)


class PageAccountingInvariantTests(unittest.TestCase):
    """Gate g1: every page the map CLAIMS must be a page the map HAS.

    `pages - 1 - modules == entity_pages`, stated against the store rather than
    against the render report's sibling field. Relational, not a baseline: both
    sides are recomputed from the map on every run, so it holds at any corpus
    size and survives every gate that moves the numbers.

    The fixture collides a class named `INDEX` with its own module index, which
    collides on EVERY platform. The real repo's `Verdict`/`verdict` collision
    needs a case-insensitive filesystem, so a fixture built on it would prove
    nothing on Linux — see `RealCorpusPageAccountingInvariantTests` for how that one is
    handled."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _build(self, make):
        make(self.repo)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["build", "--root", str(self.repo)]), 0)
        return checks.MapUnderCheck(self.repo, self.repo / ".code-map", self.repo / "map")

    def _check(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = cli.main(["check", "--root", str(self.repo)])
        return code, buf.getvalue()

    def test_the_page_accounting_invariant_holds_on_an_intact_map(self):
        m = self._build(_make_entity_repo)

        self.assertGreater(len(m.entities), 1,
                           "input precondition: the store must claim entities, or the "
                           "accounting is 1 + modules on both sides and cannot fail")

        self.assertEqual(checks.page_accounting(m), [])

    def test_the_invariant_goes_red_when_two_pages_resolve_to_one_file(self):
        self._build(_make_collision_repo)

        code, out = self._check()

        self.assertNotEqual(code, 0, "a map that lost a page to a filename collision "
                                     "passed `check`\n" + out)
        self.assertIn("FAIL page-accounting", out)
        self.assertIn("a module index the map claims and does not have", out)
        self.assertIn("pkg.thing", out)

    def test_the_invariant_goes_red_when_a_page_is_simply_deleted(self):
        """A different loss than a collision, and the reason the check counts
        the tree instead of looking for collisions: it does not care HOW the
        page went missing."""
        self._build(_make_entity_repo)
        page = self.repo / "map" / "pkg.thing" / "helper.md"
        self.assertTrue(page.exists(), "input precondition: the page must exist to delete")
        page.unlink()

        code, out = self._check()

        self.assertNotEqual(code, 0, "a map missing a page passed `check`\n" + out)
        self.assertIn("FAIL page-accounting", out)
        self.assertIn("pkg.thing:helper", out)

    def test_the_invariant_goes_red_when_the_books_balance_but_a_page_is_gone(self):
        """The reason coverage is asserted on its own and not merely reported
        when the count is off.

        One page deleted and one stray page added: the arithmetic is back in
        balance and the map still advertises a page it does not have. A count
        arm alone calls this healthy."""
        m = self._build(_make_entity_repo)
        before = len(m.pages)
        (self.repo / "map" / "pkg.thing" / "helper.md").unlink()
        (self.repo / "map" / "stray.md").write_text(
            "# not an entity\n", encoding="utf-8", newline="\n")

        m = checks.MapUnderCheck(self.repo, self.repo / ".code-map", self.repo / "map")
        self.assertEqual(len(m.pages), before,
                         "input precondition: the page count must be unchanged, or the "
                         "count arm catches this and the coverage arm proves nothing")

        failures = checks.page_accounting(m)
        self.assertEqual(failures, ["pkg.thing:helper: an entity the map claims and "
                                    "does not have"], failures)


def _filesystem_is_case_insensitive():
    """Does a path written as `A` come back as `a`?

    Measured, never assumed from `sys.platform`: the answer is a property of the
    FILESYSTEM, and a case-sensitive volume on Windows or a case-insensitive one
    on Linux both exist."""
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "CaseProbe.tmp").write_text("x", encoding="utf-8", newline="\n")
        return (Path(d) / "caseprobe.tmp").exists()


CASE_INSENSITIVE_FS = _filesystem_is_case_insensitive()

COLLISION_XFAIL_REASON = (
    "RED BY DESIGN, owned by gate g2. scripts/run_skill_eval.py declares both "
    "`class Verdict` and `def verdict`; their pages resolve to one filename on a "
    "case-insensitive filesystem, so the map advertises 3694 pages and holds 3693. "
    "g1 asserts the loss; g2 renames. strict=True on purpose: when g2 lands the "
    "rename this XPASSes, the run goes RED, and g2 is forced to delete this marker "
    "-- the defect cannot be silently left behind and the check cannot be silently "
    "left disabled. The marker is CONDITIONAL because the collision itself is: on a "
    "case-sensitive filesystem the two are separate files, nothing is lost, and the "
    "assertion below simply passes."
)


class RealCorpusPageAccountingInvariantTests(unittest.TestCase):
    """The accounting invariant against THIS repository.

    A synthetic collision proves the check can fail. This proves it is failing,
    right now, on a real defect — which is stronger evidence than any mutation.

    The build goes to a scratch directory, so the committed `map/` tree is not
    touched and the test needs nothing to be built beforehand."""

    _tmp = None

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        scratch = Path(cls._tmp.name)
        env = dict(os.environ)
        env.pop("FORCE_COLOR", None)
        env.pop("PYTHONIOENCODING", None)
        proc = subprocess.run(
            [sys.executable, "-m", "scripts.code_map", "build", "--root", str(ROOT),
             "--artifacts", str(scratch / "artifacts"), "--out", str(scratch / "map")],
            cwd=str(ROOT), capture_output=True, text=True, env=env)
        if proc.returncode != 0:
            cls._tmp.cleanup()
            raise AssertionError("HARNESS ERROR: the real-corpus build failed, so "
                                 f"nothing below is evidence\n{proc.stderr[-2000:]}")
        cls.m = checks.MapUnderCheck(ROOT, scratch / "artifacts", scratch / "map")

    @classmethod
    def tearDownClass(cls):
        if cls._tmp is not None:
            cls._tmp.cleanup()

    def test_this_repo_declares_two_entities_whose_pages_share_one_filename(self):
        """The input precondition for the xfail below, asserted rather than
        trusted: without a real collision the marker is decoration.

        Two names collide only if they are in the SAME module — that is what
        puts their pages in one directory. `tests.test_map_orient:verdict` is
        another `verdict` in this repo and collides with nothing, so a check
        that only compared leaf names would call it a collision."""
        groups = {}
        for key in self.m.entities:
            module, name = key.split(":", 1)
            groups.setdefault((module, name.lower()), []).append(key)
        collisions = sorted(tuple(sorted(v)) for v in groups.values() if len(v) > 1)

        self.assertEqual(collisions, [("scripts.run_skill_eval:Verdict",
                                       "scripts.run_skill_eval:verdict")],
                         "the collision set moved; the xfail reason below names a "
                         "specific pair and must move with it")

    @pytest.mark.xfail(CASE_INSENSITIVE_FS, strict=True, reason=COLLISION_XFAIL_REASON)
    def test_every_page_this_repo_claims_is_a_page_this_repo_has(self):
        self.assertEqual(checks.page_accounting(self.m), [])


#: The FOUR D2 collisions this repository actually has, NAMED — one row per
#: collision: the merged symbol the extractor used to emit, and the two entities
#: it merged into it. Measured with
#: `.agent-work/issue-456/reference/probe_d2.py`, recorded in
#: `.agent-work/issue-456/reference/d2_collisions.txt`, at the revision that
#: opened gate g2.
#:
#: Named rather than counted on purpose. "All four resolve" passes on an empty
#: set, and it passes on an extractor that quietly stopped emitting nested
#: definitions at all; neither is the thing being asserted.
#:
#: Every row is the same shape: two closures defined in two different METHODS of
#: one class. The old symbol was built from the innermost class on the stack
#: however deep inside a method the definition sat, so the METHOD name — the one
#: thing telling the two apart — was the part that got dropped.
D2_MEASURED_COLLISIONS = (
    ("tests.test_context_determinism:RealCheckoutSkew.project",
     ("tests.test_context_determinism:RealCheckoutSkew."
      "test_a_clean_checkout_differs_only_in_rev_never_in_shape.project",
      "tests.test_context_determinism:RealCheckoutSkew."
      "test_two_checkouts_same_commit_unequal_dirt_on_an_undeclared_file"
      "_agree_on_content.project")),
    ("tests.test_context_manifest:ProducerGuards.explode",
     ("tests.test_context_manifest:ProducerGuards."
      "test_build_manifest_with_both_edges_injected_shells_out_to_nothing.explode",
      "tests.test_context_manifest:ProducerGuards."
      "test_no_globs_or_filesystem_enumeration_anywhere_in_the_producer.explode")),
    ("tests.test_feedback_tooling:InboxLifecycleTests.f",
     ("tests.test_feedback_tooling:InboxLifecycleTests._filer.f",
      "tests.test_feedback_tooling:InboxLifecycleTests._recorder.f")),
    ("tests.test_install_constellation:InterpreterProbeTests.fake_run",
     ("tests.test_install_constellation:InterpreterProbeTests."
      "test_probe_prefers_py_over_python3_when_both_succeed.fake_run",
      "tests.test_install_constellation:InterpreterProbeTests."
      "test_probe_timeout_candidate_falls_through_without_hanging.fake_run")),
)


class RealCorpusNestedSymbolIdentityTests(unittest.TestCase):
    """Gate g2, defect D2, against THIS repository.

    A synthetic fixture proves the rule. This proves the rule was broken here,
    on four named entities, right now — which is stronger evidence than any
    fixture.

    Only `extract` runs. The defect is in the statement store, and rendering
    3,600 pages to read four symbols would pay for the whole pipeline to observe
    one stage of it. The store goes to a scratch directory, so the committed
    tree is untouched."""

    _tmp = None

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        scratch = Path(cls._tmp.name)
        proc = run_code_map(ROOT, "extract", "--root", str(ROOT),
                            "--artifacts", str(scratch / "artifacts"))
        if proc.returncode != 0:
            cls._tmp.cleanup()
            raise AssertionError("HARNESS ERROR: the real-corpus extraction failed, "
                                 f"so nothing below is evidence\n{proc.stderr[-2000:]}")
        cls.sites = contains_sites(scratch / "artifacts")

    @classmethod
    def tearDownClass(cls):
        if cls._tmp is not None:
            cls._tmp.cleanup()

    def test_the_four_measured_collisions_are_four_pairs_of_distinct_symbols(self):
        """Each named pair, by string."""
        for merged, entities in D2_MEASURED_COLLISIONS:
            with self.subTest(merged=merged):
                for entity in entities:
                    self.assertEqual(
                        len(self.sites.get(entity, ())), 1,
                        f"{entity} is not in the store exactly once under its own "
                        f"qualified name")
                self.assertFalse(
                    merged in self.sites,
                    f"{merged} is still emitted, so the enclosing method is still "
                    f"being dropped")

    def test_no_definition_symbol_is_emitted_at_two_positions(self):
        """The whole corpus, not only the four named above.

        A symbol emitted at two definition sites is two entities wearing one
        name, and every fact the map holds about either of them lands on both.
        The named test above is what keeps this one from passing on an extractor
        that emits nothing."""
        self.assertGreater(len(self.sites), 3000,
                           "input precondition: the store must hold this "
                           "repository's definitions, or this scan reads nothing")

        merged = {symbol: places for symbol, places in self.sites.items()
                  if len(places) > 1}

        self.assertEqual(merged, {})


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
