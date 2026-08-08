"""Checks over the built map that CAN FAIL.

`check` exits non-zero when any invariant below is violated. Before gate g1
every function here printed a measurement, asserted nothing, and `run()` ended
in a literal `return 0`, so a completely broken map passed. The measurements are
gone: they were diagnostics wearing a suite's clothes.

What belongs here
-----------------
A **move-invariant** relates two independently-derived facts and holds at any
corpus size: `pages - 1 - modules == entity_pages`, a page's caller list against
a second scan of the store, a page that exists and holds nothing. It survives
every later gate that changes the map's shape, because it never mentions the
shape's numbers.

A **baseline** pins a remembered constant -- "103 modules", "3411 entities", a
page's rendered text, the header format, the section order. It goes red at every
gate that legitimately moves the map, so it would be deleted rather than
believed. Baselines belong to `gB`, after the last gate that moves the numbers.

The distinction is not "does it mention a count". It is: does the expected value
come from a memory of this corpus, or from the map itself?

What these checks read
----------------------
The store and the supplement DIRECTLY, never through `render.load_stores`. A
check whose expected value is computed by the code under test can only ever
agree with it, which is not a check. So the store scan below is written a second
time on purpose, and it is compared against the RENDERED PAGES -- the artifact a
reader actually gets -- rather than against the renderer's own in-memory state.

What they do NOT prove is recorded honestly beside each check.

`check` EXITS 1 ON THIS REPO TODAY, and that is correct
------------------------------------------------------
`page_accounting` is red by exactly one page: two entities named `Verdict` and
`verdict` resolve to one filename on a case-insensitive filesystem, so the map
advertises a page it does not have. Gate `g2` owns the rename; `g1` only asserts
it. Do not silence the check to make the command green.
"""
import collections
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

from .extract import STATEMENTS_NAME
from .supplement import SUPPLEMENT_NAME

#: How many offending items a failing check names before it summarizes. A check
#: reports every failure it found in its count; it prints the first few.
MAX_REPORTED = 10

#: The directory that holds the `scripts` package, so a rebuild can be launched
#: as `python -m scripts.code_map` in a FRESH process. Taken from this module's
#: own location, so a mutated copy of the package rebuilds through the mutated
#: copy -- which is what lets a mutation test drive this check at all.
PACKAGE_HOST = pathlib.Path(__file__).resolve().parents[2]


class MapUnderCheck:
    """The built map, loaded the way a reader gets it: pages off disk, and the
    stores read straight from their files.

    Deliberately not a wrapper over `render.py`. The renderer's indexes are the
    thing under test; rebuilding them here from the same source is what makes a
    disagreement meaningful."""

    def __init__(self, root, artifacts, out):
        self.root = pathlib.Path(root)
        self.artifacts = pathlib.Path(artifacts)
        self.out = pathlib.Path(out)
        self._supplement = None
        self._pages = None
        self._scan = None
        self._text = {}

    # -- the stores ------------------------------------------------------

    @property
    def supplement(self):
        if self._supplement is None:
            self._supplement = json.loads(
                (self.artifacts / SUPPLEMENT_NAME).read_text(encoding="utf-8"))
        return self._supplement

    @property
    def entities(self):
        return self.supplement["entities"]

    @property
    def modules(self):
        return self.supplement["modules"]

    def statements(self):
        with open(self.artifacts / STATEMENTS_NAME, encoding="utf-8") as f:
            for line in f:
                yield json.loads(line)

    @property
    def scan(self):
        """The store read a SECOND time -- see `StoreScan`."""
        if self._scan is None:
            self._scan = StoreScan(self.statements())
        return self._scan

    def symbol_of(self, key):
        """The store symbol for a supplement key, joined on (file, line).

        The renderer performs the same join to decide whose inbound edges a page
        shows. Re-deriving it here is not independent OF the join -- it is the
        same two facts read twice -- so `entity_symbol_join` cross-checks the
        join's result against the entity's own name instead of trusting it."""
        entity = self.entities[key]
        module = self.modules.get(key.split(":", 1)[0])
        if module is None:
            return None
        return self.scan.defined_at.get((module["file"], entity["line"]))

    # -- the page tree ---------------------------------------------------

    @property
    def pages(self):
        """Every page in the tree, sorted. The same `rglob` the render report
        counts with -- that is the point: the report's number is checked against
        what the tree is STRUCTURALLY required to hold, not against itself."""
        if self._pages is None:
            self._pages = sorted(self.out.rglob("*.md"))
        return self._pages

    def text(self, page):
        if page not in self._text:
            self._text[page] = page.read_text(encoding="utf-8")
        return self._text[page]

    def title_key(self, page):
        """What a page SAYS it is about: its title line.

        Pages are classified by this rather than by filename, so a page that
        landed on another page's path is still read as the entity it
        describes."""
        lines = self.text(page).splitlines()
        if lines and lines[0].startswith("# "):
            return lines[0][2:].strip()
        return None

    @property
    def entity_pages(self):
        """(page, supplement key) for every page whose title names an entity."""
        out = []
        for page in self.pages:
            key = self.title_key(page)
            if key in self.entities:
                out.append((page, key))
        return out

    def rel(self, path):
        return path.relative_to(self.out).as_posix()


