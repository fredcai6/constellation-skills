# tests.test_run_skill_eval:_confirm_hang_primitive
function, tests/test_run_skill_eval.py:1212, 18 lines

```python
def _confirm_hang_primitive(hang_cmd: Path) -> None
```

Handoff stop-condition guard: independently re-confirm the `.cmd` subject

spawns AND hangs under `Popen(shell=False)` here before relying on it. If it does
not, fail loudly — do NOT silently switch to a POSIX mechanism. Self-contained
try/finally so this probe can never leak its own process.

calls stdlib: builtins.str, subprocess.Popen, time.sleep
reads internal: rse
reads stdlib: subprocess (module) x5, subprocess.DEVNULL x3, subprocess.TimeoutExpired, time (module)
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
