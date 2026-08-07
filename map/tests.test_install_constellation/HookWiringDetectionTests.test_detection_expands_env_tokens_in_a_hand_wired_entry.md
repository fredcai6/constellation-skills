# tests.test_install_constellation:HookWiringDetectionTests.test_detection_expands_env_tokens_in_a_hand_wired_entry
method, tests/test_install_constellation.py:2059, 20 lines

```python
def test_detection_expands_env_tokens_in_a_hand_wired_entry(self)
```

docs/GAUGE_WRITER_HOOK.md currently tells users to hand-wire a

`${CLAUDE_PROJECT_DIR}` entry. The installer never GENERATES that form,
but reporting a working hand-wired entry as `stale` would be a false
alarm, so resolution expands env tokens from the run's own env.

calls internal: HookWiringDetectionTests.assertEqual x2, _HookWiringFixture._entry, _HookWiringFixture._fake_hook_file, _HookWiringFixture._write_settings, load_installer
calls stdlib: tempfile.TemporaryDirectory
reads internal: _HookWiringFixture.WRITER
reads stdlib: tempfile (module)
unresolved: 3 calls (dispatch-unknown-base), 5 reads (dispatch-unknown-base)

referenced by: none found
