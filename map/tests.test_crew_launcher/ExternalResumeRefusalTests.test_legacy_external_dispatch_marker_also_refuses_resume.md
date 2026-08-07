# tests.test_crew_launcher:ExternalResumeRefusalTests.test_legacy_external_dispatch_marker_also_refuses_resume
method, tests/test_crew_launcher.py:997, 18 lines

```python
def test_legacy_external_dispatch_marker_also_refuses_resume(self)
```

A legacy external entry (dispatch marker, no `backend` field) still routes

to the external backend via entry_backend and refuses to spawn.

calls internal: ExternalResumeRefusalTests.assertEqual, ExternalResumeRefusalTests.assertIn, ExternalResumeRefusalTests.assertRaises, fake_launch, result_rel
calls stdlib: builtins.str, pathlib.Path, tempfile.TemporaryDirectory
reads internal: RC x3
reads stdlib: tempfile (module)
unresolved: 2 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found
