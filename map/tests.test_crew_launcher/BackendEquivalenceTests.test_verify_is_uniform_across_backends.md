# tests.test_crew_launcher:BackendEquivalenceTests.test_verify_is_uniform_across_backends
method, tests/test_crew_launcher.py:781, 22 lines

```python
def test_verify_is_uniform_across_backends(self)
```

CrewBackend.verify (used by both backends) finalizes on a fresh result

exactly like verify_external_result — the same instance/API on either.

calls internal: BackendEquivalenceTests.assertEqual x2, BackendEquivalenceTests.assertFalse, BackendEquivalenceTests.assertTrue, result_rel, write_handoff
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: RC x3
reads stdlib: tempfile (module)
unresolved: 7 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
