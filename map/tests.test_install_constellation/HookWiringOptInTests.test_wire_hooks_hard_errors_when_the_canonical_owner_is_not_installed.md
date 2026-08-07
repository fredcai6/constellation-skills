# tests.test_install_constellation:HookWiringOptInTests.test_wire_hooks_hard_errors_when_the_canonical_owner_is_not_installed
method, tests/test_install_constellation.py:2381, 18 lines

```python
def test_wire_hooks_hard_errors_when_the_canonical_owner_is_not_installed(self)
```

Refusing to wire something it cannot locate is correct, and is NOT a

fail-open violation: `decision:fail-open-is-inviolable` governs hook
EXECUTION paths, not installer preconditions.

calls internal: HookWiringOptInTests.assertFalse, HookWiringOptInTests.assertIn, HookWiringOptInTests.assertNotEqual, HookWiringOptInTests.assertRaises, _HookWiringFixture._dest, _HookWiringFixture._settings, load_installer
calls stdlib: builtins.str, contextlib.redirect_stderr, io.StringIO, tempfile.TemporaryDirectory
reads internal: _HookWiringFixture.OWNER_SKILL
reads stdlib: builtins.SystemExit, contextlib (module), io (module), tempfile (module)
unresolved: 3 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found
