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

from scripts.code_map import checks, cli, discovery, extract, render  # noqa: E402

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


if __name__ == "__main__":
    unittest.main()
