# tests.test_grade_lint:GradeLintTemplateRoundTripTests.test_shipped_templates_clean_under_strict_warnings
method, tests/test_grade_lint.py:317, 6 lines

```python
def test_shipped_templates_clean_under_strict_warnings(self)
```

The templates carry a grade slot on their own placeholder bullets, so

they must be clean at WARN level too — not merely FAIL-free. This is what
caught the placeholder-child-grade orphan below.

calls internal: GradeLintTemplateRoundTripTests.assertEqual, _run
calls stdlib: builtins.str
reads internal: GradeLintTemplateRoundTripTests.gl, SHIPPED_TEMPLATES

referenced by: none found
