# tests.test_install_constellation:_HookWiringFixture._run
method, tests/test_install_constellation.py:1962, 11 lines

```python
def _run(self, tmp, *extra, expect=0)
```

A real install run against <tmp>/skills, capturing its output.

calls internal: _HookWiringFixture._dest, _HookWiringFixture.assertEqual, load_installer
calls stdlib: builtins.str
reads internal: _HookWiringFixture.OWNER_SKILL
unresolved: 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 7 sites, this module only
