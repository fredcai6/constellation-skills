# tests.test_explorer_templates:DesignSpecTemplateCrossCheck.test_blank_confirmed_by_alone_fails_confirm
method, tests/test_explorer_templates.py:127, 6 lines

```python
def test_blank_confirmed_by_alone_fails_confirm(self)
```

HOLE: no docstring

calls internal: DesignSpecTemplateCrossCheck.assertEqual, DesignSpecTemplateCrossCheck.assertIn, DesignSpecTemplateCrossCheck.assertRaises, _confirmed
calls stdlib: builtins.str
reads internal: DesignSpecTemplateCrossCheck.m x3, CONFIRMED_BY_BLANK, CONFIRMED_BY_FILLED, DesignSpecTemplateCrossCheck.tpl
unresolved: 3 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found
