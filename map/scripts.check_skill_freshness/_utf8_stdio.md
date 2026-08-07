# scripts.check_skill_freshness:_utf8_stdio
function, scripts/check_skill_freshness.py:25, 7 lines

```python
def _utf8_stdio() -> None
```

Per field feedback: don't make every call site set PYTHONIOENCODING.

reads stdlib: sys (module) x2, builtins.AttributeError, builtins.OSError, sys.stderr, sys.stdout
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
