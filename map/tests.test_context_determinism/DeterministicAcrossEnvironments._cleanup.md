# tests.test_context_determinism:DeterministicAcrossEnvironments._cleanup
class method, tests/test_context_determinism.py:177, 10 lines

```python
def _cleanup(cls)
```

HOLE: no docstring

calls stdlib: subprocess.run x2, builtins.str, shutil.rmtree
reads internal: ROOT x2
reads stdlib: subprocess (module) x2, shutil (module)
unresolved: 2 calls (dynamic)

referenced by: 2 sites, this module only
