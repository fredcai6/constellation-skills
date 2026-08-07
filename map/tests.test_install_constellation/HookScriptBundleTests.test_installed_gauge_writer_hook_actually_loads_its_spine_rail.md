# tests.test_install_constellation:HookScriptBundleTests.test_installed_gauge_writer_hook_actually_loads_its_spine_rail
method, tests/test_install_constellation.py:1459, 13 lines

```python
def test_installed_gauge_writer_hook_actually_loads_its_spine_rail(self)
```

End-to-end: install, then import the INSTALLED writer and assert it

resolved its rail. Presence on disk does not prove the sibling load
works; this drives the real loader (import-time `_load_spine_rail()`).

calls internal: HookScriptBundleTests._install_owner_skill, HookScriptBundleTests.assertIsNotNone, HookScriptBundleTests.assertTrue, load_module
calls stdlib: builtins.hasattr, tempfile.TemporaryDirectory
reads internal: HookScriptBundleTests.WRITER
reads stdlib: tempfile (module)
unresolved: 2 reads (dispatch-unknown-base)

referenced by: none found
