# tests.test_spine_rail:test_session_start_bind_on_resume_still_writes_under_the_bare_key
function, tests/test_spine_rail.py:534, 26 lines

```python
def test_session_start_bind_on_resume_still_writes_under_the_bare_key(proj)
```

SessionStart never carries an agent_id, so a resumed session is by

definition top-level: the bind-on-unambiguous-scan write must land under
the BARE session_id, never under a composite one. The sid's pre-existing
composite entry is FOREIGN so the existing-binding read is skipped and the
scan path is actually reached.

calls internal: make_spine x2, write_spine x2, _abs_spine, _claim_cmd, _real_post_tool_use, _real_subagent_payloads
calls stdlib: builtins.list x3, builtins.set, builtins.str
reads internal: sr x5
unresolved: 8 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
