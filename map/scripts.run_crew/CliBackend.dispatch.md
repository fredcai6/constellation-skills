# scripts.run_crew:CliBackend.dispatch
method, scripts/run_crew.py:503, 30 lines

```python
def dispatch(self, spec: CrewSpec, *, root: Path, entries: list[dict], launch=None) -> tuple[int, dict]
```

HOLE: no docstring

calls internal: save_registry x2, CliBackend.dispatch.launch, _now, _print_drift_hint_if_any, _require_handoff, build_crew_argv, build_entry, crew_env, finalize_from_exit_code, registry_path, run_log_paths
calls stdlib: builtins.str, os.getpid
reads internal: CrewSpec.role x3, CrewSpec.work_id x3, CrewSpec.attempt x2, CrewSpec.gate x2, CrewSpec.handoff x2, CrewSpec.result x2, CliBackend.name, CrewSpec.launcher, CrewSpec.model, CrewSpec.worktree, launch_process
reads stdlib: os (module)
writes internal: CliBackend.dispatch.launch
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found
