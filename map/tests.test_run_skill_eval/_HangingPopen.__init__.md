# tests.test_run_skill_eval:_HangingPopen.__init__
method, tests/test_run_skill_eval.py:700, 6 lines

```python
def __init__(self)
```

HOLE: no docstring

calls internal: _BlockingPipe x2
calls stdlib: threading.Event
reads internal: _HangingPopen._done x2
reads stdlib: threading (module)
writes internal: _HangingPopen._done, _HangingPopen.pid, _HangingPopen.returncode, _HangingPopen.stderr, _HangingPopen.stdout

referenced by: none found
