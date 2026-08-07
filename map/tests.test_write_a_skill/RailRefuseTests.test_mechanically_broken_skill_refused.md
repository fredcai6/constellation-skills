# tests.test_write_a_skill:RailRefuseTests.test_mechanically_broken_skill_refused
method, tests/test_write_a_skill.py:109, 14 lines

```python
def test_mechanically_broken_skill_refused(self)
```

HOLE: no docstring

calls internal: RailRefuseTests.assertRaises, _write_toy
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: RailRefuseTests.rail x2, TOY_SKILL_MD
reads stdlib: tempfile (module)
unresolved: 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
