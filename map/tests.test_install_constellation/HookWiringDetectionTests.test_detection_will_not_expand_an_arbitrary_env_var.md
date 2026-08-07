# tests.test_install_constellation:HookWiringDetectionTests.test_detection_will_not_expand_an_arbitrary_env_var
method, tests/test_install_constellation.py:2080, 18 lines

```python
def test_detection_will_not_expand_an_arbitrary_env_var(self)
```

Regression, reproduced by the g2 reviewer: expansion happens in the

INSTALLER's environment while the entry runs in a future HOOK's, so an
unrelated variable that happens to be set right now could resolve a path
and report WIRED -- manufacturing the exact reassuring failure this
detector exists to prevent. Only CLAUDE_PROJECT_DIR is expandable.

calls internal: HookWiringDetectionTests.assertEqual x3, _HookWiringFixture._entry, _HookWiringFixture._fake_hook_file, _HookWiringFixture._write_settings, load_installer
calls stdlib: builtins.len, tempfile.TemporaryDirectory
reads internal: _HookWiringFixture.WRITER
reads stdlib: tempfile (module)
unresolved: 2 calls (dispatch-unknown-base), 5 reads (dispatch-unknown-base)

referenced by: none found