class StoreScan:
    """A second reading of the statement store, written from the schema rather
    than borrowed from `render.load_stores`.

    Two facts are collected:

    - `defined_at`  (file, 1-based line) -> store symbol, from `contains`. The
      store's `q.line` is 0-based and the schema does not say so (defect D1,
      owned by g3), hence the +1.
    - `inbound`     target symbol -> {caller module: sites}, from every `calls`
      and `reads` statement that did not resolve locally.

    **What a disagreement here does and does not prove.** This scan and the
    renderer read the SAME store and share its two schema conventions. So this
    catches the renderer losing, miscounting or misattributing what the store
    says -- and it does NOT audit the store against the source. An extractor
    that never recorded a call, or recorded it at the wrong line, agrees with
    itself and passes. That is a real limit, stated rather than narrowed away."""

    def __init__(self, statements):
        self.defined_at = {}
        self.inbound = collections.defaultdict(collections.Counter)
        for st in statements:
            predicate = st["p"]
            if predicate == "contains":
                q = st["q"]
                self.defined_at[(q["file"], q["line"] + 1)] = st["o"]
            elif predicate in ("calls", "reads") and st.get("res") != "local":
                caller_module = st["s"].split(":", 1)[0]
                self.inbound[st["o"]][caller_module] += 1


# ------------------------------------------------------- the rendered line
# The ONE place that knows how a page spells its inbound references. Every
# check below works in terms of what the line MEANS -- sites, distinct caller
# modules, and which of them are named -- so a later gate that respells it
# updates this and nothing else.

REFS_PREFIX = "referenced by: "
REFS_NONE = "none found"
REFS_SELF_ONLY = re.compile(r"^(\d+) sites, this module only$")
REFS_MODULES = re.compile(r"^(\d+) sites in (\d+) modules \((.*)\)$")

#: sites: total inbound edges. modules: how many distinct modules they came
#: from. named: the modules the line actually spells out -- the renderer omits
#: the page's own module from that list, so `named` can be one short of
#: `modules` by design.
Refs = collections.namedtuple("Refs", "sites modules named")


def parse_refs(line):
    """The rendered inbound line as numbers, or None when it is not one of the
    forms this map writes."""
    body = line[len(REFS_PREFIX):].strip()
    if body == REFS_NONE:
        return Refs(0, 0, ())
    match = REFS_SELF_ONLY.match(body)
    if match:
        return Refs(int(match.group(1)), 1, ())
    match = REFS_MODULES.match(body)
    if match:
        named = tuple(n.strip() for n in match.group(3).split(",") if n.strip())
        return Refs(int(match.group(1)), int(match.group(2)), named)
    return None


def refs_lines(text):
    return [ln for ln in text.splitlines() if ln.startswith(REFS_PREFIX)]


# ------------------------------------------------------------------ checks
# Each check takes a MapUnderCheck and returns a list of human-readable
# failures. An empty list is a pass. No check raises to signal a failure --
# a raise is a broken check, and `run` lets it through rather than swallowing
# it into a pass.


def no_empty_pages(m):
    """A page that exists and holds nothing is a page the map counts and a
    reader cannot use.

    `tc26`: the render report's `pages` is `rglob("*.md")`, which counts a file
    that was created and never written, so a zero-byte page is invisible in
    every number the report publishes. This is the check that sees it."""
    return [f"{m.rel(p)}: page has no content"
            for p in m.pages
            if not p.read_text(encoding="utf-8").strip()]


