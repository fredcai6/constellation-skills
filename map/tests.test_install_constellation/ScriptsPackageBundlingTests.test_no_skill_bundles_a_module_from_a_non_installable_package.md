# tests.test_install_constellation:ScriptsPackageBundlingTests.test_no_skill_bundles_a_module_from_a_non_installable_package
method, tests/test_install_constellation.py:1570, 13 lines

```python
def test_no_skill_bundles_a_module_from_a_non_installable_package(self)
```

Bundling one of these copies it flat and every relative import in it

raises on the installed side, where nothing here would catch it.

calls internal: ScriptsPackageBundlingTests.assertNotIn, ScriptsPackageBundlingTests.assertTrue, ScriptsPackageBundlingTests.subTest, load_installer
calls stdlib: builtins.set
reads internal: ScriptsPackageBundlingTests.SCRIPTS
unresolved: 2 calls (dispatch-unknown-base), 4 reads (dispatch-unknown-base)

referenced by: none found
