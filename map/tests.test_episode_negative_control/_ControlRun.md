# tests.test_episode_negative_control:_ControlRun
class, tests/test_episode_negative_control.py:419, 201 lines

```python
class _ControlRun
```

Drives ONE checklist through the real engine CLI and keeps its own tally.

CLI subprocesses, not the Python API, and that is load-bearing rather than
stylistic: `refusals` is armed by `claim` but incremented ONLY in
`checklist_engine.main()`'s `EngineError` branch, so an API-driven control would
never move the counter and would be measuring a field that production does move.

```python
VERBS = ('claim', 'start', 'attest', 'advance', 'reopen')
REOPEN_REASON = 'control'
```

- [__init__](_ControlRun.__init__.md) method: HOLE: no docstring
- [_run](_ControlRun._run.md) method: HOLE: no docstring
- [_session](_ControlRun._session.md) method: HOLE: no docstring
- [drive](_ControlRun.drive.md) method: The whole run. Every action is one a run mechanically requires.
- [expectations](_ControlRun.expectations.md) method: HOLE: no docstring
- [compose](_ControlRun.compose.md) method: The reading under test. Attribute lookup on the module happens HERE, at call
- [manifest](_ControlRun.manifest.md) method: The step's delivery manifest, as the seam wrote it (#360, see `expectations`).
- [snapshot](_ControlRun.snapshot.md) method: What the SEAM wrote on its own, with no test asking it to.

reads internal: Expect
reads stdlib: builtins.str x7, builtins.dict x4, pathlib.Path x3, builtins.list x2, builtins.bool, subprocess (module), subprocess.CompletedProcess
writes internal: _ControlRun.REOPEN_REASON, _ControlRun.VERBS

referenced by: 8 sites, this module only
