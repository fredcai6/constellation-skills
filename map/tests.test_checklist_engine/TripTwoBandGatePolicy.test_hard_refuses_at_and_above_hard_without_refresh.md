# tests.test_checklist_engine:TripTwoBandGatePolicy.test_hard_refuses_at_and_above_hard_without_refresh
method, tests/test_checklist_engine.py:3268, 12 lines

```python
def test_hard_refuses_at_and_above_hard_without_refresh(self)
```

HOLE: no docstring

calls internal: TripTwoBandGatePolicy.assertIn x2, TripTwoBandGatePolicy.assertEqual, TripTwoBandGatePolicy.assertRaises, _advance_ns, _reading
calls stdlib: builtins.str x2, builtins.min, copy.deepcopy, pathlib.Path
reads internal: E x3, TripTwoBandGatePolicy.hard x2, TripTwoBandGatePolicy.cl
reads stdlib: copy (module), unittest.mock, unittest.mock.patch
unresolved: 1 calls (chained-attribute), 2 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: none found
