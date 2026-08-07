# tests.test_verify_cycles:VerifyCyclesTests.setUp
method, tests/test_verify_cycles.py:24, 6 lines

```python
def setUp(self)
```

HOLE: no docstring

calls internal: load
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: VerifyCyclesTests.root, VerifyCyclesTests.tmp, VerifyCyclesTests.work_area
reads stdlib: tempfile (module)
writes internal: VerifyCyclesTests.m, VerifyCyclesTests.root, VerifyCyclesTests.tmp, VerifyCyclesTests.work_area
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
