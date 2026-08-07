# tests.test_episode_negative_control:_ControlRun.drive
method, tests/test_episode_negative_control.py:476, 50 lines

```python
def drive(self, ok_flag: Path) -> None
```

The whole run. Every action is one a run mechanically requires.

calls internal: _ControlRun._run x16, _ControlRun._session
calls stdlib: builtins.range
reads internal: _ControlRun._rework x4, _ControlRun.REOPEN_REASON x2, _ControlRun._failed x2, _ControlRun._reopens x2, _ControlRun.role x2, _ControlRun.work_id
writes internal: _ControlRun._reopens x2, _ControlRun._rework[] x2, _ControlRun._failed[], _ControlRun._refusals
unresolved: 4 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
