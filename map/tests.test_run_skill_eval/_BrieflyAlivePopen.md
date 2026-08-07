# tests.test_run_skill_eval:_BrieflyAlivePopen
class, tests/test_run_skill_eval.py:959, 23 lines

```python
class _BrieflyAlivePopen
```

A Popen double that reports alive for a few polls then exits 0, with pipes

already at EOF so drain threads finish immediately. Spawns nothing. Lets the
heartbeat stamp fire inside launch_agent's poll loop without a real subject.

- [__init__](_BrieflyAlivePopen.__init__.md) method: HOLE: no docstring
- [poll](_BrieflyAlivePopen.poll.md) method: HOLE: no docstring
- [wait](_BrieflyAlivePopen.wait.md) method: HOLE: no docstring

reads stdlib: builtins.int

referenced by: 2 sites, this module only
