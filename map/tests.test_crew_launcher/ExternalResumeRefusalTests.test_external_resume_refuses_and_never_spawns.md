# tests.test_crew_launcher:ExternalResumeRefusalTests.test_external_resume_refuses_and_never_spawns
method, tests/test_crew_launcher.py:976, 20 lines

```python
def test_external_resume_refuses_and_never_spawns(self)
```

HOLE: no docstring

calls internal: ExternalResumeRefusalTests.assertEqual x2, ExternalResumeRefusalTests.assertIn, fake_launch, result_rel, write_handoff
calls stdlib: builtins.str, contextlib.redirect_stderr, io.StringIO, pathlib.Path, tempfile.TemporaryDirectory
reads internal: RC x4
reads stdlib: contextlib (module), io (module), tempfile (module)
unresolved: 5 calls (dispatch-unknown-base)

referenced by: none found
