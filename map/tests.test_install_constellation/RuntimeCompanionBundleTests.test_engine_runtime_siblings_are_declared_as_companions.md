# tests.test_install_constellation:RuntimeCompanionBundleTests.test_engine_runtime_siblings_are_declared_as_companions
method, tests/test_install_constellation.py:1250, 30 lines

```python
def test_engine_runtime_siblings_are_declared_as_companions(self)
```

Derive what checklist_engine.py reaches at runtime and require every

reached sibling to be declared in SCRIPT_RUNTIME_COMPANIONS.

This replaces a regex that only saw `parent / "<name>.py"` dynamic loads.
That regex returned exactly {'gauge_reader.py'} against an engine source
that ALREADY contained `from episode_capture import emit_step_manifest`,
so #305's capture seam shipped to nobody and no test noticed: the engine
wraps the import in `try/except ImportError` with a no-op fallback, so on
every installed skill the gate completed and emitted nothing. The point
of widening this is the NEXT sidecar attached the same way, not this one.

calls internal: RuntimeCompanionBundleTests.assertEqual x3, engine_runtime_closure, load_installer
calls stdlib: builtins.set x2, builtins.sorted
reads internal: RuntimeCompanionBundleTests.ENGINE_RUNTIME_SIBLINGS, RuntimeCompanionBundleTests.SCRIPTS_ROOT
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
