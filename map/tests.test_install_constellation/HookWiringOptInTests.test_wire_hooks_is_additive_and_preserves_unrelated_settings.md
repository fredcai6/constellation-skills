# tests.test_install_constellation:HookWiringOptInTests.test_wire_hooks_is_additive_and_preserves_unrelated_settings
method, tests/test_install_constellation.py:2312, 24 lines

```python
def test_wire_hooks_is_additive_and_preserves_unrelated_settings(self)
```

An unrelated PostToolUse matcher must survive intact and unreordered,

alongside unrelated top-level keys.

calls internal: HookWiringOptInTests.assertEqual x5, HookWiringOptInTests._settings_json, HookWiringOptInTests._wire, _HookWiringFixture._write_settings
calls stdlib: builtins.len, tempfile.TemporaryDirectory
reads internal: HookWiringOptInTests.UNRELATED x2
reads stdlib: tempfile (module)

referenced by: none found
