# scripts.query_episodes:writer
function, scripts/query_episodes.py:104, 18 lines

```python
def writer()
```

g2's writer module — the single home of the record grammar (parse_episode) and

of EPISODE_STORE.md section 7's seams. Resolved lazily on every call rather than
bound once at import, so a caller that has already imported the writer (a test, a
harness) shares that exact module object and its seams, instead of this module
quietly operating on a second, divergent copy.

calls stdlib: importlib.util.module_from_spec, importlib.util.spec_from_file_location, pathlib.Path, sys.modules.get
reads internal: _WRITER_MODULE x3, _WRITER_PATH x2
reads stdlib: importlib (module) x2, importlib.util x2, sys (module) x2, sys.modules x2, builtins.OSError, builtins.ValueError
writes stdlib: sys.modules[]
unresolved: 2 calls (dispatch-unknown-base), 1 calls (dynamic), 1 reads (dispatch-unknown-base)

referenced by: 8 sites, this module only
