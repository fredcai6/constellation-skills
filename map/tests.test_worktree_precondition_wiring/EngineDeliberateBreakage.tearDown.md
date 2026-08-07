# tests.test_worktree_precondition_wiring:EngineDeliberateBreakage.tearDown
method, tests/test_worktree_precondition_wiring.py:132, 3 lines

```python
def tearDown(self)
```

HOLE: no docstring

calls stdlib: os.chdir
reads internal: EngineDeliberateBreakage._cwd, EngineDeliberateBreakage.tmp
reads stdlib: os (module)
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found
