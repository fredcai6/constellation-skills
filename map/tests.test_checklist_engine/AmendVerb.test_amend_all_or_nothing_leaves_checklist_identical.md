# tests.test_checklist_engine:AmendVerb.test_amend_all_or_nothing_leaves_checklist_identical
method, tests/test_checklist_engine.py:1493, 12 lines

```python
def test_amend_all_or_nothing_leaves_checklist_identical(self)
```

HOLE: no docstring

calls internal: AmendVerb.assertEqual x2, gate x2, AmendVerb.assertNotIn, AmendVerb.assertRaises, _add_op, gated
calls stdlib: copy.deepcopy
reads internal: E x2, PASS_COMMAND x2
reads stdlib: copy (module)
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
