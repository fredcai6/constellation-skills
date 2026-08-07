# scripts.verify_worktree_precondition_coverage:main
function, scripts/verify_worktree_precondition_coverage.py:125, 16 lines

```python
def main(argv: list[str] | None = None) -> int
```

HOLE: no docstring

calls internal: verify_coverage
calls stdlib: builtins.print x3, argparse.ArgumentParser, builtins.str, pathlib.Path
reads internal: CoverageError
reads stdlib: argparse (module) x2, sys (module) x2, sys.stderr x2, argparse.RawDescriptionHelpFormatter, builtins.__doc__, pathlib.Path
unresolved: 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
