# tests.test_install_constellation:RuntimeCompanionBundleTests
class, tests/test_install_constellation.py:1227, 166 lines

```python
class RuntimeCompanionBundleTests(TestCase)
```

A bundled script that loads a sibling at runtime must ship that sibling.

The Context Governor (epic-178) was inert in every install from the day it
shipped: `checklist_engine.py` was bundled into ten skills, `gauge_reader.py`
into none, and `_load_gauge_reader()` fails open to None -- so Trip silently
never fired and nothing reported that it wasn't firing. These tests are
derived from the engine's ACTUAL dynamic loads rather than a hand-kept list,
so a newly-added companion cannot be forgotten the same way.

```python
ENGINE_RUNTIME_SIBLINGS = {'gauge_reader.py', 'episode_capture.py', 'agent_work_root.py', 'context_manifest.py'}
SCRIPTS_ROOT = ROOT / 'scripts'
```

- [test_engine_runtime_siblings_are_declared_as_companions](RuntimeCompanionBundleTests.test_engine_runtime_siblings_are_declared_as_companions.md) method: Derive what checklist_engine.py reaches at runtime and require every
- [test_every_skill_bundling_the_engine_also_gets_its_runtime_companions](RuntimeCompanionBundleTests.test_every_skill_bundling_the_engine_also_gets_its_runtime_companions.md) method: Generalized from the gauge-reader-only form: assert the whole declared
- [test_expansion_preserves_order_and_does_not_duplicate](RuntimeCompanionBundleTests.test_expansion_preserves_order_and_does_not_duplicate.md) method: HOLE: no docstring
- [test_installed_engine_can_actually_load_its_gauge_reader](RuntimeCompanionBundleTests.test_installed_engine_can_actually_load_its_gauge_reader.md) method: End-to-end: install for real, then load the INSTALLED engine and assert
- [test_installed_engine_binds_the_real_capture_seam_not_the_fallback](RuntimeCompanionBundleTests.test_installed_engine_binds_the_real_capture_seam_not_the_fallback.md) method: End-to-end for #305/#362: install a skill whose bundle is the engine

reads internal: ROOT
writes internal: RuntimeCompanionBundleTests.ENGINE_RUNTIME_SIBLINGS, RuntimeCompanionBundleTests.SCRIPTS_ROOT

referenced by: none found
