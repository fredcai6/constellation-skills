# tests.test_install_constellation:HookWiringOptInTests.test_wire_hooks_with_dry_run_together_writes_nothing
method, tests/test_install_constellation.py:2284, 17 lines

```python
def test_wire_hooks_with_dry_run_together_writes_nothing(self)
```

THE risky combination, and it gets its own test on purpose: `dry_run`

is pre-existing plumbing that a brand-new write path can trivially fail
to consult. A no-flag dry run is trivially safe and does NOT stand in
for this.

calls internal: HookWiringOptInTests._wire, HookWiringOptInTests.assertEqual, HookWiringOptInTests.assertIn, _HookWiringFixture._write_settings
calls stdlib: tempfile.TemporaryDirectory
reads internal: HookWiringOptInTests.UNRELATED
reads stdlib: tempfile (module)
unresolved: 2 calls (dispatch-unknown-base)

referenced by: none found
