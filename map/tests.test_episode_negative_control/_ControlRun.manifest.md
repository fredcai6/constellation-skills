# tests.test_episode_negative_control:_ControlRun.manifest
method, tests/test_episode_negative_control.py:606, 9 lines

```python
def manifest(self, step: str = 'g2') -> dict
```

The step's delivery manifest, as the seam wrote it (#360, see `expectations`).

Read as bytes and decoded here rather than through `Path.read_text`, for the same
reason `expectations` does: the file's own bytes are what `context-manifest-ref`
pins, and a text read on Windows would not be them.

calls stdlib: builtins.open, json.loads
reads internal: _ControlRun.path
reads stdlib: json (module)
unresolved: 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
