# tests.test_checklist_engine:NextVerbsAreLegalFromHere.test_pending_with_open_null_precondition_suppresses_start
method, tests/test_checklist_engine.py:4258, 9 lines

```python
def test_pending_with_open_null_precondition_suppresses_start(self)
```

HOLE: no docstring

calls internal: NextVerbsAreLegalFromHere._next, NextVerbsAreLegalFromHere.assertFalse, NextVerbsAreLegalFromHere.assertTrue, gate, gated
calls stdlib: builtins.any x2, copy.deepcopy
reads internal: E
reads stdlib: copy (module)
unresolved: 3 calls (dispatch-unknown-base)

referenced by: none found
