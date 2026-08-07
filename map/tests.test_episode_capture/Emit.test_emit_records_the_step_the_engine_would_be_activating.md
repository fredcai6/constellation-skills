# tests.test_episode_capture:Emit.test_emit_records_the_step_the_engine_would_be_activating
method, tests/test_episode_capture.py:288, 10 lines

```python
def test_emit_records_the_step_the_engine_would_be_activating(self)
```

The step is chosen by the engine's own `active_id()`, so the seam must be

called AFTER the status mutation — otherwise `reopen` would record the wrong
step. Pinned with a checklist whose earlier gates are terminal.

calls internal: Emit.assertEqual, work_area
calls stdlib: json.loads, pathlib.Path, tempfile.TemporaryDirectory
reads internal: ec
reads stdlib: json (module), tempfile (module)
unresolved: 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
