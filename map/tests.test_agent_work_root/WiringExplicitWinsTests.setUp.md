# tests.test_agent_work_root:WiringExplicitWinsTests.setUp
method, tests/test_agent_work_root.py:221, 3 lines

```python
def setUp(self)
```

HOLE: no docstring

calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: WiringExplicitWinsTests.tmp
reads stdlib: tempfile (module)
writes internal: WiringExplicitWinsTests.dir, WiringExplicitWinsTests.tmp
unresolved: 1 reads (dispatch-unknown-base)

referenced by: none found
