# scripts.check_skill_freshness:main
function, scripts/check_skill_freshness.py:151, 42 lines

```python
def main(argv: list[str] | None = None) -> int
```

HOLE: no docstring

calls internal: check, update_baseline
calls stdlib: builtins.print x5, argparse.ArgumentParser, pathlib.Path
reads internal: FreshnessError
reads stdlib: pathlib.Path x2, argparse (module), builtins.OSError, builtins.__doc__, json (module), json.JSONDecodeError, sys (module), sys.stderr
unresolved: 4 calls (dispatch-unknown-base), 5 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
