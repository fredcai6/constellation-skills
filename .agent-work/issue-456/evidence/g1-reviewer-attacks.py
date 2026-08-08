"""REVIEWER attack harness for gate g1 -- mutations the implementer did NOT design for.

Not part of the suite. Every attack runs against a COPY of scripts/code_map and a
throwaway fixture repo; the shipped tree is never edited.

Reuses tests.test_code_map's `mutated_package` ONLY for its loud-failure property
(an anchor that does not occur exactly once raises HarnessError), so a mutation
that silently failed to apply cannot read as a surviving check.
"""
import pathlib
import shutil
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.code_map import checks  # noqa: E402
from tests.test_code_map import (  # noqa: E402
    mutated_package, run_code_map, _make_mixed_repo, _make_entity_repo,
    _make_cross_module_repo,
)

CODE_MAP = ROOT / "scripts" / "code_map"


def make_repo(make):
    tmp = tempfile.mkdtemp(prefix="g1atk-r-")
    make(pathlib.Path(tmp))
    return pathlib.Path(tmp)


def make_host(module=None, subs=()):
    tmp = tempfile.mkdtemp(prefix="g1atk-h-")
    if module is None:
        dest = pathlib.Path(tmp) / "scripts" / "code_map"
        shutil.copytree(CODE_MAP, dest, ignore=shutil.ignore_patterns("__pycache__"))
        return pathlib.Path(tmp)
    return mutated_package(tmp, module, subs)


def failed(stdout):
    return [ln.split(":")[0].replace("FAIL ", "")
            for ln in stdout.splitlines() if ln.startswith("FAIL ")]


def run(label, fixture, module=None, subs=(), damage=None, check_host_module=None,
        check_host_subs=()):
    """Build with `host`, optionally damage the tree, then run `check`.

    `check_host_*` lets the CHECK run from a differently-mutated package than the
    one that built -- that is how a renderer-side vacuity is isolated."""
    repo = make_repo(fixture)
    host = make_host(module, subs)
    b = run_code_map(host, "build", "--root", str(repo))
    if b.returncode != 0:
        print(f"{label:<50} BUILD FAILED rc={b.returncode} {b.stderr[-500:]}")
        return None, repo
    if damage is not None:
        damage(repo)
    chost = host
    if check_host_module is not None:
        chost = make_host(check_host_module, check_host_subs)
    p = run_code_map(chost, "check", "--root", str(repo))
    f = failed(p.stdout)
    print(f"{label:<50} exit={p.returncode} "
          f"{'CAUGHT  ' if p.returncode else 'SURVIVED'} by={f or ['NOTHING']}")
    return p, repo


# ---------------------------------------------------------------- mutations

#: Respell the inbound line so `checks.refs_lines` no longer recognises it. The
#: page still carries the numbers; the check's prefix no longer matches, so the
#: page-local check has nothing to iterate.
REFS_LINE_SUPPRESSED = (
    ('        return ["referenced by: none found", ""]\n',
     '        return ["refs: none found", ""]\n'),
    ('        s = f"referenced by: {n} sites in {len(callers)} modules (" + ", ".join(ext) + ")"\n',
     '        s = f"refs: {n} sites in {len(callers)} modules (" + ", ".join(ext) + ")"\n'),
    ('        s = f"referenced by: {n} sites, this module only"\n',
     '        s = f"refs: {n} sites, this module only"\n'),
)
EXTRACT_LEAF_MANGLED = (
    ('            sym = "%s:%s" % (self.mod, node.name)\n',
     '            sym = "%s:%s_x" % (self.mod, node.name)\n'),
)
INBOUND_DOUBLE_COUNTED = (
    ("                inbound[o][intern(modof(s))] += 1\n",
     "                inbound[o][intern(modof(s))] += 2\n"),
)
CALLER_NAME_DROPPED = (
    ("    ext = sorted(m for m in callers if m != mod)\n",
     "    ext = sorted(m for m in callers if m != mod)[1:]\n"),
)
HASH_STAMPED_ARTIFACT = (
    ('    (out / "ids.jsonl").write_text("", encoding="utf-8", newline="\\n")\n',
     '    (out / "ids.jsonl").write_text(str(hash("x")), encoding="utf-8", newline="\\n")\n'),
)


# ------------------------------------------------------------------ damages

def whitespace_only_page(repo):
    (repo / "map" / "pkg.widget" / "helper.md").write_text(
        "   \n\t\n  \n", encoding="utf-8", newline="\n")


def bom_only_page(repo):
    (repo / "map" / "pkg.widget" / "helper.md").write_text(
        "\ufeff", encoding="utf-8", newline="\n")


def header_only_page(repo):
    (repo / "map" / "pkg.widget" / "helper.md").write_text(
        "# pkg.widget:helper\n", encoding="utf-8", newline="\n")


