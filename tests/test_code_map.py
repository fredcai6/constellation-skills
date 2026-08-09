"""Tests for scripts/code_map/ — the derived code map (issue #456, gate g0).

Gate g0 introduces exactly two behaviors of its own: the discovery layer that
enumerates the **mappable corpus**, and the argparse CLI. Those two are
test-first. The pipeline stages (extract, render) are a port of the reference prototype
and are covered by end-to-end evidence, not by unit tests that would freeze
prototype behavior gates g2/g3 are going to change. A third stage, a second AST
pass over the same source, was removed at g3 when the statement schema learned
to say the six facts it had been fetching.

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

import ast
import contextlib
import difflib
import inspect
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

from scripts.code_map import checks, cli, discovery, extract, render, thresholds  # noqa: E402

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


_SCHEMA_SOURCE = '''"""A module carrying every fact the statement schema must hold.

This second paragraph is the docstring BODY. The store used to keep only the
summary line, so a reader who wanted the Args section had to open the file.
"""
__all__ = ["Gadget", "spin_up"]

WIDTH: int = 7
NAME = "gadget"


class Gadget:
    """A gadget."""

    slots: int = 3
    label: str

    @property
    def size(self):
        """How big it is."""
        return self.slots


async def spin_up(gadget: Gadget, *, times: int = 2) -> int:
    """Spin the gadget up.

    Args:
        times: how many turns to take.
    """
    return times


with open(__file__) as _f:
    def inside_a_with_block():
        """Defined inside a `with`, which is still a definition (tc34)."""
        return 4
'''


def _make_schema_repo(tmp: Path):
    """A repo exercising every field the statement schema has to carry at once.

    One module, because the subject is the schema of a line and not the shape of
    a corpus: a module docstring with a body, `__all__`, an annotated and a bare
    module constant, a class with an annotated field and an annotation-only
    field, a decorated property, an async function with annotations, a keyword
    default and a return type -- and a definition inside a `with` block, which
    the supplement stage could not see at all (`tc34`)."""
    (tmp / "pkg").mkdir()
    (tmp / "pkg" / "__init__.py").write_text("", encoding="utf-8", newline="\n")
    (tmp / "pkg" / "shape.py").write_text(_SCHEMA_SOURCE, encoding="utf-8", newline="\n")
    _git("init", "-q", cwd=tmp)
    _git("add", "pkg/__init__.py", "pkg/shape.py", cwd=tmp)


def statements_of(artifacts):
    """Every line of the statement store, as dicts, read straight off disk.

    Never through `render.load_stores`: gate g3's whole subject is what the
    store's own schema says, and asking the renderer would ask the code under
    test what it thinks it wrote."""
    with open(Path(artifacts) / "statements.jsonl", encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def physical_line_of(source, needle):
    """The 1-based line of `needle` in `source` -- GROUND TRUTH for the line
    base, read from the source text and from nothing the extractor produced.

    A line base cannot be checked against the store that declares it. It can
    only be checked against the file both of them are talking about."""
    hits = [i for i, line in enumerate(source.splitlines(), start=1)
            if needle in line]
    if len(hits) != 1:
        raise HarnessError(
            f"HARNESS ERROR: {needle!r} occurs {len(hits)} time(s) in the fixture, "
            f"expected exactly 1; the ground truth is not a single line")
    return hits[0]


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
        statements = statements_of(self.repo / ".code-map")
        modules = sum(1 for st in statements if st["p"] == "extraction-window")
        entities = sum(1 for st in statements if st["p"] == "contains")
        return 1 + modules + entities

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


def _group_statement_lines_by_file(text):
    """`statements.jsonl` text -> {source file: [its own lines, in order]},
    grouped in FIRST-SEEN order. Each file's own line order is untouched --
    that reflects the AST's own traversal of that one file, not the order
    files were visited -- only the file-to-file grouping is exposed so a
    caller can permute IT."""
    groups = {}
    for line in text.splitlines():
        if not line:
            continue
        rec = json.loads(line)
        groups.setdefault(rec["q"]["file"], []).append(line)
    return groups


def _permuted_statements(text):
    """The SAME statements a real extraction produced, as if the extractor
    had walked the corpus in the OPPOSITE file order. `discover_corpus`
    always returns a sorted list, so this is the cheapest way to exercise a
    visit order the real pipeline would never itself produce by accident --
    deterministic and reversible, not a random shuffle, so a failure here is
    reproducible."""
    groups = _group_statement_lines_by_file(text)
    out_lines = []
    for f in reversed(list(groups)):
        out_lines.extend(groups[f])
    return "\n".join(out_lines) + "\n"


_MULTI_CALLER_TARGET_SOURCE = '''"""The module two other modules point at, never its own."""


def target():
    """Called from two other modules."""
    return 1
'''

_MULTI_CALLER_ALPHA_SOURCE = '''"""Calls target once."""
from pkg.callee import target


def a():
    """Call target."""
    return target()
'''

_MULTI_CALLER_BETA_SOURCE = '''"""Calls target once."""
from pkg.callee import target


def b():
    """Call target."""
    return target()
'''


def _make_multi_caller_repo(tmp: Path):
    """`pkg.callee:target` is called from TWO other modules and never from its
    own, so its EXTERNAL caller list has more than one element -- a removed
    sort has somewhere to disagree. `_make_cross_module_repo` has only one
    external caller module, and a one-element list orders the same with or
    without a sort, so tc32 needs its own fixture with cardinality >= 2."""
    (tmp / "pkg").mkdir()
    (tmp / "pkg" / "__init__.py").write_text("", encoding="utf-8", newline="\n")
    (tmp / "pkg" / "callee.py").write_text(_MULTI_CALLER_TARGET_SOURCE, encoding="utf-8", newline="\n")
    (tmp / "pkg" / "alpha.py").write_text(_MULTI_CALLER_ALPHA_SOURCE, encoding="utf-8", newline="\n")
    (tmp / "pkg" / "beta.py").write_text(_MULTI_CALLER_BETA_SOURCE, encoding="utf-8", newline="\n")
    _git("init", "-q", cwd=tmp)
    _git("add", "pkg/__init__.py", "pkg/callee.py", "pkg/alpha.py", "pkg/beta.py", cwd=tmp)


#: tc32: delete the ONE `sorted(...)` governing caller-list order (see
#: `_bucket_line`'s own docstring for why there is only one). Without it, the
#: rendered order tracks `Counter` insertion order, which tracks the order
#: statements were visited -- exactly the failure a permuted visit order is
#: built to expose.
CALLER_ORDER_MUTATION = (
    ("    ext = sorted(m for m in counter if m != mod)\n",
     "    ext = [m for m in counter if m != mod]\n"),
)


class CallerOrderStableUnderPermutedVisitTests(unittest.TestCase):
    """tc32: a green `deterministic-rebuild` is NOT evidence that caller
    ordering is stable. That check compares two builds of the SAME tree in
    the SAME visit order, so it would stay green even if the caller list were
    ordered by dict/Counter insertion -- both runs would insert in the same
    order and agree with each other while both being visit-order-dependent.

    This builds the SAME statement store twice into a rendered page tree,
    permuting only which FILE's statements the store lists first, and asserts
    the rendered caller lists are byte-identical either way. Proven
    red-before-green: `_bucket_line` sorts the external caller list today,
    but nothing forced that -- deleting the sort via a mutated package copy
    reproduces the exact failure this test exists to catch."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _make_multi_caller_repo(self.repo)

    def tearDown(self):
        self._tmp.cleanup()

    def _extract_statements(self):
        artifacts = self.repo / ".code-map"
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["extract", "--root", str(self.repo),
                                       "--artifacts", str(artifacts)]), 0)
        return (artifacts / extract.STATEMENTS_NAME).read_text(encoding="utf-8")

    def test_caller_lists_are_byte_identical_under_a_permuted_visit_order(self):
        text = self._extract_statements()
        groups = _group_statement_lines_by_file(text)
        self.assertGreater(len(groups), 1,
                           "input precondition: need more than one file's "
                           "statements, or there is no visit order to permute")

        canonical_out = self.repo / "map-canonical"
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["render", "--root", str(self.repo),
                                       "--artifacts", str(self.repo / ".code-map"),
                                       "--out", str(canonical_out)]), 0)
        target_page = (canonical_out / "pkg.callee" / "target.md").read_text(encoding="utf-8")
        stated = checks.parse_refs(checks.refs_lines(target_page)[0])
        self.assertGreaterEqual(
            stated.modules, 2,
            "input precondition: the fixture's target must have at least 2 "
            "external caller modules, or a one-element list orders the same "
            "with or without a sort and this proves nothing")

        permuted_artifacts = self.repo / ".code-map-permuted"
        permuted_artifacts.mkdir()
        (permuted_artifacts / extract.STATEMENTS_NAME).write_text(
            _permuted_statements(text), encoding="utf-8", newline="\n")
        permuted_out = self.repo / "map-permuted"
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["render", "--root", str(self.repo),
                                       "--artifacts", str(permuted_artifacts),
                                       "--out", str(permuted_out)]), 0)

        diff = checks.tree_diff(canonical_out, permuted_out)
        self.assertEqual(diff, [], diff)

    def test_falsifier_bites_when_the_caller_order_sort_is_deleted(self):
        text = self._extract_statements()
        groups = _group_statement_lines_by_file(text)
        self.assertGreater(len(groups), 1,
                           "input precondition: need more than one file's "
                           "statements, or there is no visit order to permute")
        permuted_text = _permuted_statements(text)

        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        host = mutated_package(tmp.name, "render.py", CALLER_ORDER_MUTATION)

        canonical_artifacts = Path(tmp.name) / "artifacts-canonical"
        canonical_artifacts.mkdir()
        (canonical_artifacts / extract.STATEMENTS_NAME).write_text(
            text, encoding="utf-8", newline="\n")
        canonical_out = Path(tmp.name) / "map-canonical"
        proc = run_code_map(host, "render", "--root", str(self.repo),
                            "--artifacts", str(canonical_artifacts),
                            "--out", str(canonical_out))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

        permuted_artifacts = Path(tmp.name) / "artifacts-permuted"
        permuted_artifacts.mkdir()
        (permuted_artifacts / extract.STATEMENTS_NAME).write_text(
            permuted_text, encoding="utf-8", newline="\n")
        permuted_out = Path(tmp.name) / "map-permuted"
        proc = run_code_map(host, "render", "--root", str(self.repo),
                            "--artifacts", str(permuted_artifacts),
                            "--out", str(permuted_out))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

        diff = checks.tree_diff(canonical_out, permuted_out)
        self.assertNotEqual(
            diff, [],
            "MUTANT SURVIVED: caller lists matched across a permuted visit "
            "order even with the ordering sort deleted -- the falsifier does "
            "not actually distinguish visit-order-dependent rendering")


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
        self.assertIn("as production callers", proc.stdout)


