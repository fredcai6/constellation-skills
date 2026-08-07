# src.utils.utilization:_set_os_priority
function, src/utils/utilization.py:177, 24 lines

```python
def _set_os_priority(priority: str) -> None
```

Best-effort OS scheduling priority for the current process.

Windows uses psutil priority classes; POSIX uses ``os.nice``. "normal" leaves the
process untouched. Any failure is swallowed (priority is an optimization, not a
correctness requirement).

calls stdlib: os.nice
calls third-party: psutil.Process
reads internal: logger
reads stdlib: os (module) x2, builtins.Exception, os.name
reads third-party: psutil (module) x3
unresolved: 4 calls (dispatch-unknown-base), 2 calls (dynamic)

referenced by: 1 sites, this module only
