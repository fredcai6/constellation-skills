# tests.test_install_constellation:HookWiringOptInTests.test_wire_hooks_is_rejected_for_an_agent_with_no_hook_mechanism
method, tests/test_install_constellation.py:2417, 13 lines

```python
def test_wire_hooks_is_rejected_for_an_agent_with_no_hook_mechanism(self)
```

HOLE: no docstring

calls internal: HookWiringOptInTests.assertFalse, HookWiringOptInTests.assertNotEqual, HookWiringOptInTests.assertRaises, _HookWiringFixture._dest, _HookWiringFixture._settings, load_installer
calls stdlib: builtins.str, contextlib.redirect_stderr, io.StringIO, tempfile.TemporaryDirectory
reads internal: _HookWiringFixture.OWNER_SKILL
reads stdlib: builtins.SystemExit, contextlib (module), io (module), tempfile (module)
unresolved: 2 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found
