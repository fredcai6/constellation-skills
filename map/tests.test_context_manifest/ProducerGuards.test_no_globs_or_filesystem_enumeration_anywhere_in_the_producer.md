# tests.test_context_manifest:ProducerGuards.test_no_globs_or_filesystem_enumeration_anywhere_in_the_producer
method, tests/test_context_manifest.py:749, 42 lines

```python
def test_no_globs_or_filesystem_enumeration_anywhere_in_the_producer(self)
```

HOLE: no docstring

calls internal: ProducerGuards.assertEqual x3, ProducerGuards._names_used, ProducerGuards.addCleanup, checklist
calls stdlib: builtins.sorted, pathlib.Path, tempfile.TemporaryDirectory
reads internal: ProducerGuards.SOURCE, cm
reads stdlib: os (module) x6, os.listdir, os.scandir, os.walk, tempfile (module)
unresolved: 6 calls (dispatch-unknown-base), 3 calls (dynamic)

referenced by: none found
