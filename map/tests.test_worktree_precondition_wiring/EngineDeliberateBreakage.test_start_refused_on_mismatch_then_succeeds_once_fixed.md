# tests.test_worktree_precondition_wiring:EngineDeliberateBreakage.test_start_refused_on_mismatch_then_succeeds_once_fixed
method, tests/test_worktree_precondition_wiring.py:165, 18 lines

```python
def test_start_refused_on_mismatch_then_succeeds_once_fixed(self)
```

HOLE: no docstring

calls internal: EngineDeliberateBreakage.assertEqual x3, EngineDeliberateBreakage._gated_checklist, EngineDeliberateBreakage.assertIn, EngineDeliberateBreakage.assertRaises
calls stdlib: builtins.str, os.chdir, pathlib.Path
reads internal: EngineDeliberateBreakage.E x3, EngineDeliberateBreakage.repo x2, EngineDeliberateBreakage.tmp, ISOLATION_SCRIPT
reads stdlib: os (module), sys (module), sys.executable
unresolved: 6 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base), 1 writes (non-name-expr)

referenced by: none found
