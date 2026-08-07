# scripts.run_skill_eval:_tree_kill
function, scripts/run_skill_eval.py:597, 22 lines

```python
def _tree_kill(proc: 'subprocess.Popen') -> None
```

Hard-kill an entire process tree, best-effort, never raising — a kill failure

must not mask the timeout it is servicing. On Windows uses
`taskkill /PID <pid> /T /F` (the /T flag is what reaches grandchildren the plain
Popen.kill() TerminateProcess would leave orphaned); elsewhere falls back to
Popen.kill().

calls stdlib: builtins.str, subprocess.run
reads stdlib: subprocess (module) x5, subprocess.DEVNULL x3, builtins.OSError x2, os (module), os.name, subprocess.SubprocessError
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
