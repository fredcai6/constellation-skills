# tests.test_checklist_engine:TripTwoBandGatePolicy.test_hard_refusal_leaves_state_unmutated
method, tests/test_checklist_engine.py:3296, 7 lines

```python
def test_hard_refusal_leaves_state_unmutated(self)
```

HOLE: no docstring

calls internal: TripTwoBandGatePolicy.assertEqual, TripTwoBandGatePolicy.assertRaises, _advance_ns, _reading
calls stdlib: copy.deepcopy, pathlib.Path
reads internal: E x3, TripTwoBandGatePolicy.cl x3, TripTwoBandGatePolicy.hard
reads stdlib: copy (module), unittest.mock, unittest.mock.patch
unresolved: 1 calls (chained-attribute), 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
