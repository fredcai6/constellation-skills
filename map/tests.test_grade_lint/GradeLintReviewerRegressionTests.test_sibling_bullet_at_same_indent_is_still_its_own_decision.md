# tests.test_grade_lint:GradeLintReviewerRegressionTests.test_sibling_bullet_at_same_indent_is_still_its_own_decision
method, tests/test_grade_lint.py:414, 13 lines

```python
def test_sibling_bullet_at_same_indent_is_still_its_own_decision(self)
```

The nesting rule keys on indentation, so a SIBLING bullet must still

be graded on its own — otherwise the fix would swallow real decisions.

calls internal: GradeLintReviewerRegressionTests.assertEqual, GradeLintReviewerRegressionTests.assertIn, _run, _write
reads internal: GradeLintReviewerRegressionTests.gl, GradeLintReviewerRegressionTests.tmp
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
