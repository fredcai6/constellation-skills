# tests.test_code_map:DiscoveryTests.setUp
method, tests/test_code_map.py:62, 4 lines

```python
def setUp(self)
```

HOLE: no docstring

calls internal: _make_repo
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: DiscoveryTests._tmp, DiscoveryTests.repo
reads stdlib: tempfile (module)
writes internal: DiscoveryTests._tmp, DiscoveryTests.repo
unresolved: 1 reads (dispatch-unknown-base)

referenced by: none found
