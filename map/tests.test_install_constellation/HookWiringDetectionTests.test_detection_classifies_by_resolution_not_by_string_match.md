# tests.test_install_constellation:HookWiringDetectionTests.test_detection_classifies_by_resolution_not_by_string_match
method, tests/test_install_constellation.py:2043, 15 lines

```python
def test_detection_classifies_by_resolution_not_by_string_match(self)
```

Two entries, textually indistinguishable in shape; only one has a file

behind it. A string-matching detector cannot tell them apart at all.

calls internal: HookWiringDetectionTests.assertEqual x3, _HookWiringFixture._entry x2, _HookWiringFixture._fake_hook_file, _HookWiringFixture._write_settings, load_installer
calls stdlib: builtins.len x2, pathlib.Path, tempfile.TemporaryDirectory
reads internal: _HookWiringFixture.WRITER
reads stdlib: tempfile (module)
unresolved: 3 calls (dispatch-unknown-base), 4 reads (dispatch-unknown-base)

referenced by: none found
