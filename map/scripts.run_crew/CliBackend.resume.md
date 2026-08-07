# scripts.run_crew:CliBackend.resume
method, scripts/run_crew.py:534, 46 lines

```python
def resume(self, session: str, *, root: Path, entries: list[dict], launch=None) -> tuple[int, dict]
```

HOLE: no docstring

calls internal: CrewLaunchError x3, save_registry x2, CliBackend.resume.launch, _now, _print_drift_hint_if_any, build_crew_argv, crew_env, finalize_from_exit_code, find_entry, is_abandoned, registry_path
calls stdlib: pathlib.Path x3, builtins.str, os.getpid
reads internal: DEFAULT_LAUNCHER, launch_process
reads stdlib: os (module)
writes internal: CliBackend.resume.launch
unresolved: 6 calls (dispatch-unknown-base)

referenced by: none found
