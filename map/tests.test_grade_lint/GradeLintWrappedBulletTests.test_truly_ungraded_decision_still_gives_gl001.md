# tests.test_grade_lint:GradeLintWrappedBulletTests.test_truly_ungraded_decision_still_gives_gl001
method, tests/test_grade_lint.py:476, 9 lines

```python
def test_truly_ungraded_decision_still_gives_gl001(self)
```

A decision with no @grade anywhere nearby is the plain GL001 case,

not the wrapped shape -- the fix must not swallow it.

calls internal: GradeLintWrappedBulletTests.assertEqual x2, _run, _write
calls stdlib: json.loads
reads internal: GradeLintWrappedBulletTests.gl, GradeLintWrappedBulletTests.tmp
reads stdlib: json (module)
unresolved: 1 reads (dispatch-unknown-base)

referenced by: none found
