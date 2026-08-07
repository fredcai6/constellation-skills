# scripts.hooks.gauge_writer_hook:_load_spine_rail
function, scripts/hooks/gauge_writer_hook.py:122, 15 lines

```python
def _load_spine_rail()
```

Load scripts/hooks/spine_rail.py by file path -- robust regardless of

whether this module is run as a script or imported by a test (mirrors
tests/test_spine_rail.py's own loading technique). Returns None if the
sibling module is missing or fails to load; callers then skip (the
binding becomes unresolvable, which is itself a valid skip-on-uncertainty
outcome -- see docs/GAUGE_WRITER_HOOK.md).

calls stdlib: importlib.util.module_from_spec, importlib.util.spec_from_file_location, pathlib.Path
reads stdlib: importlib (module) x2, importlib.util x2, builtins.Exception
unresolved: 2 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base), 1 reads (unbound-name)

referenced by: 1 sites, this module only
