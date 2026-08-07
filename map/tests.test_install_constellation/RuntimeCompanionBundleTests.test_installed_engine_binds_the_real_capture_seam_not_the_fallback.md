# tests.test_install_constellation:RuntimeCompanionBundleTests.test_installed_engine_binds_the_real_capture_seam_not_the_fallback
method, tests/test_install_constellation.py:1344, 49 lines

```python
def test_installed_engine_binds_the_real_capture_seam_not_the_fallback(self)
```

End-to-end for #305/#362: install a skill whose bundle is the engine

ALONE, then load the installed engine and prove `emit_step_manifest` is
the sidecar's, not the module-local `try/except ImportError` no-op.

Asserting the dict, or even the files on disk, cannot prove this: the
fallback is what makes the failure silent, so the only honest check is
which function the installed engine actually bound. `implementer` is the
deliberate choice of skill -- its bundle carries no companion by hand, so
everything here arrives through expand_script_bundle().

calls internal: RuntimeCompanionBundleTests.assertEqual x4, RuntimeCompanionBundleTests.assertTrue, RuntimeCompanionBundleTests.subTest, load_installer, load_module
calls stdlib: pathlib.Path x2, sys.modules.pop x2, builtins.str, tempfile.TemporaryDirectory
reads stdlib: sys (module) x4, sys.modules x4, tempfile (module)
writes stdlib: sys.modules[]
unresolved: 5 calls (dispatch-unknown-base), 5 reads (dispatch-unknown-base)

referenced by: none found
