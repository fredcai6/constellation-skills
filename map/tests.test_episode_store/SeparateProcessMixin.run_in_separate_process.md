# tests.test_episode_store:SeparateProcessMixin.run_in_separate_process
method, tests/test_episode_store.py:1183, 19 lines

```python
def run_in_separate_process(self, script, args, cwd)
```

HOLE: no docstring

calls internal: SeparateProcessMixin.fail
calls stdlib: builtins.str x2, subprocess.Popen
reads internal: SeparateProcessMixin.CHILD_TIMEOUT
reads stdlib: subprocess (module) x4, subprocess.PIPE x2, subprocess.TimeoutExpired, sys (module), sys.executable
unresolved: 3 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: 5 sites, this module only
