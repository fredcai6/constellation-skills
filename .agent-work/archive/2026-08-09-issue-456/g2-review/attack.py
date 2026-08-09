"""Reviewer's own mutation harness for gate g2. Written independently of
tests/test_code_map.py so a defect in that harness cannot hide here.

Usage:  python .agent-work/issue-456/g2-review/attack.py <attack-name>
"""
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[3]
CODE_MAP = ROOT / "scripts" / "code_map"


def _git(*args, cwd):
    return subprocess.run(("git",) + args, cwd=str(cwd), check=True,
                          capture_output=True, text=True)


def mutate(tmpdir, edits):
    """edits: {module: [(old, new), ...]}. Every anchor must occur exactly once."""
    dest = pathlib.Path(tmpdir) / "scripts" / "code_map"
    shutil.copytree(CODE_MAP, dest, ignore=shutil.ignore_patterns("__pycache__"))
    for module, subs in edits.items():
        original = (CODE_MAP / module).read_text(encoding="utf-8")
        text = original
        for old, new in subs:
            n = original.count(old)
            if n != 1:
                raise SystemExit(
                    f"HARNESS ERROR: anchor occurs {n}x in {module}, expected 1:\n  {old!r}")
            text = text.replace(old, new, 1)
            if text.count(old) != 0:
                raise SystemExit(f"HARNESS ERROR: anchor survived: {old!r}")
        (dest / module).write_text(text, encoding="utf-8", newline="\n")
    return pathlib.Path(tmpdir)


def run_map(host, *args):
    env = dict(os.environ)
    env.pop("FORCE_COLOR", None)
    env.pop("PYTHONIOENCODING", None)
    return subprocess.run([sys.executable, "-m", "scripts.code_map", *args],
                          cwd=str(host), capture_output=True, text=True, env=env)


# ---------------------------------------------------------------- fixtures

NESTED = '''"""Closures in methods, plus a class in a function."""


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
        """Defined inside a function."""

        def method(self):
            """A method of a class defined inside a function."""
            return 3

    return Bundle
'''

USER = '''"""A second module that calls into the first, twice."""
from pkg import nested


def drive():
    """Call the holder from another module."""
    h = nested.Holder()
    return h.first(), h.second()


def drive_again():
    """Call it again, so the caller module has more than one site."""
    return nested.Holder().first()


def local_user():
    """A same-module caller, so the own-module clause is exercised."""
    return drive()
'''

# A case-only family with a DIFFERENT SHAPE from Verdict/verdict: the pair is
# nested inside a class (dotted qualified names), and there is a third
# module-level triple. Nothing here is named Verdict.
CASEY = '''"""Case-only page identity, in shapes the implementer did not use."""


class Box:
    """Holds a nested class and a method whose names differ only by case."""

    class Item:
        """A nested class."""

        def use(self):
            """Something to give it a body."""
            return 1

    def item(self):
        """A method whose name folds onto the nested class's."""
        return 2


class Thing:
    """Module-level, member of a three-way fold group."""


def thing():
    """Second member of the fold group."""
    return Thing


def THING():
    """Third member of the fold group."""
    return thing
'''


def make_repo(tmp, files):
    tmp = pathlib.Path(tmp)
    (tmp / "pkg").mkdir()
    (tmp / "pkg" / "__init__.py").write_text("", encoding="utf-8", newline="\n")
    names = ["pkg/__init__.py"]
    for name, text in files.items():
        (tmp / "pkg" / name).write_text(text, encoding="utf-8", newline="\n")
        names.append("pkg/" + name)
    _git("init", "-q", cwd=tmp)
    _git("add", *names, cwd=tmp)
    return tmp


# ---------------------------------------------------------------- mutations

# The exact D2 regression, on the STORE side (extract.py). The supplement is
# untouched, so this is the one thing the implementer's own join mutants never
# tried: they only ever mutated supplement.py. If the two sides were really one
# code path, this mutation would move BOTH and entity-symbol-join would survive.
D2_RESTORE = (
    ("        base = self.here()\n"
     "        return base + name if base.endswith(\":\") else base + \".\" + name\n",
     "        base = self.here()\n"
     "        if self.clsstack:\n"
     "            return \"%s:%s.%s\" % (self.mod, self.clsstack[-1], name)\n"
     "        return base + name if base.endswith(\":\") else base + \".\" + name\n"),
)

# The leaf-comparison the check used to do, restored. Combined with D2_RESTORE
# this proves the STRENGTHENING bought something: the old rule survives the
# regression, the new one kills it.
LEAF_COMPARE = (
    ("        if key != symbol:\n",
     "        if key.rsplit(\".\", 1)[-1] != symbol.rsplit(\".\", 1)[-1]:\n"),
)

# Supplement side, but a chain TRUNCATION rather than the implementer's rename:
# drop the enclosing prefix entirely.
SUPP_FLATTEN = (
    ('                    qual = f"{prefix}.{child.name}" if prefix else child.name\n',
     '                    qual = child.name\n'),
)

