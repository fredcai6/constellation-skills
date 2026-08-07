# tests.test_gauge_writer:test_binding_key_helper_returns_none_when_spine_rail_failed_to_load
function, tests/test_gauge_writer.py:714, 13 lines

```python
def test_binding_key_helper_returns_none_when_spine_rail_failed_to_load(proj, monkeypatch)
```

The `_spine_rail is None` guard lives at the binding-key call site, NOT

only inside resolve_gauge_path. `_load_spine_rail` returns None on any
import failure; an unguarded `_spine_rail.binding_key(...)` would raise
into handle_post_tool_use's outer swallow, leaving the governor silent
with zero diagnostic -- wearing the same symptom as every other silence.

This asserts the guard where it is OBSERVABLE: `_binding_key` carries no
swallow of its own, so a missing guard surfaces as a raised AttributeError
here instead of being absorbed one frame up.

reads internal: gw x3
unresolved: 3 calls (dispatch-unknown-base)

referenced by: none found
