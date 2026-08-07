# tests.test_checklist_engine:TripTwoBandGatePolicy
class, tests/test_checklist_engine.py:3221, 118 lines

```python
class TripTwoBandGatePolicy(TestCase)
```

#182 Module 3 — the Trip two-band gate policy. Thresholds are model-keyed

via #181's `thresholds_for`; NUMBERS are deferred to first-run calibration, so
every assertion is structural — pinned to the ACTUAL (soft, hard) the table
returns, never to a hardcoded 0.75/0.90. Both bands are exercised through the
`dispatch` CLI boundary (where the policy actually rides), with the gauge read
patched to a controlled Reading. Real-file wiring is covered separately below.

- [setUp](TripTwoBandGatePolicy.setUp.md) method: HOLE: no docstring
- [test_soft_fires_at_and_above_soft](TripTwoBandGatePolicy.test_soft_fires_at_and_above_soft.md) method: HOLE: no docstring
- [test_soft_never_below_soft](TripTwoBandGatePolicy.test_soft_never_below_soft.md) method: HOLE: no docstring
- [test_soft_never_forces_advance](TripTwoBandGatePolicy.test_soft_never_forces_advance.md) method: HOLE: no docstring
- [test_hard_refuses_at_and_above_hard_without_refresh](TripTwoBandGatePolicy.test_hard_refuses_at_and_above_hard_without_refresh.md) method: HOLE: no docstring
- [test_hard_never_refuses_below_hard](TripTwoBandGatePolicy.test_hard_never_refuses_below_hard.md) method: HOLE: no docstring
- [test_hard_passes_once_refresh_request_exists](TripTwoBandGatePolicy.test_hard_passes_once_refresh_request_exists.md) method: HOLE: no docstring
- [test_hard_refusal_leaves_state_unmutated](TripTwoBandGatePolicy.test_hard_refusal_leaves_state_unmutated.md) method: HOLE: no docstring
- [test_hard_advisory_on_current_points_at_attach](TripTwoBandGatePolicy.test_hard_advisory_on_current_points_at_attach.md) method: HOLE: no docstring
- [test_none_reading_never_forces_and_gives_no_advice](TripTwoBandGatePolicy.test_none_reading_never_forces_and_gives_no_advice.md) method: HOLE: no docstring
- [test_survey_checklist_gets_no_trip_policy](TripTwoBandGatePolicy.test_survey_checklist_gets_no_trip_policy.md) method: HOLE: no docstring
- [test_unresolvable_work_id_no_base_dir_no_reading](TripTwoBandGatePolicy.test_unresolvable_work_id_no_base_dir_no_reading.md) method: HOLE: no docstring

referenced by: none found
