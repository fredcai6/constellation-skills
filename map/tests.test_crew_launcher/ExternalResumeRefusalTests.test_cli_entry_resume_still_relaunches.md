# tests.test_crew_launcher:ExternalResumeRefusalTests.test_cli_entry_resume_still_relaunches
method, tests/test_crew_launcher.py:1016, 21 lines

```python
def test_cli_entry_resume_still_relaunches(self)
```

A cli entry keeps today's resume behavior (relaunch + finalize).

calls internal: ExternalResumeRefusalTests.assertEqual x2, ExternalResumeRefusalTests.assertIn, fake_launch, result_rel, write_handoff
calls stdlib: builtins.str x2, pathlib.Path, tempfile.TemporaryDirectory
reads internal: RC x5
reads stdlib: tempfile (module)
unresolved: 5 calls (dispatch-unknown-base)

referenced by: none found
