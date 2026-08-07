# tests.test_context_determinism:RealCheckoutSkew.test_a_clean_checkout_differs_only_in_rev_never_in_shape
method, tests/test_context_determinism.py:431, 96 lines

```python
def test_a_clean_checkout_differs_only_in_rev_never_in_shape(self)
```

HOLE: no docstring

- [project](RealCheckoutSkew.test_a_clean_checkout_differs_only_in_rev_never_in_shape.project.md) method: HOLE: no docstring

calls internal: RealCheckoutSkew.assertEqual x9, RealCheckoutSkew.assertIsNone x3, RealCheckoutSkew.assertIsNotNone x2, RealCheckoutSkew.assertNotEqual x2, RealCheckoutSkew.subTest x2, RealCheckoutSkew.addCleanup, RealCheckoutSkew.declaration
calls stdlib: subprocess.run x3, builtins.str x2, unittest.SkipTest x2, builtins.len, builtins.open, builtins.range, builtins.zip, pathlib.Path, shutil.copyfile, shutil.rmtree, shutil.which, tempfile.mkdtemp
reads internal: ROOT x6, RealCheckoutSkew.PROBE x2, OVERLAY, RealCheckoutSkew.TRACKED, cm
reads stdlib: shutil (module) x3, subprocess (module) x3, unittest (module) x2, tempfile (module)
unresolved: 2 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: none found
