# tests.test_install_constellation:HookWiringDetectionTests.test_detection_is_skipped_for_agents_with_no_hook_mechanism
method, tests/test_install_constellation.py:2176, 14 lines

```python
def test_detection_is_skipped_for_agents_with_no_hook_mechanism(self)
```

Hooks are a Claude Code mechanism. Reporting on -- let alone writing --

a `hooks.PostToolUse` array under ~/.codex/ would be talking about a file
nothing ever reads.

calls internal: HookWiringDetectionTests.assertEqual, HookWiringDetectionTests.assertNotIn, _HookWiringFixture._dest, load_installer
calls stdlib: builtins.str, tempfile.TemporaryDirectory
reads internal: _HookWiringFixture.OWNER_SKILL
reads stdlib: tempfile (module)
unresolved: 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
