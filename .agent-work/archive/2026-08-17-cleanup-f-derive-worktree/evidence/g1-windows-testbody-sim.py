"""Run the ACTUAL target test body under a case-folding path module.

`g1-windows-sim.py` reconstructs the six comparisons and proves the two candidate
expectations apart. This harness is the stronger form: it executes
`tests/test_spine_rail.py::test_worktree_from_spine_walks_to_the_nearest_agent_
work_ancestor` itself -- the real assertions, the real fixture paths -- with the
one Windows property that breaks it simulated, namely a `normcase` that FOLDS.

It runs the test body twice:

  PRE-FIX  : the three comparison lines textually reverted to the platform-
             inherited `== str(worktree)` / `== str(sandbox)` form.
  POST-FIX : the file exactly as it stands in the tree.

Under a folding `normcase` the PRE-FIX body must FAIL (that is B1 on Windows)
and the POST-FIX body must PASS. Under the host's own non-folding `normcase`
both pass -- which is precisely why the blocker is invisible here.

The pre-fix variant is produced by reversing the fix in the source text and
ASSERTING the substitution applied, so a silently-matched-nothing edit cannot
leave a green run that reads like a passing guard.

Usage: py .agent-work/<work-id>/evidence/g1-windows-testbody-sim.py
"""

import importlib.util
import os
import posixpath
import sys
import types
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_TEST_FILE = _REPO_ROOT / "tests" / "test_spine_rail.py"
_TEST_NAME = "test_worktree_from_spine_walks_to_the_nearest_agent_work_ancestor"

# The fix, as three exact substitutions. Reversing them rebuilds the pre-fix body.
_FIX = [
    ("assert sr._worktree_from_spine(str(spine)) == _derived_form(worktree)",
     "assert sr._worktree_from_spine(str(spine)) == str(worktree)"),
    ("assert sr._worktree_from_spine(str(path)) == _derived_form(worktree), path",
     "assert sr._worktree_from_spine(str(path)) == str(worktree), path"),
    ("assert sr._worktree_from_spine(str(nested)) == _derived_form(sandbox)",
     "assert sr._worktree_from_spine(str(nested)) == str(sandbox)"),
]


class _FoldingPath(types.ModuleType):
    """`posixpath` with a `normcase` that folds case, as Windows' does.

    Only `normcase` changes. Separator handling stays POSIX so the on-host
    `tmp_path` strings remain meaningful -- the fold alone is what B1 turns on.
    """

    def __init__(self):
        super().__init__("folding_posixpath")

    def __getattr__(self, name):
        return getattr(posixpath, name)

    @staticmethod
    def normcase(s):
        return s.lower()


class _FakeOS:
    def __init__(self, path_module):
        self.path = path_module

    def __getattr__(self, name):
        return getattr(os, name)


def _load_test_module(tag, source):
    """Exec a (possibly modified) copy of the test file as its own module."""
    name = f"test_spine_rail_{tag}"
    module = types.ModuleType(name)
    module.__file__ = str(_TEST_FILE)
    sys.modules[name] = module
    exec(compile(source, str(_TEST_FILE), "exec"), module.__dict__)
    return module


def _revert_fix(source):
    """Rebuild the pre-fix body, asserting every substitution actually applied."""
    for fixed, original in _FIX:
        if source.count(fixed) != 1:
            raise SystemExit(
                f"FAIL: expected exactly one occurrence of {fixed!r} in "
                f"{_TEST_FILE}; found {source.count(fixed)}. The harness is "
                f"stale against the file it claims to test.")
        source = source.replace(fixed, original)
    return source


def _run(tag, source, path_module, tmp_path):
    module = _load_test_module(tag, source)
    module.os = _FakeOS(path_module)          # the test's own `_derived_form`
    module.sr.os = _FakeOS(path_module)       # the hook's derivation
    try:
        getattr(module, _TEST_NAME)(tmp_path)
        return None
    except AssertionError as exc:
        first = str(exc).strip().splitlines()[0] if str(exc).strip() else "assert failed"
        return first


def main():
    source = _TEST_FILE.read_text(encoding="utf-8")
    variants = {"POST-FIX (tree)": source, "PRE-FIX (reverted)": _revert_fix(source)}
    platforms = {
        "folding normcase (Windows-like)": (_FoldingPath(), True),
        "host normcase (POSIX, identity)": (posixpath, False),
    }

    # A mixed-case tmp_path in pytest's own shape: the fold has to have something
    # to fold, or the simulation would pass for the wrong reason.
    tmp_path = Path("/tmp/pytest-of-Tommy/pytest-1/test_Worktree0")

    failures = []
    for platform_name, (path_module, folds) in platforms.items():
        print(f"--- {platform_name} " + "-" * max(0, 44 - len(platform_name)))
        for index, (variant_name, variant_source) in enumerate(variants.items()):
            error = _run(f"{index}_{len(failures)}_{abs(hash(platform_name)) % 997}",
                         variant_source, path_module, tmp_path)
            verdict = "PASS" if error is None else "FAIL"
            print(f"    {variant_name:22s} -> {verdict}"
                  + (f"  ({error})" if error else ""))

            # PRE-FIX must fail exactly where the fold bites, and nowhere else.
            expected_fail = folds and variant_name.startswith("PRE-FIX")
            if (error is not None) != expected_fail:
                failures.append(
                    f"{platform_name} / {variant_name}: got {verdict}, expected "
                    f"{'FAIL' if expected_fail else 'PASS'}")

    print()
    if failures:
        for line in failures:
            print(f"FAIL: {line}")
        return 1
    print("OK: the real test body FAILS pre-fix under a folding normcase and "
          "PASSES post-fix, while both pass under the host's identity normcase.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
