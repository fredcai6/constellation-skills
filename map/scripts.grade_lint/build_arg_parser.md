# scripts.grade_lint:build_arg_parser
function, scripts/grade_lint.py:637, 33 lines

```python
def build_arg_parser() -> argparse.ArgumentParser
```

HOLE: no docstring

calls stdlib: argparse.ArgumentParser
reads stdlib: argparse (module) x2, argparse.RawDescriptionHelpFormatter, builtins.__doc__
unresolved: 7 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
