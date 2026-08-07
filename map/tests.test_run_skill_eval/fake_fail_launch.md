# tests.test_run_skill_eval:fake_fail_launch
function, tests/test_run_skill_eval.py:546, 10 lines

```python
def fake_fail_launch(argv, *, cwd, env, stdout_path, stderr_path, timeout)
```

Agent-free fake: exits 0 (so the run COMPLETED) but leaves a broken

workspace with no completion artifact, so the process check fails -> completed
-fail (tallied, never fenced). Spawns nothing.

calls stdlib: pathlib.Path x3
reads internal: rse
unresolved: 5 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
