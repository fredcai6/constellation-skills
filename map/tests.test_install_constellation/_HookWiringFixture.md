# tests.test_install_constellation:_HookWiringFixture
class, tests/test_install_constellation.py:1940, 46 lines

```python
class _HookWiringFixture(TestCase)
```

Shared fixture for the Context Governor settings.json detection + wiring

tests. `--dest <tmp>/skills` is used everywhere so the settings file under
test is `<tmp>/settings.json` -- a real install layout, and structurally
incapable of touching the developer's own ~/.claude/settings.json.

```python
OWNER_SKILL = 'workbench'
INSTALLED_OWNER = 'constellation-workbench'
WRITER = 'gauge_writer_hook.py'
```

- [_dest](_HookWiringFixture._dest.md) method: HOLE: no docstring
- [_settings](_HookWiringFixture._settings.md) method: HOLE: no docstring
- [_write_settings](_HookWiringFixture._write_settings.md) method: HOLE: no docstring
- [_run](_HookWiringFixture._run.md) method: A real install run against <tmp>/skills, capturing its output.
- [_fake_hook_file](_HookWiringFixture._fake_hook_file.md) method: A resolvable gauge_writer_hook.py that no install created -- lets the
- [_entry](_HookWiringFixture._entry.md) static method: HOLE: no docstring

reads stdlib: pathlib.Path x4, builtins.dict x2, builtins.str x2, builtins.staticmethod
writes internal: _HookWiringFixture.INSTALLED_OWNER, _HookWiringFixture.OWNER_SKILL, _HookWiringFixture.WRITER

referenced by: none found
