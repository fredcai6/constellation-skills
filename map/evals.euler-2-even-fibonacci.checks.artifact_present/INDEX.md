# evals.euler-2-even-fibonacci.checks.artifact_present
evals/euler-2-even-fibonacci/checks/artifact_present.py, 62 lines, 3 holes

PROCESS check (gating): the workflow produced a non-empty solution deliverable.

This check BITES STRICTLY. It walks the agent's ``workspace/`` -- EXCLUDING the
corpus copy under ``.claude/`` and the engine's ``.agent-work/`` -- for a non-empty
Python solution file, and FAILs (non-zero) if none exists. There is NO completion-
sentinel fallback (issue #115 tc1): the sentinel is written as the workflow's LAST
step and could be present with no real solution behind it, so accepting it as a
stand-in was the "sentinel written without a real solution" hole. A run must now
produce a real ``solution.py`` to pass, not merely stamp the sentinel. The runner's
``--dry-run`` synthesizes a real ``solution.py`` (so this bites on it); ``--dry-run
-fail`` (only a ``BROKEN.txt`` marker) FAILs.

Usage: ``python artifact_present.py <run-dir>``  ->  exit 0 pass / non-zero fail.

imports stdlib: __future__.annotations, pathlib.Path, sys
imported by: none found

```python
EXCLUDED_PARTS = {'.claude', '.git', '.agent-work'}
```

- [_is_test_file](_is_test_file.md) function: HOLE: no docstring
- [find_solution](find_solution.md) function: HOLE: no docstring
- [main](main.md) function: HOLE: no docstring
