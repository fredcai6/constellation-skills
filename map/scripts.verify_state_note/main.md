# scripts.verify_state_note:main
function, scripts/verify_state_note.py:73, 28 lines

```python
def main(argv: list[str] | None = None) -> int
```

HOLE: no docstring

calls internal: note_path, validate
calls stdlib: builtins.print x5, argparse.ArgumentParser, pathlib.Path
reads stdlib: sys (module) x4, sys.stderr x4, pathlib.Path x2, argparse (module), builtins.__doc__
unresolved: 6 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
