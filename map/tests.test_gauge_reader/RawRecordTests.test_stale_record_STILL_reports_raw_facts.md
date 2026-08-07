# tests.test_gauge_reader:RawRecordTests.test_stale_record_STILL_reports_raw_facts
method, tests/test_gauge_reader.py:242, 10 lines

```python
def test_stale_record_STILL_reports_raw_facts(self)
```

HOLE: no docstring

calls internal: RawRecordTests.assertEqual x3, RawRecordTests._write, RawRecordTests.assertIsNone, RawRecordTests.assertIsNotNone
calls stdlib: datetime.timedelta x2, builtins.dict
reads internal: NOW x3, RawRecordTests.m x2, RawRecordTests.path x2, FRESH_RECORD, MAX_AGE
unresolved: 3 calls (dispatch-unknown-base)

referenced by: none found
