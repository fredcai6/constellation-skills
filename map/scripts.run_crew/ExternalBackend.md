# scripts.run_crew:ExternalBackend
class, scripts/run_crew.py:582, 38 lines

```python
class ExternalBackend(CrewBackend)
```

Record-only backend: the crew is dispatched out-of-band (an Agent-tool

subagent in the Constellation harness, where no headless `claude` CLI exists).
`dispatch` spawns NOTHING — it records the durable entry (running, PID-less,
keeping the `dispatch: "external"` marker) and returns `(None, entry)`; the
caller verifies the result later. `resume` is unrecoverable-by-wrapper.

```python
name = BACKEND_EXTERNAL
```

- [dispatch](ExternalBackend.dispatch.md) method: HOLE: no docstring
- [resume](ExternalBackend.resume.md) method: HOLE: no docstring

reads internal: BACKEND_EXTERNAL, CrewSpec
reads stdlib: builtins.dict x4, builtins.list x2, builtins.tuple x2, pathlib.Path x2, builtins.int, builtins.str
writes internal: ExternalBackend.name

referenced by: 5 sites, this module only
