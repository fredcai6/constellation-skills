# tests.test_gauge_reader
tests/test_gauge_reader.py, 437 lines, 59 holes

HOLE: no docstring

imports stdlib: datetime.datetime, datetime.timedelta, datetime.timezone, importlib.util, json, pathlib.Path, sys, tempfile, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 7, 18, 12, 0, 0, tzinfo=timezone.utc)
MAX_AGE = timedelta(minutes=30)
FRESH_RECORD = {'schema_version': 1, 'fill_fraction': 0.42, 'model': 'claude-opus-4-8', 'observed_at':...
```

- [load](load.md) function: HOLE: no docstring
- [UncalibratedModelTests](UncalibratedModelTests.md) class: #252: a model with no profile must yield NO reading, and the reason must
  - [UncalibratedModelTests.setUp](UncalibratedModelTests.setUp.md) method: HOLE: no docstring
  - [UncalibratedModelTests.tearDown](UncalibratedModelTests.tearDown.md) method: HOLE: no docstring
  - [UncalibratedModelTests._write_flag](UncalibratedModelTests._write_flag.md) method: HOLE: no docstring
  - [UncalibratedModelTests.test_record_for_uncalibrated_model_yields_no_reading](UncalibratedModelTests.test_record_for_uncalibrated_model_yields_no_reading.md) method: Otherwise Trip judges the fill against DEFAULT_THRESHOLDS, i.e. the
  - [UncalibratedModelTests.test_calibrated_model_still_reads](UncalibratedModelTests.test_calibrated_model_still_reads.md) method: HOLE: no docstring
  - [UncalibratedModelTests.test_uncalibrated_model_reports_the_model](UncalibratedModelTests.test_uncalibrated_model_reports_the_model.md) method: HOLE: no docstring
  - [UncalibratedModelTests.test_no_flag_reports_none](UncalibratedModelTests.test_no_flag_reports_none.md) method: HOLE: no docstring
  - [UncalibratedModelTests.test_flag_naming_a_now_calibrated_model_is_ignored](UncalibratedModelTests.test_flag_naming_a_now_calibrated_model_is_ignored.md) method: A row added since the flag was written makes it obsolete — report
  - [UncalibratedModelTests.test_corrupt_flag_never_raises](UncalibratedModelTests.test_corrupt_flag_never_raises.md) method: HOLE: no docstring
- [ModelTableSyncTests](ModelTableSyncTests.md) class: The writer supplies the window, the reader supplies the thresholds. A
  - [ModelTableSyncTests.test_writer_and_reader_cover_the_same_models](ModelTableSyncTests.test_writer_and_reader_cover_the_same_models.md) method: HOLE: no docstring
  - [ModelTableSyncTests.test_windows_agree_between_the_two_tables](ModelTableSyncTests.test_windows_agree_between_the_two_tables.md) method: The reader stores the window alongside its caps; a disagreement
- [ReadTests](ReadTests.md) class: HOLE: no docstring
  - [ReadTests.setUp](ReadTests.setUp.md) method: HOLE: no docstring
  - [ReadTests.tearDown](ReadTests.tearDown.md) method: HOLE: no docstring
  - [ReadTests._write](ReadTests._write.md) method: HOLE: no docstring
  - [ReadTests._read](ReadTests._read.md) method: HOLE: no docstring
  - [ReadTests.test_absent_file_returns_none](ReadTests.test_absent_file_returns_none.md) method: HOLE: no docstring
  - [ReadTests.test_corrupt_json_returns_none](ReadTests.test_corrupt_json_returns_none.md) method: HOLE: no docstring
  - [ReadTests.test_missing_field_returns_none](ReadTests.test_missing_field_returns_none.md) method: HOLE: no docstring
  - [ReadTests.test_wrong_typed_field_returns_none](ReadTests.test_wrong_typed_field_returns_none.md) method: HOLE: no docstring
  - [ReadTests.test_out_of_range_fill_fraction_returns_none](ReadTests.test_out_of_range_fill_fraction_returns_none.md) method: HOLE: no docstring
  - [ReadTests.test_bool_schema_version_returns_none](ReadTests.test_bool_schema_version_returns_none.md) method: HOLE: no docstring
  - [ReadTests.test_unparseable_observed_at_returns_none](ReadTests.test_unparseable_observed_at_returns_none.md) method: HOLE: no docstring
  - [ReadTests.test_stale_record_returns_none](ReadTests.test_stale_record_returns_none.md) method: HOLE: no docstring
  - [ReadTests.test_clock_skew_returns_none](ReadTests.test_clock_skew_returns_none.md) method: HOLE: no docstring
  - [ReadTests.test_stale_never_yields_a_reading_at_the_boundary](ReadTests.test_stale_never_yields_a_reading_at_the_boundary.md) method: HOLE: no docstring
  - [ReadTests.test_fresh_record_returns_a_reading](ReadTests.test_fresh_record_returns_a_reading.md) method: HOLE: no docstring
  - [ReadTests.test_small_clock_skew_within_tolerance_still_reads](ReadTests.test_small_clock_skew_within_tolerance_still_reads.md) method: HOLE: no docstring
  - [ReadTests.test_naive_now_does_not_raise](ReadTests.test_naive_now_does_not_raise.md) method: HOLE: no docstring
- [RawRecordTests](RawRecordTests.md) class: #265: raw_record reports the file's own facts with field-shape
  - [RawRecordTests.setUp](RawRecordTests.setUp.md) method: HOLE: no docstring
  - [RawRecordTests.tearDown](RawRecordTests.tearDown.md) method: HOLE: no docstring
  - [RawRecordTests._write](RawRecordTests._write.md) method: HOLE: no docstring
  - [RawRecordTests.test_absent_file_returns_none](RawRecordTests.test_absent_file_returns_none.md) method: HOLE: no docstring
  - [RawRecordTests.test_corrupt_json_returns_none](RawRecordTests.test_corrupt_json_returns_none.md) method: HOLE: no docstring
  - [RawRecordTests.test_missing_field_returns_none](RawRecordTests.test_missing_field_returns_none.md) method: HOLE: no docstring
  - [RawRecordTests.test_wrong_typed_field_returns_none](RawRecordTests.test_wrong_typed_field_returns_none.md) method: HOLE: no docstring
  - [RawRecordTests.test_stale_record_STILL_reports_raw_facts](RawRecordTests.test_stale_record_STILL_reports_raw_facts.md) method: HOLE: no docstring
  - [RawRecordTests.test_uncalibrated_model_STILL_reports_raw_facts](RawRecordTests.test_uncalibrated_model_STILL_reports_raw_facts.md) method: HOLE: no docstring
  - [RawRecordTests.test_clock_skew_STILL_reports_raw_facts](RawRecordTests.test_clock_skew_STILL_reports_raw_facts.md) method: HOLE: no docstring
  - [RawRecordTests.test_fresh_record_reports_same_facts_as_a_reading](RawRecordTests.test_fresh_record_reports_same_facts_as_a_reading.md) method: HOLE: no docstring
  - [RawRecordTests.test_returns_exactly_three_keys](RawRecordTests.test_returns_exactly_three_keys.md) method: HOLE: no docstring
- [SkipReasonTests](SkipReasonTests.md) class: #265: skip_reason mirrors uncalibrated_model's fail-safe contract for
  - [SkipReasonTests.setUp](SkipReasonTests.setUp.md) method: HOLE: no docstring
  - [SkipReasonTests.tearDown](SkipReasonTests.tearDown.md) method: HOLE: no docstring
  - [SkipReasonTests._write_skip](SkipReasonTests._write_skip.md) method: HOLE: no docstring
  - [SkipReasonTests.test_no_sidecar_returns_none](SkipReasonTests.test_no_sidecar_returns_none.md) method: HOLE: no docstring
  - [SkipReasonTests.test_corrupt_sidecar_never_raises](SkipReasonTests.test_corrupt_sidecar_never_raises.md) method: HOLE: no docstring
  - [SkipReasonTests.test_ambiguous_binding_reports_reason_and_candidate_count](SkipReasonTests.test_ambiguous_binding_reports_reason_and_candidate_count.md) method: HOLE: no docstring
  - [SkipReasonTests.test_no_usable_record_has_no_candidate_count_key](SkipReasonTests.test_no_usable_record_has_no_candidate_count_key.md) method: HOLE: no docstring
  - [SkipReasonTests.test_missing_reason_returns_none](SkipReasonTests.test_missing_reason_returns_none.md) method: HOLE: no docstring
  - [SkipReasonTests.test_missing_observed_at_returns_none](SkipReasonTests.test_missing_observed_at_returns_none.md) method: HOLE: no docstring
  - [SkipReasonTests.test_unparseable_observed_at_returns_none](SkipReasonTests.test_unparseable_observed_at_returns_none.md) method: HOLE: no docstring
  - [SkipReasonTests.test_bool_candidate_count_is_dropped_not_reported](SkipReasonTests.test_bool_candidate_count_is_dropped_not_reported.md) method: HOLE: no docstring
  - [SkipReasonTests.test_non_int_candidate_count_is_dropped_not_reported](SkipReasonTests.test_non_int_candidate_count_is_dropped_not_reported.md) method: HOLE: no docstring
  - [SkipReasonTests.test_never_staleness_checked](SkipReasonTests.test_never_staleness_checked.md) method: HOLE: no docstring
- [ThresholdsForTests](ThresholdsForTests.md) class: HOLE: no docstring
  - [ThresholdsForTests.setUp](ThresholdsForTests.setUp.md) method: HOLE: no docstring
  - [ThresholdsForTests.test_unknown_model_falls_back_to_default](ThresholdsForTests.test_unknown_model_falls_back_to_default.md) method: HOLE: no docstring
  - [ThresholdsForTests.test_known_model_returns_its_keyed_pair](ThresholdsForTests.test_known_model_returns_its_keyed_pair.md) method: HOLE: no docstring
  - [ThresholdsForTests.test_equivalence_to_prior_fraction_literals](ThresholdsForTests.test_equivalence_to_prior_fraction_literals.md) method: HOLE: no docstring
  - [ThresholdsForTests.test_trip_points_unchanged_at_boundary](ThresholdsForTests.test_trip_points_unchanged_at_boundary.md) method: HOLE: no docstring
  - [ThresholdsForTests.test_calibrated_shipped_thresholds](ThresholdsForTests.test_calibrated_shipped_thresholds.md) method: HOLE: no docstring
