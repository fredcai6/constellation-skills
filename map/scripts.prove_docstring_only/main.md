# scripts.prove_docstring_only:main
function, scripts/prove_docstring_only.py:89, 34 lines

```python
def main() -> int
```

HOLE: no docstring

calls internal: source_at x2, strip_docstrings x2
calls stdlib: builtins.print x10, ast.dump x4, ast.parse x4, argparse.ArgumentParser, builtins.__doc__.splitlines
reads stdlib: ast (module) x8, argparse (module), builtins.__doc__
unresolved: 4 calls (dispatch-unknown-base), 7 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
