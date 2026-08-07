# tests.test_install_constellation:HookScriptBundleTests.test_gauge_writer_hook_dynamic_loads_are_declared_as_companions
method, tests/test_install_constellation.py:1473, 14 lines

```python
def test_gauge_writer_hook_dynamic_loads_are_declared_as_companions(self)
```

Parse the writer's source for `parent / "<name>.py"` sibling loads and

require each to be declared. Mirrors the engine's companion test so a NEW
dynamic load cannot be added without a matching bundle entry.

calls internal: HookScriptBundleTests.assertEqual x2, load_installer
calls stdlib: builtins.set x2, re.findall
reads internal: HookScriptBundleTests.WRITER x3, HookScriptBundleTests.HOOK_SOURCE_DIR, HookScriptBundleTests.RAIL
reads stdlib: re (module)
unresolved: 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
