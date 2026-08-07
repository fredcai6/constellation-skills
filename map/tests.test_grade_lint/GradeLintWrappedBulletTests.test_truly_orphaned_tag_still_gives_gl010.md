# tests.test_grade_lint:GradeLintWrappedBulletTests.test_truly_orphaned_tag_still_gives_gl010
method, tests/test_grade_lint.py:486, 14 lines

```python
def test_truly_orphaned_tag_still_gives_gl010(self)
```

A @grade tag with no decision bullet anywhere near it (only prose)

is the plain GL010 case, not the wrapped shape -- the fix must not
swallow it either.

calls internal: GradeLintWrappedBulletTests.assertEqual x2, _run, _write
calls stdlib: json.loads
reads internal: GradeLintWrappedBulletTests.gl, GradeLintWrappedBulletTests.tmp
reads stdlib: json (module)
unresolved: 1 reads (dispatch-unknown-base)

referenced by: none found
