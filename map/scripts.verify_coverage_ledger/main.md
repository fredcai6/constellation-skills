# scripts.verify_coverage_ledger:main
function, scripts/verify_coverage_ledger.py:104, 26 lines

```python
def main(argv: list[str] | None = None) -> int
```

HOLE: no docstring

calls internal: _load_json x2, manifest_externals, verify_coverage_ledger
calls stdlib: builtins.print x2, builtins.sum x2, argparse.ArgumentParser, builtins.len, builtins.str, pathlib.Path
reads internal: CoverageLedgerError
reads stdlib: pathlib.Path x3, argparse (module), builtins.FileNotFoundError, builtins.__doc__, json (module), json.JSONDecodeError, sys (module), sys.stderr
unresolved: 7 calls (dispatch-unknown-base), 5 reads (dispatch-unknown-base), 1 reads (unbound-name)

referenced by: 1 sites, this module only
