# scripts.verify_context_declaration:main
function, scripts/verify_context_declaration.py:164, 40 lines

```python
def main(argv: list[str] | None = None) -> int
```

HOLE: no docstring

calls internal: _is_checklist, check_checklist, discover_templates
calls stdlib: builtins.print x4, argparse.ArgumentParser, builtins.str, json.loads, pathlib.Path
reads stdlib: sys (module) x3, sys.stderr x3, argparse (module) x2, pathlib.Path x2, argparse.RawDescriptionHelpFormatter, builtins.OSError, builtins.ValueError, builtins.__doc__, builtins.list, builtins.str, json (module)
unresolved: 7 calls (dispatch-unknown-base), 4 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
