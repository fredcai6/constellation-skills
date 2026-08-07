# tests.test_crew_launcher:LaunchTests.test_resume_uses_stored_session_and_handoff
method, tests/test_crew_launcher.py:261, 23 lines

```python
def test_resume_uses_stored_session_and_handoff(self)
```

HOLE: no docstring

calls internal: LaunchTests.assertEqual x2, LaunchTests.assertIn, fake_launch, result_rel, write_handoff
calls stdlib: builtins.str x3, contextlib.redirect_stdout, io.StringIO, pathlib.Path, tempfile.TemporaryDirectory
reads internal: RC x9
reads stdlib: contextlib (module), io (module), tempfile (module)
unresolved: 9 calls (dispatch-unknown-base)

referenced by: none found
