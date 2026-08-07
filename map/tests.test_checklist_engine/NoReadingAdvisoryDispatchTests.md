# tests.test_checklist_engine:NoReadingAdvisoryDispatchTests
class, tests/test_checklist_engine.py:3532, 29 lines

```python
class NoReadingAdvisoryDispatchTests(TestCase)
```

_no_reading_advisory tries each localizable cause in order and returns

the FIRST non-empty result -- the three sub-advisories are mocked
directly (band-structure style) since this is testing DISPATCH ORDER,
not any one advisory's own text.

- [test_uncalibrated_wins_over_skip_and_stale](NoReadingAdvisoryDispatchTests.test_uncalibrated_wins_over_skip_and_stale.md) method: HOLE: no docstring
- [test_skip_reason_wins_over_stale_when_uncalibrated_empty](NoReadingAdvisoryDispatchTests.test_skip_reason_wins_over_stale_when_uncalibrated_empty.md) method: HOLE: no docstring
- [test_stale_record_is_the_last_resort](NoReadingAdvisoryDispatchTests.test_stale_record_is_the_last_resort.md) method: HOLE: no docstring
- [test_all_empty_yields_empty](NoReadingAdvisoryDispatchTests.test_all_empty_yields_empty.md) method: HOLE: no docstring

referenced by: none found
