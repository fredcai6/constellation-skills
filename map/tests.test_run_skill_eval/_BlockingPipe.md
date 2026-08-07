# tests.test_run_skill_eval:_BlockingPipe
class, tests/test_run_skill_eval.py:683, 11 lines

```python
class _BlockingPipe
```

A pipe double whose read() blocks until the child is 'killed', then EOF.

Models a grandchild holding the write-handle so read() never naturally returns —
the exact wedge that hung the old subprocess.run(timeout=) wait.

- [__init__](_BlockingPipe.__init__.md) method: HOLE: no docstring
- [read](_BlockingPipe.read.md) method: HOLE: no docstring

reads stdlib: threading (module), threading.Event

referenced by: 2 sites, this module only
