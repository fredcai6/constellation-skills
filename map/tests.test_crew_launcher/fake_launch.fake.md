# tests.test_crew_launcher:fake_launch.fake
method, tests/test_crew_launcher.py:65, 12 lines

```python
def fake(argv, *, stdin, env, stdout_path, stderr_path)
```

HOLE: no docstring

calls stdlib: pathlib.Path x5
reads internal: fake_launch.write_result_at x3, fake_launch.exit_code
unresolved: 6 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found
