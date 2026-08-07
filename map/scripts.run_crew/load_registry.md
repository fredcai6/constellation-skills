# scripts.run_crew:load_registry
function, scripts/run_crew.py:106, 8 lines

```python
def load_registry(path: Path) -> list[dict]
```

Read the registry list; a missing file is an empty registry.

calls internal: CrewLaunchError
calls stdlib: builtins.isinstance, json.loads
reads stdlib: builtins.list, json (module)
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 3 sites, this module only
