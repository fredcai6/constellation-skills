# tests.test_install_constellation:HookScriptBundleTests.test_validation_accepts_hook_scripts_from_their_subdirectory
method, tests/test_install_constellation.py:1517, 10 lines

```python
def test_validation_accepts_hook_scripts_from_their_subdirectory(self)
```

`validate_required_scripts` runs before every install and resolves

sources under scripts/. A subdir-blind check turns bundling the hooks
into a hard install failure rather than a silent one.

calls internal: HookScriptBundleTests.assertEqual, HookScriptBundleTests.assertIn, load_installer
calls stdlib: builtins.len
reads internal: HookScriptBundleTests.OWNER_SKILL, HookScriptBundleTests.WRITER
unresolved: 2 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found
