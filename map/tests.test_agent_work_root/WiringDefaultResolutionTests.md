# tests.test_agent_work_root:WiringDefaultResolutionTests
class, tests/test_agent_work_root.py:288, 81 lines

```python
class WiringDefaultResolutionTests(TestCase)
```

When the explicit arg is omitted, the default path is computed through

`durable_root`. Each test stubs the module's `durable_root` to a tmpdir and
asserts the script reads/writes under `<tmpdir>/.agent-work`.

- [setUp](WiringDefaultResolutionTests.setUp.md) method: HOLE: no docstring
- [tearDown](WiringDefaultResolutionTests.tearDown.md) method: HOLE: no docstring
- [_stub](WiringDefaultResolutionTests._stub.md) method: HOLE: no docstring
- [test_apply_lessons_delta_default_uses_durable_root](WiringDefaultResolutionTests.test_apply_lessons_delta_default_uses_durable_root.md) method: HOLE: no docstring
- [test_verify_lessons_applied_default_uses_durable_root](WiringDefaultResolutionTests.test_verify_lessons_applied_default_uses_durable_root.md) method: HOLE: no docstring
- [test_verify_agent_feedback_default_durable_split](WiringDefaultResolutionTests.test_verify_agent_feedback_default_durable_split.md) method: HOLE: no docstring
- [test_collect_feedback_default_inbox_uses_durable_root](WiringDefaultResolutionTests.test_collect_feedback_default_inbox_uses_durable_root.md) method: HOLE: no docstring

referenced by: none found
