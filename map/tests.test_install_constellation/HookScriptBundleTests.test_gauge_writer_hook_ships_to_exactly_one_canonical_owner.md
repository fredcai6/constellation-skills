# tests.test_install_constellation:HookScriptBundleTests.test_gauge_writer_hook_ships_to_exactly_one_canonical_owner
method, tests/test_install_constellation.py:1495, 9 lines

```python
def test_gauge_writer_hook_ships_to_exactly_one_canonical_owner(self)
```

One canonical copy, by design: whatever later wires this hook into a

settings.json needs an unambiguous path to point at.

calls internal: HookScriptBundleTests.assertEqual, load_installer
calls stdlib: builtins.sorted
reads internal: HookScriptBundleTests.OWNER_SKILL, HookScriptBundleTests.WRITER
unresolved: 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
