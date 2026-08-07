# tests.test_episode_store:FloorInterpreterPortabilityTests.test_the_store_actually_runs_on_the_floor_interpreter
method, tests/test_episode_store.py:2879, 37 lines

```python
def test_the_store_actually_runs_on_the_floor_interpreter(self)
```

HOLE: no docstring

calls internal: FloorInterpreterPortabilityTests.assertEqual x2, FloorInterpreterPortabilityTests.assertIn, FloorInterpreterPortabilityTests.floor_interpreter, FloorInterpreterPortabilityTests.skipTest, create_op, load
calls stdlib: builtins.str x5, pathlib.Path x2, subprocess.run x2, json.dumps, tempfile.TemporaryDirectory
reads internal: QUERY_SCRIPT, WRITER_SCRIPT
reads stdlib: subprocess (module) x2, json (module), tempfile (module)
unresolved: 2 calls (dispatch-unknown-base), 8 reads (dispatch-unknown-base)

referenced by: none found
