# scripts.init_work_area:instantiate_spine
function, scripts/init_work_area.py:152, 26 lines

```python
def instantiate_spine(root: Path, work_id: str, template: Path, skill_dir: str | None = None, force: bool = False) -> Path | None
```

Write .agent-work/<work-id>/spine.json from ``template`` with placeholders resolved.

Returns the written path, or ``None`` when an existing spine.json is left
intact because ``force`` was not passed.

calls internal: _assert_no_resolver_placeholders, init_work_area, resolve_spine
calls stdlib: builtins.print, json.loads
reads stdlib: json (module)
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
