# tests.test_verify_cycles:VerifyCyclesTests.test_fail_not_a_survey
method, tests/test_verify_cycles.py:63, 5 lines

```python
def test_fail_not_a_survey(self)
```

HOLE: no docstring

calls internal: VerifyCyclesTests.assertIn, VerifyCyclesTests.assertRaises, VerifyCyclesTests.verify, VerifyCyclesTests.write_cycle
calls stdlib: builtins.str, json.dumps
reads internal: VerifyCyclesTests.m
reads stdlib: json (module)
unresolved: 2 reads (dispatch-unknown-base)

referenced by: none found
