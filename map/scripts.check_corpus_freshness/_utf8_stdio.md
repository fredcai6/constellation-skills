# scripts.check_corpus_freshness:_utf8_stdio
function, scripts/check_corpus_freshness.py:36, 7 lines

```python
def _utf8_stdio() -> None
```

Mirror check_skill_freshness: don't make every call site set PYTHONIOENCODING.

reads stdlib: sys (module) x2, builtins.AttributeError, builtins.OSError, sys.stderr, sys.stdout
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
