# tests.test_context_manifest:ProducerGuards.test_build_manifest_with_both_edges_injected_shells_out_to_nothing
method, tests/test_context_manifest.py:864, 32 lines

```python
def test_build_manifest_with_both_edges_injected_shells_out_to_nothing(self)
```

HOLE: no docstring

- [explode](ProducerGuards.test_build_manifest_with_both_edges_injected_shells_out_to_nothing.explode.md) method: HOLE: no docstring

calls internal: ProducerGuards.addCleanup, ProducerGuards.assertEqual, checklist
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: cm x2
reads stdlib: subprocess (module) x6, subprocess.Popen, subprocess.run, tempfile (module)
writes stdlib: subprocess.Popen, subprocess.run
unresolved: 3 calls (dispatch-unknown-base), 2 calls (dynamic), 1 reads (dispatch-unknown-base)

referenced by: none found
