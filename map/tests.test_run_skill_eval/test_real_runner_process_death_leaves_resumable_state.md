# tests.test_run_skill_eval:test_real_runner_process_death_leaves_resumable_state
function, tests/test_run_skill_eval.py:1271, 80 lines

```python
def test_real_runner_process_death_leaves_resumable_state(tmp_path)
```

HOLE: no docstring

- [_refuse_installer](test_real_runner_process_death_leaves_resumable_state._refuse_installer.md) method: HOLE: no docstring

calls internal: _await_launched_runner, _confirm_hang_primitive, _write_hang_cmd, make_scenario, throwaway_worktree
calls stdlib: builtins.str x6, json.loads x2, builtins.dict, builtins.isinstance, subprocess.Popen
reads internal: rse x6, PASS_CHECK, RUN_SKILL_EVAL, fake_pass_launch
reads stdlib: subprocess (module) x4, json (module) x2, subprocess.TimeoutExpired x2, builtins.int, os (module), os.environ, subprocess.DEVNULL, sys (module), sys.executable
unresolved: 18 calls (dispatch-unknown-base), 4 reads (dispatch-unknown-base)

referenced by: none found
