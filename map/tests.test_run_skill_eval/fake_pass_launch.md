# tests.test_run_skill_eval:fake_pass_launch
function, tests/test_run_skill_eval.py:535, 9 lines

```python
def fake_pass_launch(argv, *, cwd, env, stdout_path, stderr_path, timeout)
```

Agent-free fake: writes the completion artifact a finished run leaves, so

the process check bites and the run classifies completed-pass. Spawns nothing.

calls stdlib: pathlib.Path x3
reads internal: rse x2
unresolved: 5 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 13 sites, this module only
