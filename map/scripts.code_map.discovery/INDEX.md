# scripts.code_map.discovery
scripts/code_map/discovery.py, 35 lines

Enumerate the mappable corpus: the source files the map is derived from.

The corpus is every TRACKED Python file, minus the excluded prefixes below.
Tracked, because an untracked file is not yet part of the repository and a
generated one is not source. `git ls-files` is the enumerator, so .gitignore and
the index decide membership rather than a second rule that would drift from them.

imports stdlib: pathlib.Path, subprocess
imported by: scripts.code_map.checks, scripts.code_map.cli, scripts.code_map.extract, scripts.code_map.supplement, tests.test_code_map

```python
EXCLUDED_PREFIXES = ('.agent-work/',)
```

- [is_mappable](is_mappable.md) function: True when a tracked repo-relative path belongs in the mappable corpus.
- [tracked_python_files](tracked_python_files.md) function: Every Python file git tracks under `root`, as sorted posix-relative paths.
- [discover_corpus](discover_corpus.md) function: The mappable corpus under `root`, as sorted posix-relative paths.
