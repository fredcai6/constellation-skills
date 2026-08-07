# scripts.verify_diagnosis:main
function, scripts/verify_diagnosis.py:173, 21 lines

```python
def main(argv: list[str] | None = None) -> int
```

HOLE: no docstring

calls internal: verify_diagnosis
calls stdlib: builtins.print x3, argparse.ArgumentParser, json.loads, pathlib.Path
reads internal: DiagnosisError
reads stdlib: argparse (module) x2, json (module) x2, sys (module) x2, sys.stderr x2, argparse.RawDescriptionHelpFormatter, builtins.OSError, builtins.__doc__, json.JSONDecodeError
unresolved: 5 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
