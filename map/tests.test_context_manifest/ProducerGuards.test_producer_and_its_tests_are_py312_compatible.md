# tests.test_context_manifest:ProducerGuards.test_producer_and_its_tests_are_py312_compatible
method, tests/test_context_manifest.py:830, 18 lines

```python
def test_producer_and_its_tests_are_py312_compatible(self)
```

HOLE: no docstring

calls internal: ProducerGuards.fail x2, ProducerGuards.assertGreaterEqual, ProducerGuards.subTest
calls stdlib: ast.parse, ast.walk, builtins.any, builtins.isinstance, builtins.len
reads internal: ProducerGuards.PY313_ONLY_ATTRS, ProducerGuards.PY313_ONLY_KWARGS, ProducerGuards.own_files
reads stdlib: ast (module) x3, ast.Call
unresolved: 2 calls (dispatch-unknown-base), 1 calls (dynamic), 6 reads (dispatch-unknown-base)

referenced by: none found
