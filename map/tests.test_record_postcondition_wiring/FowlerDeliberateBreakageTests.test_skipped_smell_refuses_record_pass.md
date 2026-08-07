# tests.test_record_postcondition_wiring:FowlerDeliberateBreakageTests.test_skipped_smell_refuses_record_pass
method, tests/test_record_postcondition_wiring.py:255, 17 lines

```python
def test_skipped_smell_refuses_record_pass(self)
```

HOLE: no docstring

calls internal: FowlerDeliberateBreakageTests._item_for, FowlerDeliberateBreakageTests.assertEqual, FowlerDeliberateBreakageTests.assertIn, FowlerDeliberateBreakageTests.assertIsNone, FowlerDeliberateBreakageTests.assertRaises, _all_absent, _fowler_record, survey
calls stdlib: builtins.str, copy.deepcopy, json.dumps, pathlib.Path
reads internal: E x3, FowlerDeliberateBreakageTests.tmp
reads stdlib: copy (module), json (module)
unresolved: 3 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: none found
