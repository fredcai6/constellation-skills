# tests.test_gauge_reader:UncalibratedModelTests.test_record_for_uncalibrated_model_yields_no_reading
method, tests/test_gauge_reader.py:48, 7 lines

```python
def test_record_for_uncalibrated_model_yields_no_reading(self)
```

Otherwise Trip judges the fill against DEFAULT_THRESHOLDS, i.e. the

wrong scale — the exact failure #252 reports. The record here is
perfectly fresh and well-formed; only the model is unknown.

calls internal: UncalibratedModelTests.assertIsNone
calls stdlib: builtins.dict, json.dumps
reads internal: UncalibratedModelTests.path x2, FRESH_RECORD, MAX_AGE, NOW, UncalibratedModelTests.m
reads stdlib: json (module)
unresolved: 2 calls (dispatch-unknown-base)

referenced by: none found
