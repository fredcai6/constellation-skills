# tests.test_grade_lint:GradeLintReviewerRegressionTests.test_two_bracket_spans_are_not_scaffolding
method, tests/test_grade_lint.py:377, 12 lines

```python
def test_two_bracket_spans_are_not_scaffolding(self)
```

A line starting with one angle-bracket span and ending with another

is REAL ungraded decision text, not a template placeholder. The greedy
`^<.*>$` read silently PASSED it — a false clean on an invalid plan.

calls internal: GradeLintReviewerRegressionTests.assertEqual, GradeLintReviewerRegressionTests.assertIn, _run, _write
reads internal: GradeLintReviewerRegressionTests.gl, GradeLintReviewerRegressionTests.tmp
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
