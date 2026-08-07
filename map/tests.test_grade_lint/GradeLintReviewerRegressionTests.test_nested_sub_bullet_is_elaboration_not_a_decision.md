# tests.test_grade_lint:GradeLintReviewerRegressionTests.test_nested_sub_bullet_is_elaboration_not_a_decision
method, tests/test_grade_lint.py:401, 12 lines

```python
def test_nested_sub_bullet_is_elaboration_not_a_decision(self)
```

A bullet indented under a graded decision elaborates it. Treating it

as its own decision was a false FAIL on a valid plan.

calls internal: GradeLintReviewerRegressionTests.assertEqual, _run, _write
reads internal: GradeLintReviewerRegressionTests.gl, GradeLintReviewerRegressionTests.tmp
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
