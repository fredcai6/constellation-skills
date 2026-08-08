"""g5 REVIEWER: confirm the TEST bucket's caller list is order-stable too, not
just the production one (handoff item 4, tc32's sibling risk). `_bucket_line`
is one shared function called twice (once per bucket) with the SAME `sorted`
call, so the mechanism should be identical -- this fixture makes the TEST
bucket the one with >=2 external callers (pkg.callee is called from two
`tests`-package modules) and reruns the permuted-visit-order attack against
it, both canonically (must be empty) and under the reversed-insertion
mutation (must be nonempty, same as the production-bucket attack)."""
import pathlib
import sys
import tempfile
import contextlib
import io
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from scripts.code_map import checks, cli, extract  # noqa: E402
import test_code_map as T  # noqa: E402

ANCHOR = "    ext = sorted(m for m in counter if m != mod)\n"
MUTATION = ((ANCHOR, "    ext = list(reversed([m for m in counter if m != mod]))\n"),)

_TARGET = '''"""Called from two test modules."""


def target():
    """Called from two test-package modules."""
    return 1
'''

_TESTS_A = '''"""Calls target once."""
from pkg.callee import target


def test_a():
    return target()
'''

_TESTS_B = '''"""Calls target once."""
from pkg.callee import target


def test_b():
    return target()
'''


def _git(*args, cwd):
    return subprocess.run(("git",) + args, cwd=str(cwd), check=True,
                          capture_output=True, text=True)


def make_repo(tmp):
    (tmp / "pkg").mkdir()
    (tmp / "pkg" / "__init__.py").write_text("", encoding="utf-8", newline="\n")
    (tmp / "pkg" / "callee.py").write_text(_TARGET, encoding="utf-8", newline="\n")
    (tmp / "tests").mkdir()
    (tmp / "tests" / "__init__.py").write_text("", encoding="utf-8", newline="\n")
    (tmp / "tests" / "test_alpha.py").write_text(_TESTS_A, encoding="utf-8", newline="\n")
    (tmp / "tests" / "test_beta.py").write_text(_TESTS_B, encoding="utf-8", newline="\n")
    _git("init", "-q", cwd=tmp)
    _git("add", "pkg/__init__.py", "pkg/callee.py", "tests/__init__.py",
         "tests/test_alpha.py", "tests/test_beta.py", cwd=tmp)


def main():
    tmp = tempfile.TemporaryDirectory()
    repo = pathlib.Path(tmp.name) / "repo"
    repo.mkdir()
    make_repo(repo)

    artifacts = repo / ".code-map"
    with contextlib.redirect_stdout(io.StringIO()):
        rc = cli.main(["extract", "--root", str(repo), "--artifacts", str(artifacts)])
    assert rc == 0
    text = (artifacts / extract.STATEMENTS_NAME).read_text(encoding="utf-8")
    groups = T._group_statement_lines_by_file(text)
    assert len(groups) > 1, f"need >1 file, got {len(groups)}"
    permuted_text = T._permuted_statements(text)

    # sanity: confirm the target page's TEST bucket line names 2 modules
    out = repo / "map-sanity"
    with contextlib.redirect_stdout(io.StringIO()):
        rc = cli.main(["render", "--root", str(repo), "--artifacts", str(artifacts), "--out", str(out)])
    assert rc == 0
    page = (out / "pkg.callee" / "target.md").read_text(encoding="utf-8")
    lines = checks.refs_lines(page)
    test_line = next(l for l in lines if l.startswith(checks.REFS_TEST_PREFIX))
    stated = checks.parse_refs(test_line)
    assert stated.modules == 2, f"fixture precondition failed: test bucket names {stated.modules} modules, need 2 -- {test_line!r}"
    prod_line = next(l for l in lines if l.startswith(checks.REFS_PROD_PREFIX))
    print("sanity: prod line =", repr(prod_line))
    print("sanity: test line =", repr(test_line))

    results = {}
    for name, subs in (("canonical (unmutated)", None), ("reversed-insertion mutation", MUTATION)):
        work = pathlib.Path(tmp.name) / name.replace(" ", "_").replace("(", "").replace(")", "")
        work.mkdir()
        if subs:
            host = T.mutated_package(str(work), "render.py", subs)
        else:
            import shutil
            dest = work / "scripts" / "code_map"
            shutil.copytree(T.CODE_MAP, dest, ignore=shutil.ignore_patterns("__pycache__"))
            host = work

        canon_art = work / "art-canon"
        canon_art.mkdir()
        (canon_art / extract.STATEMENTS_NAME).write_text(text, encoding="utf-8", newline="\n")
        canon_out = work / "map-canon"
        p1 = T.run_code_map(host, "render", "--root", str(repo),
                             "--artifacts", str(canon_art), "--out", str(canon_out))
        assert p1.returncode == 0, p1.stdout + p1.stderr

        perm_art = work / "art-perm"
        perm_art.mkdir()
        (perm_art / extract.STATEMENTS_NAME).write_text(permuted_text, encoding="utf-8", newline="\n")
        perm_out = work / "map-perm"
        p2 = T.run_code_map(host, "render", "--root", str(repo),
                             "--artifacts", str(perm_art), "--out", str(perm_out))
        assert p2.returncode == 0, p2.stdout + p2.stderr

        diff = checks.tree_diff(canon_out, perm_out)
        results[name] = diff
        print(f"{name}: diff={'EMPTY' if not diff else diff}")

    ok = (results["canonical (unmutated)"] == [] and results["reversed-insertion mutation"] != [])
    print("TEST BUCKET ORDER STABILITY:", "CONFIRMED" if ok else "FAILED TO CONFIRM")
    tmp.cleanup()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
