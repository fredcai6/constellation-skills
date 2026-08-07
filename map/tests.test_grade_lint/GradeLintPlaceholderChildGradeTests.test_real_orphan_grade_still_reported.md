# tests.test_grade_lint:GradeLintPlaceholderChildGradeTests.test_real_orphan_grade_still_reported
method, tests/test_grade_lint.py:350, 12 lines

```python
def test_real_orphan_grade_still_reported(self)
```

The fix must not blunt GL010 generally: a grade under a PROSE line

(no decision bullet at all) is still an orphan.

calls internal: GradeLintPlaceholderChildGradeTests.assertEqual, GradeLintPlaceholderChildGradeTests.assertIn, _run, _write
reads internal: GradeLintPlaceholderChildGradeTests.gl, GradeLintPlaceholderChildGradeTests.tmp
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
