# tests.test_install_constellation:InstallConstellationTests.test_bundled_scripts_carry_their_sibling_imports
method, tests/test_install_constellation.py:639, 22 lines

```python
def test_bundled_scripts_carry_their_sibling_imports(self)
```

HOLE: no docstring

calls internal: InstallConstellationTests.assertIn, load_installer
calls stdlib: pathlib.Path x2, builtins.set, re.findall
reads stdlib: re (module) x2, re.M
unresolved: 5 calls (dispatch-unknown-base), 6 reads (dispatch-unknown-base)

referenced by: none found
