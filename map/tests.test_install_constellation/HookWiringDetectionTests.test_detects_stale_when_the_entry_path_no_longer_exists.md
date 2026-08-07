# tests.test_install_constellation:HookWiringDetectionTests.test_detects_stale_when_the_entry_path_no_longer_exists
method, tests/test_install_constellation.py:2029, 13 lines

```python
def test_detects_stale_when_the_entry_path_no_longer_exists(self)
```

The moved-install case. A string-matching detector reports this as

`wired` -- syntactically present, silently dead.

calls internal: HookWiringDetectionTests.assertEqual x3, _HookWiringFixture._entry, _HookWiringFixture._fake_hook_file, _HookWiringFixture._write_settings, load_installer
calls stdlib: builtins.len, tempfile.TemporaryDirectory
reads stdlib: tempfile (module)
unresolved: 3 calls (dispatch-unknown-base), 4 reads (dispatch-unknown-base)

referenced by: none found
