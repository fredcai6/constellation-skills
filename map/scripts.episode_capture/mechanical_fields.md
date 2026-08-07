# scripts.episode_capture:mechanical_fields
function, scripts/episode_capture.py:367, 69 lines

```python
def mechanical_fields(checklist: Mapping[str, Any], base_dir: Any = None) -> dict[str, Any]
```

The mechanical field group for the checklist's ACTIVE step, from engine state.

Returns only the fields that could be sourced honestly. A caller that finds a key
missing is being told "this could not be read", which is information; a caller
handed a plausible default would be told nothing at all.

The step is `checklist_engine.active_id()` — the engine's own selector, imported
rather than re-derived, so this can never disagree with the engine about which
step is live. When it returns `None` (every item terminal) the step-scoped fields
are refused as a group rather than reported against some other step.

calls internal: _artifact_refs, _engine, _lease_role, failed_command_count, manifest_ref, project_name, reopen_total
calls stdlib: builtins.isinstance x6
reads stdlib: builtins.bool x2, builtins.dict x2, builtins.int x2, builtins.str x2, typing.Any
unresolved: 8 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
