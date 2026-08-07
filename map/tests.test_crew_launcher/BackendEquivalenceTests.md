# tests.test_crew_launcher:BackendEquivalenceTests
class, tests/test_crew_launcher.py:713, 128 lines

```python
class BackendEquivalenceTests(TestCase)
```

The backends carry the behavior; the module functions are thin wrappers.

Each backend's dispatch/verify/resume matches the old function it replaces.

- [test_cli_dispatch_matches_launch_crew_and_tags_backend](BackendEquivalenceTests.test_cli_dispatch_matches_launch_crew_and_tags_backend.md) method: HOLE: no docstring
- [test_cli_dispatch_missing_handoff_refuses_with_launch_wording](BackendEquivalenceTests.test_cli_dispatch_missing_handoff_refuses_with_launch_wording.md) method: HOLE: no docstring
- [test_external_dispatch_records_without_spawning_returns_none](BackendEquivalenceTests.test_external_dispatch_records_without_spawning_returns_none.md) method: HOLE: no docstring
- [test_external_dispatch_missing_handoff_refuses_with_record_wording](BackendEquivalenceTests.test_external_dispatch_missing_handoff_refuses_with_record_wording.md) method: HOLE: no docstring
- [test_verify_is_uniform_across_backends](BackendEquivalenceTests.test_verify_is_uniform_across_backends.md) method: CrewBackend.verify (used by both backends) finalizes on a fresh result
- [test_cli_resume_relaunches_and_finalizes](BackendEquivalenceTests.test_cli_resume_relaunches_and_finalizes.md) method: HOLE: no docstring
- [test_external_resume_is_unrecoverable_by_wrapper](BackendEquivalenceTests.test_external_resume_is_unrecoverable_by_wrapper.md) method: HOLE: no docstring

referenced by: none found
