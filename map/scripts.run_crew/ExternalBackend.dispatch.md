# scripts.run_crew:ExternalBackend.dispatch
method, scripts/run_crew.py:591, 18 lines

```python
def dispatch(self, spec: CrewSpec, *, root: Path, entries: list[dict], launch=None) -> tuple[None, dict]
```

HOLE: no docstring

calls internal: _now, _require_handoff, build_entry, registry_path, save_registry
reads internal: CrewSpec.handoff x2, CrewSpec.work_id x2, CrewSpec.attempt, CrewSpec.gate, CrewSpec.model, CrewSpec.result, CrewSpec.role, CrewSpec.worktree, DISPATCH_EXTERNAL, ExternalBackend.name
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found
