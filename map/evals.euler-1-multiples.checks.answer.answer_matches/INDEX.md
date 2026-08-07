# evals.euler-1-multiples.checks.answer.answer_matches
evals/euler-1-multiples/checks/answer/answer_matches.py, 80 lines, 3 holes

ADVISORY answer check -- NEVER gates the verdict (structural T3).

The runner executes, records, and prints this, but the verdict gate reads ONLY
``checks/*.py`` (process). ``checks/answer/*.py`` can NEVER move the verdict. This
exists to show answer-correctness is recorded but weak-never-sufficient: a corpus
that prints the right number while botching the workflow still FAILs on the process
checks; this line is diagnostic only.

It tries to run any solution file in the workspace and check its stdout for the
known answer, else scans workspace text/data files for it.

Usage: ``python answer_matches.py <run-dir>``  (exit code is informational only).

imports stdlib: __future__.annotations, pathlib.Path, subprocess, sys
imported by: none found

```python
KNOWN_ANSWER = '233168'
EXCLUDED_PARTS = {'.claude', '.git', '.agent-work'}
SCAN_SUFFIXES = {'.txt', '.md', '.json', '.out', '.log', '.csv'}
```

- [_run_solutions](_run_solutions.md) function: HOLE: no docstring
- [_scan_files](_scan_files.md) function: HOLE: no docstring
- [main](main.md) function: HOLE: no docstring
