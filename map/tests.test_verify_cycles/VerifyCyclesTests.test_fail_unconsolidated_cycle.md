# tests.test_verify_cycles:VerifyCyclesTests.test_fail_unconsolidated_cycle
method, tests/test_verify_cycles.py:50, 6 lines

```python
def test_fail_unconsolidated_cycle(self)
```

HOLE: no docstring

calls internal: VerifyCyclesTests.write_cycle x2, VerifyCyclesTests.assertIn, VerifyCyclesTests.assertRaises, VerifyCyclesTests.verify
calls stdlib: builtins.str
reads internal: CONSOLIDATED_CYCLE, UNCONSOLIDATED_CYCLE, VerifyCyclesTests.m
unresolved: 2 reads (dispatch-unknown-base)

referenced by: none found
