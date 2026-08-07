# tests.test_install_constellation:HookWiringOptInTests.test_wired_command_uses_the_probed_interpreter_and_documented_timeout
method, tests/test_install_constellation.py:2235, 16 lines

```python
def test_wired_command_uses_the_probed_interpreter_and_documented_timeout(self)
```

The interpreter comes from the existing probe, not a hardcoded `py`;

the timeout is carried verbatim from docs/GAUGE_WRITER_HOOK.md.

calls internal: HookWiringOptInTests.assertEqual x4, HookWiringOptInTests._entries, HookWiringOptInTests._wire, HookWiringOptInTests.assertTrue, load_installer
calls stdlib: tempfile.TemporaryDirectory
reads stdlib: tempfile (module)
unresolved: 2 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found
