# evals.euler-1-multiples.checks.tests_green
evals/euler-1-multiples/checks/tests_green.py, 76 lines, 3 holes

PROCESS check (gating): tests were WRITTEN and PASS in the workspace.

This check BITES STRICTLY. It finds test files in the agent's ``workspace/`` --
EXCLUDING the corpus copy under ``.claude/`` -- and requires that at least one exist
and that pytest run GREEN over exactly those files (never the corpus). There is NO
completion-sentinel fallback (issue #115 tc1): a run must actually write a passing
test to pass, not merely stamp the sentinel. So the agent-free ``--dry-run`` (which
now synthesizes a real green ``test_solution.py``) PASSes, while ``--dry-run-fail``
(no test, no solution) FAILs.

pytest is invoked with the discovered test paths ONLY, so a live run cannot
accidentally collect the bundled corpus tests under ``.claude/``.

Usage: ``python tests_green.py <run-dir>``  ->  exit 0 pass / non-zero fail.

imports stdlib: __future__.annotations, pathlib.Path, subprocess, sys
imported by: none found

```python
EXCLUDED_PARTS = {'.claude', '.git', '.agent-work'}
```

- [find_tests](find_tests.md) function: HOLE: no docstring
- [run_pytest](run_pytest.md) function: HOLE: no docstring
- [main](main.md) function: HOLE: no docstring
