# tests.test_checklist_engine:RefreshRequestIdentity.test_hard_coattails_fixed_stale_why_ref_refused_then_fresh_releases
method, tests/test_checklist_engine.py:3372, 29 lines

```python
def test_hard_coattails_fixed_stale_why_ref_refused_then_fresh_releases(self)
```

HOLE: no docstring

calls internal: RefreshRequestIdentity.assertEqual x3, gate x3, _reading x2, RefreshRequestIdentity.assertIn, RefreshRequestIdentity.assertRaises, gated
calls stdlib: pathlib.Path x2, copy.deepcopy, types.SimpleNamespace
reads internal: E x12, PASS_COMMAND x3
reads stdlib: unittest.mock x2, unittest.mock.patch x2, copy (module), types (module)
unresolved: 2 calls (chained-attribute), 9 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found
