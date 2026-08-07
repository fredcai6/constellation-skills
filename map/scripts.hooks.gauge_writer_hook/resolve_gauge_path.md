# scripts.hooks.gauge_writer_hook:resolve_gauge_path
function, scripts/hooks/gauge_writer_hook.py:235, 33 lines

```python
def resolve_gauge_path(project_dir: Path, binding_key)
```

`.agent-work/<work_id>/gauge.json` for EVERY spine this BINDING KEY is

currently bound to (#202: one key can hold N distinct spine bindings at
once) -- a list of Path, possibly empty. Each candidate is individually
checked against `_is_contained`; a candidate that fails the fence is
dropped rather than failing the whole call, so one bad entry never blinds
the write for the key's other, legitimate bindings.

The key is `_binding_key(payload)`, NOT the bare `session_id` (#419):
Agent-tool subagents share their parent's session_id, so a session-keyed
lookup piled every crew claim under one key and left this writer with 2+
candidates and no way to tell whose reading it held -- so it wrote nothing,
for exactly the runs an orchestrator dispatches. A dispatched agent is
keyed `session_id#agent_id`; a top-level agent keeps the bare session_id.

Empty list if unresolvable (no sibling module, no key, no binding at all)
-- skip-on-uncertainty applies to WHERE we write, not just to what.

calls internal: _is_contained
calls stdlib: builtins.isinstance, pathlib.Path
reads internal: _spine_rail x2
reads stdlib: builtins.Exception, builtins.dict
unresolved: 5 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
