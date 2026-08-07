# tests.test_install_constellation:HookScriptBundleTests
class, tests/test_install_constellation.py:1395, 132 lines

```python
class HookScriptBundleTests(TestCase)
```

The Context Governor's gauge WRITER has to ship, and ship co-located.

#256 bundled the gauge *reader* into every skill carrying the engine, so an
installed tree could READ a gauge that nothing ever WROTE -- the installer
had zero references to the hook pair. These tests ship the writer.

The co-location half is the load-bearing half and it fails SILENTLY:
`gauge_writer_hook._load_spine_rail()` resolves
`Path(__file__).resolve().parent / "spine_rail.py"` inside a bare
`try/except Exception: return None`. Land the two files in different
directories and nothing raises, nothing logs -- the hook just stops
resolving gauge paths. So the assertions below are made against the
OUTCOME ON DISK from a real install, and against the real loader, never
against the bundle dict alone (which cannot see a source-path mistake).

```python
HOOK_SOURCE_DIR = ROOT / 'scripts' / 'hooks'
WRITER = 'gauge_writer_hook.py'
RAIL = 'spine_rail.py'
OWNER_SKILL = 'workbench'
INSTALLED_OWNER = 'constellation-workbench'
```

- [_install_owner_skill](HookScriptBundleTests._install_owner_skill.md) method: Really install the owner skill into a temp dest; return its scripts/ dir.
- [test_hook_pair_lands_co_located_in_a_real_install](HookScriptBundleTests.test_hook_pair_lands_co_located_in_a_real_install.md) method: Install for real and assert both files sit in the SAME directory on
- [test_installed_gauge_writer_hook_actually_loads_its_spine_rail](HookScriptBundleTests.test_installed_gauge_writer_hook_actually_loads_its_spine_rail.md) method: End-to-end: install, then import the INSTALLED writer and assert it
- [test_gauge_writer_hook_dynamic_loads_are_declared_as_companions](HookScriptBundleTests.test_gauge_writer_hook_dynamic_loads_are_declared_as_companions.md) method: Parse the writer's source for `parent / "<name>.py"` sibling loads and
- [test_owner_skill_bundle_expands_to_both_hook_scripts](HookScriptBundleTests.test_owner_skill_bundle_expands_to_both_hook_scripts.md) method: HOLE: no docstring
- [test_gauge_writer_hook_ships_to_exactly_one_canonical_owner](HookScriptBundleTests.test_gauge_writer_hook_ships_to_exactly_one_canonical_owner.md) method: One canonical copy, by design: whatever later wires this hook into a
- [test_hook_sources_stay_under_scripts_hooks](HookScriptBundleTests.test_hook_sources_stay_under_scripts_hooks.md) method: The SOURCE layout is frozen -- this repo's own settings file plus
- [test_validation_accepts_hook_scripts_from_their_subdirectory](HookScriptBundleTests.test_validation_accepts_hook_scripts_from_their_subdirectory.md) method: `validate_required_scripts` runs before every install and resolves

reads internal: ROOT
reads stdlib: builtins.str, pathlib.Path
writes internal: HookScriptBundleTests.HOOK_SOURCE_DIR, HookScriptBundleTests.INSTALLED_OWNER, HookScriptBundleTests.OWNER_SKILL, HookScriptBundleTests.RAIL, HookScriptBundleTests.WRITER

referenced by: none found
