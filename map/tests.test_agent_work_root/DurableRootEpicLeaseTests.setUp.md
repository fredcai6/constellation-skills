# tests.test_agent_work_root:DurableRootEpicLeaseTests.setUp
method, tests/test_agent_work_root.py:111, 8 lines

```python
def setUp(self)
```

HOLE: no docstring

calls internal: _git, _init_repo, _load
calls stdlib: pathlib.Path x2, builtins.str, tempfile.TemporaryDirectory
reads internal: DurableRootEpicLeaseTests.main x3, DurableRootEpicLeaseTests.tmp x2, DurableRootEpicLeaseTests.linked
reads stdlib: tempfile (module)
writes internal: DurableRootEpicLeaseTests.linked, DurableRootEpicLeaseTests.main, DurableRootEpicLeaseTests.mod, DurableRootEpicLeaseTests.tmp
unresolved: 1 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found
