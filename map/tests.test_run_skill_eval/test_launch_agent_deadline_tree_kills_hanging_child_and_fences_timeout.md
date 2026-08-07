# tests.test_run_skill_eval:test_launch_agent_deadline_tree_kills_hanging_child_and_fences_timeout
function, tests/test_run_skill_eval.py:719, 22 lines

```python
def test_launch_agent_deadline_tree_kills_hanging_child_and_fences_timeout(tmp_path, monkeypatch)
```

HOLE: no docstring

- [spy_tree_kill](test_launch_agent_deadline_tree_kills_hanging_child_and_fences_timeout.spy_tree_kill.md) method: HOLE: no docstring

calls internal: _HangingPopen
calls stdlib: builtins.str x3, builtins.dict
reads internal: rse x3, _HangingPopen.pid
reads stdlib: builtins.int, builtins.list, os (module), os.environ, subprocess (module)
unresolved: 4 calls (dispatch-unknown-base), 4 reads (dispatch-unknown-base)

referenced by: none found
