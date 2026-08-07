# tests.test_install_constellation:HookWiringOptInTests.test_wire_hooks_at_project_scope_warns_the_file_is_committable
method, tests/test_install_constellation.py:2447, 21 lines

```python
def test_wire_hooks_at_project_scope_warns_the_file_is_committable(self)
```

An absolute path embeds the user's home directory AND username, and a

project-scope settings.json is committable. Wiring must not make
committing it the path of least resistance.

calls internal: HookWiringOptInTests.assertIn x3, HookWiringOptInTests.assertEqual, HookWiringOptInTests.assertTrue, load_installer
calls stdlib: builtins.str, pathlib.Path, tempfile.TemporaryDirectory
reads internal: _HookWiringFixture.OWNER_SKILL
reads stdlib: tempfile (module)
unresolved: 5 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
