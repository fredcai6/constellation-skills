# tests.test_grade_lint:GradeLintMultiFileAndJsonTests.test_gl012_scoped_per_file_not_across_files
method, tests/test_grade_lint.py:206, 20 lines

```python
def test_gl012_scoped_per_file_not_across_files(self)
```

HOLE: no docstring

calls internal: _write x2, GradeLintMultiFileAndJsonTests.assertEqual, GradeLintMultiFileAndJsonTests.assertNotIn, _run
calls stdlib: json.loads
reads internal: GradeLintMultiFileAndJsonTests.tmp x2, GradeLintMultiFileAndJsonTests.gl
reads stdlib: json (module)
unresolved: 2 reads (dispatch-unknown-base)

referenced by: none found
