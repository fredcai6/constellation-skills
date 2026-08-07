# scripts.install_constellation:script_source_path
function, scripts/install_constellation.py:140, 6 lines

```python
def script_source_path(script: str, scripts_root: Path) -> Path
```

Where a bundled script is READ from. Single resolver so validation and the

copy loop can never disagree about a script's source -- a disagreement would
surface as a hard install failure or, worse, a missing companion.

reads internal: SCRIPT_SOURCE_SUBDIRS
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
