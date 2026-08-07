# tests.test_run_skill_eval:_write_hang_cmd
function, tests/test_run_skill_eval.py:1202, 8 lines

```python
def _write_hang_cmd(dir_path: Path) -> Path
```

A `.cmd` shim whose subject sleeps 600s, so a runner that spawns it as its

`--command` launcher blocks in launch_agent's poll loop (poll() stays None) until
something kills it — the empirically-verified hang primitive for this Windows box.
Popen(shell=False) spawns it; taskkill /T reaps the cmd.exe + `py` grandchild.

unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
