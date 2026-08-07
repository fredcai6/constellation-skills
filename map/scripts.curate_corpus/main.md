# scripts.curate_corpus:main
function, scripts/curate_corpus.py:425, 24 lines

```python
def main(argv: list[str] | None = None) -> int
```

HOLE: no docstring

calls internal: _utf8_stdio, build_record, curate, render_table
calls stdlib: builtins.print x3, argparse.ArgumentParser, json.dumps, pathlib.Path
reads stdlib: argparse (module) x2, argparse.RawDescriptionHelpFormatter, builtins.__doc__, json (module)
unresolved: 5 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
