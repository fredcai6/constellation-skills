# tests.test_gauge_reader:UncalibratedModelTests
class, tests/test_gauge_reader.py:31, 46 lines

```python
class UncalibratedModelTests(TestCase)
```

#252: a model with no profile must yield NO reading, and the reason must

be retrievable so a caller can explain the silence.

- [setUp](UncalibratedModelTests.setUp.md) method: HOLE: no docstring
- [tearDown](UncalibratedModelTests.tearDown.md) method: HOLE: no docstring
- [_write_flag](UncalibratedModelTests._write_flag.md) method: HOLE: no docstring
- [test_record_for_uncalibrated_model_yields_no_reading](UncalibratedModelTests.test_record_for_uncalibrated_model_yields_no_reading.md) method: Otherwise Trip judges the fill against DEFAULT_THRESHOLDS, i.e. the
- [test_calibrated_model_still_reads](UncalibratedModelTests.test_calibrated_model_still_reads.md) method: HOLE: no docstring
- [test_uncalibrated_model_reports_the_model](UncalibratedModelTests.test_uncalibrated_model_reports_the_model.md) method: HOLE: no docstring
- [test_no_flag_reports_none](UncalibratedModelTests.test_no_flag_reports_none.md) method: HOLE: no docstring
- [test_flag_naming_a_now_calibrated_model_is_ignored](UncalibratedModelTests.test_flag_naming_a_now_calibrated_model_is_ignored.md) method: A row added since the flag was written makes it obsolete — report
- [test_corrupt_flag_never_raises](UncalibratedModelTests.test_corrupt_flag_never_raises.md) method: HOLE: no docstring

referenced by: none found
