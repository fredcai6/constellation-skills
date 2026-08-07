# tests.test_install_constellation:HookWiringOptInTests.test_wire_hooks_refuses_an_unparseable_settings_json_without_clobbering
method, tests/test_install_constellation.py:2400, 16 lines

```python
def test_wire_hooks_refuses_an_unparseable_settings_json_without_clobbering(self)
```

HOLE: no docstring

calls internal: HookWiringOptInTests.assertEqual, HookWiringOptInTests.assertNotEqual, HookWiringOptInTests.assertRaises, _HookWiringFixture._dest, _HookWiringFixture._settings, load_installer
calls stdlib: builtins.str, contextlib.redirect_stderr, io.StringIO, tempfile.TemporaryDirectory
reads internal: _HookWiringFixture.OWNER_SKILL
reads stdlib: builtins.SystemExit, contextlib (module), io (module), tempfile (module)
unresolved: 4 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found
