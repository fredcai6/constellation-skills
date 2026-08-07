# tests.test_episode_fields:FailedCommandsFieldTests.test_a_passing_command_check_does_not_count
method, tests/test_episode_fields.py:592, 15 lines

```python
def test_a_passing_command_check_does_not_count(self)
```

The one-sided test's blind spot: a counter that counted every command

would pass a test that only ever checks it goes up.

calls internal: FailedCommandsFieldTests.assertEqual x2, LiveSpine.verb x2, FailedCommandsFieldTests.assertTrue, LiveSpine, LiveSpine.load
calls stdlib: builtins.any, pathlib.Path
reads internal: FailedCommandsFieldTests.tmp, ec
unresolved: 1 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found
