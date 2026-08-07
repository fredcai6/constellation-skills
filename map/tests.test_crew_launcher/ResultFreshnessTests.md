# tests.test_crew_launcher:ResultFreshnessTests
class, tests/test_crew_launcher.py:383, 120 lines

```python
class ResultFreshnessTests(TestCase)
```

The canonical freshness gate: a result artifact must exist AND be at/after

the crew's dispatch time. A stale leftover from a prior attempt is not fresh.

```python
BASE = 1000000000.0
```

- [test_missing_file_is_not_fresh](ResultFreshnessTests.test_missing_file_is_not_fresh.md) method: HOLE: no docstring
- [test_result_after_dispatch_is_fresh](ResultFreshnessTests.test_result_after_dispatch_is_fresh.md) method: HOLE: no docstring
- [test_stale_result_before_dispatch_is_not_fresh](ResultFreshnessTests.test_stale_result_before_dispatch_is_not_fresh.md) method: HOLE: no docstring
- [test_same_second_is_not_falsely_stale](ResultFreshnessTests.test_same_second_is_not_falsely_stale.md) method: Sub-second `started_at` after the file mtime within the SAME whole
- [test_verify_result_stale_refuses_and_leaves_running](ResultFreshnessTests.test_verify_result_stale_refuses_and_leaves_running.md) method: --verify-result on a STALE leftover prints a STALE refusal, returns 1,
- [test_verify_result_missing_refuses_with_absent_message](ResultFreshnessTests.test_verify_result_missing_refuses_with_absent_message.md) method: HOLE: no docstring
- [test_launch_finding_only_stale_result_marks_failed](ResultFreshnessTests.test_launch_finding_only_stale_result_marks_failed.md) method: A spawn that exits 0 but leaves only a STALE prior-attempt result at the
- [test_recover_default_predicate_rejects_stale_uses_started_at](ResultFreshnessTests.test_recover_default_predicate_rejects_stale_uses_started_at.md) method: HOLE: no docstring

writes internal: ResultFreshnessTests.BASE

referenced by: none found
