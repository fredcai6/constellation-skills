# tests.test_checklist_engine:StaleRecordAdvisoryTests.test_stale_record_reports_raw_facts_no_threshold_language
method, tests/test_checklist_engine.py:3498, 11 lines

```python
def test_stale_record_reports_raw_facts_no_threshold_language(self)
```

HOLE: no docstring

calls internal: StaleRecordAdvisoryTests.assertIn x3, StaleRecordAdvisoryTests.assertNotIn x2, StaleRecordAdvisoryTests._write_gauge
calls stdlib: datetime.datetime.now, datetime.timedelta, pathlib.Path, tempfile.TemporaryDirectory
reads internal: E
reads stdlib: datetime.datetime, datetime.timezone, datetime.timezone.utc, tempfile (module)
unresolved: 2 calls (dispatch-unknown-base)

referenced by: none found
