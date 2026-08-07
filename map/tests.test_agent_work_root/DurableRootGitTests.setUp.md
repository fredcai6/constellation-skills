# tests.test_agent_work_root:DurableRootGitTests.setUp
method, tests/test_agent_work_root.py:76, 6 lines

```python
def setUp(self)
```

HOLE: no docstring

calls internal: _init_repo, _load
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: DurableRootGitTests.main x2, DurableRootGitTests.tmp
reads stdlib: tempfile (module)
writes internal: DurableRootGitTests.main, DurableRootGitTests.mod, DurableRootGitTests.tmp
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