# (b): inflate the counted module total without naming another module. Hits the
# "exactly 1 unnamed" arm on pages WITH own-module sites and the "exactly 0
# unnamed" arm on pages WITHOUT them, with two distinct messages.
MODULE_COUNT_INFLATE = (
    ('        s = f"referenced by: {n} sites in {len(callers)} modules (" + ", ".join(ext) + ")"\n',
     '        s = f"referenced by: {n} sites in {len(callers) + 1} modules (" + ", ".join(ext) + ")"\n'),
)

# (b) again, the other direction: name one fewer module while counting the same.
DROP_A_NAMED_MODULE = (
    ('        s = f"referenced by: {n} sites in {len(callers)} modules (" + ", ".join(ext) + ")"\n',
     '        s = f"referenced by: {n} sites in {len(callers)} modules (" + ", ".join(ext[1:]) + ")"\n'),
)

# (c): make the disambiguating tag seed-dependent, the trap the design note
# names. If deterministic-rebuild cannot see this, that check has a hole.
HASH_BUILTIN = (
    ('    return hashlib.sha1(name.encode("utf-8")).hexdigest()[:8]\n',
     '    return "%08x" % (hash(name) & 0xFFFFFFFF)\n'),
)


# A page that has BOTH own-module sites and external ones, so its line takes
# the `... modules (...) + N in this module` form -- the ONLY shape that can
# exercise the "exactly one unnamed" arm.
BOTH = '''"""A target called from its own module and from another."""


def target():
    """The symbol every page below points at."""
    return 1


def near_one():
    """Own-module caller #1."""
    return target()


def near_two():
    """Own-module caller #2."""
    return target()
'''

FAR = '''"""A second module that calls the target three times."""
from pkg import both


def far_one():
    """External caller #1."""
    return both.target()


def far_two():
    """External caller #2."""
    return both.target(), both.target()
'''

# gap becomes 2 while own > 0 -- the "exactly one unnamed" arm, high side.
OWN_GAP_TWO = MODULE_COUNT_INFLATE

# gap becomes 0 while own > 0 -- the same arm, low side, and NOT the g1
# OWN_MODULE_NAMED mutation: no module is named that was not named before.
OWN_GAP_ZERO = (
    ('        s = f"referenced by: {n} sites in {len(callers)} modules (" + ", ".join(ext) + ")"\n',
     '        s = f"referenced by: {n} sites in {len(callers) - 1} modules (" + ", ".join(ext) + ")"\n'),
)


def _report(tag, proc):
    print(f"--- {tag}: exit {proc.returncode}")
    print(proc.stdout.strip()[-3000:])
    if proc.returncode != 0 and proc.stderr.strip():
        print("STDERR:", proc.stderr.strip()[-1500:])


def drive(name, edits, files, build_expect=0):
    with tempfile.TemporaryDirectory() as repo, tempfile.TemporaryDirectory() as host:
        make_repo(repo, files)
        h = mutate(host, edits)
        b = run_map(h, "build", "--root", repo)
        if b.returncode != build_expect:
            print(f"BUILD exit {b.returncode} (expected {build_expect})")
            print(b.stdout[-2000:], b.stderr[-2000:])
        c = run_map(h, "check", "--root", repo)
        _report(name, c)
        return c


ATTACKS = {}


def attack(fn):
    ATTACKS[fn.__name__] = fn
    return fn


@attack
def a1_store_side_d2_regression():
    """Break the STORE derivation only. entity-symbol-join must go red."""
    drive("a1 extract.py D2 restored (supplement untouched)",
          {"extract.py": D2_RESTORE},
          {"nested.py": NESTED, "user.py": USER})


@attack
def a2_old_leaf_rule_survives_it():
    """Same regression, with the OLD leaf comparison restored in checks.py.
    If this passes, the strengthening is what caught a1 -- not luck."""
    drive("a2 D2 restored + OLD leaf comparison",
          {"extract.py": D2_RESTORE, "checks.py": LEAF_COMPARE},
          {"nested.py": NESTED, "user.py": USER})


@attack
def a3_supplement_flatten():
    """Break the SUPPLEMENT derivation with a truncation, not a rename."""
    drive("a3 supplement.py chain flattened",
          {"supplement.py": SUPP_FLATTEN},
          {"nested.py": NESTED, "user.py": USER})


@attack
def a4_clean_nested_baseline():
    """No mutation: the same fixture must pass, or a1/a3 prove nothing."""
    drive("a4 clean baseline on the nested fixture", {},
          {"nested.py": NESTED, "user.py": USER})


@attack
def a5_module_count_inflate():
    drive("a5 counted module total +1",
          {"render.py": MODULE_COUNT_INFLATE},
          {"nested.py": NESTED, "user.py": USER})


@attack
def a6_drop_a_named_module():
    drive("a6 one named module dropped",
          {"render.py": DROP_A_NAMED_MODULE},
          {"nested.py": NESTED, "user.py": USER})


@attack
def a7_case_family_clean():
    """My own case-only family, different shape. Must pass with no mutation."""
    drive("a7 case-only family (Box.Item/Box.item + Thing/thing/THING)", {},
          {"casey.py": CASEY, "nested.py": NESTED, "user.py": USER})


