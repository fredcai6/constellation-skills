# scripts.verify_skip_guard:main
function, scripts/verify_skip_guard.py:98, 24 lines

```python
def main(argv: list[str] | None = None) -> int
```

HOLE: no docstring

calls internal: _load_report, find_disallowed_skips, iter_skips
calls stdlib: builtins.print x4, argparse.ArgumentParser, builtins.len, builtins.sum
reads internal: SkipGuardError
reads stdlib: sys (module) x3, sys.stderr x3, argparse (module) x2, argparse.RawDescriptionHelpFormatter, builtins.__doc__, pathlib.Path
unresolved: 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
