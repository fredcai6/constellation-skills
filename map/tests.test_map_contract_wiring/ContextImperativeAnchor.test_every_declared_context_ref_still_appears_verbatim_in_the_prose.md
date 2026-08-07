# tests.test_map_contract_wiring:ContextImperativeAnchor.test_every_declared_context_ref_still_appears_verbatim_in_the_prose
method, tests/test_map_contract_wiring.py:110, 9 lines

```python
def test_every_declared_context_ref_still_appears_verbatim_in_the_prose(self)
```

`tests/test_context_declaration_lint.py` owns this rule; it is

restated here because the anchor edit rewrites this exact string, and a
dropped path would otherwise surface as a confusing failure in a suite
that is not about this change.

calls internal: ContextImperativeAnchor.assertIn, ContextImperativeAnchor.subTest, imperative, task

referenced by: none found