@attack
def a8_seed_dependent_tag():
    """hash() instead of hashlib. deterministic-rebuild must catch it."""
    drive("a8 case tag from builtin hash()",
          {"render.py": HASH_BUILTIN},
          {"casey.py": CASEY, "nested.py": NESTED, "user.py": USER})


@attack
def a9_case_family_pages():
    """Inspect the tree my case-only family produces, unmutated."""
    with tempfile.TemporaryDirectory() as repo, tempfile.TemporaryDirectory() as host:
        make_repo(repo, {"casey.py": CASEY})
        h = mutate(host, {})
        print(run_map(h, "build", "--root", repo).returncode)
        out = pathlib.Path(repo) / "map"
        seen = {}
        for p in sorted(out.rglob("*.md")):
            rel = p.relative_to(out).as_posix()
            first = p.read_text(encoding="utf-8").splitlines()[0]
            print(f"{rel:<40} {first}")
            folded = rel.lower()
            if folded in seen:
                print("  !! FOLD COLLISION with", seen[folded])
            seen[folded] = rel
        # every link resolves
        import re as _re
        bad = []
        for p in sorted(out.rglob("*.md")):
            for target in _re.findall(r"\]\(([^)]+)\)", p.read_text(encoding="utf-8")):
                if not (p.parent / target).exists():
                    bad.append((p.relative_to(out).as_posix(), target))
        print("broken links:", bad)
        c = run_map(h, "check", "--root", repo)
        _report("a9 check on the case-only family", c)


@attack
def b0_both_clean():
    drive("b0 clean: a page with own AND external sites", {},
          {"both.py": BOTH, "far.py": FAR})


@attack
def b1_own_gap_two():
    drive("b1 own>0, gap forced to 2",
          {"render.py": OWN_GAP_TWO}, {"both.py": BOTH, "far.py": FAR})


@attack
def b2_own_gap_zero():
    drive("b2 own>0, gap forced to 0",
          {"render.py": OWN_GAP_ZERO}, {"both.py": BOTH, "far.py": FAR})


@attack
def b3_show_the_line():
    with tempfile.TemporaryDirectory() as repo, tempfile.TemporaryDirectory() as host:
        make_repo(repo, {"both.py": BOTH, "far.py": FAR})
        h = mutate(host, {})
        run_map(h, "build", "--root", repo)
        for p in sorted((pathlib.Path(repo) / "map").rglob("*.md")):
            for ln in p.read_text(encoding="utf-8").splitlines():
                if ln.startswith("referenced by: "):
                    print(f"{p.relative_to(pathlib.Path(repo) / 'map').as_posix():<28} {ln}")


COLLIDING = '''"""A module holding an entity named INDEX."""


class INDEX:
    """Lands on the module's own index page: two writes, one file."""

    def use(self):
        """Body."""
        return 1


def helper():
    """A second entity so the accounting has something to count."""
    return INDEX
'''


@attack
def c1_index_collision_still_collides():
    """g1's ONLY cross-platform falsifier for page-accounting. It must STILL
    lose a page -- if g2 reserved the INDEX stem, that check cannot fail."""
    drive("c1 INDEX collision", {}, {"thing.py": COLLIDING})


# g1's rule, restored verbatim: "at most ONE counted module may go unnamed".
OLD_REFS_RULE = (
    ('            elif stated.own and gap != 1:\n'
     '                failures.append(f"{where}: attributes {stated.own} sites to its own "\n'
     '                                f"module, so exactly one counted module -- its own -- "\n'
     '                                f"must go unnamed, but {gap} of {stated.modules} are")\n'
     '            elif not stated.own and gap != 0:\n'
     '                failures.append(f"{where}: counts {stated.modules} modules and names "\n'
     '                                f"{len(named)}; a line that attributes no sites to its "\n'
     '                                f"own module must name every module it counts")\n',
     '            elif gap > 1:\n'
     '                failures.append(f"{where}: counts {stated.modules} modules and names "\n'
     '                                f"{len(named)}; at most one -- the page\'s own -- may go "\n'
     '                                f"unnamed")\n'),
)


@attack
def b4_old_refs_rule_survives_a6():
    """Same mutant as a6, with g1's OLD 'at most one unnamed' rule restored.
    If refs-line-self-consistent goes GREEN here, the g2 rule is strictly
    stronger, not merely reworded."""
    drive("b4 a6's mutant + g1's OLD at-most-one rule",
          {"render.py": DROP_A_NAMED_MODULE, "checks.py": OLD_REFS_RULE},
          {"nested.py": NESTED, "user.py": USER})


@attack
def b5_old_refs_rule_still_kills_gap_two():
    """The old rule's own failure mode must still be reachable under the NEW
    rule: gap > 1. b1 already showed it red with own>0; this shows the old rule
    caught the same thing, i.e. nothing was weakened."""
    drive("b5 gap=2 under the OLD rule",
          {"render.py": OWN_GAP_TWO, "checks.py": OLD_REFS_RULE},
          {"both.py": BOTH, "far.py": FAR})


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    for nm, fn in ATTACKS.items():
        if which in ("all", nm):
            print("=" * 70)
            print(nm)
            fn()
