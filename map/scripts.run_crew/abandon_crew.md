# scripts.run_crew:abandon_crew
function, scripts/run_crew.py:752, 10 lines

```python
def abandon_crew(entries: list[dict], session: str, root: Path) -> dict
```

Mark a prior attempt abandoned (releases its hold on the gate/worktree).

calls internal: CrewLaunchError, _now, find_entry, registry_path, save_registry
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
