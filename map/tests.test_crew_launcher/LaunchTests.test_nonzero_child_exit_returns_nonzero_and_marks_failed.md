# tests.test_crew_launcher:LaunchTests.test_nonzero_child_exit_returns_nonzero_and_marks_failed
method, tests/test_crew_launcher.py:181, 13 lines

```python
def test_nonzero_child_exit_returns_nonzero_and_marks_failed(self)
```

HOLE: no docstring

calls internal: LaunchTests.assertEqual, LaunchTests.assertNotEqual, fake_launch, result_rel, write_handoff
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: RC x2
reads stdlib: tempfile (module)
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found
