# tests.test_checklist_engine:TripRealGaugeFileWiring
class, tests/test_checklist_engine.py:3563, 207 lines

```python
class TripRealGaugeFileWiring(TestCase)
```

#182 — end-to-end through `main()` with a REAL gauge.json written where

#180's writer drops it (a SIBLING of the spine: `base_dir/gauge.json`), read by
#181's real `read()`. Proves the path pairing and the reader wiring, not just
the band logic. Fresh fill >= hard refuses; a stale/absent gauge never forces.

- [_write_gauge](TripRealGaugeFileWiring._write_gauge.md) method: HOLE: no docstring
- [_spine](TripRealGaugeFileWiring._spine.md) method: HOLE: no docstring
- [test_fresh_hard_gauge_sibling_of_spine_refuses_then_passes_with_refresh](TripRealGaugeFileWiring.test_fresh_hard_gauge_sibling_of_spine_refuses_then_passes_with_refresh.md) method: HOLE: no docstring
- [test_stale_gauge_reads_none_and_never_forces](TripRealGaugeFileWiring.test_stale_gauge_reads_none_and_never_forces.md) method: HOLE: no docstring
- [test_absent_gauge_file_never_forces](TripRealGaugeFileWiring.test_absent_gauge_file_never_forces.md) method: HOLE: no docstring
- [_write_uncalibrated_flag](TripRealGaugeFileWiring._write_uncalibrated_flag.md) method: HOLE: no docstring
- [test_uncalibrated_model_is_announced_on_current](TripRealGaugeFileWiring.test_uncalibrated_model_is_announced_on_current.md) method: #252 — a blind governor must SAY it is blind. Silence is how an
- [test_uncalibrated_model_never_forces_or_refuses](TripRealGaugeFileWiring.test_uncalibrated_model_never_forces_or_refuses.md) method: It is a missing instrument, not a full context — with no window we
- [test_a_real_reading_wins_over_a_stale_flag](TripRealGaugeFileWiring.test_a_real_reading_wins_over_a_stale_flag.md) method: A leftover flag must not shout over a live gauge — the reading is
- [test_fresh_soft_gauge_advises_on_current_but_advance_passes](TripRealGaugeFileWiring.test_fresh_soft_gauge_advises_on_current_but_advance_passes.md) method: HOLE: no docstring
- [_write_skip_flag_sidecar](TripRealGaugeFileWiring._write_skip_flag_sidecar.md) method: HOLE: no docstring
- [test_ambiguous_binding_skip_is_announced_on_current](TripRealGaugeFileWiring.test_ambiguous_binding_skip_is_announced_on_current.md) method: HOLE: no docstring
- [test_no_usable_record_skip_is_announced_on_current](TripRealGaugeFileWiring.test_no_usable_record_skip_is_announced_on_current.md) method: HOLE: no docstring
- [test_skip_flag_never_forces_or_refuses](TripRealGaugeFileWiring.test_skip_flag_never_forces_or_refuses.md) method: HOLE: no docstring
- [test_uncalibrated_flag_wins_over_a_skip_flag_at_the_same_path](TripRealGaugeFileWiring.test_uncalibrated_flag_wins_over_a_skip_flag_at_the_same_path.md) method: Priority order proven with REAL coexisting sidecars, not just
- [test_stale_rejected_gauge_reports_raw_facts_on_current](TripRealGaugeFileWiring.test_stale_rejected_gauge_reports_raw_facts_on_current.md) method: HOLE: no docstring
- [test_stale_gauge_report_never_forces_advance](TripRealGaugeFileWiring.test_stale_gauge_report_never_forces_advance.md) method: HOLE: no docstring

referenced by: none found
