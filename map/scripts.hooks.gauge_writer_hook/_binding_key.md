# scripts.hooks.gauge_writer_hook:_binding_key
function, scripts/hooks/gauge_writer_hook.py:205, 28 lines

```python
def _binding_key(data: dict)
```

This payload's outer binding key, or None to write NOTHING.

Thin on purpose: `spine_rail.binding_key` is the single place the
composite `session_id#agent_id` key is composed anywhere in the codebase
(#419 g1), and this module CALLS it rather than reimplementing it, so the
two hooks cannot drift.

What this adds is the `_spine_rail is None` guard, moved OUT here with the
call. `_load_spine_rail` returns None on any import failure; leaving the
guard behind in `resolve_gauge_path` would strand it, and an unguarded
`_spine_rail.binding_key(...)` would raise into `handle_post_tool_use`'s
outer `except` -- silence with zero diagnostic, wearing exactly the same
symptom as every other silence this module works to keep distinguishable.

It also applies THIS module's stricter `_is_usable_agent_id` allowlist
before delegating, so an id spine_rail admits but this module could not
safely put in a path resolves to None -- write nothing -- rather than
reaching the `agent-{agent_id}.jsonl` interpolation.

Deliberately carries NO try/except of its own: `binding_key` already
swallows internally, and a bare helper makes the guard directly
observable in a test instead of being absorbed one frame up.

calls internal: _is_usable_agent_id
reads internal: _spine_rail x2
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
