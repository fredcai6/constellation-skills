# scripts.checklist_engine:_utf8_stdio
function, scripts/checklist_engine.py:43, 10 lines

```python
def _utf8_stdio() -> None
```

Captured stdio on Windows falls back to cp1252; checklist text with

non-ascii then crashes every print. Field feedback (f1brainz
engine-current-cp1252-crash): own the encoding here instead of requiring
PYTHONIOENCODING at every call site.

reads stdlib: sys (module) x2, builtins.AttributeError, builtins.OSError, sys.stderr, sys.stdout
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