#: The renderer leaves the page's OWN module out of the named caller list,
#: because the count already accounts for it. Name it anyway and the line
#: contradicts its own convention -- visible without reading the store at all.
OWN_MODULE_NAMED_MUTATION = (
    ("    ext = sorted(m for m in counter if m != mod)\n",
     "    ext = sorted(m for m in counter)\n"),
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
                       + "\nreferenced by (production): 1 sites in 3 modules (a, b, c)\n",
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
    ("    L.append(REFS_LEGEND)\n",
     "    pass\n"),
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
        lines = checks.refs_lines(m.text(page))
        self.assertEqual(len(lines), 2, lines)
        # the fixture has no test-shaped module, so every one of the fixture's
        # 5 sites lands in the production bucket -- that is the line this test
        # exercises; the tests bucket is `none found` and not the point here.
        prod = [ln for ln in lines if ln.startswith(checks.REFS_PROD_PREFIX)]
        self.assertEqual(len(prod), 1, lines)
        stated = checks.parse_refs(prod[0])
        self.assertIsNotNone(stated, prod[0])

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
            f"{self.TARGET_OWN} in this module", prod[0],
            f"the line {prod[0]!r} counts {stated.sites} sites across "
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
            refs_idx = [i for i, ln in enumerate(lines) if checks.refs_prefix_of(ln) is not None]
            if not refs_idx:
                continue
            seen += 1
            last = refs_idx[-1]
            follower = lines[last + 1] if last + 1 < len(lines) else ""
            self.assertTrue(
                follower.startswith("counted:") and "not counted:" in follower,
                f"{m.rel(page)}: the inbound lines are not followed by "
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


_SPLIT_TARGET_SOURCE = '''"""The module a production caller and a test both point at."""


def target():
    """Called from production and from a test."""
    return 1
'''

_SPLIT_ONLY_TESTS_SOURCE = '''"""A helper only a test calls -- never referenced by production."""


def helper():
    """Used by a test only."""
    return 2
'''

_SPLIT_PROD_CALLER_SOURCE = '''"""A production module that calls target. Nothing calls this one."""
from pkg.callee import target


def use():
    """Call target from production code."""
    return target()
'''

_SPLIT_TEST_MODULE_SOURCE = '''"""A pytest-shaped test module -- exercises target and helper."""
from pkg.callee import target
from pkg.only_tests import helper


def test_target():
    """Call target once and helper twice."""
    target()
    helper()
    helper()
'''


def _make_prod_test_split_repo(tmp: Path):
    """A repo shaped to exercise every fact gate g5's split must distinguish:
    an entity called from BOTH production and a test (`pkg.callee:target`), an
    entity called ONLY from a test (`pkg.only_tests:helper`), an entity nothing
    calls at all (`pkg.caller:use`), and an entity DEFINED INSIDE a
    pytest-shaped test module (`tests.test_thing:test_target`) whose own
    zero-inbound line must read as expected rather than alarming."""
    (tmp / "pkg").mkdir()
    (tmp / "pkg" / "__init__.py").write_text("", encoding="utf-8", newline="\n")
    (tmp / "pkg" / "callee.py").write_text(_SPLIT_TARGET_SOURCE, encoding="utf-8", newline="\n")
    (tmp / "pkg" / "only_tests.py").write_text(_SPLIT_ONLY_TESTS_SOURCE, encoding="utf-8", newline="\n")
    (tmp / "pkg" / "caller.py").write_text(_SPLIT_PROD_CALLER_SOURCE, encoding="utf-8", newline="\n")
    (tmp / "tests").mkdir()
    (tmp / "tests" / "__init__.py").write_text("", encoding="utf-8", newline="\n")
    (tmp / "tests" / "test_thing.py").write_text(_SPLIT_TEST_MODULE_SOURCE, encoding="utf-8", newline="\n")
    _git("init", "-q", cwd=tmp)
    _git("add", "pkg/__init__.py", "pkg/callee.py", "pkg/only_tests.py", "pkg/caller.py",
         "tests/__init__.py", "tests/test_thing.py", cwd=tmp)


class ProductionTestCallerSplitTests(unittest.TestCase):
    """Gate g5: split the caller list into production and test callers, and
    make a test-defined entity's inbound line say something true instead of
    something alarming. `referenced by: none found` today conflates three
    different facts -- dead in production and in tests, exercised by tests
    only, and IS a test (so zero inbound is the normal state) -- and a reader
    cannot tell which one a bare line means without opening another page."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _make_prod_test_split_repo(self.repo)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["build", "--root", str(self.repo)]), 0)

    def tearDown(self):
        self._tmp.cleanup()

    def _page(self, mod, name):
        return (self.repo / "map" / mod / f"{name}.md").read_text(encoding="utf-8")

    def test_an_entity_called_from_both_production_and_a_test_splits_the_two(self):
        text = self._page("pkg.callee", "target")
        self.assertIn(
            "referenced by (production): 1 sites in 1 modules (pkg.caller)", text,
            f"the production/test split must be visible on the page itself:\n{text}")
        self.assertIn(
            "referenced by (tests): 1 sites in 1 modules (tests.test_thing)", text,
            f"the test caller must be counted separately from the production one:\n{text}")

    def test_an_entity_called_only_from_tests_says_so_on_the_production_line(self):
        text = self._page("pkg.only_tests", "helper")
        self.assertIn(
            "referenced by (production): none found", text,
            f"an entity nothing in production calls must say so, even though a "
            f"test calls it:\n{text}")
        self.assertIn(
            "referenced by (tests): 2 sites in 1 modules (tests.test_thing)", text,
            f"the fact 'only tests use it' must be a distinct, visible line from "
            f"'nothing calls it':\n{text}")

    def test_a_truly_unused_entity_reads_none_found_on_both_lines(self):
        text = self._page("pkg.caller", "use")
        self.assertIn("referenced by (production): none found", text)
        self.assertIn("referenced by (tests): none found", text,
                      f"an entity dead in BOTH production and tests must not read "
                      f"the same as one only tests use:\n{text}")

    def test_a_test_defined_entity_carries_an_honest_note_not_a_bare_none_found(self):
        text = self._page("tests.test_thing", "test_target")
        self.assertIn(render.TEST_NOTE, text,
                      f"a page whose OWN entity is defined in a test module must say "
                      f"so -- zero inbound there is the normal state, not a finding:\n{text}")
        self.assertIn("referenced by (production): none found", text)
        self.assertIn("referenced by (tests): none found", text)

    def test_a_production_defined_entity_carries_no_test_defined_note(self):
        text = self._page("pkg.callee", "target")
        self.assertNotIn(render.TEST_NOTE, text,
                         f"a production entity must not be told it is a test:\n{text}")

    def test_the_page_states_what_the_split_is_derived_from(self):
        """Close criterion: the predicate is derived from a published convention
        and the page (or report) says what it was based on."""
        text = self._page("pkg.callee", "target")
        self.assertIn(render.SPLIT_LEGEND, text)
        self.assertIn("pytest", render.SPLIT_LEGEND.lower())
        self.assertIn("test_", render.SPLIT_LEGEND)

    def test_the_legend_states_the_rule_the_predicate_actually_applies(self):
        """SPLIT_LEGEND is a claim about is_test_module's code, not decoration.

        is_test_module's layout half is `"tests" in parts` -- a `tests`
        segment ANYWHERE on the dotted path, not just a top-level one (the
        Django-style app-local `pkg/tests/` layout is a real, common one). If
        the legend ever claims a narrower TOP-LEVEL-only rule while the
        predicate keeps matching anywhere, the page states something false
        about its own code -- the defect this gate exists to close.

        The two assertions guard both directions of drift: the behavioural
        pin (a NESTED tests package still classifies as a test module) fails
        if the predicate is ever narrowed without this test being touched;
        the wording assertion fails if the legend is ever worded back to
        overclaim TOP-LEVEL-only scope.

        Falsifier grade A: reproduces on real input today. RED against the
        unfixed legend (it says "a top-level tests package"); GREEN once the
        legend is reworded to state the rule the code applies."""
        nested = "pkg.sub.tests.helper"
        self.assertTrue(
            render.is_test_module(nested),
            "input precondition: a nested (non-top-level) tests package must "
            "classify as a test module in render.py's copy")
        self.assertTrue(
            checks.is_test_module(nested),
            "input precondition: a nested (non-top-level) tests package must "
            "classify as a test module in checks.py's independent copy")

        for legend in (render.SPLIT_LEGEND, checks.SPLIT_LEGEND):
            self.assertNotIn(
                "top-level", legend,
                f"the legend claims a TOP-LEVEL tests package while "
                f"is_test_module matches a `tests` segment anywhere on the "
                f"path -- {legend!r} overclaims what the code does")


#: Break SIDE A of the comparison: the EXTRACTOR's name for a definition.
#: Positions are untouched, so the map still builds, every page still lands and
#: every caller list is still internally consistent -- the pages are simply
#: titled after entities that do not exist under that name.
EXTRACTOR_RENAME_MUTATION = (
    ('        return base + name if base.endswith(":") else base + "." + name\n',
     '        return base + name.lower() if base.endswith(":") '
     'else base + "." + name.lower()\n'),
)

#: Break SIDE B: the CHECK's own reading of the source. Drop the enclosing
#: chain, so a method reads as a module-level function. If breaking this side
#: does not go red, the check is not really consulting it.
SOURCE_SCAN_FLATTEN_MUTATION = (
    ('                qualified = f"{prefix}.{child.name}" if prefix else child.name\n',
     '                qualified = child.name\n'),
)

#: Break the POSITION the two sides are joined on: emit lines one off while the
#: schema goes on declaring the base it always declared. This is defect D1 as a
#: mutation, and it is what gives the declared line base a consumer that can go
#: red.
POSITION_SHIFT_MUTATION = (
    ("    return lineno - 1 + LINE_BASE\n", "    return lineno + LINE_BASE\n"),
)


class EntitySymbolJoinTests(unittest.TestCase):
    """Gate g1, RE-BASED at g3: a page's title must be what the SOURCE defines
    at the position the store records.

    This check used to compare the extractor's symbol against a second AST
    pass's qualified key. `g3` deleted that second pass. Left standing on one
    derivation the check would have compared the store symbol against a page
    title rendered FROM that symbol — a tautology that cannot fail, which is the
    exact defect this run exists to stamp out and would have arrived here
    through a legitimate refactor.

    The second derivation now lives in `checks.SourceScan`, which reads the
    source and shares no code path with `extract.py`. The three mutations below
    are the independence proof: break the extractor's naming, break the check's
    own reading, break the position they are joined on, and the check goes red
    for each."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _make_mixed_repo(self.repo)

    def tearDown(self):
        self._tmp.cleanup()

    def _package(self, module, subs):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return mutated_package(tmp.name, module, subs)

    def _checked(self, module, subs):
        host = self._package(module, subs)
        self.assertEqual(
            run_code_map(host, "build", "--root", str(self.repo)).returncode, 0)
        return run_code_map(host, "check", "--root", str(self.repo))

    def test_every_page_title_agrees_with_the_source_at_its_position(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["build", "--root", str(self.repo)]), 0)
        m = checks.MapUnderCheck(self.repo, self.repo / ".code-map", self.repo / "map")

        self.assertTrue(m.entity_pages,
                        "input precondition: the tree must hold entity pages, or this "
                        "check compares nothing and cannot fail")
        self.assertTrue(m.source.qualified_at,
                        "input precondition: the source scan must find definitions, or "
                        "the second derivation is empty and agrees with anything")

        self.assertEqual(checks.entity_symbol_join(m), [])

    def test_the_two_derivations_do_not_share_a_code_path(self):
        """Stated as a test because it is the property the check rests on.

        `checks.py` imports two names from `extract.py` — the store's filename
        and the window predicate. Neither is a symbol derivation. If a later
        gate imports the naming itself, this check becomes a restatement and
        this test is what says so."""
        source = (CODE_MAP / "checks.py").read_text(encoding="utf-8")
        imported = re.findall(r"^from \.extract import (.+)$", source, re.M)

        self.assertEqual(imported, ["STATEMENTS_NAME, WINDOW"])
        for borrowed in ("child_sym", "Extractor", "mod_of", "store_line"):
            with self.subTest(name=borrowed):
                self.assertNotIn(borrowed, source)

    def test_join_goes_red_when_the_extractor_renames_a_definition(self):
        """SIDE A. Every position is still right, so the caller lists are still
        correct, no page is empty, no page is lost and the build is still
        deterministic. The map is nonetheless titling pages after entities that
        do not exist under that name."""
        proc = self._checked("extract.py", EXTRACTOR_RENAME_MUTATION)

        self.assertNotEqual(proc.returncode, 0,
                            "MUTANT SURVIVED: a map titling pages after entities that "
                            "do not exist passed `check`\n" + proc.stdout)
        self.assertIn("FAIL entity-symbol-join", proc.stdout)

    def test_join_goes_red_when_the_checks_own_reading_of_the_source_breaks(self):
        """SIDE B. A check nobody can break on its own side is a check that is
        not consulting that side."""
        proc = self._checked("checks.py", SOURCE_SCAN_FLATTEN_MUTATION)

        self.assertNotEqual(proc.returncode, 0,
                            "MUTANT SURVIVED: the check's own second derivation was "
                            "flattened and it still agreed\n" + proc.stdout)
        self.assertIn("FAIL entity-symbol-join", proc.stdout)

    def test_join_goes_red_when_the_recorded_position_shifts(self):
        """The position the two sides meet on — and the live consumer that makes
        the declared line base worth declaring."""
        proc = self._checked("extract.py", POSITION_SHIFT_MUTATION)

        self.assertNotEqual(proc.returncode, 0,
                            "MUTANT SURVIVED: definitions recorded one line off the "
                            "source passed `check`\n" + proc.stdout)
        self.assertIn("FAIL entity-symbol-join", proc.stdout)


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


_LEDGER_SOURCE = '''"""A module declaring two entities whose names differ only by case."""


class Ledger:
    """The book of record."""

    def post(self):
        """Add an entry."""
        return 1


def ledger():
    """Open one."""
    return Ledger()
'''


def _make_case_collision_repo(tmp: Path):
    """A FRESH case-only pair, with nothing to do with `Verdict`.

    `pkg.book:Ledger` and `pkg.book:ledger` are two entities in one module, so
    their pages land in one directory, and the renderer used to name each page
    after the entity alone -- one filename on a case-insensitive filesystem.

    A fix that only resolved the pair it was shown could not fail on the next
    pair, which is why the proof runs on a pair the fix never saw."""
    (tmp / "pkg").mkdir()
    (tmp / "pkg" / "__init__.py").write_text("", encoding="utf-8", newline="\n")
    (tmp / "pkg" / "book.py").write_text(_LEDGER_SOURCE, encoding="utf-8", newline="\n")
    _git("init", "-q", cwd=tmp)
    _git("add", "pkg/__init__.py", "pkg/book.py", cwd=tmp)


class CaseOnlyPageIdentityTests(unittest.TestCase):
    """Gate g2, defect (c): two entity names that differ only by case must not
    resolve to one page.

    TWO ARMS, and each is red on only ONE kind of filesystem — which is exactly
    why both are here. On a case-insensitive filesystem the second write
    destroys the first, so an entity the map claims has no page; on a
    case-sensitive one both files exist and nothing is lost, so the loss arm
    cannot fail and the folding arm is what sees the latent collision. Together
    they are red on every platform, and a fix that satisfies only one of them is
    not a fix."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _make_case_collision_repo(self.repo)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["build", "--root", str(self.repo)]), 0)
        self.m = checks.MapUnderCheck(self.repo, self.repo / ".code-map",
                                      self.repo / "map")

    def tearDown(self):
        self._tmp.cleanup()

    def test_the_fixture_really_declares_a_case_only_pair(self):
        """Input precondition. Without two keys that fold to one name both arms
        below are vacuous, and the whole class passes on a renderer that emits
        no pages at all."""
        groups = {}
        for key in self.m.entities:
            module, name = key.split(":", 1)
            groups.setdefault((module, name.lower()), []).append(key)
        collisions = sorted(tuple(sorted(v)) for v in groups.values() if len(v) > 1)

        self.assertEqual(collisions, [("pkg.book:Ledger", "pkg.book:ledger")])

    def test_every_entity_the_map_claims_is_an_entity_the_map_has_a_page_for(self):
        """RED on a case-insensitive filesystem: one page overwrote the other."""
        self.assertEqual(checks.page_accounting(self.m), [])

    def test_no_two_page_filenames_in_one_directory_fold_to_the_same_name(self):
        """RED on a case-sensitive filesystem, where nothing is lost and the
        collision is only latent: two files, one folded name, and the map breaks
        the moment it is checked out on Windows or macOS."""
        folded = {}
        for page in self.m.pages:
            folded.setdefault((page.parent, page.name.lower()), []).append(page.name)
        clashes = sorted(sorted(v) for v in folded.values() if len(v) > 1)

        self.assertEqual(clashes, [],
                         "two pages in one directory differ only by case, so the "
                         "tree cannot survive a case-insensitive filesystem")

    def test_every_link_the_map_writes_points_at_a_page_that_exists(self):
        """The other half of renaming a page: the links that reach it.

        Falsifier grade B — green before the fix, because on a case-insensitive
        filesystem both spellings open the one surviving file. It is red the
        moment a fix renames pages and forgets the module index or the parent
        entity's child list, which is the obvious way to get this wrong."""
        dangling = []
        for page in self.m.pages:
            for target in re.findall(r"\]\(([^)]+)\)", self.m.text(page)):
                if not (page.parent / target).exists():
                    dangling.append(f"{self.m.rel(page)} -> {target}")

        self.assertEqual(dangling, [])


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

    def test_this_repo_declares_two_entities_whose_names_differ_only_by_case(self):
        """The input precondition for the invariant below, asserted rather than
        trusted: with no case-only pair in the corpus, the assertion that
        follows would pass on a renderer that never disambiguated anything.

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
                         "the case-only pair set moved; the assertion below is "
                         "only evidence while this repository still has one")

    def test_every_page_this_repo_claims_is_a_page_this_repo_has(self):
        """Was `xfail(strict=True)` through gate g1, because `Verdict` and
        `verdict` landed on one file and the map advertised 3694 pages while
        holding 3693. `g2` made the collision impossible by construction, the
        marker XPASSed, and `strict` forced it off — which is what it was for."""
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
        for name in ("discover", "extract", "render", "build", "check"):
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
    """`build` is the whole pipeline's caller. This asserts that the stages are
    WIRED and produce their artifacts — not what they put in them.

    Two stages now, not three: `g3` folded the second AST pass's six facts into
    the statement schema and removed the stage rather than deprecating it."""

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
        for produced in (".code-map/statements.jsonl",
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


#: Emit the definition line 1-based while the schema goes on declaring the base
#: it always declared. This is defect D1 as a mutation: the store and its own
#: declaration disagree, and every reader who trusts the declaration is off by
#: one and never told.
LINE_BASE_SILENT_FLIP = (
    ("    return lineno - 1 + LINE_BASE\n",
     "    return lineno + LINE_BASE\n"),
)

#: Flip the DECLARED base. The emission follows it, so the store stays honest --
#: what this must not be is silent, because every consumer inherits the base.
LINE_BASE_DECLARED_FLIP = (
    ("LINE_BASE = 0\n", "LINE_BASE = 1\n"),
)


class StatementSchemaLineBaseTests(unittest.TestCase):
    """Gate g3, defect D1: the line base is DECLARED, not implied.

    The store has always been 0-based and the schema has always been silent
    about it. The proof of the silence was the renderer's bare `+1` at the read
    site: a reader who trusted the schema was off by one and had nothing to
    check against. The base is now declared by an extraction-window statement,
    one per file the extractor actually read.

    The declaration is checked against the SOURCE TEXT, never against the store
    that makes it. A store cannot corroborate its own convention."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _make_schema_repo(self.repo)

    def tearDown(self):
        self._tmp.cleanup()

    def _extract(self, host=None):
        if host is None:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(cli.main(["extract", "--root", str(self.repo)]), 0)
        else:
            self.assertEqual(
                run_code_map(host, "extract", "--root", str(self.repo)).returncode, 0)
        return statements_of(self.repo / ".code-map")

    def _package(self, subs):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return mutated_package(tmp.name, "extract.py", subs)

    @staticmethod
    def _windows(statements):
        return [st for st in statements if st["p"] == "extraction-window"]

    @staticmethod
    def _definition_line(statements, symbol):
        lines = [st["q"]["line"] for st in statements
                 if st["p"] == "contains" and st["o"] == symbol]
        if len(lines) != 1:
            raise HarnessError(
                f"HARNESS ERROR: {symbol} has {len(lines)} definition statements, "
                f"expected exactly 1")
        return lines[0]

    def test_line_base_is_declared_once_for_every_file_the_extractor_read(self):
        statements = self._extract()
        windows = self._windows(statements)

        self.assertEqual(sorted(st["q"]["file"] for st in windows),
                         ["pkg/__init__.py", "pkg/shape.py"],
                         "a file the extractor read and did not declare a window for "
                         "is a file whose absent facts a reader cannot tell from "
                         "facts that are not there")
        for window in windows:
            with self.subTest(file=window["q"]["file"]):
                self.assertIn("line_base", window["d"])

    def test_line_base_declaration_agrees_with_the_source_text(self):
        """The assertion that fails if the base flips underneath the schema."""
        statements = self._extract()
        base = {st["d"]["line_base"] for st in self._windows(statements)}
        self.assertEqual(len(base), 1, f"the store declares {base} as its line base")
        base = base.pop()

        for symbol, needle in (("pkg.shape:Gadget", "class Gadget:"),
                               ("pkg.shape:spin_up", "async def spin_up"),
                               ("pkg.shape:inside_a_with_block",
                                "def inside_a_with_block")):
            with self.subTest(symbol=symbol):
                stored = self._definition_line(statements, symbol)
                self.assertEqual(
                    stored + (1 - base),
                    physical_line_of(_SCHEMA_SOURCE, needle),
                    f"{symbol} is stored at line {stored} under a declared base of "
                    f"{base}, which is not where it is in the file")

    def test_line_base_is_zero_so_a_flip_is_a_deliberate_change(self):
        """Pinned, because every consumer inherits it.

        Not a corpus baseline: the base is a decision, and the point of
        declaring it is that changing it is an act rather than a drift. A gate
        that means to move it edits this line and says why."""
        statements = self._extract()

        self.assertEqual({st["d"]["line_base"] for st in self._windows(statements)},
                         {0})

    def test_line_base_check_goes_red_when_the_emission_flips_silently(self):
        """Attack: emit 1-based lines, keep declaring 0.

        Nothing else in the pipeline notices -- the offsets are internally
        consistent, so pages still render and the map still builds. Only a
        comparison against the source text sees it."""
        statements = self._extract(self._package(LINE_BASE_SILENT_FLIP))
        base = {st["d"]["line_base"] for st in self._windows(statements)}.pop()

        stored = self._definition_line(statements, "pkg.shape:Gadget")

        self.assertNotEqual(
            stored + (1 - base), physical_line_of(_SCHEMA_SOURCE, "class Gadget:"),
            "MUTANT SURVIVED: the store emitted a base it did not declare and the "
            "declaration still looked right")

    def test_line_base_declaration_follows_a_deliberate_flip(self):
        """The other half: move the base ON PURPOSE and the store stays honest.

        This is what makes the declaration worth having. A schema that could
        only ever say `0` would be a constant, not a declaration -- and the
        source-text check above would pass for the wrong reason."""
        statements = self._extract(self._package(LINE_BASE_DECLARED_FLIP))
        base = {st["d"]["line_base"] for st in self._windows(statements)}.pop()

        self.assertEqual(base, 1)
        self.assertEqual(
            self._definition_line(statements, "pkg.shape:Gadget") + (1 - base),
            physical_line_of(_SCHEMA_SOURCE, "class Gadget:"))


class StatementSchemaFactsTests(unittest.TestCase):
    """Gate g3: ONE schema carries every fact the map renders.

    Six facts used to require a second AST pass over the same source, because
    the statement vocabulary could not say them: kind, signature, span,
    docstring body, values and decorators. Each was a MEASURED gap, and the
    second pass was a whole pipeline stage kept alive to fill them. They now
    ride the one statement that already names the thing.

    Read from the store on disk, never through the renderer: the subject is
    what the schema SAYS, and the renderer would only report what it managed to
    read."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _make_schema_repo(self.repo)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["extract", "--root", str(self.repo)]), 0)
        self.statements = statements_of(self.repo / ".code-map")

    def tearDown(self):
        self._tmp.cleanup()

    def _facts(self, symbol):
        """The described facts of one definition, from its own statement."""
        rows = [st for st in self.statements
                if st["p"] == "contains" and st["o"] == symbol]
        if len(rows) != 1:
            raise HarnessError(
                f"HARNESS ERROR: {symbol} has {len(rows)} definition statements, "
                f"expected exactly 1")
        return rows[0]

    def test_schema_carries_the_kind_of_every_definition(self):
        for symbol, kind in (("pkg.shape:Gadget", "class"),
                             ("pkg.shape:Gadget.size", "property"),
                             ("pkg.shape:spin_up", "async function"),
                             ("pkg.shape:inside_a_with_block", "function")):
            with self.subTest(symbol=symbol):
                self.assertEqual(self._facts(symbol)["d"]["kind"], kind)

    def test_schema_carries_the_rendered_signature(self):
        """Annotations, the keyword-only marker, a default and the return type --
        the whole point of the field is that a reader does not open the file."""
        self.assertEqual(self._facts("pkg.shape:spin_up")["d"]["signature"],
                         "(gadget: Gadget, *, times: int = 2) -> int")
        self.assertIsNone(self._facts("pkg.shape:Gadget")["d"]["signature"],
                          "a class has no call signature and must not invent one")

    def test_schema_carries_the_span_and_it_agrees_with_the_source_text(self):
        """The span's last line is checked against the file, not against the
        store: an end line that agrees only with its own start line is not a
        span, it is arithmetic."""
        base = {st["d"]["line_base"] for st in self.statements
                if st["p"] == "extraction-window"}.pop()
        definition = self._facts("pkg.shape:spin_up")

        self.assertEqual(definition["d"]["end"] + (1 - base),
                         physical_line_of(_SCHEMA_SOURCE, "    return times"))
        self.assertEqual(definition["d"]["end"] - definition["q"]["line"] + 1, 7)

    def test_schema_carries_the_docstring_body_past_the_summary_line(self):
        """The store kept only the summary, so the Args section -- the reason a
        reader wanted the docstring at all -- was reachable only in the file."""
        body = self._facts("pkg.shape:spin_up")["d"]["doc_body"]

        self.assertIn("Args:", body)
        self.assertIn("times: how many turns to take.", body)
        self.assertNotIn("Spin the gadget up.", body,
                         "the body is what comes AFTER the summary line")

    def test_schema_carries_the_decorators(self):
        self.assertEqual(self._facts("pkg.shape:Gadget.size")["d"]["decorators"],
                         ["property"])
        self.assertEqual(self._facts("pkg.shape:spin_up")["d"]["decorators"], [])

    def _declared(self, symbol):
        rows = [st for st in self.statements
                if st["p"] == "declares" and st["o"] == symbol]
        if len(rows) != 1:
            raise HarnessError(
                f"HARNESS ERROR: {symbol} has {len(rows)} declaration statements, "
                f"expected exactly 1")
        return rows[0]

    def test_schema_carries_the_value_of_a_module_constant(self):
        """The store recorded only that a name was written, never what it was
        written to -- so `WIDTH: int = 7` reached the map as the word `WIDTH`."""
        self.assertEqual(self._declared("pkg.shape:WIDTH")["d"],
                         {"annotation": "int", "value": "7",
                          "form": "annotated-assign"})
        self.assertEqual(self._declared("pkg.shape:NAME")["d"],
                         {"annotation": None, "value": "'gadget'", "form": "assign"})

    def test_schema_carries_a_class_field_including_an_annotation_only_one(self):
        """An annotation-only field had NO statement of any kind: a dataclass
        field or a ClassVar declaration was invisible to the store."""
        self.assertEqual(self._declared("pkg.shape:Gadget.slots")["d"],
                         {"annotation": "int", "value": "3",
                          "form": "annotated-assign"})
        self.assertEqual(self._declared("pkg.shape:Gadget.label")["d"],
                         {"annotation": "str", "value": None,
                          "form": "annotation-only"})

    def test_schema_declares_a_value_without_making_it_an_entity(self):
        """A constant is a fact about its owner, not a page.

        Page accounting is one page per module index, per entity and one top
        index; a constant that arrived as an entity would demand a page and the
        count would go red."""
        self.assertNotIn("pkg.shape:WIDTH",
                         [st["o"] for st in self.statements if st["p"] == "contains"])

    def test_schema_window_carries_the_module_facts(self):
        window = [st for st in self.statements
                  if st["p"] == "extraction-window" and st["q"]["file"] == "pkg/shape.py"][0]

        self.assertEqual(window["d"]["loc"], len(_SCHEMA_SOURCE.splitlines()))
        self.assertEqual(window["d"]["all"], ["Gadget", "spin_up"])
        self.assertIn("This second paragraph is the docstring BODY",
                      window["d"]["doc_body"])


class OneSchemaCoverageTests(unittest.TestCase):
    """Gate g3, `tc34`: the second AST pass descended `node.body` and nothing
    else, so a definition inside a `with`, `if`, `try` or `for` block was not an
    entity at all -- no page, no caller list, invisible in every count the map
    published. The map did not say it was missing; it did not know.

    The statement extractor never had that blind spot: it is an
    `ast.NodeVisitor`, so it descends into a block statement and reaches the
    definition inside. Folding the six facts into the statement schema and
    removing the second pass therefore closes `tc34` by construction, and this
    is the test that says so rather than assuming it."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _make_schema_repo(self.repo)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["build", "--root", str(self.repo)]), 0)

    def tearDown(self):
        self._tmp.cleanup()

    def test_schema_merge_gives_a_page_to_a_definition_inside_a_with_block(self):
        page = self.repo / "map" / "pkg.shape" / "inside_a_with_block.md"

        self.assertTrue(
            page.exists(),
            "a definition inside a `with` block has no page: the map is not "
            "missing it, it does not know about it\n"
            + "\n".join(sorted(p.name for p in (self.repo / "map" / "pkg.shape")
                               .iterdir())))
        self.assertIn("Defined inside a `with`", page.read_text(encoding="utf-8"))

    def test_schema_merge_lists_the_with_block_definition_on_its_module_index(self):
        """A page nothing links to is a page nobody finds."""
        index = (self.repo / "map" / "pkg.shape" / "INDEX.md").read_text(encoding="utf-8")

        self.assertIn("[inside_a_with_block](inside_a_with_block.md)", index)


_ANCHOR_SOURCE = '''"""A module whose author minted two ids for the mind map to hook."""

WIDTH = 3


# [widget-spin]
def spin():
    """The first anchored definition."""
    return WIDTH


class Holder:
    """Holds the second anchored definition."""

    # [holder-hold]
    def hold(self):
        """An anchored method."""
        return 2


def unanchored():
    """Most definitions never get an id: they are minted on demand."""
    return 3
'''


def _make_anchor_repo(tmp: Path, source=None):
    """A repo carrying two authored `[kebab-slug]` anchors and one definition
    with none.

    Two, because one id cannot show that the file is SORTED; and one
    unanchored definition, because the ruling is that ids are minted on demand
    and a file that listed every definition would not be an authored layer at
    all."""
    (tmp / "pkg").mkdir()
    (tmp / "pkg" / "__init__.py").write_text("", encoding="utf-8", newline="\n")
    (tmp / "pkg" / "anchors.py").write_text(source or _ANCHOR_SOURCE,
                                            encoding="utf-8", newline="\n")
    _git("init", "-q", cwd=tmp)
    _git("add", "pkg/__init__.py", "pkg/anchors.py", cwd=tmp)


class IdsJsonlTests(unittest.TestCase):
    """Gate g3: `map/ids.jsonl` is the mind map's one lookup, and it carries NO
    position.

    The mind map stores repo and slug and nothing else, so the id has to
    survive a rename and a move. `{"id","s"}` is what makes that true: the
    symbol path is derived and disposable, the slug is authored and durable, and
    because the file holds no line number its git diff IS the id-motion report
    rather than churn nobody can read."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _make_anchor_repo(self.repo)

    def tearDown(self):
        self._tmp.cleanup()

    def _build(self, out="map"):
        with contextlib.redirect_stdout(io.StringIO()):
            code = cli.main(["build", "--root", str(self.repo),
                             "--out", str(self.repo / out)])
        self.assertEqual(code, 0)
        return (self.repo / out / "ids.jsonl").read_bytes()

    @staticmethod
    def _lines(raw):
        return [json.loads(ln) for ln in raw.decode("utf-8").splitlines()]

    def test_ids_jsonl_carries_one_sorted_line_per_minted_anchor(self):
        entries = self._lines(self._build())

        self.assertEqual(entries, [{"id": "holder-hold", "s": "pkg.anchors:Holder.hold"},
                                   {"id": "widget-spin", "s": "pkg.anchors:spin"}])

    def test_ids_jsonl_carries_no_position(self):
        """The confirmed constraint: nothing committed carries a position. The
        keys are asserted exactly, so a later gate cannot slip a `q` back in."""
        entries = self._lines(self._build())

        self.assertTrue(entries,
                        "input precondition: the file must hold ids, or a scan for "
                        "forbidden keys reads nothing and passes")
        for entry in entries:
            with self.subTest(id=entry.get("id")):
                self.assertEqual(sorted(entry), ["id", "s"])

    def test_ids_jsonl_keeps_the_id_and_moves_the_symbol_when_one_is_renamed(self):
        """Mint two, rename one. The authored id is what the mind map stored;
        the symbol path is derived, so it is the side that moves."""
        before = self._lines(self._build())

        (self.repo / "pkg" / "anchors.py").write_text(
            _ANCHOR_SOURCE.replace("def spin():", "def rotate():"),
            encoding="utf-8", newline="\n")
        after = self._lines(self._build())

        self.assertEqual([e["id"] for e in after], [e["id"] for e in before])
        self.assertEqual([e["s"] for e in after],
                         ["pkg.anchors:Holder.hold", "pkg.anchors:rotate"])

    def test_ids_jsonl_is_byte_identical_when_the_code_around_it_moves(self):
        """The payoff for carrying no position, and the thing a `q` would
        destroy: a 5-line insertion above an anchor moves every definition in
        the file and this file does not change at all."""
        before, moved_from = self._build(), self._recorded_line()

        self.assertTrue(before.strip(),
                        "input precondition: two empty files are byte-identical and "
                        "prove nothing")

        (self.repo / "pkg" / "anchors.py").write_text(
            "# padding\n" * 5 + _ANCHOR_SOURCE, encoding="utf-8", newline="\n")
        after, moved_to = self._build(out="map2"), self._recorded_line()

        self.assertEqual(moved_to, moved_from + 5,
                         "input precondition: the insertion must actually move the "
                         "entity, or this proves nothing about positions")
        self.assertEqual(before, after)

    def _recorded_line(self):
        """Where the STORE says the anchored definition is. The rendered page
        cannot serve as this precondition -- it carries no position, which is
        the very ruling this test is downstream of."""
        return [st["q"]["line"] for st in statements_of(self.repo / ".code-map")
                if st["p"] == "contains" and st["o"] == "pkg.anchors:spin"][0]

    def test_ids_jsonl_reports_a_duplicate_slug_as_a_build_error(self):
        """Two definitions claiming one id is an authored mistake, and the run
        report is where the ruling says it surfaces. Silently keeping one would
        leave the mind map pointing at whichever won."""
        (self.repo / "pkg" / "anchors.py").write_text(
            _ANCHOR_SOURCE.replace("[holder-hold]", "[widget-spin]"),
            encoding="utf-8", newline="\n")
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = cli.main(["build", "--root", str(self.repo)])

        self.assertEqual(code, 1)
        self.assertIn("widget-spin", buffer.getvalue())


class StaleAnchorExtractionTests(unittest.TestCase):
    """Gate g6: `extract` persists a span_hash on every `anchored` statement,
    and on a SECOND extraction into the SAME `--artifacts` dir, diffs the
    previous run's hashes against the new ones by slug -- the only identity
    an anchor carries today (`g7`'s Assumption:/Constraint:/etc. vocabulary,
    the real 'tag text', has not been built yet; see the handoff's resolved
    decision). A slug present in both runs whose hash now differs gets one
    `stale-anchor` statement appended to the store.

    Two extractions into the SAME artifacts directory, mirroring
    `IdsJsonlTests`'s own before/after pattern -- that is the only place a
    'previous run' can be read from before this run's write overwrites it."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _make_anchor_repo(self.repo)
        self.artifacts = self.repo / ".code-map"

    def tearDown(self):
        self._tmp.cleanup()

    def _extract(self):
        with contextlib.redirect_stdout(io.StringIO()):
            code = cli.main(["extract", "--root", str(self.repo),
                             "--artifacts", str(self.artifacts)])
        self.assertEqual(code, 0)
        return statements_of(self.artifacts)

    def _stale_slugs(self, statements):
        return {st["o"] for st in statements if st["p"] == "stale-anchor"}

    def test_stale_tag_span_hash_is_persisted_on_every_anchored_statement(self):
        statements = self._extract()
        anchored = [st for st in statements if st["p"] == "anchored"]

        self.assertTrue(anchored, "input precondition: the fixture must mint anchors, "
                                  "or there is nothing to check a hash on")
        for st in anchored:
            with self.subTest(id=st["o"]):
                self.assertIn("span_hash", st.get("d") or {})

    def test_stale_tag_first_extraction_flags_nothing(self):
        """Bootstrap: no previous store exists yet, so there is nothing to
        compare against -- the correct behavior is silence, not a false
        positive on every anchor in a brand-new repo.

        Positive control, same method: a SECOND extraction after a real
        body change must flag. Without it, this method cannot tell
        "correctly silent on bootstrap" apart from "staleness detection
        disabled" -- both look like an empty stale set."""
        statements = self._extract()

        self.assertEqual(self._stale_slugs(statements), set())

        (self.repo / "pkg" / "anchors.py").write_text(
            _ANCHOR_SOURCE.replace("    return WIDTH\n", "    return WIDTH * 2\n"),
            encoding="utf-8", newline="\n")
        after = self._extract()

        self.assertEqual(self._stale_slugs(after), {"widget-spin"},
                         "positive control: a real body change on the second "
                         "extraction was not flagged")

    def test_stale_tag_does_not_flag_a_reformat_across_two_extractions(self):
        self._extract()

        (self.repo / "pkg" / "anchors.py").write_text(
            _ANCHOR_SOURCE.replace(
                "    return WIDTH\n",
                "\n    return WIDTH  # trailing comment\n"),
            encoding="utf-8", newline="\n")
        after = self._extract()

        self.assertEqual(self._stale_slugs(after), set(),
                         "a blank line plus a trailing comment flagged a tag as stale")

        # Positive control, same method/fixture/build path/assertion
        # mechanism: a real body change on top of the reformat must still
        # flag, proving the silence above is reformat-immunity, not a
        # disabled check.
        (self.repo / "pkg" / "anchors.py").write_text(
            _ANCHOR_SOURCE.replace("    return WIDTH\n", "    return WIDTH * 2\n"),
            encoding="utf-8", newline="\n")
        control = self._extract()

        self.assertEqual(self._stale_slugs(control), {"widget-spin"},
                         "positive control: a real body change was not flagged")

    def test_stale_tag_flags_a_real_body_change_across_two_extractions(self):
        self._extract()

        (self.repo / "pkg" / "anchors.py").write_text(
            _ANCHOR_SOURCE.replace("    return WIDTH\n", "    return WIDTH * 2\n"),
            encoding="utf-8", newline="\n")
        after = self._extract()

        self.assertEqual(self._stale_slugs(after), {"widget-spin"},
                         "a real body change (WIDTH -> WIDTH * 2) under a live tag "
                         "was not flagged")

    def test_stale_tag_does_not_flag_an_unrelated_anchor(self):
        """Only the mutated slug's body changed; the other anchor in the same
        file must stay silent, or the flag is not attributing the change to
        the right tag.

        Positive control, same method: the actually-mutated slug must be
        in the SAME assertion's stale set. Checking only the unrelated
        anchor's absence cannot tell "correct attribution" apart from
        "nothing flags, ever"."""
        self._extract()

        (self.repo / "pkg" / "anchors.py").write_text(
            _ANCHOR_SOURCE.replace("    return WIDTH\n", "    return WIDTH * 2\n"),
            encoding="utf-8", newline="\n")
        after = self._extract()

        stale = self._stale_slugs(after)
        self.assertNotIn("holder-hold", stale)
        self.assertIn("widget-spin", stale,
                      "positive control: the actually-mutated slug was not flagged")

    def test_stale_tag_extract_survives_a_truncated_previous_store(self):
        """A truncated/malformed leftover statements.jsonl -- e.g. from an
        interrupted prior run, since the writer has no atomic rename -- is a
        real scenario, and the user's natural next action (run `extract`
        again) must not crash on it. Before this gate, nothing read the
        previous store, so a corrupted leftover was harmless; this gate
        introduces the read, so it must survive a bad one: treat it as
        absent, the same path a first-ever run takes, with one actionable
        line saying so -- not a silent skip."""
        self.artifacts.mkdir(parents=True, exist_ok=True)
        (self.artifacts / "statements.jsonl").write_text(
            '{"s": "widget-spin", "p": "anchored", "o": "widget-spin", '
            '"d": {"span_hash": "abc',
            encoding="utf-8")

        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = cli.main(["extract", "--root", str(self.repo),
                             "--artifacts", str(self.artifacts)])

        self.assertEqual(code, 0, buffer.getvalue())
        self.assertIn("unreadable", buffer.getvalue())
        statements = statements_of(self.artifacts)
        self.assertEqual(self._stale_slugs(statements), set(),
                         "a corrupted previous store must be treated as "
                         "absent, not compared against")


class StaleAnchorRenderReportTests(unittest.TestCase):
    """Gate g6's close criterion: the flag lands in the run report the
    reviewer already reads -- `render_report.json`, the same artifact the
    duplicate-id check already surfaces through (`IdsJsonlTests`). Two full
    `build`s into the SAME `--artifacts`/`--out` pair, mirroring that class's
    own before/after pattern."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _make_anchor_repo(self.repo)
        self.artifacts = self.repo / ".code-map"
        self.out = self.repo / "map"

    def tearDown(self):
        self._tmp.cleanup()

    def _build(self):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = cli.main(["build", "--root", str(self.repo),
                             "--artifacts", str(self.artifacts),
                             "--out", str(self.out)])
        self.assertEqual(code, 0, buffer.getvalue())
        report = json.loads((self.artifacts / "render_report.json").read_text(encoding="utf-8"))
        return report, buffer.getvalue()

    def test_stale_tag_render_report_does_not_flag_a_reformat(self):
        self._build()

        (self.repo / "pkg" / "anchors.py").write_text(
            _ANCHOR_SOURCE.replace(
                "    return WIDTH\n",
                "\n    return WIDTH  # trailing comment\n"),
            encoding="utf-8", newline="\n")
        report, out = self._build()

        self.assertEqual(report.get("stale_tags"), [])
        self.assertNotIn("stale tag", out)

        # Positive control, same method/build path/assertion mechanism: a
        # real body change on top must still flag in the run report.
        (self.repo / "pkg" / "anchors.py").write_text(
            _ANCHOR_SOURCE.replace("    return WIDTH\n", "    return WIDTH * 2\n"),
            encoding="utf-8", newline="\n")
        control_report, control_out = self._build()

        self.assertEqual(control_report.get("stale_tags"), ["widget-spin"],
                         "positive control: a real body change was not flagged")
        self.assertIn("stale tag", control_out)

    def test_stale_tag_render_report_flags_a_real_body_change(self):
        self._build()

        (self.repo / "pkg" / "anchors.py").write_text(
            _ANCHOR_SOURCE.replace("    return WIDTH\n", "    return WIDTH * 2\n"),
            encoding="utf-8", newline="\n")
        report, out = self._build()

        self.assertEqual(report.get("stale_tags"), ["widget-spin"])
        self.assertIn("widget-spin", out)
        self.assertIn("stale tag", out)

    def test_stale_tag_render_report_does_not_fail_the_build(self):
        """Advisory, not blocking: unlike a duplicate id (unambiguous data
        corruption), a stale tag might still be true -- a human has to look.
        Failing the build on it would be the twitchy tripwire the ruling
        this gate inherits (`gb`) warns against.

        Positive control, same method: the build must have actually
        flagged the tag. Exit-0 alone cannot tell "advisory" apart from
        "disabled" -- both exit 0."""
        self._build()

        (self.repo / "pkg" / "anchors.py").write_text(
            _ANCHOR_SOURCE.replace("    return WIDTH\n", "    return WIDTH * 2\n"),
            encoding="utf-8", newline="\n")
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = cli.main(["build", "--root", str(self.repo),
                             "--artifacts", str(self.artifacts),
                             "--out", str(self.out)])

        self.assertEqual(code, 0, buffer.getvalue())
        report = json.loads((self.artifacts / "render_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report.get("stale_tags"), ["widget-spin"],
                         "positive control: the build exited 0 but never actually "
                         "flagged the tag it is supposed to be advisory about")

    def test_stale_tag_advisory_line_does_not_begin_with_fail(self):
        """The advisory line must not begin with `FAIL` -- that prefix is
        `checks.py`'s and `render.py`'s own convention for genuine
        build-failing defects, and a single `build`'s stdout can legally
        carry both, distinguishable only by exit code."""
        self._build()

        (self.repo / "pkg" / "anchors.py").write_text(
            _ANCHOR_SOURCE.replace("    return WIDTH\n", "    return WIDTH * 2\n"),
            encoding="utf-8", newline="\n")
        _, out = self._build()

        stale_lines = [line for line in out.splitlines() if "stale tag" in line]
        self.assertTrue(stale_lines, "input precondition: the build must actually "
                                     "print a stale-tag line, or checking its "
                                     "prefix proves nothing")
        for line in stale_lines:
            with self.subTest(line=line):
                self.assertFalse(line.startswith("FAIL"),
                                 "advisory stale-tag line collides with the FAIL "
                                 "prefix used for genuine build-failing defects")

    def test_stale_tag_render_report_carries_no_timing_field(self):
        self._build()

        (self.repo / "pkg" / "anchors.py").write_text(
            _ANCHOR_SOURCE.replace("    return WIDTH\n", "    return WIDTH * 2\n"),
            encoding="utf-8", newline="\n")
        report, _ = self._build()

        self.assertEqual(report.get("stale_tags"), ["widget-spin"],
                         "input precondition: the report must actually carry a flag, "
                         "or scanning its keys for a timing field proves nothing")
        for key in report:
            with self.subTest(key=key):
                self.assertNotRegex(key, r"time|duration|elapsed|timestamp",
                                    "the run report grew a timing field")


_TAG_SOURCE = '''"""A module whose author left the why layer behind: comment tags."""

# Rationale: the timeout is doubled here because slow CI runners kept
# flaking below this value.
TIMEOUT = 20


# Rationale: spin always returns TIMEOUT doubled -- the caller never wants
# the raw value.
def spin():
    """A function whose whole body is explained by one tag above the def."""
    return TIMEOUT * 2


class Holder:
    """Holds a method with a function-local tag -- the real corpus's own shape."""

    def hold(self):
        """The tag sits on a LOCAL assignment, not on the def."""
        # Rejected: reading TIMEOUT directly here -- a caller mutated the
        # module constant mid-request in production, so a local copy is
        # deliberate.
        path = TIMEOUT
        return path


# See: pkg.tags:Holder.hold
def elsewhere():
    """A reference tag pointing at the definition above."""
    return None


# Constraint: budget stays under 200ms end to end -- the SLA the caller
# depends on.
def budget():
    """Gate g7 remediation fix 2: authored with the aliased keyword that
    folds into Rationale: at extraction -- must still extract and render,
    normalized to the survivor word."""
    return 200
'''


def _make_tag_repo(tmp: Path, source=None):
    """A repo exercising all three surviving grammar words (Rationale:,
    Rejected:, See:) at the three binding shapes gate g7 resolves: a
    whole-function tag (directly above `def spin`), a function-local
    assignment tag (directly above `path = TIMEOUT` inside `Holder.hold`,
    the real f1Brainz PR #733 corpus's own majority shape), and a module
    tag (directly above the module constant `TIMEOUT`). `budget()` adds
    gate g7 remediation fix 2's alias round-trip: authored with the
    ALIASED keyword `Constraint:`, which must still extract and render,
    normalized to `Rationale:`."""
    (tmp / "pkg").mkdir()
    (tmp / "pkg" / "__init__.py").write_text("", encoding="utf-8", newline="\n")
    (tmp / "pkg" / "tags.py").write_text(source or _TAG_SOURCE,
                                         encoding="utf-8", newline="\n")
    _git("init", "-q", cwd=tmp)
    _git("add", "pkg/__init__.py", "pkg/tags.py", cwd=tmp)


class CommentTagExtractionTests(unittest.TestCase):
    """Gate g7: bare `Word:` paragraph tags -- `Rationale:`/`Rejected:`/`See:`
    -- extract into `tag` statements, binding to the CURRENTLY ENCLOSING
    entity or module symbol (`self.here()`), mirroring the anchor
    convention's own forward-scan.

    Resolves the convention gap the handoff named ("where does a tag go when
    its rationale covers a whole function rather than a single line?"): a
    tag directly above a `def`/`class` binds to that entity's OWN symbol
    (the whole-function case); a tag above a statement inside a body binds
    to the ENCLOSING entity, since the map has no page finer than one per
    entity -- there is nowhere else for it to render."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _make_tag_repo(self.repo)
        self.artifacts = self.repo / ".code-map"

    def tearDown(self):
        self._tmp.cleanup()

    def _extract(self):
        with contextlib.redirect_stdout(io.StringIO()):
            code = cli.main(["extract", "--root", str(self.repo),
                             "--artifacts", str(self.artifacts)])
        self.assertEqual(code, 0)
        return statements_of(self.artifacts)

    def _tags(self, statements):
        return [st for st in statements if st["p"] == "tag"]

    def test_comment_tags_module_level_tag_binds_to_the_module_symbol(self):
        tags = self._tags(self._extract())
        module_tags = [t for t in tags if t["s"] == "pkg.tags:"]

        self.assertEqual(len(module_tags), 1, module_tags)
        self.assertEqual(module_tags[0]["o"], "Rationale")
        self.assertIn("CI runners", module_tags[0]["d"]["text"])

    def test_comment_tags_whole_function_tag_binds_to_the_functions_own_symbol(self):
        tags = self._tags(self._extract())
        fn_tags = [t for t in tags if t["s"] == "pkg.tags:spin"]

        self.assertEqual(len(fn_tags), 1, fn_tags)
        self.assertEqual(fn_tags[0]["o"], "Rationale")
        self.assertIn("doubled", fn_tags[0]["d"]["text"])

    def test_comment_tags_function_local_assignment_tag_binds_to_the_enclosing_method(self):
        """The real corpus's own shape (f1Brainz PR #733): 5 of 6 real tags
        sit above a statement INSIDE a function, not above the def -- there
        is no page finer than the enclosing entity, so this is where a tag
        placed there must land."""
        tags = self._tags(self._extract())
        method_tags = [t for t in tags if t["s"] == "pkg.tags:Holder.hold"]

        self.assertEqual(len(method_tags), 1, method_tags)
        self.assertEqual(method_tags[0]["o"], "Rejected")
        self.assertIn("mutated", method_tags[0]["d"]["text"])

    def test_comment_tags_see_reference_binds_to_the_function_it_precedes(self):
        tags = self._tags(self._extract())
        see_tags = [t for t in tags if t["s"] == "pkg.tags:elsewhere"]

        self.assertEqual(len(see_tags), 1, see_tags)
        self.assertEqual(see_tags[0]["o"], "See")
        self.assertEqual(see_tags[0]["d"]["text"], "pkg.tags:Holder.hold")

    def test_comment_tags_constraint_keyword_extracts_normalized_to_rationale(self):
        """Gate g7 remediation fix 2: `Constraint:` is a RECOGNIZED, ALIASED
        keyword, not a retired one -- it extracts, with its kind normalized
        to `Rationale` at the emission site, so the four real f1Brainz PR
        #733 tags authored with this word keep being visibly consumed."""
        tags = self._tags(self._extract())
        budget_tags = [t for t in tags if t["s"] == "pkg.tags:budget"]

        self.assertEqual(len(budget_tags), 1, budget_tags)
        self.assertEqual(budget_tags[0]["o"], "Rationale",
                         "a Constraint: authored tag must extract with kind "
                         "normalized to Rationale -- the alias, not the "
                         "retirement, is what shipped")
        self.assertIn("200ms", budget_tags[0]["d"]["text"])

    def test_comment_tags_multiline_paragraph_joins_into_one_text(self):
        """The real corpus's own shape: a tag's prose wraps across several
        comment lines, and the extracted text is the JOINED paragraph, not
        just its first line."""
        tags = self._tags(self._extract())
        method_tags = [t for t in tags if t["s"] == "pkg.tags:Holder.hold"]

        self.assertEqual(len(method_tags), 1, method_tags)
        text = method_tags[0]["d"]["text"]
        self.assertIn("reading TIMEOUT directly here", text)
        self.assertIn("a local copy is deliberate", text)


def _kind_dispatch_nodes(tree):
    """Gate g7 remediation fix 3: every AST node in `tree` that varies
    behavior on a tag's `kind`, not just an explicit `if kind == ...`/`elif`
    branch (an `ast.Compare`, the ONLY shape the original pin test caught)
    but also a dict/mapping-lookup dispatch (`SOME_MAP[t['kind']]`) or a
    `match` statement keyed on it -- shapes the review proved an
    ast.Compare-only check misses entirely (zero Compare nodes either
    produces).

    A plain READ of the tag's own kind field (`t['kind']`, the uniform
    treatment itself) must NOT trip this -- only a subscript/`.get()` that
    uses `kind` as the INDEX into some OTHER mapping does. The distinguishing
    shape: the outer lookup's key expression is itself a reference to
    `kind` (a bare `Name`) or a further subscript reading `kind` out of the
    tag (`t['kind']`) -- not a literal string key like `t['kind']`'s own
    `'kind'` constant, which would false-positive a bare read if matched by
    naive substring text."""
    found = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Compare) and "kind" in ast.unparse(n):
            found.append(n)
        elif isinstance(n, ast.Match) and "kind" in ast.unparse(n.subject):
            found.append(n)
        elif isinstance(n, ast.Subscript):
            key = n.slice
            if (isinstance(key, ast.Subscript) and "kind" in ast.unparse(key)) or \
               (isinstance(key, ast.Name) and key.id == "kind"):
                found.append(n)
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                and n.func.attr == "get" and n.args:
            arg0 = n.args[0]
            if (isinstance(arg0, ast.Subscript) and "kind" in ast.unparse(arg0)) or \
               (isinstance(arg0, ast.Name) and arg0.id == "kind"):
                found.append(n)
    return found


class CommentTagRenderTests(unittest.TestCase):
    """Gate g7: tags render on the page of whichever entity or module they
    bound to at extraction -- one line per tag, `{kind}: {text}`, same
    section and format for every kind. This uniform code path (one loop, no
    branch on `kind` anywhere in `render.py`) IS the cull test's evidence."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _make_tag_repo(self.repo)
        self.out = self.repo / "map"

    def tearDown(self):
        self._tmp.cleanup()

    def _build(self):
        with contextlib.redirect_stdout(io.StringIO()):
            code = cli.main(["build", "--root", str(self.repo), "--out", str(self.out)])
        self.assertEqual(code, 0)

    def _page(self, mod_dir, name):
        return (self.out / mod_dir / name).read_text(encoding="utf-8")

    def test_comment_tags_render_on_the_module_index_page(self):
        self._build()
        page = self._page("pkg.tags", "INDEX.md")

        self.assertIn("Rationale: the timeout is doubled here because slow "
                      "CI runners kept flaking below this value.", page)

    def test_comment_tags_render_on_the_whole_function_entity_page(self):
        self._build()
        page = self._page("pkg.tags", "spin.md")

        self.assertIn("Rationale: spin always returns TIMEOUT doubled -- "
                      "the caller never wants the raw value.", page)

    def test_comment_tags_render_on_the_enclosing_method_page_for_a_local_tag(self):
        self._build()
        page = self._page("pkg.tags", "Holder.hold.md")

        self.assertIn("Rejected: reading TIMEOUT directly here", page)
        self.assertIn("a local copy is deliberate.", page)

    def test_comment_tags_see_reference_renders_on_its_own_page(self):
        self._build()
        page = self._page("pkg.tags", "elsewhere.md")

        self.assertIn("See: pkg.tags:Holder.hold", page)

    def test_comment_tags_constraint_keyword_renders_as_rationale(self):
        """Gate g7 remediation fix 2's alias round-trip, render half: a
        `Constraint:`-authored tag shows on the page as `Rationale:` -- the
        retired keyword itself must not leak into rendered output."""
        self._build()
        page = self._page("pkg.tags", "budget.md")

        self.assertIn("Rationale: budget stays under 200ms", page)
        self.assertNotIn("Constraint:", page,
                         "the retired keyword must not survive to the rendered page")

    def test_comment_tags_render_path_carries_no_branch_on_kind(self):
        """The cull test itself, applied at code level: `tag_lines` is the
        ONLY place `render.py` reads a tag's kind, and it is one
        list-comprehension with no conditional dispatch OR lookup-dispatch
        on the value -- every kind gets the identical `f"{kind}: {text}"`
        treatment, same section, same order, same format. This is the
        evidence `.agent-work/issue-456/cull-verdict.json` cites for its
        verdict.

        Gate g7 remediation fix 3: widened from an `ast.Compare`-only check
        (which a dict-lookup dispatch or a `match` statement both evade,
        producing zero Compare nodes) to `_kind_dispatch_nodes`, which also
        catches those shapes -- verified live against a real evading
        mutation, not reasoned about (see the RESULT doc)."""
        tree = ast.parse(inspect.getsource(render.tag_lines))
        dispatch = _kind_dispatch_nodes(tree)

        self.assertEqual(dispatch, [],
                         "tag_lines varies its treatment of a tag's kind -- "
                         "the cull test's premise (uniform treatment, no "
                         "dispatch on kind) no longer holds")
        self.assertIn("kind", inspect.getsource(render.tag_lines),
                     "input precondition: the kind must actually be read and "
                     "printed verbatim, or the no-branch check proves nothing")


class CullVerdictArtifactTests(unittest.TestCase):
    """Gate g7's close criterion (critic F5): process alone is not a close
    criterion, so the cull test's verdict must be a CHECKABLE artifact, not
    a claim. These tests read `.agent-work/issue-456/cull-verdict.json` and
    check it against the code itself -- extract.py's actual recognized
    keywords and render.py's actual tag-rendering code path -- rather than
    trusting the file's own prose."""

    VERDICT_PATH = ROOT / ".agent-work" / "issue-456" / "cull-verdict.json"

    def _verdict(self):
        self.assertTrue(self.VERDICT_PATH.exists(),
                        "cull-verdict.json must exist at the path the "
                        "handoff names, or there is nothing to check")
        return json.loads(self.VERDICT_PATH.read_text(encoding="utf-8"))

    def test_comment_tags_cull_verdict_file_exists_and_parses(self):
        v = self._verdict()
        self.assertIn("verdict", v)
        self.assertIn("kinds", v)

    def test_comment_tags_cull_verdict_matches_extractors_recognized_keywords(self):
        """Gate g7 remediation fix 2: the verdict is ALIAS, not retirement --
        all five words are RECOGNIZED (checked against extract.py's own
        TAG_START pattern, not the verdict's own say-so); Assumption:/
        Constraint: additionally carry a normalization entry, re-derived
        against extract.py's actual TAG_KIND_ALIAS dict, not just the
        verdict's own prose about it."""
        v = self._verdict()
        pattern = extract.TAG_START.pattern

        self.assertEqual(sorted(v["shipped_keywords"]),
                         ["Assumption", "Constraint", "Rationale", "Rejected", "See"])
        for kw in v["shipped_keywords"]:
            with self.subTest(keyword=kw):
                self.assertIn(kw, pattern)

        self.assertEqual(v["kind_normalization"], dict(extract.TAG_KIND_ALIAS),
                         "the verdict's kind_normalization must match "
                         "extract.py's actual TAG_KIND_ALIAS, not just assert "
                         "its own prose")
        for retired, survivor in extract.TAG_KIND_ALIAS.items():
            with self.subTest(keyword=retired):
                self.assertEqual(survivor, "Rationale")

    def test_comment_tags_cull_verdict_collapse_kinds_have_no_render_dependency(self):
        """For every kind the verdict marks a collapse candidate, the render
        path must actually show zero dependency on it -- re-run the same
        widened AST check CommentTagRenderTests uses (gate g7 remediation
        fix 3: catches a dict-lookup or `match` dispatch too, not just an
        explicit compare), so this test does not merely trust the verdict's
        own 'consumer_dependencies: []' claim."""
        v = self._verdict()
        tree = ast.parse(inspect.getsource(render.tag_lines))
        dispatch = _kind_dispatch_nodes(tree)

        for kind, info in v["kinds"].items():
            if info.get("candidate_for_collapse"):
                with self.subTest(kind=kind):
                    self.assertEqual(info["consumer_dependencies"], [])
                    self.assertEqual(dispatch, [],
                                     "verdict claims no render dependency on "
                                     "kind, but tag_lines varies its treatment "
                                     "of it")

    def test_comment_tags_cull_verdict_rejected_and_see_are_not_collapse_candidates(self):
        v = self._verdict()

        self.assertFalse(v["kinds"]["Rejected"]["candidate_for_collapse"])
        self.assertFalse(v["kinds"]["See"]["candidate_for_collapse"])
        self.assertIn("Rejected", v["shipped_keywords"])
        self.assertIn("See", v["shipped_keywords"])

    def test_comment_tags_cull_verdict_states_collapse_with_a_survivor(self):
        v = self._verdict()

        self.assertEqual(v["verdict"], "collapse")
        self.assertEqual(v["collapsed_to"], "Rationale")


_STALE_TAG_SOURCE = '''"""A module whose one function carries both an anchor and a tag."""

BASE = 5


# Rationale: this function's return value is doubled deliberately -- callers
# never want the raw base rate.
# [rate-double]
def rate():
    """Doubles the base rate."""
    return BASE * 2
'''


def _make_stale_tag_repo(tmp: Path, source=None):
    """A repo whose one function carries BOTH a [slug] anchor and a
    Rationale: tag in the same comment block -- the shape gate g7's join
    to g6 depends on: a tag mints through the same [slug] allocator, so
    g6's existing span_hash/diff machinery (untouched here) is what
    detects staleness, not any new code this gate adds."""
    (tmp / "pkg").mkdir()
    (tmp / "pkg" / "__init__.py").write_text("", encoding="utf-8", newline="\n")
    (tmp / "pkg" / "rate.py").write_text(source or _STALE_TAG_SOURCE,
                                         encoding="utf-8", newline="\n")
    _git("init", "-q", cwd=tmp)
    _git("add", "pkg/__init__.py", "pkg/rate.py", cwd=tmp)


class CommentTagStaleAnchorJoinTests(unittest.TestCase):
    """Gate g7 remediation (fix 1): this fixture's function carries BOTH an
    anchor and a tag, so this test proves COEXISTENCE -- g6's pre-existing
    anchor-based flag keeps firing correctly when the same entity also
    carries a live tag, and (since the fix) the NEW tag-staleness mechanism
    fires alongside it without interference. It does NOT, on its own, prove
    the tag mechanism works independent of an anchor -- that proof is
    `CommentTagOnlyStaleTagTests`, whose fixture carries a tag and NO anchor
    at all, the shape the real corpus (zero authored slugs) actually has.

    WORKFLOW FEEDBACK: the handoff's own illustration for this test named
    `Constraint:` as the tag kind to mutate under. The cull test this gate
    ran (m2/m3 -- see cull-verdict.json) collapsed `Constraint:` into
    `Rationale:`, the survivor word, so this test uses `Rationale:` instead.
    The evidentiary claim is unchanged either way: staleness fires on REAL
    tag text sitting on the mutated entity, not just a bare slug."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _make_stale_tag_repo(self.repo)
        self.artifacts = self.repo / ".code-map"

    def tearDown(self):
        self._tmp.cleanup()

    def _extract(self):
        with contextlib.redirect_stdout(io.StringIO()):
            code = cli.main(["extract", "--root", str(self.repo),
                             "--artifacts", str(self.artifacts)])
        self.assertEqual(code, 0)
        return statements_of(self.artifacts)

    def test_comment_tags_stale_tag_flags_a_real_body_change_under_a_live_tag(self):
        before = self._extract()
        tag_rows = [st for st in before
                   if st["p"] == "tag" and st["s"] == "pkg.rate:rate"]
        self.assertEqual(len(tag_rows), 1,
                         "input precondition: the fixture's function must carry "
                         "exactly one Rationale: tag, or mutating its body proves "
                         "nothing about a TAGGED entity")
        self.assertEqual(tag_rows[0]["o"], "Rationale")

        (self.repo / "pkg" / "rate.py").write_text(
            _STALE_TAG_SOURCE.replace("return BASE * 2", "return BASE * 3"),
            encoding="utf-8", newline="\n")
        after = self._extract()

        stale = {st["o"] for st in after if st["p"] == "stale-anchor"}
        self.assertEqual(stale, {"rate-double"},
                         "the staleness flag did not fire on a real body change "
                         "under an entity carrying a live comment tag -- the "
                         "first real exercise of g6's machinery against g7's "
                         "authored tag text")

        after_tags = [st for st in after
                     if st["p"] == "tag" and st["s"] == "pkg.rate:rate"]
        self.assertEqual(len(after_tags), 1)
        self.assertEqual(after_tags[0]["d"]["text"], tag_rows[0]["d"]["text"],
                         "the tag text itself must be UNCHANGED -- this test "
                         "proves staleness fires on a body change while the "
                         "tag stays put, not on the tag changing too")

        stale_tag_syms = {st["s"] for st in after if st["p"] == "stale-tag"}
        self.assertIn("pkg.rate:rate", stale_tag_syms,
                      "the NEW tag-staleness mechanism (fix 1) must ALSO fire "
                      "here -- both flags coexist on the same real body change, "
                      "proving the extension does not disturb g6's anchor path "
                      "or vice versa")


_TAG_ONLY_STALE_SOURCE = '''"""A module whose one function carries a Rationale: tag and NO anchor at all -- gate g7 remediation fix 1's required proof that the tag-staleness mechanism does not depend on an anchor being present, which is the shape the real corpus (zero authored slugs) actually has."""

BASE = 5


# Rationale: this function's return value is doubled deliberately -- callers
# never want the raw base rate.
def rate():
    """Doubles the base rate."""
    return BASE * 2
'''


def _make_tag_only_stale_repo(tmp: Path, source=None):
    """Mirrors `_make_stale_tag_repo`'s shape exactly, minus the `[slug]`
    anchor bracket -- the one line that differs from `_STALE_TAG_SOURCE`.
    This is the fixture `CommentTagStaleAnchorJoinTests`'s own docstring
    used to claim to be but was not: an entity carrying a tag and nothing
    else authored above it."""
    (tmp / "pkg").mkdir()
    (tmp / "pkg" / "__init__.py").write_text("", encoding="utf-8", newline="\n")
    (tmp / "pkg" / "rate.py").write_text(source or _TAG_ONLY_STALE_SOURCE,
                                         encoding="utf-8", newline="\n")
    _git("init", "-q", cwd=tmp)
    _git("add", "pkg/__init__.py", "pkg/rate.py", cwd=tmp)


class CommentTagOnlyStaleTagTests(unittest.TestCase):
    """Gate g7 remediation, fix 1: the review proved the shipped join test's
    fixture carried BOTH an anchor and a tag on the same function, so its
    flag fired off g6's untouched anchor mechanism (`p == "stale-anchor"`) --
    the real corpus (zero authored slugs) would never have exercised the
    tag path at all. This class is the required proof: an entity with a tag
    and NO anchor whatsoever, checked against a NEW `stale-tag` predicate
    the anchor diff never reads."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _make_tag_only_stale_repo(self.repo)
        self.artifacts = self.repo / ".code-map"

    def tearDown(self):
        self._tmp.cleanup()

    def _extract(self):
        with contextlib.redirect_stdout(io.StringIO()):
            code = cli.main(["extract", "--root", str(self.repo),
                             "--artifacts", str(self.artifacts)])
        self.assertEqual(code, 0)
        return statements_of(self.artifacts)

    def test_comment_tags_stale_tag_flags_a_real_body_change_with_zero_anchors_present(self):
        before = self._extract()
        self.assertEqual({st["o"] for st in before if st["p"] == "anchored"}, set(),
                         "input precondition: this fixture must carry NO anchor, "
                         "or it proves nothing about the tag mechanism standing "
                         "on its own")
        tag_rows = [st for st in before
                   if st["p"] == "tag" and st["s"] == "pkg.rate:rate"]
        self.assertEqual(len(tag_rows), 1,
                         "input precondition: exactly one Rationale: tag on rate()")
        self.assertEqual(tag_rows[0]["o"], "Rationale")

        (self.repo / "pkg" / "rate.py").write_text(
            _TAG_ONLY_STALE_SOURCE.replace("return BASE * 2", "return BASE * 3"),
            encoding="utf-8", newline="\n")
        after = self._extract()

        stale = [st for st in after if st["p"] == "stale-tag"]
        self.assertEqual(len(stale), 1, stale)
        self.assertEqual(stale[0]["s"], "pkg.rate:rate",
                         "the staleness flag did not fire on a real body change "
                         "under an entity carrying a live comment tag and NO "
                         "anchor -- the mechanism this fix exists to build")

        after_tags = [st for st in after
                     if st["p"] == "tag" and st["s"] == "pkg.rate:rate"]
        self.assertEqual(len(after_tags), 1)
        self.assertEqual(after_tags[0]["d"]["text"], tag_rows[0]["d"]["text"],
                         "the tag text itself must be UNCHANGED -- staleness "
                         "fires on a body change while the tag stays put, not "
                         "on the tag changing too")

    def test_comment_tags_stale_tag_does_not_flag_on_first_extraction(self):
        """Bootstrap: no previous store exists yet, so nothing to compare
        against -- silence is correct, not a false positive."""
        before = self._extract()

        self.assertEqual([st for st in before if st["p"] == "stale-tag"], [])

    def test_comment_tags_stale_tag_does_not_flag_when_tag_text_also_changes(self):
        """A tag whose own text was also revised is not stale -- the gate's
        own rule (restated in the remediation brief): the author already
        re-read it. The identity key is (owning symbol, tag text), so a
        changed text is a different key and simply does not match across
        the two extractions -- not a false positive to special-case."""
        self._extract()

        mutated = _TAG_ONLY_STALE_SOURCE.replace(
            "return BASE * 2", "return BASE * 3").replace(
            "never want the raw base rate.",
            "never want the raw, un-doubled rate.")
        (self.repo / "pkg" / "rate.py").write_text(
            mutated, encoding="utf-8", newline="\n")
        after = self._extract()

        self.assertEqual([st for st in after if st["p"] == "stale-tag"], [],
                         "a tag whose text also changed must not be flagged stale")


class CommentTagOnlyStaleTagRenderReportTests(unittest.TestCase):
    """Gate g7 remediation fix 1's close criterion: a REAL tag's staleness,
    with zero anchors present, must land in the SAME run report and
    ADVISORY channel g6 established (`render_report.json`'s `stale_tags`
    field, the `ADVISORY stale tag` print) -- not a second reporting
    channel."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _make_tag_only_stale_repo(self.repo)
        self.artifacts = self.repo / ".code-map"
        self.out = self.repo / "map"

    def tearDown(self):
        self._tmp.cleanup()

    def _build(self):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = cli.main(["build", "--root", str(self.repo),
                             "--artifacts", str(self.artifacts),
                             "--out", str(self.out)])
        self.assertEqual(code, 0, buffer.getvalue())
        report = json.loads((self.artifacts / "render_report.json").read_text(encoding="utf-8"))
        return report, buffer.getvalue()

    def test_comment_tags_stale_tag_lands_in_the_same_render_report_field(self):
        before, _ = self._build()
        self.assertEqual(before.get("stale_tags"), [])

        (self.repo / "pkg" / "rate.py").write_text(
            _TAG_ONLY_STALE_SOURCE.replace("return BASE * 2", "return BASE * 3"),
            encoding="utf-8", newline="\n")
        report, out = self._build()

        self.assertEqual(len(report.get("stale_tags") or []), 1, report)
        self.assertIn("ADVISORY", out)
        self.assertIn("stale tag", out)
        stale_lines = [line for line in out.splitlines() if "stale tag" in line]
        for line in stale_lines:
            with self.subTest(line=line):
                self.assertFalse(line.startswith("FAIL"),
                                 "advisory stale-tag line collides with the FAIL "
                                 "prefix used for genuine build-failing defects")


class CommentTagNegativeTests(unittest.TestCase):
    """Negative extraction cases, sourced from the committed fixture
    `tests/fixtures/comment_tags_corpus/corpus.py` (precedent:
    `overread_corpus/`) rather than an inline string, and copied into an
    ephemeral git repo per test since `discovery.py`'s corpus scan requires
    `git ls-files`.

    Each negative assertion is paired with a POSITIVE CONTROL (`scaled()`'s
    `Rationale:` tag) in the SAME test method, so a fully-broken extractor
    that extracts nothing at all cannot pass these tests by accident. Every
    'does not extract' claim here was verified by breaking the extractor and
    watching the specific assertion go red -- see the RESULT doc for the
    self-check count.

    One method below (the aliased-keyword one) is no longer a negative case
    -- gate g7 remediation fix 2 made Assumption:/Constraint: extract again,
    normalized -- but it stays in this class since it shares the same
    corpus fixture and setup."""

    CORPUS = (ROOT / "tests" / "fixtures" / "comment_tags_corpus" / "corpus.py"
             ).read_text(encoding="utf-8")

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        (self.repo / "pkg").mkdir()
        (self.repo / "pkg" / "__init__.py").write_text("", encoding="utf-8", newline="\n")
        (self.repo / "pkg" / "corpus.py").write_text(self.CORPUS, encoding="utf-8", newline="\n")
        _git("init", "-q", cwd=self.repo)
        _git("add", "pkg/__init__.py", "pkg/corpus.py", cwd=self.repo)
        self.artifacts = self.repo / ".code-map"

    def tearDown(self):
        self._tmp.cleanup()

    def _tags(self):
        with contextlib.redirect_stdout(io.StringIO()):
            code = cli.main(["extract", "--root", str(self.repo),
                             "--artifacts", str(self.artifacts)])
        self.assertEqual(code, 0)
        return [st for st in statements_of(self.artifacts) if st["p"] == "tag"]

    def test_comment_tags_plain_comment_does_not_extract_as_a_tag(self):
        tags = self._tags()

        self.assertTrue(any(t["s"] == "pkg.corpus:scaled" for t in tags),
                        "positive control: the Rationale: tag on scaled() did "
                        "not extract -- a broken extractor would make the "
                        "negative assertion below pass vacuously")
        self.assertFalse(any(t["s"] == "pkg.corpus:plain_note" for t in tags),
                         "an ordinary '# Note: ...' comment extracted as a tag")

    def test_comment_tags_aliased_keywords_extract_normalized_to_rationale(self):
        """Gate g7 remediation fix 2: Assumption:/Constraint: are ALIASED,
        not retired -- both extract, and both normalize to kind Rationale
        at the emission site, with their own distinct text preserved."""
        tags = self._tags()

        self.assertTrue(any(t["s"] == "pkg.corpus:scaled" for t in tags),
                        "positive control: the Rationale: tag on scaled() did "
                        "not extract -- a broken extractor would make the "
                        "assertions below prove nothing")
        aliased = [t for t in tags if t["s"] == "pkg.corpus:aliased_words"]
        self.assertEqual(len(aliased), 2, aliased)
        for t in aliased:
            with self.subTest(text=t["d"]["text"]):
                self.assertEqual(t["o"], "Rationale",
                                 "an aliased keyword extracted without its kind "
                                 "normalized to Rationale")
        texts = {t["d"]["text"] for t in aliased}
        self.assertEqual(texts, {"this word aliases to Rationale: at extraction.",
                                 "same story -- this word aliases too."},
                         "the two aliased tags' own distinct text must survive "
                         "extraction unchanged -- only the kind is normalized")


_SUBPKG_SOURCE = '''"""A module living inside a real subpackage."""


def inside():
    """Defined inside pkg.sub, which no other module shares."""
    return 1
'''

_LOOSE_SOURCE = '''"""A module with no subpackage of its own."""


def loose():
    """Defined directly under pkg, no nesting."""
    return 2
'''


def _make_nested_subpackage_repo(tmp: Path):
    """One real subpackage (`pkg.sub`, exactly ONE member module — no other
    module shares that prefix) and one loose module directly under `pkg`.

    The minimal fixture that can tell a grouped bucket from a loose one, and
    prove the grouping rule carries no minimum size: `pkg.sub` has exactly one
    member and still gets its own heading. `pkg/sub/__init__.py` is
    deliberately NOT created — the corpus is `git ls-files -- *.py`, not a
    real import, so nothing here needs `pkg.sub` to be an importable package,
    only a directory two files share."""
    (tmp / "pkg" / "sub").mkdir(parents=True)
    (tmp / "pkg" / "__init__.py").write_text("", encoding="utf-8", newline="\n")
    (tmp / "pkg" / "other.py").write_text(_LOOSE_SOURCE, encoding="utf-8", newline="\n")
    (tmp / "pkg" / "sub" / "mod.py").write_text(_SUBPKG_SOURCE, encoding="utf-8", newline="\n")
    _git("init", "-q", cwd=tmp)
    _git("add", "pkg/__init__.py", "pkg/other.py", "pkg/sub/mod.py", cwd=tmp)


class TopIndexSecondTierTests(unittest.TestCase):
    """`g4`: the top index gets a SECOND TIER so it routes instead of listing.

    A cold reader must be able to learn the corpus's full breadth -- every
    top-level package and its size -- before reading a single per-module
    bullet, and within a package a module nested under a real subpackage must
    group with it rather than sit interleaved with the package's own loose
    modules.

    THE TRAP this class is built against (critic F9): ~75% of the real
    repo's entities are test code, and a tier that only works because of that
    shape would look perfect here and fail on the next corpus. Every
    assertion below is a property of dotted-name STRUCTURE -- how many
    segments a module's own name carries, which prefixes repeat -- never a
    name, a convention (`src/`, `test_`), or a count that only holds on this
    corpus. `.agent-work/issue-456/evidence/g4_cross_corpus.py` demonstrates
    the same structural rule on `f1Brainz` and `superCoolSpaceSim`."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _top_index(self, make):
        make(self.repo)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["build", "--root", str(self.repo)]), 0)
        return (self.repo / "map" / "INDEX.md").read_text(encoding="utf-8")

    def test_top_index_lists_every_top_level_package_before_the_first_module_bullet(self):
        """The measured failure this gate exists to fix: a trial agent read 60
        lines of the flat list and never learned the corpus had a `tests`
        package holding most of it. The overview must be readable before any
        per-module bullet, so a bounded read still sees every package."""
        text = self._top_index(_make_cross_module_repo)
        lines = text.splitlines()

        self.assertIn("## packages", lines, text)
        overview_at = lines.index("## packages")
        bullet_lines = [i for i, ln in enumerate(lines) if ln.startswith("- [")]
        self.assertTrue(bullet_lines,
                        "input precondition: the tree must contain at least one "
                        "module bullet, or 'before the first bullet' is vacuous")

        self.assertLess(overview_at, bullet_lines[0],
                        "the package overview must appear before any per-module bullet")
        self.assertIn("pkg: 3 modules, 3 entities", text,
                      "the overview must show every top-level package's own size")

    def test_top_index_groups_a_real_subpackage_under_its_own_heading_with_no_minimum_size(self):
        """`pkg.sub` has exactly ONE member module and still gets a heading --
        proof the grouping rule carries no absolute-count threshold (critic
        F4): a group of one is not a special case, it is the same rule."""
        text = self._top_index(_make_nested_subpackage_repo)

        self.assertIn("### pkg.sub (1 modules, 1 entities)", text, text)
        self.assertIn("[pkg.sub.mod](pkg.sub.mod/INDEX.md)", text)

    def test_top_index_lists_a_loose_module_directly_with_no_subheading(self):
        """A module with no subpackage of its own is listed the same way it
        always was -- an honest report of a flat corpus, not a fallback."""
        text = self._top_index(_make_nested_subpackage_repo)

        self.assertIn("[pkg.other](pkg.other/INDEX.md)", text)
        self.assertNotIn("### pkg.other", text)


class TopIndexPageLocationTests(unittest.TestCase):
    """`tc31`, owned by `g4`: nothing tied a page's LOCATION to its CONTENT --
    a page could be swapped into another module's directory and every check
    `g1`-`g3` shipped would still pass, because all of them read a page by its
    TITLE, never by where it sits. The new top-index tier adds more routing
    structure on top of that same layout, so this gate is where the gap either
    closes or gets twice as wide; this class closes it."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _make_cross_module_repo(self.repo)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["build", "--root", str(self.repo)]), 0)

    def tearDown(self):
        self._tmp.cleanup()

    def _check(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = cli.main(["check", "--root", str(self.repo)])
        return code, buf.getvalue()

    def test_top_index_page_location_check_passes_on_an_intact_map(self):
        """The positive control -- without it, a check that always failed
        would satisfy the falsifier below just as well as a real one."""
        code, out = self._check()
        self.assertEqual(code, 0, out)
        self.assertIn("ok   page-location-matches-content", out)

    def test_top_index_page_location_check_catches_a_page_relocated_to_the_wrong_module_directory(self):
        """The reproduction of `tc31` itself: physically move a built page
        into a SIBLING module's directory, title unchanged. Every check
        `g1`-`g3` shipped reads a page by its title and finds `pkg.callee:target`
        still present in the tree -- none of them ask WHERE."""
        moved_from = self.repo / "map" / "pkg.callee" / "target.md"
        moved_to = self.repo / "map" / "pkg.far" / "target.md"
        self.assertTrue(moved_from.exists(),
                        "input precondition: the page to relocate must exist")
        content = moved_from.read_text(encoding="utf-8")
        self.assertEqual(content.splitlines()[0], "# pkg.callee:target",
                         "input precondition: the page's own title still names its "
                         "true module, or relocating it changes nothing this check reads")

        moved_from.unlink()
        moved_to.write_text(content, encoding="utf-8", newline="\n")

        code, out = self._check()

        self.assertNotEqual(code, 0, "a page titled for one module, sitting inside "
                                     "another module's directory, passed `check`\n" + out)
        self.assertIn("FAIL page-location-matches-content", out)
        self.assertIn("pkg.callee:target", out)


class HoleRatioBaselineTests(unittest.TestCase):
    """Gate `gb`, threshold family 1: holes/entities against
    `thresholds.HOLE_RATIO_CEILING`.

    Against the REAL corpus, built fresh into scratch so the committed `map/`
    tree is not touched. See `thresholds.HOLE_RATIO_CEILING`'s own docstring
    for the derivation (measured on this repo AND on f1Brainz, a different
    shape and scale) and the one-line action for when it fires."""

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
        cls.report = json.loads(
            (scratch / "artifacts" / "render_report.json").read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        if cls._tmp is not None:
            cls._tmp.cleanup()

    def test_baseline_hole_ratio_stays_under_the_regression_ceiling(self):
        holes, entities = self.report["holes"], self.report["entities"]
        self.assertGreater(entities, 0,
                           "input precondition: the real corpus must define entities, "
                           "or a 0/0 ratio would not test anything")
        ratio = holes / entities
        self.assertLessEqual(
            ratio, thresholds.HOLE_RATIO_CEILING,
            f"holes/entities = {ratio:.3f} ({holes}/{entities}) crossed the "
            f"{thresholds.HOLE_RATIO_CEILING} regression ceiling -- see "
            "thresholds.HOLE_RATIO_CEILING's docstring for what to open first")


class HoleRatioBaselineFalsifierTests(unittest.TestCase):
    """Proves `HoleRatioBaselineTests` can actually fail. A ceiling that never
    goes red on anything is indistinguishable from no ceiling at all.

    `_make_entity_repo`'s three entities (`Widget`, `Widget.spin`, `helper`)
    all carry docstrings, so an intact build reports 0 holes -- the positive
    control. Mutating `render.summary_of` to always return `None` is a
    docstring-extraction regression in miniature: every entity loses its
    summary, holes/entities goes from 0.0 to 1.0, and the ceiling must catch
    that."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _make_entity_repo(self.repo)

    def tearDown(self):
        self._tmp.cleanup()

    def test_baseline_ceiling_holds_on_an_intact_map(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["build", "--root", str(self.repo)]), 0)
        report = json.loads(
            (self.repo / ".code-map" / "render_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["holes"], 0,
                         "input precondition: the fixture's entities must all carry "
                         "docstrings, or the falsifier below proves nothing")
        ratio = report["holes"] / report["entities"]
        self.assertLessEqual(ratio, thresholds.HOLE_RATIO_CEILING)

    def test_baseline_ceiling_trips_when_docstring_extraction_breaks(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        host = mutated_package(tmp.name, "render.py",
                               [("return docs.get(key)", "return None")])

        proc = run_code_map(host, "build", "--root", str(self.repo))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        report = json.loads(
            (self.repo / ".code-map" / "render_report.json").read_text(encoding="utf-8"))

        self.assertGreater(report["entities"], 0,
                           "input precondition: the fixture must define entities, or a "
                           "ratio of 0/0 would not test anything")
        ratio = report["holes"] / report["entities"]
        self.assertGreater(
            ratio, thresholds.HOLE_RATIO_CEILING,
            "MUTANT SURVIVED: summary_of() always returning None (every docstring "
            f"lost) produced holes/entities = {ratio:.3f}, which did not cross the "
            "ceiling -- the check cannot fail")


def _template_literal_constants(source):
    """Every string literal `render.py`'s OWN SOURCE authors directly --
    `ast.Constant` string nodes wherever they occur, including the literal
    segments of an f-string (`JoinedStr`'s `Constant` children), since a
    literal's text is fixed at parse time and can never carry a runtime
    interpolated value -- MINUS render.py's own module/class/function
    docstrings, which document the module for a developer and never reach a
    rendered page.

    This is EXACT-LINE PROVENANCE by construction, not a substring match
    against rendered page text: a node returned here is, by where it sits in
    render.py's own AST, text the renderer authored itself. Text that reaches
    a page through an f-string's `{expr}` part (a docstring summary, a
    symbol name, a file path, an attribute value) is never a `Constant` at
    that interpolation site -- it is the runtime VALUE of `expr`, invisible
    to this scan -- so source content copied onto a page is categorically out
    of scope, never something this function has to tell apart from template
    text after the fact."""
    tree = ast.parse(source)
    docstring_ids = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            if (node.body and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)):
                docstring_ids.add(id(node.body[0].value))
    return [node for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
            and id(node) not in docstring_ids]


class TemplateAsciiProvenanceTests(unittest.TestCase):
    """Gate `gb`, threshold family 2: `thresholds.TEMPLATE_ASCII_INVARIANT`.

    386 of this repo's rendered pages ARE non-ASCII today, every one traced
    to pre-existing docstring prose reproduced VERBATIM from source (an
    em-dash in `scripts/agent_work_root.py`) -- correct behaviour, since the
    map must not censor source text. A check that grepped rendered pages for
    non-ASCII bytes would be the twitchy version the handoff explicitly
    rejects: it cannot tell "the renderer wrote this" from "the renderer
    copied this out of a docstring" without re-deriving provenance from
    scratch, and would fire on ordinary source-content churn forever.

    So this reads `render.py`'s own AST instead (`_template_literal_
    constants`) and asserts every literal segment it authors itself is
    ASCII. It never reads a rendered page at all -- provenance is decided at
    the SOURCE, where "wrote it myself" vs "copied it from elsewhere" is
    categorical rather than inferred."""

    def test_ascii_render_py_authors_no_non_ascii_template_text(self):
        source = (CODE_MAP / "render.py").read_text(encoding="utf-8")
        offenders = [(node.lineno, repr(node.value))
                     for node in _template_literal_constants(source)
                     if not node.value.isascii()]
        self.assertEqual(
            offenders, [],
            f"non-ASCII literal(s) authored directly in render.py's own template "
            f"text (thresholds.TEMPLATE_ASCII_INVARIANT): {offenders} -- open the "
            "named line(s) and replace the character. This is NEVER the fix for a "
            "non-ASCII rendered PAGE -- that is source content and belongs untouched")


class TemplateAsciiProvenanceFalsifierTests(unittest.TestCase):
    """Proves the invariant above can actually fail, and that it stays blind
    to the exact case it must not censor."""

    def test_ascii_scan_catches_a_non_ascii_character_spliced_into_a_template_literal(self):
        source = (CODE_MAP / "render.py").read_text(encoding="utf-8")
        self.assertEqual(source.count("counted: calls and reads"), 1,
                         "input precondition: the anchor must occur exactly once "
                         "in render.py, or the mutation below is not the mutation "
                         "this test claims to apply")
        mutated = source.replace("counted: calls and reads",
                                 "counted — calls and reads", 1)

        offenders = [(node.lineno, repr(node.value))
                     for node in _template_literal_constants(mutated)
                     if not node.value.isascii()]

        self.assertNotEqual(
            offenders, [],
            "MUTANT SURVIVED: an em-dash spliced into REFS_LEGEND's own literal "
            "text was not caught")

    def test_ascii_scan_stays_blind_to_non_ascii_text_reaching_a_page_through_interpolation(self):
        """The positive control for the thing this check must NOT do: censor
        source content. `EXTERNAL` stands in for a docstring summary loaded
        from the statement store at runtime -- exactly like a real one, it
        never appears as a literal in the "render.py" source being scanned;
        only its IMPORT does. `entity_page` interpolates it, so the rendered
        page this fixture stands in for would carry the em-dash -- correct
        behaviour, since the map must not censor source text -- while the
        source text actually scanned carries none."""
        external_module_source = (
            'EXTERNAL = "an em—dash, reproduced verbatim from source"\n')
        self.assertFalse(external_module_source.isascii(),
                         "input precondition: EXTERNAL must actually be non-ASCII, "
                         "or this test cannot tell a real exclusion from a vacuous one")

        render_like_source = (
            'from fixture_external import EXTERNAL\n'
            'def entity_page(key):\n'
            '    return f"{key}: {EXTERNAL} -- literal ascii suffix"\n'
        )
        offenders = [node for node in _template_literal_constants(render_like_source)
                     if not node.value.isascii()]
        self.assertEqual(offenders, [],
                         "a name threaded through an f-string's {expr} part is not "
                         "a Constant at its use site, and must never be treated as "
                         "one -- only the FILE that actually authors the literal "
                         "(never reached by this scan) may carry non-ASCII text")


_RECALL_BASE_SOURCE = '''"""Base module: definitions read and called from elsewhere."""


GREETING = "hello"


def helper(x):
    """Add one."""
    return x + 1


class Thing:
    """Holds a value."""

    def __init__(self):
        self.value = 0

    def bump(self):
        """Reads and writes self.value; calls helper; reads GREETING."""
        self.value = helper(self.value)
        return GREETING
'''

_RECALL_USER_SOURCE = '''"""User module: cross-module and same-module calls, reads and writes."""

from .base import GREETING, helper, Thing

TABLE = {}


def use_it():
    """Calls cross-module helper and Thing(); reads cross-module GREETING;
    calls same-module helper2; writes a module-level dict entry."""
    thing = Thing()
    result = helper(1)
    doubled = helper2(2)
    TABLE["k"] = result
    return GREETING, thing, result, doubled


def helper2(n):
    """Same-module helper."""
    return n * 2
'''


def _make_recall_fixture_repo(tmp: Path):
    """Two small, hand-authored modules exercising real-shaped calls, reads
    and writes: cross-module and same-module calls, a cross-module constant
    read, a `self.attr` read/write pair, and a subscript write (which also
    reads its own base name -- see `RECALL_GROUND_TRUTH`'s docstring)."""
    (tmp / "fixture_pkg").mkdir()
    (tmp / "fixture_pkg" / "__init__.py").write_text("", encoding="utf-8", newline="\n")
    (tmp / "fixture_pkg" / "base.py").write_text(
        _RECALL_BASE_SOURCE, encoding="utf-8", newline="\n")
    (tmp / "fixture_pkg" / "user.py").write_text(
        _RECALL_USER_SOURCE, encoding="utf-8", newline="\n")
    _git("init", "-q", cwd=tmp)
    _git("add", "fixture_pkg/__init__.py", "fixture_pkg/base.py",
         "fixture_pkg/user.py", cwd=tmp)


#: Gate `gb`, threshold family 3: the HAND-LABELED ground truth `RecallFloorTests`
#: measures recall against. Every tuple below is this implementer's own manual
#: read of `_RECALL_BASE_SOURCE` / `_RECALL_USER_SOURCE` against
#: `extract.py`'s documented resolution rules (R1-R8) -- there is no automated
#: oracle behind any of these three lists, `writes` included: this pipeline is
#: stdlib only (no SCIP), and the design-time SCIP cross-check was blind to
#: `writes` anyway (DESIGN_SPEC TS7). Eleven edges total, small enough to
#: re-verify by hand in one sitting -- NOT a claim that this generalizes past
#: the patterns actually present here (plain calls, class instantiation,
#: `self.attr` read/write, a module-level constant read, a subscript write).
#: `s` is the CALLER symbol, `o` the CALLEE symbol; both must appear on an
#: `internal`-resolved statement of the named predicate for the edge to count
#: as matched.
RECALL_GROUND_TRUTH = {
    "calls": (
        ("fixture_pkg.base:Thing.bump", "fixture_pkg.base:helper"),
        ("fixture_pkg.user:use_it", "fixture_pkg.base:Thing"),
        ("fixture_pkg.user:use_it", "fixture_pkg.base:helper"),
        ("fixture_pkg.user:use_it", "fixture_pkg.user:helper2"),
    ),
    "reads": (
        ("fixture_pkg.base:Thing.bump", "fixture_pkg.base:GREETING"),
        ("fixture_pkg.base:Thing.bump", "fixture_pkg.base:Thing.value"),
        ("fixture_pkg.user:use_it", "fixture_pkg.base:GREETING"),
        ("fixture_pkg.user:use_it", "fixture_pkg.user:TABLE"),
    ),
    "writes": (
        ("fixture_pkg.base:Thing.__init__", "fixture_pkg.base:Thing.value"),
        ("fixture_pkg.base:Thing.bump", "fixture_pkg.base:Thing.value"),
        # `TABLE["k"] = result` -- a subscript write emits BOTH a "reads" edge
        # for the base name (counted above) AND this "writes" edge, suffixed
        # `[]` by `extract._store`'s Subscript branch.
        ("fixture_pkg.user:use_it", "fixture_pkg.user:TABLE[]"),
    ),
}


def _recall_by_predicate(statements, ground_truth=RECALL_GROUND_TRUTH):
    """predicate -> (matched, total) against `ground_truth`, checking that an
    `internal`-resolved statement of exactly that shape exists somewhere in
    `statements`. `total` is always `len(ground_truth[predicate])`, never a
    count read off the corpus -- this is recall against a FIXED hand-labeled
    set, not a self-referential count that could never fail to agree with
    itself."""
    found = {(st["p"], st["s"], st["o"]) for st in statements if st.get("res") == "internal"}
    out = {}
    for predicate, edges in ground_truth.items():
        matched = sum(1 for s, o in edges if (predicate, s, o) in found)
        out[predicate] = (matched, len(edges))
    return out


class RecallFloorTests(unittest.TestCase):
    """Gate `gb`, threshold family 3: `thresholds.RECALL_FLOORS`, one floor per
    predicate (`calls`, `reads`, `writes`), measured against
    `RECALL_GROUND_TRUTH` -- see its docstring for the derivation and its
    stated confidence (a small hand-labeled fixture, not a statistical sample
    of the whole extractor's error surface)."""

    _tmp = None

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.repo = Path(cls._tmp.name)
        _make_recall_fixture_repo(cls.repo)
        proc = run_code_map(CODE_MAP.parents[1], "extract", "--root", str(cls.repo),
                            "--artifacts", str(cls.repo / ".code-map"))
        if proc.returncode != 0:
            cls._tmp.cleanup()
            raise AssertionError(f"HARNESS ERROR: fixture extraction failed, so nothing "
                                 f"below is evidence\n{proc.stderr[-2000:]}")
        cls.recall = _recall_by_predicate(statements_of(cls.repo / ".code-map"))

    @classmethod
    def tearDownClass(cls):
        if cls._tmp is not None:
            cls._tmp.cleanup()

    def test_recall_ground_truth_fixture_actually_exercises_all_three_predicates(self):
        """Input precondition: an empty ground-truth list for a predicate would
        pass any floor vacuously."""
        for predicate in ("calls", "reads", "writes"):
            self.assertGreater(len(RECALL_GROUND_TRUTH[predicate]), 0,
                               f"the {predicate} ground truth is empty; the floor "
                               f"for it cannot mean anything")

    def test_recall_meets_its_committed_floor_for_every_predicate(self):
        for predicate, floor in thresholds.RECALL_FLOORS.items():
            matched, total = self.recall[predicate]
            ratio = matched / total
            self.assertGreaterEqual(
                ratio, floor,
                f"{predicate} recall = {ratio:.3f} ({matched}/{total}) fell under "
                f"the committed floor {floor} -- see thresholds.RECALL_FLOORS's "
                f"docstring for what to open first")


class RecallFloorFalsifierTests(unittest.TestCase):
    """Proves the floor above can actually fail, and stays scoped to the
    predicate it was supposed to catch.

    The mutation retargets ONE anchor -- `_store`'s `self._ref(t, "writes")`,
    the Name/Attribute write branch -- from `"writes"` to `"reads"`. That
    breaks exactly 2 of the 3 hand-labeled `writes` edges (both `self.value`
    attribute writes); the third (`TABLE["k"] = ...`'s subscript write) is
    emitted by a DIFFERENT line and stays intact, so this is a real
    predicate-dropping regression, not a wholesale extractor breakage -- and
    `calls`/`reads` recall must stay exactly where they were, proving the
    mutation did not accidentally widen its own damage."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _make_recall_fixture_repo(self.repo)

    def tearDown(self):
        self._tmp.cleanup()

    def test_recall_floor_trips_when_the_extractor_drops_a_predicate(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        host = mutated_package(tmp.name, "extract.py",
                               [('            self._ref(t, "writes")',
                                 '            self._ref(t, "reads")')])

        proc = run_code_map(host, "extract", "--root", str(self.repo),
                            "--artifacts", str(self.repo / ".code-map"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        recall = _recall_by_predicate(statements_of(self.repo / ".code-map"))

        writes_matched, writes_total = recall["writes"]
        self.assertLess(
            writes_matched / writes_total, thresholds.RECALL_FLOORS["writes"],
            "MUTANT SURVIVED: misclassifying attribute writes as reads did not "
            "push writes recall under its floor")
        for predicate in ("calls", "reads"):
            matched, total = recall[predicate]
            self.assertGreaterEqual(
                matched / total, thresholds.RECALL_FLOORS[predicate],
                f"the writes-only mutation also broke {predicate} recall, which "
                "means the falsifier is not scoped to the predicate it claims")


def _make_churn_fixture_repo(tmp: Path, n=8):
    """`n` independent single-function caller modules, all calling ONE shared
    function defined in `hub.py` -- a small, fast, fully-controlled stand-in
    for BOTH real-corpus edit classes `ChurnRatioTests` measures: an ordinary
    local edit (edit `hub.py`'s own docstring -- touches its own page and
    nothing else's) and a widely-referenced-symbol rename (rename `shared`
    -- touches every one of the `n` callers' own pages, one line each)."""
    pkg = tmp / "churn_pkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8", newline="\n")
    (pkg / "hub.py").write_text(
        '"""Hub module: one function every other module calls."""\n\n\n'
        'def shared(x):\n'
        '    """Do the shared thing."""\n'
        '    return x + 1\n',
        encoding="utf-8", newline="\n")
    names = ["hub.py"]
    for i in range(n):
        (pkg / f"mod{i}.py").write_text(
            f'"""Module {i}."""\n\n'
            f'from .hub import shared\n\n\n'
            f'def func{i}(x):\n'
            f'    """Do thing {i}."""\n'
            f'    return shared(x)\n',
            encoding="utf-8", newline="\n")
        names.append(f"mod{i}.py")
    _git("init", "-q", cwd=tmp)
    _git("add", "churn_pkg/__init__.py", *[f"churn_pkg/{nm}" for nm in names], cwd=tmp)
    return names


def _diff_line_count(a_text, b_text):
    """Added-or-removed lines between two texts, unified-diff style -- the
    SAME unit the design process measured churn in at cycle-4 (98 map lines
    vs 84 source lines), never a page or byte count."""
    diff = difflib.unified_diff(a_text.splitlines(), b_text.splitlines(), lineterm="")
    return sum(1 for ln in diff if ln.startswith(("+", "-")) and not ln.startswith(("+++", "---")))


def _map_diff_lines(root_a, root_b):
    """Total added-or-removed lines across every page that differs between
    two rendered trees."""
    def pages(root):
        return {p.relative_to(root).as_posix(): p.read_text(encoding="utf-8")
                for p in root.rglob("*.md")}
    a, b = pages(root_a), pages(root_b)
    return sum(_diff_line_count(a.get(path, ""), b.get(path, ""))
              for path in sorted(set(a) | set(b)) if a.get(path) != b.get(path))


class ChurnRatioTests(unittest.TestCase):
    """Gate `gb`, threshold family 4: `thresholds.CHURN_RATIO_CEILING_LOCAL_EDIT`
    / `_RENAME`, on the small, fast, fully-controlled `_make_churn_fixture_repo`.

    THE REAL-CORPUS MEASUREMENT lives in this gate's IMPLEMENTER_RESULT, not
    here: rebuilding this repo's real 3865-page tree and an isolated-worktree
    rename of `tests.test_checklist_engine:gated` (212 real callers,
    identified by inbound scan rather than guessed) is exactly the kind of
    one-time, expensive-to-repeat evidence `g5`'s `measure_split.py` already
    set precedent for -- reported once, not re-run every suite invocation.
    Measured there: local edit 1.27x, rename 1.02x, both under the 3x
    ceiling -- the ceiling HELD, on the first-ever measurement of the rename
    case. This class instead proves the MECHANISM behaves the same way at a
    scale fast enough to run on every `pytest` invocation, using the exact
    same `map diff lines / source diff lines` unit."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _make_churn_fixture_repo(self.repo)

    def tearDown(self):
        self._tmp.cleanup()

    def _build(self, out_name):
        artifacts = self.repo / f".code-map-{out_name}"
        out = self.repo / out_name
        with contextlib.redirect_stdout(io.StringIO()):
            code = cli.main(["build", "--root", str(self.repo),
                             "--artifacts", str(artifacts), "--out", str(out)])
        self.assertEqual(code, 0, f"HARNESS ERROR: build into {out_name} failed")
        return out

    def test_churn_local_edit_stays_under_the_ceiling(self):
        before = self._build("map-before")
        hub = self.repo / "churn_pkg" / "hub.py"
        source_before = hub.read_text(encoding="utf-8")
        source_after = source_before.replace(
            '"""Do the shared thing."""',
            '"""Do the shared thing.\n\n    Extended by one ordinary docstring line."""')
        self.assertNotEqual(source_before, source_after,
                            "input precondition: the edit must actually change the file")
        hub.write_text(source_after, encoding="utf-8", newline="\n")
        after = self._build("map-after")

        source_diff = _diff_line_count(source_before, source_after)
        map_diff = _map_diff_lines(before, after)
        self.assertGreater(source_diff, 0,
                           "input precondition: a 0-line source diff makes any ratio undefined")
        ratio = map_diff / source_diff
        self.assertLessEqual(
            ratio, thresholds.CHURN_RATIO_CEILING_LOCAL_EDIT,
            f"local-edit churn ratio {ratio:.2f} ({map_diff}/{source_diff}) crossed "
            f"the {thresholds.CHURN_RATIO_CEILING_LOCAL_EDIT}x ceiling")

    def test_churn_widely_referenced_rename_stays_under_the_ceiling(self):
        before = self._build("map-before")
        files = sorted((self.repo / "churn_pkg").glob("*.py"))
        sources_before = {f: f.read_text(encoding="utf-8") for f in files}
        total_source_diff = 0
        for f, text in sources_before.items():
            new_text, n = re.subn(r"\bshared\b", "shared_v2", text)
            if n:
                f.write_text(new_text, encoding="utf-8", newline="\n")
                total_source_diff += _diff_line_count(text, new_text)
        self.assertGreater(total_source_diff, 0,
                           "input precondition: the rename must actually change the fixture")
        after = self._build("map-after")

        map_diff = _map_diff_lines(before, after)
        ratio = map_diff / total_source_diff
        self.assertLessEqual(
            ratio, thresholds.CHURN_RATIO_CEILING_RENAME,
            f"rename churn ratio {ratio:.2f} ({map_diff}/{total_source_diff}) crossed "
            f"the {thresholds.CHURN_RATIO_CEILING_RENAME}x ceiling")


class ChurnRatioFalsifierTests(unittest.TestCase):
    """Proves the ceiling above can actually fail, on a realistic defect
    class: a corpus-WIDE statistic accidentally leaking into every page,
    instead of the per-module one the header is supposed to show.

    The mutation changes ONE word: `module_index`'s `holes = sum(1 for k in
    members if not summary_of(k))` -- correctly scoped to THIS module's own
    members -- to `entities`, the whole corpus. After that, deleting a SINGLE
    docstring anywhere changes the number every module's INDEX.md prints,
    because they are all now printing the same corpus-wide count. A tiny,
    local-looking edit ripples across every page in the fixture -- exactly
    the shape the churn ceiling exists to catch."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _make_churn_fixture_repo(self.repo)

    def tearDown(self):
        self._tmp.cleanup()

    def test_churn_ceiling_trips_when_a_corpus_wide_count_leaks_into_every_page(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        host = mutated_package(
            tmp.name, "render.py",
            [("holes = sum(1 for k in members if not summary_of(k))",
              "holes = sum(1 for k in entities if not summary_of(k))")])

        before = run_code_map(host, "build", "--root", str(self.repo),
                              "--artifacts", str(self.repo / ".code-map-before"),
                              "--out", str(self.repo / "map-before"))
        self.assertEqual(before.returncode, 0, before.stderr)

        hub = self.repo / "churn_pkg" / "hub.py"
        source_before = hub.read_text(encoding="utf-8")
        source_after = source_before.replace(
            '    """Do the shared thing."""\n', '')
        self.assertNotEqual(source_before, source_after,
                            "input precondition: the edit must actually drop a docstring")
        hub.write_text(source_after, encoding="utf-8", newline="\n")

        after = run_code_map(host, "build", "--root", str(self.repo),
                             "--artifacts", str(self.repo / ".code-map-after"),
                             "--out", str(self.repo / "map-after"))
        self.assertEqual(after.returncode, 0, after.stderr)

        source_diff = _diff_line_count(source_before, source_after)
        map_diff = _map_diff_lines(self.repo / "map-before", self.repo / "map-after")
        self.assertGreater(source_diff, 0,
                           "input precondition: a 0-line source diff makes any ratio undefined")
        ratio = map_diff / source_diff
        self.assertGreater(
            ratio, thresholds.CHURN_RATIO_CEILING_LOCAL_EDIT,
            f"MUTANT SURVIVED: a corpus-wide count leaking into every module's INDEX.md "
            f"produced churn ratio {ratio:.2f} ({map_diff}/{source_diff}), which did not "
            "cross the ceiling")


class SpanHashUnitTests(unittest.TestCase):
    """`span_hash` is the atomic primitive gate g6 builds staleness detection
    on: a normalised hash of an entity's own AST subtree, immune to
    reformatting by construction, because `ast.dump` never encodes source
    text, whitespace, or comments -- and the leading docstring statement is
    stripped before dumping, because prose describing behavior is not the
    behavior (the same reasoning that excludes comments).

    Standalone, no pipeline: parses source directly and calls span_hash on
    the resulting FunctionDef node. Red for the simplest possible reason --
    the function does not exist yet -- before any wiring into extract.py's
    Extractor or run() happens."""

    @staticmethod
    def _func_node(source):
        return ast.parse(source).body[0]

    def test_stale_tag_hash_is_unchanged_by_pure_reformatting(self):
        original = (
            "def widget(x):\n"
            "    \"\"\"Doc.\"\"\"\n"
            "    total = x + 1\n"
            "    return total\n"
        )
        reformatted = (
            "def widget(x):\n"
            "    \"\"\"Doc.\"\"\"\n"
            "\n"
            "    total = x + 1  # trailing comment\n"
            "\n"
            "    return total\n"
        )
        self.assertNotEqual(original, reformatted,
                            "input precondition: the two sources must actually differ, "
                            "or an unchanged hash proves nothing")

        h1 = extract.span_hash(self._func_node(original))
        h2 = extract.span_hash(self._func_node(reformatted))

        self.assertEqual(h1, h2, "a blank line plus a trailing comment changed the hash")

    def test_stale_tag_hash_is_unchanged_by_a_docstring_only_edit(self):
        original = (
            "def widget(x):\n"
            "    \"\"\"Original doc.\"\"\"\n"
            "    return x + 1\n"
        )
        redocumented = (
            "def widget(x):\n"
            "    \"\"\"Rewritten doc that says something else entirely.\"\"\"\n"
            "    return x + 1\n"
        )

        h1 = extract.span_hash(self._func_node(original))
        h2 = extract.span_hash(self._func_node(redocumented))

        self.assertEqual(h1, h2, "a docstring-only edit changed the hash")

    def test_stale_tag_hash_changes_on_a_real_body_change(self):
        original = (
            "def widget(x):\n"
            "    \"\"\"Doc.\"\"\"\n"
            "    return x + 1\n"
        )
        mutated = (
            "def widget(x):\n"
            "    \"\"\"Doc.\"\"\"\n"
            "    return x + 2\n"
        )

        h1 = extract.span_hash(self._func_node(original))
        h2 = extract.span_hash(self._func_node(mutated))

        self.assertNotEqual(h1, h2,
                            "a genuine behavior change (1 -> 2) left the hash unchanged")


class WrappedDocstringTests(unittest.TestCase):
    """Test that docstring summaries wrapped across lines render correctly.

    Issue #456 gate g8 defect 2 (D3): summaries wrapped across multiple
    physical lines were being cut at the first newline instead of the first
    paragraph boundary (blank line per PEP 257). A wrapped summary sentence
    would be split in half: first physical line as summary, rest as body start.
    """

    def test_wrapped_summary_is_first_paragraph(self):
        """A summary spanning multiple lines before a blank line should be joined.

        This is the core defect: 'This summary is deliberately long...' spans
        two physical lines but is one paragraph, ending at the blank line."""
        code = '''def func():
    """This summary is deliberately long enough that an author
    would wrap it across two physical lines, as authors constantly do.

    Args:
        x: parameter.
    """
    pass
'''
        tree = ast.parse(code)
        func_node = tree.body[0]

        doc = ast.get_docstring(func_node)
        summary = extract.doc_summary_of(doc)
        body = extract.doc_body_of(func_node)

        # Summary should be the entire first paragraph with newlines collapsed
        expected_summary = ("This summary is deliberately long enough that an author "
                           "would wrap it across two physical lines, as authors constantly do.")
        self.assertEqual(summary, expected_summary,
                        "Summary should be first paragraph with newlines joined to spaces")

        # Body should start at Args, not with the wrap continuation
        self.assertIsNotNone(body, "Body should exist after blank line")
        self.assertTrue(body.startswith("Args:"),
                       f"Body should start at 'Args:', got: {body[:50]}")
        self.assertNotIn("would wrap", body,
                        "Body should not contain the wrapped part of the summary")

    def test_one_line_docstring_has_no_body(self):
        """A one-line docstring has only a summary, no body."""
        code = '''def func():
    """One line summary."""
    pass
'''
        tree = ast.parse(code)
        func_node = tree.body[0]

        doc = ast.get_docstring(func_node)
        summary = extract.doc_summary_of(doc)
        body = extract.doc_body_of(func_node)

        self.assertEqual(summary, "One line summary.")
        self.assertIsNone(body, "One-line docstring should have no body")

    def test_wrapped_summary_no_body(self):
        """A wrapped summary with no blank line and no body is all summary."""
        code = '''def func():
    """This is a wrapped summary that spans
    multiple physical lines but has no body
    section at all."""
    pass
'''
        tree = ast.parse(code)
        func_node = tree.body[0]

        doc = ast.get_docstring(func_node)
        summary = extract.doc_summary_of(doc)
        body = extract.doc_body_of(func_node)

        expected = ("This is a wrapped summary that spans "
                   "multiple physical lines but has no body section at all.")
        self.assertEqual(summary, expected,
                        "Entire docstring should be summary when no blank line")
        self.assertIsNone(body, "No body when no blank line separator")

    def test_dense_paragraph_over_160_chars_no_blank_line(self):
        """A realistic dense paragraph exceeding 160 chars with no blank line.

        This is the critical boundary case: common docstring shape in this
        codebase. The summary should truncate at 160 chars, and the overflow
        should appear in the body, not be silently dropped.

        Without the fix, the overflow is lost and the page ends mid-word.
        """
        code = '''def func():
    """This is a dense docstring paragraph that wraps across multiple physical
    lines in the source but forms one continuous paragraph with no blank line
    separator, causing it to exceed the 160 character summary truncation limit."""
    pass
'''
        tree = ast.parse(code)
        func_node = tree.body[0]

        doc = ast.get_docstring(func_node)
        summary = extract.doc_summary_of(doc)
        body = extract.doc_body_of(func_node)

        # Summary should be exactly 160 chars (truncated)
        self.assertEqual(len(summary), 160,
                        "Summary should be exactly 160 chars when over limit")

        # Body should contain the overflow that would have been lost
        self.assertIsNotNone(body, "Overflow should be preserved in body")
        self.assertIn("truncation limit", body,
                     "Body should contain the overflow text (end of docstring)")

        # Together, summary + body should contain substantial content
        full_reconstructed = (summary + body) if body else summary
        self.assertGreater(len(full_reconstructed), 160,
                          "Full reconstruction should exceed 160 chars")

    def test_long_first_paragraph_with_blank_line_and_body(self):
        """A first paragraph exceeding 160 chars, followed by blank line and body.

        This is the OTHER overflow case: when there's a blank line, the
        first paragraph still has overflow that would be silently lost at
        the emit sites. The fix ensures both the summary's tail AND the
        original body are recoverable.
        """
        code = '''def func():
    """This is an extremely dense first paragraph that wraps across multiple physical lines in the source code and forms one continuous sentence that definitely exceeds the 160 character truncation limit when all the lines are joined together properly.

    Args:
        x: parameter description.
        y: another parameter.

    Returns:
        The result of the operation.
    """
    pass
'''
        tree = ast.parse(code)
        func_node = tree.body[0]

        doc = ast.get_docstring(func_node)
        summary = extract.doc_summary_of(doc)
        body = extract.doc_body_of(func_node)

        # Summary must be truncated to exactly 160 chars
        self.assertEqual(len(summary), 160,
                        "Summary should be truncated to exactly 160 chars")

        # Body must exist and contain both the overflow AND the Args section
        self.assertIsNotNone(body,
                            "Body should exist when summary is truncated (overflow + Args)")
        # The overflow text past char 160 includes "character truncation limit..." — verify it's there
        self.assertIn("character truncation limit", body,
                     "Body must contain overflow text from truncated paragraph")
        self.assertIn("Args:", body,
                     "Body should contain the original Args section")

    def test_all_shapes_preserve_complete_content(self):
        """Invariant test: for all docstring shapes, summary+body contains full text.

        This is the umbrella check that would have caught both overflow cases.
        """
        test_cases = [
            # Shape 1: wrapped summary, blank line, Args
            ('''def f1():
    """Short summary line.

    Args:
        x: param.
    """
    pass
''', "wrapped summary + blank + Args"),
            # Shape 2: no blank line, no overflow
            ('''def f2():
    """Short single line."""
    pass
''', "one-liner"),
            # Shape 3: no blank line, with overflow
            ('''def f3():
    """This is a much longer docstring that wraps across multiple lines in the source code and keeps going without any blank line separator at all, causing significant overflow at the 160 character truncation limit that applies here."""
    pass
''', "no blank line with overflow"),
            # Shape 4: blank line, first para has overflow
            ('''def f4():
    """This first paragraph is extremely long and wraps across multiple lines in the source code and still keeps going, definitely exceeding the 160 character truncation limit that applies to summary extraction when joined together.

    This is the body content that comes after the blank line.
    """
    pass
''', "blank line with first-para overflow"),
        ]

        for code, description in test_cases:
            with self.subTest(shape=description):
                tree = ast.parse(code)
                func_node = tree.body[0]
                doc = ast.get_docstring(func_node)
                summary = extract.doc_summary_of(doc)
                body = extract.doc_body_of(func_node)

                # Invariant: no silent content loss
                # Branch on SHAPE (known), not MEASUREMENT (what we're testing)
                if description in ("no blank line with overflow", "blank line with first-para overflow"):
                    # These shapes MUST overflow — assert truncation happened, unconditionally
                    self.assertEqual(len(summary), 160,
                                   f"{description}: summary must be truncated to 160 chars")
                    # Body must exist and contain the overflow
                    self.assertIsNotNone(body,
                                       f"{description}: body must contain overflow when summary is 160 chars")
                    # Verify overflow text is actually present
                    if description == "no blank line with overflow":
                        self.assertIn("truncation limit", body,
                                     f"{description}: overflow text must be in body")
                    elif description == "blank line with first-para overflow":
                        self.assertIn("joined", body,
                                     f"{description}: overflow text must be in body")

                # Reconstructed text should be non-empty (applies to all shapes)
                reconstructed = (summary or "") + ((" " + body) if body else "")
                self.assertGreater(len(reconstructed), 0,
                                  f"{description}: reconstructed text empty")


class BOMParsingTests(unittest.TestCase):
    """Test that files with UTF-8 BOM prefix are handled correctly during extraction.

    Issue #456 gate g8: BOM-prefixed files silently drop out of the map because
    the extractor cannot parse them. This test verifies the fix by confirming
    that a BOM file can be extracted without error.
    """

    def test_bom_file_can_be_extracted(self):
        """A file with UTF-8 BOM should be extractable via the build_table function.

        build_table is the entry point that the extractor uses to read and parse
        files. It should handle BOM-prefixed files gracefully."""
        fixture_dir = ROOT / "tests" / "fixtures" / "bom_corpus"
        bom_file = fixture_dir / "bom_sample.py"

        self.assertTrue(bom_file.exists(), f"BOM fixture file must exist at {bom_file}")

        # Verify BOM is actually in the file
        raw_bytes = bom_file.read_bytes()
        self.assertEqual(raw_bytes[:3], b'\xef\xbb\xbf',
                        "Fixture must have actual UTF-8 BOM bytes")

        # The build_table function should NOT return None (which indicates parse failure)
        table, tree = extract.build_table(str(bom_file))

        # After the fix, table should be non-None (parse succeeded)
        self.assertIsNotNone(table, "BOM file should parse successfully (table non-None)")
        self.assertIsNotNone(tree, "BOM file should parse successfully (tree non-None)")


class MapTreeFreshnessTests(unittest.TestCase):
    """Gate gs: the tracked `map/INDEX.md` and `map/ids.jsonl` (the map entry
    point) must match what `build` produces from THIS repo's own current
    tracked source. `.agent-work/issue-456/landing-zone-measurement.md` is why
    only these two files are tracked: the negative-control measurement showed
    they are the largest zone that survives a body-only edit while still
    moving under a shape edit. A crew opening `map/INDEX.md` trusts that it is
    current; this test is the only thing that keeps that trust honest.

    Comparison is over normalized TEXT, not raw working-tree bytes.
    `.gitattributes` sets `* text=auto` and this repo runs
    `core.autocrlf=true`, so a checkout may legitimately hold CRLF while the
    committed blob (and a fresh build, which always writes `newline="\n"`)
    holds LF -- `git add` on this very gate warned 'LF will be replaced by
    CRLF the next time Git touches it' for map/INDEX.md. Reading with the
    default text-mode universal-newline translation normalizes that away, per
    CREW_CONTEXT.md's 'Writing Files On Windows': comparing raw bytes would
    read a line-ending-only checkout artifact as staleness.
    """

    def _fresh_build(self):
        """Rebuild the map from THIS repo's current tracked source into a
        scratch --out/--artifacts pair, so the real map/ and .code-map/ trees
        are never touched by this test."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        out = Path(tmp.name) / "map"
        artifacts = Path(tmp.name) / ".code-map"
        proc = subprocess.run(
            [sys.executable, "-m", "scripts.code_map", "build", "--root", str(ROOT),
             "--artifacts", str(artifacts), "--out", str(out)],
            cwd=str(ROOT), capture_output=True, text=True,
        )
        self.assertEqual(proc.returncode, 0,
                         f"fresh build failed\n{proc.stdout}\n{proc.stderr}")
        return out

    def test_map_tree_freshness_root_index_matches_a_fresh_build(self):
        fresh = self._fresh_build()
        committed = (ROOT / "map" / "INDEX.md").read_text(encoding="utf-8")
        self.assertEqual(
            (fresh / "INDEX.md").read_text(encoding="utf-8"), committed,
            "map/INDEX.md is stale: rerun `python -m scripts.code_map build "
            "--root .` and commit the result")

    def test_map_tree_freshness_ids_jsonl_matches_a_fresh_build(self):
        """`ids.jsonl` is empty in this repo -- no anchor id has ever been
        authored here, the same fact gate g6 found scanning the only real
        corpus. Empty is not a defect; a mismatch still is."""
        fresh = self._fresh_build()
        committed = (ROOT / "map" / "ids.jsonl").read_text(encoding="utf-8")
        self.assertEqual(
            (fresh / "ids.jsonl").read_text(encoding="utf-8"), committed,
            "map/ids.jsonl is stale: rerun `python -m scripts.code_map build "
            "--root .` and commit the result")


if __name__ == "__main__":
    unittest.main()
