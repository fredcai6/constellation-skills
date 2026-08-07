# tests.test_grade_lint:GradeLintReviewerRegressionTests
class, tests/test_grade_lint.py:364, 63 lines

```python
class GradeLintReviewerRegressionTests(TestCase)
```

Two correctness bugs found by adversarial probing at review, fixed in

lane. Both are in the Markdown decision-detection heuristic, and neither is
reachable from the shipped templates — which is exactly why they needed
their own tests.

- [setUp](GradeLintReviewerRegressionTests.setUp.md) method: HOLE: no docstring
- [tearDown](GradeLintReviewerRegressionTests.tearDown.md) method: HOLE: no docstring
- [test_two_bracket_spans_are_not_scaffolding](GradeLintReviewerRegressionTests.test_two_bracket_spans_are_not_scaffolding.md) method: A line starting with one angle-bracket span and ending with another
- [test_true_placeholder_still_skipped](GradeLintReviewerRegressionTests.test_true_placeholder_still_skipped.md) method: The narrower rule must not break the placeholder skip the template
- [test_nested_sub_bullet_is_elaboration_not_a_decision](GradeLintReviewerRegressionTests.test_nested_sub_bullet_is_elaboration_not_a_decision.md) method: A bullet indented under a graded decision elaborates it. Treating it
- [test_sibling_bullet_at_same_indent_is_still_its_own_decision](GradeLintReviewerRegressionTests.test_sibling_bullet_at_same_indent_is_still_its_own_decision.md) method: The nesting rule keys on indentation, so a SIBLING bullet must still

referenced by: none found
