# scripts.recover_crews:main
function, scripts/recover_crews.py:221, 19 lines

```python
def main(argv: list[str] | None = None) -> int
```

HOLE: no docstring

calls internal: _default_result_present, classify_registry, report
calls stdlib: argparse.ArgumentParser, builtins.print, pathlib.Path
reads internal: run_crew x4
reads stdlib: argparse (module), builtins.__doc__, pathlib.Path, sys (module), sys.stderr
unresolved: 5 calls (dispatch-unknown-base), 4 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
