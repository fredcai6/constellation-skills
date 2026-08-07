# tests.test_install_constellation:HookWiringOptInTests.test_wire_hooks_writes_an_absolute_path_not_a_project_dir_token
method, tests/test_install_constellation.py:2222, 12 lines

```python
def test_wire_hooks_writes_an_absolute_path_not_a_project_dir_token(self)
```

HOLE: no docstring

calls internal: HookWiringOptInTests.assertNotIn x3, HookWiringOptInTests.assertTrue x2, HookWiringOptInTests._entries, HookWiringOptInTests._wire, HookWiringOptInTests.assertIn, _HookWiringFixture._dest, load_installer
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads stdlib: tempfile (module)
unresolved: 4 calls (dispatch-unknown-base)

referenced by: none found
