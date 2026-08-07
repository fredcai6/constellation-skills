# tests.test_episode_negative_control:_ControlRun.compose
method, tests/test_episode_negative_control.py:600, 5 lines

```python
def compose(self) -> dict
```

The reading under test. Attribute lookup on the module happens HERE, at call

time, which is what lets a red-proof monkeypatch the composer.

calls stdlib: json.loads
calls third-party: episode_capture.mechanical_fields
reads internal: _ControlRun.path x2
reads stdlib: json (module)
reads third-party: episode_capture (module)
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
