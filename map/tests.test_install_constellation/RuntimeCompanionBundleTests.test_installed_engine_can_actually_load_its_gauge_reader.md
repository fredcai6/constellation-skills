# tests.test_install_constellation:RuntimeCompanionBundleTests.test_installed_engine_can_actually_load_its_gauge_reader
method, tests/test_install_constellation.py:1321, 22 lines

```python
def test_installed_engine_can_actually_load_its_gauge_reader(self)
```

End-to-end: install for real, then load the INSTALLED engine and assert

it resolved its gauge reader. Asserting the file's presence would not
prove the import path works -- this drives the real loader.

calls internal: RuntimeCompanionBundleTests.assertTrue x2, RuntimeCompanionBundleTests.assertEqual, RuntimeCompanionBundleTests.assertIsNotNone, load_installer, load_module
calls stdlib: builtins.hasattr, builtins.str, pathlib.Path, tempfile.TemporaryDirectory
reads stdlib: tempfile (module)
unresolved: 2 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found
