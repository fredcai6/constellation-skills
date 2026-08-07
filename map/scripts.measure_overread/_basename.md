# scripts.measure_overread:_basename
function, scripts/measure_overread.py:108, 7 lines

```python
def _basename(path: str) -> str
```

Basename of `path`, tolerant of both '/' and '\' separators

regardless of the host OS running this script -- a transcript captured
on Windows can contain backslash paths even when this scan runs on a
POSIX CI box, and pathlib.PurePath's separator handling is platform-
dependent, so this is done by hand for cross-platform determinism.

unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
