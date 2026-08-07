# tests.test_crew_launcher:ExternalResumeRefusalTests
class, tests/test_crew_launcher.py:972, 65 lines

```python
class ExternalResumeRefusalTests(TestCase)
```

Decision 6: --resume routes by the recorded entry's backend. An external

entry is unrecoverable by the wrapper — it reports rather than spawning.

- [test_external_resume_refuses_and_never_spawns](ExternalResumeRefusalTests.test_external_resume_refuses_and_never_spawns.md) method: HOLE: no docstring
- [test_legacy_external_dispatch_marker_also_refuses_resume](ExternalResumeRefusalTests.test_legacy_external_dispatch_marker_also_refuses_resume.md) method: A legacy external entry (dispatch marker, no `backend` field) still routes
- [test_cli_entry_resume_still_relaunches](ExternalResumeRefusalTests.test_cli_entry_resume_still_relaunches.md) method: A cli entry keeps today's resume behavior (relaunch + finalize).

referenced by: none found
