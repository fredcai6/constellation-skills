# tests.test_install_constellation:HookScriptBundleTests.test_hook_pair_lands_co_located_in_a_real_install
method, tests/test_install_constellation.py:1433, 25 lines

```python
def test_hook_pair_lands_co_located_in_a_real_install(self)
```

Install for real and assert both files sit in the SAME directory on

disk. Inspecting the bundle dict would pass even if the copy loop wrote
them to different places.

calls internal: HookScriptBundleTests.assertIn x2, HookScriptBundleTests.assertTrue x2, HookScriptBundleTests._install_owner_skill, HookScriptBundleTests.assertEqual
calls stdlib: builtins.sorted, tempfile.TemporaryDirectory
reads internal: HookScriptBundleTests.RAIL x3, HookScriptBundleTests.WRITER x3
reads stdlib: tempfile (module)
unresolved: 4 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: none found