#: The one page in the tree that is neither a module index nor an entity: the
#: top index. A structural fact about the layout -- there is exactly one root --
#: not a remembered fact about this corpus. It stays 1 at any corpus size, which
#: is what keeps `page_accounting` an invariant rather than a baseline.
TOP_INDEX_PAGES = 1


def page_accounting(m):
    """Every page the map CLAIMS must be a page the map HAS.

    The tree is required to hold exactly one page per module index, one per
    entity, and one top index. Both sides are derived independently: the left is
    the files on disk, the right is the store. When they disagree the map is
    advertising something a reader cannot open.

    This is the check that sees a page silently overwriting another. Two entity
    names that differ only by case resolve to one filename on Windows and macOS,
    so the second write destroys the first and every count the render report
    publishes still looks right -- `pages` is an `rglob` of the tree, so it
    agrees with the tree by construction and cannot notice (that is `tc18`, and
    `tc24` rules that counting the tree a second time is NOT the fix).

    RED ON THIS REPO TODAY, by exactly one page: `scripts.run_skill_eval:Verdict`
    and `:verdict` land on one file. Gate `g2` owns the rename; `g1` only
    asserts it. See the `xfail(strict=True)` in tests/test_code_map.py.

    TWO ARMS, and the second is the durable one.

    - COVERAGE: every module and every entity the store declares must be the
      TITLE of some page. Shape-free -- it never says where a page lives or what
      it is called, so no later gate moves it -- and it is what names the loss.
    - COUNT: `pages == 1 + modules + entities`. This is the identity the render
      report contradicts, so it is the one that is red today, and it catches a
      loss that coverage cannot: a page duplicated, or a page in the tree the
      store never asked for.

    Coverage is asserted on its own rather than only as a diagnostic when the
    count is off. Attacking the count arm alone found the hole: delete one page
    and add one stray page and the arithmetic balances while a page the map
    advertises is gone.

    The count arm is the one a later gate can legitimately move: it assumes the
    tree holds exactly one index per module plus one top index. A gate that adds
    an index tier has to update the accounting -- deliberately, not silently,
    because the constant is named here and nowhere else.

    Both arms read the TITLE of every page that exists, never the renderer's
    filename expression -- a check that derives its expectation with the code
    under test's own expression can only ever agree with it."""
    titles = {m.title_key(p) for p in m.pages}
    failures = [f"{k}: an entity the map claims and does not have"
                for k in sorted(set(m.entities) - titles)]
    failures += [f"{k}: a module index the map claims and does not have"
                 for k in sorted(set(m.modules) - titles)]
    expected = TOP_INDEX_PAGES + len(m.modules) + len(m.entities)
    actual = len(m.pages)
    if actual != expected:
        failures.append(
            f"the tree holds {actual} pages; the store accounts for {expected} "
            f"({TOP_INDEX_PAGES} top index + {len(m.modules)} module indexes + "
            f"{len(m.entities)} entities)")
    return failures


def refs_line_self_consistent(m):
    """A page's `referenced by:` line must agree with its own list.

    PAGE-LOCAL: this reads the page and nothing else -- no store, no supplement.
    `inbound_attribution` is strictly stronger wherever the store can be read,
    and on a healthy map the two agree on every entity page. Two things keep
    this one from being dead weight:

    - it covers EVERY page in the tree, while `inbound_attribution` only covers
      pages whose title names a known entity. A page that lost its title, or
      that the store no longer knows about, is invisible to the store check and
      visible here.
    - it survives the store: a later gate that changes the schema breaks the
      second derivation, and this rule still holds.

    The rules are the arithmetic the line is required to satisfy whatever the
    numbers are: you cannot name a module twice, you cannot name more modules
    than you counted, at most ONE counted module may go unnamed (the page's own,
    which the renderer leaves out because the count already implies it), you
    cannot draw N sites from more than N modules, and zero sites and zero
    modules must arrive together.

    What it does NOT prove: that the numbers are RIGHT. A line can be perfectly
    self-consistent and completely wrong -- that is `inbound_attribution`'s
    job."""
    failures = []
    for page in m.pages:
        where = m.rel(page)
        title = m.title_key(page) or ""
        own = title.split(":", 1)[0] if ":" in title else title
        for line in refs_lines(m.text(page)):
            stated = parse_refs(line)
            if stated is None:
                failures.append(f"{where}: cannot read the inbound line: {line!r}")
                continue
            named = list(stated.named)
            if len(set(named)) != len(named):
                failures.append(f"{where}: names a module more than once: {named}")
            gap = stated.modules - len(named)
            if gap < 0:
                failures.append(f"{where}: names {len(named)} modules but counts only "
                                f"{stated.modules}")
            elif gap > 1:
                failures.append(f"{where}: counts {stated.modules} modules and names "
                                f"{len(named)}; at most one -- the page's own -- may go "
                                f"unnamed")
            if stated.sites < stated.modules:
                failures.append(f"{where}: {stated.sites} sites cannot come from "
                                f"{stated.modules} modules")
            if (stated.sites == 0) != (stated.modules == 0):
                failures.append(f"{where}: {stated.sites} sites and {stated.modules} "
                                f"modules disagree about whether anything references it")
            if own and own in named:
                failures.append(f"{where}: names its own module {own!r} in the caller "
                                f"list, which the count already accounts for")
    return failures


