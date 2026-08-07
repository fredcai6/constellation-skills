# tests.test_write_a_skill:RealSkillRegistrationTests.test_rail_still_refuses_a_script_that_really_is_missing
method, tests/test_write_a_skill.py:173, 14 lines

```python
def test_rail_still_refuses_a_script_that_really_is_missing(self)
```

The resolver fix must not soften the check it was guarding: a bundle

entry naming a script that exists nowhere is still a broken
registration.

calls internal: RealSkillRegistrationTests.assertRaises, _write_toy
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: RealSkillRegistrationTests.rail x2
reads stdlib: tempfile (module)
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
