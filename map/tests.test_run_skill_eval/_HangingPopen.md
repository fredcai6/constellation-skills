# tests.test_run_skill_eval:_HangingPopen
class, tests/test_run_skill_eval.py:696, 21 lines

```python
class _HangingPopen
```

A subprocess.Popen double that NEVER exits on its own: poll() stays None and

its pipes never hit EOF until something kills it. Spawns nothing.

- [__init__](_HangingPopen.__init__.md) method: HOLE: no docstring
- [poll](_HangingPopen.poll.md) method: HOLE: no docstring
- [wait](_HangingPopen.wait.md) method: HOLE: no docstring
- [_die](_HangingPopen._die.md) method: HOLE: no docstring

referenced by: 1 sites, this module only
