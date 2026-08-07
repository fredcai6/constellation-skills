# tests.test_install_constellation:HookWiringDetectionTests.test_detection_survives_an_unparseable_settings_json
method, tests/test_install_constellation.py:2124, 12 lines

```python
def test_detection_survives_an_unparseable_settings_json(self)
```

A broken settings.json must not take the install down with it, and

must not be reported as one of the three real states -- we could not
classify it at all.

calls internal: HookWiringDetectionTests.assertEqual, HookWiringDetectionTests.assertIn, _HookWiringFixture._run, _HookWiringFixture._settings, load_installer
calls stdlib: tempfile.TemporaryDirectory
reads stdlib: tempfile (module)
unresolved: 2 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found
