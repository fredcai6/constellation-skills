# tests.test_install_constellation:HookWiringDetectionTests.test_a_resolvable_entry_still_wins_over_an_undeterminable_one
method, tests/test_install_constellation.py:2112, 11 lines

```python
def test_a_resolvable_entry_still_wins_over_an_undeterminable_one(self)
```

A real working entry alongside an unevaluatable one is WIRED: the

governor demonstrably fires, whatever the other entry does.

calls internal: _HookWiringFixture._entry x2, HookWiringDetectionTests.assertEqual, _HookWiringFixture._fake_hook_file, _HookWiringFixture._write_settings, load_installer
calls stdlib: tempfile.TemporaryDirectory
reads internal: _HookWiringFixture.WRITER
reads stdlib: tempfile (module)
unresolved: 2 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found
