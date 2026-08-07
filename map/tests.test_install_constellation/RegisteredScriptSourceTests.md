# tests.test_install_constellation:RegisteredScriptSourceTests
class, tests/test_install_constellation.py:1908, 30 lines

```python
class RegisteredScriptSourceTests(TestCase)
```

Source resolution has exactly ONE owner: `script_source_path`.

The installer half of the #262 regression. `scripts/verify_skill_registered.py`
re-implemented the lookup as `REPO_ROOT/"scripts"/script`, blind to
SCRIPT_SOURCE_SUBDIRS, and falsely refused `workbench` the moment a bundled
script started shipping from `scripts/hooks/`. That was invisible to the whole
suite, so pin it from both sides: the rail's side lives in
tests/test_write_a_skill.py.

- [test_every_registered_bundle_script_resolves_through_the_shared_resolver](RegisteredScriptSourceTests.test_every_registered_bundle_script_resolves_through_the_shared_resolver.md) method: HOLE: no docstring

referenced by: none found
