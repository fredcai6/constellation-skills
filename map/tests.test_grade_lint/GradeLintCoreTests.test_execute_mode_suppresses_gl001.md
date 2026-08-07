# tests.test_grade_lint:GradeLintCoreTests.test_execute_mode_suppresses_gl001
method, tests/test_grade_lint.py:153, 14 lines

```python
def test_execute_mode_suppresses_gl001(self)
```

HOLE: no docstring

calls internal: GradeLintCoreTests.assertEqual x2, _run x2, GradeLintCoreTests.assertNotIn, _write
calls stdlib: json.loads
reads internal: GradeLintCoreTests.gl x2, GradeLintCoreTests.tmp
reads stdlib: json (module)
unresolved: 1 reads (dispatch-unknown-base)

referenced by: none found
