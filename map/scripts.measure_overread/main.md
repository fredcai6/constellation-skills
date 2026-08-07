# scripts.measure_overread:main
function, scripts/measure_overread.py:236, 32 lines

```python
def main(argv: list[str] | None = None) -> int
```

HOLE: no docstring

calls internal: format_report, scan_corpus
calls stdlib: builtins.print x3, argparse.ArgumentParser, builtins.__doc__.splitlines, pathlib.Path
reads internal: DEFAULT_CORPUS_DIR, REPO_ROOT
reads stdlib: sys (module) x2, sys.stderr x2, argparse (module), builtins.__doc__
unresolved: 4 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
