# tests.test_install_constellation:HookWiringOptInTests.test_wire_hooks_leaves_a_stale_entry_in_place_and_adds_a_sibling
method, tests/test_install_constellation.py:2362, 16 lines

```python
def test_wire_hooks_leaves_a_stale_entry_in_place_and_adds_a_sibling(self)
```

No self-healing, by design (the design brief names this an accepted

cost): the stale entry is REPORTED, never silently rewritten.

calls internal: HookWiringOptInTests.assertEqual x3, HookWiringOptInTests._entries, HookWiringOptInTests._wire, HookWiringOptInTests.assertIn, _HookWiringFixture._entry, _HookWiringFixture._settings, _HookWiringFixture._write_settings, load_installer
calls stdlib: builtins.len, tempfile.TemporaryDirectory
reads stdlib: tempfile (module)
unresolved: 1 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found
