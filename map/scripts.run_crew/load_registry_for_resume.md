# scripts.run_crew:load_registry_for_resume
function, scripts/run_crew.py:933, 8 lines

```python
def load_registry_for_resume(session: str, root: Path) -> list[dict]
```

Resolve the registry that holds `session` by parsing the work-id from a

`constellation/<work-id>/...` session name.

calls internal: CrewLaunchError, load_registry, registry_path
calls stdlib: builtins.len
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 3 sites, this module only