def duplicate_page(repo):
    d = repo / "map" / "pkg.widget"
    (d / "helper_copy.md").write_text(
        (d / "helper.md").read_text(encoding="utf-8"), encoding="utf-8", newline="\n")


def overcount_modules(repo):
    p = repo / "map" / "pkg.callee" / "target.md"
    t = p.read_text(encoding="utf-8")
    old = [ln for ln in t.splitlines() if ln.startswith("referenced by: ")]
    assert old, "HARNESS: no refs line to damage"
    t = t.replace(old[0], "referenced by: 5 sites in 3 modules (pkg.far)")
    p.write_text(t, encoding="utf-8", newline="\n")


def named_but_not_counted(repo):
    p = repo / "map" / "pkg.callee" / "target.md"
    t = p.read_text(encoding="utf-8")
    old = [ln for ln in t.splitlines() if ln.startswith("referenced by: ")][0]
    t = t.replace(old, "referenced by: 1 sites in 0 modules (pkg.far, pkg.other)")
    p.write_text(t, encoding="utf-8", newline="\n")


ATTACKS = {
    # --- no-empty-pages -------------------------------------------------
    "A1 no-empty: whitespace-only page":
        dict(fixture=_make_mixed_repo, damage=whitespace_only_page),
    "A2 no-empty: BOM-only page":
        dict(fixture=_make_mixed_repo, damage=bom_only_page),
    "A3 no-empty: header-only stub page":
        dict(fixture=_make_mixed_repo, damage=header_only_page),
    # --- page-accounting ------------------------------------------------
    "A4 accounting: duplicate page, same title":
        dict(fixture=_make_mixed_repo, damage=duplicate_page),
    # --- refs-line-self-consistent --------------------------------------
    "A5 refs-line: renderer emits NO refs line":
        dict(fixture=_make_cross_module_repo, module="render.py",
             subs=REFS_LINE_SUPPRESSED),
    "A6 refs-line: counts 3 modules, names 1":
        dict(fixture=_make_cross_module_repo, damage=overcount_modules),
    "A7 refs-line: names 2 modules, counts 0":
        dict(fixture=_make_cross_module_repo, damage=named_but_not_counted),
    # --- entity-symbol-join ---------------------------------------------
    "A8 join: EXTRACT pass mangles the leaf name":
        dict(fixture=_make_mixed_repo, module="extract.py", subs=EXTRACT_LEAF_MANGLED),
    # --- inbound-attribution --------------------------------------------
    "A9 inbound: every edge counted twice":
        dict(fixture=_make_cross_module_repo, module="render.py",
             subs=INBOUND_DOUBLE_COUNTED),
    "A10 inbound: one caller name dropped, count kept":
        dict(fixture=_make_cross_module_repo, module="render.py",
             subs=CALLER_NAME_DROPPED),
    # --- deterministic-rebuild ------------------------------------------
    "A11 determinism: artifact stamped with hash('x')":
        dict(fixture=_make_entity_repo, module="render.py", subs=HASH_STAMPED_ARTIFACT),
}


def control():
    p, _ = run("CONTROL unmutated package, undamaged map", _make_mixed_repo)
    return p


def isolate_refs_vacuity():
    """Is `refs_line_self_consistent` VACUOUS when no page carries a refs line?"""
    repo = make_repo(_make_cross_module_repo)
    host = make_host("render.py", REFS_LINE_SUPPRESSED)
    assert run_code_map(host, "build", "--root", str(repo)).returncode == 0
    m = checks.MapUnderCheck(repo, repo / ".code-map", repo / "map")
    lines = [ln for p in m.pages for ln in checks.refs_lines(m.text(p))]
    print(f"  refs lines in the whole tree: {len(lines)}")
    print(f"  refs_line_self_consistent(m) -> {checks.refs_line_self_consistent(m)}")
    print(f"  inbound_attribution(m)       -> {len(checks.inbound_attribution(m))} failures")


def isolate_treediff_vacuity():
    d = pathlib.Path(tempfile.mkdtemp(prefix="g1atk-t-"))
    (d / "a").mkdir()
    (d / "b").mkdir()
    print(f"  tree_diff(empty, empty) -> {checks.tree_diff(d / 'a', d / 'b')}")


if __name__ == "__main__":
    only = sys.argv[1:] or None
    print("=== reviewer undesigned attacks: gate g1 ===")
    if only is None or "control" in only:
        control()
    for label, kw in ATTACKS.items():
        if only and not any(o in label for o in only):
            continue
        run(label, **kw)
    if only is None or "vacuity" in (only or []):
        print("\n--- vacuity isolations ---")
        isolate_refs_vacuity()
        isolate_treediff_vacuity()
