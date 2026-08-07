# tests.test_install_constellation:ScriptsPackageBundlingTests.test_a_non_installable_package_is_a_package_and_a_flattened_dir_is_not
method, tests/test_install_constellation.py:1560, 9 lines

```python
def test_a_non_installable_package_is_a_package_and_a_flattened_dir_is_not(self)
```

The declaration has to match reality: __init__.py is what makes the

relative imports that flattening breaks.

calls internal: ScriptsPackageBundlingTests._source_dirs, ScriptsPackageBundlingTests.assertEqual, ScriptsPackageBundlingTests.subTest, load_installer
unresolved: 1 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: none found
