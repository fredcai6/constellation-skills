# tests.test_crew_launcher:BackendEquivalenceTests.test_cli_resume_relaunches_and_finalizes
method, tests/test_crew_launcher.py:804, 20 lines

```python
def test_cli_resume_relaunches_and_finalizes(self)
```

HOLE: no docstring

calls internal: BackendEquivalenceTests.assertEqual x2, BackendEquivalenceTests.assertIn, fake_launch, result_rel, write_handoff
calls stdlib: builtins.str x2, pathlib.Path, tempfile.TemporaryDirectory
reads internal: RC x5
reads stdlib: tempfile (module)
unresolved: 6 calls (dispatch-unknown-base)

referenced by: none found
