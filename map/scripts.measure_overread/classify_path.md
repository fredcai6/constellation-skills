# scripts.measure_overread:classify_path
function, scripts/measure_overread.py:117, 13 lines

```python
def classify_path(path: str) -> str | None
```

Classify `path` as "state", "engine-source", or None (not structural).

None includes every path this instrument does not count as a structural
read -- see the module docstring's "Explicitly NOT counted" section.

calls internal: _basename
reads internal: _ENGINE_SOURCE_PATTERNS, _STATE_FILE_PATTERNS
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
