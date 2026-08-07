# tests.test_explorer_templates:CycleTemplateCrossCheck.test_one_unconsolidated_among_consolidated_fails
method, tests/test_explorer_templates.py:198, 8 lines

```python
def test_one_unconsolidated_among_consolidated_fails(self)
```

HOLE: no docstring

calls internal: CycleTemplateCrossCheck._write_cycle x2, CycleTemplateCrossCheck._verify, CycleTemplateCrossCheck.assertIn, CycleTemplateCrossCheck.assertRaises
calls stdlib: builtins.dict, builtins.str
reads internal: CycleTemplateCrossCheck.tpl x2, CycleTemplateCrossCheck.m
unresolved: 2 reads (dispatch-unknown-base)

referenced by: none found
