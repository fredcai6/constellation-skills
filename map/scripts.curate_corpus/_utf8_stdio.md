# scripts.curate_corpus:_utf8_stdio
function, scripts/curate_corpus.py:145, 7 lines

```python
def _utf8_stdio() -> None
```

Match the sibling scripts: don't force every caller to set PYTHONIOENCODING.

reads stdlib: sys (module) x2, builtins.AttributeError, builtins.OSError, sys.stderr, sys.stdout
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
