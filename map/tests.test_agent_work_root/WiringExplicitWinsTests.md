# tests.test_agent_work_root:WiringExplicitWinsTests
class, tests/test_agent_work_root.py:215, 71 lines

```python
class WiringExplicitWinsTests(TestCase)
```

Explicit path args must ALWAYS win; the durable helper is consulted only

for the default. Each test poisons the module's `durable_root` so that if a
script consulted it for an explicitly-supplied path, the test would fail.

- [setUp](WiringExplicitWinsTests.setUp.md) method: HOLE: no docstring
- [tearDown](WiringExplicitWinsTests.tearDown.md) method: HOLE: no docstring
- [_poison](WiringExplicitWinsTests._poison.md) static method: HOLE: no docstring
- [test_apply_lessons_delta_explicit_file_wins](WiringExplicitWinsTests.test_apply_lessons_delta_explicit_file_wins.md) method: HOLE: no docstring
- [test_verify_lessons_applied_explicit_file_wins](WiringExplicitWinsTests.test_verify_lessons_applied_explicit_file_wins.md) method: HOLE: no docstring
- [test_verify_agent_feedback_explicit_root_wins_for_both](WiringExplicitWinsTests.test_verify_agent_feedback_explicit_root_wins_for_both.md) method: HOLE: no docstring
- [test_collect_feedback_explicit_inbox_wins](WiringExplicitWinsTests.test_collect_feedback_explicit_inbox_wins.md) method: HOLE: no docstring

reads stdlib: builtins.staticmethod

referenced by: none found
