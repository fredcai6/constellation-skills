# tests.test_install_constellation:HookWiringDetectionTests.test_undeterminable_is_reported_as_neither_wired_nor_stale
method, tests/test_install_constellation.py:2099, 12 lines

```python
def test_undeterminable_is_reported_as_neither_wired_nor_stale(self)
```

"I cannot tell" must not be laundered into either confident verdict.

calls internal: HookWiringDetectionTests.assertNotIn x2, HookWiringDetectionTests.assertEqual, HookWiringDetectionTests.assertIn, _HookWiringFixture._entry, _HookWiringFixture._write_settings, load_installer
calls stdlib: tempfile.TemporaryDirectory
reads internal: _HookWiringFixture.WRITER
reads stdlib: tempfile (module)
unresolved: 2 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found
