# tests.test_gauge_reader:UncalibratedModelTests.test_flag_naming_a_now_calibrated_model_is_ignored
method, tests/test_gauge_reader.py:67, 5 lines

```python
def test_flag_naming_a_now_calibrated_model_is_ignored(self)
```

A row added since the flag was written makes it obsolete — report

nothing rather than nag about a model that now resolves fine.

calls internal: UncalibratedModelTests._write_flag, UncalibratedModelTests.assertIsNone
reads internal: UncalibratedModelTests.m, UncalibratedModelTests.path
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found
