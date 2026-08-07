# tests.test_grade_lint:GradeLintWrappedBulletTests.test_shipped_templates_lint_clean_under_strict_warnings
method, tests/test_grade_lint.py:501, 5 lines

```python
def test_shipped_templates_lint_clean_under_strict_warnings(self)
```

Regression guard named by the handoff: the wrapped-bullet diagnostic

must not false-positive on any of the four shipped templates.

calls internal: GradeLintWrappedBulletTests.assertEqual, _run
calls stdlib: builtins.str
reads internal: GradeLintWrappedBulletTests.gl, SHIPPED_TEMPLATES

referenced by: none found
