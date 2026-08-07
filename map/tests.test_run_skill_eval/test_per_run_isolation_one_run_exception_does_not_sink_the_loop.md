# tests.test_run_skill_eval:test_per_run_isolation_one_run_exception_does_not_sink_the_loop
function, tests/test_run_skill_eval.py:1172, 24 lines

```python
def test_per_run_isolation_one_run_exception_does_not_sink_the_loop(tmp_path)
```

HOLE: no docstring

- [flaky_launch](test_per_run_isolation_one_run_exception_does_not_sink_the_loop.flaky_launch.md) method: HOLE: no docstring

calls internal: make_scenario, throwaway_worktree
calls stdlib: builtins.any, builtins.len, builtins.range, builtins.str, json.loads
reads internal: rse x2, PASS_CHECK
reads stdlib: json (module)
unresolved: 4 calls (dispatch-unknown-base), 4 reads (dispatch-unknown-base)

referenced by: none found
