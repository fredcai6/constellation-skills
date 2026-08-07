# tests.test_crew_launcher:ExternalDispatchTests
class, tests/test_crew_launcher.py:294, 87 lines

```python
class ExternalDispatchTests(TestCase)
```

--dispatch external: record the durable registry entry + duplicate-guard

+ result verification WITHOUT spawning any subprocess (the Agent-tool harness
has no headless `claude` CLI to launch).

- [test_external_dispatch_records_without_spawning](ExternalDispatchTests.test_external_dispatch_records_without_spawning.md) method: HOLE: no docstring
- [test_external_missing_handoff_is_refused](ExternalDispatchTests.test_external_missing_handoff_is_refused.md) method: HOLE: no docstring
- [test_external_duplicate_active_lock_is_refused](ExternalDispatchTests.test_external_duplicate_active_lock_is_refused.md) method: HOLE: no docstring
- [test_verify_result_absent_then_present_marks_completed](ExternalDispatchTests.test_verify_result_absent_then_present_marks_completed.md) method: HOLE: no docstring

referenced by: none found
