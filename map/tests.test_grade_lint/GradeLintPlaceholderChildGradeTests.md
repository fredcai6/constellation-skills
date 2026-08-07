# tests.test_grade_lint:GradeLintPlaceholderChildGradeTests
class, tests/test_grade_lint.py:325, 37 lines

```python
class GradeLintPlaceholderChildGradeTests(TestCase)
```

Regression: a grade welded to a decision that was skipped as template

scaffolding is itself scaffolding, and must NOT report as an orphan grade.
Before the fix, every template that showed a grade slot under its own
`- <placeholder>` bullet emitted a spurious GL010.

- [setUp](GradeLintPlaceholderChildGradeTests.setUp.md) method: HOLE: no docstring
- [tearDown](GradeLintPlaceholderChildGradeTests.tearDown.md) method: HOLE: no docstring
- [test_grade_under_placeholder_bullet_is_not_an_orphan](GradeLintPlaceholderChildGradeTests.test_grade_under_placeholder_bullet_is_not_an_orphan.md) method: HOLE: no docstring
- [test_real_orphan_grade_still_reported](GradeLintPlaceholderChildGradeTests.test_real_orphan_grade_still_reported.md) method: The fix must not blunt GL010 generally: a grade under a PROSE line

referenced by: none found
