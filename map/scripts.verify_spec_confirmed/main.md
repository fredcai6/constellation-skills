# scripts.verify_spec_confirmed:main
function, scripts/verify_spec_confirmed.py:187, 17 lines

```python
def main(argv: list[str] | None = None) -> int
```

HOLE: no docstring

calls internal: resolve_target, verify_spec_confirmed
calls stdlib: builtins.print x2, argparse.ArgumentParser, builtins.str
reads internal: SpecVerificationError
reads stdlib: argparse (module), builtins.__doc__, pathlib.Path, sys (module), sys.stderr
unresolved: 5 calls (dispatch-unknown-base), 5 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
