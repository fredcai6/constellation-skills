# scripts.context_manifest:manifest_path
function, scripts/context_manifest.py:431, 5 lines

```python
def manifest_path(agent_work_root: Any, work_id: str, step: str) -> Path
```

`<agent_work_root>/<work-id>/context/<step>.json` — named for this

function's own parameter, so the path shape is readable without knowing which
directory the caller happens to pass.

calls stdlib: builtins.str, pathlib.Path

referenced by: 1 sites, this module only
