# tests.test_gauge_writer:test_worktree_local_agent_work_outside_project_dir_still_writes
function, tests/test_gauge_writer.py:235, 18 lines

```python
def test_worktree_local_agent_work_outside_project_dir_still_writes(proj, tmp_path)
```

Containment checks the `.agent-work/<work_id>/` SHAPE, not containment

within project_dir. Under an active Admiral epic lease `durable_root()`
resolves to the worktree root, so a legitimate spine can sit in a
different checkout entirely -- that must still be written, or the governor
goes blind for exactly the epic runs it matters most in.

calls internal: _bind, _hook_data
calls stdlib: json.loads
calls third-party: pytest.approx
reads internal: EXPECTED_FILL, EXPECTED_MODEL, _FIXTURE, gw
reads stdlib: json (module)
reads third-party: pytest (module)
unresolved: 4 calls (dispatch-unknown-base)

referenced by: none found
