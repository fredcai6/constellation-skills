# tests.test_run_skill_eval:_no_real_agent
function, tests/test_run_skill_eval.py:42, 25 lines

```python
@pytest.fixture(autouse=True)
def _no_real_agent(monkeypatch)
```

Fail LOUDLY if any test spawns a real `claude` agent subprocess. Check

subprocesses (`sys.executable <script> <run-dir>`) are allowed; a launcher
whose basename starts with `claude` is not. Wraps BOTH `subprocess.run` (used by
`run_check` and the taskkill tree-kill) and `subprocess.Popen` (used by the live
`launch_agent` seam) so every spawn path is intercepted.

- [_assert_not_claude](_no_real_agent._assert_not_claude.md) method: HOLE: no docstring
- [guarded_run](_no_real_agent.guarded_run.md) method: HOLE: no docstring
- [guarded_popen](_no_real_agent.guarded_popen.md) method: HOLE: no docstring

reads stdlib: subprocess (module) x4, subprocess.Popen, subprocess.run
unresolved: 2 calls (dispatch-unknown-base)

referenced by: none found