def entity_symbol_join(m):
    """A page's title must agree with the store symbol found at its position.

    Two INDEPENDENT AST passes produce the map: `extract.py` emits a `contains`
    statement naming the symbol at (file, line), and `supplement.py` records the
    entity's qualified name and its line. The renderer welds them with a
    (file, line) join -- that join is what decides whose docstring and whose
    callers a page shows. If the two passes ever disagree about what sits at a
    position, the join silently lands a page on another entity's facts.

    Comparing the join's OUTPUT against the entity's own name is what makes this
    a check rather than a restatement: the join is re-derived here from the same
    two facts, so it is not independent OF the join, but the name is a third fact
    neither pass shares with the other.

    The WHOLE symbol, not just the leaf: since `g2` fixed D2, `extract.py` names
    every definition as its enclosing scope's symbol plus its own name, so the
    store symbol equals the supplement's qualified key for every entity in the
    corpus. Comparing leaves would let the two passes disagree about the whole
    enclosing chain -- exactly the merge D2 was -- and still pass.

    An entity that joins to NO symbol is a failure too: the renderer falls back
    to the key, and the page then shows no docstring and no callers from the
    store while still looking like a finished page."""
    failures = []
    for page, key in m.entity_pages:
        where = m.rel(page)
        symbol = m.symbol_of(key)
        if symbol is None:
            failures.append(f"{where}: {key} joins to no store symbol, so the page "
                            f"carries nothing the store knows about it")
            continue
        if key != symbol:
            failures.append(f"{where}: page is titled {key} but the store symbol at "
                            f"that position is {symbol}")
    return failures


def inbound_attribution(m):
    """Every page's caller set must match an independent full scan of the store.

    Three facts per page, all compared against the second scan rather than
    against the renderer: how many inbound sites, how many distinct modules
    they came from, and which modules those are (less the page's own, which the
    renderer leaves out of the list because the count already says `this
    module`).

    This is the check that notices a map that lies about who uses what -- the
    single thing an agent reads the map FOR."""
    failures = []
    for page, key in m.entity_pages:
        where = m.rel(page)
        lines = refs_lines(m.text(page))
        if len(lines) != 1:
            failures.append(f"{where}: {len(lines)} inbound lines, expected exactly 1")
            continue
        stated = parse_refs(lines[0])
        if stated is None:
            failures.append(f"{where}: cannot read the inbound line: {lines[0]!r}")
            continue

        symbol = m.symbol_of(key)
        truth = m.scan.inbound.get(symbol, {}) if symbol is not None else {}
        own_module = key.split(":", 1)[0]
        expected_named = tuple(sorted(set(truth) - {own_module}))

        if stated.sites != sum(truth.values()):
            failures.append(f"{where}: page says {stated.sites} inbound sites, "
                            f"the store has {sum(truth.values())}")
        if stated.modules != len(truth):
            failures.append(f"{where}: page says {stated.modules} calling modules, "
                            f"the store has {len(truth)}")
        if tuple(sorted(stated.named)) != expected_named:
            failures.append(f"{where}: page names {list(stated.named)} as callers, "
                            f"the store has {list(expected_named)}")
    return failures


