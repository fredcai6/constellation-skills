# tests.test_gauge_reader:RawRecordTests
class, tests/test_gauge_reader.py:207, 75 lines

```python
class RawRecordTests(TestCase)
```

#265: raw_record reports the file's own facts with field-shape

validation only -- no staleness, no clock-skew, no calibration gate. The
caller-facing purpose is a frozen `gauge.json` `read()` itself rejected
(e.g. simply too old) still has SOMETHING honest to say about it.

- [setUp](RawRecordTests.setUp.md) method: HOLE: no docstring
- [tearDown](RawRecordTests.tearDown.md) method: HOLE: no docstring
- [_write](RawRecordTests._write.md) method: HOLE: no docstring
- [test_absent_file_returns_none](RawRecordTests.test_absent_file_returns_none.md) method: HOLE: no docstring
- [test_corrupt_json_returns_none](RawRecordTests.test_corrupt_json_returns_none.md) method: HOLE: no docstring
- [test_missing_field_returns_none](RawRecordTests.test_missing_field_returns_none.md) method: HOLE: no docstring
- [test_wrong_typed_field_returns_none](RawRecordTests.test_wrong_typed_field_returns_none.md) method: HOLE: no docstring
- [test_stale_record_STILL_reports_raw_facts](RawRecordTests.test_stale_record_STILL_reports_raw_facts.md) method: HOLE: no docstring
- [test_uncalibrated_model_STILL_reports_raw_facts](RawRecordTests.test_uncalibrated_model_STILL_reports_raw_facts.md) method: HOLE: no docstring
- [test_clock_skew_STILL_reports_raw_facts](RawRecordTests.test_clock_skew_STILL_reports_raw_facts.md) method: HOLE: no docstring
- [test_fresh_record_reports_same_facts_as_a_reading](RawRecordTests.test_fresh_record_reports_same_facts_as_a_reading.md) method: HOLE: no docstring
- [test_returns_exactly_three_keys](RawRecordTests.test_returns_exactly_three_keys.md) method: HOLE: no docstring

referenced by: none found
