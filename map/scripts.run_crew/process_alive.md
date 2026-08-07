# scripts.run_crew:process_alive
function, scripts/run_crew.py:275, 17 lines

```python
def process_alive(pid: int | None) -> bool
```

Whether `pid` names a live process. The injectable PID-liveness seam used

by recovery classification (recover_crews imports it). Default uses
`os.kill(pid, 0)`: ESRCH/no-such-process -> dead; EPERM (the process exists
but is not ours) -> alive. Tests monkeypatch this so recovery never inspects
real PIDs.

calls stdlib: builtins.int, os.kill
reads stdlib: builtins.OSError, builtins.PermissionError, builtins.ProcessLookupError, builtins.ValueError, os (module)

referenced by: none found
