# scripts.verify_interrogation:main
function, scripts/verify_interrogation.py:170, 23 lines

```python
def main(argv: list[str] | None = None) -> int
```

HOLE: no docstring

calls internal: verify_interrogation
calls stdlib: builtins.print x3, argparse.ArgumentParser, builtins.bool, builtins.len, json.loads, pathlib.Path
reads internal: InterrogationError
reads stdlib: argparse (module) x2, json (module) x2, sys (module) x2, sys.stderr x2, argparse.RawDescriptionHelpFormatter, builtins.OSError, builtins.__doc__, json.JSONDecodeError
unresolved: 5 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
