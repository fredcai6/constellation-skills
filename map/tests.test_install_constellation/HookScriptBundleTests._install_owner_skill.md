# tests.test_install_constellation:HookScriptBundleTests._install_owner_skill
method, tests/test_install_constellation.py:1421, 11 lines

```python
def _install_owner_skill(self, tmp: str) -> Path
```

Really install the owner skill into a temp dest; return its scripts/ dir.

calls internal: HookScriptBundleTests.assertEqual, load_installer
calls stdlib: builtins.str, pathlib.Path
reads internal: HookScriptBundleTests.INSTALLED_OWNER, HookScriptBundleTests.OWNER_SKILL
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
