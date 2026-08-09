"""g5 REVIEWER: prove the two independently hand-written `is_test_module`
copies (render.py's, checks.py's) are a REAL independent pair, not decoration
(handoff "Also verify" item 2). The handoff already confirmed checks.py has no
`import` from render.py by grep -- that only proves textual independence.
Independence is only worth something if a DIVERGENCE is CATCHABLE: this script
mutates ONLY the checks.py copy (widening its rule so it disagrees with
render.py's for one module), builds a small real fixture through the mutated
package, and confirms `python -m scripts.code_map check` goes RED specifically
on `inbound-attribution` -- the check that reads checks.is_test_module, not
render.py's.

If nothing goes red, the second copy is decoration -- a tc29/tc38 finding.
"""
import pathlib
import sys
import tempfile
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

import test_code_map as T  # noqa: E402

# Widen checks.py's copy ONLY: classify a module named "helpers" (which is
# NOT a test module by the real rule) as a test module too, by adding it to
# the "last segment" check. This diverges checks.py from render.py for any
# module whose last dotted segment is exactly "helpers".
ANCHOR = (
    "def is_test_module(mod):\n"
    "    \"\"\"Second, independently hand-written reading of the SAME pytest-derived\n"
)
# Simpler, safer anchor: the return line unique to checks.py's copy.
CHECKS_RETURN_ANCHOR = (
    '    if last.startswith("test_") or last.endswith("_test"):\n'
    '        return True\n'
    '    return "tests" in parts\n'
)
DIVERGED = (
    '    if last.startswith("test_") or last.endswith("_test"):\n'
    '        return True\n'
    '    if last == "helpers":\n'
    '        return True\n'
    '    return "tests" in parts\n'
)


def _git(*args, cwd):
    return subprocess.run(("git",) + args, cwd=str(cwd), check=True,
                          capture_output=True, text=True)


_CALLEE = '''"""Called from a module named helpers -- classified PRODUCTION by the
real rule (does not match test_*/*_test naming, no `tests` package segment)."""


def target():
    """Called once from pkg.helpers."""
    return 1
'''

_HELPERS = '''"""A production-looking caller module named "helpers"."""
from pkg.callee import target


def use_it():
    return target()
'''


def make_repo(tmp):
    (tmp / "pkg").mkdir()
    (tmp / "pkg" / "__init__.py").write_text("", encoding="utf-8", newline="\n")
    (tmp / "pkg" / "callee.py").write_text(_CALLEE, encoding="utf-8", newline="\n")
    (tmp / "pkg" / "helpers.py").write_text(_HELPERS, encoding="utf-8", newline="\n")
    _git("init", "-q", cwd=tmp)
    _git("add", "pkg/__init__.py", "pkg/callee.py", "pkg/helpers.py", cwd=tmp)


def main():
    # First confirm the anchor occurs in checks.py's own copy, distinctly from
    # render.py's (both files contain the identical 3-line body, but
    # mutated_package's harness checks the COUNT within the ONE module file
    # named, so mutating "checks.py" only touches checks.py's copy).
    checks_src = (T.CODE_MAP / "checks.py").read_text(encoding="utf-8")
    render_src = (T.CODE_MAP / "render.py").read_text(encoding="utf-8")
    print("anchor occurrences in checks.py:", checks_src.count(CHECKS_RETURN_ANCHOR))
    print("anchor occurrences in render.py:", render_src.count(CHECKS_RETURN_ANCHOR))
    assert checks_src.count(CHECKS_RETURN_ANCHOR) == 1
    assert render_src.count(CHECKS_RETURN_ANCHOR) == 1

    tmp = tempfile.TemporaryDirectory()
    repo = pathlib.Path(tmp.name) / "repo"
    repo.mkdir()
    make_repo(repo)

    work = pathlib.Path(tmp.name) / "work"
    work.mkdir()
    host = T.mutated_package(str(work), "checks.py", ((CHECKS_RETURN_ANCHOR, DIVERGED),))

    # Confirm render.py's copy in the SAME mutated host is untouched (proves
    # the mutation landed ONLY in checks.py, not both).
    render_in_host = (host / "scripts" / "code_map" / "render.py").read_text(encoding="utf-8")
    assert render_in_host.count(CHECKS_RETURN_ANCHOR) == 1, "render.py copy must be untouched"
    checks_in_host = (host / "scripts" / "code_map" / "checks.py").read_text(encoding="utf-8")
    assert checks_in_host.count(DIVERGED) == 1, "checks.py copy must carry the divergence"

    artifacts = work / ".code-map"
    out = work / "map"
    p1 = T.run_code_map(host, "build", "--root", str(repo), "--artifacts", str(artifacts), "--out", str(out))
    print("--- build ---")
    print(p1.stdout)
    print(p1.stderr)
    assert p1.returncode == 0, "build itself should still succeed"

    p2 = T.run_code_map(host, "check", "--artifacts", str(artifacts), "--out", str(out))
    print("--- check (against the diverged checks.py) ---")
    print(p2.stdout)
    print(p2.stderr)
    print("check exit code:", p2.returncode)

    caught = (p2.returncode != 0) and ("inbound-attribution" in p2.stdout) and ("FAIL" in p2.stdout)
    print()
    print("DIVERGENCE CAUGHT:", "YES" if caught else "NO -- the second copy is decoration")
    tmp.cleanup()
    return 0 if caught else 1


if __name__ == "__main__":
    sys.exit(main())
