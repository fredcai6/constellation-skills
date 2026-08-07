# tests.test_worktree_precondition_wiring:EnumerationDeliberateBreakage.setUp
method, tests/test_worktree_precondition_wiring.py:61, 3 lines

```python
def setUp(self)
```

HOLE: no docstring

calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: EnumerationDeliberateBreakage.tmp
reads stdlib: tempfile (module)
writes internal: EnumerationDeliberateBreakage.tmp, EnumerationDeliberateBreakage.tmp_root
unresolved: 1 reads (dispatch-unknown-base)

referenced by: none found
