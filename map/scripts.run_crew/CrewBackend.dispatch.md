# scripts.run_crew:CrewBackend.dispatch
method, scripts/run_crew.py:454, 5 lines

```python
def dispatch(self, spec: CrewSpec, *, root: Path, entries: list[dict], launch=None) -> tuple[int | None, dict]
```

Record the durable entry (running) BEFORE work. cli: spawn the

subprocess then finalize -> (exit_code, entry). external: record-only, no
subprocess -> (None, entry); the caller verifies later.

reads stdlib: builtins.NotImplementedError

referenced by: none found
