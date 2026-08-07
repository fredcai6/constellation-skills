# tests.test_crew_launcher:BackendEquivalenceTests.test_cli_dispatch_matches_launch_crew_and_tags_backend
method, tests/test_crew_launcher.py:717, 19 lines

```python
def test_cli_dispatch_matches_launch_crew_and_tags_backend(self)
```

HOLE: no docstring

calls internal: BackendEquivalenceTests.assertEqual x5, BackendEquivalenceTests.assertIn, fake_launch, result_rel, write_handoff
calls stdlib: os.getpid, pathlib.Path, tempfile.TemporaryDirectory
reads internal: RC x3
reads stdlib: builtins.dict, builtins.list, os (module), tempfile (module)
unresolved: 4 calls (dispatch-unknown-base)

referenced by: none found
