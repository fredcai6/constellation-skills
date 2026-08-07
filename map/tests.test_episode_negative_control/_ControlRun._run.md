# tests.test_episode_negative_control:_ControlRun._run
method, tests/test_episode_negative_control.py:450, 22 lines

```python
def _run(self, *argv: str, refused: bool = False) -> subprocess.CompletedProcess
```

HOLE: no docstring

calls stdlib: builtins.str x2, builtins.tuple, subprocess.run
reads internal: _ControlRun._refusals x2, ENGINE, _ControlRun.VERBS, _ControlRun.calls, _ControlRun.issued, _ControlRun.path
reads stdlib: subprocess (module), sys (module), sys.executable
writes internal: _ControlRun._refusals
unresolved: 2 calls (dispatch-unknown-base), 4 reads (dispatch-unknown-base)

referenced by: 18 sites, this module only
