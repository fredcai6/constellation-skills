# tests.test_checklist_engine:AmendVerb.test_amend_add_refuses_before_frozen_gate
method, tests/test_checklist_engine.py:1428, 12 lines

```python
def test_amend_add_refuses_before_frozen_gate(self)
```

HOLE: no docstring

calls internal: gate x3, AmendVerb.assertIn, AmendVerb.assertRaises, _add_op, gated
calls stdlib: builtins.str
reads internal: PASS_COMMAND x3, E x2
unresolved: 1 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found
