# tests.test_spine_rail:_real_post_tool_use
function, tests/test_spine_rail.py:262, 10 lines

```python
def _real_post_tool_use(payload, command, cwd)
```

A PostToolUse payload built from a REAL captured payload: its own

session_id, and its own agent_id or the genuine ABSENCE of one, preserved
verbatim from the capture. Only `tool_input` and `cwd` are swapped, for the
engine command whose effect is under test. No agent_id is ever invented
here -- the point is that the harness delivers it.

calls stdlib: builtins.dict, builtins.str

referenced by: 24 sites, this module only