def _build_into(root, workdir, hash_seed):
    """Build `root` into `workdir` in a FRESH PROCESS. Returns the page tree, or
    a failure string.

    A fresh process is the whole point. Set iteration order and dict rehashing
    vary with the interpreter's string hash seed, and a seed is fixed for the
    life of a process -- so two builds inside ONE process share it and a
    hash-ordered listing looks perfectly stable. The two seeds are pinned to
    different values rather than left to per-process randomization so the check
    exercises that difference every run instead of once in a while."""
    out = pathlib.Path(workdir) / "map"
    proc = subprocess.run(
        [sys.executable, "-m", "scripts.code_map", "build", "--root", str(root),
         "--artifacts", str(pathlib.Path(workdir) / "artifacts"), "--out", str(out)],
        cwd=str(PACKAGE_HOST), capture_output=True, text=True,
        env={**os.environ, "PYTHONHASHSEED": hash_seed},
    )
    if proc.returncode != 0:
        return None, (f"rebuild (PYTHONHASHSEED={hash_seed}) exited "
                      f"{proc.returncode}: {proc.stderr.strip()[-400:]}")
    return out, None


def _tree(root):
    """relative posix path -> bytes, for every page in a rendered tree."""
    root = pathlib.Path(root)
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in root.rglob("*") if p.is_file()}


def tree_diff(left, right):
    """Every path on which two rendered trees disagree. Empty list = identical.

    Not a boolean: the failure a reader needs is WHICH page moved."""
    a, b = _tree(left), _tree(right)
    out = []
    for path in sorted(set(a) - set(b)):
        out.append(f"{path}: in the first build only")
    for path in sorted(set(b) - set(a)):
        out.append(f"{path}: in the second build only")
    for path in sorted(set(a) & set(b)):
        if a[path] != b[path]:
            out.append(f"{path}: {len(a[path])} bytes vs {len(b[path])} bytes"
                       if len(a[path]) != len(b[path])
                       else f"{path}: same length, different bytes")
    return out


def deterministic_rebuild(m):
    """Two builds from unchanged source must produce BYTE-IDENTICAL page trees.

    Any non-empty diff is the failure. Nothing in a run report carries a
    timestamp or a duration precisely so this diff can cover the whole tree --
    do not add one.

    This does not touch the tree at `--out`: it builds twice into scratch and
    compares those two against each other, so it is a statement about the
    pipeline rather than about whether the committed tree happens to be
    fresh."""
    workdir = tempfile.mkdtemp(prefix="code-map-determinism-")
    try:
        first, err = _build_into(m.root, pathlib.Path(workdir) / "a", "0")
        if err:
            return [err]
        second, err = _build_into(m.root, pathlib.Path(workdir) / "b", "1")
        if err:
            return [err]
        return tree_diff(first, second)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


CHECKS = (
    ("no-empty-pages", no_empty_pages),
    ("page-accounting", page_accounting),
    ("refs-line-self-consistent", refs_line_self_consistent),
    ("entity-symbol-join", entity_symbol_join),
    ("inbound-attribution", inbound_attribution),
    ("deterministic-rebuild", deterministic_rebuild),
)


# ------------------------------------------------------------------- stage

def run(root, artifacts, out):
    """Run every check over the built map. Returns 0 when all pass, 1 otherwise.

    A check stage that cannot look must not report success -- a missing page
    tree or a missing store is a failure, not a skip."""
    m = MapUnderCheck(root, artifacts, out)
    missing = [str(p) for p in (m.out, m.artifacts / SUPPLEMENT_NAME,
                                m.artifacts / STATEMENTS_NAME) if not p.exists()]
    if missing:
        print("FAIL cannot check: nothing built at " + ", ".join(missing)
              + " -- run `build` first")
        return 1

    failed = []
    for name, check in CHECKS:
        failures = check(m)
        if failures:
            failed.append(name)
            print(f"FAIL {name}: {len(failures)}")
            for line in failures[:MAX_REPORTED]:
                print("      " + line)
            if len(failures) > MAX_REPORTED:
                print(f"      ... and {len(failures) - MAX_REPORTED} more")
        else:
            print(f"ok   {name}")
    if failed:
        print(f"FAILED {len(failed)} of {len(CHECKS)} checks: " + ", ".join(failed))
        return 1
    print(f"passed {len(CHECKS)} checks")
    return 0
