# tests.test_install_constellation:HookScriptBundleTests.test_hook_sources_stay_under_scripts_hooks
method, tests/test_install_constellation.py:1505, 11 lines

```python
def test_hook_sources_stay_under_scripts_hooks(self)
```

The SOURCE layout is frozen -- this repo's own settings file plus

tests/test_gauge_writer.py and tests/test_spine_rail.py hardcode
`scripts/hooks/...`. Bundling must reach into the subdirectory rather
than relocate the sources up into scripts/.

calls internal: HookScriptBundleTests.assertEqual, HookScriptBundleTests.assertFalse, HookScriptBundleTests.assertTrue, HookScriptBundleTests.subTest, load_installer
reads internal: HookScriptBundleTests.HOOK_SOURCE_DIR, HookScriptBundleTests.RAIL, HookScriptBundleTests.WRITER, ROOT
unresolved: 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
