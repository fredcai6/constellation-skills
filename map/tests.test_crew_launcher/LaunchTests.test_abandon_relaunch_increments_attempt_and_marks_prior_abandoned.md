# tests.test_crew_launcher:LaunchTests.test_abandon_relaunch_increments_attempt_and_marks_prior_abandoned
method, tests/test_crew_launcher.py:232, 28 lines

```python
def test_abandon_relaunch_increments_attempt_and_marks_prior_abandoned(self)
```

HOLE: no docstring

calls internal: LaunchTests.assertEqual x3, LaunchTests.assertIn, LaunchTests.assertTrue, fake_launch, result_rel, write_handoff
calls stdlib: builtins.str, contextlib.redirect_stdout, io.StringIO, pathlib.Path, tempfile.TemporaryDirectory
reads internal: RC x7
reads stdlib: contextlib (module), io (module), tempfile (module)
unresolved: 6 calls (dispatch-unknown-base)

referenced by: none found
