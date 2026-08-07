# scripts.run_crew:CliBackend
class, scripts/run_crew.py:496, 84 lines

```python
class CliBackend(CrewBackend)
```

Spawn a headless `claude` CLI subprocess via the single `launch_process`

seam. Records the durable entry (running) BEFORE the child starts, runs it
foreground, then finalizes from the child exit code + result freshness.

```python
name = BACKEND_CLI
```

- [dispatch](CliBackend.dispatch.md) method: HOLE: no docstring
- [resume](CliBackend.resume.md) method: HOLE: no docstring

reads internal: BACKEND_CLI, CrewSpec
reads stdlib: builtins.dict x4, builtins.int x2, builtins.list x2, builtins.tuple x2, pathlib.Path x2, builtins.str
writes internal: CliBackend.name

referenced by: 4 sites, this module only
