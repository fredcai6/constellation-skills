# tests.test_crew_launcher:write_result_with_mtime
function, tests/test_crew_launcher.py:19, 7 lines

```python
def write_result_with_mtime(path: Path, mtime: float) -> None
```

Write a result artifact and stamp its mtime deterministically into the

past/future, so STALE vs FRESH is decided by the clock we choose, not by
wall-time flakiness.

calls stdlib: os.utime
reads stdlib: os (module)
unresolved: 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 11 sites, this module only
