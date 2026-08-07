# tests.test_grade_lint:GradeLintWrappedBulletTests
class, tests/test_grade_lint.py:429, 77 lines

```python
class GradeLintWrappedBulletTests(TestCase)
```

Human ruling, issue #239 item 3: "wrapped bullets should be invalid and

we should mechanically test for them." The weld rule stays strictly
same-line-or-next-non-blank (not extended); a decision bullet that wraps
onto a continuation line before its @grade tag is INVALID and must report
ONE actionable GL013 naming the real cause, not the confusing GL001+GL010
pair a naive same-shape check would otherwise emit.

- [setUp](GradeLintWrappedBulletTests.setUp.md) method: HOLE: no docstring
- [tearDown](GradeLintWrappedBulletTests.tearDown.md) method: HOLE: no docstring
- [test_wrapped_bullet_reports_gl013_not_gl001_gl010](GradeLintWrappedBulletTests.test_wrapped_bullet_reports_gl013_not_gl001_gl010.md) method: HOLE: no docstring
- [test_normal_welded_bullet_still_passes_clean](GradeLintWrappedBulletTests.test_normal_welded_bullet_still_passes_clean.md) method: HOLE: no docstring
- [test_truly_ungraded_decision_still_gives_gl001](GradeLintWrappedBulletTests.test_truly_ungraded_decision_still_gives_gl001.md) method: A decision with no @grade anywhere nearby is the plain GL001 case,
- [test_truly_orphaned_tag_still_gives_gl010](GradeLintWrappedBulletTests.test_truly_orphaned_tag_still_gives_gl010.md) method: A @grade tag with no decision bullet anywhere near it (only prose)
- [test_shipped_templates_lint_clean_under_strict_warnings](GradeLintWrappedBulletTests.test_shipped_templates_lint_clean_under_strict_warnings.md) method: Regression guard named by the handoff: the wrapped-bullet diagnostic

referenced by: none found
