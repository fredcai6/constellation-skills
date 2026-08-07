# tests.test_worktree_precondition_wiring:EngineDeliberateBreakage.setUp
method, tests/test_worktree_precondition_wiring.py:120, 11 lines

```python
def setUp(self)
```

HOLE: no docstring

calls internal: EngineDeliberateBreakage._git x2, _load_engine
calls stdlib: os.getcwd, pathlib.Path, tempfile.TemporaryDirectory
reads internal: EngineDeliberateBreakage.repo, EngineDeliberateBreakage.tmp
reads stdlib: os (module), tempfile (module)
writes internal: EngineDeliberateBreakage.E, EngineDeliberateBreakage._cwd, EngineDeliberateBreakage.repo, EngineDeliberateBreakage.tmp
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
