# tests.test_grade_lint:GradeLintMultiFileAndJsonTests.test_json_structural_walk
method, tests/test_grade_lint.py:229, 33 lines

```python
def test_json_structural_walk(self)
```

HOLE: no docstring

calls internal: GradeLintMultiFileAndJsonTests.assertIn x2, GradeLintMultiFileAndJsonTests.assertEqual, _run, _write
calls stdlib: json.dumps, json.loads
reads internal: GradeLintMultiFileAndJsonTests.gl, GradeLintMultiFileAndJsonTests.tmp
reads stdlib: json (module) x2
unresolved: 1 reads (dispatch-unknown-base)

referenced by: none found
