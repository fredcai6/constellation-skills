# scripts.verify_cycles:main
function, scripts/verify_cycles.py:54, 14 lines

```python
def main(argv: list[str] | None = None) -> int
```

HOLE: no docstring

calls internal: verify_cycles
calls stdlib: builtins.print x2, argparse.ArgumentParser, builtins.str
reads internal: CyclesVerificationError
reads stdlib: argparse (module), builtins.__doc__, pathlib.Path, sys (module), sys.stderr
unresolved: 3 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
