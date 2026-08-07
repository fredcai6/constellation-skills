# scripts.run_crew:CrewBackend.resume
method, scripts/run_crew.py:460, 4 lines

```python
def resume(self, session: str, *, root: Path, entries: list[dict], launch=None) -> tuple[int, dict]
```

cli: relaunch the subprocess with the stored session/handoff and

finalize. external: unrecoverable-by-wrapper (raise CrewLaunchError).

reads stdlib: builtins.NotImplementedError

referenced by: 1 sites, this module only
