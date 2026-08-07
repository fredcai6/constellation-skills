# tests.test_crew_launcher:BackendInvariantContractTests.test_both_backends_verify_exists_and_fresh_identically
method, tests/test_crew_launcher.py:1057, 23 lines

```python
def test_both_backends_verify_exists_and_fresh_identically(self)
```

HOLE: no docstring

calls internal: BackendInvariantContractTests.assertEqual x3, BackendInvariantContractTests.assertFalse x3, BackendInvariantContractTests.assertTrue x2, write_result_with_mtime x2, BackendInvariantContractTests._entry_for
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: BackendInvariantContractTests.BASE x2, RC x2
reads stdlib: tempfile (module)
unresolved: 5 calls (dispatch-unknown-base), 9 reads (dispatch-unknown-base)

referenced by: none found
