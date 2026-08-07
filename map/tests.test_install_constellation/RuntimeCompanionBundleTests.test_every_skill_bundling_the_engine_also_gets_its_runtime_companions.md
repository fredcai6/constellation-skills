# tests.test_install_constellation:RuntimeCompanionBundleTests.test_every_skill_bundling_the_engine_also_gets_its_runtime_companions
method, tests/test_install_constellation.py:1281, 20 lines

```python
def test_every_skill_bundling_the_engine_also_gets_its_runtime_companions(self)
```

Generalized from the gauge-reader-only form: assert the whole declared

companion tuple lands in every engine-carrying bundle, so adding a
companion to the dict automatically widens this test's coverage.

calls internal: RuntimeCompanionBundleTests.assertIn x2, RuntimeCompanionBundleTests.assertTrue, RuntimeCompanionBundleTests.subTest, load_installer
unresolved: 2 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: none found
