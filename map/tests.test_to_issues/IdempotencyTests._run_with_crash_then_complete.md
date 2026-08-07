# tests.test_to_issues:IdempotencyTests._run_with_crash_then_complete
method, tests/test_to_issues.py:235, 21 lines

```python
def _run_with_crash_then_complete(self, crash_at: str)
```

HOLE: no docstring

calls internal: IdempotencyTests.assertEqual x3, IdempotencyTests.assertRaises, well_formed_manifest
calls stdlib: builtins.set, pathlib.Path, tempfile.TemporaryDirectory
reads internal: IdempotencyTests.filer x4, CONFIRMED_SPEC x2
reads stdlib: tempfile (module)
unresolved: 6 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 3 sites, this module only
