# tests.test_install_constellation:ScriptsPackageBundlingTests
class, tests/test_install_constellation.py:1529, 62 lines

```python
class ScriptsPackageBundlingTests(TestCase)
```

Issue #456 g0: scripts/ gained its first real Python package, and the

install destination is flat. A package whose modules import each other
relatively cannot survive that flattening, so every directory under scripts/
has to be on the record as one thing or the other.

```python
SCRIPTS = ROOT / 'scripts'
```

- [_source_dirs](ScriptsPackageBundlingTests._source_dirs.md) method: Directories under scripts/ that hold Python modules.
- [test_every_scripts_subdirectory_is_declared_one_way_or_the_other](ScriptsPackageBundlingTests.test_every_scripts_subdirectory_is_declared_one_way_or_the_other.md) method: The gate this test exists for: a new package under scripts/ fails here
- [test_a_non_installable_package_is_a_package_and_a_flattened_dir_is_not](ScriptsPackageBundlingTests.test_a_non_installable_package_is_a_package_and_a_flattened_dir_is_not.md) method: The declaration has to match reality: __init__.py is what makes the
- [test_no_skill_bundles_a_module_from_a_non_installable_package](ScriptsPackageBundlingTests.test_no_skill_bundles_a_module_from_a_non_installable_package.md) method: Bundling one of these copies it flat and every relative import in it
- [test_the_declared_package_is_runnable_from_a_checkout](ScriptsPackageBundlingTests.test_the_declared_package_is_runnable_from_a_checkout.md) method: The stated alternative to bundling has to actually work, or the

reads internal: ROOT
writes internal: ScriptsPackageBundlingTests.SCRIPTS

referenced by: none found
