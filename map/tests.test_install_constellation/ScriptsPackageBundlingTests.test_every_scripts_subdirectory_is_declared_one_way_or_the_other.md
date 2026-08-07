# tests.test_install_constellation:ScriptsPackageBundlingTests.test_every_scripts_subdirectory_is_declared_one_way_or_the_other
method, tests/test_install_constellation.py:1543, 16 lines

```python
def test_every_scripts_subdirectory_is_declared_one_way_or_the_other(self)
```

The gate this test exists for: a new package under scripts/ fails here

until somebody decides whether it bundles, instead of failing at install
time in someone else's run.

calls internal: ScriptsPackageBundlingTests._source_dirs x2, ScriptsPackageBundlingTests.assertTrue x2, ScriptsPackageBundlingTests.subTest, load_installer
calls stdlib: builtins.len x2, builtins.list
unresolved: 3 calls (dispatch-unknown-base), 8 reads (dispatch-unknown-base)

referenced by: none found
