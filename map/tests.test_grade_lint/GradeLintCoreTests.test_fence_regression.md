# tests.test_grade_lint:GradeLintCoreTests.test_fence_regression
method, tests/test_grade_lint.py:181, 14 lines

```python
def test_fence_regression(self)
```

HOLE: no docstring

calls internal: GradeLintCoreTests.assertEqual x2, _run, _write
calls stdlib: json.loads
reads internal: GradeLintCoreTests.gl, GradeLintCoreTests.tmp
reads stdlib: json (module)
unresolved: 1 reads (dispatch-unknown-base)

referenced by: none found
