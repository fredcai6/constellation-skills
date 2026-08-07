# tests.test_agent_work_root:DurableRootFallbackTests.test_no_start_returns_cwd
method, tests/test_agent_work_root.py:202, 11 lines

```python
def test_no_start_returns_cwd(self)
```

HOLE: no docstring

calls internal: _norm x4, DurableRootFallbackTests.assertEqual x2
calls stdlib: os.chdir x2, os.getcwd, pathlib.Path.cwd
reads internal: DurableRootFallbackTests.tmp x2, DurableRootFallbackTests.mod
reads stdlib: os (module) x3, pathlib.Path
unresolved: 1 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found
