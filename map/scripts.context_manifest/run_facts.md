# scripts.context_manifest:run_facts
function, scripts/context_manifest.py:339, 27 lines

```python
def run_facts(roots: Mapping[str, Any], work_id: str | None = None) -> dict
```

The `/run` subtree: every legitimately-varying fact, and nothing else.

Absolute roots, timestamps and host facts all live here. Nothing varying may
live outside this subtree — that is what makes the determinism comparison a
single-pointer exclusion instead of a maintained field list.

A `dirty` flag lived here between #300 g5 rework 1 and #327 (#305 g4), when
it was removed outright — it is a fact about the producing environment's
noise (repo-wide, dominated by the run's own bookkeeping) rather than about
the bytes delivered, and it was neither dependable enough to rely on nor
varying informatively enough to read. Nothing replaced it: per-declared-file
dirtiness is derivable from content alone. Do not re-add it here without
reading the module docstring's measurement first.

calls stdlib: datetime.datetime.now, pathlib.Path, pathlib.Path.cwd, platform.python_version
reads internal: ROOT_TOKENS
reads stdlib: datetime.datetime, datetime.timezone, datetime.timezone.utc, pathlib.Path, platform (module), sys (module), sys.platform
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
